from __future__ import annotations

import secrets
from typing import cast

from redis.exceptions import RedisError

from climaprev.application.errors import DependencyUnavailable
from climaprev.infrastructure.redis_delay import RedisConnection

_RELEASE_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
"""

_REFRESH_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('EXPIRE', KEYS[1], ARGV[2])
end
return 0
"""


class RedisLock:
    def __init__(self, redis: RedisConnection, *, environment: str = "development") -> None:
        self._redis = redis
        self._environment = environment

    async def acquire(self, key: str, ttl_seconds: int = 10) -> str | None:
        token = secrets.token_urlsafe(32)
        try:
            acquired = await self._redis.set(
                self._redis_key(key),
                token,
                ex=ttl_seconds,
                nx=True,
            )
        except RedisError as error:
            raise DependencyUnavailable from error
        return token if acquired is True else None

    async def release(self, key: str, token: str) -> bool:
        try:
            deleted = cast(
                int,
                await self._redis.eval(_RELEASE_SCRIPT, 1, self._redis_key(key), token),
            )
        except RedisError as error:
            raise DependencyUnavailable from error
        return deleted == 1

    async def refresh(self, key: str, token: str, ttl_seconds: int = 10) -> bool:
        try:
            refreshed = cast(
                int,
                await self._redis.eval(
                    _REFRESH_SCRIPT,
                    1,
                    self._redis_key(key),
                    token,
                    str(ttl_seconds),
                ),
            )
        except RedisError as error:
            raise DependencyUnavailable from error
        return refreshed == 1

    def _redis_key(self, key: str) -> str:
        return f"climaprev:{self._environment}:lock:{key}"
