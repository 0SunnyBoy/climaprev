import asyncio
from typing import cast

from fastapi import APIRouter, Request
from redis.exceptions import RedisError
from starlette.responses import Response

from climaprev.api.observability import RequestMetrics
from climaprev.infrastructure.metrics_store import prometheus_text

router = APIRouter()


@router.get("/internal/metrics", include_in_schema=False)
async def metrics(request: Request) -> dict[str, object]:
    """Per-worker snapshot; the homologation entrance blocks this route."""
    return cast(RequestMetrics, request.app.state.metrics).snapshot()


@router.get("/internal/metrics/prometheus", include_in_schema=False)
async def shared_metrics(request: Request) -> Response:
    if not request.app.state.settings.metrics_aggregation_enabled:
        return Response("shared metrics disabled\n", status_code=503)
    try:
        async with asyncio.timeout(2):
            report = await request.app.state.metrics_store.read()
        if not report["active_workers"] or report["truncated"]:
            return Response("incomplete metric snapshot\n", status_code=503)
        return Response(prometheus_text(report), media_type="text/plain; version=0.0.4")
    except (RedisError, TimeoutError, ValueError, TypeError):
        return Response("metric store unavailable\n", status_code=503)
