import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from tests.support.experiment import approval_fixture, protocol_fixture, station_csv

from climaprev.tools.experimental_campaign import (
    CampaignLedger,
    build_target_calendar,
    run_calendar,
)
from climaprev.tools.experimental_coverage import audit_target_coverage
from climaprev.tools.experimental_pairing import pair_calendar_captures
from climaprev.tools.historical_experiment import digest

SLOT = datetime(2030, 1, 1, tzinfo=UTC)
DAY = SLOT + timedelta(days=1)


class FixedCollectionClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return SLOT if tz else SLOT.replace(tzinfo=None)


def pipeline_protocol():
    envelope = protocol_fixture()
    plan = envelope["protocol"]
    plan["models"] = ["gfs_global", "icon_global"]
    plan["horizons"] = [1]
    plan["variables"] += [
        {"name": "temperature_max_c", "unit": "°C", "semantics": "instant", "aggregation": "max"},
        {"name": "wind_kmh", "unit": "km/h", "semantics": "instant", "aggregation": "mean"},
        {"name": "gust_kmh", "unit": "km/h", "semantics": "previous_hour_max", "aggregation": "max"},
        {"name": "humidity_pct", "unit": "%", "semantics": "instant", "aggregation": "mean"},
    ]
    envelope["sha256"] = digest(plan)
    return envelope


def source_csv(partial=False):
    raw = station_csv(["VENTO, VELOCIDADE HORARIA (m/s)",
                       "UMIDADE RELATIVA DO AR, HORARIA (%)"],
                      [["10", "60"]] * 24, start=DAY)
    if partial:
        lines = raw.splitlines()
        lines.pop(-3)
        raw = b"\n".join(lines) + b"\n"
    return raw


def payload():
    times = [int((DAY + timedelta(hours=index)).timestamp()) for index in range(25)]
    return {"hourly_units": {"time": "unixtime", "temperature_2m": "°C",
                              "relative_humidity_2m": "%", "precipitation": "mm",
                              "wind_speed_10m": "km/h", "wind_gusts_10m": "km/h"},
            "hourly": {"time": times, "temperature_2m": [20] * 25,
                       "relative_humidity_2m": [50] * 25, "precipitation": [1] * 25,
                       "wind_speed_10m": [10] * 25, "wind_gusts_10m": [15] * 25}}


async def pilot(directory: Path, monkeypatch, mode="ok"):
    directory.mkdir()
    monkeypatch.setattr("climaprev.tools.experimental_collection.datetime", FixedCollectionClock)
    envelope = pipeline_protocol()
    calendar = build_target_calendar(envelope, enabled=True, approvals=[approval_fixture(envelope)])
    source = directory / "station.csv"
    source.write_bytes(source_csv(mode == "partial"))
    ledger = CampaignLedger(directory / "ledger.sqlite")
    calls = []

    def transport(request):
        calls.append(request)
        if mode == "unavailable" and request.url.params["models"] == "gfs_global":
            return httpx.Response(503)
        return httpx.Response(200, json=payload())

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as client:
        captures = await run_calendar(calendar, ledger, client, directory / "archive",
                                      now=SLOT + timedelta(hours=1) if mode == "missed" else SLOT)
        if mode == "restart":
            retry = await run_calendar(calendar, ledger, client, directory / "archive", now=SLOT)
            assert [item["status"] for item in retry] == ["already_reserved_no_retry"] * 2
    pairs = pair_calendar_captures(calendar, ledger.path, {"SYN": source})
    coverage = audit_target_coverage(calendar, ledger.path, pairs, now=DAY + timedelta(days=1),
                                     observation_files={"SYN": source})
    return captures, pairs, coverage, calls, ledger.path


