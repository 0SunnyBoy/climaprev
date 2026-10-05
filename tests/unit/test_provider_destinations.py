import pytest
from pydantic import ValidationError

from climaprev.config import Settings


@pytest.mark.parametrize(
    "field",
    [
        "forecast_base_url",
        "geocoding_base_url",
        "historical_forecast_base_url",
        "historical_weather_base_url",
        "inmet_alerts_base_url",
    ],
)
@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example",
        "http://api.open-meteo.com",
        "https://user:SentinelSecret@api.open-meteo.com",
        "https://api.open-meteo.com/#SentinelSecret",
        "https://api.open-meteo.com:444",
        "https://api.open-meteo.com:bad",
        "https://api.open-meteo.com/?token=SentinelSecret",
    ],
)
def test_production_rejects_unapproved_destinations_without_echo(field: str, url: str) -> None:
    with pytest.raises(ValidationError) as raised:
        Settings(environment="production", **{field: url})
    assert "invalid production provider destination" in str(raised.value)
    assert url not in str(raised.value)
    assert "SentinelSecret" not in str(raised.value)


def test_production_accepts_defaults_and_explicit_allowlist(production_config) -> None:
    assert Settings(environment="production", **production_config).forecast_base_url == "https://api.open-meteo.com"
    assert Settings(environment="production", **production_config).inmet_alerts_base_url == (
        "https://apiprevmet3.inmet.gov.br"
    )
    settings = Settings(
        environment="production",
        provider_allowed_hosts=("weather.example",),
        forecast_base_url="https://weather.example:443/v1",
        geocoding_base_url="https://weather.example/geo",
        historical_forecast_base_url="https://weather.example/historical-forecast",
        historical_weather_base_url="https://weather.example/historical-weather",
        inmet_alerts_base_url="https://weather.example/alerts",
        **production_config,
    )
    assert settings.forecast_base_url == "https://weather.example:443/v1"


@pytest.mark.parametrize(
    "environment,url", [("load", "http://provider-mock:8080"), ("test", "https://forecast.test")]
)
def test_explicit_nonproduction_mocks_remain_supported(environment: str, url: str) -> None:
    assert Settings(environment=environment, forecast_base_url=url).forecast_base_url == url
