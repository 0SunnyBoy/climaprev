import json
import subprocess
import sys
import time

import httpx
import pytest


@pytest.mark.parametrize("channel", ["query", "ip", "token", "payload"])
def test_real_runtime_emits_only_sanitized_request_metadata(channel: str) -> None:
    sentinel = "SentinelPrivate" + channel
    process = subprocess.Popen(
        [sys.executable, "-m", "climaprev.runtime"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        with httpx.Client(base_url="http://127.0.0.1:8000") as client:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                assert process.poll() is None, "runtime exited before readiness"
                try:
                    if client.get("/health/live").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                time.sleep(0.05)
            else:
                pytest.fail("runtime did not become live within 10 seconds")
            headers = {"X-Request-ID": "log-proof"}
            if channel == "ip":
                headers["X-Forwarded-For"] = "198.51.100.99"
            if channel == "token":
                headers["Authorization"] = "Bearer " + sentinel
            response = client.request(
                "GET",
                "/api/v1/risk",
                params={"location_text": sentinel},
                headers=headers,
                content=sentinel if channel == "payload" else b"",
            )
            assert response.status_code == 422
    finally:
        process.terminate()
        output, _ = process.communicate(timeout=5)
    assert sentinel not in output
    assert "198.51.100.99" not in output
    assert "127.0.0.1" not in output
    records = [json.loads(line) for line in output.splitlines()]
    record = next(record for record in records if record["request_id"] == "log-proof")
    assert record["status"] == 422
    assert record["route"] == "/api/v1/risk"
    assert record["latency_ms"] >= 0
    assert set(record) == {
        "event",
        "route",
        "status",
        "latency_ms",
        "cache",
        "provider",
        "retries",
        "error_code",
        "request_id",
    }
