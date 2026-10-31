from copy import deepcopy
from datetime import datetime, timedelta

from climaprev.tools.audit_historical import audit_snapshot


def sample(*, boundary=True):
    times = [(datetime(2025, 1, 1) + timedelta(hours=h)).isoformat()
             for h in range(25 if boundary else 24)]
    sources = {}
    for name, suffix in (("forecast", "_previous_day1"), ("observed", "")):
        sources[name] = {
            "latitude": -1.5, "longitude": -48.5, "timezone": "America/Belem",
            "utc_offset_seconds": -10800,
            "hourly_units": {f"precipitation{suffix}": "mm",
                             f"temperature_2m{suffix}": "°C",
                             f"wind_gusts_10m{suffix}": "km/h"},
            "hourly": {"time": times, f"precipitation{suffix}": list(range(len(times))),
                       f"temperature_2m{suffix}": [25] * len(times),
                       f"wind_gusts_10m{suffix}": [10] * len(times)},
        }
    return {"configuration": {"start": "2025-01-01", "end": "2025-01-01",
                              "timezone": "America/Belem", "lead_days": 1}, **sources}


def test_previous_hour_accumulation_uses_next_midnight_and_preserves_input():
    data = sample()
    before = deepcopy(data)
    result = audit_snapshot(data)
    day = result["sources"]["observed"]["days"][0]
    assert day["timestamp_date_total_mm"] == 276
    assert day["civil_preceding_hour_total_mm"] == 300
    assert day["civil_preceding_hour_max_mm"] == 24
    assert day["missing_interval_endpoints"] == []
    assert data == before


def test_absent_boundary_is_null_and_reports_utc_endpoint():
    result = audit_snapshot(sample(boundary=False))
    day = result["sources"]["observed"]["days"][0]
    assert day["civil_preceding_hour_total_mm"] is None
    assert day["civil_preceding_hour_max_mm"] is None
    assert day["missing_interval_endpoints"] == ["2025-01-02T03:00:00+00:00"]


def test_missing_internal_hour_does_not_become_zero_rain():
    data = sample()
    data["observed"]["hourly"]["precipitation"][12] = None
    result = audit_snapshot(data)
    observed = result["sources"]["observed"]
    assert observed["timestamp_date_total_mm"] is None
    assert observed["days"][0]["civil_preceding_hour_total_mm"] is None
    assert observed["days"][0]["civil_preceding_hour_max_mm"] is None
