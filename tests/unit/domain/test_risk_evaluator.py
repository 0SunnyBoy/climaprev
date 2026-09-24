from datetime import UTC, date, datetime

import pytest

from climaprev.domain.models import CanonicalLocation, DailyForecast, DatePeriod, NormalizedForecast
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy


def forecast_for(**changes: float | None) -> NormalizedForecast:
    day = DailyForecast(
        date=date(2026, 8, 28),
        temperature_min_c=changes.get("temperature_min_c", 18.0),
        temperature_max_c=changes.get("temperature_max_c", 28.0),
        temperature_mean_c=23.0,
        humidity_mean_pct=70.0,
        precipitation_sum_mm=changes.get("precipitation_sum_mm", 0.0),
        precipitation_probability_max_pct=0.0,
        precipitation_max_hourly_mm=changes.get("precipitation_max_hourly_mm", 0.0),
        wind_max_kmh=20.0,
        wind_gust_max_kmh=changes.get("wind_gust_max_kmh", 20.0),
        weather_code=0,
    )
    return NormalizedForecast(
        location=CanonicalLocation(
            name="Sao Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            timezone="America/Sao_Paulo",
            source="test",
        ),
        period=DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 28)),
        days=(day,),
        provider="test",
        fetched_at=datetime(2026, 8, 28, tzinfo=UTC),
        is_stale=False,
        missing_fields=(),
    )


def evaluate(**changes: float | None):
    return RiskEvaluator().evaluate(forecast_for(**changes), RiskPolicy())


def test_returns_low_when_no_reliable_value_reaches_a_condition() -> None:
    assessment = evaluate()

    assert assessment.level == "low"
    assert assessment.conditions == ()


@pytest.mark.parametrize(
    ("hourly_rain", "expected_level"),
    [(20.0, "moderate"), (30.0, "high")],
)
def test_evaluates_hourly_heavy_rain_proxy(hourly_rain: float, expected_level: str) -> None:
    assessment = evaluate(precipitation_max_hourly_mm=hourly_rain)
    heavy_rain = next(condition for condition in assessment.conditions if condition.type == "heavy_rain_proxy")

    assert assessment.level == expected_level
    assert heavy_rain.value == hourly_rain
    assert heavy_rain.unit == "mm/h"


def test_evaluates_high_daily_heavy_rain_proxy() -> None:
    assessment = evaluate(precipitation_sum_mm=50.0)
    heavy_rain = next(condition for condition in assessment.conditions if condition.type == "heavy_rain_proxy")

    assert assessment.level == "high"
    assert heavy_rain.value == 50.0
    assert heavy_rain.unit == "mm/day"


@pytest.mark.parametrize(
    ("gust", "expected_level"),
    [(40.0, "moderate"), (61.0, "high")],
)
def test_evaluates_strong_wind_proxy(gust: float, expected_level: str) -> None:
    assessment = evaluate(wind_gust_max_kmh=gust)

    assert assessment.level == expected_level
    assert assessment.conditions[0].type == "strong_wind_proxy"
    assert assessment.conditions[0].value == gust
    assert assessment.conditions[0].unit == "km/h"


@pytest.mark.parametrize(
    ("field", "value", "expected_level"),
    [
        ("temperature_max_c", 35.0, "moderate"),
        ("temperature_max_c", 40.0, "high"),
        ("temperature_min_c", 5.0, "moderate"),
        ("temperature_min_c", 0.0, "high"),
    ],
)
def test_evaluates_temperature_extreme_proxy(
    field: str, value: float, expected_level: str
) -> None:
    assessment = evaluate(**{field: value})

    assert assessment.level == expected_level
    assert assessment.conditions[0].type == "temperature_extreme_proxy"
    assert assessment.conditions[0].value == value
    assert assessment.conditions[0].unit == "celsius"
    assert "indicador" in assessment.conditions[0].reason


def test_derives_flooding_risk_proxy_from_the_highest_rain_band() -> None:
    assessment = evaluate(precipitation_max_hourly_mm=20.0, precipitation_sum_mm=50.0)

    flooding = next(condition for condition in assessment.conditions if condition.type == "flooding_risk_proxy")
    assert flooding.severity == "high"
    assert flooding.value == 50.0
    assert flooding.unit == "mm/day"
    assert "avaliação hidrológica local" in flooding.reason


def test_high_condition_takes_precedence_over_moderate_conditions() -> None:
    assessment = evaluate(precipitation_max_hourly_mm=20.0, wind_gust_max_kmh=61.0)

    assert assessment.level == "high"


def test_ignores_missing_values_without_treating_them_as_zero() -> None:
    assessment = evaluate(
        temperature_min_c=None,
        temperature_max_c=None,
        precipitation_sum_mm=None,
        precipitation_max_hourly_mm=None,
        wind_gust_max_kmh=None,
    )

    assert assessment.level == "low"
    assert assessment.conditions == ()


def test_returns_the_forecast_heuristic_method_and_policy_version() -> None:
    assessment = evaluate(precipitation_max_hourly_mm=20.0)

    assert assessment.method == "forecast_heuristic"
    assert assessment.policy_version == "reference-v1"


def test_orders_conditions_deterministically_by_type() -> None:
    assessment = evaluate(
        temperature_max_c=35.0,
        precipitation_max_hourly_mm=20.0,
        wind_gust_max_kmh=40.0,
    )

    assert [condition.type for condition in assessment.conditions] == [
        "flooding_risk_proxy",
        "heavy_rain_proxy",
        "strong_wind_proxy",
        "temperature_extreme_proxy",
    ]
