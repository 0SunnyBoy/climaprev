from datetime import date

import pytest

from climaprev.domain.models import DailyForecast, DatePeriod


def test_date_period_counts_both_boundary_days() -> None:
    period = DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 30))

    assert period.days == 3


def test_date_period_rejects_an_end_before_start() -> None:
    with pytest.raises(ValueError):
        DatePeriod(start=date(2026, 8, 30), end=date(2026, 8, 28))


def test_daily_forecast_preserves_missing_weather_values() -> None:
    forecast = DailyForecast(
        date=date(2026, 8, 28),
        temperature_min_c=None,
        temperature_max_c=None,
        temperature_mean_c=None,
        humidity_mean_pct=None,
        precipitation_sum_mm=None,
        precipitation_probability_max_pct=None,
        precipitation_max_hourly_mm=None,
        wind_max_kmh=None,
        wind_gust_max_kmh=None,
        weather_code=None,
    )

    assert forecast.temperature_mean_c is None
    assert forecast.precipitation_sum_mm is None
    assert forecast.weather_code is None
