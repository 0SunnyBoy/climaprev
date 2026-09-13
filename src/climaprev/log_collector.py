"""Bounded local JSON log collection over a private Unix datagram socket."""

from __future__ import annotations

import json
import math
import re
import socket
import stat
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

RETENTION_SECONDS = 7 * 24 * 60 * 60
CLEANUP_SECONDS = 60
SOCKET_PATH = Path("/run/climaprev-logs/request.sock")
LOG_DIRECTORY = Path("/var/log/climaprev")
_ROUTES = {
    "/",
    "/api/v1/risk",
    "/health/live",
    "/health/ready",
    "/internal/metrics",
    "/internal/*",
    "/assets",
    "/assets/*",
    "unmatched",
}
_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class LogStore:
    def __init__(
        self,
        directory: Path,
        *,
        clock: Callable[[], float] = time.time,
        max_file_bytes: int = 1024 * 1024,
    ) -> None:
        self.directory = directory
        self.clock = clock
        self.max_file_bytes = max_file_bytes
        directory.mkdir(parents=True, exist_ok=True)
        self.prune()

    def prune(self) -> None:
        # Start one cleanup interval early so hourly files never exceed seven days
        # while the collector is running, including when no traffic is received.
        cutoff = self.clock() - RETENTION_SECONDS + CLEANUP_SECONDS
        for path in self.directory.glob("*.jsonl"):
            if path.stem.isdigit() and int(path.stem) <= cutoff:
                path.unlink(missing_ok=True)

    def append(self, raw: bytes) -> None:
        if len(raw) > 8192:
            return
        try:
            # Accept the fixed syslog transport prefix used by app and nginx.
            message = json.loads(raw[raw.index(b"{") :].rstrip(b"\x00"))
            if not isinstance(message, dict):
                return
            event = message.get("event")
            identity = message.get("request_id")
            status = message.get("status")
            latency = message.get("latency_ms")
            if event == "entry_completed":
                latency = float(message["duration_seconds"]) * 1000
            if (
                event not in ("request_completed", "entry_completed")
                or not isinstance(identity, str)
                or _REQUEST_ID.fullmatch(identity) is None
                or type(status) is not int
                or not 100 <= status <= 599
                or not isinstance(latency, (int, float))
                or isinstance(latency, bool)
                or not math.isfinite(latency)
                or latency < 0
            ):
                return
        except (ValueError, TypeError, KeyError):
            return
        now = self.clock()
        route = message.get("route")
        saved = {
            "event": event,
            "request_id": identity,
            "route": route if isinstance(route, str) and route in _ROUTES else "unmatched",
            "status": status,
            "latency_ms": round(latency, 2),
            "recorded_at": datetime.fromtimestamp(now, UTC).isoformat(),
        }
        path = self.directory / f"{int(now) // 3600 * 3600}.jsonl"
        with path.open("ab") as output:
            output.write(json.dumps(saved, separators=(",", ":")).encode() + b"\n")
        if path.stat().st_size > self.max_file_bytes:
            tail = path.read_bytes()[-self.max_file_bytes :]
            path.write_bytes(tail[tail.find(b"\n") + 1 :])


def receive_once(server: socket.socket, store: LogStore) -> None:
    try:
        store.append(server.recv(8193))
    except TimeoutError:
        pass
    finally:
        store.prune()


def main() -> None:
    if "--check" in sys.argv:
        raise SystemExit(
            0 if SOCKET_PATH.exists() and stat.S_ISSOCK(SOCKET_PATH.stat().st_mode) else 1
        )
    store = LogStore(LOG_DIRECTORY)
    SOCKET_PATH.unlink(missing_ok=True)
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as server:
        server.bind(str(SOCKET_PATH))
        SOCKET_PATH.chmod(0o666)
        server.settimeout(CLEANUP_SECONDS)
        while True:
            receive_once(server, store)


if __name__ == "__main__":
    main()
