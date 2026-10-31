import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import pytest
from tests.support.experiment import approval_fixture, protocol_fixture

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
from climaprev.tools.experimental_campaign import CampaignLedger, build_manifest
from climaprev.tools.experimental_d7_archive import load_control_archive
from climaprev.tools.experimental_d7_control import (
    SCOPE,
    build_control_calendar,
    run_control_calendar,
)
from climaprev.tools.experimental_d7_ledger import ControlLedger, pilot_budget
from climaprev.tools.historical_experiment import digest

FIRST = datetime(2030, 1, 1, 18, tzinfo=UTC)
SLOT = FIRST + timedelta(days=14)


def d7_protocol(zone="UTC", slot=SLOT):
    value = protocol_fixture()
    protocol = value["protocol"]
    protocol.update({"id": "synthetic-d7-not-real", "models": ["operational-baseline"],
                     "horizons": [7], "slots": [slot.isoformat()],
                     "criteria": {"control_scope": SCOPE, "execution_scope": "secondary_exploratory_only"}})
    protocol["stations"][0]["timezone"] = zone
    protocol["splits"] = {"adjustment": {"start": "2029-01-01", "end": "2030-06-30"},
                          "validation": {"start": "2030-07-15", "end": "2030-09-30"},
                          "test": {"start": "2031-01-01", "end": "2031-12-31"}}
    value["sha256"] = digest(protocol)
    return value


def calendar(protocol=None, enabled=True):
    protocol = protocol or d7_protocol()
    return build_control_calendar(protocol, now=SLOT-timedelta(days=1), enabled=enabled,
                                  approvals=[approval_fixture(protocol)])


@pytest.fixture
def pilot(tmp_path):
    value = protocol_fixture()
    protocol = value["protocol"]
    protocol["slots"] = [(FIRST+timedelta(days=i)).isoformat() for i in range(14)]
    protocol["criteria"] = {"adaptive_technical_pilot": True, "quota_per_station_model": 14}
    value["sha256"] = digest(protocol)
    location = CanonicalLocation("Synthetic", 0., 0., "UTC", "test")
    path = tmp_path / "pilot" / "pilot.sqlite"
    ledger = CampaignLedger(path)
    manifests = []
    for i in range(14):
        slot = FIRST+timedelta(days=i)
        manifest = build_manifest("synthetic", [location], protocol["models"], slot,
                                  enabled=True, collection_authorized=True)
        manifests.append(manifest)
        collected = slot+timedelta(minutes=1)
        target = (slot+timedelta(days=1)).replace(hour=0)
        for job in manifest["plan"]["jobs"]:
            baseline = job["identity"]["model"] == "operational-baseline"
            if baseline:
                payload = {"forecast": {"location": asdict(location), "fetched_at": collected.isoformat(),
                                        "days": [{"date": target.date().isoformat(), "precipitation_sum_mm": 0.}]}}
            else:
                payload = {"request_parameters": {"models": "gfs_global"}, "response": {
                    "hourly_units": {"time": "unixtime", "precipitation": "mm"},
                    "hourly": {"time": [int((target+timedelta(hours=h)).timestamp()) for h in range(1, 25)],
                               "precipitation": [0.]*24}}}
            capture = ForecastCapture("open-meteo", "unknown" if baseline else "gfs_global",
                                      "https://api.open-meteo.com/v1/forecast", location, collected,
                                      target, target+timedelta(days=1),
                                      selection_mode="automatic" if baseline else "explicit")
            artifact = archive_forecast(path.parent/"archives", capture, payload)
            assert ledger.reserve(job["key"], "open-meteo", collected, 30)
            ledger.finish(job["key"], str(artifact), None)
    return value, manifests, path


def response_payload(job):
    zone = ZoneInfo(job["station"]["timezone"])
    start = datetime.fromisoformat(job["start_utc"])
    end = datetime.fromisoformat(job["end_utc"])
    next_end = (end.astimezone(zone)+timedelta(days=1)).astimezone(UTC)
    count = int((next_end-start).total_seconds()/3600)
    days = [start, end]
    return {"timezone": zone.key, "latitude": 0., "longitude": 0., "elevation": 10.,
            "daily_units": {"time": "unixtime", "precipitation_sum": "mm"},
            "daily": {"time": [int(t.timestamp()) for t in days],
                      "temperature_2m_min": [20., 20.], "temperature_2m_max": [30., 30.],
                      "precipitation_sum": [24., 24.], "precipitation_probability_max": [50., 50.],
                      "wind_speed_10m_max": [10., 10.], "wind_gusts_10m_max": [20., 20.],
                      "weather_code": [3, 3]},
            "hourly_units": {"time": "unixtime", "temperature_2m": "°C", "precipitation": "mm",
                             "relative_humidity_2m": "%", "precipitation_probability": "%"},
            "hourly": {"time": [int((start+timedelta(hours=h)).timestamp()) for h in range(count)],
                       "temperature_2m": [25.]*count, "precipitation": [1.]*count,
                       "relative_humidity_2m": [60.]*count, "precipitation_probability": [50.]*count}}


