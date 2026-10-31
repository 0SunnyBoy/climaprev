from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest

from climaprev.tools.compare_station_variables import compare_variables, main


def fixtures():
    text = ("ESTACAO:;BELEM\nCODIGO (WMO):;A201\nLATITUDE:;-1.4\n"
            "LONGITUDE:;-48.4\nALTITUDE:;10\n"
            "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
            "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
            "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C);\n")
    for hour in range(4, 28):
        stamp = datetime(2025, 1, 1) + timedelta(hours=hour)
        text += f"{stamp:%Y/%m/%d};{stamp:%H%M} UTC;0;10;30;20;\n"
    observed = {
        "timezone": "America/Belem", "utc_offset_seconds": -10800,
        "latitude": -1.5, "longitude": -48.5,
        "hourly_units": {"temperature_2m": "°C", "wind_gusts_10m": "km/h"},
        "hourly": {"time": [(datetime(2025, 1, 1) + timedelta(hours=index)).isoformat()
                            for index in range(25)],
                   "temperature_2m": [25.0] * 25, "wind_gusts_10m": [40.0] * 25},
    }
    forecast = deepcopy(observed)
    for name in ("hourly", "hourly_units"):
        forecast[name] = {key + "_previous_day1" if key != "time" else key: value
                          for key, value in forecast[name].items()}
    return {"configuration": {"start": "2025-01-01", "end": "2025-01-01",
                              "timezone": "America/Belem", "lead_days": 1},
            "observed": observed, "forecast": forecast}, text.encode()


def test_temperature_instants_and_gust_interval_endpoints_use_distinct_windows():
    dataset, raw = fixtures()
    dataset["observed"]["hourly"]["temperature_2m"][0] = 19
    dataset["observed"]["hourly"]["temperature_2m"][-1] = 100
    dataset["observed"]["hourly"]["wind_gusts_10m"][0] = 999
    dataset["observed"]["hourly"]["wind_gusts_10m"][-1] = 45
    dataset["forecast"]["hourly"]["wind_gusts_10m_previous_day1"][0] = 999
    dataset["forecast"]["hourly"]["wind_gusts_10m_previous_day1"][-1] = 45
    result = compare_variables(dataset, raw, expected_station="A201")
    assert result["variables"]["temperature_min_c"]["cases"][0]["observed"] == 19
    assert result["variables"]["temperature_max_c"]["cases"][0]["observed"] == 25
    assert result["variables"]["gust_kmh"]["cases"][0]["observed"] == 999
    assert result["variables"]["gust_kmh"]["cases"][0]["forecast"] == 45
    assert result["variables"]["gust_kmh"]["metrics"]["forecast"]["bias"] == 9
    assert not result["calibration_ready"]
    assert not result["variables"]["temperature_max_c"]["comparable_as_identical_measurement"]


def test_missing_boundary_only_excludes_gust_not_temperature():
    dataset, raw = fixtures()
    for values in dataset["forecast"]["hourly"].values():
        values.pop()
    result = compare_variables(dataset, raw, expected_station="A201")["variables"]
    assert result["gust_kmh"]["paired_days"] == 0
    assert result["gust_kmh"]["metrics"]["forecast"]["mae"] is None
    assert result["temperature_max_c"]["paired_days"] == 1


def test_station_missing_field_only_excludes_matching_variable():
    dataset, raw = fixtures()
    raw = raw.replace(b";0;10;30;20;", b";0;10;-9999;20;", 1)
    result = compare_variables(dataset, raw, expected_station="A201")["variables"]
    assert result["temperature_max_c"]["paired_days"] == 0
    assert result["temperature_min_c"]["paired_days"] == 1
    assert result["gust_kmh"]["paired_days"] == 1


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, -1])
def test_invalid_gust_values_fail_closed(value):
    dataset, raw = fixtures()
    dataset["forecast"]["hourly"]["wind_gusts_10m_previous_day1"][5] = value
    with pytest.raises(ValueError):
        compare_variables(dataset, raw, expected_station="A201")


@pytest.mark.parametrize("mutation", ["unit", "duplicate", "width", "timezone"])
def test_invalid_metadata_and_time_series_fail_closed(mutation):
    dataset, raw = fixtures()
    observed = dataset["observed"]
    if mutation == "unit":
        observed["hourly_units"]["temperature_2m"] = "F"
    elif mutation == "duplicate":
        observed["hourly"]["time"][1] = observed["hourly"]["time"][0]
    elif mutation == "width":
        observed["hourly"]["wind_gusts_10m"].pop()
    else:
        observed["timezone"] = "UTC"
    with pytest.raises(ValueError):
        compare_variables(dataset, raw, expected_station="A201")


def test_sources_and_provenance_are_preserved():
    dataset, raw = fixtures()
    before = deepcopy(dataset)
    result = compare_variables(dataset, raw, expected_station="A201")
    assert dataset == before
    assert len(result["snapshot_dataset_sha256"]) == 64
    assert result["station_to_grid_distance_km"]["forecast"] > 0


@pytest.mark.parametrize("key,value", [("forecast_model", "ecmwf_ifs"),
                                       ("observed_model", "cerra"), ("lead_days", True)])
def test_unsupported_model_semantics_are_rejected(key, value):
    dataset, raw = fixtures()
    dataset["configuration"][key] = value
    with pytest.raises(ValueError):
        compare_variables(dataset, raw, expected_station="A201")


@pytest.mark.parametrize("when,start_hour,count", [("2025-03-09", 5, 23),
                                                  ("2025-11-02", 4, 25)])
def test_dst_days_require_actual_number_of_utc_samples(when, start_hour, count):
    dataset, raw = fixtures()
    dataset["configuration"].update(start=when, end=when, timezone="America/New_York")
    start = datetime.fromisoformat(when).replace(hour=start_hour, tzinfo=UTC)
    text = "\n".join(raw.decode().splitlines()[:6]) + "\n"
    for index in range(1, count + 1):
        stamp = start + timedelta(hours=index)
        text += f"{stamp:%Y/%m/%d};{stamp:%H%M} UTC;0;10;30;20;\n"
    for name in ("forecast", "observed"):
        payload = dataset[name]
        payload["timezone"] = "America/New_York"
        payload["hourly"]["time"] = [(start + timedelta(hours=index)).isoformat()
                                      for index in range(count + 1)]
        for key in payload["hourly"]:
            if key != "time":
                payload["hourly"][key] = [25.0] * (count + 1)
    result = compare_variables(dataset, text.encode(), expected_station="A201")
    for field in result["variables"].values():
        assert field["paired_days"] == 1
        assert field["cases"][0]["expected_hours"] == count


def test_cli_preserves_existing_output(tmp_path, monkeypatch):
    dataset, raw = fixtures()
    source, output = tmp_path / "station.csv", tmp_path / "report.json"
    source.write_bytes(raw)
    output.write_text("original", encoding="utf-8")
    monkeypatch.setattr("climaprev.tools.compare_station_variables.load_snapshot", lambda _: dataset)
    monkeypatch.setattr("sys.argv", ["compare", "--input", "unused", "--station-csv", str(source),
                                    "--station", "A201", "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert output.read_text(encoding="utf-8") == "original"
