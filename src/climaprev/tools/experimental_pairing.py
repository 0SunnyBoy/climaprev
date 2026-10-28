"""Exploratory rain pairing with an explicitly identified INMET station and day."""

import hashlib
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_equivalence import check_equivalence
from climaprev.tools.experimental_normalization import Measurement, complete_rain_total
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
