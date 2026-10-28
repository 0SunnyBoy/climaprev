"""Paired exploratory rainfall comparison; never fit, rank or promote candidates."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.verification import classify_pairs, numerical_pairs
from climaprev.tools.experimental_normalization import _number
from climaprev.tools.experimental_protocol import aware_timestamp
from climaprev.tools.historical_experiment import canonical_json, digest, read_json
from climaprev.tools.station_baseline import event_level

Case = tuple[str, float, float, str, str, str, int]


def _rain(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("rain must be a finite nonnegative number or null")
    return float(value)


def compare_rain_models(
    reports: Sequence[dict[str, Any]], baseline: str, *, require_run: bool = True,
    allow_retrospective: bool = False,
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
    return {
        "schema": "climaprev-exploratory-rain-comparison-v1", "baseline": baseline,
        "input_reports_sha256": [digest(report) for report in reports],
        "common_cases": len(common), "reported_union_cases": len(universe),
        "common_case_identity": digest(sorted(common)),
        "models": comparisons,
        "strata": [{"station": station, "collection_lead_days": lead,
                    "common_cases": len(keys & common), "reported_union_cases": len(keys),
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
                        "Common-case scores must be read with per-model coverage and exclusions."],
    }


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



@dataclass(frozen=True, slots=True, order=True)
class VariableCase:
    station: str
    latitude: float
    longitude: float
    timezone: str
    variable: str
    unit: str
    aggregation: str
    start_utc: str
    end_utc: str
    slot_utc: str


def _variable_event(variable: str, aggregation: str) -> str | None:
    return {("precipitation_mm", "sum"): "daily_rain", ("precipitation_mm", "max"): "hourly_rain",
            ("gust_kmh", "max"): "gust", ("temperature_max_c", "max"): "heat",
            ("temperature_min_c", "min"): "cold"}.get((variable, aggregation))


def _variable_score(
    pairs: list[tuple[float, float]], variable: str, aggregation: str,
) -> dict[str, Any]:
    event = _variable_event(variable, aggregation)
    classification = (asdict(classify_pairs([(event_level(event, obs), event_level(event, pred))
                                            for obs, pred in pairs])) if event else None)
    return {"numerical": asdict(numerical_pairs(pairs)), "classification": classification,
            "diagnostic_event": event}


def _case_day(case: VariableCase) -> date:
    return aware_timestamp(case.start_utc).astimezone(ZoneInfo(case.timezone)).date()


def _case_lead(case: VariableCase) -> int:
    return (_case_day(case) - aware_timestamp(case.slot_utc).astimezone(ZoneInfo(case.timezone)).date()).days


def compare_variable_models(
    reports: Sequence[dict[str, Any]], baseline: str, *, models: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Compare declared arms on identical units, observations, slots and target intervals."""
    declared = sorted({report["model"] for report in reports} if models is None else set(models))
    if baseline not in declared or len(declared) < 2 or any(not isinstance(m, str) or not m.strip()
                                                          for m in declared):
        raise ValueError("baseline and at least one declared comparator are required")
    axes: set[tuple[str, str, str]] = set()
    arms: dict[tuple[str, str, str], dict[str, dict[VariableCase, tuple[float, float]]]] = defaultdict(
        lambda: defaultdict(dict))
    seen: dict[tuple[str, str, str], dict[str, set[VariableCase]]] = defaultdict(
        lambda: defaultdict(set))
    excluded: dict[tuple[str, str, str], dict[str, dict[VariableCase, list[str]]]] = defaultdict(
        lambda: defaultdict(dict))
    reference: dict[VariableCase, tuple[float | None, str, str, str | None]] = {}
    units: dict[tuple[str, str], str] = {}
    for report in reports:
        if report.get("schema") != "climaprev-variable-pairs-v1" or report["model"] not in declared:
            raise ValueError("comparison requires versioned pairs for declared models")
        model, variable, unit, aggregation = (report[key] for key in ("model", "variable", "unit", "aggregation"))
        if not all(isinstance(value, str) and value.strip() for value in (variable, unit, aggregation)):
            raise ValueError("comparison requires explicit variable, unit and aggregation")
        canonical_units = {"precipitation_mm": "mm", "temperature_c": "°C",
                           "temperature_min_c": "°C", "temperature_max_c": "°C",
                           "wind_kmh": "km/h", "gust_kmh": "km/h", "humidity_pct": "%"}
        if variable not in canonical_units or unit != canonical_units[variable]:
            raise ValueError("variable unit is not the canonical measurement unit")
        if not all(isinstance(report.get(key), str) and report[key].strip()
                   for key in ("source_sha256", "observed_semantics")):
            raise ValueError("observed reference provenance is required")
        axis = (variable, unit, aggregation)
        axes.add(axis)
        if (variable, aggregation) in units and units[variable, aggregation] != unit:
            raise ValueError("variable unit contracts differ across models")
        units[variable, aggregation] = unit
        location, station = report["location"], report["station"]
        zone = ZoneInfo(location["timezone"])
        for field, bound in (("latitude", 90), ("longitude", 180)):
            for value in (location[field], station[field]):
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not isfinite(value) or abs(value) > bound):
                    raise ValueError("invalid comparison coordinates")
            if abs(location[field] - station[field]) > 0.0001:
                raise ValueError("comparison point differs from station")
        slot = aware_timestamp(report["collection_slot"])
        deadline = aware_timestamp(report["collection_deadline"])
        collected = aware_timestamp(report["collected_at"])
        if slot >= deadline:
            raise ValueError("collection slot must precede its deadline")
        for row in report["rows"]:
            start, end = aware_timestamp(row["start_utc"]), aware_timestamp(row["end_utc"])
            day = date.fromisoformat(row["date"])
            if (start != datetime.combine(day, time.min, zone).astimezone(UTC)
                    or end != datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)):
                raise ValueError("comparison target differs from its local day")
            key = VariableCase(station["code"], float(location["latitude"]), float(location["longitude"]),
                               location["timezone"], variable, unit, aggregation,
                               start.isoformat(), end.isoformat(), slot.isoformat())
            if key in seen[axis][model]:
                raise ValueError("duplicate comparison case within a model")
            seen[axis][model].add(key)
            observed, forecast = _number(row["observed"], variable), _number(row["forecast"], variable)
            identity = (observed, report["source_sha256"], report["observed_semantics"],
                        report.get("source_field"))
            if key in reference and reference[key] != identity:
                raise ValueError("models do not share the same observed reference")
            reference[key] = identity
            reasons = []
            if observed is None:
                reasons.append("observation_missing_or_incomplete")
            if forecast is None:
                reasons.append("forecast_missing_or_incomplete")
            if row.get("eligible_exploratory") is not True or row.get("exclusions") != []:
                reasons.append("upstream_quality_exclusion")
            if collected < slot or collected >= deadline:
                reasons.append("collection_outside_slot")
            if collected >= start:
                reasons.append("collected_not_before_target")
            excluded[axis][model][key] = reasons
            if not reasons and observed is not None and forecast is not None:
                arms[axis][model][key] = (observed, forecast)
    output = []
    for axis in sorted(axes):
        variable, unit, aggregation = axis
        for model in declared:
            arms[axis].setdefault(model, {})
            seen[axis].setdefault(model, set())
        common = set.intersection(*(set(arms[axis][m]) for m in declared))
        universe = set.union(*(seen[axis][m] for m in declared))

        def scores(
            keys: set[VariableCase], common: set[VariableCase] = common,
            axis: tuple[str, str, str] = axis, variable: str = variable,
            aggregation: str = aggregation,
        ) -> dict[str, Any]:
            shared = sorted(keys & common)
            result = {m: _variable_score([arms[axis][m][key] for key in shared], variable, aggregation)
                      for m in declared}
            baseline_mae = result[baseline]["numerical"]["mae"]
            for m in declared:
                mae = result[m]["numerical"]["mae"]
                reported = seen[axis][m] & keys
                eligible = set(arms[axis][m]) & keys
                result[m].update({"relative_mae_gain": 1 - mae / baseline_mae
                                  if baseline_mae not in (None, 0) and mae is not None else None,
                                  "reported_cases": len(reported), "eligible_cases": len(eligible),
                                  "excluded_unique_cases": len(reported - eligible),
                                  "excluded_reasons": dict(Counter(reason for key in reported
                                      for reason in excluded[axis][m].get(key, []))),
                                  "absent_from_reported_union": len(keys - seen[axis][m]),
                                  "eligible_outside_common": len(eligible - common)})
            return result

        strata: dict[tuple[str, int], set[VariableCase]] = defaultdict(set)
        for case in universe:
            strata[case.station, _case_lead(case)].add(case)
        output.append({"variable": variable, "unit": unit, "aggregation": aggregation,
                       "common_cases": len(common), "reported_union_cases": len(universe),
                       "models": scores(universe),
                       "paired_cases": [{"identity": asdict(case), "date": _case_day(case).isoformat(),
                                         "lead_days": _case_lead(case),
                                         "observed": arms[axis][baseline][case][0],
                                         "forecasts": {m: arms[axis][m][case][1] for m in declared}}
                                        for case in sorted(common)],
                       "strata": [{"station": station, "slot_lead_days": lead,
                                   "common_cases": len(keys & common),
                                   "reported_union_cases": len(keys), "models": scores(keys)}
                                  for (station, lead), keys in sorted(strata.items())]})
    return {"schema": "climaprev-variable-comparison-v1", "baseline": baseline, "models": declared,
            "groups": output, "input_reports_sha256": sorted(digest(report) for report in reports),
            "cohort": "collection_slot", "classification_policy": "reference-v1-diagnostic",
            "scientific_approval": False, "promotion_allowed": False,
            "limitations": ["Slot/collection timing is not verified model-run lead time.",
                            "The reported union omits targets absent from every arm; read calendar coverage.",
                            "Point estimates are diagnostic, not independent scientific acceptance."]}


if __name__ == "__main__":
    main()
