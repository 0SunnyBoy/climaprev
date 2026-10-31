"""Consolidation retains the full calendar and already computed scores."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from tests.support.experiment import approval_fixture, protocol_fixture, variable_report

from climaprev.tools.experimental_campaign import CampaignLedger, build_target_calendar
from climaprev.tools.experimental_comparison import (
    compare_variable_models,
    export_study_report,
    paired_uncertainty,
)
from climaprev.tools.experimental_coverage import audit_target_coverage
from climaprev.tools.historical_experiment import canonical_json, digest


def inputs(tmp_path: Path) -> dict:
    protocol = protocol_fixture()
    protocol["protocol"].update(slots=["2029-12-31T00:00:00+00:00"], horizons=[1, 7])
    protocol["sha256"] = digest(protocol["protocol"])
    calendar = build_target_calendar(protocol, enabled=True, approvals=[approval_fixture(protocol)])
    CampaignLedger(tmp_path / "absent.sqlite")
    reports = [variable_report(m, [p], [0]) for m, p in (("operational-baseline", 2), ("gfs_global", 1))]
    comparison = compare_variable_models(reports, "operational-baseline")
    coverage = audit_target_coverage(calendar, tmp_path / "absent.sqlite", reports,
                                     now=datetime(2030, 2, 1, tzinfo=UTC), observation_files={})
    uncertainty = paired_uncertainty(comparison, block_days=7, repetitions=10, seed=1, confidence=0.95)
    paths = {}
    for name, data in (("protocol", protocol), ("calendar", calendar), ("coverage", coverage),
                       ("comparison", comparison), ("uncertainty", uncertainty)):
        paths[name + "_path"] = tmp_path / (name + ".json")
        paths[name + "_path"].write_text(canonical_json(data))
    paths["pair_paths"] = []
    for index, report in enumerate(reports):
        path = tmp_path / f"pair{index}.json"
        path.write_text(canonical_json(report))
        paths["pair_paths"].append(path)
    return paths


def test_export_keeps_omitted_targets_unique_exclusions_and_overlapping_reasons(tmp_path):
    result = export_study_report(tmp_path / "result.json", code_version="fixture", **inputs(tmp_path))
    payload = result["payload"]
    assert payload["population"]["planned_targets"] == 4
    assert payload["population"]["excluded_unique_targets"] == 4
    assert payload["population"]["eligible_targets"] == 0
    assert sum(payload["population"]["overlapping_reason_counts"].values()) > 4
    assert payload["comparison"]["groups"][0]["models"]["gfs_global"]["relative_mae_gain"] == 0.5
    assert result["protocol_sha256"]
    assert len(result["inputs"]) == 7
    assert payload["promotion_allowed"] is False


def test_reordering_pairs_is_byte_identical_and_idempotent(tmp_path):
    paths = inputs(tmp_path)
    output = tmp_path / "result.json"
    export_study_report(output, code_version="fixture", **paths)
    original = output.read_bytes()
    paths["pair_paths"].reverse()
    export_study_report(output, code_version="fixture", **paths)
    assert output.read_bytes() == original


def test_divergent_export_cannot_replace_existing_evidence(tmp_path):
    paths = inputs(tmp_path)
    output = tmp_path / "result.json"
    export_study_report(output, code_version="fixture", **paths)
    original = output.read_bytes()
    with pytest.raises(ValueError, match="overwrite"):
        export_study_report(output, code_version="changed", **paths)
    assert output.read_bytes() == original


@pytest.mark.parametrize("parent", ["comparison", "uncertainty", "coverage"])
def test_mismatched_parent_identity_is_refused(tmp_path, parent):
    import json

    paths = inputs(tmp_path)
    path = paths[parent + "_path"]
    data = json.loads(path.read_text())
    key = {"comparison": "input_reports_sha256", "uncertainty": "comparison_sha256",
           "coverage": "calendar_sha256"}[parent]
    data[key] = [] if parent == "comparison" else "changed"
    path.write_text(canonical_json(data))
    with pytest.raises(ValueError, match="identity"):
        export_study_report(tmp_path / "result.json", code_version="fixture", **paths)
    assert not (tmp_path / "result.json").exists()
