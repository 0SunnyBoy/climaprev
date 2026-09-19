from __future__ import annotations

from datetime import UTC, date

import httpx
import pytest
import respx

from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.infrastructure.providers.open_meteo import (
    LocationNotFound,
    OpenMeteoForecastClient,
    OpenMeteoGeocodingClient,
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from tests.contract.providers.test_open_meteo_payload import (
    valid_forecast_payload,
    valid_geocoding_payload,
)

GEOCODING_BASE_URL = "https://geocoding.test"
FORECAST_BASE_URL = "https://forecast.test"


def settings(**overrides: object) -> Settings:
    return Settings(
        geocoding_base_url=GEOCODING_BASE_URL,
        forecast_base_url=FORECAST_BASE_URL,
        **overrides,
    )


def location() -> CanonicalLocation:
    return CanonicalLocation(
        name="Rio de Janeiro",
        latitude=-22.90642,
        longitude=-43.18223,
        timezone="America/Sao_Paulo",
        source="open-meteo-geocoding",
    )


def period() -> DatePeriod:
    return DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 29))


@pytest.mark.asyncio
async def test_geocoding_selects_the_first_complete_result_and_sends_portuguese_query() -> None:
    payload = valid_geocoding_payload()
    payload["results"].insert(
        0,
        {"name": "Rio incompleto", "latitude": -22.9, "longitude": -43.1},
    )
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock(assert_all_called=True) as mock:
            route = mock.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json=payload)

            result = await adapter.resolve("Rio de Janeiro")

    assert route.called
    assert route.calls[0].request.url.params["name"] == "Rio de Janeiro"
    assert route.calls[0].request.url.params["language"] == "pt"
    assert result == location()


@pytest.mark.asyncio
async def test_geocoding_maps_an_empty_result_to_location_not_found() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json={"results": []})

            with pytest.raises(LocationNotFound):
                await adapter.resolve("Lugar inexistente")


@pytest.mark.asyncio
async def test_geocoding_search_returns_context_for_ambiguous_candidates() -> None:
    payload = valid_geocoding_payload()
    payload["results"].append(
        {
            "name": "Rio de Janeiro",
            "latitude": -22.9,
            "longitude": -43.2,
            "timezone": "America/Sao_Paulo",
            "admin1": "Rio de Janeiro",
            "country": "Brasil",
        }
    )
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json=payload)

            results = await adapter.search("Rio")

    assert len(results) == 2
    assert results[1].name == "Rio de Janeiro, Rio de Janeiro, Brasil"


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{}, {"results": None}], ids=["missing", "null"])
async def test_geocoding_rejects_missing_or_null_results_as_invalid_weather_data(
    payload: dict[str, object],
) -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.resolve("Rio de Janeiro")


@pytest.mark.asyncio
async def test_geocoding_rejects_an_invalid_iana_timezone() -> None:
    payload = valid_geocoding_payload()
    payload["results"][0]["timezone"] = "Invalid/Timezone"
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.resolve("Rio de Janeiro")


@pytest.mark.asyncio
async def test_geocoding_maps_a_malformed_timezone_key_to_weather_data_invalid() -> None:
    payload = valid_geocoding_payload()
    payload["results"][0]["timezone"] = "../America/Sao_Paulo"
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.resolve("Rio de Janeiro")


@pytest.mark.asyncio
async def test_forecast_normalizes_open_meteo_data_and_sends_required_parameters() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock(assert_all_called=True) as mock:
            route = mock.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(
                200,
                json=valid_forecast_payload(),
            )

            result = await adapter.forecast(location(), period())

    params = route.calls[0].request.url.params
    assert params["latitude"] == "-22.90642"
    assert params["longitude"] == "-43.18223"
    assert params["start_date"] == "2026-08-28"
    assert params["end_date"] == "2026-08-29"
    assert params["timezone"] == "auto"
    assert "forecast_days" not in params
    assert params["temperature_unit"] == "celsius"
    assert params["precipitation_unit"] == "mm"
    assert params["wind_speed_unit"] == "kmh"
    assert params["daily"] == (
        "temperature_2m_min,temperature_2m_max,precipitation_sum,"
        "precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,weather_code"
    )
    assert params["hourly"] == (
        "temperature_2m,relative_humidity_2m,precipitation,precipitation_probability"
    )
    assert result.provider == "open-meteo"
    assert result.fetched_at.tzinfo is UTC
    assert result.location == location()
    assert result.period == period()
    assert result.days[0].temperature_min_c == 16.0
    assert result.days[0].temperature_max_c == 25.0
    assert result.days[0].temperature_mean_c == 21.5
    assert result.days[0].humidity_mean_pct == 75.0
    assert result.days[0].precipitation_sum_mm == 1.2
    assert result.days[0].precipitation_probability_max_pct == 40.0
    assert result.days[0].precipitation_max_hourly_mm == 1.2
    assert result.days[0].wind_max_kmh == 18.0
    assert result.days[0].wind_gust_max_kmh == 32.0
    assert result.days[0].weather_code == 3
    assert result.days[1].humidity_mean_pct == 65.0
    assert result.days[1].precipitation_probability_max_pct == 55.0
    assert result.days[1].precipitation_max_hourly_mm == 2.5


