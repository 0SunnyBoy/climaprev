"""Exploratory rain pairing with an explicitly identified INMET station and day."""

import hashlib
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_normalization import (
    Measurement,
    complete_rain_total,
    validate_measurements,
)
from climaprev.tools.experimental_observations import _measurement
from climaprev.tools.historical_experiment import digest
from climaprev.tools.inmet_observations import StationHour, parse_station_csv


def station_measurements(hours: list[StationHour]) -> list[Measurement]:
    if len({hour.endpoint for hour in hours}) != len(hours):
        raise ValueError("duplicate station endpoints")
    result = []
    for hour in hours:
        if hour.endpoint.utcoffset() is None:
            raise ValueError("station endpoint must have an offset")
        value = hour.rain_mm
        if value is not None and (not isfinite(value) or value < 0):
            raise ValueError("invalid station rainfall")
        endpoint = hour.endpoint.astimezone(UTC)
        result.append(Measurement("precipitation_mm", endpoint - timedelta(hours=1), endpoint,
                                  value, "mm", "observed_previous_hour_sum"))
    return result


def pair_station_rain(
    measurements: list[Measurement], location: CanonicalLocation, raw_csv: bytes,
    station: str, period: DatePeriod, *, collected_at: datetime, model: str,
    run_at: datetime | None = None,
) -> dict[str, Any]:
    if period.days > 366 or collected_at.utcoffset() is None or not model.strip():
        raise ValueError("bounded period, model and aware collection timestamp required")
    if run_at is not None and (run_at.utcoffset() is None
                              or run_at.astimezone(UTC) > collected_at.astimezone(UTC)):
        raise ValueError("run needs an offset and cannot follow collection")
    metadata, hours = parse_station_csv(raw_csv, expected_station=station)
    if (abs(metadata["latitude"] - location.latitude) > 0.0001
            or abs(metadata["longitude"] - location.longitude) > 0.0001):
        raise ValueError("forecast must be at verified station coordinates")
    observed = station_measurements(hours)
    zone = ZoneInfo(location.timezone)
    rows = []
    for index in range(period.days):
        day: date = period.start + timedelta(days=index)
        start = datetime.combine(day, time.min, zone).astimezone(UTC)
        end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
        forecast_value = complete_rain_total(measurements, start, end)
        observed_value = complete_rain_total(observed, start, end)
        reasons = []
        if forecast_value is None:
            reasons.append("incomplete_forecast_interval")
        if observed_value is None:
            reasons.append("incomplete_observation_interval")
        rows.append({"date": day.isoformat(), "start_utc": start.isoformat(),
                     "end_utc": end.isoformat(), "forecast_mm": forecast_value,
                     "observed_mm": observed_value, "exclusions": reasons,
                     "eligible_exploratory": not reasons,
                     "collected_before_target": collected_at.astimezone(UTC) < start,
                     "collection_lead_days": (day - collected_at.astimezone(zone).date()).days,
                     "run_lead_hours": ((start - run_at.astimezone(UTC)).total_seconds() / 3600
                                        if run_at is not None else None)})
    return {"schema": "climaprev-station-rain-pairs-v2", "model": model,
            "collected_at": collected_at.astimezone(UTC).isoformat(),
            "run_at": run_at.astimezone(UTC).isoformat() if run_at else None,
            "location": asdict(location), "station": metadata, "rows": rows,
            "source_sha256": hashlib.sha256(raw_csv).hexdigest(),
            "forecast_samples_sha256": digest([asdict(item) for item in measurements]),
            "semantics": "civil_day_precipitation_not_disaster_impact",
            "scientific_approval": False,
            "limitation": "exploratory eligibility is not independence or confirmatory approval"}


def pair_baseline_rain(baseline: dict[str, Any], raw_csv: bytes, station: str) -> dict[str, Any]:
    """Pair the adapter's daily sum directly; never fabricate an hourly baseline."""
    if baseline.get("model_identity") != "unknown_auto_selection":
        raise ValueError("expected an archived automatic baseline")
    forecast = baseline["forecast"]
    period = DatePeriod(date.fromisoformat(str(forecast["period"]["start"])),
                        date.fromisoformat(str(forecast["period"]["end"])))
    result = pair_station_rain(
        [], CanonicalLocation(**forecast["location"]), raw_csv, station, period,
        collected_at=datetime.fromisoformat(str(forecast["fetched_at"])), model="operational-baseline",
    )
    values = {}
    for day in forecast["days"]:
        key = str(day["date"])
        if key in values:
            raise ValueError("duplicate baseline date")
        value = day["precipitation_sum_mm"]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not isfinite(value) or value < 0):
            raise ValueError("invalid baseline daily rainfall")
        values[key] = value
    for row in result["rows"]:
        value = values.get(row["date"])
        row["forecast_mm"] = value
        if value is not None:
            row["exclusions"].remove("incomplete_forecast_interval")
        if f"{row['date']}.precipitation.coverage" in forecast["missing_fields"]:
            row["exclusions"].append("baseline_hourly_rain_coverage")
        row["eligible_exploratory"] = not row["exclusions"]
    del result["forecast_samples_sha256"]
    result["baseline_sha256"] = digest(baseline)
    result["forecast_aggregation"] = "production_adapter_daily_sum_without_hourly_reconstruction"
    return result


