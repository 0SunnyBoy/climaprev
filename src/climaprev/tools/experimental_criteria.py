"""Diagnostic scientific criteria; consumes evidence, never computes CIs or promotes."""

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True, slots=True)
class RainCriteria:
    min_relative_mae_gain: float
    min_absolute_mae_gain_mm: float
    min_common_coverage: float
    min_pairs: int
    min_observed_events: int
    max_recall_loss: float
    max_false_alarm_increase: float
    confidence: float
    max_extreme_interval_width: float | None = None

    def __post_init__(self) -> None:
        for field, value in asdict(self).items():
            if field == "max_extreme_interval_width" and value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError(f"invalid criterion: {field}")
        for value in (self.min_relative_mae_gain, self.min_common_coverage,
                      self.max_recall_loss, self.max_false_alarm_increase):
            if not 0 <= value <= 1:
                raise ValueError("criteria fractions must be between zero and one")
        if self.min_absolute_mae_gain_mm < 0 or not 0 < self.confidence < 1:
            raise ValueError("invalid physical margin or confidence")
        for value in (self.min_pairs, self.min_observed_events):
            if not isinstance(value, int) or value < 1:
                raise ValueError("positive integer support required")
        if self.max_extreme_interval_width is not None and not 0 < self.max_extreme_interval_width <= 2:
            raise ValueError("invalid extreme interval width")


@dataclass(frozen=True, slots=True)
class RainEvidence:
    baseline_mae: float | None
    candidate_mae: float | None
    planned_cases: int
    common_pairs: int
    observed_events: int
    same_cases: bool
    independent_test: bool
    # All intervals are candidate minus baseline, paired on identical cases.
    mae_difference_interval: tuple[float, float] | None = None
    recall_difference_interval: tuple[float, float] | None = None
    false_alarm_difference_interval: tuple[float, float] | None = None
    confidence: float | None = None
    baseline_predicted_events: int | None = None
    candidate_predicted_events: int | None = None


def evaluate_rain_criteria(criteria: RainCriteria, evidence: RainEvidence) -> dict[str, Any]:
    """Evaluate explicit caller-supplied criteria, with no approved default values.

    Evidence independence and interval methodology are declared inputs, not
    authenticated here. A met result is not scientific approval or promotion.
    Missing support/intervals yields inconclusive rather than apparent success.
    """
    for count in (evidence.planned_cases, evidence.common_pairs, evidence.observed_events):
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("nonnegative integer evidence counts required")
    if not evidence.observed_events <= evidence.common_pairs <= evidence.planned_cases:
        raise ValueError("events, pairs and planned counts are inconsistent")
    for predicted_count in (evidence.baseline_predicted_events, evidence.candidate_predicted_events):
        if predicted_count is not None and (
            isinstance(predicted_count, bool) or not isinstance(predicted_count, int)
            or not 0 <= predicted_count <= evidence.common_pairs
        ):
            raise ValueError("invalid predicted event support")
    for mae in (evidence.baseline_mae, evidence.candidate_mae):
        if mae is not None and (isinstance(mae, bool) or not isinstance(mae, (int, float))
                                or not isfinite(mae) or mae < 0):
            raise ValueError("MAE must be finite, nonnegative or null")
    intervals = (evidence.mae_difference_interval, evidence.recall_difference_interval,
                 evidence.false_alarm_difference_interval)
    for index, interval in enumerate(intervals):
        if interval is not None and (
            len(interval) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                      or not isfinite(v) for v in interval)
            or interval[0] > interval[1]
            or (index > 0 and not -1 <= interval[0] <= interval[1] <= 1)
        ):
            raise ValueError("invalid difference interval")
    if evidence.confidence is not None and (
        isinstance(evidence.confidence, bool) or not isinstance(evidence.confidence, (int, float))
        or not isfinite(evidence.confidence) or not 0 < evidence.confidence < 1
    ):
        raise ValueError("invalid evidence confidence")
    missing = []
    coverage = evidence.common_pairs / evidence.planned_cases if evidence.planned_cases else None
    if evidence.same_cases is not True:
        missing.append("identical_cases_not_established")
    if evidence.independent_test is not True:
        missing.append("independent_test_not_established")
    if evidence.common_pairs < criteria.min_pairs:
        missing.append("insufficient_pairs")
    if evidence.observed_events < criteria.min_observed_events:
        missing.append("insufficient_observed_events")
    if coverage is None or coverage < criteria.min_common_coverage:
        missing.append("insufficient_common_coverage")
    if evidence.baseline_mae in (None, 0) or evidence.candidate_mae is None:
        missing.append("mae_gain_undefined")
    if any(interval is None for interval in intervals):
        missing.append("paired_uncertainty_missing")
    if evidence.confidence != criteria.confidence:
        missing.append("confidence_not_matching")
    if criteria.max_extreme_interval_width is not None:
        if not evidence.baseline_predicted_events or not evidence.candidate_predicted_events:
            missing.append("predicted_event_support_missing")
        if any(interval is not None and interval[1] - interval[0] > criteria.max_extreme_interval_width
               for interval in intervals[1:]):
            missing.append("extreme_intervals_too_wide")
    absolute_gain = (evidence.baseline_mae - evidence.candidate_mae
                     if evidence.baseline_mae is not None and evidence.candidate_mae is not None
                     else None)
    relative_gain = (absolute_gain / evidence.baseline_mae
                     if absolute_gain is not None and evidence.baseline_mae not in (None, 0)
                     else None)
    failures = []
    if absolute_gain is not None and absolute_gain < criteria.min_absolute_mae_gain_mm:
        failures.append("absolute_gain_below_margin")
    if relative_gain is not None and relative_gain < criteria.min_relative_mae_gain:
        failures.append("relative_gain_below_margin")
    if evidence.mae_difference_interval and evidence.mae_difference_interval[1] >= 0:
        failures.append("mae_improvement_not_supported")
    if (evidence.recall_difference_interval
            and evidence.recall_difference_interval[0] < -criteria.max_recall_loss):
        failures.append("recall_protection_not_supported")
    if (evidence.false_alarm_difference_interval
            and evidence.false_alarm_difference_interval[1] > criteria.max_false_alarm_increase):
        failures.append("false_alarm_protection_not_supported")
    return {
        "schema": "climaprev-rain-criteria-diagnostic-v1",
        "status": "inconclusive" if missing else "not_met" if failures else "met",
        "missing_requirements": missing, "failed_criteria": failures,
        "absolute_mae_gain_mm": absolute_gain, "relative_mae_gain": relative_gain,
        "common_coverage": coverage, "criteria": asdict(criteria),
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Declared evidence and supplied intervals are not independently audited.",
                        "No interval calculation, campaign execution or approval occurs here."],
    }
