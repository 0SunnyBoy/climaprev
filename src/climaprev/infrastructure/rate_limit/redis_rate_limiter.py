from __future__ import annotations

import time
from typing import cast

from redis.exceptions import RedisError

from climaprev.application.ports import RateLimitDecision
from climaprev.infrastructure.errors import DependencyUnavailable
from climaprev.infrastructure.redis_delay import RedisConnection

_ALLOW_SCRIPT = """
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_per_millisecond = tonumber(ARGV[3])
local state = redis.call('HMGET', KEYS[1], 'tokens', 'updated_at')
local tokens = tonumber(state[1])
local updated_at = tonumber(state[2])

if tokens == nil then
    tokens = capacity
    updated_at = now
else
    local elapsed = math.max(0, now - updated_at)
    tokens = math.min(capacity, tokens + elapsed * refill_per_millisecond)
    updated_at = now
end

local allowed = tokens >= 1
if allowed then
    tokens = tokens - 1
end

redis.call('HSET', KEYS[1], 'tokens', tokens, 'updated_at', updated_at)
redis.call('PEXPIRE', KEYS[1], math.ceil(capacity / refill_per_millisecond))

local retry_after_seconds = 0
if not allowed then
    retry_after_seconds = math.ceil((1 - tokens) / refill_per_millisecond / 1000)
end

return {allowed and 1 or 0, math.floor(tokens), retry_after_seconds}
"""


class RedisRateLimiter:
    def __init__(self, redis: RedisConnection, *, environment: str = "development") -> None:
        self._redis = redis
        self._environment = environment

    async def allow(
        self,
        identity: str,
        limit: int,
        window_seconds: int,
        burst: int,
    ) -> RateLimitDecision:
        refill_per_millisecond = limit / (window_seconds * 1000)
        try:
            response = cast(
                list[int],
                await self._redis.eval(
                    _ALLOW_SCRIPT,
                    1,
                    self._redis_key(identity),
                    str(int(time.time() * 1000)),
                    str(burst),
                    str(refill_per_millisecond),
                ),
            )
        except RedisError as error:
            raise DependencyUnavailable from error

        return RateLimitDecision(
            allowed=response[0] == 1,
            remaining=response[1],
            retry_after_seconds=response[2],
        )

    def _redis_key(self, identity: str) -> str:
        return f"climaprev:{self._environment}:rate-limit:v1:{identity}"
