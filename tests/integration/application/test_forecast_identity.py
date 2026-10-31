from dataclasses import replace
from datetime import timedelta

from climaprev.domain.units import TemperatureUnit
from tests.support.forecast import (
    LOCATION,
    FakeGeocoder,
    FakeProvider,
    InMemoryCache,
    forecast,
    service,
    text_query,
)


async def test_close_coordinates_never_share_a_forecast():
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)
    first = replace(text_query(), location_text=None, latitude=-23.55051, longitude=-46.63331)
    second = replace(first, latitude=-23.55052)
    a = await query_service.execute(first, "a")
    provider.value = replace(forecast(), days=(replace(forecast().days[0], temperature_max_c=30),))
    b = await query_service.execute(second, "b")
    assert a.days[0].temperature_max == 40
    assert b.days[0].temperature_max == 30
    assert b.location.latitude == -23.55052
    assert len(provider.calls) == 2


async def test_same_point_different_display_names_reuses_canonical_data():
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    a = await service(cache=cache, provider=provider).execute(text_query(), "a")
    alias = replace(LOCATION, name="Centro", source="alternate", timezone="UTC")
    b = await service(cache=cache, provider=provider, geocoder=FakeGeocoder(alias)).execute(
        replace(text_query(), location_text="Centro"), "b")
    assert len(provider.calls) == 1
    assert b.location.name == "Centro"
    assert b.location.source == "alternate"
    assert b.location.timezone == "America/Sao_Paulo"
    assert b.days == a.days
    assert b.cache_status == "hit"


async def test_another_period_fetches_its_own_data():
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)
    await query_service.execute(text_query(), "a")
    query = replace(text_query(), start_date=text_query().start_date + timedelta(days=1),
                    end_date=text_query().end_date + timedelta(days=1))
    result = await query_service.execute(query, "b")
    assert result.period.start == query.start_date
    assert len(provider.calls) == 2


async def test_another_destination_never_reads_previous_provider_cache():
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    await service(cache=cache, provider=provider).execute(text_query(), "a")
    provider.value = replace(forecast(), days=(replace(forecast().days[0], temperature_max_c=30),))
    result = await service(cache=cache, provider=provider,
                           provider_identity="https://alternate.test/private").execute(text_query(), "b")
    assert len(provider.calls) == 2
    assert result.days[0].temperature_max == 30
    keys = [key for key in cache.entries if key.startswith("forecast:")]
    assert len(keys) == 2
    assert all(key.startswith("forecast:v2:") and len(key.removeprefix("forecast:v2:")) == 64
               for key in keys)
    assert all("alternate" not in key and "23.5505" not in key for key in keys)


async def test_output_units_share_canonical_cache():
    cache = InMemoryCache()
    provider = FakeProvider(forecast())
    query_service = service(cache=cache, provider=provider)
    a = await query_service.execute(text_query(), "a")
    b = await query_service.execute(text_query(unit=TemperatureUnit.FAHRENHEIT), "b")
    assert len(provider.calls) == 1
    assert a.days[0].temperature_max == 40
    assert b.days[0].temperature_max == 104
    assert b.cache_status == "hit"
