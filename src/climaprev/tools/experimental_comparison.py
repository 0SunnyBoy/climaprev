"""Paired exploratory rainfall comparison; never fit, rank or promote candidates."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.verification import classify_pairs, numerical_pairs
from climaprev.tools.historical_experiment import canonical_json, digest, read_json

Case = tuple[str, float, float, str, str, str, int]


def _rain(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("rain must be a finite nonnegative number or null")
    return float(value)


def compare_rain_models(
    reports: Sequence[dict[str, Any]], baseline: str, *, require_run: bool = True,
    allow_retrospective: bool = False, include_cases: bool = False,
) -> dict[str, Any]:
    """Use identical station/interval/collection-day-lead pairs, exposing exclusions.

    Supplied run metadata is an eligibility input, not independently authenticated
    provider evidence. Collection-day lead is not a verified model-run horizon.
    """
    arms: dict[str, dict[Case, tuple[float, float]]] = defaultdict(dict)
    seen: dict[str, set[Case]] = defaultdict(set)
    excluded: dict[str, Counter[str]] = defaultdict(Counter)
    observations: dict[Case, tuple[float | None, str]] = {}
    threshold = RiskPolicy().daily_rain_high_mm
    for report in reports:
        if report.get("schema") != "climaprev-station-rain-pairs-v2":
            raise ValueError("comparison requires v2 pair reports with explicit timing")
        model = report["model"]
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model identity is required")
        station, location = report["station"], report["location"]
        for field, bound in (("latitude", 90), ("longitude", 180)):
            for value in (location[field], station[field]):
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not isfinite(value) or abs(value) > bound):
                    raise ValueError("invalid station coordinates")
            if abs(location[field] - station[field]) > 0.0001:
                raise ValueError("comparison point differs from the station")
        zone = ZoneInfo(location["timezone"])
        collected = datetime.fromisoformat(report["collected_at"])
        run = datetime.fromisoformat(report["run_at"]) if report["run_at"] else None
        if collected.utcoffset() is None or (run and (run.utcoffset() is None or run > collected)):
            raise ValueError("invalid collection/run chronology")
        for row in report["rows"]:
            start, end = datetime.fromisoformat(row["start_utc"]), datetime.fromisoformat(row["end_utc"])
            if start.utcoffset() is None or end.utcoffset() is None or start >= end:
                raise ValueError("invalid target interval")
            start, end = start.astimezone(UTC), end.astimezone(UTC)
            day = date.fromisoformat(row["date"])
            if (start != datetime.combine(day, time.min, zone).astimezone(UTC)
                    or end != datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)):
                raise ValueError("target interval differs from the declared local day")
            lead = row["collection_lead_days"]
            if isinstance(lead, bool) or not isinstance(lead, int):
                raise TypeError("collection-day lead must be an integer")
            if lead != (day - collected.astimezone(zone).date()).days:
                raise ValueError("collection-day lead differs from timestamps")
            key = (station["code"], location["latitude"], location["longitude"],
                   location["timezone"], start.isoformat(), end.isoformat(), lead)
            if key in seen[model]:
                raise ValueError("duplicate case within a model")
            seen[model].add(key)
            forecast, observed = _rain(row["forecast_mm"]), _rain(row["observed_mm"])
            observation = (observed, report["source_sha256"])
            if key in observations and observations[key] != observation:
                raise ValueError("models do not share the same observation and source")
            observations[key] = observation
            reasons = []
            if forecast is None:
                reasons.append("forecast_missing_or_incomplete")
            if observed is None:
                reasons.append("observation_missing_or_incomplete")
            if row["exclusions"] or row["eligible_exploratory"] is not True:
                reasons.append("upstream_quality_exclusion")
            if collected >= start and not allow_retrospective:
                reasons.append("collected_not_before_target")
            if require_run and (run is None or run >= start):
                reasons.append("run_unknown_or_not_before_target")
            excluded[model].update(reasons)
            if not reasons and forecast is not None and observed is not None:
                arms[model][key] = (observed, forecast)
        arms.setdefault(model, {})
    if baseline not in arms or len(arms) < 2:
        raise ValueError("baseline and at least one comparator are required")
    common = set.intersection(*(set(cases) for cases in arms.values()))
    universe: set[Case] = set().union(*seen.values())
    groups: dict[tuple[str, int], set[Case]] = defaultdict(set)
    for key in universe:
        groups[(key[0], key[-1])].add(key)

    def score(model: str, keys: set[Case]) -> dict[str, Any]:
        pairs = [arms[model][key] for key in sorted(keys)]
        numerical = asdict(numerical_pairs(pairs))
        detection = classify_pairs([("high" if obs >= threshold else "low",
                                     "high" if pred >= threshold else "low")
                                    for obs, pred in pairs]).detection[-1]
        return {"numerical": numerical, "high_rain_detection": asdict(detection)}

    scores = {model: score(model, common) for model in sorted(arms)}
    baseline_mae = scores[baseline]["numerical"]["mae"]
    comparisons = {}
    for model, result in scores.items():
        mae = result["numerical"]["mae"]
        comparisons[model] = {
            **result, "reported_cases": len(seen[model]), "eligible_cases": len(arms[model]),
            "excluded_unique_cases": len(seen[model]) - len(arms[model]),
            "absent_from_reported_union": len(universe - seen[model]),
            "excluded_reasons": dict(excluded[model]),
            "eligible_outside_common": len(set(arms[model]) - common),
            "relative_mae_gain": (1 - mae / baseline_mae if baseline_mae not in (None, 0)
                                  and mae is not None else None),
        }
    result = {
        "schema": "climaprev-exploratory-rain-comparison-v1", "baseline": baseline,
        "input_reports_sha256": [digest(report) for report in reports],
        "common_cases": len(common), "reported_union_cases": len(universe),
        "common_case_identity": digest(sorted(common)),
        "models": comparisons,
        "strata": [{"station": station, "collection_lead_days": lead,
                    "common_cases": len(keys & common), "reported_union_cases": len(keys),
                    "control": {
                        "reference_model": baseline,
                        "kind": ("operational_adapter" if baseline == "operational-baseline"
                                 else "experimental_reference"),
                        "status": ("absent" if not keys & seen[baseline]
                                   else "no_common_eligible_cases" if not keys & common
                                   else "exploratory_paired_cases"),
                        "public_v1_superiority_established": False,
                    },
                    "models": {m: {**score(m, keys & common),
                                   "reported_cases": len(keys & seen[m]),
                                   "eligible_cases": len(keys & set(arms[m])),
                                   "absent_from_reported_union": len(keys - seen[m])}
                               for m in sorted(arms)}}
                   for (station, lead), keys in sorted(groups.items())],
        "high_rain_threshold_mm": threshold, "threshold_basis": "diagnostic_reference_v1",
        "timing_mode": "retrospective_allowed" if allow_retrospective else "collected_before_target",
        "run_required": require_run, "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Exploratory point estimates; no confidence intervals or promotion test.",
                        "Collection-day labels do not prove equal model-run lead hours.",
                        "Reason counters overlap; they are not a count of unique excluded cases.",
                        "The reported union does not include targets omitted by every arm.",
                        "Pair counts are not counts of independent weather events.",
                        "A secondary model reference cannot replace an absent operational baseline.",
                        "Common-case scores must be read with per-model coverage and exclusions."],
    }
    if include_cases:
        result["paired_cases"] = [
            {"station": key[0], "start_utc": key[4], "end_utc": key[5],
             "collection_lead_days": key[6], "timezone": key[3],
             "observed_mm": arms[baseline][key][0],
             "forecasts_mm": {model: arms[model][key][1] for model in sorted(arms)}}
            for key in sorted(common)
        ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-retrospective", action="store_true")
    parser.add_argument("--allow-unknown-run", action="store_true")
    args = parser.parse_args()
    try:
        result = compare_rain_models([read_json(path) for path in args.input], args.baseline,
                                     require_run=not args.allow_unknown_run,
                                     allow_retrospective=args.allow_retrospective)
        encoded = canonical_json(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded + "\n")
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        parser.exit(2, f"experimental comparison failed: {error}\n")


if __name__ == "__main__":
    main()