async def execute(tmp_path, pilot, *, plan=None, handler=None, clock=lambda: SLOT):
    plan = plan or calendar()
    protocol, manifests, pilot_path = pilot
    job = plan["plan"]["jobs"][0]
    payload = response_payload(job)
    requests = []

    def respond(request):
        requests.append(request)
        return handler(request, payload) if handler else httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await run_control_calendar(
            plan, pilot_protocol=protocol, pilot_manifests=manifests, pilot_ledger=pilot_path,
            ledger=tmp_path/"d7.sqlite", directory=tmp_path/"d7-archives", client=client,
            approvals=[approval_fixture(plan["plan"]["protocol"])], clock=clock)
    return result, requests


def test_calendar_is_disabled_by_default_and_requires_own_e1():
    protocol = d7_protocol()
    assert not build_control_calendar(protocol, now=FIRST)["plan"]["enabled"]
    with pytest.raises(ValueError, match="E1"):
        build_control_calendar(protocol, now=FIRST, enabled=True)
    with pytest.raises(ValueError, match="E1"):
        build_control_calendar(protocol, now=FIRST, enabled=True,
                               approvals=[approval_fixture(protocol_fixture())])


@pytest.mark.parametrize("zone", ["UTC", "America/Belem", "America/Sao_Paulo", "Asia/Tokyo"])
def test_d7_uses_local_date_of_slot_and_exact_next_midnight(zone):
    plan = calendar(d7_protocol(zone))
    job = plan["plan"]["jobs"][0]
    expected = SLOT.astimezone(ZoneInfo(zone)).date()+timedelta(days=7)
    assert job["target_date"] == expected.isoformat()
    assert datetime.fromisoformat(job["start_utc"]).astimezone(ZoneInfo(zone)).date() == expected
    assert datetime.fromisoformat(job["end_utc"])-datetime.fromisoformat(job["start_utc"]) == timedelta(days=1)


def test_cross_year_and_daylight_saving_are_civil_day_intervals():
    slot = datetime(2029, 12, 28, 18, tzinfo=UTC)
    plan = build_control_calendar(d7_protocol(slot=slot), now=slot-timedelta(days=1))
    assert plan["plan"]["jobs"][0]["target_date"] == "2030-01-04"
    slot = datetime(2030, 3, 3, 18, tzinfo=UTC)  # New York DST starts on the target date.
    plan = build_control_calendar(d7_protocol("America/New_York", slot), now=slot-timedelta(days=1))
    job = plan["plan"]["jobs"][0]
    assert datetime.fromisoformat(job["end_utc"])-datetime.fromisoformat(job["start_utc"]) == timedelta(hours=23)


def test_past_slot_and_reserved_partitions_are_rejected():
    with pytest.raises(ValueError, match="strictly future"):
        build_control_calendar(d7_protocol(), now=SLOT)
    value = d7_protocol()
    value["protocol"]["splits"]["adjustment"]["end"] = "2029-06-30"
    value["sha256"] = digest(value["protocol"])
    with pytest.raises(ValueError, match="development"):
        build_control_calendar(value, now=FIRST)


def test_equivalent_offset_spellings_cannot_duplicate_one_slot():
    value = d7_protocol()
    value["protocol"]["slots"].append("2030-01-15T15:00:00-03:00")
    value["sha256"] = digest(value["protocol"])
    with pytest.raises(ValueError, match="duplicate UTC"):
        build_control_calendar(value, now=FIRST)


async def test_complete_capture_preserves_raw_bytes_closing_hour_and_pilot(tmp_path, pilot):
    original = pilot[2].read_bytes()
    result, requests = await execute(tmp_path, pilot)
    assert len(requests) == 1 and result[0]["status"] == "completed"
    request = requests[0]
    assert request.url.params["start_date"] == "2030-01-22"
    assert request.url.params["end_date"] == "2030-01-23"
    assert request.url.params["timeformat"] == "unixtime"
    data = load_control_archive(Path(result[0]["archive"]))
    assert data["rain_interval_total_mm"] == 24
    assert data["forecast"]["days"][0]["precipitation_sum_mm"] == 24
    assert data["request"]["adapter_request_parameters"]["end_date"] == "2030-01-22"
    assert not data["scientific_approval"] and not data["promotion_allowed"]
    assert pilot[2].read_bytes() == original
    again, calls = await execute(tmp_path, pilot)
    assert not calls and again[0]["status"] == "already_reserved_no_retry"


