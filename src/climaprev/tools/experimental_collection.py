"""Bounded one-shot experimental collection, independent of the public API."""

import argparse
import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation
from climaprev.infrastructure.http.client import AsyncJsonHttpClient
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
from climaprev.tools.experimental_normalization import (
    complete_rain_total,
    met_norway_measurements,
    open_meteo_measurements,
)
from climaprev.tools.historical_experiment import canonical_json

MODELS = ("gfs_global", "ecmwf_ifs025", "icon_global", "met-norway")
_FIELDS = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_gusts_10m"
_USER_AGENT = "ClimaPrev/0.1.0 https://github.com/0SunnyBoy/climaprev"


async def collect_once(
    client: httpx.AsyncClient, location: CanonicalLocation, model: str, directory: Path,
    *, run_at: datetime | None = None,
    before_send: Callable[[str], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    if model not in MODELS:
        raise ValueError("unsupported experimental model")
    is_met = model == "met-norway"
    if run_at is not None:
        if run_at.utcoffset() is None:
            raise ValueError("model run must have an offset")
        run_at = run_at.astimezone(UTC)
        if (is_met or run_at.hour not in {0, 6, 12, 18} or run_at.minute or run_at.second
                or run_at.microsecond or run_at > datetime.now(UTC)):
            raise ValueError("unsupported or future explicit run")
    endpoint = ("https://api.met.no/weatherapi/locationforecast/2.0/compact" if is_met
                else "https://api.open-meteo.com/v1/forecast")
    if run_at is not None:
        endpoint = "https://single-runs-api.open-meteo.com/v1/forecast"
    params: dict[str, str | float | int] = (
        {"lat": round(location.latitude, 4), "lon": round(location.longitude, 4)} if is_met
        else {"latitude": location.latitude, "longitude": location.longitude, "models": model,
              "hourly": _FIELDS, "forecast_days": 8 if model == "icon_global" else 9,
              "timezone": "GMT",
              "timeformat": "unixtime", "wind_speed_unit": "kmh"})
    settings = Settings(additional_retries=0, provider_max_response_bytes=4 * 1024 * 1024)
    if run_at is not None:
        params["run"] = run_at.strftime("%Y-%m-%dT%H:%M")
    http = AsyncJsonHttpClient(client, settings, before_send=before_send,
                              headers={"User-Agent": _USER_AGENT,
                                                       "Accept": "application/json"})
    payload = await http.get_json(endpoint, params)
    collected = datetime.now(UTC)
    samples = (met_norway_measurements(payload) if is_met else open_meteo_measurements(payload))
    if not samples:
        raise ValueError("provider returned no supported measurements")
    start = min(m.start for m in samples)
    end = max(m.end or m.start for m in samples)
    capture = ForecastCapture("met-norway" if is_met else "open-meteo",
                              "ecmwf-ifs-global-unspecified" if is_met else model,
                              endpoint, location, collected, start, end, run_at=run_at)
    # Updated_at and generationtime_ms are never inferred to be initialization times.
    archived = archive_forecast(directory, capture, {"request_parameters": params,
                                                     "response": payload})
    zone = ZoneInfo(location.timezone)
    today = collected.astimezone(zone).date()
    coverage = {}
    for lead in (1, 3, 7):
        day = today + timedelta(days=lead)
        day_start = datetime.combine(day, time.min, zone)
        day_end = datetime.combine(day + timedelta(days=1), time.min, zone)
        total = complete_rain_total(samples, day_start, day_end)
        coverage[f"D+{lead}"] = {
            "target_local_date": day.isoformat(),
            "rain_total_mm": total, "complete_rain_interval": total is not None,
        }
    return {"model": model, "archive": str(archived),
            "run_at": run_at.isoformat() if run_at else None,
            "run_identity_basis": "requested_single_run" if run_at else "unknown",
            "availability": "available_by_collection_not_first_publication_time",
            "interpretation": "coverage_labels_are_days_after_collection",
            "collected_at": collected.isoformat(), "samples": [asdict(m) for m in samples],
            "rain_coverage": coverage, "scientific_approval": False}


async def _main(args: argparse.Namespace) -> bool:
    location = CanonicalLocation("experimental-point", args.latitude, args.longitude,
                                 args.timezone, "explicit-cli-input")
    succeeded = True
    async with httpx.AsyncClient(trust_env=False, follow_redirects=False) as client:
        for model in dict.fromkeys(args.models):
            try:
                report = await collect_once(client, location, model, args.output, run_at=args.run)
                print(canonical_json(report), flush=True)
            except (ValueError, TypeError, OverflowError, httpx.HTTPError, ProviderPermanentError,
                    ProviderTransientError, WeatherDataInvalid) as error:
                succeeded = False
                print(json.dumps({"model": model, "error": type(error).__name__}), flush=True)
    return succeeded


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=MODELS)
    parser.add_argument("--run", type=datetime.fromisoformat)
    raise SystemExit(0 if asyncio.run(_main(parser.parse_args())) else 1)
