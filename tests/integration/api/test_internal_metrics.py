import json
import os
import subprocess
import sys
from datetime import UTC, datetime

from tests.integration.api.test_risk_endpoint import app_for


async def test_internal_snapshot_exposes_process_identity_and_existing_counters() -> None:
    before = datetime.now(UTC)
    async with app_for() as (client, _, _, _):
        await client.get("/health/live")
        response = await client.get("/internal/metrics")
    payload = response.json()
    assert response.status_code == 200
    assert len(payload["instance_id"]) == 32
    assert payload["pid"] == os.getpid()
    assert before <= datetime.fromisoformat(payload["started_at"]) <= datetime.now(UTC)
    assert payload["http_requests_total"] == {"GET|/health/live|200": 1}
    assert payload["requests_total"] == 1


async def test_restart_has_distinct_identity_and_no_previous_counters() -> None:
    code = "from climaprev.api.observability import RequestMetrics; import json; print(json.dumps(RequestMetrics().snapshot()))"
    first = json.loads(subprocess.check_output([sys.executable, "-c", code], text=True))
    second = json.loads(subprocess.check_output([sys.executable, "-c", code], text=True))
    assert first["pid"] != second["pid"]
    assert first["instance_id"] != second["instance_id"]
    assert first["requests_total"] == second["requests_total"] == 0


async def test_internal_snapshot_omits_inputs_settings_and_secrets() -> None:
    async with app_for() as (client, _, _, _):
        await client.get(
            "/PrivatePath",
            params={"query": "PrivateQuery"},
            headers={"Authorization": "Bearer PrivateToken", "X-Request-ID": "PrivateID"},
        )
        response = await client.get("/internal/metrics")
    assert response.status_code == 200
    for sentinel in ("PrivatePath", "PrivateQuery", "PrivateToken", "PrivateID", "redis://"):
        assert sentinel not in response.text
    assert "settings" not in response.json()
    assert "environment" not in response.json()
