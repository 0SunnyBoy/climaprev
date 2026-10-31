from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import UTC, date, datetime

import httpx
import pytest

from climaprev.api.deps import get_forecast_query_service, get_rate_limiter
from climaprev.api.errors import ApplicationError
from climaprev.api.observability import RequestMetrics
from climaprev.application.errors import (
    DependencyUnavailable,
    LocationNotFound,
    ProviderTransientError,
    WeatherDataInvalid,
    WeatherProviderUnavailable,
)
from climaprev.application.ports import RateLimitDecision
from climaprev.application.query import ForecastQuery
from climaprev.application.query_result import (
    DataQuality,
    ForecastDay,
    ForecastSource,
    OfficialAlertsResult,
    RiskQueryResult,
)
from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod, OfficialAlert, RiskAssessment
from climaprev.domain.units import TemperatureUnit
from climaprev.main import create_app, lifespan
from tests.security_fixtures import isolated_settings


class FakeForecastQueryService:
    def __init__(self, result: RiskQueryResult | Exception) -> None:
        self._result = result
        self.calls: list[tuple[ForecastQuery, str]] = []

    async def execute(self, query: ForecastQuery, request_id: str) -> RiskQueryResult:
        self.calls.append((query, request_id))
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class CapturingRateLimiter:
    def __init__(self) -> None:
        self.identities: list[str] = []

    async def allow(
        self,
        identity: str,
        limit: int,
        window_seconds: int,
        burst: int,
    ) -> RateLimitDecision:
        self.identities.append(identity)
        return RateLimitDecision(allowed=True, remaining=burst - 1, retry_after_seconds=0)


def query_result(*, unit: TemperatureUnit = TemperatureUnit.CELSIUS) -> RiskQueryResult:
    period = DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 28))
    return RiskQueryResult(
        request_id="service-request-id",
        location=CanonicalLocation(
            name="Sao Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            timezone="America/Sao_Paulo",
            source="fake-geocoding",
        ),
        period=period,
        temperature_unit=unit,
        days=(
            ForecastDay(
                date=period.start,
                temperature_min=20.0 if unit is TemperatureUnit.CELSIUS else 68.0,
                temperature_max=40.0 if unit is TemperatureUnit.CELSIUS else 104.0,
                temperature_mean=30.0 if unit is TemperatureUnit.CELSIUS else 86.0,
                humidity_mean_pct=70.0,
                precipitation_sum_mm=5.0,
                precipitation_probability_max_pct=40.0,
                precipitation_max_hourly_mm=3.0,
                wind_max_kmh=25.0,
                wind_gust_max_kmh=30.0,
                weather_code=1,
            ),
        ),
        forecast_risk=RiskAssessment(
            level="high",
            method="forecast_heuristic",
            policy_version="reference-v1",
            conditions=(),
        ),
        official_alerts=OfficialAlertsResult(status="not_configured", items=()),
        data_quality=DataQuality(is_stale=False, missing_fields=()),
        source=ForecastSource(provider="fake-open-meteo", fetched_at=datetime(2026, 8, 28, 12, tzinfo=UTC)),
        disclaimer="Forecast estimate only.",
    )


@pytest.mark.asyncio
async def test_router_converts_http_schema_to_application_query() -> None:
    async with app_for() as (client, service, _, _):
        response = await client.get("/api/v1/risk", params=valid_query())

    assert response.status_code == 200
    assert isinstance(service.calls[0][0], ForecastQuery)


@pytest.mark.asyncio
async def test_post_router_converts_json_schema_to_application_query() -> None:
    async with app_for() as (client, service, _, _):
        response = await client.post("/api/v1/risk", json=valid_query())

    assert response.status_code == 200
    assert isinstance(service.calls[0][0], ForecastQuery)
    assert service.calls[0][0].location_text == "Sao Paulo"


