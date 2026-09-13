import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.application.errors import DependencyUnavailable, ProviderTransientError, WeatherDataInvalid
from climaprev.application.services import forecast_query
from climaprev.application.services.forecast_query import WeatherProviderUnavailable
from climaprev.infrastructure.cache.redis_lock import RedisLock
from tests.integration.application.test_forecast_query import (
    FakeProvider, InMemoryCache, InMemoryLock, forecast, service, text_query,
)
from tests.integration.test_end_to_end import end_to_end_client
from tests.integration.test_evolution_data import PARAMS


class SlowProvider:
    def __init__(self):
        self.started = asyncio.Event()
        self.cancelled = False

    async def forecast(self, location, period):
        self.started.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled = True


class LostLock(InMemoryLock):
    async def refresh(self, key, token, ttl_seconds):
        return False


class FailedRelease(InMemoryLock):
    async def release(self, key, token):
        raise DependencyUnavailable()


async def test_lost_heartbeat_cancels_provider_and_returns_public_503(monkeypatch):
    monkeypatch.setattr(forecast_query, "_LOCK_HEARTBEAT_SECONDS", 0.001)
    provider = SlowProvider()
    cache = InMemoryCache()
    async with end_to_end_client() as (client, app):
        app.state.forecast_query_service = service(cache=cache, lock=LostLock(), provider=provider)
        response = await client.get("/api/v1/risk", params=PARAMS)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "WEATHER_PROVIDER_UNAVAILABLE"
    assert provider.cancelled is True
    assert not any(key.startswith("forecast:") for key in cache.entries)


@pytest.mark.parametrize("error,expected", [
    (ProviderTransientError(), WeatherProviderUnavailable),
    (WeatherDataInvalid(), WeatherDataInvalid),
])
async def test_failed_release_preserves_primary_provider_error(error, expected):
    cache = InMemoryCache()
    query_service = service(cache=cache, lock=FailedRelease(), provider=FakeProvider(error))
    with pytest.raises(expected):
        await query_service.execute(text_query(), "primary-error")
    assert not any(key.startswith("forecast:") for key in cache.entries)


async def test_release_failure_without_primary_error_is_dependency_unavailable():
    query_service = service(lock=FailedRelease(), provider=FakeProvider(forecast()))
    with pytest.raises(DependencyUnavailable):
        await query_service.execute(text_query(), "release-error")


async def test_client_cancellation_cancels_provider_and_releases_own_lock():
    provider = SlowProvider()
    lock = InMemoryLock()
    cache = InMemoryCache()
    query_service = service(cache=cache, lock=lock, provider=provider)
    task = asyncio.create_task(query_service.execute(text_query(), "cancelled-client"))
    await provider.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert provider.cancelled is True
    assert len(lock.releases) == 1
    assert lock.releases[0][1] == "lock-token"
    assert not any(key.startswith("forecast:") for key in cache.entries)


async def test_actual_lock_ownership_loss_never_deletes_another_owner(monkeypatch):
    monkeypatch.setattr(forecast_query, "_LOCK_HEARTBEAT_SECONDS", 0.001)
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    environment = f"ownership-{uuid4().hex}"
    provider = SlowProvider()
    cache = InMemoryCache()
    query_service = service(cache=cache, lock=RedisLock(redis, environment=environment),
                            provider=provider)
    task = asyncio.create_task(query_service.execute(text_query(), "lost-owner"))
    try:
        await provider.started.wait()
        keys = await redis.keys(f"climaprev:{environment}:lock:*")
        assert len(keys) == 1
        await redis.set(keys[0], "new-owner-token", ex=10)
        with pytest.raises(WeatherProviderUnavailable):
            await task
        assert await redis.get(keys[0]) == "new-owner-token"
        assert provider.cancelled is True
        assert not any(key.startswith("forecast:") for key in cache.entries)
    finally:
        await redis.aclose()


async def test_ownership_loss_does_not_fall_back_to_valid_stale(monkeypatch):
    monkeypatch.setattr(forecast_query, "_LOCK_HEARTBEAT_SECONDS", 0.001)
    cache = InMemoryCache()
    await service(cache=cache).execute(text_query(), "warm")
    key = next(key for key in cache.entries if key.startswith("forecast:"))
    cache.mark_stale(key)
    before = cache.entries[key]
    provider = SlowProvider()
    with pytest.raises(WeatherProviderUnavailable):
        await service(cache=cache, lock=LostLock(), provider=provider).execute(text_query(), "lost")
    assert cache.entries[key] == before
    assert provider.cancelled is True
