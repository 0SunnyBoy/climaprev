"""Freeze paired spatial requests without collecting data or fitting a policy."""

import hashlib
from typing import Any

from climaprev.tools.collect_campaign import campaign_jobs
from climaprev.tools.historical_experiment import digest
from climaprev.tools.inmet_observations import parse_station_csv
from climaprev.tools.validate_historical import _forecast_params, _observed_params

STATIONS = {"belem": "A201", "brasilia": "A001", "porto-alegre": "A801"}


def spatial_plan(
    protocol: dict[str, Any], sources: dict[str, tuple[bytes, str]],
) -> dict[str, Any]:
    """Verify annual source identity and hold elevation/grid rules constant per pair."""
    jobs = campaign_jobs(protocol)
    collection = protocol["initial_adjustment_collection"]
    if (collection["year"] != 2024 or collection["months"] != [1, 4, 7, 10]
            or collection["lead_days"] != [1, 3, 7]
            or collection["days_in_each_month"] != {
                "first": 1, "last": 28, "boundary_day": 29}):
        raise ValueError("spatial experiment requires the fixed 2024 preparation windows")
    if set(sources) != set(STATIONS):
        raise ValueError("exactly three verified station sources are required")
    stations = {}
    for city, code in STATIONS.items():
        raw, expected = sources[city]
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("station CSV checksum mismatch")
        metadata, hours = parse_station_csv(raw, expected_station=code)
        if not hours or any(hour.endpoint.year != 2024 for hour in hours):
            raise ValueError("station source must contain only annual 2024 observations")
        stations[city] = {key: metadata[key] for key in (
            "code", "name", "latitude", "longitude", "altitude")}
        stations[city]["csv_sha256"] = expected
    requests = []
    for name, config in jobs:
        city = name.split("-2024-", 1)[0]
        station = stations[city]
        for arm in ("municipal-control", "station"):
            providers = {}
            for provider, params in (
                ("forecast", _forecast_params(config)), ("observed", _observed_params(config)),
            ):
                params.update(elevation=station["altitude"], cell_selection="nearest")
                if arm == "station":
                    params.update(latitude=station["latitude"], longitude=station["longitude"])
                providers[provider] = params
            requests.append({"pair": name, "arm": arm, "parameters": providers})
    return {
        "schema": "climaprev-spatial-plan-v1", "protocol_sha256": digest(protocol),
        "stations": stations, "requests": requests, "snapshot_count": len(requests),
        "maximum_http_calls_without_retries": len(requests) * 2,
        "evaluation_last_day": 28, "boundary_day": 29,
        "comparison": "fresh paired arms; old municipal snapshots are historical references only",
        "eligibility": "intersection of original eligible dates and both fresh arms per variable",
        "uncertainty": "retain original temporal bootstrap restrictions; no independence by horizon",
        "provider_preflight_required": True, "collection_executed": False,
        "candidate_fitting_executed": False, "calibration_fitting_executed": False,
        "stop_before_stage": 6,
    }
