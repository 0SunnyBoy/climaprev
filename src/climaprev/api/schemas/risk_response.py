"""Public response schemas and conversion from application output."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from climaprev.application.query_result import RiskQueryResult
from climaprev.domain.models import RiskOverview
from climaprev.domain.units import TemperatureUnit


class LocationResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    timezone: str
    source: str


class PeriodResponse(BaseModel):
    start_date: date
    end_date: date


class ForecastDayResponse(BaseModel):
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


class RiskConditionResponse(BaseModel):
    type: str
    severity: Literal["moderate", "high"]
    value: float
    unit: str
    reason: str


class ForecastRiskResponse(BaseModel):
    level: Literal["low", "moderate", "high"]
    method: str
    policy_version: str
    conditions: list[RiskConditionResponse]
    peak_days: list[date]
    daily: list[RiskDayResponse]


class RiskDayResponse(BaseModel):
    date: date
    level: Literal["low", "moderate", "high"]
    conditions: list[RiskConditionResponse]


class RiskOverviewResponse(BaseModel):
    level: Literal["low", "moderate", "high"]
    source: Literal["forecast_heuristic", "official_alert"]
    peak_days: list[date]


class OfficialAlertResponse(BaseModel):
    source: str
    event: str
    severity: str
    effective_at: datetime
    expires_at: datetime | None
    geographic_scope: str
    source_url: str | None


class OfficialAlertsResponse(BaseModel):
    status: Literal["available", "not_configured", "unavailable"]
    items: list[OfficialAlertResponse]


class DataQualityResponse(BaseModel):
    is_stale: bool
    missing_fields: list[str]
    completeness: Literal["complete", "partial", "unavailable"]


class SourceResponse(BaseModel):
    provider: str
    fetched_at: datetime


class RiskQueryResponse(BaseModel):
    request_id: str
    location: LocationResponse
    period: PeriodResponse
    temperature_unit: TemperatureUnit
    days: list[ForecastDayResponse]
    forecast_risk: ForecastRiskResponse
    risk_overview: RiskOverviewResponse
    official_alerts: OfficialAlertsResponse
    data_quality: DataQualityResponse
    source: SourceResponse
    disclaimer: str

    @classmethod
    def from_result(cls, result: RiskQueryResult, request_id: str) -> RiskQueryResponse:
        overview = result.risk_overview or RiskOverview(
            level=result.forecast_risk.level,
            source="forecast_heuristic",
            peak_days=result.forecast_risk.peak_days,
        )
        return cls.model_validate({
            "request_id": request_id,
            "location": result.location,
            "period": {"start_date": result.period.start, "end_date": result.period.end},
            "temperature_unit": result.temperature_unit,
            "days": result.days,
            "forecast_risk": result.forecast_risk,
            "risk_overview": overview,
            "official_alerts": result.official_alerts,
            "data_quality": result.data_quality,
            "source": result.source,
            "disclaimer": result.disclaimer,
        }, from_attributes=True)