@pytest.mark.asyncio
async def test_post_maps_invalid_json_query_to_422_error_envelope() -> None:
    async with app_for() as (client, _, _, _):
        response = await client.post(
            "/api/v1/risk",
            json={"start_date": "2026-08-28"},
            headers={"X-Request-ID": "invalid-post-request"},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_LOCATION_INPUT"
    assert response.json()["error"]["request_id"] == "invalid-post-request"


@pytest.mark.asyncio
async def test_serializes_optional_official_alert_fields_as_null() -> None:
    result = query_result()
    result = replace(
        result,
        official_alerts=OfficialAlertsResult(
            status="available",
            items=(OfficialAlert(
                source="inmet",
                event="rain",
                severity="moderate",
                effective_at=datetime(2026, 8, 28, tzinfo=UTC),
                expires_at=None,
                geographic_scope="Sao Paulo",
                source_url=None,
            ),),
        ),
    )
    async with app_for(result) as (client, _, _, _):
        response = await client.get("/api/v1/risk", params=valid_query())

    assert response.status_code == 200
    alert = response.json()["official_alerts"]["items"][0]
    assert alert["expires_at"] is None
    assert alert["source_url"] is None


@asynccontextmanager
async def app_for(
    result: RiskQueryResult | Exception | None = None,
    *,
    redis_url: str | None = None,
    cors_allow_origins: tuple[str, ...] = (),
    trusted_proxy_ips: tuple[str, ...] = (),
    peer: tuple[str, int] = ("127.0.0.1", 123),
) -> AsyncIterator[tuple[httpx.AsyncClient, FakeForecastQueryService, RequestMetrics, object]]:
    settings = isolated_settings(
        redis_url=redis_url or os.environ["REDIS_URL"],
        cors_allow_origins=cors_allow_origins,
        trusted_proxy_ips=trusted_proxy_ips,
    )
    app = create_app(settings)
    service = FakeForecastQueryService(query_result() if result is None else result)
    app.dependency_overrides[get_forecast_query_service] = lambda: service
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=peer)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client, service, app.state.metrics, app


def valid_query(**overrides: str) -> dict[str, str]:
    return {
        "location_text": "Sao Paulo",
        "start_date": "2026-08-28",
        **overrides,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("day,allowed", [("2026-08-27", False), ("2026-08-28", True),
                                        ("2026-09-03", True), ("2026-09-04", True), ("2026-09-10", True), ("2026-09-11", False)])
async def test_public_forecast_window_prevents_service_calls_outside_bounds(method, day, allowed):
    async with app_for() as (client, service, _, _):
        data = valid_query(start_date=day)
        response = await client.request(method, "/api/v1/risk", **(
            {"params": data} if method == "GET" else {"json": data}))
    assert response.status_code == (200 if allowed else 422)
    assert len(service.calls) == int(allowed)
    if not allowed:
        assert response.json()["error"]["code"] == "INVALID_PERIOD"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("start,end,allowed", [
    ("2026-09-04", "2026-09-10", True),
    ("2026-08-28", "2026-09-04", False),
    ("2026-09-05", "2026-09-11", False),
])
async def test_second_week_period_is_limited_to_seven_dates_and_propagated(method, start, end, allowed):
    async with app_for() as (client, service, _, _):
        data = valid_query(start_date=start, end_date=end)
        response = await client.request(method, "/api/v1/risk", **(
            {"params": data} if method == "GET" else {"json": data}))
    assert response.status_code == (200 if allowed else 422)
    assert len(service.calls) == int(allowed)
    if allowed:
        assert service.calls[0][0].start_date == date.fromisoformat(start)
        assert service.calls[0][0].end_date == date.fromisoformat(end)


@pytest.mark.asyncio
async def test_returns_complete_celsius_risk_contract_and_propagates_request_id() -> None:
    async with app_for() as (client, service, metrics, _):
        response = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Request-ID": "request-123"},
        )

    assert response.status_code == 200, response.text
    assert response.headers["x-request-id"] == "request-123"
    assert response.json() == {
        "request_id": "request-123",
        "location": {
            "name": "Sao Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "timezone": "America/Sao_Paulo",
            "source": "fake-geocoding",
        },
        "period": {"start_date": "2026-08-28", "end_date": "2026-08-28"},
        "temperature_unit": "celsius",
        "days": [
            {
                "date": "2026-08-28",
                "temperature_min": 20.0,
                "temperature_max": 40.0,
                "temperature_mean": 30.0,
                "humidity_mean_pct": 70.0,
                "precipitation_sum_mm": 5.0,
                "precipitation_probability_max_pct": 40.0,
                "precipitation_max_hourly_mm": 3.0,
                "wind_max_kmh": 25.0,
                "wind_gust_max_kmh": 30.0,
                "weather_code": 1,
            }
        ],
        "forecast_risk": {
            "level": "high",
            "method": "forecast_heuristic",
            "policy_version": "reference-v1",
            "conditions": [],
            "peak_days": [],
            "daily": [],
        },
        "risk_overview": {"level": "high", "source": "forecast_heuristic", "peak_days": []},
        "official_alerts": {"status": "not_configured", "items": []},
        "data_quality": {"is_stale": False, "missing_fields": [], "completeness": "complete"},
        "source": {"provider": "fake-open-meteo", "fetched_at": "2026-08-28T12:00:00Z"},
        "disclaimer": "Forecast estimate only.",
    }
    assert service.calls[0][1] == "request-123"
    snapshot = metrics.snapshot()
    assert snapshot["request_latency_ms_count"] == 1
    assert snapshot["cache_misses_total"] == 1
    assert snapshot["upstream_errors_total"] == 0
    assert snapshot["upstream_retries_total"] == 0


