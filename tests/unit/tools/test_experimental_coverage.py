from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_campaign import CampaignLedger, build_manifest
from climaprev.tools.experimental_coverage import audit_calendar
from climaprev.tools.historical_experiment import digest

NOW = datetime(2026, 10, 27, 12, tzinfo=UTC)
POINT = CanonicalLocation("Synthetic", -1.4, -48.4, "America/Belem", "test")


def manifest(slot, models=None):
    return build_manifest("synthetic", [POINT], models or ["gfs_global"], slot,
                          enabled=True, collection_authorized=True)


def test_calendar_counts_entirely_absent_slots_and_future_denominator(tmp_path):
    db = tmp_path / "ledger.db"
    CampaignLedger(db)
    plans = [manifest(NOW - timedelta(days=1)), manifest(NOW),
             manifest(NOW + timedelta(days=1))]
    result = audit_calendar(plans, db, now=NOW)
    assert result["planned_jobs"] == 3
    assert result["due_jobs"] == 2
    assert result["status_counts"] == {"missed": 1, "open": 1, "future": 1}
    assert result["completion_fraction_due"] == 0


def test_completed_failed_and_unresolved_are_distinct_without_mutation(tmp_path):
    db = tmp_path / "ledger.db"
    ledger = CampaignLedger(db)
    plan = manifest(NOW - timedelta(days=1), ["gfs_global", "ecmwf_ifs025", "icon_global"])
    keys = [job["key"] for job in plan["plan"]["jobs"]]
    for key in keys:
        assert ledger.reserve(key, "open-meteo", NOW, 10)
    ledger.finish(keys[0], "synthetic/archive.json", None)
    ledger.finish(keys[1], None, "ValueError")
    ledger.reserve("other-campaign", "open-meteo", NOW, 10)
    before = db.read_bytes()
    result = audit_calendar([plan], db, now=NOW)
    assert result["status_counts"] == {"completed": 1, "failed": 1, "unresolved_reservation": 1}
    assert result["completion_fraction_due"] == pytest.approx(1 / 3)
    assert result["unplanned_ledger_jobs"] == 1
    assert db.read_bytes() == before
    assert result["promotion_allowed"] is False


def test_future_only_has_no_success_rate(tmp_path):
    db = tmp_path / "ledger.db"
    CampaignLedger(db)
    result = audit_calendar([manifest(NOW + timedelta(days=1))], db, now=NOW)
    assert result["completion_fraction_due"] is None


def test_inactive_manifest_is_not_counted_as_failed_collection(tmp_path):
    db = tmp_path / "ledger.db"
    CampaignLedger(db)
    plan = build_manifest("disabled", [POINT], ["gfs_global"], NOW - timedelta(days=1))
    result = audit_calendar([plan], db, now=NOW)
    assert result["status_counts"] == {"inactive": 1}
    assert result["due_jobs"] == 0
    assert result["completion_fraction_due"] is None


def test_missing_database_is_not_created(tmp_path):
    db = tmp_path / "absent.db"
    import sqlite3

    with pytest.raises(sqlite3.OperationalError):
        audit_calendar([], db, now=NOW)
    assert not db.exists()


@pytest.mark.parametrize("problem", ["hash", "duplicate", "slot", "naive"])
def test_invalid_calendars_rejected(tmp_path, problem):
    db = tmp_path / "ledger.db"
    CampaignLedger(db)
    item = manifest(NOW)
    plans = [item]
    clock = NOW
    if problem == "hash":
        item["plan"]["enabled"] = False
    elif problem == "duplicate":
        plans.append(deepcopy(item))
    elif problem == "slot":
        item["plan"]["expires"] = item["plan"]["slot"]
        item["plan_sha256"] = digest(item["plan"])
    else:
        clock = NOW.replace(tzinfo=None)
    with pytest.raises(ValueError):
        audit_calendar(plans, db, now=clock)


