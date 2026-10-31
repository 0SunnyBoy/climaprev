from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from climaprev.tools.experimental_equivalence import check_equivalence
from climaprev.tools.experimental_normalization import Measurement

START = datetime(2026, 10, 27, 12, tzinfo=UTC)
FORECAST = Measurement("precipitation_mm", START, START + timedelta(hours=1), 2,
                       "mm", "previous_hour_sum")
OBSERVED = replace(FORECAST, semantics="observed_previous_hour_sum")


def test_hourly_rain_uses_equal_intervals_without_requiring_equal_values():
    result = check_equivalence("rain_accumulation", FORECAST, replace(OBSERVED, value=3))
    assert result.compatible_measurements
    assert not result.scientific_approval
    assert not result.promotion_allowed


def test_offsets_representing_same_instant_are_compatible():
    zone = timezone(timedelta(hours=-3))
    observation = replace(OBSERVED, start=START.astimezone(zone),
                          end=(START + timedelta(hours=1)).astimezone(zone))
    assert check_equivalence("rain_accumulation", FORECAST, observation).compatible_measurements


@pytest.mark.parametrize("value", [None, -1, float("nan"), float("inf"), True])
def test_missing_or_invalid_values_are_never_eligible(value):
    assert not check_equivalence("rain_accumulation", replace(FORECAST, value=value),
                                 OBSERVED).compatible_measurements


@pytest.mark.parametrize("changes", [
    {"unit": "m"}, {"variable": "gust_kmh"}, {"semantics": "instant"},
    {"end": None}, {"start": START + timedelta(hours=1)},
    {"start": START.replace(tzinfo=None)},
    {"end": (START + timedelta(hours=1)).replace(tzinfo=None)},
])
def test_contract_mismatches_are_explicit(changes):
    result = check_equivalence("rain_accumulation", replace(FORECAST, **changes), OBSERVED)
    assert not result.compatible_measurements
    assert result.exclusions


def test_six_hour_rain_is_not_silently_prorated_to_one_hour():
    forecast = replace(FORECAST, end=START + timedelta(hours=6), semantics="next_6_hours_sum")
    assert not check_equivalence("rain_accumulation", forecast, OBSERVED).compatible_measurements


def test_forecast_and_observation_roles_are_not_interchangeable():
    assert not check_equivalence("rain_accumulation", OBSERVED, FORECAST).compatible_measurements


@pytest.mark.parametrize("target,variable,unit,semantics", [
    ("gust_previous_hour_max", "gust_kmh", "km/h", "previous_hour_max"),
    ("temperature_previous_hour_max", "temperature_c", "°C", "previous_hour_max"),
    ("temperature_previous_hour_min", "temperature_c", "°C", "previous_hour_min"),
])
def test_matching_hourly_extrema_contracts(target, variable, unit, semantics):
    forecast = replace(FORECAST, variable=variable, unit=unit, semantics=semantics)
    observation = replace(forecast, semantics="observed_" + semantics)
    assert check_equivalence(target, forecast, observation).compatible_measurements
    instant = replace(forecast, end=None, semantics="instant")
    assert not check_equivalence(target, instant, observation).compatible_measurements


def test_humidity_requires_an_actual_instantaneous_observation_contract():
    forecast = replace(FORECAST, variable="humidity_pct", unit="%", value=80,
                       end=None, semantics="instant")
    observed = replace(forecast, semantics="observed_instant")
    assert check_equivalence("humidity_instant", forecast, observed).compatible_measurements
    assert not check_equivalence("humidity_instant", replace(forecast, value=101),
                                 observed).compatible_measurements


def test_negative_temperature_is_valid_and_sustained_wind_is_not_gust():
    forecast = Measurement("temperature_c", START, None, -4, "°C", "instant")
    observed = replace(forecast, semantics="observed_instant")
    assert check_equivalence("temperature_instant", forecast, observed).compatible_measurements
    with pytest.raises(ValueError, match="wind averaging"):
        check_equivalence("wind_instant", FORECAST, OBSERVED)
