"""Compare civil-interval rainfall across horizons on identical complete ERA5 targets."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from climaprev.domain.verification import numerical_pairs
from climaprev.tools.audit_historical import audit_snapshot
from climaprev.tools.compare_station import append_boundary
from climaprev.tools.historical_experiment import canonical_json, load_snapshot


def compare_horizons(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    if not datasets:
        raise ValueError("at least one horizon is required")
    first = datasets[0]["configuration"]
    indexed: dict[int, dict[str, Any]] = {}
    provenance = {}
    for dataset in datasets:
        config = dataset["configuration"]
        for key in ("start", "end", "latitude", "longitude", "timezone", "forecast_model",
                    "observed_model", "minimum_coverage"):
            if config.get(key) != first.get(key):
                raise ValueError(f"horizon configuration differs: {key}")
        lead = config["lead_days"]
        if lead in indexed:
            raise ValueError("duplicate horizon")
        for key in ("latitude", "longitude", "timezone", "utc_offset_seconds", "hourly_units"):
            if dataset["observed"].get(key) != datasets[0]["observed"].get(key):
                raise ValueError(f"reference metadata differs: {key}")
        audit = audit_snapshot(dataset)
        indexed[lead] = {
            name: {row["date"]: row for row in audit["sources"][name]["days"]}
            for name in ("forecast", "observed")}
        provenance[str(lead)] = {
            "derived_dataset_sha256": hashlib.sha256(canonical_json(dataset).encode()).hexdigest(),
            "boundary_parents": dataset.get("boundary_parent_sha256"),
        }
    cases, excluded = [], []
    leads = sorted(indexed)
    for day in indexed[leads[0]]["observed"]:
        targets = [indexed[lead]["observed"][day]["civil_preceding_hour_total_mm"]
                   for lead in leads]
        predictions = {str(lead): indexed[lead]["forecast"][day]["civil_preceding_hour_total_mm"]
                       for lead in leads}
        available = [value for value in targets if value is not None]
        if available and any(abs(value - available[0]) > 0.000001 for value in available):
            raise ValueError(f"conflicting observed target for {day}")
        missing = [f"reference_D{lead}" for lead, value in zip(leads, targets, strict=True)
                   if value is None]
        missing += [f"forecast_D{lead}" for lead, value in predictions.items() if value is None]
        if missing:
            excluded.append({"date": day, "incomplete_sources": missing})
        else:
            cases.append({"date": day, "observed_mm": targets[0], "predicted_mm": predictions})
    return {
        "schema": "climaprev-civil-rain-horizons-v1", "convention": "civil-day-preceding-hour-v1",
        "configuration": {key: value for key, value in first.items() if key != "lead_days"},
        "lead_days": leads, "unique_paired_dates": len(cases), "cases": cases,
        "excluded_dates": excluded, "provenance": provenance,
        "metrics": {str(lead): asdict(numerical_pairs([
            (row["observed_mm"], row["predicted_mm"][str(lead)]) for row in cases]))
                    for lead in leads},
        "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "decision": "diagnostic_only_not_approved",
        "limitations": ["ERA5 is reanalysis, not station truth or an impact label.",
                        "Horizons share dates and are not independent observations.",
                        "No calibration, risk label or promotion is produced."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--boundary-input", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.input) != len(args.boundary_input):
        parser.exit(2, "each input requires one boundary input in the same order\n")
    datasets = [append_boundary(load_snapshot(original), load_snapshot(boundary))
                for original, boundary in zip(args.input, args.boundary_input, strict=True)]
    result = compare_horizons(datasets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
