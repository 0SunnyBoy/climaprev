from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.infrastructure.errors import DependencyUnavailable
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter


@pytest.fixture
async def redis() -> Redis:
    client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.integration
async def test_rate_limit_is_shared_between_instances_and_reports_remaining(redis: Redis) -> None:
    first_instance = RedisRateLimiter(redis, environment="integration")
    second_instance = RedisRateLimiter(redis, environment="integration")
    identity = f"127.0.0.1:{uuid4().hex}"

    first = await first_instance.allow(identity, limit=60, window_seconds=60, burst=10)
    second = await second_instance.allow(identity, limit=60, window_seconds=60, burst=10)

    assert first.allowed is True
    assert first.remaining == 9
    assert second.allowed is True
    assert second.remaining == 8


@pytest.mark.integration
async def test_rate_limit_enforces_atomic_burst_and_returns_retry_after(redis: Redis) -> None:
    limiter = RedisRateLimiter(redis, environment="integration")
    identity = f"127.0.0.1:{uuid4().hex}"

    decisions = await asyncio.gather(
        *(limiter.allow(identity, limit=60, window_seconds=60, burst=10) for _ in range(11))
    )

    allowed = [decision for decision in decisions if decision.allowed]
    denied = [decision for decision in decisions if not decision.allowed]
    assert len(allowed) == 10
    assert all(decision.remaining >= 0 for decision in decisions)
    assert len(denied) == 1
    assert denied[0].remaining == 0
    assert denied[0].retry_after_seconds == 1


@pytest.mark.integration
async def test_rate_limit_state_has_a_ttl(redis: Redis) -> None:
    limiter = RedisRateLimiter(redis, environment="integration")
    identity = f"127.0.0.1:{uuid4().hex}"

    await limiter.allow(identity, limit=60, window_seconds=60, burst=10)

    assert 0 < await redis.pttl(f"climaprev:integration:rate-limit:v1:{identity}") <= 10_000


@pytest.mark.integration
async def test_rate_limit_raises_dependency_unavailable_when_redis_cannot_connect() -> None:
    unavailable_redis = Redis.from_url(
        "redis://redis:6399/0",
        decode_responses=True,
        socket_connect_timeout=0.1,
    )
    limiter = RedisRateLimiter(unavailable_redis, environment="integration")
    try:
        with pytest.raises(DependencyUnavailable):
            await limiter.allow("127.0.0.1", limit=60, window_seconds=60, burst=10)
    finally:
        await unavailable_redis.aclose()
