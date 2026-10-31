"""Composition, cache isolation, expiry and full return to the original baseline."""

from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta

import pytest

from climaprev.application.errors import (
    ProviderTransientError,
    WeatherDataInvalid,
    WeatherProviderUnavailable,
)
from climaprev.config import Settings
from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.infrastructure.providers.candidate_forecast import (
    PreparedCandidateForecast,
    prepare_forecast,
)
from climaprev.main import compose_forecast_query, create_app
from climaprev.tools.experimental_candidate import record_decision, register_candidate
from climaprev.tools.historical_experiment import canonical_json
from tests.integration.providers.test_candidate_forecast import prepared_bundle
from tests.support.experiment import (
    approval_fixture,
    independent_evaluation_fixture,
    review_fixture,
)
from tests.support.forecast import (
    LOCATION,
    PERIOD,
    FakeAlerts,
    FakeGeocoder,
    FakeProvider,
    InMemoryCache,
    InMemoryLock,
    forecast,
    text_query,
)


def composed(*, provider=None, candidate=None, cache=None, now=None, alerts=None):
    return compose_forecast_query(Settings(), geocoder=FakeGeocoder(),
                                   weather_provider=provider or FakeProvider(forecast()),
                                   candidate_provider=candidate, cache=cache or InMemoryCache(),
                                   lock=InMemoryLock(), official_alert_provider=alerts or FakeAlerts([]),
                                   now=now or (lambda: forecast().fetched_at))


def test_default_application_has_no_candidate_and_uses_original_components():
    assert Settings().candidate_bundle_file is None
    assert create_app(Settings()).state.candidate_provider is None
    query = composed()
    assert asdict(query._risk_policy) == asdict(RiskPolicy())
    assert query._forecasts._calibration == ForecastCalibration.disabled()
    assert isinstance(query._forecasts._weather_provider, FakeProvider)


def test_selection_without_e3_fails_before_application_starts():
    bundle, _ = prepared_bundle()
    bundle["decision"]["decision"]["approvals"] = []
    with pytest.raises(WeatherDataInvalid, match="identity"):
        create_app(Settings(), strategy_bundle=bundle)


@pytest.mark.asyncio
async def test_candidate_values_and_policy_are_used_once_with_separate_cache():
    bundle, value = prepared_bundle()
    original = bundle["candidate"]["candidate"]
    bundle["candidate"] = register_candidate(protocol=bundle["protocol"], policy=original["policy"],
        calibration=asdict(ForecastCalibration(profile_version="synthetic-enabled", enabled=True,
                                               temperature_offset_c=-10)),
        normalization=original["normalization"], models=original["models"], code_version="synthetic")
    bundle["evaluation"] = independent_evaluation_fixture(bundle["protocol"], bundle["candidate"])
    bundle["decision"] = record_decision(bundle["protocol"], bundle["candidate"], bundle["evaluation"],
        opinion=review_fixture(bundle["protocol"], bundle["candidate"], bundle["evaluation"]),
        approvals=[approval_fixture(bundle["protocol"], "E3")])
    bundle["forecasts"] = [prepare_forecast(bundle["candidate"], value,
        expires_at=value.fetched_at + timedelta(minutes=10), source_hashes={"gfs_global": "d" * 64})]
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    cache, original_provider = InMemoryCache(), FakeProvider(value)
    baseline = composed(provider=original_provider, cache=cache)
    first = await baseline.execute(text_query(), "v1")
    selected = composed(provider=original_provider, candidate=provider, cache=cache)
    candidate_result = await selected.execute(text_query(), "candidate")
    repeat = await selected.execute(text_query(), "candidate-cache")
    rollback = composed(provider=original_provider, cache=cache)
    restored = await rollback.execute(text_query(), "rollback")
    assert first.days[0].temperature_max == 40
    assert candidate_result.days[0].temperature_max == 30
    assert repeat.days == candidate_result.days
    assert candidate_result.forecast_risk.policy_version == "reference-candidate-1"
    assert restored.days == first.days
    assert restored.forecast_risk == first.forecast_risk
    assert restored.cache_status == "hit"
    assert restored.forecast_risk.policy_version == "reference-v1"
    assert len(original_provider.calls) == 1
    assert len([key for key in cache.entries if key.startswith("forecast:")]) == 2
    assert rollback._forecasts._calibration == ForecastCalibration.disabled()
    assert rollback._forecasts._provider_identity == Settings().forecast_base_url


@pytest.mark.asyncio
async def test_cached_candidate_cannot_outlive_prepared_expiration():
    bundle, value = prepared_bundle()
    clock = [value.fetched_at]
    provider = PreparedCandidateForecast(bundle, now=lambda: clock[0])
    query = composed(candidate=provider, now=lambda: clock[0])
    await query.execute(text_query(), "fresh")
    clock[0] += timedelta(minutes=10)
    with pytest.raises(WeatherProviderUnavailable, match="expired"):
        await query.execute(text_query(), "expired-cache")


@pytest.mark.asyncio
async def test_expiry_while_waiting_for_alerts_is_checked_before_delivery():
    bundle, value = prepared_bundle()
    clock = [value.fetched_at]
    class SlowAlerts(FakeAlerts):
        async def get_alerts(self, location, period):
            clock[0] += timedelta(minutes=10)
            return []
    query = composed(candidate=PreparedCandidateForecast(bundle, now=lambda: clock[0]),
                     now=lambda: clock[0], alerts=SlowAlerts([]))
    with pytest.raises(WeatherProviderUnavailable, match="expired"):
        await query.execute(text_query(), "late-delivery")


@pytest.mark.asyncio
async def test_unavailable_candidate_scope_does_not_silently_use_baseline():
    bundle, value = prepared_bundle()
    candidate = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    baseline = FakeProvider(ProviderTransientError("must not be reached"))
    query = composed(candidate=candidate, provider=baseline)
    other = replace(text_query(), location_text=None, latitude=1, longitude=1)
    with pytest.raises(WeatherProviderUnavailable, match="prepared"):
        await query.execute(other, "out-of-scope")
    assert baseline.calls == []


def test_file_selection_is_explicit_and_removal_restores_default(tmp_path):
    bundle, value = prepared_bundle()
    # Startup can load an expired bundle; delivery still refuses it.
    path = tmp_path / "candidate.json"
    path.write_text(canonical_json(bundle))
    selected = create_app(Settings(candidate_bundle_file=path))
    assert isinstance(selected.state.candidate_provider, PreparedCandidateForecast)
    assert create_app(Settings()).state.candidate_provider is None
    assert value.location == LOCATION
    assert value.period == PERIOD
    assert datetime.now(UTC) > value.fetched_at


@pytest.mark.asyncio
async def test_lifespan_wires_selected_and_default_provider_into_the_public_service():
    from climaprev.infrastructure.providers.open_meteo import OpenMeteoForecastClient

    bundle, _ = prepared_bundle()
    selected = create_app(Settings(metrics_aggregation_enabled=False), strategy_bundle=bundle)
    async with selected.router.lifespan_context(selected):
        query = selected.state.forecast_query_service
        assert query._forecasts._weather_provider is selected.state.candidate_provider
        assert query._risk_policy.policy_version == "reference-candidate-1"
    baseline = create_app(Settings(metrics_aggregation_enabled=False))
    async with baseline.router.lifespan_context(baseline):
        query = baseline.state.forecast_query_service
        assert isinstance(query._forecasts._weather_provider, OpenMeteoForecastClient)
        assert query._risk_policy.policy_version == "reference-v1"
        assert query._forecasts._calibration == ForecastCalibration.disabled()
