from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager, suppress

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from starlette.middleware.trustedhost import TrustedHostMiddleware

from climaprev.api.exception_handlers import register_error_handlers
from climaprev.api.observability import RequestMetrics, observe_request
from climaprev.api.routes import risk_router
from climaprev.api.routes.health import register_health_routes
from climaprev.api.routes.locations import router as locations_router
from climaprev.api.routes.metrics import router as metrics_router
from climaprev.application.services.forecast_query import ForecastQueryService
from climaprev.config import Settings
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.cache.redis_lock import RedisLock
from climaprev.infrastructure.metrics_store import MetricsStore
from climaprev.infrastructure.providers.inmet_alerts import InmetOfficialAlertsProvider
from climaprev.infrastructure.providers.open_meteo import (
    OpenMeteoForecastClient,
    OpenMeteoGeocodingClient,
)
from climaprev.infrastructure.rate_limit.provider_budget import ProviderBudget
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter
from climaprev.infrastructure.redis_delay import DelayedRedis, RedisConnection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    async with AsyncExitStack() as resources:
        http_client = httpx.AsyncClient(
            follow_redirects=False,
            trust_env=False,
            limits=httpx.Limits(
                max_connections=settings.http_max_connections,
                max_keepalive_connections=settings.http_max_keepalive_connections,
            ),
            timeout=httpx.Timeout(
                connect=settings.connect_timeout_seconds,
                read=settings.read_timeout_seconds,
                write=settings.read_timeout_seconds,
                pool=settings.connect_timeout_seconds,
            ),
        )
        resources.push_async_callback(http_client.aclose)
        raw_redis = Redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
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
        app.state.rate_limiter = RedisRateLimiter(
            redis, environment=settings.environment, identity_key=settings.client_ip_hmac_key
        )
        provider_budget = ProviderBudget(redis, settings)
        geocoder = OpenMeteoGeocodingClient(
            http_client,
            settings,
            on_retry=app.state.metrics.record_upstream_retry,
            before_send=provider_budget.consume,
        )
        app.state.location_search = geocoder
        app.state.forecast_query_service = ForecastQueryService(
            geocoder=geocoder,
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
            official_alert_provider=InmetOfficialAlertsProvider(
                http_client,
                settings,
                on_retry=app.state.metrics.record_upstream_retry,
                before_send=provider_budget.consume,
            ),
            metrics=app.state.metrics,
            provider_identity=settings.forecast_base_url,
        )
        app.state.metrics_store = MetricsStore(raw_redis, settings.environment)
        publisher = None
        if settings.metrics_aggregation_enabled:
            publisher = asyncio.create_task(app.state.metrics_store.run(app.state.metrics))
        try:
            yield
        finally:
            if publisher is not None:
                publisher.cancel()
                with suppress(asyncio.CancelledError):
                    await publisher


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or Settings()
    documentation = runtime_settings.environment == "development"
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs" if documentation else None,
        redoc_url="/redoc" if documentation else None,
        openapi_url="/openapi.json" if documentation else None,
    )
    app.state.settings = runtime_settings
    app.state.metrics = RequestMetrics()
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=list(runtime_settings.allowed_hosts), www_redirect=False
    )
    if app.state.settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(app.state.settings.cors_allow_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
            expose_headers=["X-Request-ID", "Retry-After"],
        )
    app.middleware("http")(observe_request)
    app.include_router(risk_router)
    app.include_router(locations_router)
    app.include_router(metrics_router)
    register_error_handlers(app)
    register_health_routes(app)
    return app


app = create_app()
