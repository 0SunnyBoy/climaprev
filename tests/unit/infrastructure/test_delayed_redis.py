from __future__ import annotations

import time

import pytest

from climaprev.config import Settings
from climaprev.infrastructure.redis_delay import DelayedRedis


class RecordingRedis:
    async def get(self, key: str) -> str:
        return key


@pytest.mark.asyncio
async def test_delayed_redis_adds_the_configured_delay_to_operations() -> None:
    redis = DelayedRedis(RecordingRedis(), delay_milliseconds=25)

    started_at = time.perf_counter()
    value = await redis.get("forecast-key")
    elapsed = time.perf_counter() - started_at

    assert value == "forecast-key"
    assert elapsed >= 0.02


def test_redis_latency_is_enabled_only_for_the_load_redis_scenario() -> None:
    delayed = Settings(
        environment="load",
        load_scenario="redis_latency",
        load_redis_operation_delay_ms=25,
    )
    ordinary = Settings(environment="load", load_scenario="warm_cache")

    assert delayed.effective_redis_operation_delay_ms == 25
    assert ordinary.effective_redis_operation_delay_ms == 0
