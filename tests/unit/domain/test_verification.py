from math import sqrt

import pytest

from climaprev.domain.risk_policy import ExperimentalRiskPolicy, RiskPolicy, policy_fingerprint
from climaprev.domain.verification import classify_pairs, numerical_pairs


def test_matrix_orientation_and_separate_false_alarm_denominators() -> None:
    score = classify_pairs([
        ("low", "low"), ("low", "moderate"), ("moderate", "high"),
        ("high", "low"), ("high", "high"),
    ])
    assert score.confusion_matrix == ((1, 1, 0), (0, 0, 1), (1, 0, 1))
    assert score.accuracy == 2 / 5
    assert score.classes[2].support == 2
    assert score.classes[2].precision == 1 / 2
    assert score.classes[2].recall == 1 / 2
    high = score.detection[1]
    assert (high.hits, high.misses, high.false_alarms, high.correct_negatives) == (1, 1, 1, 2)
    assert high.false_alarm_ratio == 1 / 2
    assert high.false_positive_rate == 1 / 3
    assert score.detection[0].recall == 2 / 3


def test_undefined_scores_are_null_with_explicit_zero_support() -> None:
    score = classify_pairs([])
    assert score.cases == 0
    assert score.accuracy is None and score.macro_f1 is None
    assert score.classes[2].support == 0
    assert score.classes[2].recall is None
    assert score.detection[1].false_alarm_ratio is None
    assert classify_pairs([("high", "low")]).classes[2].f1 == 0


def test_numerical_verification_uses_forecast_minus_observed() -> None:
    score = numerical_pairs([(1.0, 2.0), (3.0, 1.0)])
    assert score.bias == -0.5 and score.mae == 1.5
    assert score.rmse == sqrt(2.5)
    assert numerical_pairs([]).mae is None
    with pytest.raises(ValueError, match="finite"):
        numerical_pairs([(float("nan"), 1.0)])


def test_candidate_identity_does_not_change_v1_and_tracks_parameters() -> None:
    baseline = RiskPolicy()
    candidate = ExperimentalRiskPolicy(hourly_rain_moderate_mm=21)
    assert baseline.hourly_rain_moderate_mm == 20
    assert baseline.policy_version == "reference-v1"
    assert candidate.policy_version == "reference-candidate-1"
    assert policy_fingerprint(candidate) != policy_fingerprint(ExperimentalRiskPolicy())
    assert policy_fingerprint(baseline) == policy_fingerprint(RiskPolicy())


@pytest.mark.parametrize("parameters", [
    {"policy_version": "reference-v1"}, {"policy_version": "reference-candidate-"},
    {"hourly_rain_high_mm": 10}, {"hourly_rain_moderate_mm": -1},
    {"temperature_min_high_c": 8}, {"wind_gust_high_kmh": float("nan")},
    {"daily_rain_high_mm": True},
])
def test_candidate_rejects_misleading_versions_and_invalid_thresholds(parameters) -> None:
    with pytest.raises(ValueError):
        ExperimentalRiskPolicy(**parameters)
