from __future__ import annotations

import os
from datetime import UTC, datetime

LOAD_SCENARIOS = frozenset({"warm_cache", "cold_cache", "lock_contention", "slow_upstream", "redis_latency"})
DEFAULT_REQUESTS_PER_SECOND_PER_USER = 1.0

_REQUESTS: tuple[dict[str, str], ...] = (
    {"location_text": "Sao Paulo", "start_date": "", "temperature_unit": "celsius"},
    {"location_text": "Rio de Janeiro", "start_date": "", "temperature_unit": "fahrenheit"},
    {
        "latitude": "-22.90642",
        "longitude": "-43.18223",
        "start_date": "",
        "temperature_unit": "celsius",
    },
    {
        "latitude": "-23.55052",
        "longitude": "-46.63331",
        "start_date": "",
        "temperature_unit": "fahrenheit",
    },
)

def selected_scenario() -> str:
    scenario = os.getenv("CLIMAPREV_LOAD_SCENARIO", "warm_cache").strip().lower()
    if scenario not in LOAD_SCENARIOS:
        choices = ", ".join(sorted(LOAD_SCENARIOS))
        raise ValueError(f"CLIMAPREV_LOAD_SCENARIO must be one of: {choices}")
    return scenario


def per_user_request_rate() -> float:
    raw_rate = os.getenv(
        "CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER",
        str(DEFAULT_REQUESTS_PER_SECOND_PER_USER),
    )
    try:
        rate = float(raw_rate)
    except ValueError as error:
        raise ValueError("CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER must be a number") from error
    if rate <= 0:
        raise ValueError("CLIMAPREV_LOAD_REQUESTS_PER_SECOND_PER_USER must be greater than zero")
    return rate


def request_parameters(scenario: str, sequence: int, *, user_id: str) -> dict[str, str]:
    start_date = datetime.now(UTC).date().isoformat()
    if scenario not in LOAD_SCENARIOS:
        raise ValueError("unknown load scenario")
    if not user_id:
        raise ValueError("user_id must not be empty")
    index = 0 if scenario == "warm_cache" else sequence % len(_REQUESTS)
    request = dict(_REQUESTS[index])
    request["start_date"] = start_date
    if scenario in {"cold_cache", "slow_upstream"}:
        scenario_label = "cold" if scenario == "cold_cache" else "slow"
        request = {
            "location_text": f"ClimaPrev load {scenario_label} {user_id} {sequence}",
            "start_date": start_date,
            "temperature_unit": request["temperature_unit"],
        }
    elif scenario == "lock_contention":
        request = {
            "location_text": "ClimaPrev load lock contention",
            "start_date": start_date,
            "temperature_unit": "celsius",
        }
    return request