def _daily_value(
    samples: list[Measurement], start: datetime, end: datetime, *, unit: str,
    semantics: str, aggregation: str,
) -> float | None:
    selected = sorted((m for m in samples if (m.end is None and start <= m.start < end
                       or m.end is not None and m.start < end and m.end > start)),
                      key=lambda m: m.start)
    validate_measurements(selected, unit=unit, semantics=semantics)
    cursor, values, weights = start, [], []
    for sample in selected:
        stop = sample.end or sample.start + timedelta(hours=1)
        if sample.start != cursor or stop > end or sample.value is None:
            return None
        values.append(sample.value)
        weights.append((stop - sample.start).total_seconds())
        cursor = stop
    if not values or cursor != end:
        return None
    if aggregation == "max":
        return max(values)
    if aggregation == "min":
        return min(values)
    if aggregation == "sum":
        return sum(values)
    if aggregation == "mean":
        return sum(value * weight for value, weight in zip(values, weights, strict=True))/sum(weights)
    raise ValueError("unsupported daily aggregation")


def pair_variable_days(
    forecast: list[Measurement], observations: dict[str, Any], location: CanonicalLocation,
    period: DatePeriod, *, variable: str, unit: str, aggregation: str,
    forecast_semantics: str, observed_semantics: str, model: str, collected_at: datetime,
    forecast_variable: str | None = None, equivalence_reference: str | None = None,
    run_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pair daily values while distinguishing instrument equivalence from support."""
    if (period.days > 366 or collected_at.utcoffset() is None or not model.strip()
            or aggregation not in {"min", "max", "sum", "mean"}):
        raise ValueError("bounded period, aware collection, model and aggregation required")
    station = observations["station"]
    for field, bound in (("latitude", 90), ("longitude", 180)):
        for value in (getattr(location, field), station[field]):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or abs(value) > bound):
                raise ValueError("invalid pairing coordinates")
        if abs(getattr(location, field) - station[field]) > 0.0001:
            raise ValueError("pairing point differs from station")
    predicted = [m for m in forecast if m.variable == (forecast_variable or variable)]
    observed = [_measurement(row) for row in observations["measurements"]
                if row["variable"] == variable]
    equivalent = (forecast_semantics.removeprefix("observed_")
                  == observed_semantics.removeprefix("observed_")) or bool(equivalence_reference)
    zone = ZoneInfo(location.timezone)
    rows = []
    for index in range(period.days):
        day = period.start + timedelta(days=index)
        start = datetime.combine(day, time.min, zone).astimezone(UTC)
        end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
        predicted_value = _daily_value(predicted, start, end, unit=unit,
                                       semantics=forecast_semantics, aggregation=aggregation)
        observed_value = _daily_value(observed, start, end, unit=unit,
                                      semantics=observed_semantics, aggregation=aggregation)
        reasons = []
        if predicted_value is None:
            reasons.append("incomplete_forecast_interval")
        if observed_value is None:
            reasons.append("incomplete_observation_interval")
        rows.append({"date": day.isoformat(), "start_utc": start.isoformat(),
                     "end_utc": end.isoformat(), "forecast": predicted_value,
                     "observed": observed_value, "exclusions": reasons,
                     "eligible_exploratory": not reasons,
                     "eligible_confirmatory": not reasons and equivalent and collected_at < start,
                     "comparable_as_identical_measurement": equivalent,
                     "diagnostic_reasons": [] if equivalent else ["measurement_semantics_not_equivalent"],
                     "collection_lead_days": (day - collected_at.astimezone(zone).date()).days})
    return {"schema": "climaprev-variable-pairs-v1", "model": model,
            "variable": variable, "unit": unit, "aggregation": aggregation,
            "forecast_semantics": forecast_semantics, "observed_semantics": observed_semantics,
            "station": station, "location": asdict(location), "rows": rows,
            "collected_at": collected_at.astimezone(UTC).isoformat(),
            "run_evidence": run_evidence,
            "source_sha256": observations["source_sha256"],
            "source_field": observations["source_fields"].get(variable),
            "forecast_samples_sha256": digest([asdict(m) for m in forecast]),
            "equivalence_reference": equivalence_reference, "scientific_approval": False}
