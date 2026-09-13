from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from climaprev.api.deps import enforce_rate_limit, get_forecast_query_service
from climaprev.api.schemas.risk import RiskQueryParams
from climaprev.application.query import ForecastQuery
from climaprev.application.services.forecast_query import ForecastQueryPort, RiskQueryResult
from climaprev.domain.units import TemperatureUnit

router = APIRouter(prefix="/api/v1", tags=["risk"])


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
    official_alerts: OfficialAlertsResponse
    data_quality: DataQualityResponse
    source: SourceResponse
    disclaimer: str

    @classmethod
    def from_result(cls, result: RiskQueryResult, request_id: str) -> RiskQueryResponse:
        return cls(
            request_id=request_id,
            location=LocationResponse(
                name=result.location.name,
                latitude=result.location.latitude,
                longitude=result.location.longitude,
                timezone=result.location.timezone,
                source=result.location.source,
            ),
            period=PeriodResponse(start_date=result.period.start, end_date=result.period.end),
            temperature_unit=result.temperature_unit,
            days=[
                ForecastDayResponse(
                    date=day.date,
                    temperature_min=day.temperature_min,
                    temperature_max=day.temperature_max,
                    temperature_mean=day.temperature_mean,
                    humidity_mean_pct=day.humidity_mean_pct,
                    precipitation_sum_mm=day.precipitation_sum_mm,
                    precipitation_probability_max_pct=day.precipitation_probability_max_pct,
                    precipitation_max_hourly_mm=day.precipitation_max_hourly_mm,
                    wind_max_kmh=day.wind_max_kmh,
                    wind_gust_max_kmh=day.wind_gust_max_kmh,
                    weather_code=day.weather_code,
                )
                for day in result.days
            ],
            forecast_risk=ForecastRiskResponse(
                level=result.forecast_risk.level,
                method=result.forecast_risk.method,
                policy_version=result.forecast_risk.policy_version,
                conditions=[
                    RiskConditionResponse(
                        type=condition.type,
                        severity=condition.severity,
                        value=condition.value,
                        unit=condition.unit,
                        reason=condition.reason,
                    )
                    for condition in result.forecast_risk.conditions
                ],
            ),
            official_alerts=OfficialAlertsResponse(
                status=result.official_alerts.status,
                items=[
                    OfficialAlertResponse(
                        source=alert.source,
                        event=alert.event,
                        severity=alert.severity,
                        effective_at=alert.effective_at,
                        expires_at=alert.expires_at,
                        geographic_scope=alert.geographic_scope,
                        source_url=alert.source_url,
                    )
                    for alert in result.official_alerts.items
                ],
            ),
            data_quality=DataQualityResponse(
                is_stale=result.data_quality.is_stale,
                missing_fields=list(result.data_quality.missing_fields),
                completeness=result.data_quality.completeness,
            ),
            source=SourceResponse(
                provider=result.source.provider,
                fetched_at=result.source.fetched_at,
            ),
            disclaimer=result.disclaimer,
        )


@router.get("/risk", response_model=RiskQueryResponse, dependencies=[Depends(enforce_rate_limit)])
async def get_risk(
    request: Request,
    query: Annotated[RiskQueryParams, Depends()],
    service: Annotated[ForecastQueryPort, Depends(get_forecast_query_service)],
) -> RiskQueryResponse:
    request.state.provider = "open-meteo"
    request.state.cache = "miss"
    result = await service.execute(
        ForecastQuery(
            location_text=query.location_text,
            latitude=query.latitude,
            longitude=query.longitude,
            start_date=query.start_date,
            end_date=query.end_date or query.start_date,
            temperature_unit=query.temperature_unit,
        ),
        request.state.request_id,
    )
    request.state.provider = result.source.provider
    request.state.cache = result.cache_status
    return RiskQueryResponse.from_result(result, request.state.request_id)
