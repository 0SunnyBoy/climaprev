from typing import cast

from fastapi import APIRouter, Request

from climaprev.api.observability import RequestMetrics

router = APIRouter()


@router.get("/internal/metrics", include_in_schema=False)
async def metrics(request: Request) -> dict[str, object]:
    """Per-worker snapshot; the homologation entrance blocks this route."""
    return cast(RequestMetrics, request.app.state.metrics).snapshot()
