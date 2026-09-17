import json
import socket
from pathlib import Path

from climaprev.log_collector import CLEANUP_SECONDS, RETENTION_SECONDS, LogStore, receive_once


def record(identity="proof", **extra):
    return json.dumps(
        {
            "event": "request_completed",
            "request_id": identity,
            "route": "/api/v1/risk",
            "status": 200,
            "latency_ms": 3,
            **extra,
        }
    ).encode()


def test_expiry_is_bounded_by_seven_days_and_does_not_refresh_on_read(tmp_path: Path) -> None:
    clock = [3600.0]
    store = LogStore(tmp_path, clock=lambda: clock[0])
    store.append(record())
    path = next(tmp_path.glob("*.jsonl"))
    clock[0] += RETENTION_SECONDS - CLEANUP_SECONDS - 1
    store.prune()
    assert path.exists()
    assert json.loads(path.read_text())["request_id"] == "proof"
    clock[0] += 1
    store.prune()
    assert not path.exists()


def test_idle_receive_timeout_still_expires_logs(tmp_path: Path) -> None:
    clock = [3600.0]
    store = LogStore(tmp_path / "logs", clock=lambda: clock[0])
    store.append(record())
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as server:
        server.bind(str(tmp_path / "socket"))
        server.settimeout(0.01)
        clock[0] += RETENTION_SECONDS
        receive_once(server, store)
    assert list((tmp_path / "logs").glob("*.jsonl")) == []


def test_restart_prunes_before_accepting_new_records(tmp_path: Path) -> None:
    LogStore(tmp_path, clock=lambda: 3600.0).append(record("old"))
    restarted = LogStore(tmp_path, clock=lambda: 3600.0 + RETENTION_SECONDS)
    assert list(tmp_path.glob("*.jsonl")) == []
    restarted.append(record("new"))
    assert json.loads(next(tmp_path.glob("*.jsonl")).read_text())["request_id"] == "new"


def test_socket_input_keeps_only_allowed_fields_and_normalized_routes(tmp_path: Path) -> None:
    store = LogStore(tmp_path, clock=lambda: 3600.0)
    store.append(
        record(
            route="/PrivatePath",
            query="PrivateQuery",
            ip="198.51.100.99",
            token="PrivateToken",
            payload={"value": "PrivatePayload"},
        )
    )
    content = next(tmp_path.glob("*.jsonl")).read_text()
    for private in (
        "PrivatePath",
        "PrivateQuery",
        "198.51.100.99",
        "PrivateToken",
        "PrivatePayload",
    ):
        assert private not in content
    saved = json.loads(content)
    assert saved["route"] == "unmatched"
    assert set(saved) == {"event", "request_id", "route", "status", "latency_ms", "recorded_at"}
    assert saved["status"] == 200 and saved["latency_ms"] == 3


def test_invalid_and_oversized_socket_records_are_not_persisted(tmp_path: Path) -> None:
    store = LogStore(tmp_path, clock=lambda: 3600.0)
    for raw in (
        b"not-json",
        b"x" * 8193,
        record(status=True),
        record(latency_ms=float("nan")),
        record(identity="invalid\nID"),
    ):
        store.append(raw)
    assert list(tmp_path.glob("*.jsonl")) == []


def test_hourly_size_bound_keeps_latest_complete_records(tmp_path: Path) -> None:
    store = LogStore(tmp_path, clock=lambda: 3600.0, max_file_bytes=512)
    for number in range(20):
        store.append(record(f"proof-{number}"))
    path = next(tmp_path.glob("*.jsonl"))
    assert path.stat().st_size <= 512
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert rows[-1]["request_id"] == "proof-19"
    assert rows[0]["request_id"] != "proof-0"
