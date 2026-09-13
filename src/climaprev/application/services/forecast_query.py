from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from time import monotonic, perf_counter
from typing import TYPE_CHECKING, Literal, Protocol, cast
from urllib.parse import quote

from climaprev.application.ports import (
    CacheEntry,
    CachePort,
    GeocodingPort,
    LockPort,
    MetricsPort,
    OfficialAlertPort,
    RiskEvaluatorPort,
    WeatherProviderPort,
)
from climaprev.application.query import ForecastQuery
from climaprev.domain.data_quality import Completeness, completeness
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    NormalizedForecast,
    OfficialAlert,
    RiskAssessment,
)
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.units import TemperatureUnit, convert_temperature
from climaprev.application.errors import DependencyUnavailable, ProviderTransientError

if TYPE_CHECKING:
    from climaprev.domain.models import RiskCondition

_GEO_CACHE_TTL_SECONDS = 24 * 60 * 60
_FORECAST_FRESH_TTL_SECONDS = 10 * 60
_FORECAST_STALE_TTL_SECONDS = 15 * 60
_LOCK_TTL_SECONDS = 10
_LOCK_HEARTBEAT_SECONDS = _LOCK_TTL_SECONDS / 2
_LOCK_WAITER_DEADLINE_SECONDS = 30
_LOCK_POLL_SECONDS = 0.01
_DISCLAIMER = (
    "Esta previsão é uma estimativa baseada em dados meteorológicos e não substitui alertas "
    "oficiais das autoridades competentes."
)


class WeatherProviderUnavailable(Exception):
    """The weather provider could not produce a forecast and no valid stale value exists."""


class LockOwnershipLost(WeatherProviderUnavailable):
    """The service lost the refresh lock while an upstream request was in progress."""


@dataclass(frozen=True, slots=True)
class ForecastDay:
    date: date
    temperature_min: float | None
    temperature_max: float | None
    temperature_mean: float | None
    humidity_mean_pct: float | None
    precipitation_sum_mm: float | None
    precipitation_probability_max_pct: float | None
    precipitation_max_hourly_mm: float | None
    wind_max_kmh: float | None
    wind_gust_max_kmh: float | None
    weather_code: int | None


@dataclass(frozen=True, slots=True)
class DataQuality:
    is_stale: bool
    missing_fields: tuple[str, ...]
    completeness: Completeness = "complete"


@dataclass(frozen=True, slots=True)
class ForecastSource:
    provider: str
    fetched_at: datetime


@dataclass(frozen=True, slots=True)
class OfficialAlertsResult:
    status: Literal["available", "not_configured", "unavailable"]
    items: tuple[OfficialAlert, ...]


@dataclass(frozen=True, slots=True)
class RiskQueryResult:
    location: CanonicalLocation
    period: DatePeriod
    temperature_unit: TemperatureUnit
    days: tuple[ForecastDay, ...]
    forecast_risk: RiskAssessment
    official_alerts: OfficialAlertsResult
    data_quality: DataQuality
    source: ForecastSource
    disclaimer: str
    request_id: str
    cache_status: Literal["hit", "miss", "stale"] = "miss"


class ForecastQueryPort(Protocol):
    async def execute(self, query: ForecastQuery, request_id: str) -> RiskQueryResult: ...


@dataclass(frozen=True, slots=True)
class _CachedForecast:
    forecast: NormalizedForecast
    expires_at: datetime

    @property
    def is_stale(self) -> bool:
        return self.forecast.is_stale


