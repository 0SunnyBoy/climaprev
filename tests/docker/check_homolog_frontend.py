"""Host-side smoke checks for the homologation frontend boundary."""

import argparse
import json
import re
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.homolog.yml"
ENV_FILE = ROOT / ".homolog" / "compose.env"
DEFAULT_CA_FILE = ROOT / ".homolog" / "ca.crt"


def compose(*args: str, env_file: Path | None = ENV_FILE) -> None:
    command = ["docker", "compose"]
    if env_file is not None:
        command.extend(["--env-file", str(env_file)])
    result = subprocess.run(
        [*command, "-f", str(COMPOSE_FILE), *args],
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


def check(
    port: int, ca_file: Path = DEFAULT_CA_FILE, env_file: Path | None = ENV_FILE
) -> None:
    base = f"https://localhost:{port}"
    context = ssl.create_default_context(cafile=str(ca_file))

    status, body, headers = request(f"{base}/", context)
    assert status == 200
    assert content_type(headers) == "text/html"
    assert "<!doctype html>" in body.lower()

    assets = re.findall(r"(?:href|src)=\"(/assets/[^\"]+)\"", body)
    assert any(asset.endswith(".css") for asset in assets)
    assert any(asset.endswith(".js") for asset in assets)
    for path in assets:
        status, body, headers = request(f"{base}{path}", context)
        assert status == 200
        assert content_type(headers) in {"text/css", "application/javascript"}
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

    compose("exec", "-T", "entrada", "nginx", "-t", env_file=env_file)
    print("Homolog frontend smoke: page/assets/API/health/internal boundary/nginx config OK.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18443)
    parser.add_argument("--ca-file", type=Path, default=DEFAULT_CA_FILE)
    parser.add_argument("--env-file", type=Path, default=ENV_FILE)
    parser.add_argument("--use-process-env", action="store_true")
    args = parser.parse_args()
    check(args.port, args.ca_file, None if args.use_process_env else args.env_file)
