import asyncio
import os
from hashlib import sha256
from urllib.parse import urlsplit

import httpx
import pytest
from redis.asyncio import Redis

from climaprev.application.errors import DependencyUnavailable, ProviderRateLimited
from climaprev.config import Settings
from climaprev.infrastructure.http.client import AsyncJsonHttpClient
from climaprev.infrastructure.providers.open_meteo import OpenMeteoGeocodingClient
from climaprev.infrastructure.rate_limit.provider_budget import ProviderBudget
from tests.security_fixtures import isolated_settings


@pytest.fixture
async def budget():
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    settings = isolated_settings(
        redis_url=os.environ["REDIS_URL"],
        provider_budget_capacity=2,
        provider_budget_refill=2,
        provider_budget_window_seconds=60,
    )
    try:
        yield redis, settings, ProviderBudget(redis, settings)
    finally:
        await redis.aclose()


async def test_two_instances_limit_ten_concurrent_http_attempts_to_two(budget) -> None:
    redis, settings, first = budget
    second = ProviderBudget(redis, settings)
    sent = []

    def respond(request):
        sent.append(request.url.path)
        return httpx.Response(200, json={"allowed": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        clients = [
            AsyncJsonHttpClient(http, settings, before_send=item.consume)
            for item in (first, second)
        ]
        results = await asyncio.gather(
            *(clients[i % 2].get_json(settings.forecast_base_url + "/x", {}) for i in range(10)),
            return_exceptions=True,
        )
    assert len(sent) == 2
    assert sum(result == {"allowed": True} for result in results) == 2
    assert sum(isinstance(result, ProviderRateLimited) for result in results) == 8


async def test_refill_allows_exactly_one_new_attempt_after_thirty_seconds(
    budget, monkeypatch
) -> None:
    _, settings, quota = budget
    clock = [1000.0]
    monkeypatch.setattr(
        "climaprev.infrastructure.rate_limit.redis_rate_limiter.time.time", lambda: clock[0]
    )
    await quota.consume(settings.forecast_base_url + "/x")
    await quota.consume(settings.forecast_base_url + "/x")
    with pytest.raises(ProviderRateLimited):
        await quota.consume(settings.forecast_base_url + "/x")
    clock[0] += 30
    await quota.consume(settings.forecast_base_url + "/x")
    with pytest.raises(ProviderRateLimited):
        await quota.consume(settings.forecast_base_url + "/x")


async def test_geocoding_retries_each_consume_budget_and_never_send_third(budget) -> None:
    _, settings, quota = budget
    attempts = []

    def respond(request):
        attempts.append(request.url.path)
        return httpx.Response(503, json={"private": "sentinel"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        geocoder = OpenMeteoGeocodingClient(http, settings, before_send=quota.consume)
        with pytest.raises(ProviderRateLimited, match="budget exhausted"):
            await geocoder.resolve("Town")
    assert attempts == ["/v1/search", "/v1/search"]


async def test_unavailable_redis_never_bypasses_budget() -> None:
    redis = Redis.from_url("redis://redis:6399/0", socket_connect_timeout=0.1)
    quota = ProviderBudget(redis, Settings())
    sent = []
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: sent.append(request))
    ) as http:
        client = AsyncJsonHttpClient(http, Settings(), before_send=quota.consume)
        with pytest.raises(DependencyUnavailable):
            await client.get_json("https://forecast.test", {})
    await redis.aclose()
    assert sent == []


async def test_runtime_cache_hit_spends_nothing_and_new_location_is_denied(budget) -> None:
    import respx

    from climaprev.main import create_app
    from tests.contract.providers.test_open_meteo_payload import valid_forecast_payload

    redis, settings, _ = budget
    settings.provider_budget_capacity = 1
    app = create_app(settings)
    params = {
        "latitude": "-22.90642",
        "longitude": "-43.18223",
        "start_date": "2026-08-28",
        "end_date": "2026-08-29",
    }
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        with respx.mock as mock:
            forecast = mock.get(settings.forecast_base_url + "/v1/forecast").respond(
                200, json=valid_forecast_payload()
            )
            first = await client.get("/api/v1/risk", params=params)
            destination = sha256(urlsplit(settings.forecast_base_url).netloc.encode()).hexdigest()
            keys = [
                key
                async for key in redis.scan_iter(
                    f"climaprev:{settings.environment}:provider-budget:rate-limit:v1:{destination}"
                )
            ]
            assert len(keys) == 1
            before = await redis.hgetall(keys[0])
            cached = await client.get("/api/v1/risk", params=params)
            after = await redis.hgetall(keys[0])
            denied = await client.get("/api/v1/risk", params={**params, "latitude": "-22"})
    assert first.status_code == 200
    assert cached.status_code == 200
    assert cached.json()["days"] == first.json()["days"]
    assert before == after
    assert denied.status_code == 503
    assert denied.json()["error"]["code"] == "WEATHER_PROVIDER_UNAVAILABLE"
    assert forecast.call_count == 1
