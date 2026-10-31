from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from climaprev.api.observability import RequestMetrics
from climaprev.application.errors import (
    ProviderTransientError,
    WeatherDataInvalid,
    WeatherProviderUnavailable,
)
from climaprev.application.official_alerts import OfficialAlertsNotConfiguredProvider
from climaprev.application.ports import CacheEntry
from climaprev.application.query import ForecastQuery
from climaprev.application.services import forecast_cache
from climaprev.domain.models import (
    OfficialAlert,
)
from climaprev.domain.units import TemperatureUnit
from tests.support.forecast import (
    LOCATION,
    PERIOD,
    FakeAlerts,
    FakeGeocoder,
    FakeProvider,
    InMemoryCache,
    InMemoryLock,
    cached_forecast,
    forecast,
    service,
    text_query,
)


@pytest.mark.asyncio
async def test_geocodes_text_once_and_caches_location_for_24_hours() -> None:
    cache = InMemoryCache()
    geocoder = FakeGeocoder()
    query_service = service(cache=cache, geocoder=geocoder)

    first = await query_service.execute(text_query(), "request-one")
    second = await query_service.execute(text_query(), "request-two")

    assert first.location == LOCATION
    assert second.location == LOCATION
    assert geocoder.texts == ["Sao Paulo"]
    geo_writes = [call for call in cache.set_calls if call[0].startswith("geo:v1:")]
    assert len(geo_writes) == 1
    assert geo_writes[0][2:] == (86400, 86400)


@pytest.mark.asyncio
async def test_uses_coordinates_without_geocoding() -> None:
    geocoder = FakeGeocoder()
    provider = FakeProvider(forecast())
    query_service = service(geocoder=geocoder, provider=provider)
    query = ForecastQuery(
        location_text=None,
        latitude=-23.55051,
        longitude=-46.63331,
        start_date=PERIOD.start,
        end_date=PERIOD.start,
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    result = await query_service.execute(query, "coordinates-request")

    assert geocoder.texts == []
    assert provider.calls[0][0].latitude == -23.55051
    assert provider.calls[0][0].longitude == -46.63331
    assert result.location.latitude == -23.55051


@pytest.mark.asyncio
async def test_reuses_a_fresh_forecast_without_calling_provider() -> None:
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)

    await query_service.execute(text_query(), "first-request")
    provider.value = ProviderTransientError("provider must not be called for fresh cache")
    result = await query_service.execute(text_query(), "cached-request")

    assert len(provider.calls) == 1
    assert result.data_quality.is_stale is False


@pytest.mark.asyncio
async def test_refreshes_from_provider_when_cached_day_omits_a_serialized_field() -> None:
    cache = InMemoryCache()
    cached = cached_forecast()
    del cached["days"][0]["temperature_max_c"]  # type: ignore[index]
    forecast_key = forecast_cache.forecast_cache_key(LOCATION, PERIOD)
    cache.entries[forecast_key] = CacheEntry(value=cached, is_stale=False)
    provider_day = replace(forecast().days[0], temperature_max_c=20.0)
    provider = FakeProvider(replace(forecast(), days=(provider_day,)))
    query_service = service(cache=cache, provider=provider)

    result = await query_service.execute(text_query(), "truncated-cache-request")

    assert len(provider.calls) == 1
    assert result.forecast_risk.level == "low"


@pytest.mark.asyncio
async def test_refreshes_from_provider_when_cached_forecast_is_bound_to_another_request() -> None:
    cache = InMemoryCache()
    cached = cached_forecast()
    cached["location"] = {**cached["location"], "latitude": -22.90642}  # type: ignore[arg-type]
    forecast_key = forecast_cache.forecast_cache_key(LOCATION, PERIOD)
    cache.entries[forecast_key] = CacheEntry(value=cached, is_stale=False)
    provider_day = replace(forecast().days[0], temperature_max_c=20.0)
    provider = FakeProvider(replace(forecast(), days=(provider_day,)))
    query_service = service(cache=cache, provider=provider)

    result = await query_service.execute(text_query(), "mismatched-cache-request")

    assert len(provider.calls) == 1
    assert result.forecast_risk.level == "low"


