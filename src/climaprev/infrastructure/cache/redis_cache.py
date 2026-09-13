from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from redis.exceptions import RedisError

from climaprev.application.ports import CacheEntry
from climaprev.infrastructure.errors import DependencyUnavailable
from climaprev.infrastructure.redis_delay import RedisConnection


class RedisCache:
    def __init__(self, redis: RedisConnection, *, environment: str = "development",
                 clock: Callable[[], float] = time.time) -> None:
        self._redis = redis
        self._environment = environment
        self._clock = clock

    async def get(self, key: str) -> CacheEntry | None:
        try:
            raw = await self._redis.get(self._redis_key(key))
        except RedisError as error:
            raise DependencyUnavailable from error
        if raw is None:
            return None

        envelope = cast(dict[str, object], json.loads(raw))
        now = self._clock()
        fresh_until = cast(float, envelope["fresh_until"])
        stale_until = cast(float, envelope["stale_until"])
        if now >= stale_until:
            return None

        return CacheEntry(value=envelope["value"], is_stale=now >= fresh_until,
                          expires_at=datetime.fromtimestamp(stale_until, UTC))

    async def set(
        self,
        key: str,
        value: CacheEntry,
        fresh_ttl_seconds: int,
        stale_ttl_seconds: int,
    ) -> None:
        created_at = self._clock()
        envelope = {
            "created_at": created_at,
            "fresh_until": created_at + fresh_ttl_seconds,
            "stale_until": created_at + stale_ttl_seconds,
            "value": value.value,
        }
        try:
            await self._redis.set(
                self._redis_key(key),
                json.dumps(envelope, separators=(",", ":")),
                ex=stale_ttl_seconds,
            )
        except RedisError as error:
            raise DependencyUnavailable from error

    def _redis_key(self, key: str) -> str:
        return f"climaprev:{self._environment}:{key}"
