import httpx
import pytest

from climaprev.api.deps import enforce_rate_limit
from climaprev.main import create_app


@pytest.mark.asyncio
async def test_web_does_not_capture_api_health_or_internal_routes() -> None:
    app = create_app()
    app.dependency_overrides[enforce_rate_limit] = lambda: None
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        live = await client.get("/health/live")
        internal = await client.get("/internal/metrics")
        absent = await client.get("/api/nonexistent")
    assert live.json() == {"status": "live"}
    assert live.status_code == internal.status_code == 200
    assert "instance_id" in internal.json()
    assert absent.status_code == 404
    assert "text/html" not in absent.headers["content-type"]