@pytest.mark.asyncio
async def test_rechecks_cache_after_acquiring_lock_before_calling_provider() -> None:
    cache = InMemoryCache()
    lock = InMemoryLock()
    provider = FakeProvider(ProviderTransientError("provider should not be reached"))
    query_service = service(cache=cache, lock=lock, provider=provider)

    async def publish_forecast() -> None:
        forecast_key = forecast_cache.forecast_cache_key(LOCATION, PERIOD)
        await cache.set(forecast_key, CacheEntry(value=cached_forecast(), is_stale=False), 600, 900)

    lock.on_acquire = publish_forecast

    result = await query_service.execute(text_query(), "double-check-request")

    assert lock.acquires[0][1] == 10
    assert provider.calls == []
    assert result.forecast_risk.level == "high"


@pytest.mark.asyncio
async def test_concurrent_requests_share_one_provider_call() -> None:
    cache = InMemoryCache()
    lock = InMemoryLock(release_delay=0.05)
    provider = FakeProvider(forecast(), wait=True)
    query_service = service(cache=cache, lock=lock, provider=provider)

    first, second = await asyncio.gather(
        query_service.execute(text_query(), "concurrent-one"),
        query_service.execute(text_query(), "concurrent-two"),
    )

    assert len(provider.calls) == 1
    assert first.forecast_risk.level == second.forecast_risk.level == "high"


@pytest.mark.asyncio
async def test_lock_wait_uses_bounded_backoff_and_records_contention_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cache = InMemoryCache()
    lock = InMemoryLock()
    await lock.acquire("held-key", ttl_seconds=100)
    lock.acquires.clear()
    metrics = RequestMetrics()
    query_service = service(cache=cache, lock=lock, metrics=metrics)
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(forecast_cache, "monotonic", lambda: 0.0)
    monkeypatch.setattr(forecast_cache, "uniform", lambda _lower, _upper: 1.0)
    monkeypatch.setattr(forecast_cache, "_LOCK_MAX_ATTEMPTS", 5)

    result = await query_service._forecasts._wait_for_lock("wait-key", LOCATION, PERIOD)

    assert result is None
    assert len(lock.acquires) == 5
    assert sleeps == [0.05, 0.1, 0.2, 0.4]
    snapshot = metrics.snapshot()
    assert snapshot["lock_contention_total"] == 1
    assert snapshot["lock_timeouts_total"] == 1


@pytest.mark.asyncio
async def test_renews_ten_second_lock_during_long_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(forecast_cache, "_LOCK_HEARTBEAT_SECONDS", 0.01)
    cache = InMemoryCache()
    lock = InMemoryLock(expires_after_seconds=0.04)
    provider = FakeProvider(forecast(), wait_seconds=0.12)
    query_service = service(cache=cache, lock=lock, provider=provider)

    first_task = asyncio.create_task(query_service.execute(text_query(), "long-one"))
    await asyncio.sleep(0.02)
    second_task = asyncio.create_task(query_service.execute(text_query(), "long-two"))
    first, second = await asyncio.gather(first_task, second_task)

    assert len(provider.calls) == 1
    assert lock.acquires[0][1] == 10
    assert lock.refreshes
    assert first.forecast_risk.level == second.forecast_risk.level == "high"


@pytest.mark.asyncio
async def test_waits_past_lock_ttl_for_heartbeat_renewed_owner() -> None:
    cache = InMemoryCache()
    lock = InMemoryLock()
    provider = FakeProvider(forecast(), wait_seconds=11.0)
    query_service = service(cache=cache, lock=lock, provider=provider)

    first_task = asyncio.create_task(query_service.execute(text_query(), "real-long-one"))
    await asyncio.sleep(0.05)
    second_task = asyncio.create_task(query_service.execute(text_query(), "real-long-two"))
    first, second = await asyncio.gather(first_task, second_task)

    assert len(provider.calls) == 1
    assert lock.acquires[0][1] == 10
    assert len(lock.refreshes) >= 2
    assert first.forecast_risk.level == second.forecast_risk.level == "high"


