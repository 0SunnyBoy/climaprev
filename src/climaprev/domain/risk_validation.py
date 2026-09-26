"""Offline validation helpers for the heuristic risk policy.

This module deliberately does not fetch or invent historical observations. A
caller must provide an approved dataset containing a forecast and the observed
risk level for the same period. That keeps calibration reproducible and makes
the current policy the safe fallback when no validated dataset is available.
"""

from dataclasses import dataclass
from typing import Literal

from climaprev.domain.models import NormalizedForecast
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy

RiskLevel = Literal["low", "moderate", "high"]


@dataclass(frozen=True, slots=True)
class HistoricalRiskCase:
    forecast: NormalizedForecast
    observed_level: RiskLevel


@dataclass(frozen=True, slots=True)
class RiskValidationReport:
    cases: int
    correct: int
    false_positives: int
    false_negatives: int
    accuracy: float
    policy_version: str


def validate_policy(
    cases: tuple[HistoricalRiskCase, ...],
    policy: RiskPolicy,
    evaluator: RiskEvaluator | None = None,
) -> RiskValidationReport:
    """Compare policy classifications with reviewed historical observations."""

    risk_evaluator = evaluator or RiskEvaluator()
    correct = false_positives = false_negatives = 0
    for case in cases:
        predicted = risk_evaluator.evaluate(case.forecast, policy).level
        if predicted == case.observed_level:
            correct += 1
        elif _rank(predicted) > _rank(case.observed_level):
            false_positives += 1
        else:
            false_negatives += 1

    total = len(cases)
    return RiskValidationReport(
        cases=total,
        correct=correct,
        false_positives=false_positives,
        false_negatives=false_negatives,
        accuracy=correct / total if total else 0.0,
        policy_version=policy.policy_version,
    )


def _rank(level: RiskLevel) -> int:
    return {"low": 0, "moderate": 1, "high": 2}[level]
