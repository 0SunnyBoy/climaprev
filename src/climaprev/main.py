from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.responses import JSONResponse

from climaprev.api.errors import ApplicationError, ErrorBody, ErrorEnvelope, RateLimitExceeded
from climaprev.api.observability import RequestMetrics, observe_request
from climaprev.api.routes import risk_router
from climaprev.application.errors import (
    DependencyUnavailable,
    LocationNotFound,
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.application.official_alerts import OfficialAlertsNotConfiguredProvider
from climaprev.application.services.forecast_query import (
    ForecastQueryService,
    WeatherProviderUnavailable,
)
from climaprev.config import Settings
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.cache.redis_lock import RedisLock
from climaprev.infrastructure.providers.open_meteo import (
    OpenMeteoForecastClient,
    OpenMeteoGeocodingClient,
)
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter
from climaprev.infrastructure.rate_limit.provider_budget import ProviderBudget
from climaprev.infrastructure.redis_delay import DelayedRedis, RedisConnection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    async with AsyncExitStack() as resources:
        http_client = httpx.AsyncClient()
        resources.push_async_callback(http_client.aclose)
        raw_redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.redis_socket_timeout_seconds,
            socket_timeout=settings.redis_socket_timeout_seconds,
        )
        redis: RedisConnection = raw_redis
        if settings.effective_redis_operation_delay_ms:
            redis = DelayedRedis(
                raw_redis,
                delay_milliseconds=settings.effective_redis_operation_delay_ms,
            )
        resources.push_async_callback(redis.aclose)
        app.state.redis = redis
        app.state.rate_limiter = RedisRateLimiter(redis, environment=settings.environment)
        provider_budget = ProviderBudget(redis, settings)
        app.state.forecast_query_service = ForecastQueryService(
            geocoder=OpenMeteoGeocodingClient(
                http_client,
                settings,
                on_retry=app.state.metrics.record_upstream_retry,
                before_send=provider_budget.consume,
            ),
            weather_provider=OpenMeteoForecastClient(
                http_client,
                settings,
                on_retry=app.state.metrics.record_upstream_retry,
                before_send=provider_budget.consume,
            ),
            cache=RedisCache(
                redis,
                environment=settings.environment,
                on_corruption=app.state.metrics.record_cache_corruption,
            ),
            lock=RedisLock(redis, environment=settings.environment),
            risk_evaluator=RiskEvaluator(),
            risk_policy=RiskPolicy(),
            official_alert_provider=OfficialAlertsNotConfiguredProvider(),
            metrics=app.state.metrics,
            provider_identity=settings.forecast_base_url,
        )
        yield


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.state.settings = settings or Settings()
    app.state.metrics = RequestMetrics()
    if app.state.settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(app.state.settings.cors_allow_origins),
            allow_credentials=False,
            allow_methods=["GET"],
            allow_headers=["X-Request-ID"],
        )
    app.middleware("http")(observe_request)
    app.include_router(risk_router)
    _register_error_handlers(app)
    _register_health_routes(app)
    return app


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        code, message = _validation_error(error)
        return _error_response(request, 422, code, message)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(
        request: Request,
        error: ValidationError,
    ) -> JSONResponse:
        code, message = _validation_error(error)
        return _error_response(request, 422, code, message)

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
        if error.status_code == 422 and error.code in {
            "INVALID_LOCATION_INPUT",
            "INVALID_PERIOD",
            "INVALID_TEMPERATURE_UNIT",
        }:
            return _error_response(request, 422, error.code, error.message)
        return _error_response(request, 500, "INTERNAL_ERROR", "internal server error")

    @app.exception_handler(LocationNotFound)
    async def location_not_found_handler(request: Request, error: LocationNotFound) -> JSONResponse:
        return _error_response(request, 404, "LOCATION_NOT_FOUND", "location was not found")

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, error: RateLimitExceeded) -> JSONResponse:
        return _error_response(
            request,
            429,
            "RATE_LIMIT_EXCEEDED",
            "rate limit exceeded",
            headers={"Retry-After": str(error.retry_after_seconds)},
        )

    @app.exception_handler(WeatherDataInvalid)
    async def weather_data_handler(request: Request, error: WeatherDataInvalid) -> JSONResponse:
        return _error_response(request, 502, "WEATHER_DATA_INVALID", "weather data was invalid")

    @app.exception_handler(ProviderPermanentError)
    async def provider_rejected_handler(
        request: Request, error: ProviderPermanentError
    ) -> JSONResponse:
        return _error_response(
            request, 502, "WEATHER_PROVIDER_REJECTED", "weather provider rejected the request"
        )

    @app.exception_handler(ProviderTransientError)
    @app.exception_handler(WeatherProviderUnavailable)
    async def weather_unavailable_handler(
        request: Request,
        error: ProviderTransientError | WeatherProviderUnavailable,
    ) -> JSONResponse:
        return _error_response(
            request,
            503,
            "WEATHER_PROVIDER_UNAVAILABLE",
            "weather provider is unavailable",
        )

    @app.exception_handler(DependencyUnavailable)
    async def dependency_handler(request: Request, error: DependencyUnavailable) -> JSONResponse:
        return _error_response(request, 503, "DEPENDENCY_UNAVAILABLE", "dependency is unavailable")

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, error: Exception) -> JSONResponse:
        return _error_response(request, 500, "INTERNAL_ERROR", "internal server error")


def _register_health_routes(app: FastAPI) -> None:
    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready")
    async def ready(request: Request) -> dict[str, str]:
        try:
            available = await request.app.state.redis.ping()
        except RedisError as error:
            request.app.state.metrics.record_dependency_circuit_state("redis", "open")
            raise DependencyUnavailable from error
        if available is not True:
            request.app.state.metrics.record_dependency_circuit_state("redis", "open")
            raise DependencyUnavailable
        request.app.state.metrics.record_dependency_circuit_state("redis", "closed")
        return {"status": "ready"}


def _validation_error(error: RequestValidationError | ValidationError) -> tuple[str, str]:
    locations = [item.get("loc", ()) for item in error.errors()]
    if any("temperature_unit" in location for location in locations):
        return "INVALID_TEMPERATURE_UNIT", "temperature_unit must be celsius or fahrenheit"
    if any("start_date" in location or "end_date" in location for location in locations):
        return "INVALID_PERIOD", "date period is invalid"
    messages = [str(item.get("msg", "")) for item in error.errors()]
    if any("date period" in message or "end_date" in message for message in messages):
        return "INVALID_PERIOD", "date period is invalid"
    return "INVALID_LOCATION_INPUT", "location input is invalid"


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request.state.error_code = code
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content=ErrorEnvelope(
            error=ErrorBody(code=code, message=message, request_id=request_id)
        ).model_dump(),
        headers=headers,
    )


app = create_app()
