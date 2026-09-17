from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.infrastructure.cache.redis_lock import RedisLock
from climaprev.infrastructure.errors import DependencyUnavailable


@pytest.fixture
async def redis() -> Redis:
    client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.integration
async def test_lock_rejects_second_token_and_only_owner_can_release(redis: Redis) -> None:
    lock = RedisLock(redis, environment="integration")
    key = f"forecast:v1:{uuid4().hex}"

    token = await lock.acquire(key)

    assert token is not None
    assert await lock.acquire(key) is None
    assert await lock.release(key, "other-token") is False
    assert await lock.release(key, token) is True
    assert await lock.acquire(key) is not None


@pytest.mark.integration
async def test_lock_expires_after_its_ttl(redis: Redis) -> None:
    lock = RedisLock(redis, environment="integration")
    key = f"forecast:v1:{uuid4().hex}"

    assert await lock.acquire(key, ttl_seconds=1) is not None


@pytest.mark.integration
async def test_lock_refreshes_only_for_its_owner(redis: Redis) -> None:
    lock = RedisLock(redis, environment="integration")
    key = f"forecast:v1:{uuid4().hex}"

    token = await lock.acquire(key, ttl_seconds=1)

    assert token is not None
    assert await lock.refresh(key, "other-token", ttl_seconds=1) is False
    await asyncio.sleep(0.6)
    assert await lock.refresh(key, token, ttl_seconds=1) is True

    await asyncio.sleep(0.6)

    assert await lock.acquire(key, ttl_seconds=1) is None

    await asyncio.sleep(1.1)

    assert await lock.acquire(key, ttl_seconds=1) is not None


@pytest.mark.integration
async def test_concurrent_lock_acquires_grant_exactly_one_token(redis: Redis) -> None:
    lock = RedisLock(redis, environment="integration")
    key = f"forecast:v1:{uuid4().hex}"

    tokens = await asyncio.gather(*(lock.acquire(key) for _ in range(20)))

    granted = [token for token in tokens if token is not None]
    assert len(granted) == 1


@pytest.mark.integration
async def test_lock_acquire_raises_dependency_unavailable_when_redis_cannot_connect() -> None:
    unavailable_redis = Redis.from_url(
        "redis://redis:6399/0",
        decode_responses=True,
        socket_connect_timeout=0.1,
    )
    lock = RedisLock(unavailable_redis, environment="integration")
    try:
        with pytest.raises(DependencyUnavailable):
            await lock.acquire("forecast:v1:unavailable")
    finally:
        await unavailable_redis.aclose()


@pytest.mark.integration
async def test_lock_release_raises_dependency_unavailable_when_redis_cannot_connect() -> None:
    unavailable_redis = Redis.from_url(
        "redis://redis:6399/0",
        decode_responses=True,
        socket_connect_timeout=0.1,
    )
    lock = RedisLock(unavailable_redis, environment="integration")
    try:
        with pytest.raises(DependencyUnavailable):
            await lock.release("forecast:v1:unavailable", "token")
    finally:
        await unavailable_redis.aclose()
