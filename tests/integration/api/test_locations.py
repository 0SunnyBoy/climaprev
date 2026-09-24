from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest

from climaprev.api.deps import get_location_search
from climaprev.domain.models import CanonicalLocation
from climaprev.main import create_app
from tests.security_fixtures import isolated_settings


class FakeLocationSearch:
    async def search(self, text: str) -> list[CanonicalLocation]:
        assert text == "Rio"
        return [
            CanonicalLocation(
                name="Rio de Janeiro, Rio de Janeiro, Brasil",
                latitude=-22.90642,
                longitude=-43.18223,
                timezone="America/Sao_Paulo",
                source="open-meteo-geocoding",
            )
        ]


@asynccontextmanager
async def client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(
        isolated_settings(
            redis_url=os.environ["REDIS_URL"],
        )
    )
    app.dependency_overrides[get_location_search] = lambda: FakeLocationSearch()
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
            yield http


@pytest.mark.asyncio
async def test_location_search_returns_candidates_with_context() -> None:
    async with client() as http:
        response = await http.get("/api/v1/locations/search", params={"query": "Rio"})

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Rio de Janeiro, Rio de Janeiro, Brasil"


@pytest.mark.asyncio
async def test_location_search_rejects_short_queries() -> None:
    async with client() as http:
        response = await http.get("/api/v1/locations/search", params={"query": "R"})

    assert response.status_code == 422
