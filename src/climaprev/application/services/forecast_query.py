"""Orchestrate location, forecast, risk evaluation and official alerts."""

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime

from climaprev.application.errors import WeatherProviderUnavailable
from climaprev.application.ports import (
    CachePort,
    GeocodingPort,
    LockPort,
    MetricsPort,
    OfficialAlertPort,
    RiskEvaluatorPort,
    WeatherProviderPort,
)
from climaprev.application.query import ForecastQuery
from climaprev.application.query_result import (
    DataQuality,
    ForecastSource,
    RiskQueryResult,
    build_risk_overview,
    response_day,
    response_risk,
)
from climaprev.application.services.alert_query import CachedOfficialAlerts
from climaprev.application.services.forecast_cache import CachedForecastProvider
from climaprev.application.services.location_resolver import CachedLocationResolver
from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.data_quality import completeness
from climaprev.domain.models import DatePeriod
from climaprev.domain.risk_policy import RiskPolicy

_DISCLAIMER = (
    "Esta previsão é uma estimativa baseada em dados meteorológicos e não substitui alertas "
    "oficiais das autoridades competentes."
)


class ForecastQueryService:
    def __init__(
        self,
        *,
        geocoder: GeocodingPort,
        weather_provider: WeatherProviderPort,
        cache: CachePort,
        lock: LockPort,
        risk_evaluator: RiskEvaluatorPort,
        risk_policy: RiskPolicy,
        official_alert_provider: OfficialAlertPort,
        calibration: ForecastCalibration | None = None,
        metrics: MetricsPort | None = None,
        provider_identity: str = "https://api.open-meteo.com",
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._locations = CachedLocationResolver(geocoder, cache)
        self._forecasts = CachedForecastProvider(
            weather_provider=weather_provider, cache=cache, lock=lock,
            calibration=calibration, metrics=metrics, provider_identity=provider_identity, now=now,
        )
        self._alerts = CachedOfficialAlerts(official_alert_provider, cache, now=now)
        self._risk_evaluator = risk_evaluator
        self._risk_policy = risk_policy
        self._metrics = metrics
        self._now = now

    async def execute(self, query: ForecastQuery, request_id: str) -> RiskQueryResult:
        period = DatePeriod(start=query.start_date, end=query.end_date)
        location = await self._locations.resolve(query)
        forecast, cache_status, fallback_expires_at = await self._forecasts.get(location, period)
        forecast_risk = self._risk_evaluator.evaluate(forecast, self._risk_policy)
        if self._metrics is not None:
            self._metrics.record_risk_evaluation(forecast_risk)
            self._metrics.record_missing_fields(forecast.missing_fields)
        official_alerts = await self._alerts.get(location, period)
        if self._metrics is not None:
            self._metrics.record_official_alert_status(official_alerts.status)
        response_forecast_risk = response_risk(forecast_risk, query.temperature_unit)
        risk_overview = build_risk_overview(
            forecast_risk, official_alerts, period, forecast.location.timezone
        )
        if fallback_expires_at is not None and self._now() >= fallback_expires_at:
            raise WeatherProviderUnavailable("cached forecast expired before delivery")

        return RiskQueryResult(
            location=replace(location, timezone=forecast.location.timezone),
            period=period,
            temperature_unit=query.temperature_unit,
            days=tuple(response_day(day, query.temperature_unit) for day in forecast.days),
            forecast_risk=response_forecast_risk,
            risk_overview=risk_overview,
            official_alerts=official_alerts,
            data_quality=DataQuality(
                is_stale=forecast.is_stale,
                missing_fields=forecast.missing_fields,
                completeness=completeness(forecast),
            ),
            source=ForecastSource(provider=forecast.provider, fetched_at=forecast.fetched_at),
            disclaimer=_DISCLAIMER,
            request_id=request_id,
            cache_status=cache_status,
        )
