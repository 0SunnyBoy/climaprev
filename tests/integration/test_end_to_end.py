from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import pytest
import respx

from climaprev.config import Settings
from climaprev.main import create_app
from tests.contract.providers.test_open_meteo_payload import (
    valid_forecast_payload,
    valid_geocoding_payload,
)


@asynccontextmanager
async def end_to_end_client() -> AsyncIterator[tuple[httpx.AsyncClient, object]]:
    app = create_app(
        Settings(
            redis_url=os.environ["REDIS_URL"],
            environment=f"e2e-{uuid4().hex}",
            rate_limit=1_000,
            rate_limit_burst=1_000,
        )
    )
    async with app.router.lifespan_context(app):
        await app.state.redis.flushdb()
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client, app


@pytest.mark.asyncio
async def test_end_to_end_uses_real_redis_and_never_calls_open_meteo_after_cache_warmup(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="climaprev.request")
    async with end_to_end_client() as (client, app):
        settings = app.state.settings
        with respx.mock(assert_all_called=True) as mock:
            geocoding = mock.get(f"{settings.geocoding_base_url}/v1/search").respond(
                200, json=valid_geocoding_payload()
            )
            forecast = mock.get(f"{settings.forecast_base_url}/v1/forecast").respond(
                200, json=valid_forecast_payload()
            )
            first = await client.get(
                "/api/v1/risk",
                    params={
                        "location_text": "Sensitive Rio",
                        "start_date": "2026-08-28",
                        "end_date": "2026-08-29",
                    },
                headers={"X-Request-ID": "e2e-cache"},
            )
            cached_fahrenheit = await client.get(
                "/api/v1/risk",
                params={
                    "location_text": "Sensitive Rio",
                    "start_date": "2026-08-28",
                    "end_date": "2026-08-29",
                    "temperature_unit": "fahrenheit",
                },
            )

    assert first.status_code == 200, first.text
    assert first.headers["x-request-id"] == "e2e-cache"
    assert first.json()["official_alerts"] == {"status": "unavailable", "items": []}
    assert "estimativa" in first.json()["disclaimer"].lower()
    assert cached_fahrenheit.status_code == 200, cached_fahrenheit.text
    assert cached_fahrenheit.json()["temperature_unit"] == "fahrenheit"
    assert cached_fahrenheit.json()["days"][0]["temperature_max"] == 77.0
    assert geocoding.call_count == 1
    assert forecast.call_count == 1
    snapshot = app.state.metrics.snapshot()
    assert snapshot["cache_misses_total"] == 1
    assert snapshot["cache_hits_total"] == 1
    assert snapshot["weather_provider_requests_total"]["open-meteo|success"] == 1
    log_records = [json.loads(record.message) for record in caplog.records]
    assert all("Sensitive Rio" not in record.message for record in caplog.records)
    assert log_records[-1]["cache"] == "hit"
    assert log_records[-1]["request_id"] == cached_fahrenheit.headers["x-request-id"]


@pytest.mark.asyncio
async def test_end_to_end_supports_coordinates_fahrenheit_and_health_with_real_redis() -> None:
    async with end_to_end_client() as (client, app):
        settings = app.state.settings
        with respx.mock(assert_all_called=True) as mock:
            forecast = mock.get(f"{settings.forecast_base_url}/v1/forecast").respond(
                200, json=valid_forecast_payload()
            )
            live = await client.get("/health/live")
            ready = await client.get("/health/ready")
            response = await client.get(
                "/api/v1/risk",
                params={
                    "latitude": "-22.90642",
                    "longitude": "-43.18223",
                    "start_date": "2026-08-28",
                    "end_date": "2026-08-29",
                    "temperature_unit": "fahrenheit",
                },
            )

    assert live.json() == {"status": "live"}
    assert ready.json() == {"status": "ready"}
    assert response.status_code == 200, response.text
    assert response.json()["location"]["source"] == "coordinates"
    assert response.json()["temperature_unit"] == "fahrenheit"
    assert response.json()["days"][0]["temperature_min"] == 60.8
    assert forecast.call_count == 1
