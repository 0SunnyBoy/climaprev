from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pytest
from tests.support.experiment import approval_fixture, protocol_fixture

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
from climaprev.tools.experimental_campaign import CampaignLedger, build_manifest
from climaprev.tools.experimental_pilot_quota import audit_quota_progress, plan_quota_slot
from climaprev.tools.historical_experiment import digest

FIRST = datetime(2030, 1, 1, 18, tzinfo=UTC)


def protocol():
    value = protocol_fixture()
    value["protocol"]["slots"] = [FIRST.isoformat()]
    value["protocol"]["criteria"] = {"adaptive_technical_pilot": True, "quota_per_station_model": 14}
    value["sha256"] = digest(value["protocol"])
    return value


def test_missed_capture_gets_a_new_identity_and_targets_not_backdated():
    envelope = protocol()
    first = plan_quota_slot(envelope, {}, slot=FIRST, now=FIRST)
    tomorrow = FIRST + timedelta(days=1)
    next_plan = plan_quota_slot(envelope, {}, slot=tomorrow, now=tomorrow)
    assert first["requested_jobs"] == next_plan["requested_jobs"] == 2
    assert first["manifests"][0]["plan"]["jobs"][0]["key"] != next_plan["manifests"][0]["plan"]["jobs"][0]["key"]
    assert next_plan["manifests"][0]["plan"]["jobs"][0]["identity"]["slot"] == tomorrow.isoformat()
    assert not next_plan["promotion_allowed"]


def test_stations_models_at_quota_stop_without_recollecting_completed_pairs():
    dates = [(FIRST + timedelta(days=i)).date().isoformat() for i in range(14)]
    now = FIRST + timedelta(days=14)
    result = plan_quota_slot(protocol(), {"SYN": {"gfs_global": dates}}, slot=now, now=now)
    assert result["requested_jobs"] == 1
    assert result["manifests"][0]["plan"]["jobs"][0]["identity"]["model"] == "operational-baseline"
    done = plan_quota_slot(protocol(), {"SYN": {m: dates for m in ("gfs_global", "operational-baseline")}}, slot=now, now=now)
    assert done["quota_complete"] and done["requested_jobs"] == 0


def test_today_completed_pair_waits_for_another_day_without_duplicate_calls():
    result = plan_quota_slot(protocol(), {"SYN": {"gfs_global": [FIRST.date().isoformat()]}}, slot=FIRST, now=FIRST)
    assert result["requested_jobs"] == 1


def test_collection_requires_explicit_e1_even_when_planning_is_permitted():
    envelope = protocol()
    with pytest.raises(ValueError, match="E1"):
        plan_quota_slot(envelope, {}, slot=FIRST, now=FIRST, enabled=True)
    result = plan_quota_slot(envelope, {}, slot=FIRST, now=FIRST, enabled=True,
                             approvals=[approval_fixture(envelope)])
    assert result["manifests"][0]["plan"]["enabled"]


@pytest.mark.parametrize("receipts", [
    {"OTHER": {}}, {"SYN": {"unknown": []}},
    {"SYN": {"gfs_global": ["2030-01-01", "2030-01-01"]}},
    {"SYN": {"gfs_global": ["2031-01-01"]}},
])
def test_invalid_receipt_declarations_rejected(receipts):
    with pytest.raises(ValueError):
        plan_quota_slot(protocol(), receipts, slot=FIRST, now=FIRST)


def test_expired_slot_rejected_and_extended_pilot_invalidates_conditional_partitions():
    with pytest.raises(ValueError, match="no backfill"):
        plan_quota_slot(protocol(), {}, slot=FIRST, now=FIRST+timedelta(hours=1))
    result = plan_quota_slot(protocol(), {}, slot=FIRST+timedelta(days=20), now=FIRST)
    assert result["requires_partition_replan"]
    assert not result["confirmation_enabled"]


def test_quota_audit_counts_only_verified_d1_archive_and_keeps_missing_attempts(tmp_path):
    envelope = protocol()
    location = CanonicalLocation("Synthetic", 0, 0, "UTC", "test")
    manifest = build_manifest("synthetic", [location], ["operational-baseline", "gfs_global"],
                              FIRST, enabled=True, collection_authorized=True)
    ledger_path = tmp_path / "ledger.sqlite"
    ledger = CampaignLedger(ledger_path)
    job = manifest["plan"]["jobs"][0]
    collected = FIRST+timedelta(minutes=1)
    payload = {"forecast": {"location": asdict(location), "fetched_at": collected.isoformat(),
                           "days": [{"date": "2030-01-02", "precipitation_sum_mm": 1.5}]}}
    capture = ForecastCapture("open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast",
                              location, collected, FIRST, FIRST+timedelta(days=7),
                              selection_mode="automatic")
    archive = archive_forecast(tmp_path, capture, payload)
    assert ledger.reserve(job["key"], "open-meteo", collected, 30)
    ledger.finish(job["key"], str(archive), None)
    result = audit_quota_progress(envelope, [manifest], ledger_path, now=FIRST+timedelta(days=1))
    assert result["completed_dates"]["SYN"]["operational-baseline"] == ["2030-01-01"]
    assert result["completed_dates"]["SYN"]["gfs_global"] == []
    assert result["operational_audit"]["status_counts"]["missed"] == 1
    archive.write_text("corrupted", encoding="utf-8")
    rejected = audit_quota_progress(envelope, [manifest], ledger_path, now=FIRST+timedelta(days=1))
    assert rejected["completed_dates"]["SYN"]["operational-baseline"] == []
    assert len(rejected["rejected_completed_jobs"]) == 1
