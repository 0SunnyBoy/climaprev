from __future__ import annotations

import asyncio
from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, Request

from climaprev.api.deps import enforce_rate_limit, get_forecast_query_service
from climaprev.api.forecast_window import validate_public_period
from climaprev.api.schemas.risk import RiskQueryParams
from climaprev.api.schemas.risk_response import RiskQueryResponse
from climaprev.application.errors import WeatherProviderUnavailable
from climaprev.application.ports import ForecastQueryPort
from climaprev.application.query import ForecastQuery
from climaprev.config import Settings

router = APIRouter(prefix="/api/v1", tags=["risk"])


async def _execute_risk(
    request: Request,
    query: RiskQueryParams,
    service: ForecastQueryPort,
) -> RiskQueryResponse:
    validate_public_period(query.start_date, query.end_date or query.start_date)
    request.state.provider = "open-meteo"
    request.state.cache = "miss"
    settings = cast(Settings, request.app.state.settings)
    try:
        async with asyncio.timeout(settings.query_total_timeout_seconds):
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
    except TimeoutError:
        raise WeatherProviderUnavailable("public risk query deadline exceeded") from None
    request.state.provider = result.source.provider
    request.state.cache = result.cache_status
    return RiskQueryResponse.from_result(result, request.state.request_id)


@router.get("/risk", response_model=RiskQueryResponse, dependencies=[Depends(enforce_rate_limit)])
async def get_risk(
    request: Request,
    query: Annotated[RiskQueryParams, Depends()],
    service: Annotated[ForecastQueryPort, Depends(get_forecast_query_service)],
) -> RiskQueryResponse:
    return await _execute_risk(request, query, service)


@router.post("/risk", response_model=RiskQueryResponse, dependencies=[Depends(enforce_rate_limit)])
async def post_risk(
    request: Request,
    query: Annotated[RiskQueryParams, Body()],
    service: Annotated[ForecastQueryPort, Depends(get_forecast_query_service)],
) -> RiskQueryResponse:
    return await _execute_risk(request, query, service)
