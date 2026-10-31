"""Collect immutable spatial pairs; no fitting, promotion or application writes."""

import asyncio
import math
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderRateLimited,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.config import Settings
from climaprev.domain.models import DatePeriod
from climaprev.infrastructure.http.client import AsyncJsonHttpClient
from climaprev.tools.historical_data import normalize_hourly
from climaprev.tools.historical_experiment import digest, load_snapshot, save_snapshot, snapshot


def validate_payload(payload: dict[str, Any], params: dict[str, Any], lead: int) -> None:
    """Require returned grid metadata, requested elevation and structurally valid hours."""
    for key, bound in (("latitude", 90), ("longitude", 180), ("elevation", None)):
        value = payload.get(key)
        if (isinstance(value, bool) or not isinstance(value, int | float)
                or not math.isfinite(value) or (bound is not None and abs(value) > bound)):
            raise ValueError(f"invalid returned {key}")
    if abs(payload["elevation"] - params["elevation"]) > 0.1:
        raise ValueError("provider did not preserve the requested elevation")
    if payload.get("timezone") != params["timezone"]:
        raise ValueError("provider timezone differs")
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict) or not hourly.get("time"):
        raise ValueError("provider hourly series is empty")
    for field in params["hourly"].split(","):
        if not isinstance(hourly.get(field), list) or len(hourly[field]) != len(hourly["time"]):
            raise ValueError("provider hourly fields are missing or misaligned")
    suffix = f"_previous_day{lead}" if lead else ""
    normalize_hourly(payload, DatePeriod(date.fromisoformat(params["start_date"]),
                                       date.fromisoformat(params["end_date"])), suffix=suffix)


async def collect_spatial(
    plan: dict[str, Any], expected_plan: dict[str, Any], directory: Path,
    *, settings: Settings | None = None, preflight_only: bool = False,
) -> dict[str, Any]:
    """Revalidate the frozen plan against verified sources before any network I/O.

    First pair is the preflight. Failure prevents expansion. Completed snapshots
    may be resumed only with identical provenance and requests. Calls are serial;
    retries/timeouts use the existing bounded HTTP client.
    """
    if plan != expected_plan or plan.get("schema") != "climaprev-spatial-plan-v1":
        raise ValueError("spatial plan differs from verified preparation sources")
    current = settings or Settings(environment="test")
    urls = {
        "forecast": f"{current.historical_forecast_base_url.rstrip('/')}/v1/forecast",
        "observed": f"{current.historical_weather_base_url.rstrip('/')}/v1/archive",
    }
    plan_hash = digest(plan)
    completed: dict[str, str] = {}
    failures = []
    directory.mkdir(parents=True, exist_ok=True)
    jobs = plan["requests"][:2] if preflight_only else plan["requests"]
    async with httpx.AsyncClient() as client:
        http = AsyncJsonHttpClient(client, current)
        for index, job in enumerate(jobs):
            name = f"{job['pair']}-{job['arm']}"
            params = job["parameters"]["forecast"]
            lead = int(job["pair"].rsplit("-d", 1)[1])
            configuration = {
                "latitude": params["latitude"], "longitude": params["longitude"],
                "start": params["start_date"], "end": params["end_date"],
                "lead_days": lead, "timezone": params["timezone"], "minimum_coverage": 1.0,
                "forecast_model": params["models"],
                "observed_model": job["parameters"]["observed"]["models"],
                "spatial_plan_sha256": plan_hash, "spatial_arm": job["arm"],
            }
            requests = {provider: {"url": url, "params": job["parameters"][provider]}
                        for provider, url in urls.items()}
            path = directory / f"{name}.inputs.json"
            try:
                if path.exists():
                    data = load_snapshot(path)
                    if data["configuration"] != configuration or data["requests"] != requests:
                        raise ValueError("cached spatial snapshot provenance differs")
                else:
                    payloads = {}
                    for provider, request in requests.items():
                        payloads[provider] = await http.get_json(request["url"], request["params"])
                        validate_payload(payloads[provider], request["params"],
                                         lead if provider == "forecast" else 0)
                    data = snapshot(configuration, payloads["forecast"], payloads["observed"],
                                    dict[str, object](requests))
                    save_snapshot(path, data)
                for provider in urls:
                    validate_payload(data[provider], job["parameters"][provider],
                                     lead if provider == "forecast" else 0)
                completed[name] = digest(data)
                print(f"collected {name}", flush=True)
            except (ValueError, OSError, KeyError, TypeError, WeatherDataInvalid,
                    ProviderPermanentError, ProviderRateLimited, ProviderTransientError,
                    httpx.HTTPError) as error:
                failures.append({"job": name, "error": type(error).__name__, "detail": str(error)})
                print(f"failed {name}: {type(error).__name__}", flush=True)
                if index < 2:
                    break
            if index < len(jobs) - 1:
                await asyncio.sleep(1)
    return {
        "schema": "climaprev-spatial-collection-v1", "plan_sha256": plan_hash,
        "requested_snapshots": len(jobs), "parent_snapshots": completed, "failures": failures,
        "preflight_passed": all(
            f"{job['pair']}-{job['arm']}" in completed for job in plan["requests"][:2]),
        "complete": len(completed) == len(plan["requests"]) and not failures,
        "cell_selection_limitation": "nearest is submitted explicitly; provider does not echo the rule",
        "candidate_fitting_executed": False, "calibration_fitting_executed": False,
        "stop_before_stage": 6,
    }
