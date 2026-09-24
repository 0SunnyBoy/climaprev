import json

from tests.integration.api.test_risk_endpoint import app_for


async def test_thousand_unknown_paths_have_one_unmatched_dimension() -> None:
    async with app_for() as (client, _, metrics, _):
        for number in range(1000):
            response = await client.get(f"/unknown-{number}")
            assert response.status_code == 404
    assert metrics.snapshot()["http_requests_total"] == {"GET|unmatched|404": 1000}


async def test_known_routes_keep_separate_dimensions() -> None:
    async with app_for() as (client, _, metrics, _):
        await client.get("/health/live")
        await client.get("/health/ready")
        await client.get("/api/v1/risk")
    assert metrics.snapshot()["http_requests_total"] == {
        "GET|/health/live|200": 1,
        "GET|/health/ready|200": 1,
        "GET|/api/v1/risk|422": 1,
    }


async def test_query_ip_and_arbitrary_path_never_become_dimensions() -> None:
    async with app_for() as (client, _, metrics, _):
        await client.get(
            "/UnknownSentinel",
            params={"q": "QuerySentinel"},
            headers={"X-Forwarded-For": "198.51.100.99"},
        )
    snapshot = json.dumps(metrics.snapshot())
    assert "UnknownSentinel" not in snapshot
    assert "QuerySentinel" not in snapshot
    assert "198.51.100.99" not in snapshot
    assert metrics.snapshot()["http_requests_total"] == {"GET|unmatched|404": 1}
