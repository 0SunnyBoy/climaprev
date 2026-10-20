from datetime import date

import httpx
import pytest
import respx

from climaprev.config import Settings
from climaprev.tools.validate_historical import HistoricalValidationConfig, collect_and_validate


def _hourly(*, suffix: str, gust: list[float]) -> dict[str, object]:
    return {
        "time": [f"2026-01-01T{hour:02d}:00" for hour in range(24)],
        f"temperature_2m{suffix}": [20.0, 25.0, 30.0] + [30.0] * 21,
        f"relative_humidity_2m{suffix}": [70.0] * 24,
        f"precipitation{suffix}": [0.0, 1.0, 0.0] + [0.0] * 21,
        f"wind_gusts_10m{suffix}": gust + [gust[-1]] * 21,
        f"weather_code{suffix}": [1.0] * 24,
    }


@pytest.mark.asyncio
@respx.mock
async def test_collects_previous_run_and_observed_weather_without_database() -> None:
    forecast_route = respx.get("https://previous-runs.test/v1/forecast").mock(
        return_value=httpx.Response(
            200,
            json={"timezone": "UTC", "hourly_units": {
                "temperature_2m_previous_day1": "°C", "precipitation_previous_day1": "mm",
                "wind_gusts_10m_previous_day1": "km/h",
            }, "hourly": _hourly(suffix="_previous_day1", gust=[20, 20, 20])},
        )
    )
    observed_route = respx.get("https://archive.test/v1/archive").mock(
        return_value=httpx.Response(
            200,
            json={"timezone": "UTC", "hourly_units": {
                "temperature_2m": "°C", "precipitation": "mm", "wind_gusts_10m": "km/h",
            }, "hourly": _hourly(suffix="", gust=[70, 70, 70])},
        )
    )

    result = await collect_and_validate(
        HistoricalValidationConfig(
            latitude=-1.4558,
            longitude=-48.5044,
            start=date(2026, 1, 1),
            end=date(2026, 1, 1),
            lead_days=1,
        ),
        settings=Settings(
            environment="test",
            historical_forecast_base_url="https://previous-runs.test",
            historical_weather_base_url="https://archive.test",
        ),
    )

    assert forecast_route.called
    assert observed_route.called
    assert result.cases == 1
    assert result.report.false_negatives == 1
    assert result.report.accuracy == 0.0


def test_historical_collection_is_bounded_and_uses_supported_leads() -> None:
    with pytest.raises(ValueError, match="limited"):
        HistoricalValidationConfig(
            latitude=0,
            longitude=0,
            start=date(2026, 1, 1),
            end=date(2026, 2, 2),
            lead_days=1,
        )

    with pytest.raises(ValueError, match="between 1 and 7"):
        HistoricalValidationConfig(
            latitude=0,
            longitude=0,
            start=date(2026, 1, 1),
            end=date(2026, 1, 1),
            lead_days=8,
        )
