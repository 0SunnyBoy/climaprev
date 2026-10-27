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
