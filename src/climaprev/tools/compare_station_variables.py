"""Diagnostic station comparisons for gust and daily temperature extrema; no fitting."""

import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta, timezone
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import DatePeriod
from climaprev.domain.verification import numerical_pairs
from climaprev.tools.compare_station import _distance, append_boundary
from climaprev.tools.historical_experiment import canonical_json, load_snapshot
from climaprev.tools.inmet_observations import MAX_BYTES, import_station

FIELDS = {
    "gust_kmh": ("wind_gusts_10m", "km/h", "preceding_hour_maximum", "maximum"),
    "temperature_max_c": ("temperature_2m", "°C", "instantaneous_samples", "maximum"),
    "temperature_min_c": ("temperature_2m", "°C", "instantaneous_samples", "minimum"),
}


def _series(payload: dict[str, Any], field: str, unit: str, suffix: str) -> dict[datetime, Any]:
    key = field + suffix
    if payload["hourly_units"].get(key) != unit:
        raise ValueError(f"unsupported or missing units: {key}")
    offset = payload["utc_offset_seconds"]
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise TypeError("UTC offset must be integer seconds")
    fixed_zone = timezone(timedelta(seconds=offset))
    values = {}
    for raw, value in zip(payload["hourly"]["time"], payload["hourly"][key], strict=True):
        if not isinstance(raw, str):
            raise TypeError("comparison requires ISO timestamps")
        stamp = datetime.fromisoformat(raw)
        if stamp.minute or stamp.second or stamp.microsecond:
            raise ValueError("model samples must be aligned to UTC hours")
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=fixed_zone)
        stamp = stamp.astimezone(UTC)
        if stamp.minute or stamp in values:
            raise ValueError("duplicate or unaligned model instant")
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("model values must be finite numbers or null")
            if field == "wind_gusts_10m" and value < 0:
                raise ValueError("model gust must not be negative")
        values[stamp] = value
    return values


def compare_variables(dataset: dict[str, Any], raw: bytes, *, expected_station: str) -> dict[str, Any]:
    config = dataset["configuration"]
    lead = config["lead_days"]
    if isinstance(lead, bool) or not isinstance(lead, int) or not 1 <= lead <= 7:
        raise ValueError("lead_days must be an integer between 1 and 7")
    if config.get("forecast_model", "gfs_global") != "gfs_global":
        raise ValueError("gust comparison currently supports gfs_global forecast only")
    if config.get("observed_model", "era5") != "era5":
        raise ValueError("gust comparison currently supports era5 reference only")
    period = DatePeriod(date.fromisoformat(config["start"]), date.fromisoformat(config["end"]))
    zone = ZoneInfo(config["timezone"])
    station = import_station(raw, expected_station=expected_station, period=period,
                             timezone=config["timezone"])
    series = {}
    for name in ("forecast", "observed"):
        payload = dataset[name]
        if payload.get("timezone") != config["timezone"]:
            raise ValueError("model timezone differs from configuration")
        suffix = f"_previous_day{config['lead_days']}" if name == "forecast" else ""
        series[name] = {field: _series(payload, spec[0], spec[1], suffix)
                        for field, spec in FIELDS.items()}
    variables = {}
    for field, (_, unit, semantics, aggregation) in FIELDS.items():
        cases, excluded = [], []
        for day in station["days"]:
            when = date.fromisoformat(day["date"])
            start = datetime.combine(when, time.min, zone).astimezone(UTC)
            end = datetime.combine(when + timedelta(days=1), time.min, zone).astimezone(UTC)
            values = {"station": day["fields"][field]["value"]}
            missing = {"station": day["fields"][field]["missing_endpoints_utc"]}
            for name in series:
                # GFS gust is a preceding-hour maximum; ERA5 gust and temperatures
                # are instantaneous according to each provider's variable table.
                interval = field == "gust_kmh" and name == "forecast"
                cursor = start + timedelta(hours=1) if interval else start
                expected = []
                while (cursor <= end if interval else cursor < end):
                    expected.append(cursor)
                    cursor += timedelta(hours=1)
                samples = series[name][field]
                absent = [stamp for stamp in expected if samples.get(stamp) is None]
                missing[name] = [stamp.isoformat() for stamp in absent]
                valid = [samples[stamp] for stamp in expected if samples.get(stamp) is not None]
                values[name] = None if absent else round(
                    min(valid) if aggregation == "minimum" else max(valid), 6)
            if any(value is None for value in values.values()):
                excluded.append({"date": day["date"], "missing_instants_utc": missing})
            else:
                cases.append({"date": day["date"], "expected_hours": len(expected), **values})
        variables[field] = {
            "unit": unit, "forecast_semantics": semantics,
            "source_semantics": {
                "forecast": semantics, "observed": "instantaneous_samples",
                "station": "preceding_hour_extrema"},
            "station_semantics": "preceding_hour_extrema",
            "comparable_as_identical_measurement": False,
            "paired_days": len(cases), "cases": cases, "excluded_days": excluded,
            "metrics": {name: asdict(numerical_pairs([(row["station"], row[name]) for row in cases]))
                        for name in ("forecast", "observed")},
        }
    return {
        "schema": "climaprev-station-variables-comparison-v1",
        "convention": "civil-day-interval-extrema-and-instantaneous-samples-v1",
        "configuration": config, "station": station["station"],
        "station_source_sha256": station["source_sha256"],
        "station_importer_sha256": station["importer_sha256"],
        "snapshot_dataset_sha256": hashlib.sha256(canonical_json(dataset).encode()).hexdigest(),
        "comparison_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "station_to_grid_distance_km": {
            name: _distance(station["station"]["latitude"], station["station"]["longitude"],
                            dataset[name]["latitude"], dataset[name]["longitude"])
            for name in ("forecast", "observed")},
        "variables": variables, "decision": "diagnostic_only_not_approved",
        "calibration_ready": False,
        "semantic_sources": {
            "forecast": "https://open-meteo.com/en/docs/gfs-api",
            "observed": "https://open-meteo.com/en/docs/historical-weather-api",
            "station": "https://portal.inmet.gov.br/glossario/nublado"},
        "limitations": [
            "Temperature sample extrema differ from observed continuous preceding-hour extrema.",
            "Temperature discrepancies mix sampling, spatial representativeness and forecast error.",
            "ERA5 instantaneous gust samples differ from GFS and station preceding-hour maxima.",
            "Authenticity, sensor quality and spatial representativeness require review.",
            "No fitted coefficients, risk thresholds, promotion or calibration approval are produced.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--boundary-input", type=Path)
    parser.add_argument("--station-csv", type=Path, required=True)
    parser.add_argument("--station", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.station_csv.stat().st_size > MAX_BYTES:
            raise ValueError("station CSV exceeds 32 MiB")
        dataset = load_snapshot(args.input)
        if args.boundary_input:
            dataset = append_boundary(dataset, load_snapshot(args.boundary_input))
        result = compare_variables(dataset, args.station_csv.read_bytes(), expected_station=args.station)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as error:
        parser.exit(2, f"station variable comparison failed: {error}\n")


if __name__ == "__main__":
    main()
