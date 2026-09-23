"""Host-side checks against the real local TLS entrance; no trust bypass."""

import argparse
import json
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4


def docker(*args: str) -> str:
    return subprocess.check_output(["docker", *args], text=True)


def request(url: str, context: ssl.SSLContext, *, identity: str = "tls-proof"):
    query = urllib.request.Request(
        url,
        method="GET",
        data=b"PrivatePayloadSentinel",
        headers={
            "Authorization": "Bearer PrivateTokenSentinel",
            "X-Forwarded-For": "198.51.100.99",
            "X-Request-ID": identity,
        },
    )
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


def logs():
    code = (
        "from pathlib import Path; import json; "
        "print(json.dumps([json.loads(line) for p in Path('/var/log/climaprev').glob('*.jsonl') "
        "for line in p.read_text().splitlines()]))"
    )
    return json.loads(docker("exec", "climaprev-homolog-collector-1", "python", "-c", code))


def check(
    port: int,
    ca_file: Path = Path(".homolog/ca.crt"),
    env_file: Path | None = Path(".homolog/compose.env"),
) -> None:
    base = f"https://localhost:{port}"
    proof_id = "public-" + uuid4().hex
    restart_id = "restart-" + uuid4().hex
    rejected = False
    try:
        urllib.request.urlopen(base + "/health/live", timeout=5)
    except urllib.error.URLError as error:
        rejected = isinstance(error.reason, ssl.SSLCertVerificationError)
    assert rejected
    context = ssl.create_default_context(cafile=str(ca_file))
    status, body, _ = request(base + "/health/live", context)
    assert status == 200 and json.loads(body) == {"status": "live"}
    for path in ("/internal", "/internal/metrics", "/%69nternal/metrics", "//internal/metrics"):
        status, body, _ = request(base + path, context)
        assert status == 404
        assert "instance_id" not in body
    code = (
        "import urllib.request; "
        "print(urllib.request.urlopen('http://localhost:8000/internal/metrics').read().decode())"
    )
    snapshot = json.loads(docker("exec", "climaprev-homolog-app-1", "python", "-c", code))
    assert snapshot["pid"] > 0 and len(snapshot["instance_id"]) == 32
    assert "http_requests_total" in snapshot
    status, _, headers = request(
        base + "/api/v1/risk?location_text=PrivateLocationSentinel",
        context,
        identity=proof_id,
    )
    assert status == 422
    assert headers["x-request-id"] == proof_id
    records = []
    for _ in range(20):
        records = logs()
        paired = [row for row in records if row["request_id"] == proof_id]
        if {row["event"] for row in paired} == {"request_completed", "entry_completed"}:
            break
        time.sleep(0.1)
    assert {row["event"] for row in paired} == {"request_completed", "entry_completed"}
    assert all(row["status"] == 422 and row["route"] == "/api/v1/risk" for row in paired)
    assert all(row["latency_ms"] >= 0 for row in paired)
    serialized = json.dumps(records)
    for sentinel in (
        "PrivatePayloadSentinel",
        "PrivateTokenSentinel",
        "PrivateLocationSentinel",
        "198.51.100.99",
        "127.0.0.1",
    ):
        assert sentinel not in serialized
    for service in ("app", "redis", "collector", "entrada"):
        driver = docker(
            "inspect",
            f"climaprev-homolog-{service}-1",
            "--format",
            "{{.HostConfig.LogConfig.Type}}",
        ).strip()
        assert driver == "none"
    code = "from pathlib import Path; Path('/var/log/climaprev/0.jsonl').write_text('{}\\n')"
    docker("exec", "climaprev-homolog-collector-1", "python", "-c", code)
    compose_args = ["compose"]
    if env_file is not None:
        compose_args.extend(["--env-file", str(env_file)])
    docker(*compose_args, "-f", "docker-compose.homolog.yml", "restart", "collector")
    for _ in range(30):
        state = docker(
            "inspect", "climaprev-homolog-collector-1", "--format", "{{.State.Health.Status}}"
        ).strip()
        if state == "healthy":
            break
        time.sleep(0.2)
    code = "from pathlib import Path; assert not Path('/var/log/climaprev/0.jsonl').exists()"
    docker("exec", "climaprev-homolog-collector-1", "python", "-c", code)
    # Confirm both senders reconnect after the collector's socket is recreated.
    for _ in range(20):
        request(base + "/health/live", context, identity=restart_id)
        events = {row["event"] for row in logs() if row["request_id"] == restart_id}
        if events == {"request_completed", "entry_completed"}:
            break
        time.sleep(0.1)
    assert events == {"request_completed", "entry_completed"}
    print(
        "TLS CA accepted/untrusted CA rejected; internal routes hidden; internal snapshot accessible; "
        "app/entrance logs sanitized; engine logging disabled; expired log removed on restart; senders recovered."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18443)
    parser.add_argument("--ca-file", type=Path, default=Path(".homolog/ca.crt"))
    parser.add_argument("--env-file", type=Path, default=Path(".homolog/compose.env"))
    parser.add_argument("--use-process-env", action="store_true")
    args = parser.parse_args()
    check(args.port, args.ca_file, None if args.use_process_env else args.env_file)