@pytest.mark.parametrize("mode", ["missing_final_hour", "missing_rain", "wrong_unit", "bad_timezone", "bad_json", "redirect", "http_error", "late"])
async def test_invalid_or_incomplete_forecasts_cannot_be_eligible(tmp_path, pilot, mode):
    def handler(request, payload):
        if mode == "missing_final_hour":
            payload["hourly"]["precipitation"][24] = None
        elif mode == "missing_rain":
            payload["daily"]["precipitation_sum"][0] = None
        elif mode == "wrong_unit":
            payload["hourly_units"]["precipitation"] = "inch"
        elif mode == "bad_timezone":
            payload["timezone"] = "Asia/Tokyo"
        elif mode == "bad_json":
            return httpx.Response(200, content=b"not-json")
        elif mode == "redirect":
            return httpx.Response(302, headers={"location": "https://example.com"})
        elif mode == "http_error":
            return httpx.Response(503, content=b"temporary failure")
        elif mode == "late":
            stamps[0] = SLOT+timedelta(minutes=31)
        return httpx.Response(200, json=payload)
    stamps = [SLOT]
    result, requests = await execute(tmp_path, pilot, handler=handler, clock=lambda: stamps[0])
    assert len(requests) == 1 and result[0]["status"] in {"failed", "ineligible"}
    data = load_control_archive(Path(result[0]["archive"]))
    assert not data["rain_eligible_exploratory"]
    again, calls = await execute(tmp_path, pilot)
    assert not calls and again[0]["status"] == "already_reserved_no_retry"


async def test_raw_archive_corruption_is_detected(tmp_path, pilot):
    result, _ = await execute(tmp_path, pilot)
    path = Path(result[0]["archive"])
    data = load_control_archive(path)
    (path.parent/data["request"]["raw_file"]).write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="integrity"):
        load_control_archive(path)


@pytest.mark.parametrize("when", [SLOT-timedelta(seconds=1), SLOT+timedelta(minutes=30)])
async def test_outside_window_has_no_http_or_ledger_creation(tmp_path, pilot, when):
    result, calls = await execute(tmp_path, pilot, clock=lambda: when)
    assert not result and not calls and not (tmp_path/"d7.sqlite").exists()


async def test_disabled_calendar_does_not_touch_pilot_or_create_ledger(tmp_path, pilot):
    result, calls = await execute(tmp_path, pilot, plan=calendar(enabled=False))
    assert not result and not calls and not (tmp_path/"d7.sqlite").exists()


async def test_frozen_version_change_blocks_before_network(tmp_path, pilot):
    plan = calendar()
    plan["plan"]["versions"]["tools/experimental_d7_control.py"] = "different"
    plan["sha256"] = digest(plan["plan"])
    with pytest.raises(ValueError, match="frozen identity"):
        await execute(tmp_path, pilot, plan=plan)
    assert not (tmp_path/"d7.sqlite").exists()


def test_shared_budget_counts_reservations_including_failures(tmp_path):
    ledger = ControlLedger(tmp_path/"d7.sqlite")
    assert ledger.reserve_job("a")
    ledger.reserve_request("a", SLOT, 29)
    ledger.finish("a", "failed", None)
    assert ledger.reserve_job("b")
    with pytest.raises(ValueError, match="budget exhausted"):
        ledger.reserve_request("b", SLOT, 29)


@pytest.mark.parametrize("count", [-1, True, 31, 1.5])
def test_invalid_external_budget_cannot_bypass_limit(tmp_path, count):
    ledger = ControlLedger(tmp_path/"d7.sqlite")
    assert ledger.reserve_job("synthetic")
    with pytest.raises(ValueError, match="bounded pilot call count"):
        ledger.reserve_request("synthetic", SLOT, count)


async def test_pilot_workspace_cannot_be_used_for_d7_archives(tmp_path, pilot):
    protocol, manifests, path = pilot
    plan = calendar()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: pytest.fail("no HTTP"))) as client:
        with pytest.raises(ValueError, match="workspace"):
            await run_control_calendar(
                plan, pilot_protocol=protocol, pilot_manifests=manifests, pilot_ledger=path,
                ledger=path.parent/"new.sqlite", directory=path.parent/"new-archives", client=client,
                approvals=[approval_fixture(plan["plan"]["protocol"])], clock=lambda: SLOT)


