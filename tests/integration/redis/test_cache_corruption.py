import json
import os
from uuid import uuid4

import pytest
import respx
from redis.asyncio import Redis

from climaprev.api.observability import RequestMetrics
from climaprev.infrastructure.cache.redis_cache import RedisCache
from tests.contract.providers.test_open_meteo_payload import valid_forecast_payload
from tests.integration.test_end_to_end import end_to_end_client
from tests.integration.test_evolution_data import PARAMS


@pytest.mark.parametrize("raw", [
    "broken-json", "[]", "null", "{}",
    '{"created_at": 1, "fresh_until": 2, "stale_until": 3}',
    '{"created_at": 1, "fresh_until": "two", "stale_until": 3, "value": {}}',
    '{"created_at": true, "fresh_until": 2, "stale_until": 3, "value": {}}',
    '{"created_at": NaN, "fresh_until": 2, "stale_until": 3, "value": {}}',
    '{"created_at": 1, "fresh_until": 2, "stale_until": Infinity, "value": {}}',
    '{"created_at": 3, "fresh_until": 2, "stale_until": 4, "value": {}}',
    '{"created_at": 1, "fresh_until": 4, "stale_until": 3, "value": {}}',
    '{"created_at": 1, "fresh_until": 2, "stale_until": 1e100, "value": {}}',
])
async def test_corrupt_cache_is_miss_with_one_fixed_counter(raw):
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    environment = f"corrupt-{uuid4().hex}"
    metrics = RequestMetrics()
    cache = RedisCache(redis, environment=environment, on_corruption=metrics.record_cache_corruption)
    try:
        await redis.set(f"climaprev:{environment}:sentinel-location", raw)
        assert await cache.get("sentinel-location") is None
        snapshot = metrics.snapshot()
        assert snapshot["cache_corruptions_total"] == 1
        assert "sentinel-location" not in json.dumps(snapshot)
    finally:
        await redis.aclose()


async def test_public_request_recovers_corrupted_forecast_without_500():
    async with end_to_end_client() as (client, app):
        with respx.mock as mock:
            provider = mock.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=valid_forecast_payload())
            first = await client.get("/api/v1/risk", params=PARAMS)
            keys = await app.state.redis.keys(f"climaprev:{app.state.settings.environment}:forecast:*")
            assert len(keys) == 1
            await app.state.redis.set(keys[0], "broken-json")
            recovered = await client.get("/api/v1/risk", params=PARAMS)
    assert first.status_code == recovered.status_code == 200
    assert recovered.json()["days"][0]["temperature_max"] == 25
    assert provider.call_count == 2
    assert app.state.metrics.snapshot()["cache_corruptions_total"] == 2
