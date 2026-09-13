import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.application.ports import CacheEntry
from climaprev.application.services import forecast_query
from climaprev.application.services.forecast_query import WeatherProviderUnavailable
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.http.client import ProviderTransientError
from tests.integration.application.test_forecast_query import (
    LOCATION, PERIOD, FakeAlerts, FakeProvider, InMemoryLock, cached_forecast, service, text_query,
)


@pytest.fixture
async def clock_cache():
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    clock = [1_800_000_000.0]
    environment = f"expiry-{uuid4().hex}"
    cache = RedisCache(redis, environment=environment, clock=lambda: clock[0])
    key = forecast_query._forecast_key(LOCATION, PERIOD)
    await cache.set(key, CacheEntry(cached_forecast(), False), 600, 900)
    try:
        yield clock, cache, redis, f"climaprev:{environment}:{key}"
    finally:
        await redis.aclose()


@pytest.mark.parametrize("elapsed,status", [(599, "hit"), (600, "stale"), (899, "stale"),
                                            (900, "unavailable")])
async def test_ttl_boundaries_use_cache_expiration_and_never_extend_it(clock_cache, elapsed, status):
    clock, cache, redis, redis_key = clock_cache
    raw = await redis.get(redis_key)
    ttl = await redis.pttl(redis_key)
    clock[0] += elapsed
    query_service = service(cache=cache, provider=FakeProvider(ProviderTransientError()),
                            now=lambda: datetime.fromtimestamp(clock[0], UTC))
    if status == "unavailable":
        with pytest.raises(WeatherProviderUnavailable):
            await query_service.execute(text_query(), "boundary")
    else:
        result = await query_service.execute(text_query(), "boundary")
        assert result.cache_status == status
        assert result.data_quality.is_stale == (status == "stale")
        assert result.days[0].temperature_max == 40
    assert await redis.get(redis_key) == raw
    assert await redis.pttl(redis_key) <= ttl


@pytest.mark.parametrize("during", ["lock", "retry", "alerts"])
async def test_stale_expiring_during_wait_is_never_delivered(clock_cache, monkeypatch, during):
    clock, cache, redis, redis_key = clock_cache
    clock[0] += 899
    lock = InMemoryLock()
    provider = FakeProvider(ProviderTransientError())
    alerts = FakeAlerts()
    if during == "lock":
        async def no_lock(*args, **kwargs):
            clock[0] += 1
            return None
        monkeypatch.setattr(lock, "acquire", no_lock)
        monkeypatch.setattr(forecast_query, "_LOCK_WAITER_DEADLINE_SECONDS", 0)
    elif during == "retry":
        async def fail_after_retry(*args, **kwargs):
            clock[0] += 1
            raise ProviderTransientError()
        monkeypatch.setattr(provider, "forecast", fail_after_retry)
    else:
        async def delayed_alerts(*args):
            clock[0] += 1
            return []
        monkeypatch.setattr(alerts, "get_alerts", delayed_alerts)
    before = await redis.get(redis_key)
    query_service = service(cache=cache, lock=lock, provider=provider, alerts=alerts,
                            now=lambda: datetime.fromtimestamp(clock[0], UTC))
    with pytest.raises(WeatherProviderUnavailable):
        await query_service.execute(text_query(), "expired-during-wait")
    assert await redis.get(redis_key) == before