@pytest.mark.asyncio
async def test_returns_fahrenheit_and_accepts_coordinate_query() -> None:
    async with app_for(query_result(unit=TemperatureUnit.FAHRENHEIT)) as (client, service, _, _):
        response = await client.get(
            "/api/v1/risk",
            params={
                "latitude": "-23.5505",
                "longitude": "-46.6333",
                "start_date": "2026-08-28",
                "temperature_unit": "fahrenheit",
            },
        )

    assert response.status_code == 200
    assert response.json()["temperature_unit"] == "fahrenheit"
    assert response.json()["days"][0]["temperature_max"] == 104.0
    query = service.calls[0][0]
    assert query.location_text is None
    assert query.latitude == -23.5505


@pytest.mark.parametrize(
    ("params", "code"),
    [
        ({"start_date": "2026-08-28"}, "INVALID_LOCATION_INPUT"),
        (valid_query(end_date="2026-08-27"), "INVALID_PERIOD"),
        (valid_query(temperature_unit="kelvin"), "INVALID_TEMPERATURE_UNIT"),
    ],
)
@pytest.mark.asyncio
async def test_maps_invalid_query_to_422_error_envelope(params: dict[str, str], code: str) -> None:
    async with app_for() as (client, _, _, _):
        response = await client.get(
            "/api/v1/risk",
            params=params,
            headers={"X-Request-ID": "invalid-request"},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["request_id"] == "invalid-request"


@pytest.mark.parametrize(
    ("error", "status", "code"),
    [
        (LocationNotFound("missing"), 404, "LOCATION_NOT_FOUND"),
        (WeatherDataInvalid("invalid"), 502, "WEATHER_DATA_INVALID"),
        (ProviderTransientError("down"), 503, "WEATHER_PROVIDER_UNAVAILABLE"),
        (WeatherProviderUnavailable("down"), 503, "WEATHER_PROVIDER_UNAVAILABLE"),
        (DependencyUnavailable(), 503, "DEPENDENCY_UNAVAILABLE"),
        (RuntimeError("secret internal details"), 500, "INTERNAL_ERROR"),
    ],
)
@pytest.mark.asyncio
async def test_maps_service_failures_to_safe_error_envelopes(
    error: Exception,
    status: int,
    code: str,
) -> None:
    async with app_for(error) as (client, _, metrics, _):
        response = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Request-ID": "error-request"},
        )

    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["request_id"] == "error-request"
    assert "secret internal details" not in response.text
    if code == "WEATHER_PROVIDER_UNAVAILABLE":
        assert metrics.snapshot()["upstream_errors_total"] == 1


@pytest.mark.asyncio
async def test_maps_input_application_error_to_422_error_envelope() -> None:
    async with app_for(
        ApplicationError(
            code="INVALID_PERIOD",
            message="end_date must not be before start_date",
            status_code=422,
        )
    ) as (client, _, _, _):
        response = await client.get("/api/v1/risk", params=valid_query())

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_PERIOD"


@pytest.mark.asyncio
async def test_rate_limit_is_enforced_per_client_ip_with_real_redis() -> None:
    async with app_for() as (client, _, metrics, _):
        responses = [await client.get("/api/v1/risk", params=valid_query()) for _ in range(11)]

    assert [response.status_code for response in responses].count(200) == 10
    denied = responses[-1]
    assert denied.status_code == 429
    assert denied.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert denied.headers["retry-after"] == "1"
    assert metrics.snapshot()["rate_limit_exceeded_total"] == 1


@pytest.mark.asyncio
async def test_generates_safe_request_id_when_header_is_unsafe() -> None:
    async with app_for() as (client, _, _, _):
        response = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Request-ID": "unsafe\nvalue"},
        )

    assert response.status_code == 200
    generated = response.headers["x-request-id"]
    assert response.json()["request_id"] == generated
    assert generated != "unsafe\nvalue"
    assert len(generated) == 32


@pytest.mark.asyncio
async def test_live_does_not_require_redis_and_ready_requires_redis() -> None:
    async with app_for(redis_url="redis://redis:6399/0") as (client, _, _, _):
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "live"}
    assert ready.status_code == 503
    assert ready.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"


