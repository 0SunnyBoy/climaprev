from datetime import UTC, datetime, timedelta

from climaprev.tools.experimental_measurement_review import MeasurementContext, review_measurement
from climaprev.tools.experimental_normalization import Measurement

START = datetime(2030, 1, 1, tzinfo=UTC)


def test_native_wind_mean_contract_is_distinct_from_instantaneous_wind():
    context = MeasurementContext("declared-test", 0, 0, 10., True)
    forecast = Measurement("wind_kmh", START, START+timedelta(minutes=10), 10., "km/h", "previous_10_minute_mean")
    observed = Measurement("wind_kmh", START, START+timedelta(minutes=10), 11., "km/h", "observed_previous_10_minute_mean")
    result = review_measurement("wind_previous_10_minute_mean", forecast, observed,
                                forecast_context=context, observation_context=context)
    assert result["declared_instrumental_review_complete"]
    assert not result["context_authenticity_verified"] and not result["promotion_allowed"]
    instant = Measurement("wind_kmh", START, None, 10., "km/h", "instant")
    rejected = review_measurement("wind_previous_10_minute_mean", instant, observed,
                                  forecast_context=context, observation_context=context)
    assert not rejected["measurement_contract_compatible"]


def test_unknown_heights_and_representativeness_remain_blockers_even_for_matching_gusts():
    forecast = Measurement("gust_kmh", START, START+timedelta(hours=1), 40., "km/h", "previous_hour_max")
    observed = Measurement("gust_kmh", START, START+timedelta(hours=1), 41., "km/h", "observed_previous_hour_max")
    context = MeasurementContext("declared-test", 0, 0)
    result = review_measurement("gust_previous_hour_max", forecast, observed,
                                forecast_context=context, observation_context=context)
    assert result["measurement_contract_compatible"]
    assert not result["declared_instrumental_review_complete"]
    assert result["metadata_exclusions"] == ["sensor_height_unknown", "representativeness_not_reviewed"]


def test_temperature_hourly_mean_is_not_instantaneous_and_height_is_not_inferred():
    forecast = Measurement("temperature_c", START, None, 25., "°C", "instant")
    observed = Measurement("temperature_c", START, START+timedelta(hours=1), 25., "°C", "observed_previous_hour_mean")
    result = review_measurement("temperature_instant", forecast, observed,
                                forecast_context=MeasurementContext("model", 0, 0, 2., True),
                                observation_context=MeasurementContext("station", 1, 0, 10., True))
    assert not result["measurement_contract_compatible"]
    assert "sensor_height_mismatch" in result["metadata_exclusions"]
    assert "point_version_mismatch" in result["metadata_exclusions"]


def test_rain_accumulation_does_not_invent_a_forecast_sensor_height_requirement():
    forecast = Measurement("precipitation_mm", START, START+timedelta(hours=1), 5., "mm", "previous_hour_sum")
    observed = Measurement("precipitation_mm", START, START+timedelta(hours=1), 5., "mm", "observed_previous_hour_sum")
    context = MeasurementContext("declared-rain-test", 0, 0, representativeness_reviewed=True)
    result = review_measurement("rain_accumulation", forecast, observed,
                                forecast_context=context, observation_context=context)
    assert result["declared_instrumental_review_complete"]
    assert not result["scientific_approval"]
