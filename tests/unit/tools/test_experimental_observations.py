from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pytest
from tests.support.experiment import station_csv

from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.experimental_observations import (
    pair_temperature_instants,
    parse_observations,
)

TEMP = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)"


@pytest.mark.parametrize("text,expected", [("25", 25), ("-5", -5), ("-9999", None), ("", None)])
def test_temperature_import_preserves_hourly_mean_source_and_missing_values(text, expected):
    result = parse_observations(station_csv([TEMP], [[text]]), expected_station="SYN")
    sample = result["measurements"][0]
    assert sample["value"] == expected
    assert sample["unit"] == "°C"
    assert sample["semantics"] == "observed_previous_hour_mean"
    assert sample["start"] == datetime(2030, 1, 1, tzinfo=UTC)
    assert sample["end"] == datetime(2030, 1, 1, 1, tzinfo=UTC)
    assert result["source_fields"]["temperature_c"] == TEMP
    assert len(result["source_sha256"]) == 64


def test_absent_temperature_field_does_not_substitute_hourly_extreme():
    result = parse_observations(station_csv([], [[]]), expected_station="SYN")
    assert result["measurements"] == []
    assert "temperature_c" in result["missing_fields"]


def test_wrong_station_and_duplicate_hours_fail_closed():
    raw = station_csv([TEMP], [["25"]])
    with pytest.raises(ValueError, match="station"):
        parse_observations(raw, expected_station="OTHER")
    duplicated = raw + raw.splitlines()[-1] + b"\n"
    with pytest.raises(ValueError, match="duplicate"):
        parse_observations(duplicated, expected_station="SYN")


def test_true_temperature_instants_pair_only_matching_instants():
    stamp = datetime(2030, 1, 1, 1, tzinfo=UTC)
    observation = {"measurements": [asdict(Measurement("temperature_c", stamp, None, 20,
                                                       "°C", "instant"))],
                   "source_fields": {"temperature_c": "synthetic-point-sensor"},
                   "source_sha256": "synthetic-point-source"}
    forecast = [Measurement("temperature_c", stamp, None, 25, "°C", "instant"),
                Measurement("temperature_c", stamp + timedelta(hours=1), None, 30, "°C", "instant")]
    result = pair_temperature_instants(forecast, observation)
    assert len(result) == 1
    assert result[0]["observed"] == 20
    assert result[0]["forecast"] == 25
    assert result[0]["source_field"] == "synthetic-point-sensor"
    assert result[0]["source_sha256"] == "synthetic-point-source"


def test_inmet_hourly_mean_is_not_silently_paired_as_temperature_instant():
    observation = parse_observations(station_csv([TEMP], [["25"]]), expected_station="SYN")
    point = Measurement("temperature_c", datetime(2030, 1, 1, 1, tzinfo=UTC), None, 25, "°C", "instant")
    assert pair_temperature_instants([point], observation) == []


@pytest.mark.parametrize("value,expected", [("10", 36), ("0", 0), ("-9999", None)])
def test_wind_speed_and_gust_have_separate_units_intervals_and_missing_values(value, expected):
    header = "VENTO, VELOCIDADE HORARIA (m/s)"
    result = parse_observations(station_csv([header], [[value]]), expected_station="SYN",
                                variables=["wind_kmh", "gust_kmh"])
    samples = {row["variable"]: row for row in result["measurements"]}
    assert samples["wind_kmh"]["value"] == expected
    assert samples["wind_kmh"]["unit"] == "km/h"
    assert samples["wind_kmh"]["semantics"] == "observed_previous_10_minute_mean"
    assert samples["wind_kmh"]["start"] == datetime(2030, 1, 1, 0, 50, tzinfo=UTC)
    assert samples["gust_kmh"]["value"] == 36
    assert samples["gust_kmh"]["semantics"] == "observed_previous_hour_max"
    assert samples["gust_kmh"]["start"] == datetime(2030, 1, 1, tzinfo=UTC)


def test_negative_wind_is_rejected_without_replacing_it_with_gust():
    raw = station_csv(["VENTO, VELOCIDADE HORARIA (m/s)"], [["-1"]])
    with pytest.raises(ValueError, match="negative"):
        parse_observations(raw, expected_station="SYN", variables=["wind_kmh"])


@pytest.mark.parametrize("headers", [[], ["VENTO, VELOCIDADE HORARIA (km/h)"]])
def test_missing_or_unknown_wind_unit_excludes_wind_only(headers):
    raw = station_csv(headers, [["10"]] if headers else [[]])
    result = parse_observations(raw, expected_station="SYN", variables=["wind_kmh", "gust_kmh"])
    assert result["missing_fields"] == ["wind_kmh"]
    assert [row["variable"] for row in result["measurements"]] == ["gust_kmh"]