@pytest.mark.asyncio
async def test_ready_uses_real_redis() -> None:
    async with app_for() as (client, _, _, _):
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_cors_uses_configured_allowlist() -> None:
    async with app_for(cors_allow_origins=("https://console.example",)) as (client, _, _, _):
        allowed = await client.options(
            "/api/v1/risk",
            headers={
                "Origin": "https://console.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        allowed_post = await client.options(
            "/api/v1/risk",
            headers={
                "Origin": "https://console.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-request-id",
            },
        )
        denied = await client.options(
            "/api/v1/risk",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        actual = await client.get("/health/live", headers={"Origin": "https://console.example"})

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "https://console.example"
    assert allowed_post.status_code == 200
    assert allowed_post.headers["access-control-allow-origin"] == "https://console.example"
    assert "content-type" in allowed_post.headers["access-control-allow-headers"].lower()
    assert actual.headers["access-control-expose-headers"] == "X-Request-ID, Retry-After"
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


@pytest.mark.asyncio
async def test_rejects_location_text_over_the_public_input_limit() -> None:
    async with app_for() as (client, _, _, _):
        response = await client.get(
            "/api/v1/risk",
            params=valid_query(location_text="a" * 201),
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_LOCATION_INPUT"


@pytest.mark.asyncio
async def test_uses_only_a_valid_trusted_forwarded_chain_for_rate_limit_identity() -> None:
    async with app_for(
        trusted_proxy_ips=("10.0.0.1", "10.0.0.2"),
        peer=("10.0.0.2", 123),
    ) as (client, _, _, app):
        limiter = CapturingRateLimiter()
        app.dependency_overrides[get_rate_limiter] = lambda: limiter
        trusted = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Forwarded-For": "198.51.100.7, 10.0.0.1"},
        )
        spoofed = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Forwarded-For": "198.51.100.8, not-an-ip"},
        )

    assert trusted.status_code == 200
    assert spoofed.status_code == 200
    assert limiter.identities == ["198.51.100.7", "10.0.0.2"]


def test_settings_accept_csv_or_json_lists_and_reject_wildcard_in_any_production_case(
    monkeypatch: pytest.MonkeyPatch,
    production_config,
) -> None:
    monkeypatch.setenv("CLIMAPREV_CORS_ALLOW_ORIGINS", "https://console.example,https://ops.example")
    monkeypatch.setenv("CLIMAPREV_TRUSTED_PROXY_IPS", '["10.0.0.1", "2001:db8::1"]')
    settings = Settings(environment="Production", **production_config)

    assert settings.environment == "production"
    assert settings.cors_allow_origins == ("https://console.example", "https://ops.example")
    assert settings.trusted_proxy_ips == ("10.0.0.1", "2001:db8::1")

    with pytest.raises(ValueError, match="wildcard"):
        Settings(environment="PRODUCTION", cors_allow_origins=("*",), **production_config)


@pytest.mark.asyncio
async def test_request_log_is_structured_and_omits_location_text(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="climaprev.request")
    async with app_for() as (client, _, _, _):
        response = await client.get(
            "/api/v1/risk",
            params=valid_query(location_text="Sensitive Town"),
            headers={"X-Request-ID": "log-request"},
        )

    assert response.status_code == 200
    record = json.loads(caplog.records[-1].message)
    assert record["route"] == "/api/v1/risk"
    assert record["status"] == 200
    assert record["request_id"] == "log-request"
    assert "Sensitive Town" not in caplog.records[-1].message


@pytest.mark.asyncio
async def test_lifespan_closes_http_client_when_redis_creation_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ClosingHttpClient:
        def __init__(self, *args, **kwargs) -> None:
            self.closed = False
            self.args = args
            self.kwargs = kwargs

        async def aclose(self) -> None:
            self.closed = True

    http_client = ClosingHttpClient()
    def fake_async_client(*args, **kwargs):
        http_client.args = args
        http_client.kwargs = kwargs
        return http_client

    settings = isolated_settings(redis_url=os.environ["REDIS_URL"])
    app = create_app(settings)
    monkeypatch.setattr(
        "climaprev.main.httpx.AsyncClient", fake_async_client
    )
    monkeypatch.setattr(
        "climaprev.main.Redis.from_url",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("redis construction failed")),
    )

    with pytest.raises(RuntimeError, match="redis construction failed"):
        async with lifespan(app):
            pass

    assert http_client.closed is True
    assert http_client.kwargs["follow_redirects"] is False
    assert http_client.kwargs["trust_env"] is False
    assert http_client.kwargs["limits"].max_connections == settings.http_max_connections
    assert (
        http_client.kwargs["limits"].max_keepalive_connections
        == settings.http_max_keepalive_connections
    )
    timeout = http_client.kwargs["timeout"]
    assert timeout.connect == settings.connect_timeout_seconds
    assert timeout.read == settings.read_timeout_seconds
    assert timeout.write == settings.read_timeout_seconds
    assert timeout.pool == settings.connect_timeout_seconds
