from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from random import uniform
from time import monotonic, perf_counter
from typing import TYPE_CHECKING, Literal, Protocol, cast
from urllib.parse import quote
from zoneinfo import ZoneInfo

from climaprev.application.errors import DependencyUnavailable, ProviderTransientError
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
from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.data_quality import Completeness, completeness
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    NormalizedForecast,
    OfficialAlert,
    RiskAssessment,
    RiskOverview,
)
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.units import TemperatureUnit, convert_temperature

if TYPE_CHECKING:
    from climaprev.domain.models import RiskCondition

_GEO_CACHE_TTL_SECONDS = 24 * 60 * 60
_FORECAST_FRESH_TTL_SECONDS = 10 * 60
_FORECAST_STALE_TTL_SECONDS = 15 * 60
_OFFICIAL_ALERTS_FRESH_TTL_SECONDS = 5 * 60
_OFFICIAL_ALERTS_STALE_TTL_SECONDS = 10 * 60
_OFFICIAL_ALERTS_FAILURE_FRESH_TTL_SECONDS = 30
_OFFICIAL_ALERTS_FAILURE_STALE_TTL_SECONDS = 60
_LOCK_TTL_SECONDS = 10
_LOCK_HEARTBEAT_SECONDS = _LOCK_TTL_SECONDS / 2
_LOCK_WAITER_DEADLINE_SECONDS = 30
_LOCK_INITIAL_BACKOFF_SECONDS = 0.05
_LOCK_MAX_BACKOFF_SECONDS = 1.0
_LOCK_BACKOFF_FACTOR = 2.0
_LOCK_BACKOFF_JITTER = 0.25
_LOCK_MAX_ATTEMPTS = 64
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
    risk_overview: RiskOverview | None = None
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
        calibration: ForecastCalibration | None = None,
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
        self._calibration = calibration or ForecastCalibration.disabled()
        self._metrics = metrics
        self._provider_identity = provider_identity.rstrip("/")
        self._now = now

    async def execute(self, query: ForecastQuery, request_id: str) -> RiskQueryResult:
        period = DatePeriod(start=query.start_date, end=query.end_date)
        location = await self._resolve_location(query)
        forecast_key = _forecast_key(
            location,
            period,
            self._provider_identity,
            self._calibration.profile_version,
        )
        forecast, cache_status, fallback_expires_at = await self._get_forecast(
            forecast_key, location, period
        )
        forecast_risk = self._risk_evaluator.evaluate(forecast, self._risk_policy)
        if self._metrics is not None:
            self._metrics.record_risk_evaluation(forecast_risk)
            self._metrics.record_missing_fields(forecast.missing_fields)
        official_alerts = await self._get_official_alerts(location, period)
        if self._metrics is not None:
            self._metrics.record_official_alert_status(official_alerts.status)
        response_forecast_risk = _response_risk(forecast_risk, query.temperature_unit)
        risk_overview = _risk_overview(
            forecast_risk, official_alerts, period, forecast.location.timezone
        )
        if fallback_expires_at is not None and self._now() >= fallback_expires_at:
            raise WeatherProviderUnavailable("cached forecast expired before delivery")

        return RiskQueryResult(
            location=replace(location, timezone=forecast.location.timezone),
            period=period,
            temperature_unit=query.temperature_unit,
            days=tuple(_response_day(day, query.temperature_unit) for day in forecast.days),
            forecast_risk=response_forecast_risk,
            risk_overview=risk_overview,
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
                    forecast = self._calibration.apply(forecast)
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
        backoff_seconds = _LOCK_INITIAL_BACKOFF_SECONDS
        contended = False
        for attempt in range(_LOCK_MAX_ATTEMPTS):
            token = await self._lock.acquire(key, ttl_seconds=_LOCK_TTL_SECONDS)
            if token is not None:
                return token
            if not contended:
                self._metrics_record_lock_contention()
                contended = True

            cached = await self._read_forecast(key, location, period)
            if cached is not None and not cached.is_stale:
                return cached

            remaining_seconds = deadline - monotonic()
            if remaining_seconds <= 0:
                self._metrics_record_lock_timeout()
                return None
            if attempt == _LOCK_MAX_ATTEMPTS - 1:
                self._metrics_record_lock_timeout()
                return None
            wait_seconds = min(
                remaining_seconds,
                backoff_seconds
                * uniform(1 - _LOCK_BACKOFF_JITTER, 1 + _LOCK_BACKOFF_JITTER),
            )
            await asyncio.sleep(wait_seconds)
            backoff_seconds = min(
                _LOCK_MAX_BACKOFF_SECONDS,
                backoff_seconds * _LOCK_BACKOFF_FACTOR,
            )
        self._metrics_record_lock_timeout()
        return None

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

        cache_key = _official_alerts_key(location, period)
        try:
            cached = await self._cache.get(cache_key)
        except Exception:  # noqa: BLE001 - optional cache must not block the forecast.
            cached = None
        if (cached is not None and not cached.is_stale and cached.expires_at is not None
                and self._now() < cached.expires_at):
            cached_result = _official_alerts_from_cache(cached.value)
            if cached_result is not None and all(
                alert.expires_at is not None and self._now() < alert.expires_at
                for alert in cached_result.items
            ):
                return replace(cached_result, items=_deliverable_alerts(
                    cached_result.items, location, period, self._now()))

        try:
            alerts = await self._official_alert_provider.get_alerts(location, period)
            alert_items = _deliverable_alerts(tuple(alerts), location, period, self._now())
        except Exception:  # noqa: BLE001 - optional alert providers must not block the forecast.
            unavailable = OfficialAlertsResult(status="unavailable", items=())
            try:
                await self._cache.set(
                    cache_key,
                    CacheEntry(value=_official_alerts_to_cache(unavailable), is_stale=False),
                    _OFFICIAL_ALERTS_FAILURE_FRESH_TTL_SECONDS,
                    _OFFICIAL_ALERTS_FAILURE_STALE_TTL_SECONDS,
                )
            except Exception:  # noqa: BLE001 - optional cache must not block the forecast.
                return unavailable
            return unavailable
        available = OfficialAlertsResult(status="available", items=alert_items)
        try:
            await self._cache.set(
                cache_key,
                CacheEntry(value=_official_alerts_to_cache(available), is_stale=False),
                _OFFICIAL_ALERTS_FRESH_TTL_SECONDS,
                _OFFICIAL_ALERTS_STALE_TTL_SECONDS,
            )
        except Exception:  # noqa: BLE001 - optional cache must not block the forecast.
            return replace(available, items=_deliverable_alerts(
                available.items, location, period, self._now()))
        return replace(available, items=_deliverable_alerts(
            available.items, location, period, self._now()))

    def _metrics_record_cache(self, status: str) -> None:
        if self._metrics is not None:
            self._metrics.record_cache_status(status)

    def _metrics_record_provider(self, provider: str, duration_seconds: float, outcome: str) -> None:
        if self._metrics is not None:
            self._metrics.record_provider_request(provider, duration_seconds, outcome)

    def _metrics_record_upstream_error(self) -> None:
        if self._metrics is not None:
            self._metrics.record_upstream_error()

    def _metrics_record_lock_contention(self) -> None:
        if self._metrics is not None:
            self._metrics.record_lock_contention()

    def _metrics_record_lock_timeout(self) -> None:
        if self._metrics is not None:
            self._metrics.record_lock_timeout()


def _geo_key(location_text: str) -> str:
    return f"geo:v1:{quote(location_text.casefold(), safe='')}"


def _forecast_key(
    location: CanonicalLocation, period: DatePeriod,
    provider_identity: str = "https://api.open-meteo.com",
    calibration_profile: str = "disabled",
) -> str:
    identity = json.dumps(
        [location.latitude, location.longitude, period.start.isoformat(), period.end.isoformat(),
         "normalization-v2", provider_identity.rstrip("/"), calibration_profile],
        separators=(",", ":"), allow_nan=False,
    )
    return "forecast:v2:" + hashlib.sha256(identity.encode()).hexdigest()


def _official_alerts_key(location: CanonicalLocation, period: DatePeriod) -> str:
    identity = json.dumps(
        [
            location.latitude,
            location.longitude,
            period.start.isoformat(),
            period.end.isoformat(),
            location.timezone,
            "inmet-alerts-v2",
        ],
        separators=(",", ":"),
        allow_nan=False,
    )
    return "official-alerts:v1:" + hashlib.sha256(identity.encode()).hexdigest()


def _deliverable_alerts(
    alerts: tuple[OfficialAlert, ...], location: CanonicalLocation, period: DatePeriod, now: datetime,
) -> tuple[OfficialAlert, ...]:
    zone = ZoneInfo(location.timezone)
    start = datetime.combine(period.start, datetime.min.time(), zone)
    end = datetime.combine(period.end + timedelta(days=1), datetime.min.time(), zone)
    result = []
    for alert in alerts:
        if (alert.effective_at.tzinfo is None or alert.expires_at is None
                or alert.expires_at.tzinfo is None or alert.expires_at <= alert.effective_at):
            raise ValueError("official alert has unknown or invalid validity")
        if alert.expires_at > now and alert.effective_at < end and alert.expires_at > start:
            result.append(alert)
    return tuple(result)


def _official_alerts_to_cache(result: OfficialAlertsResult) -> dict[str, object]:
    return {
        "status": result.status,
        "items": [
            {
                "source": alert.source,
                "event": alert.event,
                "severity": alert.severity,
                "effective_at": alert.effective_at.isoformat(),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
                "geographic_scope": alert.geographic_scope,
                "source_url": alert.source_url,
            }
            for alert in result.items
        ],
    }


def _official_alerts_from_cache(value: object) -> OfficialAlertsResult | None:
    if not isinstance(value, Mapping):
        return None
    status = value.get("status")
    items = value.get("items")
    if status not in {"available", "unavailable"} or not isinstance(items, list):
        return None
    if status == "unavailable" and items:
        return None
    alerts: list[OfficialAlert] = []
    for item in items:
        if not isinstance(item, Mapping):
            return None
        source = _string(item.get("source"))
        event = _string(item.get("event"))
        severity = _string(item.get("severity"))
        effective_at = _datetime(item.get("effective_at"))
        expires_at_value = item.get("expires_at")
        expires_at = None if expires_at_value is None else _datetime(expires_at_value)
        geographic_scope = _string(item.get("geographic_scope"))
        source_url_value = item.get("source_url")
        source_url = None if source_url_value is None else _string(source_url_value)
        if (
            source is None
            or event is None
            or severity is None
            or effective_at is None
            or expires_at is None
            or (expires_at is not None and effective_at is not None and expires_at <= effective_at)
            or (expires_at_value is not None and expires_at is None)
            or geographic_scope is None
            or (source_url_value is not None and source_url is None)
        ):
            return None
        alerts.append(
            OfficialAlert(
                source=source,
                event=event,
                severity=severity,
                effective_at=effective_at,
                expires_at=expires_at,
                geographic_scope=geographic_scope,
                source_url=source_url,
            )
        )
    return OfficialAlertsResult(status=cast(Literal["available", "unavailable"], status), items=tuple(alerts))


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
    daily = tuple(
        replace(
            day,
            conditions=tuple(_response_condition(condition, unit) for condition in day.conditions),
        )
        for day in assessment.daily
    )
    return replace(assessment, conditions=conditions, daily=daily)


def _risk_overview(
    forecast_risk: RiskAssessment,
    official_alerts: OfficialAlertsResult,
    period: DatePeriod,
    timezone: str,
) -> RiskOverview:
    """Build the user-facing risk priority without hiding the heuristic result."""

    if not official_alerts.items:
        return RiskOverview(
            level=forecast_risk.level,
            source="forecast_heuristic",
            peak_days=forecast_risk.peak_days,
        )

    alert_level = max(
        (_official_alert_level(alert.severity) for alert in official_alerts.items),
        key=_risk_rank,
    )
    level = max((forecast_risk.level, alert_level), key=_risk_rank)
    alert_days: set[date] = set()
    zone = ZoneInfo(timezone)
    for alert in official_alerts.items:
        start = alert.effective_at.astimezone(zone).date()
        end = (alert.expires_at.astimezone(zone).date() if alert.expires_at else start)
        current = max(start, period.start)
        last = min(end, period.end)
        while current <= last:
            alert_days.add(current)
            current += timedelta(days=1)

    return RiskOverview(
        level=level,
        source="official_alert",
        peak_days=tuple(sorted(set(forecast_risk.peak_days).union(alert_days))),
    )


def _official_alert_level(severity: str) -> Literal["low", "moderate", "high"]:
    normalized = severity.casefold()
    if any(marker in normalized for marker in ("extreme", "severe", "high", "red", "grave")):
        return "high"
    return "moderate"


def _risk_rank(level: str) -> int:
    return {"low": 0, "moderate": 1, "high": 2}[level]


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
