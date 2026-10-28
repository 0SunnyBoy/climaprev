import json
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pytest
from tests.support.station_csv import station_variables_csv

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast
from climaprev.tools.experimental_evaluation import evaluate_slot, load_capture

SLOT = datetime(2024, 1, 1, 18, tzinfo=UTC)
CHECKED = datetime(2024, 1, 4, tzinfo=UTC)
LOCATION = CanonicalLocation("Synthetic", 0, 0, "UTC", "test")


def archive(tmp_path, model):
    first = SLOT.replace(hour=0)
    if model == "operational-baseline":
        capture = ForecastCapture("open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast",
                                  LOCATION, SLOT, first, first + timedelta(days=3),
                                  selection_mode="automatic")
        payload = {"model_identity": "unknown_auto_selection", "forecast": {
            "location": asdict(LOCATION), "fetched_at": SLOT.isoformat(),
            "period": {"start": "2024-01-01", "end": "2024-01-03"}, "missing_fields": [],
            "days": [{"date": f"2024-01-0{i}", "precipitation_sum_mm": 24} for i in (1, 2, 3)]}}
    else:
        capture = ForecastCapture("open-meteo", model, "https://single-runs-api.open-meteo.com/v1/forecast",
                                  LOCATION, SLOT, first - timedelta(hours=1),
                                  first + timedelta(hours=71), run_at=first)
        payload = {"request_parameters": {"models": model, "run": "2024-01-01T00:00"},
                   "response": {"hourly_units": {
                       "time": "unixtime", "precipitation": "mm", "temperature_2m": "°C",
                       "relative_humidity_2m": "%", "wind_gusts_10m": "km/h"},
                       "hourly": {"time": [int((first + timedelta(hours=i)).timestamp()) for i in range(72)],
                                  "precipitation": [1] * 72, "temperature_2m": [21] * 72,
                                  "relative_humidity_2m": [50] * 72, "wind_gusts_10m": [8.2] * 72}}}
    return archive_forecast(tmp_path, capture, payload)


def setup_inputs(tmp_path):
    csv = tmp_path / "station.csv"
    csv.write_bytes(station_variables_csv())
    paths = {m: archive(tmp_path, m) for m in ("operational-baseline", "gfs_global", "ecmwf_ifs025")}
    return csv, paths


def test_integrates_rain_and_gust_without_fabricating_hourly_baseline(tmp_path):
    csv, paths = setup_inputs(tmp_path)
    result = evaluate_slot(paths, csv, "A201", timezone="UTC", slot=SLOT, checked_at=CHECKED,
                            horizons=(1,))
    day = result["horizons"][0]
    assert day["rain"]["common_cases"] == 1
    assert day["rain"]["models"]["gfs_global"]["numerical"]["mae"] == 0
    gust = day["variables"][0]
    assert gust["comparison"]["common_cases"] == 24
    assert gust["reference_kind"] == "experimental_model_not_public_v1"
    assert not gust["hourly_operational_baseline_available"]
    for variable in day["variables"][1:]:
        assert not variable["observation_semantics_compatible"]
        assert variable["comparison"]["common_cases"] == 0
    assert not result["pilot_activated"] and not result["promotion_allowed"]


def test_all_arm_omissions_keep_planned_horizons_and_hours(tmp_path):
    csv, _ = setup_inputs(tmp_path)
    result = evaluate_slot({}, csv, "A201", timezone="UTC", slot=SLOT, checked_at=CHECKED,
                            horizons=(1, 7))
    for day in result["horizons"]:
        assert day["planned_daily_rain_cases"] == 1
        assert len(day["missing_expected_arms"]) == 5
        assert day["rain"] is None
        assert all(v["planned_hourly_cases"] == 24 for v in day["variables"])


@pytest.mark.parametrize("problem", ["corrupt", "wrong_model", "wrong_slot", "future_observation"])
def test_incompatible_inputs_fail_closed(tmp_path, problem):
    csv, paths = setup_inputs(tmp_path)
    slot, checked = SLOT, CHECKED
    if problem == "corrupt":
        path = paths["gfs_global"]
        data = json.loads(path.read_text())
        data["payload"]["response"]["hourly"]["precipitation"][0] = 999
        path.write_text(json.dumps(data), encoding="utf-8")
    elif problem == "wrong_model":
        paths["icon_global"] = paths.pop("gfs_global")
    elif problem == "wrong_slot":
        slot = SLOT + timedelta(hours=1)
    else:
        checked = SLOT
    with pytest.raises(ValueError):
        evaluate_slot(paths, csv, "A201", timezone="UTC", slot=slot, checked_at=checked, horizons=(1,))


def test_load_capture_checks_content_address(tmp_path):
    path = archive(tmp_path, "gfs_global")
    wrong_name = tmp_path / "renamed.json"
    wrong_name.write_bytes(path.read_bytes())
    with pytest.raises(ValueError, match="integrity"):
        load_capture(wrong_name)


def test_cli_integrates_explicit_inputs_and_refuses_overwrite(tmp_path):
    csv, paths = setup_inputs(tmp_path)
    output = tmp_path / "evaluation.json"
    command = [sys.executable, "-m", "climaprev.tools.experimental_evaluation",
               "--station-csv", str(csv), "--station", "A201", "--timezone", "UTC",
               "--slot", SLOT.isoformat(), "--output", str(output)]
    for model, path in paths.items():
        command.extend(["--archive", f"{model}={path}"])
    subprocess.run(command, check=True, capture_output=True)
    previous = output.read_bytes()
    assert json.loads(previous)["horizons"][0]["rain"]["common_cases"] == 1
    assert subprocess.run(command, check=False, capture_output=True).returncode == 2
    assert output.read_bytes() == previous
