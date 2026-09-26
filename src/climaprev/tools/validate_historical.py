"""Validate the risk policy with Open-Meteo historical forecast runs.

This is an offline analysis command, not a production API route. It compares
archived forecasts from fixed lead times with historical weather data and
writes only an aggregate report. No database is required and no calibration is
activated automatically.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from math import isfinite
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DailyForecast, DatePeriod, NormalizedForecast
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.risk_validation import (
    HistoricalRiskCase,
    RiskValidationReport,
    validate_policy,
)
from climaprev.infrastructure.http.client import AsyncJsonHttpClient, WeatherDataInvalid

_FIELDS = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_gusts_10m",
    "weather_code",
)
_MAX_PERIOD_DAYS = 31


@dataclass(frozen=True, slots=True)
class HistoricalValidationConfig:
    latitude: float
    longitude: float
    start: date
    end: date
    lead_days: int
    timezone: str = "auto"

    def __post_init__(self) -> None:
        period = DatePeriod(self.start, self.end)
        if period.days > _MAX_PERIOD_DAYS:
            raise ValueError(f"historical validation is limited to {_MAX_PERIOD_DAYS} days")
        if not 1 <= self.lead_days <= 7:
            raise ValueError("lead_days must be between 1 and 7")


@dataclass(frozen=True, slots=True)
class HistoricalValidationResult:
    location: CanonicalLocation
    period: DatePeriod
    lead_days: int
    cases: int
    report: RiskValidationReport
    forecast_source: str
    observed_source: str


async def collect_and_validate(
    config: HistoricalValidationConfig,
    *,
    settings: Settings | None = None,
) -> HistoricalValidationResult:
    """Collect a bounded historical sample and evaluate the current policy."""

    current_settings = settings or Settings(environment="test")
    location = CanonicalLocation(
        name=f"{config.latitude:.4f},{config.longitude:.4f}",
        latitude=config.latitude,
        longitude=config.longitude,
        timezone="UTC",
        source="open-meteo-historical-validation",
    )
    async with httpx.AsyncClient() as client:
        http = AsyncJsonHttpClient(client, current_settings)
        forecast_payload = await http.get_json(
            f"{current_settings.historical_forecast_base_url.rstrip('/')}/v1/forecast",
            _forecast_params(config),
        )
        observed_payload = await http.get_json(
            f"{current_settings.historical_weather_base_url.rstrip('/')}/v1/archive",
            _observed_params(config),
        )

    forecast_timezone = _timezone(forecast_payload.get("timezone"))
    observed_timezone = _timezone(observed_payload.get("timezone"))
    location = CanonicalLocation(
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude,
        timezone=forecast_timezone,
        source=location.source,
    )
    forecast_days = _daily_forecasts(
        forecast_payload, config, field_suffix=f"_previous_day{config.lead_days}",
        timezone=forecast_timezone,
    )
    observed_days = _daily_forecasts(
        observed_payload, config, field_suffix="", timezone=observed_timezone,
    )
    evaluator = RiskEvaluator()
    policy = RiskPolicy()
    cases = tuple(
        HistoricalRiskCase(
            forecast=_normalized_forecast(location, day, (forecast_days[day],)),
            observed_level=evaluator.evaluate(
                _normalized_forecast(location, day, (observed_days[day],)), policy
            ).level,
        )
        for day in sorted(set(forecast_days).intersection(observed_days))
    )
    if not cases:
        raise WeatherDataInvalid("historical APIs returned no aligned daily observations")
    return HistoricalValidationResult(
        location=location,
        period=DatePeriod(config.start, config.end),
        lead_days=config.lead_days,
        cases=len(cases),
        report=validate_policy(cases, policy, evaluator),
        forecast_source="Open-Meteo Previous Runs API",
        observed_source="Open-Meteo Historical Weather API",
    )


def _forecast_params(config: HistoricalValidationConfig) -> dict[str, str | float | int]:
    return {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "start_date": config.start.isoformat(),
        "end_date": config.end.isoformat(),
        "timezone": config.timezone,
        "hourly": ",".join(f"{field}_previous_day{config.lead_days}" for field in _FIELDS),
    }


def _observed_params(config: HistoricalValidationConfig) -> dict[str, str | float | int]:
    return {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "start_date": config.start.isoformat(),
        "end_date": config.end.isoformat(),
        "timezone": config.timezone,
        "hourly": ",".join(_FIELDS),
    }


def _daily_forecasts(
    payload: dict[str, object],
    config: HistoricalValidationConfig,
    *,
    field_suffix: str,
    timezone: str,
) -> dict[date, DailyForecast]:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise WeatherDataInvalid("historical hourly payload must be an object")
    raw_times = hourly.get("time")
    if not isinstance(raw_times, list) or not raw_times or not all(isinstance(item, str) for item in raw_times):
        raise WeatherDataInvalid("historical hourly.time must be a non-empty list")
    times = tuple(_parse_hour(item, timezone) for item in raw_times)
    series: dict[str, list[float | None]] = {}
    for field in _FIELDS:
        key = f"{field}{field_suffix}"
        values = hourly.get(key)
        if not isinstance(values, list) or len(values) != len(times):
            raise WeatherDataInvalid(f"historical hourly.{key} is missing or misaligned")
        series[field] = [_number(value) for value in values]

    result: dict[date, DailyForecast] = {}
    for day_index in range(DatePeriod(config.start, config.end).days):
        day = config.start + timedelta(days=day_index)
        indexes = [index for index, timestamp in enumerate(times) if timestamp.date() == day]
        if not indexes:
            continue
        temperatures = _values(series["temperature_2m"], indexes)
        precipitation = _values(series["precipitation"], indexes)
        gusts = _values(series["wind_gusts_10m"], indexes)
        humidity = _values(series["relative_humidity_2m"], indexes)
        codes = [series["weather_code"][index] for index in indexes]
        result[day] = DailyForecast(
            date=day,
            temperature_min_c=min(temperatures) if temperatures else None,
            temperature_max_c=max(temperatures) if temperatures else None,
            temperature_mean_c=_mean(temperatures),
            humidity_mean_pct=_mean(humidity),
            precipitation_sum_mm=sum(precipitation) if precipitation else None,
            precipitation_probability_max_pct=None,
            precipitation_max_hourly_mm=max(precipitation) if precipitation else None,
            wind_max_kmh=None,
            wind_gust_max_kmh=max(gusts) if gusts else None,
            weather_code=next((int(code) for code in codes if code is not None), None),
        )
    return result


def _normalized_forecast(
    location: CanonicalLocation,
    day: date,
    days: tuple[DailyForecast, ...],
) -> NormalizedForecast:
    return NormalizedForecast(
        location=location,
        period=DatePeriod(day, day),
        days=days,
        provider="open-meteo-historical",
        fetched_at=datetime.now(UTC),
        is_stale=False,
        missing_fields=(),
    )


def _timezone(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WeatherDataInvalid("historical timezone is missing")
    try:
        ZoneInfo(value)
    except (KeyError, ValueError) as error:
        raise WeatherDataInvalid("historical timezone is invalid") from error
    return value


def _parse_hour(value: str, timezone: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise WeatherDataInvalid("historical hourly timestamps are invalid") from error
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=ZoneInfo(timezone))


def _number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float) or not isfinite(value):
        raise WeatherDataInvalid("historical values must be finite numbers or null")
    return float(value)


def _values(series: Sequence[float | None], indexes: list[int]) -> list[float]:
    return [value for index in indexes if (value := series[index]) is not None]


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _result_json(result: HistoricalValidationResult) -> dict[str, object]:
    return {
        "location": asdict(result.location),
        "period": {"start": result.period.start.isoformat(), "end": result.period.end.isoformat()},
        "lead_days": result.lead_days,
        "cases": result.cases,
        "report": asdict(result.report),
        "sources": {"forecast": result.forecast_source, "observed": result.observed_source},
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--lead-days", type=int, choices=range(1, 8), default=1)
    parser.add_argument("--output", type=Path)
    return parser


async def _run(args: argparse.Namespace) -> int:
    config = HistoricalValidationConfig(
        latitude=args.latitude,
        longitude=args.longitude,
        start=args.start,
        end=args.end,
        lead_days=args.lead_days,
    )
    result = await collect_and_validate(config)
    payload = json.dumps(_result_json(result), ensure_ascii=False, indent=2) + "\n"
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
    except (ValueError, WeatherDataInvalid) as error:
        raise SystemExit(f"historical validation failed: {error}") from error


if __name__ == "__main__":
    main()
