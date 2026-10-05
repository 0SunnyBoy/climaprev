from datetime import UTC, date, datetime

import pytest

from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.models import CanonicalLocation, DailyForecast, DatePeriod, NormalizedForecast


def _forecast() -> NormalizedForecast:
    return NormalizedForecast(
        location=CanonicalLocation("Sao Paulo", -23.55, -46.63, "America/Sao_Paulo", "test"),
        period=DatePeriod(date(2026, 1, 1), date(2026, 1, 1)),
        days=(
            DailyForecast(
                date=date(2026, 1, 1),
                temperature_min_c=20.0,
                temperature_max_c=30.0,
                temperature_mean_c=25.0,
                humidity_mean_pct=70.0,
                precipitation_sum_mm=10.0,
                precipitation_probability_max_pct=50.0,
                precipitation_max_hourly_mm=4.0,
                wind_max_kmh=20.0,
                wind_gust_max_kmh=30.0,
                weather_code=1,
            ),
        ),
        provider="test",
        fetched_at=datetime(2026, 1, 1, tzinfo=UTC),
        is_stale=False,
        missing_fields=(),
    )


def test_disabled_calibration_preserves_provider_forecast() -> None:
    forecast = _forecast()

    assert ForecastCalibration.disabled().apply(forecast) == forecast


def test_enabled_calibration_applies_reviewed_profile_without_changing_probability() -> None:
    calibrated = ForecastCalibration(
        profile_version="reviewed-2026-01",
        enabled=True,
        temperature_offset_c=-1.0,
        precipitation_multiplier=1.2,
        wind_multiplier=0.8,
    ).apply(_forecast())

    day = calibrated.days[0]
    assert day.temperature_max_c == 29.0
    assert day.precipitation_sum_mm == 12.0
    assert day.wind_gust_max_kmh == 24.0
    assert day.precipitation_probability_max_pct == 50.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"profile_version": ""},
        {"precipitation_multiplier": -1.0},
        {"wind_multiplier": float("nan")},
    ],
)
def test_calibration_rejects_invalid_profiles(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ForecastCalibration(**kwargs)  # type: ignore[arg-type]
