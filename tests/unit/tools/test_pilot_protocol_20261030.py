"""Check the committed preparation contracts without reading weather outcomes."""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from climaprev.tools.experimental_campaign import build_target_calendar, validate_target_calendar
from climaprev.tools.experimental_preparation import TemporalPartition, validate_partitions
from climaprev.tools.experimental_protocol import validate_protocol
from climaprev.tools.historical_experiment import digest

DOCS = Path(__file__).resolve().parents[3] / "docs/planejamento/reference-candidate-1"


def read(name):
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def test_pilot_protocol_binds_criteria_and_partitions_without_authorizing_collection():
    envelope = read("protocolo-consolidado-2026-10-30.json")
    protocol = validate_protocol(envelope)
    criteria = read("criterios-consolidados-2026-10-30.json")
    partitions = read("particoes-temporais-2026-10-30.json")
    assert protocol["criteria"]["plan_sha256"] == digest(criteria)
    assert protocol["criteria"]["partition_plan_sha256"] == digest(partitions)
    assert criteria["uncertainty"]["final_block_days"] is None
    assert not protocol["criteria"]["confirmatory_ready"]
    calendar = validate_target_calendar(build_target_calendar(envelope))
    assert not calendar["enabled"] and not calendar["approvals"]
    assert sum(len(m["plan"]["jobs"]) for m in calendar["manifests"]) == 210
    assert len(calendar["targets"]) == 630


def test_rescheduled_d7_targets_fit_development_and_preserve_issuance_embargo():
    protocol = validate_protocol(read("protocolo-consolidado-2026-10-30.json"))
    schedule = read("particoes-temporais-2026-10-30.json")
    parts = [TemporalPartition(p["name"], date.fromisoformat(p["start"]), date.fromisoformat(p["end"]))
             for p in schedule["partitions"]]
    assert datetime.fromisoformat(protocol["slots"][-1]).date() + timedelta(days=7) <= parts[0].end
    result = validate_partitions(parts, embargo_days=7, max_horizon_days=7,
                                 candidate_frozen_at=datetime.fromisoformat(schedule["candidate_freeze_deadline"]))
    assert not result["confirmation_enabled"]
    assert not result["prospective_independence_verified"]
