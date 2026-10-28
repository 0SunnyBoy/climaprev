"""Explicit synthetic protocol, never an approval or a real campaign."""

from typing import Any

from climaprev.tools.historical_experiment import digest


def protocol_fixture() -> dict[str, Any]:
    protocol = {
        "schema": "climaprev-experiment-protocol-v1", "id": "synthetic",
        "code_version": "synthetic-revision",
        "stations": [{"code": "SYN", "name": "Synthetic", "latitude": 0.0,
                      "longitude": 0.0, "timezone": "UTC"}],
        "variables": [{"name": "precipitation_mm", "unit": "mm",
                       "semantics": "previous_hour_sum", "aggregation": "sum"}],
        "models": ["operational-baseline", "gfs_global"],
        "slots": ["2030-01-01T00:00:00+00:00"], "horizons": [1, 3, 7],
        "slot_window_minutes": 30, "provider_daily_call_limit": 30,
        "splits": {"adjustment": {"start": "2029-01-01", "end": "2029-03-31"},
                   "validation": {"start": "2029-04-01", "end": "2029-06-30"},
                   "test": {"start": "2030-01-01", "end": "2030-12-31"}},
        "criteria": {},
    }
    return {"protocol": protocol, "sha256": digest(protocol)}
