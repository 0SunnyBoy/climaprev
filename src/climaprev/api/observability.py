from __future__ import annotations

import json
import logging
import os
import re
from collections import Counter, defaultdict, deque
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.responses import JSONResponse, Response

from climaprev.api.errors import ErrorBody, ErrorEnvelope

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_LOGGER = logging.getLogger("climaprev.request")
_UPSTREAM_ERROR_CODES = {
    "WEATHER_DATA_INVALID",
    "WEATHER_PROVIDER_UNAVAILABLE",
    "WEATHER_PROVIDER_REJECTED",
}
_RETRY_COUNT: ContextVar[list[int] | None] = ContextVar("climaprev_retry_count", default=None)
_REQUEST_EVENTS: ContextVar[set[str] | None] = ContextVar("climaprev_metric_events", default=None)
_LATENCY_SAMPLE_LIMIT = 2048
_LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 30)


def _latency_summary(samples: deque[float]) -> dict[str, float | int]:
    if not samples:
        return {"sample_count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
    ordered = sorted(samples)

    def percentile(rate: float) -> float:
        index = min(len(ordered) - 1, int(rate * len(ordered)))
        return round(ordered[index], 2)

    return {
        "sample_count": len(ordered),
        "p50": percentile(0.50),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
    }


class RequestMetrics:
    """Small in-process metric sink; a deployment can export its counters externally."""

    def __init__(self) -> None:
        self._instance_id = uuid4().hex
        self._started_at = datetime.now(UTC).isoformat()
        self._counters: Counter[str] = Counter()
        self._request_duration_count = 0
        self._request_duration_sum_seconds = 0.0
        self._request_duration_buckets: Counter[str] = Counter()
        self._provider_duration_count = 0
        self._provider_duration_sum_seconds = 0.0
        self._request_latency_samples: deque[float] = deque(maxlen=_LATENCY_SAMPLE_LIMIT)
        self._provider_latency_samples: defaultdict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=_LATENCY_SAMPLE_LIMIT)
        )
        self._states: dict[str, str] = {}

    def begin_request(self) -> object:
        return _REQUEST_EVENTS.set(set())

    def end_request(self, token: object) -> None:
        _REQUEST_EVENTS.reset(token)  # type: ignore[arg-type]

    def _record_once(self, event: str) -> bool:
        events = _REQUEST_EVENTS.get()
        if events is None:
            return True
        if event in events:
            return False
        events.add(event)
        return True

    def record_upstream_retry(self) -> None:
        self._counters["upstream_retries_total"] += 1
        retries = _RETRY_COUNT.get()
        if retries is not None:
            retries[0] += 1

    def record_rate_limit_rejection(self) -> None:
        self._counters["rate_limit_rejections_total"] += 1

    def record_cache_corruption(self) -> None:
        self._counters["cache_corruptions_total"] += 1

    def record_cache_status(self, status: str) -> None:
        if not self._record_once(f"cache:{status}"):
            return
        if status == "hit":
            self._counters["cache_hits_total"] += 1
        elif status == "miss":
            self._counters["cache_misses_total"] += 1
        elif status == "stale":
            self._counters["cache_stale_total"] += 1

    def record_provider_request(self, provider: str, duration_seconds: float, outcome: str) -> None:
        self._counters[f"weather_provider_requests_total:{provider}|{outcome}"] += 1
        self._provider_duration_count += 1
        self._provider_duration_sum_seconds += duration_seconds
        self._provider_latency_samples[provider].append(max(duration_seconds, 0.0) * 1000)

    def record_upstream_error(self) -> None:
        if not self._record_once("upstream_error"):
            return
        self._counters["upstream_errors_total"] += 1

    def record_official_alert_status(self, status: str) -> None:
        if status in {"available", "unavailable", "not_configured"}:
            self._counters[f"official_alert_checks_total:{status}"] += 1

    def record_risk_evaluation(self, assessment: object) -> None:
        level = getattr(assessment, "level", "unknown")
        policy_version = getattr(assessment, "policy_version", "unknown")
        self._counters[f"risk_evaluations_total:{level}|{policy_version}"] += 1

    def record_missing_fields(self, fields: tuple[str, ...]) -> None:
        for field in fields:
            self._counters[f"weather_missing_fields_total:{field}"] += 1

    def record_lock_contention(self) -> None:
        self._counters["lock_contention_total"] += 1

    def record_lock_timeout(self) -> None:
        self._counters["lock_timeouts_total"] += 1

    def record_dependency_circuit_state(self, dependency: str, state: str) -> None:
        self._states[dependency] = state

    def record_request(
        self,
        *,
        method: str = "GET",
        route: str = "unknown",
        status_code: int,
        duration_seconds: float | None = None,
        latency_ms: float | None = None,
        cache: str | None,
        error_code: str | None,
        provider: str | None = None,
        retries: int = 0,
    ) -> None:
        seconds = duration_seconds if duration_seconds is not None else (latency_ms or 0) / 1000
        self._counters[f"http_requests_total:{method}|{route}|{status_code}"] += 1
        self._counters["requests_total"] += 1
        self._request_duration_count += 1
        self._request_duration_sum_seconds += seconds
        for boundary in _LATENCY_BUCKETS:
            if seconds <= boundary:
                self._request_duration_buckets[str(boundary)] += 1
        self._request_duration_buckets["+Inf"] += 1
        self._request_latency_samples.append(max(seconds, 0.0) * 1000)
        if status_code in {429, 502, 503}:
            self._counters[f"http_status_{status_code}_total"] += 1
        if error_code in _UPSTREAM_ERROR_CODES:
            self.record_upstream_error()
        if status_code >= 500:
            self._counters["server_errors_total"] += 1
        if provider is not None:
            self._counters[f"providers_seen:{provider}"] += 1
        if retries:
            self._counters["request_retries_total"] += retries

    def snapshot(self) -> dict[str, object]:
        provider_requests = {
            key.split(":", 1)[1]: value
            for key, value in self._counters.items()
            if key.startswith("weather_provider_requests_total:")
        }
        risk_evaluations = {
            key.split(":", 1)[1]: value
            for key, value in self._counters.items()
            if key.startswith("risk_evaluations_total:")
        }
        missing_fields = {
            key.split(":", 1)[1]: value
            for key, value in self._counters.items()
            if key.startswith("weather_missing_fields_total:")
        }
        return {
            "instance_id": self._instance_id,
            "pid": os.getpid(),
            "started_at": self._started_at,
            "http_requests_total": {
                key.split(":", 1)[1]: value
                for key, value in self._counters.items()
                if key.startswith("http_requests_total:")
            },
            "http_request_duration_seconds": {
                "count": self._request_duration_count,
                "sum": self._request_duration_sum_seconds,
            },
            "request_latency_ms": _latency_summary(self._request_latency_samples),
            "http_request_duration_buckets": {
                **{str(boundary): self._request_duration_buckets[str(boundary)] for boundary in _LATENCY_BUCKETS},
                "+Inf": self._request_duration_buckets["+Inf"],
            },
            "weather_provider_requests_total": provider_requests,
            "weather_provider_duration_seconds": {
                "count": self._provider_duration_count,
                "sum": self._provider_duration_sum_seconds,
            },
            "weather_provider_latency_ms": {
                provider: _latency_summary(samples)
                for provider, samples in self._provider_latency_samples.items()
            },
            "weather_provider_request_duration_seconds": {
                "count": self._provider_duration_count,
                "sum": self._provider_duration_sum_seconds,
            },
            "requests_total": self._counters["requests_total"],
            "official_alert_checks_total": {status: self._counters[f"official_alert_checks_total:{status}"]
                                            for status in ("available", "unavailable", "not_configured")},
            "request_latency_ms_count": self._request_duration_count,
            "cache_corruptions_total": self._counters["cache_corruptions_total"],
            "cache_hits_total": self._counters["cache_hits_total"],
            "cache_misses_total": self._counters["cache_misses_total"],
            "cache_stale_total": self._counters["cache_stale_total"],
            "upstream_errors_total": self._counters["upstream_errors_total"],
            "upstream_retries_total": self._counters["upstream_retries_total"],
            "rate_limit_rejections_total": self._counters["rate_limit_rejections_total"],
            "rate_limit_exceeded_total": self._counters["rate_limit_rejections_total"],
            "http_status_429_total": self._counters["http_status_429_total"],
            "http_status_502_total": self._counters["http_status_502_total"],
            "http_status_503_total": self._counters["http_status_503_total"],
            "server_errors_total": self._counters["server_errors_total"],
            "risk_evaluations_total": risk_evaluations,
            "weather_missing_fields_total": missing_fields,
            "lock_contention_total": self._counters["lock_contention_total"],
            "lock_timeouts_total": self._counters["lock_timeouts_total"],
            "dependency_circuit_state": dict(self._states),
        }


