import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pytest
from tests.support.experiment import protocol_fixture, station_csv

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
from climaprev.tools.experimental_campaign import (
    CampaignLedger,
    build_manifest,
    build_target_calendar,
)
from climaprev.tools.experimental_pilot_report import build_pilot_report, main
from climaprev.tools.historical_experiment import digest

FIRST = datetime(2030, 1, 1, 18, tzinfo=UTC)


def prepared(tmp_path, *, collect=True):
    envelope = protocol_fixture()
    p = envelope["protocol"]
    p["models"] = ["operational-baseline"]
    p["slots"] = [(FIRST+timedelta(days=i)).isoformat() for i in range(14)]
    p["criteria"] = {"adaptive_technical_pilot": True, "quota_per_station_model": 14}
    envelope["sha256"] = digest(p)
    ledger_path = tmp_path / "ledger.sqlite"
    ledger = CampaignLedger(ledger_path)
    location = CanonicalLocation("Synthetic", 0, 0, "UTC", "test")
    manifests = []
    for i in range(15):
        slot = FIRST+timedelta(days=i)
        manifest = build_manifest("synthetic", [location], ["operational-baseline"], slot,
                                  enabled=True, collection_authorized=True)
        manifests.append(manifest)
        if not collect or i == 1:
            continue
        stamp = slot+timedelta(minutes=1)
        capture = ForecastCapture("open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast",
                                  location, stamp, slot, slot+timedelta(days=8), selection_mode="automatic")
        payload = {"forecast": {"location": asdict(location), "fetched_at": stamp.isoformat(),
                               "days": [{"date": (slot+timedelta(days=1)).date().isoformat(),
                                         "precipitation_sum_mm": 0.}]}}
        archive = archive_forecast(tmp_path, capture, payload)
        job = manifest["plan"]["jobs"][0]["key"]
        assert ledger.reserve(job, "open-meteo", stamp, 30)
        ledger.finish(job, str(archive), None)
    return envelope, manifests, ledger_path


def test_completed_quota_preserves_missed_attempt_and_requires_real_observation_tail(tmp_path):
    envelope, manifests, ledger = prepared(tmp_path)
    now = FIRST+timedelta(days=22)
    without_truth = build_pilot_report(envelope, manifests, ledger, now=now)
    assert without_truth["quota_complete"] and not without_truth["technical_pilot_complete"]
    assert without_truth["closure_status"] == "observation_gaps_after_tail"
    assert without_truth["accepted_replacement_captures"] == 1
    assert without_truth["operational_audit"]["status_counts"]["missed"] == 1
    csv = tmp_path / "observations.csv"
    csv.write_bytes(station_csv([], [[] for _ in range(22*24)]))
    complete = build_pilot_report(envelope, manifests, ledger, now=now, observations={"SYN": csv})
    assert complete["technical_pilot_complete"]
    assert complete["closure_status"] == "complete"
    assert not complete["scientific_approval"] and not complete["promotion_allowed"]
    csv.write_bytes(csv.read_bytes().replace(b"2030/01/02;0100 UTC;0;", b"2030/01/02;0100 UTC;;"))
    incomplete = build_pilot_report(envelope, manifests, ledger, now=now, observations={"SYN": csv})
    assert not incomplete["technical_pilot_complete"]
    assert "2030-01-02" in incomplete["observations"][0]["incomplete_due_dates"]


def test_empty_pilot_never_closes_or_fabricates_a_tail(tmp_path):
    envelope, manifests, ledger = prepared(tmp_path, collect=False)
    result = build_pilot_report(envelope, manifests, ledger, now=FIRST-timedelta(hours=1))
    assert result["accepted_captures"] == 0
    assert result["actual_observation_tail_end"] is None
    assert not result["technical_pilot_complete"]
    assert result["observations"][0]["due_hour_coverage"] is None


def test_future_observation_targets_stay_pending(tmp_path):
    envelope, manifests, ledger = prepared(tmp_path)
    result = build_pilot_report(envelope, manifests, ledger, now=FIRST+timedelta(days=15))
    assert result["quota_complete"]
    assert result["observations"][0]["pending_days"] > 0
    assert not result["observation_tail_complete"]
    assert result["closure_status"] == "waiting_for_observation_tail"


def test_report_cli_rejects_a_different_protocol_before_writing(tmp_path, monkeypatch):
    envelope, _, ledger = prepared(tmp_path, collect=False)
    calendar = build_target_calendar(envelope)
    other = json.loads(json.dumps(envelope))
    other["protocol"]["id"] = "different-study"
    other["sha256"] = digest(other["protocol"])
    protocol_path, calendar_path, output = (tmp_path/name for name in ("protocol.json", "calendar.json", "result.json"))
    protocol_path.write_text(json.dumps(other), encoding="utf-8")
    calendar_path.write_text(json.dumps(calendar), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["pilot-report", "--protocol", str(protocol_path),
                                     "--calendar", str(calendar_path), "--ledger", str(ledger),
                                     "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2 and not output.exists()
