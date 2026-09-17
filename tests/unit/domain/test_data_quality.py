from datetime import UTC, date, datetime

import pytest

from climaprev.domain.data_quality import completeness
from climaprev.domain.models import CanonicalLocation, DailyForecast, DatePeriod, NormalizedForecast


@pytest.mark.parametrize("state,expected", [("zero", "complete"), ("none", "unavailable"),
                                           ("gap", "partial")])
def test_completeness_depends_on_policy_inputs_and_coverage(state, expected):
    value = None if state == "none" else 0
    day = DailyForecast(
        date=date(2026, 8, 28), temperature_min_c=value, temperature_max_c=value,
        temperature_mean_c=None, humidity_mean_pct=None, precipitation_sum_mm=value,
        precipitation_probability_max_pct=None, precipitation_max_hourly_mm=value,
        wind_max_kmh=None, wind_gust_max_kmh=value, weather_code=None,
    )
    forecast = NormalizedForecast(
        location=CanonicalLocation("Test", 0, 0, "UTC", "coordinates"),
        period=DatePeriod(day.date, day.date), days=(day,), provider="fixture",
        fetched_at=datetime(2026, 8, 28, tzinfo=UTC), is_stale=False,
        missing_fields=("hourly.2026-08-28.precipitation.coverage",) if state == "gap" else (),
    )
    assert completeness(forecast) == expected
