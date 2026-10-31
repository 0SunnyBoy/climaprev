"""Forecast recovery, cache freshness and distributed refresh ownership."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from random import uniform
from time import monotonic, perf_counter
from typing import Literal

from climaprev.application.cache_codec import decode_forecast, encode_forecast
from climaprev.application.errors import (
    DependencyUnavailable,
    LockOwnershipLost,
    ProviderTransientError,
    WeatherProviderUnavailable,
)
from climaprev.application.ports import (
    CacheEntry,
    CachePort,
    LockPort,
    MetricsPort,
    WeatherProviderPort,
)
from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.models import CanonicalLocation, DatePeriod, NormalizedForecast

_FORECAST_FRESH_TTL_SECONDS = 10 * 60
_FORECAST_STALE_TTL_SECONDS = 15 * 60
_LOCK_TTL_SECONDS = 10
_LOCK_HEARTBEAT_SECONDS = _LOCK_TTL_SECONDS / 2
_LOCK_WAITER_DEADLINE_SECONDS = 30
_LOCK_INITIAL_BACKOFF_SECONDS = 0.05
_LOCK_MAX_BACKOFF_SECONDS = 1.0
_LOCK_BACKOFF_FACTOR = 2.0
_LOCK_BACKOFF_JITTER = 0.25
_LOCK_MAX_ATTEMPTS = 64


@dataclass(frozen=True, slots=True)
class _CachedForecast:
    forecast: NormalizedForecast
    expires_at: datetime


class CachedForecastProvider:
    def __init__(
        self, *, weather_provider: WeatherProviderPort, cache: CachePort, lock: LockPort,
        calibration: ForecastCalibration | None = None, metrics: MetricsPort | None = None,
        provider_identity: str = "https://api.open-meteo.com",
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._weather_provider = weather_provider
        self._cache = cache
        self._lock = lock
        self._calibration = calibration or ForecastCalibration.disabled()
        self._metrics = metrics
        self._provider_identity = provider_identity.rstrip("/")
        self._now = now

    async def get(
        self, location: CanonicalLocation, period: DatePeriod,
    ) -> tuple[NormalizedForecast, Literal["hit", "miss", "stale"], datetime | None]:
        key = forecast_cache_key(location, period, self._provider_identity, self._calibration.profile_version)
        cached = await self._read_forecast(key, location, period)
        if cached is not None and not cached.forecast.is_stale:
            self._metrics_record_cache("hit")
            return cached.forecast, "hit", None
        stale_forecast = cached if cached is not None and cached.forecast.is_stale else None

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
            if cached_after_lock is not None and not cached_after_lock.forecast.is_stale:
                self._metrics_record_cache("hit")
                return cached_after_lock.forecast, "hit", None
            if cached_after_lock is not None and cached_after_lock.forecast.is_stale:
                stale_forecast = cached_after_lock

            try:
                started_at = perf_counter()
                try:
                    forecast = await self._forecast_with_lock_heartbeat(key, token, location, period)
                    forecast = self._calibration.apply(forecast)
                except Exception:
                    if self._metrics is not None:
                        self._metrics.record_provider_request(
                            "open-meteo", perf_counter() - started_at, "error"
                        )
                        self._metrics.record_upstream_error()
                    raise
                else:
                    if self._metrics is not None:
                        self._metrics.record_provider_request(
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
                CacheEntry(value=encode_forecast(canonical_forecast), is_stale=False),
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
                if self._metrics is not None:
                    self._metrics.record_lock_contention()
                contended = True

            cached = await self._read_forecast(key, location, period)
            if cached is not None and not cached.forecast.is_stale:
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
        forecast = decode_forecast(entry.value, location, period)
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

    def _metrics_record_cache(self, status: str) -> None:
        if self._metrics is not None:
            self._metrics.record_cache_status(status)

    def _metrics_record_lock_timeout(self) -> None:
        if self._metrics is not None:
            self._metrics.record_lock_timeout()


def forecast_cache_key(
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


async def _cancel_and_await(task: asyncio.Task[object]) -> None:
    if not task.done():
        task.cancel()
    # Cleanup consumes task failures; the selected result above owns error propagation.
    with suppress(asyncio.CancelledError, Exception):
        await task
