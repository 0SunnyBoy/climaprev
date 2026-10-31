from __future__ import annotations

import pytest
import respx

from tests.contract.providers.test_open_meteo_payload import valid_forecast_payload
from tests.integration.test_end_to_end import end_to_end_client


def civil_payload(day: str, hours: list[int], timezone: str = "UTC"):
    payload = valid_forecast_payload()
    payload["timezone"] = timezone
    payload["daily"] = {k: [day] if k == "time" else [v[0]]
                        for k, v in payload["daily"].items()}
    payload["hourly"] = {k: [f"{day}T{h:02}:00" for h in hours] if k == "time"
                         else [0] * len(hours) for k in payload["hourly"]}
    return payload


@pytest.mark.parametrize("day,hours,timezone,expected", [
    ("2026-08-28", list(range(24)), "UTC", "complete"),
    ("2026-08-28", list(range(23)), "UTC", "partial"),
    ("2026-08-28", [], "UTC", "partial"),
    ("2026-03-08", [0, 1, *range(3, 24)], "America/New_York", "complete"),
    ("2026-11-01", [0, 1, *range(1, 24)], "America/New_York", "complete"),
])
async def test_civil_hour_coverage_public_contract(day, hours, timezone, expected, monkeypatch) -> None:
    from datetime import date

    monkeypatch.setattr("climaprev.api.forecast_window.utc_today", lambda: date.fromisoformat(day))
    payload = civil_payload(day, hours, timezone)
    response = await request_payload(payload, day)
    assert response.status_code == 200
    quality = response.json()["data_quality"]
    assert quality["completeness"] == expected
    assert (f"hourly.{day}.precipitation.coverage" in quality["missing_fields"]) == (
        expected == "partial")
    assert response.json()["location"]["timezone"] == timezone
    assert response.json()["days"][0]["precipitation_max_hourly_mm"] == (0 if hours else None)


async def request_payload(payload, day="2026-08-28"):
    async with end_to_end_client() as (client, app):
        with respx.mock:
            respx.get(f"{app.state.settings.forecast_base_url}/v1/forecast").respond(
                200, json=payload)
            return await client.get("/api/v1/risk", params={"latitude": 1, "longitude": 1,
                                    "start_date": day, "end_date": day})


@pytest.mark.parametrize("mode,expected", [
    ("zero", "complete"), ("null", "partial"), ("all_null", "unavailable"),
    ("strong_partial", "partial"), ("rain_null", "partial"),
])
async def test_policy_input_completeness_and_missing_fields(mode, expected) -> None:
    payload = civil_payload("2026-08-28", list(range(24)))
    if mode in ("zero", "all_null"):
        for field in ("temperature_2m_min", "temperature_2m_max", "precipitation_sum",
                      "wind_gusts_10m_max"):
            payload["daily"][field] = [None if mode == "all_null" else 0]
    if mode == "all_null":
        payload["hourly"]["precipitation"] = [None] * 24
    if mode in ("null", "strong_partial"):
        payload["daily"]["wind_gusts_10m_max"] = [None]
    if mode == "strong_partial":
        payload["daily"]["precipitation_sum"] = [100]
    if mode == "rain_null":
        payload["hourly"]["precipitation"][5] = None
    response = await request_payload(payload)
    assert response.status_code == 200
    result = response.json()
    assert result["data_quality"]["completeness"] == expected
    if mode in ("null", "all_null", "strong_partial"):
        assert "days.2026-08-28.wind_gust_max_kmh" in result["data_quality"]["missing_fields"]
        assert result["days"][0]["wind_gust_max_kmh"] is None
    if mode == "strong_partial":
        assert result["forecast_risk"]["level"] == "high"
    if mode == "all_null":
        assert result["forecast_risk"]["conditions"] == []
    if mode == "rain_null":
        assert "hourly.2026-08-28.precipitation.coverage" in result["data_quality"]["missing_fields"]


@pytest.mark.parametrize("times", [
    ["2026-08-28T00:00", "2026-08-28T00:00"],
    ["2026-08-28T02:00", "2026-08-28T01:00"],
    ["2026-08-29T00:00"], ["2026-08-28T00:30"],
])
async def test_extra_unordered_or_outside_hours_are_invalid(times) -> None:
    payload = civil_payload("2026-08-28", [0] * len(times))
    payload["hourly"]["time"] = times
    response = await request_payload(payload)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "WEATHER_DATA_INVALID"
