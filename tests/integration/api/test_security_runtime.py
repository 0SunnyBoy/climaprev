"""HTTP-01, SEC-01, AUTH-01 runtime boundaries with synthetic secrets."""

import httpx
import pytest
import respx

from climaprev.config import Settings
from climaprev.main import create_app
from tests.integration.api.test_risk_endpoint import app_for, valid_query
from tests.integration.providers.test_http_bounds import Stream
from tests.integration.test_evolution_data import PARAMS
from tests.security_fixtures import isolated_settings


@pytest.mark.parametrize("host,status", [("app", 200), ("localhost", 200), ("127.0.0.1", 200),
                                         ("testserver", 200), ("forged.example", 400)])
async def test_production_host_validation_and_anonymous_health(production_config, host, status):
    app = create_app(Settings(environment="production", **production_config))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=f"http://{host}") as client:
        response = await client.get("/health/live")
    assert response.status_code == status
    if status == 200:
        assert response.json() == {"status": "live"}
    else:
        assert response.text == "Invalid host header"
    assert "SyntheticRedisPasswordForTests" not in response.text
    assert "ab" * 32 not in response.text


async def test_lifespan_uses_shared_hmac_secret_and_has_no_cors_by_default():
    async with app_for() as (client, _, _, app):
        response = await client.get("/api/v1/risk", params=valid_query(),
                                    headers={"Origin": "https://untrusted.example"})
        stored = app.state.rate_limiter._redis_key("127.0.0.1")
        assert await app.state.redis.exists(stored) == 1
        assert stored.startswith("climaprev:test:rate-limit:v2:")
        assert "127.0.0.1" not in stored
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
    assert "set-cookie" not in response.headers


async def test_equivalent_ipv6_from_proxy_keeps_one_quota():
    async with app_for(trusted_proxy_ips=("10.0.0.2",), peer=("10.0.0.2", 443)) as (client, _, _, _):
        for _ in range(10):
            response = await client.get("/api/v1/risk", params=valid_query(),
                                        headers={"X-Forwarded-For": "2001:db8::7"})
            assert response.status_code == 200
        blocked = await client.get("/api/v1/risk", params=valid_query(),
                                    headers={"X-Forwarded-For": "2001:0db8:0:0:0:0:0:7"})
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "1"


@pytest.mark.parametrize("kind,status,code", [
    ("oversized", 502, "WEATHER_PROVIDER_REJECTED"),
    ("redirect", 502, "WEATHER_PROVIDER_REJECTED"),
    ("deadline", 503, "WEATHER_PROVIDER_UNAVAILABLE"),
])
async def test_resource_failures_keep_sanitized_api_envelopes(kind, status, code):
    settings = isolated_settings(provider_max_response_bytes=10, provider_total_timeout_seconds=0.03)
    app = create_app(settings)
    stream = Stream([b"SensitiveProviderBody"], delay=1 if kind == "deadline" else 0)
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client, respx.mock as mock:
        upstream = mock.get(settings.forecast_base_url + "/v1/forecast").mock(
            return_value=httpx.Response(302 if kind == "redirect" else 200, stream=stream,
                                       headers={"Location": "https://forbidden.test"})
        )
        response = await client.get("/api/v1/risk", params=PARAMS)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert "SensitiveProviderBody" not in response.text
    assert settings.forecast_base_url not in response.text
    assert upstream.call_count == 1
    assert stream.closed


async def test_runtime_does_not_consult_ambient_proxy_configuration(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "invalid-proxy-sentinel")
    monkeypatch.setenv("HTTPS_PROXY", "invalid-proxy-sentinel")
    monkeypatch.setenv("ALL_PROXY", "invalid-proxy-sentinel")
    app = create_app(isolated_settings())
    # HTTPX raises during construction if trust_env=True with these proxy URLs.
    async with app.router.lifespan_context(app):
        assert await app.state.redis.ping() is True
