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
