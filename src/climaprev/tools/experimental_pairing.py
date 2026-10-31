"""Exploratory rain pairing with an explicitly identified INMET station and day."""

import hashlib
import sqlite3
from collections.abc import Mapping
from contextlib import closing
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_archive import load_forecast_capture
from climaprev.tools.experimental_campaign import validate_target_calendar
from climaprev.tools.experimental_collection import describe_run
from climaprev.tools.experimental_equivalence import check_equivalence
from climaprev.tools.experimental_normalization import (
    Measurement,
    _number,
    complete_rain_total,
    met_norway_measurements,
    open_meteo_measurements,
    validate_measurements,
)
from climaprev.tools.experimental_observations import (
    _EXTRA_FIELDS,
    _measurement,
    parse_observations,
)
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
    rain_samples = [m for m in measurements if m.variable == "precipitation_mm"]
    if any(m.start.utcoffset() is None or (m.end and m.end.utcoffset() is None)
           for m in rain_samples):
        raise ValueError("forecast measurements require aware timestamps")
    zone = ZoneInfo(location.timezone)
    rows = []
    for index in range(period.days):
        day: date = period.start + timedelta(days=index)
        start = datetime.combine(day, time.min, zone).astimezone(UTC)
        end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
        forecast_value = complete_rain_total(measurements, start, end)
        observed_value = complete_rain_total(observed, start, end)
        contract_exclusions = set()
        for sample in rain_samples:
            if sample.start >= end or (sample.end is not None and sample.end <= start):
                continue
            if sample.end is None:
                contract_exclusions.add("forecast_interval_missing")
                continue
            observation = Measurement(
                "precipitation_mm", sample.start, sample.end,
                complete_rain_total(observed, sample.start, sample.end),
                "mm", "observed_interval_sum",
            )
            check = check_equivalence("rain_accumulation", sample, observation)
            # Observation gaps are disclosed by the daily observation coverage.
            # Here reject incompatible forecast metadata, not observation outages.
            contract_exclusions.update(reason for reason in check.exclusions
                                       if reason.startswith("forecast_"))
        if contract_exclusions:
            forecast_value = None
        reasons = []
        if forecast_value is None:
            reasons.append("incomplete_forecast_interval")
        if observed_value is None:
            reasons.append("incomplete_observation_interval")
        if contract_exclusions:
            reasons.append("incompatible_measurement_contract")
        rows.append({"date": day.isoformat(), "start_utc": start.isoformat(),
                     "end_utc": end.isoformat(), "forecast_mm": forecast_value,
                     "observed_mm": observed_value, "exclusions": reasons,
                     "measurement_contract_exclusions": sorted(contract_exclusions),
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
    if aggregation == "max" and any(sample.variable == "precipitation_mm"
            and (sample.end is None or sample.end - sample.start != timedelta(hours=1))
            for sample in selected):
        return None  # A six-hour amount cannot establish an hourly rain maximum.
    cursor, values, weights = start, [], []
    for sample in selected:
        stop = sample.end or sample.start + timedelta(hours=1)
        if semantics == "observed_previous_10_minute_mean":
            complete = (sample.end is not None and sample.end == cursor + timedelta(hours=1)
                        and sample.start == sample.end - timedelta(minutes=10))
        else:
            complete = sample.start == cursor
        if not complete or stop > end or sample.value is None:
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


def pair_capture(
    path: Path, raw_csv: bytes, location: CanonicalLocation, period: DatePeriod, *,
    station: str, model: str, contract: dict[str, Any], equivalence_reference: str | None = None,
) -> dict[str, Any]:
    """Compose the existing archive, normalization and pairing contracts offline."""
    capture = load_forecast_capture(path, model=model, location=location)
    metadata, payload = capture["metadata"], capture["payload"]
    variable = contract["name"]
    observations = parse_observations(raw_csv, expected_station=station, variables=[variable])
    baseline = model == "operational-baseline"
    samples = ([] if baseline else met_norway_measurements(payload["response"])
               if metadata["provider"] == "met-norway"
               else open_meteo_measurements(payload["response"]))
    field = None
    if baseline:
        field = {
            ("precipitation_mm", "sum"): "precipitation_sum_mm",
            ("precipitation_mm", "max"): "precipitation_max_hourly_mm",
            ("temperature_c", "mean"): "temperature_mean_c",
            ("temperature_max_c", "max"): "temperature_max_c",
            ("temperature_min_c", "min"): "temperature_min_c",
            ("gust_kmh", "max"): "wind_gust_max_kmh",
            ("wind_kmh", "max"): "wind_max_kmh",
            ("humidity_pct", "mean"): "humidity_mean_pct",
        }.get((variable, contract["aggregation"]))
    semantics = f"production_daily_{field or 'unsupported'}" if baseline else contract["semantics"]
    collected = datetime.fromisoformat(metadata["collected_at"])
    report = pair_variable_days(
        samples, observations, location, period, variable=variable, unit=contract["unit"],
        aggregation=contract["aggregation"], forecast_semantics=semantics,
        observed_semantics=_EXTRA_FIELDS[variable][2], model=model, collected_at=collected,
        forecast_variable="temperature_c" if variable in {"temperature_max_c", "temperature_min_c"}
        else variable, equivalence_reference=equivalence_reference,
        run_evidence=describe_run(collected, requested_run=datetime.fromisoformat(metadata["run_at"])
                                  if metadata["run_at"] else None),
    )
    report["capture_sha256"] = path.stem
    if baseline:
        forecast = payload["forecast"]
        days = {}
        for day in forecast["days"]:
            key = str(day["date"])
            if key in days:
                raise ValueError("duplicate baseline target date")
            days[key] = day
        for row in report["rows"]:
            day = days.get(row["date"])
            value = _number(day.get(field), variable) if day is not None and field else None
            row["forecast"] = value
            if value is not None:
                row["exclusions"].remove("incomplete_forecast_interval")
            elif day is None:
                row["exclusions"].append("baseline_target_absent")
            elif field is None:
                row["exclusions"].append("baseline_aggregation_not_supported")
            if (variable == "precipitation_mm"
                    and f"{row['date']}.precipitation.coverage" in forecast["missing_fields"]):
                row["exclusions"].append("baseline_hourly_rain_coverage")
            row["eligible_exploratory"] = not row["exclusions"]
            row["eligible_confirmatory"] = (not row["exclusions"]
                and row["comparable_as_identical_measurement"]
                and collected < datetime.fromisoformat(row["start_utc"]))
        del report["forecast_samples_sha256"]
        report["baseline_sha256"] = digest(payload)
        report["forecast_aggregation"] = "production_adapter_daily_value_without_hourly_reconstruction"
    return report


def pair_calendar_captures(
    calendar: dict[str, Any], ledger: Path, observation_files: Mapping[str, Path],
) -> list[dict[str, Any]]:
    """Prepare only the frozen targets, using persisted captures after a restart too."""
    data = validate_target_calendar(calendar)
    protocol = data["protocol"]["protocol"]
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        paths = {row[0]: Path(row[1]) for row in db.execute(
            "SELECT job,artifact FROM captures WHERE status='completed' AND artifact IS NOT NULL"
        )}
    raw = {code: path.read_bytes() for code, path in observation_files.items()}
    reports = []
    for target in data["targets"]:
        if not target["active"] or target["job"] not in paths or target["station"] not in raw:
            continue
        station = next(item for item in protocol["stations"] if item["code"] == target["station"])
        contract = next(item for item in protocol["variables"] if item["name"] == target["variable"])
        location = CanonicalLocation(station["name"], station["latitude"], station["longitude"],
                                     station["timezone"], "explicit-station-registry")
        day = date.fromisoformat(target["date"])
        report = pair_capture(
            paths[target["job"]], raw[target["station"]], location, DatePeriod(day, day),
            station=target["station"], model=target["model"], contract=contract,
            equivalence_reference=protocol["criteria"].get("equivalence_references", {}).get(
                target["variable"]),
        )
        report["target_key"] = target["key"]
        report["collection_slot"] = target["slot"]
        report["collection_deadline"] = (datetime.fromisoformat(target["slot"]) + timedelta(
            minutes=protocol["slot_window_minutes"])).isoformat()
        report["protocol_sha256"] = data["protocol"]["sha256"]
        reports.append(report)
    return reports
