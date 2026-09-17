from __future__ import annotations

import pytest
import respx

from tests.contract.providers.test_open_meteo_payload import (
    valid_forecast_payload,
    valid_geocoding_payload,
)
from tests.integration.test_end_to_end import end_to_end_client

PARAMS = {"latitude": "-22.90642", "longitude": "-43.18223",
          "start_date": "2026-08-28", "end_date": "2026-08-29"}


@pytest.mark.parametrize("by_text", [False, True])
async def test_effective_timezone_survives_public_response_and_cache(by_text: bool) -> None:
    payload = valid_forecast_payload()
    payload["timezone"] = "America/Belem"
    params = dict(PARAMS)
    if by_text:
        params.pop("latitude")
        params.pop("longitude")
        params["location_text"] = "Rio"
    async with end_to_end_client() as (client, app):
        with respx.mock(assert_all_called=False) as mock:
            mock.get(f"{app.state.settings.geocoding_base_url}/v1/search").respond(
                200, json=valid_geocoding_payload())
            upstream = mock.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=payload)
            first = await client.get("/api/v1/risk", params=params)
            second = await client.get("/api/v1/risk", params=params)
    assert first.status_code == second.status_code == 200
    assert first.json()["location"]["timezone"] == "America/Belem"
    assert second.json()["location"]["timezone"] == "America/Belem"
    assert upstream.call_count == 1


@pytest.mark.parametrize("timezone", ["Invalid/Timezone", "../UTC"])
async def test_invalid_forecast_timezone_returns_sanitized_502(timezone: str) -> None:
    payload = valid_forecast_payload()
    payload["timezone"] = timezone
    async with end_to_end_client() as (client, app):
        with respx.mock:
            respx.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=payload)
            response = await client.get("/api/v1/risk", params=PARAMS)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "WEATHER_DATA_INVALID"
    assert timezone not in response.text


@pytest.mark.parametrize("section,field,value", [
    ("daily", "temperature_2m_min", float("nan")),
    ("daily", "temperature_2m_max", float("inf")),
    ("hourly", "temperature_2m", float("-inf")),
    ("hourly", "relative_humidity_2m", -1),
    ("hourly", "relative_humidity_2m", 101),
    ("daily", "precipitation_probability_max", -1),
    ("hourly", "precipitation_probability", 101),
    ("daily", "precipitation_sum", -0.1),
    ("hourly", "precipitation", -0.1),
    ("daily", "wind_speed_10m_max", -1),
    ("daily", "wind_gusts_10m_max", -1),
    ("hourly", "wind_speed_10m", -1),
    ("hourly", "wind_gusts_10m", -1),
    ("daily", "temperature_2m_min", 26),
])
async def test_weather_bounds_are_rejected_before_cache(section, field, value) -> None:
    import json

    payload = valid_forecast_payload()
    payload[section][field][0] = value
    async with end_to_end_client() as (client, app):
        with respx.mock as mock:
            upstream = mock.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, content=json.dumps(payload))
            response = await client.get("/api/v1/risk", params=PARAMS)
        keys = await app.state.redis.keys("*:forecast:*")
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "WEATHER_DATA_INVALID"
    assert upstream.call_count == 1
    assert keys == []


@pytest.mark.parametrize("value", [0, 100, None])
async def test_percentage_boundaries_and_null_are_preserved(value) -> None:
    payload = valid_forecast_payload()
    payload["hourly"]["relative_humidity_2m"] = [value] * 4
    payload["hourly"]["precipitation_probability"] = [value] * 4
    async with end_to_end_client() as (client, app):
        with respx.mock:
            respx.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=payload)
            response = await client.get("/api/v1/risk", params=PARAMS)
    assert response.status_code == 200
    assert response.json()["days"][0]["humidity_mean_pct"] == value
    assert response.json()["days"][0]["precipitation_probability_max_pct"] == value


@pytest.mark.parametrize("values,unit,expected", [
    ([19, 24, 20, 25], "celsius", 21.5),
    ([19, 24, 20, 25], "fahrenheit", 70.7),
    ([19, None, 20, 25], "celsius", 19),
    ([None, None, None, None], "celsius", None),
])
async def test_daily_temperature_mean_uses_only_non_null_samples(values, unit, expected) -> None:
    payload = valid_forecast_payload()
    payload["hourly"]["temperature_2m"] = values
    async with end_to_end_client() as (client, app):
        with respx.mock:
            respx.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=payload)
            response = await client.get("/api/v1/risk", params={**PARAMS, "temperature_unit": unit})
    assert response.status_code == 200
    result = response.json()
    assert result["days"][0]["temperature_mean"] == expected
    assert result["temperature_unit"] == unit
    assert "hourly.2026-08-28.temperature_2m.coverage" in result["data_quality"]["missing_fields"]
    assert result["days"][0]["precipitation_sum_mm"] == 1.2
