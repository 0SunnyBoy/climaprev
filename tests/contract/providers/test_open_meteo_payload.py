from __future__ import annotations

from copy import deepcopy
from typing import Any


def valid_geocoding_payload() -> dict[str, Any]:
    return {
        "results": [
            {
                "id": 3469058,
                "name": "Rio de Janeiro",
                "latitude": -22.90642,
                "longitude": -43.18223,
                "timezone": "America/Sao_Paulo",
                "country_code": "BR",
            }
        ]
    }


def valid_forecast_payload() -> dict[str, Any]:
    return {
        "latitude": -22.90642,
        "longitude": -43.18223,
        "timezone": "America/Sao_Paulo",
        "daily": {
            "time": ["2026-08-28", "2026-08-29"],
            "temperature_2m_min": [16.0, 17.0],
            "temperature_2m_max": [25.0, 26.0],
            "precipitation_sum": [1.2, 3.4],
            "precipitation_probability_max": [40, 55],
            "wind_speed_10m_max": [18.0, 21.0],
            "wind_gusts_10m_max": [32.0, 35.0],
            "weather_code": [3, 61],
        },
        "hourly": {
            "time": [
                "2026-08-28T00:00",
                "2026-08-28T12:00",
                "2026-08-29T00:00",
                "2026-08-29T12:00",
            ],
            "temperature_2m": [19.0, 24.0, 20.0, 25.0],
            "relative_humidity_2m": [70, 80, 60, 70],
            "precipitation": [0.0, 1.2, 2.5, 0.1],
            "precipitation_probability": [10, 40, 55, 20],
        },
    }


def test_geocoding_fixture_contains_a_resolvable_location() -> None:
    result = valid_geocoding_payload()["results"][0]

    assert result["name"] == "Rio de Janeiro"
    assert result["latitude"] == -22.90642
    assert result["timezone"] == "America/Sao_Paulo"


def test_forecast_fixture_contains_aligned_daily_and_hourly_series() -> None:
    payload = valid_forecast_payload()

    assert payload["timezone"] == "America/Sao_Paulo"
    assert len(payload["daily"]["time"]) == len(payload["daily"]["weather_code"])
    assert len(payload["hourly"]["time"]) == len(payload["hourly"]["precipitation"])


def test_forecast_fixture_can_be_mutated_without_changing_the_original() -> None:
    payload = valid_forecast_payload()
    changed = deepcopy(payload)
    changed["daily"]["precipitation_sum"][0] = 99.9

    assert payload["daily"]["precipitation_sum"][0] == 1.2