class ForecastQueryService:
    def __init__(
        self,
        *,
        geocoder: GeocodingPort,
        weather_provider: WeatherProviderPort,
        cache: CachePort,
        lock: LockPort,
        risk_evaluator: RiskEvaluatorPort,
        risk_policy: RiskPolicy,
        official_alert_provider: OfficialAlertPort,
        metrics: MetricsPort | None = None,
        provider_identity: str = "https://api.open-meteo.com",
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._geocoder = geocoder
        self._weather_provider = weather_provider
        self._cache = cache
        self._lock = lock
        self._risk_evaluator = risk_evaluator
        self._risk_policy = risk_policy
        self._official_alert_provider = official_alert_provider
        self._metrics = metrics
        self._provider_identity = provider_identity.rstrip("/")
        self._now = now

    async def execute(self, query: ForecastQuery, request_id: str) -> RiskQueryResult:
        period = DatePeriod(start=query.start_date, end=query.end_date)
        location = await self._resolve_location(query)
        forecast_key = _forecast_key(location, period, self._provider_identity)
        forecast, cache_status, fallback_expires_at = await self._get_forecast(
            forecast_key, location, period
        )
        forecast_risk = self._risk_evaluator.evaluate(forecast, self._risk_policy)
        if self._metrics is not None:
            self._metrics.record_risk_evaluation(forecast_risk)
            self._metrics.record_missing_fields(forecast.missing_fields)
        response_forecast_risk = _response_risk(forecast_risk, query.temperature_unit)
        official_alerts = await self._get_official_alerts(location, period)
        if fallback_expires_at is not None and self._now() >= fallback_expires_at:
            raise WeatherProviderUnavailable("cached forecast expired before delivery")

        return RiskQueryResult(
            location=replace(location, timezone=forecast.location.timezone),
            period=period,
            temperature_unit=query.temperature_unit,
            days=tuple(_response_day(day, query.temperature_unit) for day in forecast.days),
            forecast_risk=response_forecast_risk,
            official_alerts=official_alerts,
            data_quality=DataQuality(
                is_stale=forecast.is_stale,
                missing_fields=forecast.missing_fields,
                completeness=completeness(forecast),
            ),
            source=ForecastSource(provider=forecast.provider, fetched_at=forecast.fetched_at),
            disclaimer=_DISCLAIMER,
            request_id=request_id,
            cache_status=cache_status,
        )

    async def _resolve_location(self, query: ForecastQuery) -> CanonicalLocation:
        if query.location_text is None:
            if query.latitude is None or query.longitude is None:
                raise ValueError("validated query must include a location")
            return CanonicalLocation(
                name=f"{query.latitude:.4f},{query.longitude:.4f}",
                latitude=query.latitude,
                longitude=query.longitude,
                timezone="UTC",
                source="coordinates",
            )

        key = _geo_key(query.location_text)
        cached = await self._cache.get(key)
        if cached is not None:
            location = _location_from_cache(cached.value)
            if location is not None:
                return location

        location = await self._geocoder.resolve(query.location_text)
        await self._cache.set(
            key,
            CacheEntry(value=_location_to_cache(location), is_stale=False),
            fresh_ttl_seconds=_GEO_CACHE_TTL_SECONDS,
            stale_ttl_seconds=_GEO_CACHE_TTL_SECONDS,
        )
        return location

    async def _get_forecast(
        self,
        key: str,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> tuple[NormalizedForecast, Literal["hit", "miss", "stale"], datetime | None]:
        cached = await self._read_forecast(key, location, period)
        if cached is not None and not cached.is_stale:
            self._metrics_record_cache("hit")
            return cached.forecast, "hit", None
        stale_forecast = cached if cached is not None and cached.is_stale else None

        lock_result = await self._wait_for_lock(key, location, period)
        if isinstance(lock_result, _CachedForecast):
            self._metrics_record_cache("hit")
            return lock_result.forecast, "hit", None
        token = lock_result
        if token is None:
            if stale_forecast is not None and self._now() < stale_forecast.expires_at:
                self._metrics_record_cache("stale")
                return stale_forecast.forecast, "stale", stale_forecast.expires_at
            raise WeatherProviderUnavailable("forecast refresh lock timed out")

        primary_error: BaseException | None = None
        try:
            cached_after_lock = await self._read_forecast(key, location, period)
            if cached_after_lock is not None and not cached_after_lock.is_stale:
                self._metrics_record_cache("hit")
                return cached_after_lock.forecast, "hit", None
            if cached_after_lock is not None and cached_after_lock.is_stale:
                stale_forecast = cached_after_lock

            try:
                started_at = perf_counter()
                try:
                    forecast = await self._forecast_with_lock_heartbeat(key, token, location, period)
                except Exception:
                    self._metrics_record_provider("open-meteo", perf_counter() - started_at, "error")
                    self._metrics_record_upstream_error()
                    raise
                else:
                    self._metrics_record_provider(
                        forecast.provider, perf_counter() - started_at, "success"
                    )
            except ProviderTransientError as error:
                if stale_forecast is not None and self._now() < stale_forecast.expires_at:
                    self._metrics_record_cache("stale")
                    return stale_forecast.forecast, "stale", stale_forecast.expires_at
                raise WeatherProviderUnavailable("weather provider is temporarily unavailable") from error

            canonical_forecast = replace(forecast, is_stale=False)
            await self._cache.set(
                key,
                CacheEntry(value=_forecast_to_cache(canonical_forecast), is_stale=False),
                fresh_ttl_seconds=_FORECAST_FRESH_TTL_SECONDS,
                stale_ttl_seconds=_FORECAST_STALE_TTL_SECONDS,
            )
            self._metrics_record_cache("miss")
            return canonical_forecast, "miss", None
        except BaseException as error:
            primary_error = error
            raise
        finally:
            try:
                await self._lock.release(key, token)
            except DependencyUnavailable:
                if primary_error is None:
                    raise

    async def _wait_for_lock(
        self,
        key: str,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> str | _CachedForecast | None:
        deadline = monotonic() + _LOCK_WAITER_DEADLINE_SECONDS
        while True:
            token = await self._lock.acquire(key, ttl_seconds=_LOCK_TTL_SECONDS)
            if token is not None:
                return token

            cached = await self._read_forecast(key, location, period)
            if cached is not None and not cached.is_stale:
                return cached

            if monotonic() >= deadline:
                return None
            await asyncio.sleep(_LOCK_POLL_SECONDS)

    async def _read_forecast(
        self,
        key: str,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> _CachedForecast | None:
        entry = await self._cache.get(key)
        if entry is None or entry.expires_at is None or self._now() >= entry.expires_at:
            return None
        forecast = _forecast_from_cache(entry.value, location, period)
        if forecast is None:
            return None
        return _CachedForecast(replace(forecast, is_stale=entry.is_stale), entry.expires_at)

    async def _forecast_with_lock_heartbeat(
        self,
        key: str,
        token: str,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> NormalizedForecast:
        provider_task = asyncio.create_task(self._weather_provider.forecast(location, period))
        heartbeat_task = asyncio.create_task(self._maintain_lock(key, token))
        try:
            done, _ = await asyncio.wait(
                {provider_task, heartbeat_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            if heartbeat_task in done:
                await _cancel_and_await(provider_task)
                heartbeat_task.result()
                raise AssertionError("lock heartbeat must run until it is cancelled")
            return provider_task.result()
        finally:
            await _cancel_and_await(heartbeat_task)
            await _cancel_and_await(provider_task)

    async def _maintain_lock(self, key: str, token: str) -> None:
        while True:
            await asyncio.sleep(_LOCK_HEARTBEAT_SECONDS)
            if not await self._lock.refresh(key, token, ttl_seconds=_LOCK_TTL_SECONDS):
                raise LockOwnershipLost("forecast refresh lock ownership was lost")

    async def _get_official_alerts(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> OfficialAlertsResult:
        if getattr(self._official_alert_provider, "status", None) == "not_configured":
            return OfficialAlertsResult(status="not_configured", items=())
        try:
            alerts = await self._official_alert_provider.get_alerts(location, period)
        except Exception:  # noqa: BLE001 - optional alert providers must not block the forecast.
            return OfficialAlertsResult(status="unavailable", items=())
        return OfficialAlertsResult(status="available", items=tuple(alerts))

    def _metrics_record_cache(self, status: str) -> None:
        if self._metrics is not None:
            self._metrics.record_cache_status(status)

    def _metrics_record_provider(self, provider: str, duration_seconds: float, outcome: str) -> None:
        if self._metrics is not None:
            self._metrics.record_provider_request(provider, duration_seconds, outcome)

    def _metrics_record_upstream_error(self) -> None:
        if self._metrics is not None:
            self._metrics.record_upstream_error()


def _geo_key(location_text: str) -> str:
    return f"geo:v1:{quote(location_text.casefold(), safe='')}"


def _forecast_key(
    location: CanonicalLocation, period: DatePeriod,
    provider_identity: str = "https://api.open-meteo.com",
) -> str:
    identity = json.dumps(
        [location.latitude, location.longitude, period.start.isoformat(), period.end.isoformat(),
         "normalization-v2", provider_identity.rstrip("/")],
        separators=(",", ":"), allow_nan=False,
    )
    return "forecast:v2:" + hashlib.sha256(identity.encode()).hexdigest()


def _response_day(day: DailyForecast, unit: TemperatureUnit) -> ForecastDay:
    return ForecastDay(
        date=day.date,
        temperature_min=convert_temperature(day.temperature_min_c, unit),
        temperature_max=convert_temperature(day.temperature_max_c, unit),
        temperature_mean=convert_temperature(day.temperature_mean_c, unit),
        humidity_mean_pct=day.humidity_mean_pct,
        precipitation_sum_mm=day.precipitation_sum_mm,
        precipitation_probability_max_pct=day.precipitation_probability_max_pct,
        precipitation_max_hourly_mm=day.precipitation_max_hourly_mm,
        wind_max_kmh=day.wind_max_kmh,
        wind_gust_max_kmh=day.wind_gust_max_kmh,
        weather_code=day.weather_code,
    )


def _response_risk(assessment: RiskAssessment, unit: TemperatureUnit) -> RiskAssessment:
    if unit is TemperatureUnit.CELSIUS:
        return assessment

    conditions = tuple(
        _response_condition(condition, unit) for condition in assessment.conditions
    )
    return replace(assessment, conditions=conditions)


def _response_condition(condition: RiskCondition, unit: TemperatureUnit) -> RiskCondition:
    if condition.type != "temperature_extreme_proxy":
        return condition
    converted = cast(float, convert_temperature(condition.value, unit))
    return replace(condition, value=converted, unit="fahrenheit")


def _location_to_cache(location: CanonicalLocation) -> dict[str, object]:
    return {
        "name": location.name,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timezone": location.timezone,
        "source": location.source,
    }


def _location_from_cache(value: object) -> CanonicalLocation | None:
    if not isinstance(value, Mapping):
        return None
    name = _string(value.get("name"))
    latitude = _number(value.get("latitude"))
    longitude = _number(value.get("longitude"))
    timezone = _string(value.get("timezone"))
    source = _string(value.get("source"))
    if name is None or latitude is None or longitude is None or timezone is None or source is None:
        return None
    return CanonicalLocation(
        name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        source=source,
    )


def _forecast_to_cache(forecast: NormalizedForecast) -> dict[str, object]:
    return {
        "location": _location_to_cache(forecast.location),
        "period": {
            "start": forecast.period.start.isoformat(),
            "end": forecast.period.end.isoformat(),
        },
        "days": [
            {
                "date": day.date.isoformat(),
                "temperature_min_c": day.temperature_min_c,
                "temperature_max_c": day.temperature_max_c,
                "temperature_mean_c": day.temperature_mean_c,
                "humidity_mean_pct": day.humidity_mean_pct,
                "precipitation_sum_mm": day.precipitation_sum_mm,
                "precipitation_probability_max_pct": day.precipitation_probability_max_pct,
                "precipitation_max_hourly_mm": day.precipitation_max_hourly_mm,
                "wind_max_kmh": day.wind_max_kmh,
                "wind_gust_max_kmh": day.wind_gust_max_kmh,
                "weather_code": day.weather_code,
            }
            for day in forecast.days
        ],
        "provider": forecast.provider,
        "fetched_at": forecast.fetched_at.isoformat(),
        "is_stale": False,
        "missing_fields": list(forecast.missing_fields),
    }


def _forecast_from_cache(
    value: object,
    expected_location: CanonicalLocation,
    expected_period: DatePeriod,
) -> NormalizedForecast | None:
    if not isinstance(value, Mapping):
        return None
    location = _location_from_cache(value.get("location"))
    period = _period_from_cache(value.get("period"))
    days = _days_from_cache(value.get("days"))
    provider = _string(value.get("provider"))
    fetched_at = _datetime(value.get("fetched_at"))
    missing_fields = _strings(value.get("missing_fields"))
    if not isinstance(value.get("is_stale"), bool):
        return None
    if (
        location is None
        or period is None
        or days is None
        or provider is None
        or fetched_at is None
        or missing_fields is None
    ):
        return None
    expected_days = tuple(period.start + timedelta(days=index) for index in range(period.days))
    if tuple(day.date for day in days) != expected_days:
        return None
    if (location.latitude != expected_location.latitude
            or location.longitude != expected_location.longitude or period != expected_period):
        return None
    return NormalizedForecast(
        location=replace(expected_location, timezone=location.timezone),
        period=period,
        days=days,
        provider=provider,
        fetched_at=fetched_at,
        is_stale=False,
        missing_fields=missing_fields,
    )


def _period_from_cache(value: object) -> DatePeriod | None:
    if not isinstance(value, Mapping):
        return None
    start = _date(value.get("start"))
    end = _date(value.get("end"))
    if start is None or end is None:
        return None
    try:
        return DatePeriod(start=start, end=end)
    except ValueError:
        return None


def _days_from_cache(value: object) -> tuple[DailyForecast, ...] | None:
    if not isinstance(value, list):
        return None
    days: list[DailyForecast] = []
    for item in value:
        if not isinstance(item, Mapping):
            return None
        parsed = _day_from_cache(item)
        if parsed is None:
            return None
        days.append(parsed)
    return tuple(days)


def _day_from_cache(value: Mapping[object, object]) -> DailyForecast | None:
    required_fields = (
        "date",
        "temperature_min_c",
        "temperature_max_c",
        "temperature_mean_c",
        "humidity_mean_pct",
        "precipitation_sum_mm",
        "precipitation_probability_max_pct",
        "precipitation_max_hourly_mm",
        "wind_max_kmh",
        "wind_gust_max_kmh",
        "weather_code",
    )
    if any(field not in value for field in required_fields):
        return None
    day_date = _date(value.get("date"))
    weather_code = _integer_or_none(value.get("weather_code"))
    numbers = {
        key: _number_or_none(value.get(key))
        for key in (
            "temperature_min_c",
            "temperature_max_c",
            "temperature_mean_c",
            "humidity_mean_pct",
            "precipitation_sum_mm",
            "precipitation_probability_max_pct",
            "precipitation_max_hourly_mm",
            "wind_max_kmh",
            "wind_gust_max_kmh",
        )
    }
    if day_date is None or isinstance(weather_code, _InvalidValue):
        return None
    if any(isinstance(number, _InvalidValue) for number in numbers.values()):
        return None
    return DailyForecast(
        date=day_date,
        temperature_min_c=cast(float | None, numbers["temperature_min_c"]),
        temperature_max_c=cast(float | None, numbers["temperature_max_c"]),
        temperature_mean_c=cast(float | None, numbers["temperature_mean_c"]),
        humidity_mean_pct=cast(float | None, numbers["humidity_mean_pct"]),
        precipitation_sum_mm=cast(float | None, numbers["precipitation_sum_mm"]),
        precipitation_probability_max_pct=cast(
            float | None, numbers["precipitation_probability_max_pct"]
        ),
        precipitation_max_hourly_mm=cast(float | None, numbers["precipitation_max_hourly_mm"]),
        wind_max_kmh=cast(float | None, numbers["wind_max_kmh"]),
        wind_gust_max_kmh=cast(float | None, numbers["wind_gust_max_kmh"]),
        weather_code=weather_code,
    )


class _InvalidValue:
    pass


_INVALID = _InvalidValue()


def _string(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _number_or_none(value: object) -> float | None | _InvalidValue:
    if value is None:
        return None
    number = _number(value)
    return _INVALID if number is None else number


def _integer_or_none(value: object) -> int | None | _InvalidValue:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return _INVALID
    return value


def _date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _strings(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return tuple(value)


async def _cancel_and_await(task: asyncio.Task[object]) -> None:
    if not task.done():
        task.cancel()
    # Cleanup consumes task failures; the selected result above owns error propagation.
    with suppress(asyncio.CancelledError, Exception):
        await task
