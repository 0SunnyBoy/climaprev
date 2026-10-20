"""Collect quality-checked historical inputs, or replay saved inputs without network I/O.

The observed target is frozen reference-v1 on reanalysis. Results diagnose
meteorological agreement; they neither validate impacts nor activate a policy.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from math import isfinite
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
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.domain.risk_validation import RiskValidationReport
from climaprev.infrastructure.http.client import AsyncJsonHttpClient
from climaprev.tools.historical_experiment import (
    digest,
    evaluate_snapshots,
    load_snapshot,
    save_snapshot,
    snapshot,
)

_FIELDS = ("temperature_2m", "relative_humidity_2m", "precipitation",
           "wind_gusts_10m", "weather_code")


@dataclass(frozen=True, slots=True)
class HistoricalValidationConfig:
    latitude: float
    longitude: float
    start: date
    end: date
    lead_days: int
    timezone: str = "auto"
    minimum_coverage: float = 1.0
    forecast_model: str = "gfs_global"
    observed_model: str = "era5"

    def __post_init__(self) -> None:
        if DatePeriod(self.start, self.end).days > 31:
            raise ValueError("historical validation is limited to 31 days per collection")
        if (isinstance(self.lead_days, bool) or not isinstance(self.lead_days, int)
                or not 1 <= self.lead_days <= 7):
            raise ValueError("lead_days must be between 1 and 7")
        CanonicalLocation("experiment", self.latitude, self.longitude, "UTC", "experiment")
        if self.timezone != "auto":
            ZoneInfo(self.timezone)
        if not isfinite(self.minimum_coverage) or not 0 < self.minimum_coverage <= 1:
            raise ValueError("minimum_coverage must be between zero (exclusive) and one")
        if not self.forecast_model.strip() or not self.observed_model.strip():
            raise ValueError("forecast and observed models must be explicit")


@dataclass(frozen=True, slots=True)
class HistoricalValidationResult:
    location: CanonicalLocation
    period: DatePeriod
    lead_days: int
    cases: int
    report: RiskValidationReport
    forecast_source: str
    observed_source: str
    comparison: dict[str, Any]
    inputs: dict[str, Any] = field(repr=False)


async def collect_and_validate(
    config: HistoricalValidationConfig, *, settings: Settings | None = None,
    save_input: Path | None = None,
) -> HistoricalValidationResult:
    """Two bounded provider calls; no Redis or public application side effects."""
    current = settings or Settings(environment="test")
    forecast_url = f"{current.historical_forecast_base_url.rstrip('/')}/v1/forecast"
    observed_url = f"{current.historical_weather_base_url.rstrip('/')}/v1/archive"
    forecast_params = _forecast_params(config)
    observed_params = _observed_params(config)
    async with httpx.AsyncClient() as client:
        http = AsyncJsonHttpClient(client, current)
        forecast = await http.get_json(forecast_url, forecast_params)
        observed = await http.get_json(observed_url, observed_params)
    configuration = asdict(config)
    configuration["start"] = config.start.isoformat()
    configuration["end"] = config.end.isoformat()
    inputs = snapshot(configuration, forecast, observed, {
        "forecast": {"url": forecast_url, "params": forecast_params},
        "observed": {"url": observed_url, "params": observed_params},
    })
    if save_input is not None:
        save_snapshot(save_input, inputs)
    return replay(inputs)


def replay(inputs: dict[str, Any]) -> HistoricalValidationResult:
    comparison = evaluate_snapshots([inputs])
    config = inputs["configuration"]
    overall = comparison["variants"]["R0"]["overall"]
    matrix = overall["confusion_matrix"]
    over = sum(matrix[actual][predicted] for actual in range(3)
               for predicted in range(3) if predicted > actual)
    under = sum(matrix[actual][predicted] for actual in range(3)
                for predicted in range(3) if predicted < actual)
    report = RiskValidationReport(
        overall["cases"], overall["correct"], over, under,
        overall["accuracy"] if overall["accuracy"] is not None else 0.0, "reference-v1",
    )
    location = CanonicalLocation(
        f"{config['latitude']:.4f},{config['longitude']:.4f}", config["latitude"],
        config["longitude"], inputs["forecast"]["timezone"], "historical-experiment",
    )
    return HistoricalValidationResult(
        location, DatePeriod(date.fromisoformat(config["start"]), date.fromisoformat(config["end"])),
        config["lead_days"], report.cases, report, "Open-Meteo Previous Runs API",
        "Open-Meteo Historical Weather API (reanalysis)", comparison, inputs,
    )


def _params(config: HistoricalValidationConfig, suffix: str, model: str) -> dict[str, str | float | int]:
    return {
        "latitude": config.latitude, "longitude": config.longitude,
        "start_date": config.start.isoformat(), "end_date": config.end.isoformat(),
        "timezone": config.timezone, "hourly": ",".join(field + suffix for field in _FIELDS),
        "temperature_unit": "celsius", "wind_speed_unit": "kmh", "precipitation_unit": "mm",
        "models": model,
    }


def _forecast_params(config: HistoricalValidationConfig) -> dict[str, str | float | int]:
    return _params(config, f"_previous_day{config.lead_days}", config.forecast_model)


def _observed_params(config: HistoricalValidationConfig) -> dict[str, str | float | int]:
    return _params(config, "", config.observed_model)


def _result_json(result: HistoricalValidationResult) -> dict[str, object]:
    return {
        "location": asdict(result.location),
        "period": {"start": result.period.start.isoformat(), "end": result.period.end.isoformat()},
        "lead_days": result.lead_days, "cases": result.cases, "report": asdict(result.report),
        "sources": {"forecast": result.forecast_source, "observed": result.observed_source},
        "dataset_sha256": digest(result.inputs), "comparison": result.comparison,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="replay a checksum-verified snapshot without network")
    parser.add_argument("--save-input", type=Path, help="save immutable raw inputs and provenance")
    parser.add_argument("--latitude", type=float)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    parser.add_argument("--lead-days", type=int, choices=range(1, 8))
    parser.add_argument("--timezone")
    parser.add_argument("--minimum-coverage", type=float)
    parser.add_argument("--forecast-model")
    parser.add_argument("--observed-model")
    parser.add_argument("--output", type=Path)
    return parser


async def _run(args: argparse.Namespace) -> int:
    if args.input is not None:
        if args.save_input is not None or any(getattr(args, key) is not None for key in (
            "latitude", "longitude", "start", "end", "lead_days", "timezone",
            "minimum_coverage", "forecast_model", "observed_model",
        )):
            raise ValueError("replay must not be combined with collection parameters")
        result = replay(load_snapshot(args.input))
    else:
        if any(getattr(args, key) is None for key in ("latitude", "longitude", "start", "end")):
            raise ValueError("collection requires latitude, longitude, start and end")
        result = await collect_and_validate(HistoricalValidationConfig(
            args.latitude, args.longitude, args.start, args.end,
            args.lead_days if args.lead_days is not None else 1,
            args.timezone if args.timezone is not None else "auto",
            args.minimum_coverage if args.minimum_coverage is not None else 1.0,
            args.forecast_model if args.forecast_model is not None else "gfs_global",
            args.observed_model if args.observed_model is not None else "era5",
        ), save_input=args.save_input)
    payload = json.dumps(_result_json(result), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"Historical validation report written to {args.output}")
    return 0


def main() -> None:
    args = _parser().parse_args()
    try:
        raise SystemExit(asyncio.run(_run(args)))
    except (ValueError, WeatherDataInvalid, OSError, TypeError, KeyError,
            ProviderPermanentError, ProviderTransientError) as error:
        raise SystemExit(f"historical validation failed: {error}") from error


if __name__ == "__main__":
    main()