@pytest.mark.asyncio
async def test_uses_stale_forecast_when_provider_has_transient_failure() -> None:
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)

    await query_service.execute(text_query(), "fresh-request")
    forecast_key = next(key for key in cache.entries if key.startswith("forecast:v2:"))
    cache.mark_stale(forecast_key)
    provider.value = ProviderTransientError("temporary outage")

    result = await query_service.execute(text_query(), "stale-request")

    assert result.data_quality.is_stale is True
    assert result.source.provider == "open-meteo"


@pytest.mark.asyncio
async def test_records_cache_risk_missing_fields_and_stale_provider_failure_metrics() -> None:
    cache = InMemoryCache()
    provider = FakeProvider(forecast(missing_fields=("daily.weather_code",)))
    metrics = RequestMetrics()
    query_service = service(cache=cache, provider=provider, metrics=metrics)

    await query_service.execute(text_query(), "metrics-fresh")
    forecast_key = next(key for key in cache.entries if key.startswith("forecast:v2:"))
    cache.mark_stale(forecast_key)
    provider.value = ProviderTransientError("temporary outage")

    stale = await query_service.execute(text_query(), "metrics-stale")
    snapshot = metrics.snapshot()

    assert stale.cache_status == "stale"
    assert snapshot["cache_misses_total"] == 1
    assert snapshot["cache_stale_total"] == 1
    assert snapshot["weather_provider_requests_total"]["open-meteo|success"] == 1
    assert snapshot["weather_provider_requests_total"]["open-meteo|error"] == 1
    assert snapshot["upstream_errors_total"] == 1
    assert snapshot["risk_evaluations_total"]["high|reference-v1"] == 2
    assert snapshot["weather_missing_fields_total"]["daily.weather_code"] == 2


@pytest.mark.asyncio
async def test_raises_unavailable_when_no_valid_stale_forecast_exists() -> None:
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)

    await query_service.execute(text_query(), "fresh-request")
    forecast_key = next(key for key in cache.entries if key.startswith("forecast:v2:"))
    del cache.entries[forecast_key]
    provider.value = ProviderTransientError("temporary outage")

    with pytest.raises(WeatherProviderUnavailable):
        await query_service.execute(text_query(), "expired-stale-request")


@pytest.mark.asyncio
async def test_does_not_use_stale_forecast_when_provider_payload_is_invalid() -> None:
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)

    await query_service.execute(text_query(), "fresh-request")
    forecast_key = next(key for key in cache.entries if key.startswith("forecast:v2:"))
    cache.mark_stale(forecast_key)
    provider.value = WeatherDataInvalid("invalid payload")

    with pytest.raises(WeatherDataInvalid):
        await query_service.execute(text_query(), "invalid-payload-request")


@pytest.mark.asyncio
async def test_converts_temperature_output_without_changing_celsius_risk_evaluation() -> None:
    celsius_service = service()
    fahrenheit_service = service()

    celsius = await celsius_service.execute(text_query(), "celsius-request")
    fahrenheit = await fahrenheit_service.execute(
        text_query(unit=TemperatureUnit.FAHRENHEIT), "fahrenheit-request"
    )

    assert celsius.forecast_risk.level == fahrenheit.forecast_risk.level == "high"
    assert celsius.days[0].temperature_max == 40.0
    assert fahrenheit.days[0].temperature_max == 104.0
    assert celsius.forecast_risk.conditions[0].value == 40.0
    assert celsius.forecast_risk.conditions[0].unit == "celsius"
    assert fahrenheit.forecast_risk.conditions[0].value == 104.0
    assert fahrenheit.forecast_risk.conditions[0].unit == "fahrenheit"
    assert fahrenheit.forecast_risk.daily[0].conditions[0].value == 104.0
    assert fahrenheit.forecast_risk.daily[0].conditions[0].unit == "fahrenheit"


@pytest.mark.asyncio
async def test_keeps_forecast_when_official_alerts_are_not_configured_or_fail() -> None:
    not_configured = await service(alerts=OfficialAlertsNotConfiguredProvider()).execute(
        text_query(), "not-configured-request"
    )
    unavailable = await service(alerts=FakeAlerts(RuntimeError("alerts down"))).execute(
        text_query(), "alerts-failed-request"
    )

    assert not_configured.official_alerts.status == "not_configured"
    assert not_configured.official_alerts.items == ()
    assert unavailable.official_alerts.status == "unavailable"
    assert unavailable.official_alerts.items == ()
    assert unavailable.forecast_risk.level == "high"


