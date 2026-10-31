from datetime import UTC, date, datetime, timedelta

import pytest

from climaprev.domain.models import DatePeriod
from climaprev.tools.inmet_observations import import_station, parse_station_csv


def station_csv(*, missing=False, boundary=True, encoding="utf-8", day=date(2025, 1, 1),
                first_hour=4, count=24):
    # Synthetic format fixture; not a real station observation.
    text = ("REGIAO:;N\nUF:;PA\nESTACAO:;BELÉM\nCODIGO (WMO):;A201\n"
            "LATITUDE:;-1,4\nLONGITUDE:;-48,4\nALTITUDE:;10\nDATA DE FUNDACAO:;2003-01-01\n"
            "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
            "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
            "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C);\n")
    start = datetime(day.year, day.month, day.day, first_hour, tzinfo=UTC)
    for index in range(count if boundary else count - 1):
        stamp = start + timedelta(hours=index)
        rain = "-9999" if missing and index == 5 else "1,5"
        text += f"{stamp:%Y/%m/%d};{stamp:%H%M} UTC;{rain};10;30;20;\n"
    return text.encode(encoding)


def report(raw):
    return import_station(raw, expected_station="A201", period=DatePeriod(
        date(2025, 1, 1), date(2025, 1, 1)), timezone="America/Belem")


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_csv_decimals_units_and_civil_boundary(encoding):
    result = report(station_csv(encoding=encoding))
    fields = result["days"][0]["fields"]
    assert fields["rain_mm"]["value"] == 36
    assert fields["gust_kmh"]["value"] == 36
    assert fields["temperature_min_c"]["value"] == 20
    assert fields["temperature_max_c"]["value"] == 30
    assert result["days"][0]["expected_hours"] == 24
    assert result["station"]["name"] == "BELÉM"


def test_sentinel_excludes_only_affected_variable():
    fields = report(station_csv(missing=True))["days"][0]["fields"]
    assert fields["rain_mm"]["value"] is None
    assert fields["rain_mm"]["max_hourly_mm"] is None
    assert fields["rain_mm"]["valid_hours"] == 23
    assert fields["gust_kmh"]["eligible"]


def test_missing_next_day_boundary_is_reported():
    rain = report(station_csv(boundary=False))["days"][0]["fields"]["rain_mm"]
    assert rain["value"] is None
    assert rain["missing_endpoints_utc"] == ["2025-01-02T03:00:00+00:00"]


@pytest.mark.parametrize("old,new", [
    ("A201", "A202"),
    ("(m/s)", "(km/h)"),
    ("Hora UTC", "Hora local"),
    (";1,5;10;30;20;", ";-2;10;30;20;"),
    (";1,5;10;30;20;", ";NaN;10;30;20;"),
    (";1,5;10;30;20;", ";1,5;10;10;20;"),
])
def test_invalid_identity_units_and_values_fail_closed(old, new):
    raw = station_csv().decode().replace(old, new).encode()
    with pytest.raises(ValueError):
        report(raw)


def test_duplicate_endpoints_are_rejected():
    raw = station_csv()
    raw += raw.splitlines()[-1] + b"\n"
    with pytest.raises(ValueError, match="duplicate INMET UTC"):
        report(raw)


@pytest.mark.parametrize("day,first,count", [(date(2025, 3, 9), 6, 23),
                                            (date(2025, 11, 2), 5, 25)])
def test_dst_coverage_uses_utc_endpoints(day, first, count):
    result = import_station(station_csv(day=day, first_hour=first, count=count),
                            expected_station="A201", period=DatePeriod(day, day),
                            timezone="America/New_York")
    assert result["days"][0]["expected_hours"] == count
    assert result["days"][0]["fields"]["rain_mm"]["value"] == 1.5 * count


def test_raw_hash_tracks_source_changes():
    first = report(station_csv())
    second = report(station_csv().replace(b";10;30;20;", b";11;30;20;"))
    assert first["source_sha256"] != second["source_sha256"]
    assert first["importer_sha256"] == second["importer_sha256"]


def test_hourly_temperature_is_not_substituted_for_interval_extrema():
    raw = station_csv().decode().replace("TEMPERATURA MÁXIMA NA HORA ANT. (AUT)",
                                       "TEMPERATURA DO AR - BULBO SECO, HORARIA").encode()
    with pytest.raises(ValueError, match="temperature_max_c"):
        parse_station_csv(raw, expected_station="A201")


