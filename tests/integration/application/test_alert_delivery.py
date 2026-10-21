from datetime import UTC, datetime, timedelta

import pytest

from climaprev.domain.models import OfficialAlert
from tests.support.forecast import (
    FakeAlerts,
    InMemoryCache,
    service,
    text_query,
)


def warning(now, *, expires=True):
    return OfficialAlert(source="INMET", event="Synthetic storm", severity="Severe",
                         effective_at=now - timedelta(hours=1),
                         expires_at=now + timedelta(seconds=1) if expires else None,
                         geographic_scope="Synthetic area", source_url=None)


@pytest.mark.asyncio
async def test_unknown_alert_validity_is_unavailable_not_empty_available():
    now = datetime(2026, 8, 28, 12, tzinfo=UTC)
    result = await service(alerts=FakeAlerts(items=(warning(now, expires=False),)),
                           now=lambda: now).execute(text_query(), "invalid-validity")
    assert result.official_alerts.status == "unavailable"
    assert result.official_alerts.items == ()
    assert result.risk_overview.source == "forecast_heuristic"


@pytest.mark.asyncio
async def test_alert_expiring_while_optional_cache_is_written_is_not_delivered():
    now = [datetime(2026, 8, 28, 12, tzinfo=UTC)]

    class DelayedCache(InMemoryCache):
        async def set(self, key, value, fresh_ttl_seconds, stale_ttl_seconds=0):
            if key.startswith("official-alerts:"):
                now[0] += timedelta(seconds=2)
            await super().set(key, value, fresh_ttl_seconds, stale_ttl_seconds)

    result = await service(cache=DelayedCache(), alerts=FakeAlerts(items=(warning(now[0]),)),
                           now=lambda: now[0]).execute(text_query(), "expiry-during-cache")
    assert result.official_alerts.status == "available"
    assert result.official_alerts.items == ()
    assert result.risk_overview.source == "forecast_heuristic"
