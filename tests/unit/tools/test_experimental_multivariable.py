from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pytest
from tests.support.station_csv import station_variables_csv as csv_data

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_multivariable import (
    compare_variable_reports,
    pair_station_variable,
)
from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.experimental_observations import (
    qualify_observation_window,
    station_variable_measurements,
)

DAY = date(2024, 1, 2)
START = datetime(2024, 1, 2, tzinfo=UTC)
LOCATION = CanonicalLocation("Synthetic", 0, 0, "UTC", "test")


def report(model="baseline", value=9.2, *, target="gust_previous_hour_max", raw=None):
    variable, unit, semantics = {
        "temperature_instant": ("temperature_c", "°C", "instant"),
        "humidity_instant": ("humidity_pct", "%", "instant"),
        "gust_previous_hour_max": ("gust_kmh", "km/h", "previous_hour_max"),
        "temperature_previous_hour_max": ("temperature_c", "°C", "instant"),
        "temperature_previous_hour_mean": ("temperature_c", "°C", "previous_hour_mean"),
    }[target]
    samples = [Measurement(variable, START + timedelta(hours=i),
                            START + timedelta(hours=i+1) if semantics != "instant" else None,
                            value, unit, semantics) for i in range(24)]
    return pair_station_variable(samples, LOCATION, raw or csv_data(), "A201", DatePeriod(DAY, DAY),
                                  target=target, model=model, collected_at=START - timedelta(hours=6))


def test_instant_fields_and_gust_units_without_changing_historical_importer():
    metadata, samples = station_variable_measurements(csv_data(), station="A201")
    assert not metadata["optional_fields_missing"]
    assert metadata["sustained_wind"].startswith("withheld")
    assert next(m.value for m in samples if m.variable == "gust_kmh") == pytest.approx(7.2)
    assert next(m.value for m in samples if m.variable == "humidity_pct") == 50


def test_common_sample_metrics_and_explicit_full_planned_coverage():
    result = compare_variable_reports([report(), report("candidate", 8.2)], "baseline")
    assert result["planned_cases"] == result["common_cases"] == 24
    assert result["common_coverage"] == 1
    assert result["models"]["baseline"]["numerical"]["mae"] == pytest.approx(2)
    assert result["models"]["candidate"]["numerical"]["mae"] == pytest.approx(1)
    assert not result["scientific_approval"] and not result["promotion_allowed"]


def test_rows_omitted_by_all_models_do_not_disappear_from_denominator():
    a, b = report(), report("candidate", 21)
    a["rows"].pop()
    b["rows"].pop()
    result = compare_variable_reports([a, b], "baseline")
    assert result["planned_cases"] == 24 and result["common_cases"] == 23
    assert result["models"]["candidate"]["missing_from_plan"] == 1


def test_missing_optional_column_or_sentinel_does_not_become_zero():
    missing = report(target="humidity_instant", raw=csv_data(humidity=False))
    assert all(row["observed_value"] is None for row in missing["rows"])
    partial = report(target="humidity_instant", raw=csv_data(missing=True))
    assert not any(row["eligible_exploratory"] for row in partial["rows"])
    assert "observation_semantics_not_equivalent" in partial["rows"][0]["exclusions"]
    _, samples = station_variable_measurements(csv_data(missing=True), station="A201")
    assert sum(m.value is None for m in samples if m.variable == "humidity_pct") == 1


def test_instantaneous_forecast_is_not_an_hourly_maximum():
    result = report(target="temperature_previous_hour_max")
    assert not any(row["eligible_exploratory"] for row in result["rows"])


@pytest.mark.parametrize("problem", ["duplicate", "source", "observation", "slot", "nonfinite"])
def test_incompatible_or_ambiguous_reports_are_rejected(problem):
    a, b = report(), report("candidate", 21)
    if problem == "duplicate":
        b["rows"].append(deepcopy(b["rows"][0]))
    elif problem == "source":
        b["source_sha256"] = "other"
    elif problem == "observation":
        b["rows"][0]["observed_value"] = 999
    elif problem == "slot":
        b["collected_at"] = (START - timedelta(hours=7)).isoformat()
    else:
        b["rows"][0]["forecast_value"] = float("nan")
    with pytest.raises(ValueError):
        compare_variable_reports([a, b], "baseline")


def test_retrospective_collection_is_recomputed_and_excluded():
    a, b = report(), report("candidate", 21)
    for row in (a, b):
        row["collected_at"] = START.isoformat()
    assert compare_variable_reports([a, b], "baseline")["common_cases"] == 0


def test_coordinates_cannot_be_silently_reassigned():
    with pytest.raises(ValueError, match="source-version"):
        pair_station_variable([], replace(LOCATION, latitude=0.1), csv_data(), "A201",
                              DatePeriod(DAY, DAY), target="humidity_instant", model="test",
                              collected_at=START - timedelta(days=1))


def test_freshness_window_rejects_stale_data_and_missing_humidity():
    metadata, samples = station_variable_measurements(csv_data(), station="A201")
    args = {"start": START, "end": START + timedelta(days=1), "checked_at": START + timedelta(days=2),
            "min_coverage": 0.9}
    fresh = qualify_observation_window(metadata, samples, LOCATION, **args)
    assert fresh["measurement_coverage_ready"]
    assert not fresh["technical_pairing_ready"]  # Coverage is not semantic equivalence.
    args.update(start=START + timedelta(days=30), end=START + timedelta(days=31),
                checked_at=START + timedelta(days=32))
    stale = qualify_observation_window(metadata, samples, LOCATION, **args)
    assert not stale["technical_pairing_ready"]
    assert stale["variables"]["humidity_pct"]["coverage"] == 0


def test_source_hourly_mean_cannot_be_labeled_an_instantaneous_temperature():
    result = report(target="temperature_instant")
    assert not any(row["eligible_exploratory"] for row in result["rows"])
    assert "observation_semantics_not_equivalent" in result["rows"][0]["exclusions"]
    mean = report(value=21, target="temperature_previous_hour_mean")
    assert sum(row["eligible_exploratory"] for row in mean["rows"]) == 24


@pytest.mark.parametrize("day,expected", [(date(2024, 3, 10), 23), (date(2024, 11, 3), 25)])
def test_planned_denominator_respects_local_dst(day, expected):
    result = pair_station_variable([], replace(LOCATION, timezone="America/New_York"), csv_data(),
                                    "A201", DatePeriod(day, day), target="temperature_instant",
                                    model="synthetic", collected_at=START - timedelta(days=1))
    assert result["planned_cases"] == expected
    assert not any(row["eligible_exploratory"] for row in result["rows"])


def test_missing_humidity_blocks_readiness_without_erasing_other_variables():
    metadata, samples = station_variable_measurements(csv_data(humidity=False), station="A201")
    result = qualify_observation_window(metadata, samples, LOCATION, start=START,
                                        end=START + timedelta(days=1),
                                        checked_at=START + timedelta(days=2), min_coverage=0.9)
    assert not result["technical_pairing_ready"]
    assert result["variables"]["humidity_pct"]["coverage"] == 0
    assert result["variables"]["temperature_c"]["coverage"] == 1


@pytest.mark.parametrize("value", [float("nan"), True, -1])
def test_invalid_observation_values_cannot_pass_readiness(value):
    metadata, samples = station_variable_measurements(csv_data(), station="A201")
    samples[0] = replace(samples[0], value=value)
    with pytest.raises(ValueError, match="invalid observation"):
        qualify_observation_window(metadata, samples, LOCATION, start=START,
                                   end=START + timedelta(days=1),
                                   checked_at=START + timedelta(days=2), min_coverage=0.9)