def test_cli_refuses_to_overwrite_existing_evidence(tmp_path, monkeypatch):
    from climaprev.tools.inmet_observations import main

    source = tmp_path / "station.csv"
    source.write_bytes(station_csv())
    output = tmp_path / "observed.json"
    output.write_text("existing evidence", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["inmet_observations", "--input", str(source),
                                    "--station", "A201", "--timezone", "America/Belem",
                                    "--start", "2025-01-01", "--end", "2025-01-01",
                                    "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert output.read_text(encoding="utf-8") == "existing evidence"


def model_dataset(*, boundary=True):
    from copy import deepcopy

    count = 25 if boundary else 24
    hourly = {
        "time": [(datetime(2025, 1, 1) + timedelta(hours=index)).isoformat()
                 for index in range(count)],
        "precipitation": [2.0] * count, "temperature_2m": [25.0] * count,
        "wind_gusts_10m": [10.0] * count,
    }
    observed = {"latitude": -1.5, "longitude": -48.5, "timezone": "America/Belem",
                "utc_offset_seconds": -10800, "hourly": hourly,
                "hourly_units": {"precipitation": "mm", "temperature_2m": "°C",
                                 "wind_gusts_10m": "km/h"}}
    forecast = deepcopy(observed)
    forecast["hourly"] = {key + "_previous_day1" if key != "time" else key: value
                          for key, value in forecast["hourly"].items()}
    forecast["hourly_units"] = {key + "_previous_day1": value
                                for key, value in forecast["hourly_units"].items()}
    return {"configuration": {"start": "2025-01-01", "end": "2025-01-01",
                              "timezone": "America/Belem", "lead_days": 1},
            "observed": observed, "forecast": forecast}


def test_station_comparison_uses_same_complete_cases_and_error_direction():
    from climaprev.tools.compare_station import compare_station

    result = compare_station(model_dataset(), station_csv(), expected_station="A201")
    assert result["paired_days"] == 1
    assert result["cases"][0]["station"] == 36
    assert result["metrics"]["forecast"]["bias"] == 12
    assert result["metrics"]["observed"]["mae"] == 12
    assert result["station_to_grid_distance_km"]["forecast"] > 0


@pytest.mark.parametrize("missing_source", ["station", "model"])
def test_station_comparison_never_scores_unpaired_or_missing_boundary(missing_source):
    from climaprev.tools.compare_station import compare_station

    result = compare_station(model_dataset(boundary=missing_source != "model"),
                             station_csv(missing=missing_source == "station"),
                             expected_station="A201")
    assert result["paired_days"] == 0
    assert result["metrics"]["forecast"]["mae"] is None
    assert result["metrics"]["observed"]["cases"] == 0
    assert len(result["excluded_days"]) == 1


def next_day_dataset():
    from copy import deepcopy

    boundary = deepcopy(model_dataset(boundary=False))
    boundary["configuration"].update(start="2025-01-02", end="2025-01-02")
    for name in ("forecast", "observed"):
        boundary[name]["hourly"]["time"] = [
            stamp.replace("2025-01-01", "2025-01-02")
            for stamp in boundary[name]["hourly"]["time"]]
    return boundary


def test_boundary_merge_restores_final_day_without_mutating_parents():
    from copy import deepcopy

    from climaprev.tools.compare_station import append_boundary, compare_station

    original, boundary = model_dataset(boundary=False), next_day_dataset()
    before = deepcopy(original), deepcopy(boundary)
    merged = append_boundary(original, boundary)
    result = compare_station(merged, station_csv(), expected_station="A201")
    assert result["paired_days"] == 1
    assert (original, boundary) == before
    assert set(merged["boundary_parent_sha256"]) == {"original", "boundary"}


@pytest.mark.parametrize("key,value", [("lead_days", 7), ("timezone", "UTC"),
                                       ("end", "2025-01-03")])
def test_incompatible_boundary_is_rejected(key, value):
    from climaprev.tools.compare_station import append_boundary

    boundary = next_day_dataset()
    boundary["configuration"][key] = value
    with pytest.raises(ValueError, match="boundary"):
        append_boundary(model_dataset(boundary=False), boundary)


def horizon_dataset(lead):
    data = model_dataset()
    data["configuration"]["lead_days"] = lead
    for name in ("hourly", "hourly_units"):
        data["forecast"][name] = {key.replace("_previous_day1", f"_previous_day{lead}"): value
                                   for key, value in data["forecast"][name].items()}
    return data


def test_horizons_share_dates_and_detect_conflicting_reference():
    from climaprev.tools.compare_rain_horizons import compare_horizons

    one, three = horizon_dataset(1), horizon_dataset(3)
    result = compare_horizons([three, one])
    assert result["unique_paired_dates"] == 1
    assert result["lead_days"] == [1, 3]
    assert result["metrics"]["1"]["bias"] == 0
    three["observed"]["hourly"]["precipitation"][5] = 3
    with pytest.raises(ValueError, match="conflicting observed target"):
        compare_horizons([one, three])


def test_horizons_exclude_date_from_all_metrics_if_one_forecast_is_incomplete():
    from climaprev.tools.compare_rain_horizons import compare_horizons

    one, three = horizon_dataset(1), horizon_dataset(3)
    three["forecast"]["hourly"]["precipitation_previous_day3"][5] = None
    result = compare_horizons([one, three])
    assert result["unique_paired_dates"] == 0
    assert result["metrics"]["1"]["mae"] is None
    assert result["metrics"]["3"]["cases"] == 0


def test_duplicate_horizons_fail_closed():
    from climaprev.tools.compare_rain_horizons import compare_horizons

    with pytest.raises(ValueError, match="duplicate horizon"):
        compare_horizons([horizon_dataset(1), horizon_dataset(1)])
