"""Conservative official alert retrieval and delivery validity."""

import hashlib
import json
from collections.abc import Callable
from contextlib import suppress
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from climaprev.application.cache_codec import decode_alerts, encode_alerts
from climaprev.application.ports import CacheEntry, CachePort, OfficialAlertPort
from climaprev.application.query_result import OfficialAlertsResult
from climaprev.domain.models import CanonicalLocation, DatePeriod, OfficialAlert

_OFFICIAL_ALERTS_FRESH_TTL_SECONDS = 5 * 60
_OFFICIAL_ALERTS_STALE_TTL_SECONDS = 10 * 60
_OFFICIAL_ALERTS_FAILURE_FRESH_TTL_SECONDS = 30
_OFFICIAL_ALERTS_FAILURE_STALE_TTL_SECONDS = 60


class CachedOfficialAlerts:
    def __init__(self, provider: OfficialAlertPort, cache: CachePort, *,
                 now: Callable[[], datetime] = lambda: datetime.now(UTC)) -> None:
        self._official_alert_provider = provider
        self._cache = cache
        self._now = now

    async def get(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> OfficialAlertsResult:
        if getattr(self._official_alert_provider, "status", None) == "not_configured":
            return OfficialAlertsResult(status="not_configured", items=())

        cache_key = _official_alerts_key(location, period)
        try:
            cached = await self._cache.get(cache_key)
        except Exception:  # noqa: BLE001 - optional cache must not block the forecast.
            cached = None
        if (cached is not None and not cached.is_stale and cached.expires_at is not None
                and self._now() < cached.expires_at):
            cached_result = decode_alerts(cached.value)
            if cached_result is not None and all(
                alert.expires_at is not None and self._now() < alert.expires_at
                for alert in cached_result.items
            ):
                return replace(cached_result, items=_deliverable_alerts(
                    cached_result.items, location, period, self._now()))

        try:
            alerts = await self._official_alert_provider.get_alerts(location, period)
            alert_items = _deliverable_alerts(tuple(alerts), location, period, self._now())
        except Exception:  # noqa: BLE001 - optional alert providers must not block the forecast.
            unavailable = OfficialAlertsResult(status="unavailable", items=())
            with suppress(Exception):  # Optional cache must not block the forecast.
                await self._cache.set(
                    cache_key,
                    CacheEntry(value=encode_alerts(unavailable), is_stale=False),
                    _OFFICIAL_ALERTS_FAILURE_FRESH_TTL_SECONDS,
                    _OFFICIAL_ALERTS_FAILURE_STALE_TTL_SECONDS,
                )
            return unavailable
        available = OfficialAlertsResult(status="available", items=alert_items)
        with suppress(Exception):  # Optional cache must not block the forecast.
            await self._cache.set(
                cache_key,
                CacheEntry(value=encode_alerts(available), is_stale=False),
                _OFFICIAL_ALERTS_FRESH_TTL_SECONDS,
                _OFFICIAL_ALERTS_STALE_TTL_SECONDS,
            )
        return replace(available, items=_deliverable_alerts(
            available.items, location, period, self._now()))



def _official_alerts_key(location: CanonicalLocation, period: DatePeriod) -> str:
    identity = json.dumps(
        [
            location.latitude,
            location.longitude,
            period.start.isoformat(),
            period.end.isoformat(),
            location.timezone,
            "inmet-alerts-v2",
        ],
        separators=(",", ":"),
        allow_nan=False,
    )
    return "official-alerts:v1:" + hashlib.sha256(identity.encode()).hexdigest()


def _deliverable_alerts(
    alerts: tuple[OfficialAlert, ...], location: CanonicalLocation, period: DatePeriod, now: datetime,
) -> tuple[OfficialAlert, ...]:
    zone = ZoneInfo(location.timezone)
    start = datetime.combine(period.start, datetime.min.time(), zone)
    end = datetime.combine(period.end + timedelta(days=1), datetime.min.time(), zone)
    result = []
    for alert in alerts:
        if (alert.effective_at.tzinfo is None or alert.expires_at is None
                or alert.expires_at.tzinfo is None or alert.expires_at <= alert.effective_at):
            raise ValueError("official alert has unknown or invalid validity")
        if alert.expires_at > now and alert.effective_at < end and alert.expires_at > start:
            result.append(alert)
    return tuple(result)
