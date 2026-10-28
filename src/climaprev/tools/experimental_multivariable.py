"""Exploratory same-window pairing and planned-denominator variable comparison."""

import hashlib
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime, time, timedelta
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.domain.verification import numerical_pairs
from climaprev.tools.experimental_equivalence import check_equivalence
from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.experimental_observations import station_variable_measurements
from climaprev.tools.historical_experiment import digest

_TARGETS = {
    "temperature_instant": ("temperature_c", "°C", "instant", "observed_instant"),
    "humidity_instant": ("humidity_pct", "%", "instant", "observed_instant"),
    "gust_previous_hour_max": ("gust_kmh", "km/h", "previous_hour_max", "observed_previous_hour_max"),
    "temperature_previous_hour_max": ("temperature_c", "°C", "previous_hour_max",
                                      "observed_previous_hour_max"),
    "temperature_previous_hour_min": ("temperature_c", "°C", "previous_hour_min",
                                      "observed_previous_hour_min"),
    "temperature_previous_hour_mean": ("temperature_c", "°C", "previous_hour_mean",
                                       "observed_previous_hour_mean"),
}
CaseWindow = tuple[str, str | None]


def _windows(period: DatePeriod, zone: ZoneInfo, target: str) -> list[tuple[datetime, datetime | None]]:
    if target not in _TARGETS or period.days > 366:
        raise ValueError("supported target and period up to 366 days required")
    start = datetime.combine(period.start, time.min, zone).astimezone(UTC)
    end = datetime.combine(period.end + timedelta(days=1), time.min, zone).astimezone(UTC)
    if start >= end or (end - start).total_seconds() % 3600:
        raise ValueError("target period needs complete hourly windows")
    result = []
    while start < end:
        result.append((start, None if _TARGETS[target][2] == "instant" else start + timedelta(hours=1)))
        start += timedelta(hours=1)
    return result


def _index(samples: Sequence[Measurement]) -> dict[tuple[Any, ...], Measurement]:
    result = {}
    for sample in samples:
        if sample.start.utcoffset() is None or (sample.end and sample.end.utcoffset() is None):
            raise ValueError("aware measurement timestamps required")
        key = (sample.variable, sample.start.astimezone(UTC),
               sample.end.astimezone(UTC) if sample.end else None, sample.semantics)
        if key in result:
            raise ValueError("duplicate measurement identity")
        result[key] = sample
    return result


def pair_station_variable(
    forecasts: Sequence[Measurement], location: CanonicalLocation, raw: bytes,
    station: str, period: DatePeriod, *, target: str, model: str,
    collected_at: datetime, run_at: datetime | None = None,
) -> dict[str, Any]:
    if not model.strip() or collected_at.utcoffset() is None:
        raise ValueError("model and aware collection required")
    if run_at is not None and (run_at.utcoffset() is None or run_at > collected_at):
        raise ValueError("invalid model-run chronology")
    zone = ZoneInfo(location.timezone)
    windows = _windows(period, zone, target)
    metadata, observations = station_variable_measurements(raw, station=station)
    if any(abs(metadata[field] - getattr(location, field)) > 0.0001
           for field in ("latitude", "longitude")):
        raise ValueError("forecast point differs from source-version station coordinates")
    predicted, observed = _index(forecasts), _index(observations)
    variable, unit, forecast_semantics, observation_semantics = _TARGETS[target]
    rows = []
    for start, end in windows:
        forecast = predicted.get((variable, start, end, forecast_semantics),
                                 Measurement(variable, start, end, None, unit, forecast_semantics))
        observation = observed.get((variable, start, end, observation_semantics),
                                   Measurement(variable, start, end, None, unit, observation_semantics))
        check = check_equivalence(target, forecast, observation)
        day = start.astimezone(zone).date()
        day_start = datetime.combine(day, time.min, zone).astimezone(UTC)
        reasons = list(check.exclusions)
        if target in {"temperature_instant", "humidity_instant"}:
            reasons.append("observation_semantics_not_equivalent")
        if collected_at.astimezone(UTC) >= day_start:
            reasons.append("collected_not_before_target_day")
        rows.append({"start_utc": start.isoformat(), "end_utc": end.isoformat() if end else None,
                     "forecast_value": forecast.value, "observed_value": observation.value,
                     "exclusions": reasons, "eligible_exploratory": not reasons})
    return {
        "schema": "climaprev-station-variable-pairs-v1", "target": target, "model": model,
        "unit": unit, "location": asdict(location), "station": metadata,
        "period": asdict(period), "planned_cases": len(windows), "rows": rows,
        "collected_at": collected_at.astimezone(UTC).isoformat(),
        "run_at": run_at.astimezone(UTC).isoformat() if run_at else None,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "forecast_samples_sha256": digest([asdict(sample) for sample in forecasts]),
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Declared CSV semantics do not certify instrument/height equivalence.",
                        "No interpolation or hourly-extreme inference from instantaneous temperatures.",
                        "Exploratory decision-time comparison, not equal model-run-age verification."],
    }


