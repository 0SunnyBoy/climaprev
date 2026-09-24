from __future__ import annotations

import json
from datetime import date

import httpx
import pytest
import respx

from climaprev.application.errors import WeatherDataInvalid
from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.infrastructure.providers.inmet_alerts import InmetOfficialAlertsProvider

BASE_URL = "https://inmet.test"
LOCATION = CanonicalLocation(
    name="Rio de Janeiro",
    latitude=-22.9068,
    longitude=-43.1729,
    timezone="America/Sao_Paulo",
    source="fixture",
)
PERIOD = DatePeriod(start=date(2026, 9, 18), end=date(2026, 9, 18))


def _polygon(*, inside: bool = True) -> str:
    if inside:
        ring = [[-44, -24], [-42, -24], [-42, -22], [-44, -22], [-44, -24]]
    else:
        ring = [[-50, -20], [-48, -20], [-48, -18], [-50, -18], [-50, -20]]
    return json.dumps({"type": "Polygon", "coordinates": [ring]})


def _alert(*, identifier: int = 12345, inside: bool = True) -> dict[str, object]:
    return {
        "id": identifier,
        "inicio": "2026-09-18 08:00",
        "fim": "2026-09-18 18:00",
        "poligono": _polygon(inside=inside),
        "descricao": "Tempestade",
        "severidade": "Perigo Potencial",
        "regioes": "Sudeste",
    }


def _settings() -> Settings:
    return Settings(inmet_alerts_base_url=BASE_URL, additional_retries=0)


@pytest.mark.asyncio
async def test_inmet_provider_filters_active_alerts_by_point_and_period() -> None:
    payload = {"hoje": [_alert()], "futuro": [_alert(identifier=54321, inside=False)]}
    async with httpx.AsyncClient() as client:
        provider = InmetOfficialAlertsProvider(client, _settings())
        with respx.mock(assert_all_called=True) as mock:
            route = mock.get(f"{BASE_URL}/avisos/ativos").respond(200, json=payload)

            alerts = await provider.get_alerts(LOCATION, PERIOD)

    assert route.called
    assert len(alerts) == 1
    assert alerts[0].source == "INMET"
    assert alerts[0].event == "Tempestade"
    assert alerts[0].severity == "Perigo Potencial"
    assert alerts[0].geographic_scope == "Sudeste"
    assert alerts[0].source_url == "https://avisos.inmet.gov.br/12345"
    assert alerts[0].effective_at.isoformat() == "2026-09-18T08:00:00-03:00"


@pytest.mark.asyncio
async def test_inmet_provider_excludes_non_overlapping_period() -> None:
    payload = {"hoje": [{**_alert(), "inicio": "2026-09-19 08:00"}], "futuro": []}
    async with httpx.AsyncClient() as client:
        provider = InmetOfficialAlertsProvider(client, _settings())
        with respx.mock:
            respx.get(f"{BASE_URL}/avisos/ativos").respond(200, json=payload)

            alerts = await provider.get_alerts(LOCATION, PERIOD)

    assert alerts == []


@pytest.mark.asyncio
async def test_inmet_provider_rejects_invalid_alert_buckets() -> None:
    async with httpx.AsyncClient() as client:
        provider = InmetOfficialAlertsProvider(client, _settings())
        with respx.mock:
            respx.get(f"{BASE_URL}/avisos/ativos").respond(200, json={"hoje": {}})

            with pytest.raises(WeatherDataInvalid):
                await provider.get_alerts(LOCATION, PERIOD)