@pytest.mark.asyncio
async def test_official_alerts_raise_priority_and_mark_their_active_days() -> None:
    alerts = FakeAlerts(
        items=(
            OfficialAlert(
                source="INMET",
                event="Tempestade severa",
                severity="Severe",
                effective_at=datetime(2026, 8, 28, 15, tzinfo=UTC),
                expires_at=datetime(2026, 8, 29, 3, tzinfo=UTC),
                geographic_scope="Sao Paulo",
                source_url="https://example.test/alert",
            ),
        )
    )

    result = await service(alerts=alerts, now=lambda: datetime(2026, 8, 28, 12, tzinfo=UTC)).execute(
        text_query(), "official-alert-request")

    assert result.risk_overview is not None
    assert result.risk_overview.source == "official_alert"
    assert result.risk_overview.level == "high"
    assert result.risk_overview.peak_days == (PERIOD.start,)


@pytest.mark.asyncio
async def test_caches_successful_official_alert_lookup() -> None:
    cache = InMemoryCache()
    alerts = FakeAlerts()
    query_service = service(cache=cache, alerts=alerts)

    first = await query_service.execute(text_query(), "alerts-cache-one")
    second = await query_service.execute(text_query(), "alerts-cache-two")

    assert alerts.calls == 1
    assert first.official_alerts.status == second.official_alerts.status == "available"
    assert any(key.startswith("official-alerts:v1:") for key in cache.entries)


@pytest.mark.asyncio
@pytest.mark.parametrize('stale', [True, False])
async def test_refreshes_stale_or_expired_official_alert_cache(stale: bool) -> None:
    cache = InMemoryCache()
    alerts = FakeAlerts()
    now = datetime(2026, 8, 28, 12, tzinfo=UTC)
    query_service = service(cache=cache, alerts=alerts, now=lambda: now)
    await query_service.execute(text_query(), 'alerts-first')
    key = next(key for key in cache.entries if key.startswith('official-alerts:v1:'))
    cache.entries[key] = replace(cache.entries[key], is_stale=stale,
                                 expires_at=now + timedelta(seconds=60) if stale else now)
    alerts.error = RuntimeError('source unavailable during refresh')
    result = await query_service.execute(text_query(), 'alerts-refresh')
    assert alerts.calls == 2
    assert result.official_alerts.status == 'unavailable'
    assert result.official_alerts.items == ()


@pytest.mark.asyncio
async def test_refreshes_alert_expiring_before_cache_entry() -> None:
    cache = InMemoryCache()
    clock = [datetime(2026, 8, 28, 12, tzinfo=UTC)]
    alerts = FakeAlerts(items=(OfficialAlert(
        source='INMET', event='Synthetic storm', severity='Severe',
        effective_at=clock[0], expires_at=clock[0]+timedelta(minutes=1),
        geographic_scope='Sao Paulo', source_url=None,
    ),))
    query_service = service(cache=cache, alerts=alerts, now=lambda: clock[0])
    await query_service.execute(text_query(), 'alerts-before-expiry')
    clock[0] += timedelta(minutes=2)
    alerts.items = ()
    result = await query_service.execute(text_query(), 'alerts-after-expiry')
    assert alerts.calls == 2
    assert result.official_alerts.status == 'available'
    assert result.official_alerts.items == ()


@pytest.mark.asyncio
async def test_returns_request_metadata_disclaimer_and_missing_fields() -> None:
    result = await service(provider=FakeProvider(forecast(missing_fields=("daily.weather_code",)))).execute(
        text_query(), "trace-123"
    )

    assert result.request_id == "trace-123"
    assert result.source.provider == "open-meteo"
    assert result.source.fetched_at == datetime(2026, 8, 28, 12, tzinfo=UTC)
    assert "estimativa" in result.disclaimer.lower()
    assert "alertas oficiais" in result.disclaimer.lower()
    assert result.data_quality.missing_fields == ("daily.weather_code",)
