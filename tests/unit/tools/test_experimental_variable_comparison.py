from copy import deepcopy

import pytest
from tests.support.experiment import variable_report

from climaprev.tools.experimental_comparison import compare_variable_models


def test_known_multivariable_errors_use_the_same_cases_and_spec_defined_values():
    baseline = variable_report("baseline", [2, 14], [0, 10])
    candidate = variable_report("candidate", [1, 12], [0, 10])
    result = compare_variable_models([baseline, candidate], "baseline")
    group = result["groups"][0]
    assert group["common_cases"] == 2
    assert group["models"]["baseline"]["numerical"]["mae"] == 3
    assert group["models"]["candidate"]["numerical"]["mae"] == 1.5
    assert group["models"]["candidate"]["numerical"]["bias"] == 1.5
    assert group["models"]["candidate"]["numerical"]["rmse"] == pytest.approx(2.5 ** 0.5)
    assert group["models"]["candidate"]["relative_mae_gain"] == 0.5
    assert result["scientific_approval"] is False
    assert result["promotion_allowed"] is False


def test_missing_cases_use_common_sample_and_report_exclusions_and_absences():
    baseline = variable_report("b", [2, 14, 4], [0, 10, 0])
    candidate = variable_report("c", [1, None, 2], [0, 10, 0])
    candidate["rows"].pop()
    group = compare_variable_models([baseline, candidate], "b")["groups"][0]
    assert group["common_cases"] == 1
    assert group["reported_union_cases"] == 3
    assert group["models"]["c"]["excluded_unique_cases"] == 1
    assert group["models"]["c"]["absent_from_reported_union"] == 1
    assert group["models"]["b"]["eligible_outside_common"] == 2
    assert group["models"]["b"]["numerical"]["mae"] == 2


@pytest.mark.parametrize("mutation", ["observation", "source", "unit", "same_wrong_unit", "duplicate"])
def test_different_reference_units_and_duplicate_cases_fail_closed(mutation):
    baseline = variable_report("b", [2], [0])
    candidate = deepcopy(variable_report("c", [1], [0]))
    if mutation == "observation":
        candidate["rows"][0]["observed"] = 1
    elif mutation == "source":
        candidate["source_sha256"] = "different-source"
    elif mutation in {"unit", "same_wrong_unit"}:
        candidate["unit"] = "inch"
        if mutation == "same_wrong_unit":
            baseline["unit"] = "inch"
    else:
        candidate["rows"].append(deepcopy(candidate["rows"][0]))
    with pytest.raises(ValueError, match="reference|unit|duplicate"):
        compare_variable_models([baseline, candidate], "b")


def test_empty_population_is_undefined_instead_of_zero_error():
    group = compare_variable_models([variable_report(m, [], []) for m in ("b", "c")], "b")["groups"][0]
    assert group["common_cases"] == 0
    assert group["models"]["c"]["numerical"]["mae"] is None
    assert group["models"]["c"]["relative_mae_gain"] is None


def test_perfect_baseline_and_no_positive_event_do_not_imply_perfect_candidate_skill():
    group = compare_variable_models([variable_report(m, [0], [0]) for m in ("b", "c")], "b")["groups"][0]
    assert group["models"]["c"]["relative_mae_gain"] is None
    assert group["models"]["c"]["classification"]["detection"][-1]["recall"] is None


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, -1])
def test_invalid_rain_forecasts_are_rejected(value):
    with pytest.raises(ValueError):
        compare_variable_models([variable_report("b", [0], [0]),
                                 variable_report("c", [value], [0])], "b")


def test_collection_lead_is_explicit_and_unknown_run_cannot_enter_verified_cohort():
    reports = [variable_report(m, [1], [0]) for m in ("b", "c")]
    collected = compare_variable_models(reports, "b")
    assert collected["groups"][0]["strata"][0]["slot_lead_days"] == 1
    verified = compare_variable_models(reports, "b", cohort="verified_run")
    assert verified["groups"][0]["common_cases"] == 0
    assert verified["groups"][0]["models"]["c"]["excluded_reasons"]["run_not_verified"] == 1
    assert collected["cohort"] != verified["cohort"]


def test_requested_run_cannot_masquerade_as_verified_initialization():
    reports = [variable_report(m, [1], [0]) for m in ("b", "c")]
    for report in reports:
        report["run_evidence"] = {"basis": "requested_only", "run_at": report["collection_slot"]}
    result = compare_variable_models(reports, "b", cohort="verified_run")
    assert result["groups"][0]["common_cases"] == 0


def test_verified_runs_keep_initialization_and_exact_hour_lead_separate():
    reports = [variable_report(m, [1], [0]) for m in ("b", "c")]
    for report in reports:
        report["run_evidence"] = {"basis": "verified", "run_at": "2029-12-30T18:00:00+00:00",
                                  "verification_reference": "synthetic-provider-evidence"}
    result = compare_variable_models(reports, "b", cohort="verified_run")
    case = result["groups"][0]["paired_cases"][0]
    assert case["verified_run_lead_hours"] == 30
    assert case["identity"]["run_utc"] == "2029-12-30T18:00:00+00:00"
    reports[1]["run_evidence"]["run_at"] = "2029-12-30T12:00:00+00:00"
    assert compare_variable_models(reports, "b", cohort="verified_run")["groups"][0]["common_cases"] == 0


def test_d7_missing_v1_has_only_explicitly_secondary_model_comparison():
    reports = [variable_report(m, [1] * 7, [0] * 7) for m in ("v1", "gfs", "icon")]
    reports[0]["rows"].pop()
    result = compare_variable_models(reports, "v1", secondary_models=("gfs", "icon"))
    d7 = result["groups"][0]["strata"][-1]
    assert d7["slot_lead_days"] == 7
    assert d7["common_cases"] == 0
    assert d7["models"]["gfs"]["relative_mae_gain"] is None
    secondary = result["secondary_comparison"]
    assert secondary["comparison_role"] == "secondary_no_v1_control"
    assert secondary["groups"][0]["strata"][-1]["common_cases"] == 1
    assert secondary["promotion_allowed"] is False


def test_retrospective_pairs_require_opt_in_and_remain_diagnostic():
    reports = [variable_report(m, [1], [0]) for m in ("b", "c")]
    for report in reports:
        report.update(collection_slot="2030-01-01T00:00:00+00:00",
                      collection_deadline="2030-01-01T00:30:00+00:00",
                      collected_at="2030-01-01T00:05:00+00:00")
    assert compare_variable_models(reports, "b")["groups"][0]["common_cases"] == 0
    result = compare_variable_models(reports, "b", allow_retrospective=True)
    assert result["groups"][0]["common_cases"] == 1
    assert result["timing_mode"] == "retrospective_diagnostic"
    assert result["promotion_allowed"] is False
