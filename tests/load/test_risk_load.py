from __future__ import annotations

import time
from datetime import date

import httpx
import pytest

from tests.load.scenarios import (
    DEFAULT_REQUESTS_PER_SECOND_PER_USER,
    LOAD_SCENARIOS,
    per_user_request_rate,
    request_parameters,
    selected_scenario,
)


def test_load_harness_exposes_the_documented_selectable_scenarios() -> None:
    assert set(LOAD_SCENARIOS) == {
        "warm_cache",
        "cold_cache",
        "lock_contention",
        "slow_upstream",
        "redis_latency",
    }


@pytest.mark.parametrize("scenario", sorted(LOAD_SCENARIOS))
def test_load_harness_builds_fixed_valid_risk_requests_for_each_scenario(
    monkeypatch: pytest.MonkeyPatch,
    scenario: str,
) -> None:
    monkeypatch.setenv("CLIMAPREV_LOAD_SCENARIO", scenario)

    params = request_parameters(selected_scenario(), sequence=0, user_id="user-a")

    assert len(params["start_date"]) == 10
    assert params["temperature_unit"] in {"celsius", "fahrenheit"}
    assert ("location_text" in params) != ("latitude" in params)


def test_load_harness_rejects_an_unknown_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLIMAPREV_LOAD_SCENARIO", "unknown")

    with pytest.raises(ValueError, match="CLIMAPREV_LOAD_SCENARIO"):
        selected_scenario()


def test_warm_cache_reuses_one_fixed_cache_key() -> None:
    assert request_parameters("warm_cache", sequence=0, user_id="user-a") == request_parameters(
        "warm_cache", sequence=999, user_id="user-b"
    )


def test_cold_cache_uses_a_unique_location_key_across_users_and_requests() -> None:
    first_user_first_request = request_parameters("cold_cache", sequence=0, user_id="user-a")
    first_user_second_request = request_parameters("cold_cache", sequence=1, user_id="user-a")
    second_user_first_request = request_parameters("cold_cache", sequence=0, user_id="user-b")

    locations = {
        first_user_first_request["location_text"],
        first_user_second_request["location_text"],
        second_user_first_request["location_text"],
    }
    assert locations == {
        "ClimaPrev load cold user-a 0",
        "ClimaPrev load cold user-a 1",
        "ClimaPrev load cold user-b 0",
    }


def test_slow_upstream_uses_a_unique_location_key_across_users_and_requests() -> None:
    requests = {
        request_parameters("slow_upstream", sequence=0, user_id="user-a")["location_text"],
        request_parameters("slow_upstream", sequence=1, user_id="user-a")["location_text"],
        request_parameters("slow_upstream", sequence=0, user_id="user-b")["location_text"],
    }

    assert requests == {
        "ClimaPrev load slow user-a 0",
        "ClimaPrev load slow user-a 1",
        "ClimaPrev load slow user-b 0",
    }


def test_lock_contention_reuses_one_forecast_key_across_concurrent_users() -> None:
    first = request_parameters("lock_contention", sequence=0, user_id="user-a")
    second = request_parameters("lock_contention", sequence=1, user_id="user-b")

    assert first == second


def test_default_locust_rate_is_one_request_per_second_per_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER", raising=False)

    assert DEFAULT_REQUESTS_PER_SECOND_PER_USER == 1.0
    assert per_user_request_rate() == 1.0


def test_locust_rate_can_be_explicitly_overridden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER", "1.5")

    assert per_user_request_rate() == 1.5


@pytest.mark.asyncio
async def test_slow_upstream_scenario_injects_configured_provider_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIMAPREV_LOAD_SCENARIO", "slow_upstream")
    monkeypatch.setenv("CLIMAPREV_PROVIDER_MOCK_DELAY_MS", "25")
    from tests.load.mock_provider import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://provider-mock") as client:
        started_at = time.perf_counter()
        response = await client.get("/v1/search", params={"name": "Sao Paulo"})
        elapsed = time.perf_counter() - started_at

    assert response.headers["x-provider-mock-delay-ms"] == "25"
    assert elapsed >= 0.02


@pytest.mark.asyncio
async def test_mock_provider_serves_a_valid_deterministic_open_meteo_contract() -> None:
    """The Docker load profile must not call the public Open-Meteo service."""
    from tests.load.mock_provider import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://provider-mock") as client:
        geocoding = await client.get("/v1/search", params={"name": "Sao Paulo"})
        forecast = await client.get(
            "/v1/forecast",
            params={
                "latitude": "-23.55052",
                "longitude": "-46.63331",
                "start_date": "2026-08-30",
                "end_date": "2026-08-31",
            },
        )

    assert geocoding.status_code == 200
    assert geocoding.json()["results"][0]["timezone"] == "America/Sao_Paulo"
    assert forecast.status_code == 200
    payload = forecast.json()
    assert payload["timezone"] == "America/Sao_Paulo"
    assert payload["daily"]["time"] == [date(2026, 8, 30).isoformat(), date(2026, 8, 31).isoformat()]
    assert payload["hourly"]["time"] == ["2026-08-30T00:00", "2026-08-31T00:00"]


@pytest.mark.asyncio
async def test_mock_geocoding_varies_coordinates_by_unique_location() -> None:
    """Distinct load locations must produce distinct forecast-cache keys."""
    from tests.load.mock_provider import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://provider-mock") as client:
        first = await client.get("/v1/search", params={"name": "ClimaPrev load cold user-a 0"})
        repeated = await client.get("/v1/search", params={"name": "ClimaPrev load cold user-a 0"})
        second = await client.get("/v1/search", params={"name": "ClimaPrev load cold user-b 0"})

    first_location = first.json()["results"][0]
    repeated_location = repeated.json()["results"][0]
    second_location = second.json()["results"][0]
    assert (first_location["latitude"], first_location["longitude"]) == (
        repeated_location["latitude"],
        repeated_location["longitude"],
    )
    assert (first_location["latitude"], first_location["longitude"]) != (
        second_location["latitude"],
        second_location["longitude"],
    )