async def test_http_failure_preserves_exact_unparsed_response_bytes(tmp_path, pilot):
    raw = b'  {"reason" : "synthetic failure", "value": 2.000 }\n'
    result, _ = await execute(tmp_path, pilot, handler=lambda *_: httpx.Response(503, content=raw))
    archive = Path(result[0]["archive"])
    data = load_control_archive(archive)
    assert (archive.parent/data["request"]["raw_file"]).read_bytes() == raw


def test_incomplete_pilot_and_missing_seed_history_block_control(tmp_path, pilot):
    protocol, manifests, path = pilot
    with pytest.raises(ValueError, match="seed history"):
        pilot_budget(protocol, manifests[1:], path, SLOT)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("UPDATE captures SET status='failed',artifact=NULL,error='SyntheticFailure' WHERE job=?", (manifests[0]["plan"]["jobs"][0]["key"],))
    with pytest.raises(ValueError, match="quota is complete"):
        pilot_budget(protocol, manifests, path, SLOT)


def test_completed_pilot_still_blocks_on_future_seed_dates(pilot):
    protocol, manifests, path = pilot
    assert pilot_budget(protocol, manifests, path, SLOT) == 0
    extra = build_manifest("synthetic", [CanonicalLocation("Synthetic", 0., 0., "UTC", "test")],
                           protocol["protocol"]["models"], SLOT)
    with pytest.raises(ValueError, match="after all pilot manifest dates"):
        pilot_budget(protocol, [*manifests, extra], path, SLOT)


def test_archive_json_corruption_is_detected(tmp_path, pilot):
    path = tmp_path/"bad.json"
    path.write_text(json.dumps({"capture": {}, "sha256": "wrong"}))
    with pytest.raises(ValueError, match="identity"):
        load_control_archive(path)


def test_seed_date_with_missing_pair_is_not_a_complete_seed(pilot):
    protocol, manifests, path = pilot
    first = manifests[0]
    first["plan"]["jobs"].pop()
    first["plan_sha256"] = digest(first["plan"])
    with pytest.raises(ValueError, match="station/model seed universe"):
        pilot_budget(protocol, manifests, path, SLOT)


@pytest.mark.parametrize("slot,hours", [(datetime(2030, 3, 3, 18, tzinfo=UTC), 23),
                                        (datetime(2030, 10, 27, 18, tzinfo=UTC), 25)])
async def test_real_capture_path_handles_short_and_long_civil_days(tmp_path, pilot, slot, hours):
    protocol = d7_protocol("America/New_York", slot)
    protocol["protocol"]["splits"]["adjustment"]["end"] = "2030-11-30"
    protocol["protocol"]["splits"]["validation"] = {"start": "2030-12-10", "end": "2030-12-31"}
    protocol["sha256"] = digest(protocol["protocol"])
    result, _ = await execute(tmp_path, pilot, plan=calendar(protocol), clock=lambda: slot)
    assert result[0]["status"] == "completed"
    data = load_control_archive(Path(result[0]["archive"]))
    assert data["rain_interval_total_mm"] == hours


def test_independent_workers_cannot_exceed_shared_daily_budget(tmp_path):
    path = tmp_path/"parallel.sqlite"
    ControlLedger(path)

    def reserve(index):
        ledger = ControlLedger(path)
        key = str(index)
        assert ledger.reserve_job(key)
        try:
            ledger.reserve_request(key, SLOT, 28)
            return True
        except ValueError as error:
            assert "budget exhausted" in str(error)
            return False

    with ThreadPoolExecutor(max_workers=4) as workers:
        accepted = list(workers.map(reserve, range(8)))
    assert sum(accepted) == 2


async def test_runtime_without_own_approval_is_blocked_before_io(tmp_path, pilot):
    plan = calendar()
    protocol, manifests, path = pilot
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: pytest.fail("no HTTP"))) as client:
        with pytest.raises(ValueError, match="E1"):
            await run_control_calendar(
                plan, pilot_protocol=protocol, pilot_manifests=manifests, pilot_ledger=path,
                ledger=tmp_path/"d7.sqlite", directory=tmp_path/"d7", client=client,
                approvals=[], clock=lambda: SLOT)
    assert not (tmp_path/"d7.sqlite").exists()
