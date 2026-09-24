import json
import logging

import pytest
import respx

from tests.integration.api.test_risk_endpoint import app_for, valid_query
from tests.integration.test_end_to_end import end_to_end_client


async def test_unexpected_failure_has_sanitized_500_log_and_metrics(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="climaprev.request")
    async with app_for(RuntimeError("PrivateExceptionSentinel")) as (client, _, metrics, _):
        response = await client.get(
            "/api/v1/risk", params=valid_query(), headers={"X-Request-ID": "failure-proof"}
        )
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert response.headers["x-request-id"] == "failure-proof"
    assert response.json()["error"]["request_id"] == "failure-proof"
    records = [
        json.loads(item.message) for item in caplog.records if item.name == "climaprev.request"
    ]
    assert records[-1]["request_id"] == "failure-proof"
    assert records[-1]["status"] == 500
    assert records[-1]["route"] == "/api/v1/risk"
    assert records[-1]["latency_ms"] >= 0
    assert "PrivateExceptionSentinel" not in caplog.text + response.text
    assert metrics.snapshot()["server_errors_total"] == 1


async def test_real_upstream_body_never_appears_in_failure_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="climaprev.request")
    async with end_to_end_client() as (client, app):
        with respx.mock as mock:
            mock.get(app.state.settings.forecast_base_url + "/v1/forecast").respond(
                400, json={"payload": "PrivateUpstreamSentinel"}
            )
            response = await client.get(
                "/api/v1/risk",
                params={"latitude": "-22", "longitude": "-43", "start_date": "2026-08-28"},
                headers={"X-Request-ID": "upstream-proof"},
            )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "WEATHER_PROVIDER_REJECTED"
    records = [
        json.loads(item.message) for item in caplog.records if item.name == "climaprev.request"
    ]
    assert records[-1]["request_id"] == "upstream-proof"
    assert records[-1]["status"] == 502
    assert records[-1]["latency_ms"] >= 0
    assert "PrivateUpstreamSentinel" not in caplog.text + response.text