def coverage_inputs(tmp_path):
    import hashlib
    from dataclasses import asdict

    from tests.support.experiment import approval_fixture, protocol_fixture, station_csv

    from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
    from climaprev.tools.experimental_campaign import build_target_calendar

    envelope = protocol_fixture()
    envelope["protocol"]["models"] = ["gfs_global"]
    envelope["protocol"]["horizons"] = [1]
    envelope["sha256"] = digest(envelope["protocol"])
    calendar = build_target_calendar(envelope, enabled=True, approvals=[approval_fixture(envelope)])
    target = calendar["calendar"]["targets"][0]
    slot = datetime(2030, 1, 1, tzinfo=UTC)
    start = datetime(2030, 1, 2, tzinfo=UTC)
    location = CanonicalLocation("Synthetic", 0, 0, "UTC", "fixture")
    capture = ForecastCapture("open-meteo", "gfs_global", "https://api.open-meteo.com/v1/forecast",
                              location, slot, start, start + timedelta(days=1))
    archive = archive_forecast(tmp_path / "captures", capture, {"synthetic": True})
    raw = station_csv([], [[]] * 24).replace(b"2030/01/01", b"2030/01/02")
    raw = raw.replace(b"2030/01/02;0000", b"2030/01/03;0000")
    source = tmp_path / "station.csv"
    source.write_bytes(raw)
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    assert ledger.reserve(target["job"], "open-meteo", slot, 30)
    ledger.finish(target["job"], str(archive), None)
    report = {"schema": "climaprev-variable-pairs-v1", "model": "gfs_global",
              "variable": "precipitation_mm", "unit": "mm", "aggregation": "sum",
              "forecast_semantics": "previous_hour_sum",
              "observed_semantics": "observed_previous_hour_sum",
              "capture_sha256": archive.stem, "source_sha256": hashlib.sha256(raw).hexdigest(),
              "station": {"code": "SYN", "latitude": 0, "longitude": 0},
              "location": asdict(location), "collected_at": slot.isoformat(),
              "rows": [{"date": "2030-01-02", "start_utc": start.isoformat(),
                        "end_utc": (start + timedelta(days=1)).isoformat(),
                        "forecast": 24.0, "observed": 0.0,
                        "eligible_exploratory": True, "eligible_confirmatory": True,
                        "comparable_as_identical_measurement": True, "exclusions": []}]}
    return calendar, ledger.path, report, archive, source


def test_target_coverage_binds_complete_pair_to_valid_capture_and_observational_source(tmp_path):
    from climaprev.tools.experimental_coverage import audit_target_coverage

    calendar, ledger, report, _, source = coverage_inputs(tmp_path)
    before = ledger.read_bytes()
    result = audit_target_coverage(calendar, ledger, [report],
                                   now=datetime(2030, 1, 4, tzinfo=UTC),
                                   observation_files={"SYN": source})
    assert result["planned_targets"] == 1
    assert result["due_targets"] == 1
    assert result["eligible_exploratory_targets"] == 1
    assert result["rows"][0]["reasons"] == []
    assert ledger.read_bytes() == before


@pytest.mark.parametrize("problem,reason", [
    ("missing", "capture_missing_or_invalid"), ("hash", "capture_missing_or_invalid"),
    ("partial", "pair_quality_exclusion"), ("absent", "paired_report_missing"),
    ("binding", "pair_capture_mismatch"), ("observation", "observation_source_mismatch"),
    ("location", "pair_location_mismatch"),
])
def test_completed_job_does_not_hide_missing_corrupt_or_ineligible_data(tmp_path, problem, reason):
    from climaprev.tools.experimental_coverage import audit_target_coverage

    calendar, ledger, report, archive, source = coverage_inputs(tmp_path)
    reports = [report]
    if problem == "missing":
        archive.unlink()
    elif problem == "hash":
        archive.write_text('{"corrupt":true}')
    elif problem == "partial":
        report["rows"][0]["eligible_exploratory"] = False
        report["rows"][0]["exclusions"] = ["incomplete_observation_interval"]
    elif problem == "absent":
        reports = []
    elif problem == "binding":
        report["capture_sha256"] = "another-capture"
    elif problem == "observation":
        source.write_text("changed-observation")
    else:
        report["location"]["longitude"] = 1
    result = audit_target_coverage(calendar, ledger, reports,
                                   now=datetime(2030, 1, 4, tzinfo=UTC),
                                   observation_files={"SYN": source})
    assert result["due_targets"] == 1
    assert result["eligible_exploratory_targets"] == 0
    assert reason in result["rows"][0]["reasons"]