@pytest.mark.asyncio
@pytest.mark.parametrize("mode,eligible,calls", [
    ("ok", 10, 2), ("unavailable", 5, 2), ("partial", 0, 2),
    ("restart", 10, 2), ("missed", 0, 0),
])
async def test_synthetic_pilot_links_capture_ledger_observations_pairs_and_coverage(
    tmp_path, monkeypatch, mode, eligible, calls,
):
    captures, pairs, coverage, requests, ledger = await pilot(tmp_path / mode, monkeypatch, mode)
    assert len(requests) == calls
    assert coverage["planned_targets"] == 10
    assert coverage["due_targets"] == 10
    assert coverage["eligible_exploratory_targets"] == eligible
    assert coverage["scientific_approval"] is False
    with sqlite3.connect(ledger) as db:
        states = db.execute("SELECT status FROM captures ORDER BY job").fetchall()
    assert len(states) == calls
    if mode == "ok":
        assert all(item["status"] == "completed" for item in captures)
        rain = [p for p in pairs if p["variable"] == "precipitation_mm"]
        assert rain[0]["rows"][0]["forecast"] == 24
        assert rain[0]["rows"][0]["observed"] == 0
        wind = [p for p in pairs if p["variable"] == "wind_kmh"]
        assert wind[0]["rows"][0]["observed"] == 36
        assert wind[0]["rows"][0]["eligible_confirmatory"] is False


@pytest.mark.asyncio
async def test_pilot_reproduces_scientific_content_with_same_inputs_and_clock(tmp_path, monkeypatch):
    one = await pilot(tmp_path / "one", monkeypatch)
    two = await pilot(tmp_path / "two", monkeypatch)
    assert one[1] == two[1]
    assert one[2] == two[2]
    assert [item["status"] for item in one[0]] == [item["status"] for item in two[0]]


def baseline_capture(tmp_path):
    from climaprev.domain.models import CanonicalLocation
    from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast

    location = CanonicalLocation("Synthetic", 0, 0, "UTC", "fixture")
    capture = ForecastCapture("open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast",
                              location, SLOT, SLOT, SLOT + timedelta(days=7), selection_mode="automatic")
    path = archive_forecast(tmp_path, capture, {
        "forecast": {"days": [{"date": "2030-01-02", "precipitation_sum_mm": 12,
                                  "wind_max_kmh": 50}], "missing_fields": []},
    })
    return path, location


def test_baseline_pairs_daily_value_directly_and_keeps_d7_absent(tmp_path):
    from climaprev.domain.models import DatePeriod
    from climaprev.tools.experimental_pairing import pair_capture

    path, location = baseline_capture(tmp_path)
    raw = station_csv([], [[]] * (8 * 24), start=SLOT)
    contract = protocol_fixture()["protocol"]["variables"][0]
    report = pair_capture(path, raw, location, DatePeriod(DAY.date(), (SLOT + timedelta(days=7)).date()),
                          station="SYN", model="operational-baseline", contract=contract)
    assert report["rows"][0]["forecast"] == 12
    assert report["rows"][0]["observed"] == 0
    assert report["rows"][0]["eligible_exploratory"] is True
    assert report["rows"][-1]["forecast"] is None
    assert "baseline_target_absent" in report["rows"][-1]["exclusions"]
    assert "forecast_samples_sha256" not in report
    assert report["forecast_aggregation"] == "production_adapter_daily_value_without_hourly_reconstruction"


def test_baseline_daily_maximum_is_not_fabricated_into_mean_wind(tmp_path):
    from climaprev.domain.models import DatePeriod
    from climaprev.tools.experimental_pairing import pair_capture

    path, location = baseline_capture(tmp_path)
    report = pair_capture(path, source_csv(), location, DatePeriod(DAY.date(), DAY.date()),
                          station="SYN", model="operational-baseline",
                          contract={"name": "wind_kmh", "unit": "km/h",
                                    "semantics": "instant", "aggregation": "mean"})
    assert report["rows"][0]["forecast"] is None
    assert "baseline_aggregation_not_supported" in report["rows"][0]["exclusions"]


def test_pairing_refuses_a_capture_changed_after_ledger_completion(tmp_path):
    from climaprev.domain.models import DatePeriod
    from climaprev.tools.experimental_pairing import pair_capture

    path, location = baseline_capture(tmp_path)
    path.write_text('{"changed":true}')
    with pytest.raises(ValueError, match="capture"):
        pair_capture(path, source_csv(), location, DatePeriod(DAY.date(), DAY.date()),
                     station="SYN", model="operational-baseline",
                     contract=protocol_fixture()["protocol"]["variables"][0])