@pytest.mark.asyncio
async def test_forecast_accepts_the_valid_utc_timezone() -> None:
    payload = valid_forecast_payload()
    payload["timezone"] = "UTC"
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)
            result = await adapter.forecast(location(), period())

    assert result.fetched_at.tzinfo is UTC


@pytest.mark.asyncio
async def test_forecast_preserves_missing_series_as_none_instead_of_zero() -> None:
    payload = valid_forecast_payload()
    del payload["daily"]["precipitation_probability_max"]
    del payload["hourly"]["relative_humidity_2m"]
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)
            result = await adapter.forecast(location(), period())

    assert result.days[0].humidity_mean_pct is None
    assert result.days[0].precipitation_probability_max_pct == 40.0
    assert "daily.precipitation_probability_max" in result.missing_fields
    assert "hourly.relative_humidity_2m" in result.missing_fields


@pytest.mark.asyncio
async def test_forecast_aggregates_precipitation_probability_from_hourly_values() -> None:
    payload = valid_forecast_payload()
    payload["daily"]["precipitation_probability_max"][0] = 40
    payload["hourly"]["precipitation_probability"][0] = 85
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)
            result = await adapter.forecast(location(), period())

    assert result.days[0].precipitation_probability_max_pct == 85.0


@pytest.mark.asyncio
async def test_forecast_marks_hourly_data_that_omits_a_requested_day_as_partial() -> None:
    payload = valid_forecast_payload()
    for values in payload["hourly"].values():
        del values[2:]
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)

            result = await adapter.forecast(location(), period())

    assert result.days[1].precipitation_max_hourly_mm is None
    assert "hourly.2026-08-29.precipitation.coverage" in result.missing_fields


@pytest.mark.asyncio
async def test_forecast_rejects_hourly_data_outside_the_requested_period() -> None:
    payload = valid_forecast_payload()
    for field, values in payload["hourly"].items():
        if field == "time":
            values.append("2026-08-30T00:00")
        else:
            values.append(values[-1])
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.forecast(location(), period())


@pytest.mark.asyncio
async def test_forecast_rejects_an_invalid_iana_timezone() -> None:
    payload = valid_forecast_payload()
    payload["timezone"] = "Invalid/Timezone"
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.forecast(location(), period())


@pytest.mark.asyncio
async def test_forecast_rejects_misaligned_hourly_series() -> None:
    payload = valid_forecast_payload()
    payload["hourly"]["precipitation"].pop()
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock:
            respx.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.forecast(location(), period())


@pytest.mark.asyncio
async def test_geocoding_maps_invalid_json_to_weather_data_invalid() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(200, content=b"not json")

            with pytest.raises(WeatherDataInvalid):
                await adapter.resolve("Rio de Janeiro")


@pytest.mark.asyncio
async def test_geocoding_maps_a_404_to_a_permanent_provider_error() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings())
        with respx.mock:
            respx.get(f"{GEOCODING_BASE_URL}/v1/search").respond(404, json={"error": True})

            with pytest.raises(ProviderPermanentError):
                await adapter.resolve("Rio de Janeiro")


@pytest.mark.asyncio
async def test_geocoding_retries_a_503_only_for_configured_additional_attempts() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingClient(client, settings(additional_retries=2))
        with respx.mock(assert_all_called=True) as mock:
            route = mock.get(f"{GEOCODING_BASE_URL}/v1/search").respond(503, json={"error": True})

            with pytest.raises(ProviderTransientError):
                await adapter.resolve("Rio de Janeiro")

    assert route.call_count == 3


@pytest.mark.asyncio
async def test_forecast_omits_forecast_days_when_dates_are_explicit() -> None:
    long_period = DatePeriod(start=date(2026, 8, 1), end=date(2026, 8, 17))
    payload = valid_forecast_payload()
    payload["daily"]["time"] = [long_period.start.isoformat()] * long_period.days
    for field, values in payload["daily"].items():
        if field != "time":
            payload["daily"][field] = [values[0]] * long_period.days
    payload["hourly"] = {
        field: ([long_period.start.isoformat() + "T00:00"] if field == "time" else [values[0]])
        for field, values in payload["hourly"].items()
    }
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoForecastClient(client, settings())
        with respx.mock(assert_all_called=True) as mock:
            route = mock.get(f"{FORECAST_BASE_URL}/v1/forecast").respond(200, json=payload)

            with pytest.raises(WeatherDataInvalid):
                await adapter.forecast(location(), long_period)

    assert "forecast_days" not in route.calls[0].request.url.params


def test_settings_reads_http_values_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLIMAPREV_CONNECT_TIMEOUT_SECONDS", "1.5")
    monkeypatch.setenv("CLIMAPREV_READ_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("CLIMAPREV_ADDITIONAL_RETRIES", "1")

    configured = Settings()

    assert configured.connect_timeout_seconds == 1.5
    assert configured.read_timeout_seconds == 4.5
    assert configured.additional_retries == 1


def test_settings_clamps_additional_retries_to_the_two_attempt_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIMAPREV_ADDITIONAL_RETRIES", "9")

    configured = Settings()

    assert configured.additional_retries == 2