def request_id_from_header(value: str | None) -> str:
    if value is not None and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return uuid4().hex


def normalized_route(request: Request) -> str:
    route = request.scope.get("route")
    return str(getattr(route, "path", "unmatched"))


async def observe_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request_id_from_header(request.headers.get("x-request-id"))
    request.state.request_id = request_id
    retry_token = _RETRY_COUNT.set([0])
    metric_token = request.app.state.metrics.begin_request()
    started_at = perf_counter()
    try:
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 -- HTTP boundary must sanitize unexpected failures.
            # Cancellation derives from BaseException and must still propagate.
            request.state.error_code = "INTERNAL_ERROR"
            envelope = ErrorEnvelope(
                error=ErrorBody(
                    request_id=request_id, code="INTERNAL_ERROR", message="internal server error"
                )
            )
            response = JSONResponse(status_code=500, content=envelope.model_dump(mode="json"))
        response.headers["X-Request-ID"] = request_id
        latency_ms = round((perf_counter() - started_at) * 1000, 2)
        cache = getattr(request.state, "cache", None)
        error_code = getattr(request.state, "error_code", None)
        retry_state = _RETRY_COUNT.get()
        retries = retry_state[0] if retry_state is not None else 0
        request.app.state.metrics.record_request(
            method=request.method,
            route=normalized_route(request),
            status_code=response.status_code,
            duration_seconds=latency_ms / 1000,
            cache=cache,
            error_code=error_code,
            provider=getattr(request.state, "provider", None),
            retries=retries,
        )
        if cache is not None:
            request.app.state.metrics.record_cache_status(cache)
        _LOGGER.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "route": normalized_route(request),
                    "status": response.status_code,
                    "latency_ms": latency_ms,
                    "cache": cache,
                    "provider": getattr(request.state, "provider", None),
                    "retries": retries,
                    "error_code": error_code,
                    "request_id": request_id,
                },
                separators=(",", ":"),
            )
        )
        return response
    finally:
        _RETRY_COUNT.reset(retry_token)
        request.app.state.metrics.end_request(metric_token)
