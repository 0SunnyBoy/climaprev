"""Diagnose existing high-relevant cases only, without opening reserved outcomes."""

import hashlib
import json
from datetime import date
from pathlib import Path

from climaprev.tools.compare_station_variables import _series
from climaprev.tools.historical_experiment import digest, load_snapshot
from climaprev.tools.inmet_observations import parse_station_csv
from climaprev.tools.temporal_diagnostic import daily_profile, nearest_peak_lag


def main():
    evidence = Path("docs/planejamento/reference-candidate-1/evidence")
    parent = evidence / "catalogo-erros-espaciais-2024-2026-10-19.json"
    output = evidence / "diagnostico-horario-2024-2026-10-19-v2.json"
    if output.exists():
        raise ValueError("temporal diagnosis already exists")
    catalog = json.loads(parent.read_text(encoding="utf-8"))
    stations, snapshots, records = {}, {}, []
    fields = {"daily_rain": ("rain_mm", "precipitation", "mm"),
              "hourly_rain": ("rain_mm", "precipitation", "mm"),
              "gust": ("gust_kmh", "wind_gusts_10m", "km/h"),
              "heat": ("temperature_max_c", "temperature_2m", "°C"),
              "cold": ("temperature_min_c", "temperature_2m", "°C")}
    for row in catalog["high_relevant_cases"]:
        day = date.fromisoformat(row["date"])
        if day.year != 2024:
            raise ValueError("diagnosis is restricted to 2024")
        code = row["station"]
        if code not in stations:
            raw = Path(f".historical-reports/inmet/{code}-2024.csv").read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["station_csv_sha256"]:
                raise ValueError("CSV changed")
            stations[code] = parse_station_csv(raw, expected_station=code)[1]
        station_field, model_field, unit = fields[row["event"]]
        station_series = {hour.endpoint: getattr(hour, station_field) for hour in stations[code]}
        profiles = {}
        observation = None
        for arm, expected in row["parent_snapshots"].items():
            name = f"{row['location']}-2024-{day.month:02d}-d{row['lead_days']}-{arm}"
            if name not in snapshots:
                snapshots[name] = load_snapshot(Path(
                    f".historical-reports/spatial-2024-2026-10-19/{name}.inputs.json"))
            data = snapshots[name]
            if digest(data) != expected:
                raise ValueError("snapshot changed")
            zone = data["configuration"]["timezone"]
            if observation is None:
                observation = daily_profile(station_series, day, zone, preceding=True,
                                            minimum=row["event"] == "cold")
                aggregate = observation["sum"] if row["event"] == "daily_rain" else observation["peak"]
                if aggregate is None or abs(aggregate - row["station_value"]) > 0.00001:
                    raise ValueError("station temporal aggregate differs from catalog")
            profiles[arm] = {}
            for source in ("forecast", "observed"):
                suffix = f"_previous_day{row['lead_days']}" if source == "forecast" else ""
                series = _series(data[source], model_field, unit, suffix)
                preceding = row["event"] in ("daily_rain", "hourly_rain") or (
                    row["event"] == "gust" and source == "forecast")
                profile = daily_profile(series, day, zone, preceding=preceding,
                                        minimum=row["event"] == "cold")
                aggregate = profile["sum"] if row["event"] == "daily_rain" else profile["peak"]
                if aggregate is None or abs(aggregate - row["arms"][arm][source]["value"]) > 0.00001:
                    raise ValueError("model temporal aggregate differs from catalog")
                profiles[arm][source] = {
                    "profile": profile, "preceding_hour_interval": preceding,
                    "nearest_tied_peak_endpoint_lag_hours": nearest_peak_lag(observation, profile)}
        records.append({"location": row["location"], "date": row["date"], "event": row["event"],
                        "lead_days": row["lead_days"], "station": code,
                        "parent_snapshots": row["parent_snapshots"],
                        "observation": observation, "models": profiles})
    result = {
        "schema": "climaprev-temporal-diagnostic-v1", "records": records,
        "catalog_file_sha256": hashlib.sha256(parent.read_bytes()).hexdigest(),
        "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (
            Path(__file__), Path("src/climaprev/tools/temporal_diagnostic.py"))},
        "candidate_fitting_executed": False, "calibration_fitting_executed": False,
        "stop_before_stage": 6, "scientific_approval": False,
        "limitations": ["Nearest tied-peak lag is descriptive and can be zero for flat series.",
                        "Rain daily peak time describes the maximum hourly contribution, not daily-sum timing.",
                        "Endpoint timestamps do not locate the true sub-hour extreme.",
                        "Different sampling semantics remain; no dates shifted or thresholds fitted.",
                        "Timing mismatch does not establish the cause of a missed high event."]}
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Diagnosed {len(records)} high-relevant case records")


if __name__ == "__main__":
    main()
