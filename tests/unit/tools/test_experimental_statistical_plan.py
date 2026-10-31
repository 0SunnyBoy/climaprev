from datetime import date, timedelta

import pytest

from climaprev.tools.experimental_criteria import RainCriteria
from climaprev.tools.experimental_statistical_plan import (
    allocate_family_confidence,
    assess_block_sensitivity,
    evaluate_development_family,
)
from climaprev.tools.experimental_uncertainty import RainPair


def test_bonferroni_allocation_is_prospective_and_does_not_validate_bootstrap():
    result = allocate_family_confidence(["mae", "recall", "false_alarm"], confidence=.95)
    assert result["plan"]["interval_confidence"] == pytest.approx(1-.05/3)
    assert not result["marginal_method_validated"] and not result["promotion_allowed"]
    assert result == allocate_family_confidence(["false_alarm", "mae", "recall"], confidence=.95)


@pytest.mark.parametrize("claims,confidence", [([], .95), (["a", "a "], .95), ([""], .95),
                                             (["a"], True), (["a"], 1.)])
def test_invalid_confidence_family_rejected(claims, confidence):
    with pytest.raises(ValueError):
        allocate_family_confidence(claims, confidence=confidence)


def test_short_calendar_segments_and_wet_dates_are_not_independent_support():
    days = [date(2024, 1, 1)+timedelta(days=i) for i in range(10)]
    days += [date(2024, 2, 1)+timedelta(days=i) for i in range(10)]
    pairs = [RainPair(station, day, 60., 70.+i, 65.)
             for i, day in enumerate(days) for station in ("A", "B")]
    result = assess_block_sensitivity(
        pairs, cohort_id="synthetic-D1", criteria=RainCriteria(.05, 0., .9, 10, 2, 0., 0., .95),
        planned_cases=50, block_lengths=[7, 14], event_threshold_mm=50., repetitions=30, seed=7,
    )
    assert result["observed_event_cases"] == 40 and result["observed_event_dates"] == 20
    assert result["independent_event_count"] is None
    assert result["sensitivity"][0]["nonoverlapping_calendar_blocks"] == 2
    assert result["sensitivity"][1]["short_segments"] == 2
    assert result["sensitivity"][1]["analysis"]["scores"]["mae"]["interval"] is None
    assert result["selected_block_days"] is None
    assert not result["confirmatory_support_established"]


def test_declared_family_uses_allocated_confidence_and_refuses_reserved_partitions():
    pairs = [RainPair("A", date(2024, 1, 1)+timedelta(days=i), 60., 70.+i, 65.) for i in range(20)]
    options = {"criteria": RainCriteria(.05, 0., .9, 10, 2, 0., 0., .95),
               "planned_cases": {"pooled": 20}, "block_days": 3,
               "event_threshold_mm": 50., "repetitions": 30, "seed": 7,
               "candidate_id": "synthetic", "partition": "development"}
    claims = {"pooled.mae": ("pooled", "mae"), "pooled.recall": ("pooled", "recall")}
    result = evaluate_development_family({"pooled": pairs}, claims, **options)
    assert result["claims"]["pooled.mae"]["score"]["confidence"] == pytest.approx(.975)
    assert result["claims"]["pooled.recall"]["score"]["interval"] is None
    assert not result["simultaneous_coverage_verified"]
    options["partition"] = "confirmation"
    with pytest.raises(ValueError, match="development-only"):
        evaluate_development_family({"pooled": pairs}, claims, **options)
