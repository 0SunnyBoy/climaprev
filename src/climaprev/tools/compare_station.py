"""Compare daily civil-interval rainfall against a local station CSV; no fitting."""

import argparse
import hashlib
import json
from copy import deepcopy
from dataclasses import asdict
from datetime import date, timedelta
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any

from climaprev.domain.models import DatePeriod
from climaprev.domain.verification import numerical_pairs
from climaprev.tools.audit_historical import audit_snapshot
from climaprev.tools.historical_experiment import canonical_json, load_snapshot
from climaprev.tools.inmet_observations import MAX_BYTES, import_station


def append_boundary(dataset: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    """Create a derived input with next-day rows; retain hashes of both parents."""
    config, other = dataset["configuration"], boundary["configuration"]
    next_day = (date.fromisoformat(config["end"]) + timedelta(days=1)).isoformat()
    if other["start"] != next_day or other["end"] != next_day:
        raise ValueError("boundary input must contain exactly the next day")
    for key in ("latitude", "longitude", "timezone", "lead_days", "forecast_model",
                "observed_model", "minimum_coverage"):
        if config.get(key) != other.get(key):
            raise ValueError(f"boundary configuration differs: {key}")
    for key in ("reference", "algorithms_sha256"):
        if dataset.get(key) != boundary.get(key):
            raise ValueError(f"boundary provenance differs: {key}")
    result = deepcopy(dataset)
    for name in ("forecast", "observed"):
        original, extra = result[name], boundary[name]
        for key in ("latitude", "longitude", "timezone", "utc_offset_seconds", "hourly_units"):
            if original.get(key) != extra.get(key):
                raise ValueError(f"boundary source metadata differs: {name}.{key}")
        if original["hourly"].keys() != extra["hourly"].keys():
            raise ValueError("boundary hourly fields differ")
        for field in original["hourly"]:
            original["hourly"][field].extend(extra["hourly"][field])
    result["boundary_parent_sha256"] = {
        label: hashlib.sha256(canonical_json(parent).encode()).hexdigest()
        for label, parent in (("original", dataset), ("boundary", boundary))}
    return result


def _distance(latitude: float, longitude: float, other_lat: float, other_lon: float) -> float:
    lat1, lat2 = radians(latitude), radians(other_lat)
    delta_lat, delta_lon = lat2 - lat1, radians(other_lon - longitude)
    chord = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return round(6371.0088 * 2 * asin(sqrt(min(1.0, chord))), 3)


def compare_station(dataset: dict[str, Any], raw: bytes, *, expected_station: str) -> dict[str, Any]:
    audit = audit_snapshot(dataset)
    config = dataset["configuration"]
    station = import_station(raw, expected_station=expected_station,
                             period=DatePeriod(date.fromisoformat(config["start"]),
                                               date.fromisoformat(config["end"])),
                             timezone=config["timezone"])
    source_days = {name: {row["date"]: row for row in audit["sources"][name]["days"]}
                   for name in ("forecast", "observed")}
    cases, excluded = [], []
    for day in station["days"]:
        when = day["date"]
        rain = day["fields"]["rain_mm"]
        values = {"station": rain["value"], **{
            name: source_days[name][when]["civil_preceding_hour_total_mm"]
            for name in source_days}}
        missing = [name for name, value in values.items() if value is None]
        if missing:
            excluded.append({"date": when, "incomplete_sources": missing,
                             "missing_endpoints_utc": {
                                 "station": rain["missing_endpoints_utc"], **{
                                     name: source_days[name][when]["missing_interval_endpoints"]
                                     for name in source_days}}})
        else:
            cases.append({"date": when, **values})
    distances = {}
    for name in ("forecast", "observed"):
        payload = dataset[name]
        distances[name] = _distance(station["station"]["latitude"],
                                    station["station"]["longitude"],
                                    payload["latitude"], payload["longitude"])
    return {
        "schema": "climaprev-station-rain-comparison-v1", "convention": station["convention"],
        "station": station["station"], "configuration": config,
        "station_source_sha256": station["source_sha256"],
        "station_importer_sha256": station["importer_sha256"],
        "comparison_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "interval_auditor_sha256": hashlib.sha256(
            Path(__file__).with_name("audit_historical.py").read_bytes()).hexdigest(),
        "snapshot_dataset_sha256": hashlib.sha256(canonical_json(dataset).encode()).hexdigest(),
        "station_to_grid_distance_km": distances,
        "unit": "mm", "paired_days": len(cases), "cases": cases, "excluded_days": excluded,
        "metrics": {name: asdict(numerical_pairs([(row["station"], row[name]) for row in cases]))
                    for name in ("forecast", "observed")},
        "decision": "diagnostic_only_not_approved",
        "limitations": ["Spatial distances are disclosed, not accepted automatically.",
                        "Temperature and gust comparisons are not implemented in this report.",
                        "No risk labels, fitted coefficients or promotion are produced.",
                        "Station authenticity, sensor quality and lead semantics require review."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--station-csv", type=Path, required=True)
    parser.add_argument("--boundary-input", type=Path)
    parser.add_argument("--station", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.station_csv.stat().st_size > MAX_BYTES:
        parser.exit(2, "station CSV exceeds 32 MiB\n")
    dataset = load_snapshot(args.input)
    if args.boundary_input:
        dataset = append_boundary(dataset, load_snapshot(args.boundary_input))
    result = compare_station(dataset, args.station_csv.read_bytes(),
                             expected_station=args.station)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
