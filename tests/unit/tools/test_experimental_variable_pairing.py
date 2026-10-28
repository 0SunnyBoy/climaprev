from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.experimental_pairing import pair_variable_days


def inputs(day=date(2030, 1, 1), zone="UTC", instant=False):
    tz = ZoneInfo(zone)
    start = datetime.combine(day, time.min, tz).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, tz).astimezone(UTC)
    count = int((end - start).total_seconds() / 3600)
    forecast, observed = [], []
    for index in range(count):
        left, right = start + timedelta(hours=index), start + timedelta(hours=index + 1)
        forecast.append(Measurement("temperature_c", left, None if instant else right,
                                    25 + index / 10, "°C", "instant" if instant else "previous_hour_max"))
        observed.append(asdict(Measurement("temperature_max_c", left, right, 24, "°C",
                                            "observed_previous_hour_max")))
    observation = {"station": {"code": "SYN", "latitude": 0, "longitude": 0},
                   "measurements": observed, "source_fields": {"temperature_max_c": "synthetic-max"},
                   "source_sha256": "synthetic-source"}
    location = CanonicalLocation("Synthetic", 0, 0, zone, "fixture")
    return forecast, observation, location, DatePeriod(day, day), start, end


def pair(data, *, instant=False, reference=None):
    forecast, observed, location, period, start, _ = data
    return pair_variable_days(
        forecast, observed, location, period, variable="temperature_max_c",
        forecast_variable="temperature_c", unit="°C", aggregation="max",
        forecast_semantics="instant" if instant else "previous_hour_max",
        observed_semantics="observed_previous_hour_max", model="synthetic-model",
        collected_at=start - timedelta(days=1), equivalence_reference=reference,
    )


def test_equivalent_interval_extremes_remain_comparable_with_known_values():
    result = pair(inputs())
    row = result["rows"][0]
    assert row["forecast"] == 27.3
    assert row["observed"] == 24
    assert row["eligible_exploratory"] is True
    assert row["eligible_confirmatory"] is True
    assert row["comparable_as_identical_measurement"] is True
    assert result["scientific_approval"] is False


def test_instant_extrema_are_diagnostic_without_explicit_equivalence_reference():
    data = inputs(instant=True)
    row = pair(data, instant=True)["rows"][0]
    assert row["eligible_exploratory"] is True
    assert row["eligible_confirmatory"] is False
    assert row["comparable_as_identical_measurement"] is False
    approved_contract = pair(data, instant=True, reference="synthetic-reviewed-equivalence")
    assert approved_contract["rows"][0]["eligible_confirmatory"] is True
    assert approved_contract["equivalence_reference"] == "synthetic-reviewed-equivalence"


@pytest.mark.parametrize("day,hours", [(date(2026, 3, 8), 23), (date(2026, 11, 1), 25)])
def test_pairing_respects_actual_local_day_duration(day, hours):
    data = inputs(day, "America/New_York")
    result = pair(data)
    row = result["rows"][0]
    assert (datetime.fromisoformat(row["end_utc"]) - datetime.fromisoformat(row["start_utc"])).total_seconds() == hours * 3600
    assert row["eligible_exploratory"] is True


def test_missing_boundary_excludes_only_the_incomplete_variable():
    data = inputs()
    data[1]["measurements"].pop()
    row = pair(data)["rows"][0]
    assert row["forecast"] == 27.3
    assert row["observed"] is None
    assert row["eligible_exploratory"] is False
    assert row["exclusions"] == ["incomplete_observation_interval"]


def test_next_midnight_is_included_for_intervals_and_outside_instant_ignored():
    data = inputs()
    data[0].append(Measurement("temperature_c", data[-1], data[-1] + timedelta(hours=1),
                               999, "°C", "previous_hour_max"))
    assert pair(data)["rows"][0]["forecast"] == 27.3


def test_negative_temperature_minimum_remains_valid_in_both_sources():
    forecast, observed, location, period, start, _ = inputs()
    forecast = [Measurement("temperature_c", m.start, m.end, -3, "°C", "previous_hour_min")
                for m in forecast]
    observed["measurements"] = [asdict(Measurement("temperature_min_c", m["start"], m["end"],
                                                   -5, "°C", "observed_previous_hour_min"))
                                for m in observed["measurements"]]
    observed["source_fields"] = {"temperature_min_c": "synthetic-min"}
    row = pair_variable_days(
        forecast, observed, location, period, variable="temperature_min_c",
        forecast_variable="temperature_c", unit="°C", aggregation="min",
        forecast_semantics="previous_hour_min", observed_semantics="observed_previous_hour_min",
        model="synthetic", collected_at=start - timedelta(days=1),
    )["rows"][0]
    assert row["forecast"] == -3
    assert row["observed"] == -5
    assert row["eligible_exploratory"] is True


@pytest.mark.parametrize("aggregation,expected", [("max", None), ("sum", 24)])
def test_six_hour_rain_can_form_daily_total_but_never_an_hourly_maximum(aggregation, expected):
    _, observation, location, period, start, _ = inputs()
    forecast = [Measurement("precipitation_mm", start + timedelta(hours=i),
                            start + timedelta(hours=i + 6), 6, "mm", "next_6_hours_sum")
                for i in range(0, 24, 6)]
    observation["measurements"] = [asdict(Measurement("precipitation_mm", start + timedelta(hours=i),
                                                      start + timedelta(hours=i + 1), 1, "mm",
                                                      "observed_previous_hour_sum")) for i in range(24)]
    observation["source_fields"] = {"precipitation_mm": "synthetic-hourly-rain"}
    row = pair_variable_days(
        forecast, observation, location, period, variable="precipitation_mm", unit="mm",
        aggregation=aggregation, forecast_semantics="next_6_hours_sum",
        observed_semantics="observed_previous_hour_sum", model="synthetic-six-hour",
        collected_at=start - timedelta(days=1),
    )["rows"][0]
    assert row["forecast"] == expected
    assert row["eligible_exploratory"] is (expected is not None)
