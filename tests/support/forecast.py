from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from time import monotonic

from climaprev.api.observability import RequestMetrics
from climaprev.application.official_alerts import OfficialAlertsNotConfiguredProvider
from climaprev.application.ports import CacheEntry
from climaprev.application.query import ForecastQuery
from climaprev.application.services.forecast_query import ForecastQueryService
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    NormalizedForecast,
    OfficialAlert,
)
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.units import TemperatureUnit

LOCATION = CanonicalLocation(
    name="Sao Paulo",
    latitude=-23.5505,
    longitude=-46.6333,
    timezone="America/Sao_Paulo",
    source="fake-geocoding",
)
PERIOD = DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 28))


def forecast(*, missing_fields: tuple[str, ...] = ()) -> NormalizedForecast:
    return NormalizedForecast(
        location=LOCATION,
        period=PERIOD,
        days=(
            DailyForecast(
                date=PERIOD.start,
                temperature_min_c=20.0,
                temperature_max_c=40.0,
                temperature_mean_c=30.0,
                humidity_mean_pct=70.0,
                precipitation_sum_mm=5.0,
                precipitation_probability_max_pct=40.0,
                precipitation_max_hourly_mm=3.0,
                wind_max_kmh=25.0,
                wind_gust_max_kmh=30.0,
                weather_code=1,
            ),
        ),
        provider="open-meteo",
        fetched_at=datetime(2026, 8, 28, 12, tzinfo=UTC),
        is_stale=False,
        missing_fields=missing_fields,
    )


def cached_forecast() -> dict[str, object]:
    return {
        "location": {
            "name": "Sao Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timezone": "America/Sao_Paulo",
            "source": "fake-geocoding",
        },
        "period": {"start": "2026-08-28", "end": "2026-08-28"},
        "days": [
            {
                "date": "2026-08-28",
                "temperature_min_c": 20.0,
                "temperature_max_c": 40.0,
                "temperature_mean_c": 30.0,
                "humidity_mean_pct": 70.0,
                "precipitation_sum_mm": 5.0,
                "precipitation_probability_max_pct": 40.0,
                "precipitation_max_hourly_mm": 3.0,
                "wind_max_kmh": 25.0,
                "wind_gust_max_kmh": 30.0,
                "weather_code": 1,
            }
        ],
        "provider": "open-meteo",
        "fetched_at": "2026-08-28T12:00:00+00:00",
        "is_stale": False,
        "missing_fields": [],
    }


class InMemoryCache:
    def __init__(self) -> None:
        self.entries: dict[str, CacheEntry] = {}
        self.set_calls: list[tuple[str, CacheEntry, int, int]] = []

    async def get(self, key: str) -> CacheEntry | None:
        entry = self.entries.get(key)
        if entry is not None and entry.expires_at is None:
            entry = replace(entry, expires_at=datetime.now(UTC) + timedelta(seconds=900))
            self.entries[key] = entry
        return entry

    async def set(
        self,
        key: str,
        value: CacheEntry,
        fresh_ttl_seconds: int,
        stale_ttl_seconds: int,
    ) -> None:
        self.entries[key] = replace(value, expires_at=datetime.now(UTC) +
                                    timedelta(seconds=stale_ttl_seconds))
        self.set_calls.append((key, value, fresh_ttl_seconds, stale_ttl_seconds))

    def mark_stale(self, key: str) -> None:
        entry = self.entries[key]
        self.entries[key] = replace(entry, is_stale=True)


class InMemoryLock:
    def __init__(
        self,
        *,
        expires_after_seconds: float | None = None,
        release_delay: float = 0.0,
    ) -> None:
        self._held = False
        self._expires_after_seconds = expires_after_seconds
        self._expires_at = 0.0
        self._release_delay = release_delay
        self.acquires: list[tuple[str, int]] = []
        self.refreshes: list[tuple[str, str, int]] = []
        self.releases: list[tuple[str, str]] = []
        self.on_acquire: Callable[[], Awaitable[None]] | None = None

    async def acquire(self, key: str, ttl_seconds: int) -> str | None:
        self.acquires.append((key, ttl_seconds))
        if self._held and monotonic() >= self._expires_at:
            self._held = False
        if self._held:
            return None
        self._held = True
        self._expires_at = monotonic() + (self._expires_after_seconds or float(ttl_seconds))
        if self.on_acquire is not None:
            await self.on_acquire()
        return "lock-token"

    async def refresh(self, key: str, token: str, ttl_seconds: int) -> bool:
        self.refreshes.append((key, token, ttl_seconds))
        if not self._held or token != "lock-token" or monotonic() >= self._expires_at:
            return False
        self._expires_at = monotonic() + (self._expires_after_seconds or float(ttl_seconds))
        return True

    async def release(self, key: str, token: str) -> bool:
        self.releases.append((key, token))
        if self._release_delay:
            await asyncio.sleep(self._release_delay)
        self._held = False
        return True


class FakeGeocoder:
    def __init__(self, location: CanonicalLocation = LOCATION) -> None:
        self.location = location
        self.texts: list[str] = []

    async def resolve(self, text: str) -> CanonicalLocation:
        self.texts.append(text)
        return self.location


class FakeProvider:
    def __init__(
        self,
        value: NormalizedForecast | Exception,
        *,
        wait: bool = False,
        wait_seconds: float = 0.0,
    ) -> None:
        self.value = value
        self.wait_seconds = 0.03 if wait else wait_seconds
        self.calls: list[tuple[CanonicalLocation, DatePeriod]] = []

    async def forecast(self, location: CanonicalLocation, period: DatePeriod) -> NormalizedForecast:
        self.calls.append((location, period))
        if self.wait_seconds:
            await asyncio.sleep(self.wait_seconds)
        if isinstance(self.value, Exception):
            raise self.value
        return replace(self.value, location=location, period=period)


class FakeAlerts:
    def __init__(
        self,
        error: Exception | None = None,
        items: tuple[OfficialAlert, ...] = (),
    ) -> None:
        self.error = error
        self.items = items
        self.calls = 0

    async def get_alerts(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> list[object]:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return list(self.items)


def service(
    *,
    cache: InMemoryCache | None = None,
    lock: InMemoryLock | None = None,
    geocoder: FakeGeocoder | None = None,
    provider: FakeProvider | None = None,
    alerts: object | None = None,
    metrics: RequestMetrics | None = None,
    provider_identity: str = "https://api.open-meteo.com",
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> ForecastQueryService:
    return ForecastQueryService(
        geocoder=geocoder or FakeGeocoder(),
        weather_provider=provider or FakeProvider(forecast()),
        cache=cache or InMemoryCache(),
        lock=lock or InMemoryLock(),
        risk_evaluator=RiskEvaluator(),
        risk_policy=RiskPolicy(),
        official_alert_provider=alerts or OfficialAlertsNotConfiguredProvider(),
        metrics=metrics,
        provider_identity=provider_identity,
        now=now,
    )


def text_query(*, unit: TemperatureUnit = TemperatureUnit.CELSIUS) -> ForecastQuery:
    return ForecastQuery(
        location_text="Sao Paulo",
        latitude=None,
        longitude=None,
        start_date=PERIOD.start,
        end_date=PERIOD.end,
        temperature_unit=unit,
    )
