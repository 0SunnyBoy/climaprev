"""Prospective confidence allocation and development-only temporal support diagnostics."""

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import asdict, replace
from datetime import timedelta
from math import isfinite
from pathlib import Path
from typing import Any

from climaprev.tools.experimental_criteria import RainCriteria
from climaprev.tools.experimental_uncertainty import RainPair, evaluate_paired_rain
from climaprev.tools.historical_experiment import digest


def allocate_family_confidence(claims: Sequence[str], *, confidence: float) -> dict[str, Any]:
    """Bonferroni allocation for a pre-selected finite family, not CI validation.

    Simultaneous coverage requires valid marginal intervals at the allocated
    confidence. Bootstrap validity and preregistration are not established here.
    """
    names = [name.strip() for name in claims]
    if (not names or any(not name for name in names) or len(set(names)) != len(names)
            or isinstance(confidence, bool) or not isinstance(confidence, (int, float))
            or not isfinite(confidence) or not 0 < confidence < 1):
        raise ValueError("unique predeclared claims and valid family confidence required")
    individual = 1-(1-confidence)/len(names)
    if not 0 < individual < 1:
        raise ValueError("confidence allocation exceeds numerical precision")
    plan = {"method": "bonferroni-confidence-allocation", "claims": sorted(names),
            "family_confidence": confidence, "interval_confidence": individual,
            "marginal_alpha": (1-confidence)/len(names)}
    return {"schema": "climaprev-confidence-family-plan-v1", "plan": plan,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "plan_sha256": digest(plan), "marginal_method_validated": False,
            "scientific_approval": False, "promotion_allowed": False}


def assess_block_sensitivity(
    pairs: Sequence[RainPair], *, cohort_id: str, criteria: RainCriteria,
    planned_cases: int, block_lengths: Sequence[int], event_threshold_mm: float,
    repetitions: int, seed: int,
) -> dict[str, Any]:
    """Descriptive block support plus paired exploratory intervals; never choose a winner.

    Calendar blocks and wet dates are not independently occurring weather events.
    This function is for eligible development data, not reserved outcomes.
    """
    blocks = list(block_lengths)
    if (not cohort_id.strip() or not blocks or len(set(blocks)) != len(blocks)
            or any(isinstance(b, bool) or not isinstance(b, int) or b < 1 for b in blocks)):
        raise ValueError("cohort identity and distinct positive block lengths required")
    dates = sorted({row.day for row in pairs})
    segments: list[int] = []
    previous = None
    for day in dates:
        if previous is None or day != previous+timedelta(days=1):
            segments.append(0)
        segments[-1] += 1
        previous = day
    rows = []
    for block in blocks:
        diagnostic = evaluate_paired_rain(
            pairs, criteria=criteria, planned_cases=planned_cases,
            event_threshold_mm=event_threshold_mm, block_days=block,
            repetitions=repetitions, seed=seed,
        )
        rows.append({"block_days": block,
                     "nonoverlapping_calendar_blocks": sum(length//block for length in segments),
                     "short_segments": sum(length < block for length in segments),
                     "analysis": diagnostic})
    return {
        "schema": "climaprev-development-block-support-v1", "cohort_id": cohort_id,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "criteria_sha256": digest(asdict(criteria)), "calendar_dates": len(dates),
        "calendar_segment_lengths": segments,
        "observed_event_dates": len({row.day for row in pairs if row.observed >= event_threshold_mm}),
        "observed_event_cases": sum(row.observed >= event_threshold_mm for row in pairs),
        "sensitivity": rows, "selected_block_days": None,
        "independent_event_count": None, "confirmatory_support_established": False,
        "intervals_are_marginal": True, "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["No block is selected using performance or interval width.",
                        "Multiplicity allocation does not repair invalid marginal intervals.",
                        "No power or effective independent-event minimum is inferred."],
    }


def evaluate_development_family(
    cohorts: Mapping[str, Sequence[RainPair]], claims: Mapping[str, tuple[str, str]], *,
    criteria: RainCriteria, planned_cases: Mapping[str, int], block_days: int,
    event_threshold_mm: float, repetitions: int, seed: int,
    candidate_id: str, partition: str,
) -> dict[str, Any]:
    """Compute only declared development intervals at allocated confidence.

    No claim of valid simultaneous coverage follows from applying an allocation
    to exploratory bootstrap intervals. Reserved selection/confirmation is refused.
    """
    if partition != "development" or not candidate_id.strip() or not claims:
        raise ValueError("explicit candidate and development-only family required")
    if (any(not name or name != name.strip() or metric not in {"mae", "recall", "false_alarm"}
            for name, (_, metric) in claims.items())
            or len(set(claims.values())) != len(claims)
            or {cohort for cohort, _ in claims.values()} != set(cohorts)
            or set(planned_cases) != set(cohorts)):
        raise ValueError("claims, metrics and planned cohorts differ")
    allocation = allocate_family_confidence(list(claims), confidence=criteria.confidence)
    adjusted = replace(criteria, confidence=allocation["plan"]["interval_confidence"])
    analyses = {cohort: evaluate_paired_rain(
        rows, criteria=adjusted, planned_cases=planned_cases[cohort],
        event_threshold_mm=event_threshold_mm, block_days=block_days,
        repetitions=repetitions, seed=seed,
    ) for cohort, rows in cohorts.items()}
    selected = {name: {"cohort": cohort, "metric": metric,
                       "score": analyses[cohort]["scores"].get(metric)}
                for name, (cohort, metric) in claims.items()}
    return {
        "schema": "climaprev-development-declared-family-v1", "partition": partition,
        "candidate_id": candidate_id, "confidence_allocation": allocation,
        "cohort_input_sha256": {name: result["paired_input_sha256"] for name, result in analyses.items()},
        "claims": selected, "block_days": block_days,
        "all_intervals_computable": all(row["score"] and row["score"]["interval"] is not None
                                         for row in selected.values()),
        "marginal_method_validated": False, "simultaneous_coverage_verified": False,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scientific_approval": False, "promotion_allowed": False,
    }
