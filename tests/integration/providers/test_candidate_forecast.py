"""Prepared strategy delivery has no weather/campaign HTTP dependency."""

from copy import deepcopy
from dataclasses import replace
from datetime import timedelta

import pytest

from climaprev.application.errors import WeatherDataInvalid, WeatherProviderUnavailable
from climaprev.infrastructure.providers.candidate_forecast import (
    PreparedCandidateForecast,
    prepare_forecast,
)
from climaprev.tools.historical_experiment import digest
from tests.support.experiment import accepted_bundle_fixture
from tests.support.forecast import forecast


def prepared_bundle(*, partial=False):
    value = forecast()
    if partial:
        value = replace(value, days=(replace(value.days[0], humidity_mean_pct=None),),
                        missing_fields=("humidity_mean_pct",))
    bundle = accepted_bundle_fixture()
    artifact = prepare_forecast(bundle["candidate"], value,
                                 expires_at=value.fetched_at + timedelta(minutes=10),
                                 source_hashes={"gfs_global": "d" * 64})
    bundle["forecasts"] = [artifact]
    return bundle, value


@pytest.mark.asyncio
async def test_prepared_forecast_returns_existing_port_contract_and_provenance():
    bundle, value = prepared_bundle()
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    result = await provider.forecast(value.location, value.period)
    assert result == value
    assert provider.provenance[0]["sources"] == {"gfs_global": "d" * 64}
    assert provider.strategy_identity.startswith("candidate:")


@pytest.mark.asyncio
async def test_partial_values_and_quality_flags_are_preserved():
    bundle, value = prepared_bundle(partial=True)
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    result = await provider.forecast(value.location, value.period)
    assert result.days[0].humidity_mean_pct is None
    assert result.missing_fields == ("humidity_mean_pct",)


@pytest.mark.asyncio
async def test_expired_or_unprepared_request_fails_through_existing_error_contract():
    bundle, value = prepared_bundle()
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at + timedelta(minutes=10))
    with pytest.raises(WeatherProviderUnavailable, match="expired"):
        await provider.forecast(value.location, value.period)
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    with pytest.raises(WeatherProviderUnavailable, match="prepared"):
        await provider.forecast(replace(value.location, latitude=1), value.period)


@pytest.mark.parametrize("mutation", ["candidate", "normalization", "payload", "future"])
def test_wrong_or_tampered_identity_is_rejected(mutation):
    bundle, value = prepared_bundle()
    artifact = bundle["forecasts"][0]
    if mutation == "payload":
        artifact["prepared"]["forecast"]["days"][0]["wind_max_kmh"] = 999
    elif mutation == "future":
        artifact["prepared"]["forecast"]["fetched_at"] = (value.fetched_at + timedelta(minutes=1)).isoformat()
        artifact["sha256"] = digest(artifact["prepared"])
    else:
        key = "candidate_sha256" if mutation == "candidate" else "normalization"
        artifact["prepared"][key] = "wrong"
        artifact["sha256"] = digest(artifact["prepared"])
    with pytest.raises(WeatherDataInvalid, match="identity"):
        PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)


@pytest.mark.asyncio
async def test_request_uses_frozen_copy_with_no_network_or_campaign_call(monkeypatch):
    import httpx

    from climaprev.tools import experimental_campaign

    bundle, value = prepared_bundle()
    provider = PreparedCandidateForecast(bundle, now=lambda: value.fetched_at)
    def forbidden(*args, **kwargs):
        pytest.fail("delivery attempted an HTTP/campaign operation")
    monkeypatch.setattr(httpx.AsyncClient, "send", forbidden)
    monkeypatch.setattr(experimental_campaign, "run_calendar", forbidden)
    bundle["forecasts"].clear()
    assert await provider.forecast(value.location, value.period) == value
    copy = deepcopy(provider.provenance)
    copy.clear()
    assert len(provider.provenance) == 1
