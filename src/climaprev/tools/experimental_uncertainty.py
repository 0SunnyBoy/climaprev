"""Offline paired rain uncertainty; no data acquisition, fitting or promotion."""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from functools import partial
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.bootstrap import bootstrap_dates
from climaprev.tools.experimental_comparison import compare_rain_models
from climaprev.tools.experimental_criteria import RainCriteria, RainEvidence, evaluate_rain_criteria
from climaprev.tools.historical_experiment import digest


@dataclass(frozen=True, slots=True)
class RainPair:
    station: str
    day: date
    observed: float
    baseline: float
    candidate: float

    def __post_init__(self) -> None:
        if not isinstance(self.station, str) or not self.station.strip() or type(self.day) is not date:
            raise ValueError("station and calendar date required")
        for value in (self.observed, self.baseline, self.candidate):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
                raise ValueError("rain must be finite and nonnegative")


def evaluate_paired_rain(
    pairs: Sequence[RainPair], *, criteria: RainCriteria, planned_cases: int,
    event_threshold_mm: float, block_days: int, repetitions: int, seed: int,
) -> dict[str, Any]:
    """One caller-selected horizon/experiment, clustering all stations by date.

    Pair eligibility, provenance and partition independence must be verified upstream.
    Independence remains false: this diagnostic cannot certify its own input data.
    Intervals are marginal exploratory percentile intervals, not multiplicity adjusted.
    """
    if isinstance(planned_cases, bool) or not isinstance(planned_cases, int) or planned_cases < len(pairs):
        raise ValueError("planned cases must include every pair")
    for value, minimum in ((block_days, 1), (repetitions, 2)):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError("invalid resampling parameters")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("integer seed required")
    if (isinstance(event_threshold_mm, bool) or not isinstance(event_threshold_mm, (int, float))
            or not isfinite(event_threshold_mm) or event_threshold_mm <= 0):
        raise ValueError("positive finite event threshold required")
    ordered = sorted(pairs, key=lambda row: (row.day, row.station))
    if len({(row.station, row.day) for row in ordered}) != len(ordered):
        raise ValueError("duplicate station/date: separate horizons and experiments")

    def difference(rows: Sequence[RainPair], metric: str) -> float | None:
        if metric == "mae":
            return sum(abs(row.candidate-row.observed)-abs(row.baseline-row.observed)
                       for row in rows)/len(rows)
        observed = [row for row in rows if row.observed >= event_threshold_mm]
        if metric == "recall":
            if not observed:
                return None
            return sum(int(row.candidate >= event_threshold_mm)
                       - int(row.baseline >= event_threshold_mm) for row in observed)/len(observed)
        rates = []
        for arm in ("baseline", "candidate"):
            predicted = [row for row in rows if getattr(row, arm) >= event_threshold_mm]
            if not predicted:
                return None
            rates.append(sum(row.observed < event_threshold_mm for row in predicted)/len(predicted))
        return rates[1]-rates[0]

    scores = {}
    for metric in ("mae", "recall", "false_alarm") if ordered else ():
        scores[metric] = bootstrap_dates(
            ordered, day=lambda row: row.day,
            statistic=partial(difference, metric=metric),
            block_days=block_days, repetitions=repetitions, seed=seed,
            confidence=criteria.confidence,
        )
    evidence = RainEvidence(
        baseline_mae=sum(abs(row.baseline-row.observed) for row in ordered)/len(ordered) if ordered else None,
        candidate_mae=sum(abs(row.candidate-row.observed) for row in ordered)/len(ordered) if ordered else None,
        planned_cases=planned_cases, common_pairs=len(ordered),
        observed_events=sum(row.observed >= event_threshold_mm for row in ordered),
        baseline_predicted_events=sum(row.baseline >= event_threshold_mm for row in ordered),
        candidate_predicted_events=sum(row.candidate >= event_threshold_mm for row in ordered),
        same_cases=True, independent_test=False,
        mae_difference_interval=scores["mae"].interval if scores else None,
        recall_difference_interval=scores["recall"].interval if scores else None,
        false_alarm_difference_interval=scores["false_alarm"].interval if scores else None,
        confidence=criteria.confidence,
    )
    return {
        "schema": "climaprev-paired-rain-uncertainty-v1",
        "method": "paired-calendar-moving-block-percentile",
        "paired_input_sha256": digest([
            {"station": row.station, "date": row.day.isoformat(),
             "observed": row.observed, "baseline": row.baseline, "candidate": row.candidate}
            for row in ordered
        ]),
        "event_threshold_mm": event_threshold_mm,
        "scores": {metric: asdict(score) for metric, score in scores.items()},
        "evidence": asdict(evidence), "diagnostic": evaluate_rain_criteria(criteria, evidence),
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": [
            "Input provenance, eligibility and independent partitions are not certified here.",
            "Block length and effective support require development-data diagnostics.",
            "Intervals are marginal exploratory intervals without multiplicity adjustment.",
            "Missing pairs can bias estimates; planned coverage remains explicit.",
            "False alarm means false alarms divided by predicted events.",
        ],
    }


