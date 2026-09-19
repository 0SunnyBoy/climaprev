#!/usr/bin/env python3
"""Host-side smoke checks for the homologation frontend boundary."""

import argparse
import json
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.homolog.yml"
ENV_FILE = ROOT / ".homolog" / "compose.env"
CA_FILE = ROOT / ".homolog" / "ca.crt"


def compose(*args: str) -> None:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            str(ENV_FILE),
            "-f",
            str(COMPOSE_FILE),
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        raise AssertionError(f"Compose command failed: {' '.join(args)}\n{details}")


def request(url: str, context: ssl.SSLContext, *, identity: str | None = None):
    headers = {"Accept": "application/json, text/html, text/css, application/javascript"}
    if identity:
        headers["X-Request-ID"] = identity
    query = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(query, context=context, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return (
            response.status,
            response.read().decode(),
            {key.lower(): value for key, value in response.headers.items()},
        )


def content_type(headers: dict[str, str]) -> str:
    return headers.get("content-type", "").split(";", 1)[0].lower()


def check(port: int) -> None:
    base = f"https://localhost:{port}"
    context = ssl.create_default_context(cafile=str(CA_FILE))

    status, body, headers = request(f"{base}/", context)
    assert status == 200
    assert content_type(headers) == "text/html"
    assert "<!doctype html>" in body.lower()

    for path, expected_type in (
        ("/assets/styles.css", "text/css"),
        ("/assets/app.js", "application/javascript"),
    ):
        status, body, headers = request(f"{base}{path}", context)
        assert status == 200
        assert content_type(headers) == expected_type
        assert body

    status, body, headers = request(f"{base}/health/live", context)
    assert status == 200
    assert json.loads(body) == {"status": "live"}

    request_id = "smoke-" + uuid4().hex
    status, body, headers = request(
        f"{base}/api/v1/risk", context, identity=request_id
    )
    assert status == 422
    assert "error" in json.loads(body)
    assert headers["x-request-id"] == request_id

    for path in ("/internal", "/internal/metrics", "/%69nternal/metrics"):
        status, _, _ = request(f"{base}{path}", context)
        assert status == 404

    status, _, _ = request(f"{base}/__climaprev_smoke_unknown__", context)
    assert status == 404

    compose("exec", "-T", "entrada", "nginx", "-t")
    print("Homolog frontend smoke: page/assets/API/health/internal boundary/nginx config OK.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18443)
    check(parser.parse_args().port)
