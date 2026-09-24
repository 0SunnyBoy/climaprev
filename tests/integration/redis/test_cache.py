from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.application.ports import CacheEntry
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.errors import DependencyUnavailable


@pytest.fixture
async def redis() -> Redis:
    client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.integration
async def test_cache_returns_miss_fresh_stale_then_expired_entry(redis: Redis) -> None:
    cache = RedisCache(redis, environment="integration")
    key = f"forecast:v1:-22.9:-43.1:2026-08-28:2026-08-29:{uuid4().hex}"

    assert await cache.get(key) is None

    await cache.set(
        key,
        CacheEntry(value={"temperature_c": 24.5}, is_stale=False),
        fresh_ttl_seconds=1,
        stale_ttl_seconds=3,
    )

    fresh = await cache.get(key)
    assert fresh is not None
    expires_at = fresh.expires_at
    assert expires_at is not None and expires_at > datetime.now(UTC)
    assert fresh == CacheEntry(value={"temperature_c": 24.5}, is_stale=False, expires_at=expires_at)

    await asyncio.sleep(1.1)

    assert await cache.get(key) == CacheEntry(
        value={"temperature_c": 24.5}, is_stale=True, expires_at=expires_at)

    await asyncio.sleep(2.1)

    assert await cache.get(key) is None


@pytest.mark.integration
async def test_cache_uses_environment_versioned_namespace_json_envelope_and_stale_ttl(
    redis: Redis,
) -> None:
    cache = RedisCache(redis, environment="integration")
    key = f"geo:v1:{uuid4().hex}"

    await cache.set(
        key,
        CacheEntry(value={"latitude": -22.9064, "longitude": -43.1822}, is_stale=False),
        fresh_ttl_seconds=60,
        stale_ttl_seconds=90,
    )

    redis_key = f"climaprev:integration:{key}"
    raw = await redis.get(redis_key)

    assert raw is not None
    envelope = json.loads(raw)
    assert envelope["value"] == {"latitude": -22.9064, "longitude": -43.1822}
    assert envelope["created_at"] < envelope["fresh_until"] < envelope["stale_until"]
    assert 0 < await redis.ttl(redis_key) <= 90


@pytest.mark.integration
async def test_cache_get_raises_dependency_unavailable_when_redis_cannot_connect() -> None:
    unavailable_redis = Redis.from_url(
        "redis://redis:6399/0",
        decode_responses=True,
        socket_connect_timeout=0.1,
    )
    cache = RedisCache(unavailable_redis, environment="integration")
    try:
        with pytest.raises(DependencyUnavailable):
            await cache.get("geo:v1:unavailable")
    finally:
        await unavailable_redis.aclose()


@pytest.mark.integration
async def test_cache_set_raises_dependency_unavailable_when_redis_cannot_connect() -> None:
    unavailable_redis = Redis.from_url(
        "redis://redis:6399/0",
        decode_responses=True,
        socket_connect_timeout=0.1,
    )
    cache = RedisCache(unavailable_redis, environment="integration")
    try:
        with pytest.raises(DependencyUnavailable):
            await cache.set(
                "geo:v1:unavailable",
                CacheEntry(value={"latitude": -22.9064}, is_stale=False),
                fresh_ttl_seconds=60,
                stale_ttl_seconds=90,
            )
    finally:
        await unavailable_redis.aclose()
