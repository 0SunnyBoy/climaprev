from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from math import isfinite
from typing import cast

from redis.exceptions import RedisError

from climaprev.application.ports import CacheEntry
from climaprev.infrastructure.errors import DependencyUnavailable
from climaprev.infrastructure.redis_delay import RedisConnection


class RedisCache:
    def __init__(self, redis: RedisConnection, *, environment: str = "development",
                 clock: Callable[[], float] = time.time,
                 on_corruption: Callable[[], None] | None = None) -> None:
        self._redis = redis
        self._environment = environment
        self._clock = clock
        self._on_corruption = on_corruption

    async def get(self, key: str) -> CacheEntry | None:
        try:
            raw = await self._redis.get(self._redis_key(key))
        except RedisError as error:
            raise DependencyUnavailable from error
        if raw is None:
            return None

        try:
            envelope = json.loads(raw)
            if not isinstance(envelope, dict) or "value" not in envelope:
                raise ValueError("cache envelope must be an object containing value")
            timestamps = [envelope.get(field) for field in
                          ("created_at", "fresh_until", "stale_until")]
            if any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not isfinite(value) for value in timestamps):
                raise ValueError("cache timestamps must be finite numbers")
            created_at, fresh_until, stale_until = cast(list[float], timestamps)
            if not created_at <= fresh_until <= stale_until:
                raise ValueError("cache timestamps are not ordered")
            expires_at = datetime.fromtimestamp(stale_until, UTC)
        except (ValueError, TypeError, OverflowError, OSError):
            if self._on_corruption is not None:
                self._on_corruption()
            return None
        now = self._clock()
        if now >= stale_until:
            return None
        return CacheEntry(value=envelope["value"], is_stale=now >= fresh_until,
                          expires_at=expires_at)

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
