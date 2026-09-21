"""IP-01: the spec formula, domain separation, canonicalization, and fail-closed."""

import hmac
from unittest.mock import AsyncMock

import pytest

from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter


def test_production_cannot_be_constructed_without_key():
    for environment in ("production", " PRODUCTION "):
        with pytest.raises(ValueError, match="required in production"):
            RedisRateLimiter(AsyncMock(), environment=environment)


@pytest.mark.parametrize("key", [b"", b"x" * 31, b"x" * 33, "x" * 32])
def test_hmac_requires_32_binary_bytes(key):
    with pytest.raises(ValueError, match="32 bytes"):
        RedisRateLimiter(AsyncMock(), identity_key=key)


async def test_spec_hmac_digest_is_same_across_workers_and_never_contains_ip():
    redis = AsyncMock()
    redis.eval.return_value = [1, 9, 0]
    key = bytes(range(32))
    for identity in ("2001:db8::7", "2001:0db8:0:0:0:0:0:7"):
        limiter = RedisRateLimiter(redis, environment="production", identity_key=key)
        decision = await limiter.allow(identity, 60, 60, 10)
        assert decision.allowed and decision.remaining == 9 and decision.retry_after_seconds == 0
    expected = hmac.digest(key, b"climaprev-ip-v1|production|2001:db8::7", "sha256").hex()
    stored = [call.args[2] for call in redis.eval.call_args_list]
    assert stored == [f"climaprev:production:rate-limit:v2:{expected}"] * 2
    assert all("2001:db8" not in value for value in stored)


def test_key_environment_and_distinct_ip_are_separated():
    first = RedisRateLimiter(AsyncMock(), environment="production", identity_key=b"a" * 32)
    other = RedisRateLimiter(AsyncMock(), environment="production", identity_key=b"b" * 32)
    test = RedisRateLimiter(AsyncMock(), environment="test", identity_key=b"a" * 32)
    keys = {first._redis_key("198.51.100.1"), other._redis_key("198.51.100.1"),
            test._redis_key("198.51.100.1"), first._redis_key("198.51.100.2")}
    assert len(keys) == 4
    assert first._redis_key("not-an-ip") == first._redis_key("unknown")


@pytest.mark.parametrize("environment", ["development", "test", "load"])
def test_synthetic_nonproduction_can_keep_v1(environment):
    limiter = RedisRateLimiter(AsyncMock(), environment=environment)
    assert limiter._redis_key("198.51.100.1") == f"climaprev:{environment}:rate-limit:v1:198.51.100.1"