def compare_variable_reports(reports: Sequence[dict[str, Any]], baseline: str) -> dict[str, Any]:
    """Compare one station/target/period on identical eligible planned windows."""
    if len(reports) < 2:
        raise ValueError("at least two models required")
    first = reports[0]
    location = CanonicalLocation(**first["location"])
    period = DatePeriod(*(datetime.fromisoformat(str(first["period"][k])).date()
                          for k in ("start", "end")))
    zone = ZoneInfo(first["location"]["timezone"])
    if first["unit"] != _TARGETS[first["target"]][1]:
        raise ValueError("unit differs from target contract")
    if any(abs(first["station"][field] - getattr(location, field)) > 0.0001
           for field in ("latitude", "longitude")):
        raise ValueError("station point differs")
    expected = {(s.isoformat(), e.isoformat() if e else None)
                for s, e in _windows(period, zone, first["target"])}
    shared_fields = ("target", "unit", "location", "period", "source_sha256")
    arms: dict[str, dict[CaseWindow, tuple[float, float]]] = {}
    seen: dict[str, set[CaseWindow]] = {}
    reference_observations: dict[CaseWindow, float | None] = {}
    decision_slot = None
    for report in reports:
        if report.get("schema") != "climaprev-station-variable-pairs-v1":
            raise ValueError("unsupported variable-pair report")
        if (any(report[field] != first[field] for field in shared_fields)
                or report["station"] != first["station"]):
            raise ValueError("incompatible variable, station, period or observational source")
        model = report["model"]
        if not isinstance(model, str) or not model.strip() or model in arms:
            raise ValueError("missing or duplicate model")
        collected = datetime.fromisoformat(report["collected_at"])
        if collected.utcoffset() is None:
            raise ValueError("aware collection required")
        collected = collected.astimezone(UTC)
        slot = collected.replace(minute=30 * (collected.minute // 30), second=0, microsecond=0)
        if decision_slot is not None and slot != decision_slot:
            raise ValueError("different collection slots cannot be compared")
        decision_slot = slot
        run = datetime.fromisoformat(report["run_at"]) if report["run_at"] else None
        if run is not None and (run.utcoffset() is None or run > collected):
            raise ValueError("invalid model-run chronology")
        arms[model], seen[model] = {}, set()
        for row in report["rows"]:
            key = (row["start_utc"], row["end_utc"])
            if key not in expected or key in seen[model]:
                raise ValueError("unexpected or duplicate target window")
            seen[model].add(key)
            predicted, observation = row["forecast_value"], row["observed_value"]
            for value in (predicted, observation):
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                          or not isfinite(value)):
                    raise ValueError("finite values or null required")
                if value is not None and (first["unit"] == "%" and not 0 <= value <= 100
                                          or first["unit"] == "km/h" and value < 0):
                    raise ValueError("invalid physical measurement")
            if key in reference_observations and reference_observations[key] != observation:
                raise ValueError("different observations on the same case")
            reference_observations[key] = observation
            day = datetime.fromisoformat(key[0]).astimezone(zone).date()
            day_start = datetime.combine(day, time.min, zone).astimezone(UTC)
            if (not row["exclusions"] and row["eligible_exploratory"] is True
                    and collected < day_start and predicted is not None and observation is not None):
                arms[model][key] = (observation, predicted)
    if baseline not in arms:
        raise ValueError("baseline model missing")
    common = set.intersection(*(set(cases) for cases in arms.values()))
    return {
        "schema": "climaprev-variable-comparison-v1", "target": first["target"], "baseline": baseline,
        "planned_cases": len(expected), "common_cases": len(common),
        "common_coverage": len(common) / len(expected),
        "models": {model: {
            "numerical": asdict(numerical_pairs([cases[key] for key in sorted(common)])),
            "reported_cases": len(seen[model]), "eligible_cases": len(cases),
            "missing_from_plan": len(expected - seen[model]),
            "ineligible_reported_cases": len(seen[model]) - len(cases),
        } for model, cases in arms.items()},
        "input_reports_sha256": [digest(report) for report in reports],
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Point estimates only; no uncertainty or promotion.",
                        "Hourly pairs are not independent event counts.",
                        "No certified instrument equivalence or model-run-age comparability.",
                        "All-model omissions remain visible through the planned denominator."],
    }
