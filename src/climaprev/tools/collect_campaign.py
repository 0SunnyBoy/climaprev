"""Collect the authorized preparation campaign; never fit candidates or open holdouts."""

import argparse
import asyncio
import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.tools.compare_rain_horizons import compare_horizons
from climaprev.tools.historical_experiment import digest, load_snapshot
from climaprev.tools.validate_historical import HistoricalValidationConfig, collect_and_validate

LOCATIONS = {
    "belem": (-1.4558, -48.5044, "America/Belem"),
    "brasilia": (-15.7939, -47.8828, "America/Sao_Paulo"),
    "porto-alegre": (-30.0346, -51.2177, "America/Sao_Paulo"),
}


def campaign_jobs(protocol: dict[str, Any]) -> list[tuple[str, HistoricalValidationConfig]]:
    authorization = protocol["authorization"]
    if (4 not in authorization["allowed_stages"]
            or authorization["candidate_fitting_allowed"]
            or authorization["calibration_fitting_allowed"]):
        raise ValueError("campaign requires preparation-only authorization")
    collection = protocol["initial_adjustment_collection"]
    if collection["locations"] != ["Belém", "Brasília", "Porto Alegre"]:
        raise ValueError("unsupported campaign locations; revise explicit coordinate map")
    split = protocol["splits"]["adjustment"]
    earliest, latest = date.fromisoformat(split["start"]), date.fromisoformat(split["end"])
    jobs = []
    for name, (latitude, longitude, zone) in LOCATIONS.items():
        for month in collection["months"]:
            days = collection["days_in_each_month"]
            start = date(collection["year"], month, days["first"])
            last = date(collection["year"], month, days["last"])
            end = date(collection["year"], month, days["boundary_day"])
            if end != last + timedelta(days=1) or not earliest <= start <= last < end <= latest:
                raise ValueError("campaign must stay inside adjustment, including boundary")
            for lead in collection["lead_days"]:
                config = HistoricalValidationConfig(latitude, longitude, start, end, lead, zone)
                jobs.append((f"{name}-{start:%Y-%m}-d{lead}", config))
    if len({name for name, _ in jobs}) != len(jobs):
        raise ValueError("duplicate campaign job")
    return jobs


def diagnostic_window(dataset: dict[str, Any]) -> dict[str, Any]:
    """Use last collected day only as boundary, without rewriting the parent."""
    result = deepcopy(dataset)
    result["campaign_parent_sha256"] = digest(dataset)
    end = date.fromisoformat(result["configuration"]["end"]) - timedelta(days=1)
    result["configuration"]["end"] = end.isoformat()
    return result


async def run_campaign(protocol: dict[str, Any], directory: Path) -> dict[str, Any]:
    jobs = campaign_jobs(protocol)
    directory.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(2)
    collected: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, str]] = []

    async def collect(name: str, config: HistoricalValidationConfig) -> None:
        async with semaphore:
            path = directory / f"{name}.inputs.json"
            try:
                if path.exists():
                    inputs = load_snapshot(path)
                    expected = {
                        "latitude": config.latitude, "longitude": config.longitude,
                        "start": config.start.isoformat(), "end": config.end.isoformat(),
                        "lead_days": config.lead_days, "timezone": config.timezone,
                        "minimum_coverage": config.minimum_coverage,
                        "forecast_model": config.forecast_model, "observed_model": config.observed_model,
                    }
                    if inputs["configuration"] != expected:
                        raise ValueError("cached campaign configuration differs")
                else:
                    result = await collect_and_validate(config, save_input=path)
                    inputs = result.inputs
                collected[name] = inputs
                print(f"collected {name}", flush=True)
            except (ValueError, OSError, KeyError, TypeError, WeatherDataInvalid,
                    ProviderPermanentError, ProviderTransientError, httpx.HTTPError) as error:
                failures.append({"job": name, "error": type(error).__name__, "detail": str(error)})
                print(f"failed {name}: {type(error).__name__}", flush=True)

    await asyncio.gather(*(collect(name, config) for name, config in jobs))
    groups: dict[str, list[dict[str, Any]]] = {}
    for name, data in sorted(collected.items()):
        groups.setdefault(name.rsplit("-d", 1)[0], []).append(diagnostic_window(data))
    comparisons = {}
    for name, datasets in groups.items():
        if len(datasets) != len(protocol["initial_adjustment_collection"]["lead_days"]):
            failures.append({"job": name, "error": "IncompleteGroup", "detail": "missing horizon"})
            continue
        try:
            comparisons[name] = compare_horizons(datasets)
        except ValueError as error:
            failures.append({"job": name, "error": type(error).__name__, "detail": str(error)})
    return {
        "schema": "climaprev-preparation-campaign-v1", "protocol_sha256": digest(protocol),
        "locations": {name: {"latitude": lat, "longitude": lon, "timezone": zone,
                              "meaning": "municipal experiment point, not verified station location"}
                      for name, (lat, lon, zone) in LOCATIONS.items()},
        "requested_jobs": len(jobs), "collected_jobs": len(collected), "failures": failures,
        "parent_snapshots": {name: digest(data) for name, data in sorted(collected.items())},
        "comparisons": comparisons,
        "unique_location_dates": sum(report["unique_paired_dates"] for report in comparisons.values()),
        "stop_before_stage": 6, "candidate_fitting_executed": False,
        "calibration_fitting_executed": False, "holdout_accessed_by_campaign": False,
        "decision": "preparation_only_not_scientifically_approved",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.exit(2, "campaign output already exists\n")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    report = asyncio.run(run_campaign(protocol, args.directory))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
