import json
import time

import httpx
import pytest
import respx

from tests.contract.providers.test_open_meteo_payload import valid_forecast_payload
from tests.integration.test_end_to_end import end_to_end_client
from tests.integration.test_evolution_data import PARAMS


@pytest.mark.parametrize("kind,status,code,attempts", [
    (429, 503, "WEATHER_PROVIDER_UNAVAILABLE", 1),
    (400, 502, "WEATHER_PROVIDER_REJECTED", 1),
    (401, 502, "WEATHER_PROVIDER_REJECTED", 1),
    (404, 502, "WEATHER_PROVIDER_REJECTED", 1),
    (503, 503, "WEATHER_PROVIDER_UNAVAILABLE", 3),
    ("timeout", 503, "WEATHER_PROVIDER_UNAVAILABLE", 3),
    ("network", 503, "WEATHER_PROVIDER_UNAVAILABLE", 3),
    ("payload", 502, "WEATHER_DATA_INVALID", 1),
])
@pytest.mark.parametrize("geocoding", [False, True])
async def test_external_failure_contract_is_sanitized(kind, status, code, attempts, geocoding):
    async with end_to_end_client() as (client, app):
        params = dict(PARAMS)
        url = f"{app.state.settings.forecast_base_url}/v1/forecast"
        if geocoding:
            params.pop("latitude")
            params.pop("longitude")
            params["location_text"] = "SentinelCity"
            url = f"{app.state.settings.geocoding_base_url}/v1/search"
        with respx.mock as mock:
            route = mock.get(url)
            if kind == "timeout":
                route.mock(side_effect=httpx.ReadTimeout("SentinelSecret"))
            elif kind == "network":
                route.mock(side_effect=httpx.ConnectError("SentinelSecret"))
            elif kind == "payload":
                route.respond(200, content="SentinelSecret")
            else:
                route.respond(kind, json={"error": "SentinelSecret"})
            response = await client.get("/api/v1/risk", params=params,
                                        headers={"X-Request-ID": "provider-contract"})
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["request_id"] == "provider-contract"
    assert response.headers["x-request-id"] == "provider-contract"
    assert "SentinelSecret" not in response.text
    assert url not in response.text
    assert route.call_count == attempts


@pytest.mark.parametrize("upstream_status,expected", [(429, 200), (400, 502)])
async def test_provider_limit_allows_valid_stale_but_rejection_does_not(upstream_status, expected):
    async with end_to_end_client() as (client, app):
        with respx.mock as mock:
            route = mock.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=valid_forecast_payload())
            initial = await client.get("/api/v1/risk", params=PARAMS)
            keys = await app.state.redis.keys(f"climaprev:{app.state.settings.environment}:forecast:*")
            assert len(keys) == 1
            value = json.loads(await app.state.redis.get(keys[0]))
            value.update(created_at=time.time() - 601, fresh_until=time.time() - 1,
                          stale_until=time.time() + 299)
            await app.state.redis.set(keys[0], json.dumps(value), ex=299)
            route.respond(upstream_status, json={"error": "SentinelSecret"})
            response = await client.get("/api/v1/risk", params=PARAMS)
    assert initial.status_code == 200
    assert response.status_code == expected
    assert route.call_count == 2
    if expected == 200:
        assert response.json()["data_quality"]["is_stale"] is True
        assert response.json()["days"][0]["temperature_max"] == 25
    else:
        assert response.json()["error"]["code"] == "WEATHER_PROVIDER_REJECTED"
    assert "SentinelSecret" not in response.text
