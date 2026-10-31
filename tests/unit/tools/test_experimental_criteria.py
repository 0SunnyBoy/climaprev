from dataclasses import replace

import pytest

from climaprev.tools.experimental_criteria import RainCriteria, RainEvidence, evaluate_rain_criteria

# Synthetic criteria for exercising the contract; not an approved campaign.
CRITERIA = RainCriteria(0.05, 0.5, 0.8, 20, 5, 0.05, 0.05, 0.95)
EVIDENCE = RainEvidence(10, 8, 100, 90, 10, True, True,
                        (-3, -1), (-0.02, 0.03), (-0.01, 0.02), 0.95)


def test_met_diagnostic_does_not_authorize_promotion():
    result = evaluate_rain_criteria(CRITERIA, EVIDENCE)
    assert result["status"] == "met"
    assert result["relative_mae_gain"] == pytest.approx(0.2)
    assert result["absolute_mae_gain_mm"] == 2
    assert not result["scientific_approval"]
    assert not result["promotion_allowed"]


def test_extreme_precision_gate_requires_predicted_support_and_narrow_intervals():
    criteria = replace(CRITERIA, max_extreme_interval_width=0.1)
    assert evaluate_rain_criteria(criteria, EVIDENCE)["status"] == "inconclusive"
    evidence = replace(EVIDENCE, baseline_predicted_events=12, candidate_predicted_events=11)
    assert evaluate_rain_criteria(criteria, evidence)["status"] == "met"
    wide = replace(evidence, recall_difference_interval=(-0.02, 0.2))
    result = evaluate_rain_criteria(criteria, wide)
    assert result["status"] == "inconclusive"
    assert "extreme_intervals_too_wide" in result["missing_requirements"]


@pytest.mark.parametrize("changes,reason", [
    ({"mae_difference_interval": None}, "paired_uncertainty_missing"),
    ({"same_cases": False}, "identical_cases_not_established"),
    ({"independent_test": False}, "independent_test_not_established"),
    ({"common_pairs": 19}, "insufficient_pairs"),
    ({"observed_events": 0}, "insufficient_observed_events"),
    ({"planned_cases": 200}, "insufficient_common_coverage"),
    ({"baseline_mae": 0}, "mae_gain_undefined"),
    ({"candidate_mae": None}, "mae_gain_undefined"),
    ({"confidence": 0.9}, "confidence_not_matching"),
])
def test_missing_requirements_cannot_pass(changes, reason):
    result = evaluate_rain_criteria(CRITERIA, replace(EVIDENCE, **changes))
    assert result["status"] == "inconclusive"
    assert reason in result["missing_requirements"]


@pytest.mark.parametrize("changes,reason", [
    ({"candidate_mae": 9.8}, "absolute_gain_below_margin"),
    ({"candidate_mae": 9.8}, "relative_gain_below_margin"),
    ({"mae_difference_interval": (-1, 0)}, "mae_improvement_not_supported"),
    ({"recall_difference_interval": (-0.06, 0.02)}, "recall_protection_not_supported"),
    ({"false_alarm_difference_interval": (0, 0.06)}, "false_alarm_protection_not_supported"),
])
def test_small_gain_and_extreme_regressions_are_not_hidden(changes, reason):
    result = evaluate_rain_criteria(CRITERIA, replace(EVIDENCE, **changes))
    assert result["status"] == "not_met"
    assert reason in result["failed_criteria"]


@pytest.mark.parametrize("changes", [
    {"common_pairs": True}, {"observed_events": 91}, {"common_pairs": 101},
    {"candidate_mae": float("nan")}, {"baseline_mae": -1},
    {"recall_difference_interval": (-2, 0)}, {"mae_difference_interval": (1, -1)},
    {"false_alarm_difference_interval": (0, float("inf"))}, {"confidence": True},
])
def test_invalid_evidence_is_rejected(changes):
    with pytest.raises(ValueError):
        evaluate_rain_criteria(CRITERIA, replace(EVIDENCE, **changes))


@pytest.mark.parametrize("changes", [
    {"min_relative_mae_gain": 5}, {"min_pairs": True}, {"min_observed_events": 0},
    {"min_absolute_mae_gain_mm": -1}, {"max_recall_loss": float("nan")},
    {"confidence": 1}, {"min_pairs": 1.5},
])
def test_invalid_or_percentage_instead_of_fraction_is_rejected(changes):
    with pytest.raises(ValueError):
        replace(CRITERIA, **changes)
