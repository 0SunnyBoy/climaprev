"""Framework-independent output of the forecast query use case."""

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from typing import Literal, cast
from zoneinfo import ZoneInfo

from climaprev.domain.data_quality import Completeness
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    OfficialAlert,
    RiskAssessment,
    RiskCondition,
    RiskOverview,
)
from climaprev.domain.units import TemperatureUnit, convert_temperature


@dataclass(frozen=True, slots=True)
class ForecastDay:
    date: date
    temperature_min: float | None
    temperature_max: float | None
    temperature_mean: float | None
    humidity_mean_pct: float | None
    precipitation_sum_mm: float | None
    precipitation_probability_max_pct: float | None
    precipitation_max_hourly_mm: float | None
    wind_max_kmh: float | None
    wind_gust_max_kmh: float | None
    weather_code: int | None


@dataclass(frozen=True, slots=True)
class DataQuality:
    is_stale: bool
    missing_fields: tuple[str, ...]
    completeness: Completeness = "complete"


@dataclass(frozen=True, slots=True)
class ForecastSource:
    provider: str
    fetched_at: datetime


@dataclass(frozen=True, slots=True)
class OfficialAlertsResult:
    status: Literal["available", "not_configured", "unavailable"]
    items: tuple[OfficialAlert, ...]


@dataclass(frozen=True, slots=True)
class RiskQueryResult:
    location: CanonicalLocation
    period: DatePeriod
    temperature_unit: TemperatureUnit
    days: tuple[ForecastDay, ...]
    forecast_risk: RiskAssessment
    official_alerts: OfficialAlertsResult
    data_quality: DataQuality
    source: ForecastSource
    disclaimer: str
    request_id: str
    risk_overview: RiskOverview | None = None
    cache_status: Literal["hit", "miss", "stale"] = "miss"


def response_day(day: DailyForecast, unit: TemperatureUnit) -> ForecastDay:
    return ForecastDay(
        date=day.date,
        temperature_min=convert_temperature(day.temperature_min_c, unit),
        temperature_max=convert_temperature(day.temperature_max_c, unit),
        temperature_mean=convert_temperature(day.temperature_mean_c, unit),
        humidity_mean_pct=day.humidity_mean_pct,
        precipitation_sum_mm=day.precipitation_sum_mm,
        precipitation_probability_max_pct=day.precipitation_probability_max_pct,
        precipitation_max_hourly_mm=day.precipitation_max_hourly_mm,
        wind_max_kmh=day.wind_max_kmh,
        wind_gust_max_kmh=day.wind_gust_max_kmh,
        weather_code=day.weather_code,
    )


def response_risk(assessment: RiskAssessment, unit: TemperatureUnit) -> RiskAssessment:
    if unit is TemperatureUnit.CELSIUS:
        return assessment

    conditions = tuple(
        _response_condition(condition, unit) for condition in assessment.conditions
    )
    daily = tuple(
        replace(
            day,
            conditions=tuple(_response_condition(condition, unit) for condition in day.conditions),
        )
        for day in assessment.daily
    )
    return replace(assessment, conditions=conditions, daily=daily)


def build_risk_overview(
    forecast_risk: RiskAssessment,
    official_alerts: OfficialAlertsResult,
    period: DatePeriod,
    timezone: str,
) -> RiskOverview:
    """Build the user-facing risk priority without hiding the heuristic result."""

    if not official_alerts.items:
        return RiskOverview(
            level=forecast_risk.level,
            source="forecast_heuristic",
            peak_days=forecast_risk.peak_days,
        )

    alert_level = max(
        (_official_alert_level(alert.severity) for alert in official_alerts.items),
        key=_risk_rank,
    )
    level = max((forecast_risk.level, alert_level), key=_risk_rank)
    alert_days: set[date] = set()
    zone = ZoneInfo(timezone)
    for alert in official_alerts.items:
        start = alert.effective_at.astimezone(zone).date()
        end = (alert.expires_at.astimezone(zone).date() if alert.expires_at else start)
        current = max(start, period.start)
        last = min(end, period.end)
        while current <= last:
            alert_days.add(current)
            current += timedelta(days=1)

    return RiskOverview(
        level=level,
        source="official_alert",
        peak_days=tuple(sorted(set(forecast_risk.peak_days).union(alert_days))),
    )


def _official_alert_level(severity: str) -> Literal["low", "moderate", "high"]:
    normalized = severity.casefold()
    if any(marker in normalized for marker in ("extreme", "severe", "high", "red", "grave")):
        return "high"
    return "moderate"


def _risk_rank(level: str) -> int:
    return {"low": 0, "moderate": 1, "high": 2}[level]


def _response_condition(condition: RiskCondition, unit: TemperatureUnit) -> RiskCondition:
    if condition.type != "temperature_extreme_proxy":
        return condition
    converted = cast(float, convert_temperature(condition.value, unit))
    return replace(condition, value=converted, unit="fahrenheit")