def evaluate_development_reports(
    reports: Sequence[dict[str, Any]], *, baseline: str, candidate: str,
    planned_dates: dict[str, Sequence[date]], development_start: date, development_end: date,
    allowed_sources: set[str], lead_days: int, criteria: RainCriteria,
    event_threshold_mm: float, block_lengths: Sequence[int], repetitions: int, seed: int,
    require_run: bool = True,
) -> dict[str, Any]:
    """Validate v2 pair reports and evaluate a declared development-only calendar.

    The caller must supply the already-authorized source allowlist and partition.
    Declared hashes/eligibility are checked for consistency, not authenticated.
    Selection/confirmation cannot be certified or executed by this function.
    """
    if development_start > development_end or baseline == candidate or not baseline or not candidate:
        raise ValueError("distinct arms and ordered development partition required")
    if isinstance(lead_days, bool) or not isinstance(lead_days, int) or lead_days < 1:
        raise ValueError("positive collection-day lead required")
    blocks = list(block_lengths)
    if (not blocks or any(isinstance(n, bool) or not isinstance(n, int) or n < 1 for n in blocks)
            or len(set(blocks)) != len(blocks)):
        raise ValueError("distinct positive block lengths required")
    calendar: set[tuple[str, date]] = set()
    for station, days in planned_dates.items():
        if not station.strip() or len(set(days)) != len(days):
            raise ValueError("station calendar must be unique")
        for day in days:
            if type(day) is not date or not development_start <= day <= development_end:
                raise ValueError("calendar outside declared development partition")
            calendar.add((station, day))
    if not calendar:
        raise ValueError("explicit planned calendar required")
    filtered = []
    slots: dict[tuple[str, date], int] = {}
    for report in reports:
        if report.get("schema") != "climaprev-station-rain-pairs-v2":
            raise ValueError("v2 rain pair report required")
        if report["model"] not in (baseline, candidate):
            raise ValueError("unexpected experimental arm")
        source = report["source_sha256"]
        if (not isinstance(source, str) or len(source) != 64
                or any(c not in "0123456789abcdef" for c in source) or source not in allowed_sources):
            raise ValueError("observation source not in development allowlist")
        collected = datetime.fromisoformat(report["collected_at"])
        if collected.utcoffset() is None:
            raise ValueError("aware collection time required")
        selected = []
        for row in report["rows"]:
            day = date.fromisoformat(row["date"])
            if not development_start <= day <= development_end:
                raise ValueError("report includes targets outside development partition")
            if row["collection_lead_days"] != lead_days:
                continue
            key = (report["station"]["code"], day)
            if key not in calendar:
                raise ValueError("reported case outside planned calendar")
            slot = int(collected.astimezone(UTC).timestamp()) // 1800
            if key in slots and slots[key] != slot:
                raise ValueError("arms must share a collection slot")
            slots[key] = slot
            selected.append(row)
        filtered.append({**report, "rows": selected})
    comparison = compare_rain_models(filtered, baseline, require_run=require_run, include_cases=True)
    pairs = [RainPair(
        row["station"], datetime.fromisoformat(row["start_utc"]).astimezone(
            ZoneInfo(row["timezone"])).date(), row["observed_mm"],
        row["forecasts_mm"][baseline], row["forecasts_mm"][candidate],
    ) for row in comparison["paired_cases"]]

    def evaluate(rows: Sequence[RainPair], planned: int) -> list[dict[str, Any]]:
        return [evaluate_paired_rain(
            rows, criteria=criteria, planned_cases=planned, event_threshold_mm=event_threshold_mm,
            block_days=block, repetitions=repetitions, seed=seed,
        ) for block in blocks]

    return {
        "schema": "climaprev-development-rain-uncertainty-v1",
        "partition": {"name": "development", "start": development_start.isoformat(),
                      "end": development_end.isoformat()},
        "input_reports_sha256": [digest(report) for report in reports],
        "planned_calendar_sha256": digest(sorted((station, day.isoformat()) for station, day in calendar)),
        "baseline": baseline, "candidate": candidate, "collection_lead_days": lead_days,
        "comparison": comparison, "aggregate_sensitivity": evaluate(pairs, len(calendar)),
        "station_sensitivity": {
            station: evaluate([row for row in pairs if row.station == station],
                              sum(code == station for code, _ in calendar))
            for station in sorted(planned_dates)
        },
        "multiplicity": "unadjusted_exploratory_no_confirmatory_selection",
        "scientific_approval": False, "promotion_allowed": False,
    }
