"""Bounded expiring worker snapshots; scrape privately and retain history externally."""
from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from climaprev.api.observability import RequestMetrics

LEASE_SECONDS = 20
MAX_WORKERS = 256
_IDENTITY = re.compile(r"^[a-f0-9]{32}$")
_COUNTERS = ("cache_hits_total", "cache_misses_total", "cache_stale_total", "cache_corruptions_total",
             "upstream_errors_total", "upstream_retries_total", "rate_limit_rejections_total",
             "lock_contention_total", "lock_timeouts_total", "server_errors_total")


class MetricsStore:
    def __init__(self, redis: Redis, environment: str, *, clock: Callable[[], float] = time.time):
        self.redis = redis
        self.prefix = f"climaprev:{environment}:metrics"
        self.clock = clock

    async def publish(self, metrics: RequestMetrics) -> None:
        snapshot = metrics.snapshot()
        allowed = (*_COUNTERS, "instance_id", "http_requests_total", "http_request_duration_seconds",
                   "http_request_duration_buckets", "official_alert_checks_total")
        data = {key: snapshot[key] for key in allowed}
        identity = str(data["instance_id"])
        now = self.clock()
        envelope = json.dumps({"published_at": now, "snapshot": data}, allow_nan=False)
        if len(envelope.encode()) > 65536:
            raise ValueError("worker metric snapshot exceeds 64 KiB")
        await self.redis.set(f"{self.prefix}:{identity}", envelope, ex=LEASE_SECONDS)
        await self.redis.zadd(f"{self.prefix}:registry", {identity: now})
        await self.redis.zremrangebyscore(f"{self.prefix}:registry", "-inf", now - LEASE_SECONDS)
        await self.redis.expire(f"{self.prefix}:registry", LEASE_SECONDS * 2)

    async def read(self) -> dict[str, Any]:
        identities = await self.redis.zrange(f"{self.prefix}:registry", 0, MAX_WORKERS - 1)
        workers = []
        for identity in identities:
            if not isinstance(identity, str) or not _IDENTITY.fullmatch(identity):
                continue
            raw = await self.redis.get(f"{self.prefix}:{identity}")
            if not isinstance(raw, str) or len(raw.encode()) > 65536:
                continue
            try:
                envelope = json.loads(raw)
                age = self.clock() - envelope["published_at"]
                data = envelope["snapshot"]
                if (not isinstance(data, dict) or data.get("instance_id") != identity
                        or not 0 <= age < LEASE_SECONDS
                        or not isinstance(data.get("http_requests_total"), dict)
                        or not isinstance(data.get("http_request_duration_seconds"), dict)):
                    continue
                workers.append(data)
            except (ValueError, TypeError, KeyError):
                continue
        return {"workers": workers, "active_workers": len(workers),
                "truncated": len(identities) == MAX_WORKERS, "lease_seconds": LEASE_SECONDS,
                "limitation": "Live counters reset on restart; retain history externally. "
                              "Do not average worker percentiles."}

    async def run(self, metrics: RequestMetrics) -> None:
        while True:
            try:
                await self.publish(metrics)
            except (RedisError, OSError, ValueError):
                pass  # Optional telemetry loss must not block forecasts.
            await asyncio.sleep(5)


def prometheus_text(report: dict[str, Any]) -> str:
    lines = ["# TYPE climaprev_active_workers gauge",
             f"climaprev_active_workers {report['active_workers']}",
             "# TYPE climaprev_metrics_truncated gauge",
             f"climaprev_metrics_truncated {int(report['truncated'])}"]
    lines += ["# TYPE climaprev_http_requests_total counter",
              "# TYPE climaprev_http_request_duration_seconds histogram"]
    lines += [f"# TYPE climaprev_{key} counter" for key in _COUNTERS]
    lines.append("# TYPE climaprev_official_alert_checks_total counter")
    for worker in report["workers"]:
        label = f"worker={json.dumps(worker['instance_id'])}"
        for status, count in worker.get("official_alert_checks_total", {}).items():
            lines.append(f"climaprev_official_alert_checks_total{{{label},status={json.dumps(status)}}} {count}")
        for key in _COUNTERS:
            value = worker.get(key, 0)
            if type(value) is int and value >= 0:
                lines.append(f"climaprev_{key}{{{label}}} {value}")
        for key, value in worker.get("http_requests_total", {}).items():
            method, route, status = key.split("|", 2)
            labels = f"{label},method={json.dumps(method)},route={json.dumps(route)},status={json.dumps(status)}"
            lines.append(f"climaprev_http_requests_total{{{labels}}} {int(value)}")
        duration = worker.get("http_request_duration_seconds", {})
        for key in ("count", "sum"):
            lines.append(f"climaprev_http_request_duration_seconds_{key}{{{label}}} {duration.get(key, 0)}")
        for boundary, count in worker.get("http_request_duration_buckets", {}).items():
            lines.append(f"climaprev_http_request_duration_seconds_bucket{{{label},le={json.dumps(boundary)}}} {count}")
    return "\n".join(lines) + "\n"
