from __future__ import annotations

import asyncio
from typing import cast

from redis.asyncio import Redis


class DelayedRedis:
    """Load-profile wrapper that delays every Redis operation used by ClimaPrev."""

    def __init__(self, redis: Redis, *, delay_milliseconds: int) -> None:
        self._redis = redis
        self._delay_seconds = delay_milliseconds / 1000

    async def get(self, key: str) -> str | None:
        await self._delay()
        return cast(str | None, await self._redis.get(key))

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool | None:
        await self._delay()
        return cast(bool | None, await self._redis.set(key, value, ex=ex, nx=nx))

    async def eval(self, script: str, numkeys: int, *keys_and_args: str) -> object:
        await self._delay()
        return await self._redis.eval(script, numkeys, *keys_and_args)

    async def ping(self) -> bool:
        await self._delay()
        return await self._redis.ping()

    async def aclose(self) -> None:
        await self._redis.aclose()

    async def _delay(self) -> None:
        if self._delay_seconds:
            await asyncio.sleep(self._delay_seconds)


type RedisConnection = Redis | DelayedRedis
