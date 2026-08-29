from datetime import date

import pytest

from climaprev.application.official_alerts import OfficialAlertsNotConfiguredProvider
from climaprev.domain.models import CanonicalLocation, DatePeriod


@pytest.mark.asyncio
async def test_returns_not_configured_status_and_no_official_alerts() -> None:
    provider = OfficialAlertsNotConfiguredProvider()
    location = CanonicalLocation(
        name="Sao Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
        timezone="America/Sao_Paulo",
        source="test",
    )
    period = DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 28))

    alerts = await provider.get_alerts(location, period)

    assert provider.status == "not_configured"
    assert alerts == []
