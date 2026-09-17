from pathlib import Path

import httpx
import pytest

import climaprev
from climaprev.api.deps import enforce_rate_limit
from climaprev.main import create_app


@pytest.mark.asyncio
async def test_page_serves_labeled_same_origin_query_form() -> None:
    app = create_app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<html lang="pt-BR">' in response.text
    assert 'action="/api/v1/risk"' in response.text
    for field in ("location_text", "latitude", "longitude", "start_date", "end_date", "temperature_unit"):
        assert f'name="{field}"' in response.text
        assert f'for="{field}"' in response.text
    assert 'src="/assets/app.js"' in response.text


@pytest.mark.asyncio
async def test_static_assets_serve_with_correct_media_types() -> None:
    app = create_app()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
        css = await client.get("/assets/styles.css")
        script = await client.get("/assets/app.js")
        absent = await client.get("/assets/absent.js")
    assert css.status_code == script.status_code == 200
    assert css.headers["content-type"].startswith("text/css")
    assert "javascript" in script.headers["content-type"]
    assert absent.status_code == 404


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


def test_assets_are_available_from_package_directory() -> None:
    web = Path(climaprev.__file__).parent / "web"
    assert (web / "index.html").is_file()
    assert (web / "styles.css").is_file()
    assert (web / "app.js").is_file()
