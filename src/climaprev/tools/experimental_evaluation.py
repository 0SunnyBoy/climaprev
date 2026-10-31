"""Offline integration of explicit archives, station CSV and per-horizon reports."""

import argparse
import hashlib
from dataclasses import asdict
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_archive import ForecastCapture
from climaprev.tools.experimental_campaign import pipeline_versions
from climaprev.tools.experimental_comparison import compare_rain_models
from climaprev.tools.experimental_multivariable import (
    compare_variable_reports,
    pair_station_variable,
)
from climaprev.tools.experimental_normalization import (
    met_norway_measurements,
    open_meteo_measurements,
)
from climaprev.tools.experimental_observations import (
    qualify_observation_window,
    station_variable_measurements,
)
from climaprev.tools.experimental_pairing import pair_baseline_rain, pair_station_rain
from climaprev.tools.historical_experiment import canonical_json, digest, read_json
from climaprev.tools.inmet_observations import MAX_BYTES

MODELS = ("operational-baseline", "gfs_global", "ecmwf_ifs025", "icon_global", "met-norway")


def load_capture(path: Path) -> tuple[ForecastCapture, dict[str, Any]]:
    """Verify content-addressed integrity, not authenticity of provider declarations."""
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("archive exceeds 4 MiB")
    data = read_json(path)
    if (data.get("schema") != "climaprev-experimental-archive-v1"
            or path.stem != digest(data) or data["payload_sha256"] != digest(data["payload"])):
        raise ValueError("archive integrity mismatch")
    meta = data["metadata"]
    capture = ForecastCapture(
        meta["provider"], meta["model"], meta["endpoint"], CanonicalLocation(**meta["location"]),
        datetime.fromisoformat(meta["collected_at"]), datetime.fromisoformat(meta["valid_start"]),
        datetime.fromisoformat(meta["valid_end"]),
        datetime.fromisoformat(meta["run_at"]) if meta["run_at"] else None,
        selection_mode=meta["selection_mode"],
    )
    return capture, data["payload"]


def evaluate_slot(
    archives: dict[str, Path], station_csv: Path, station: str, *, timezone: str,
    slot: datetime, checked_at: datetime, horizons: tuple[int, ...] = (1, 3, 7),
) -> dict[str, Any]:
    """Read explicit inputs only, never collect, fit, fill missing arms or promote."""
    if (slot.utcoffset() is None or checked_at.utcoffset() is None or checked_at < slot
            or not horizons or len(set(horizons)) != len(horizons)
            or any(isinstance(h, bool) or not isinstance(h, int) or h not in {1, 3, 7}
                   for h in horizons) or set(archives) - set(MODELS)):
        raise ValueError("aware clocks, known arms and unique D1/D3/D7 horizons required")
    if station_csv.stat().st_size > MAX_BYTES:
        raise ValueError("station CSV exceeds size limit")
    raw = station_csv.read_bytes()
    metadata, observations = station_variable_measurements(raw, station=station)
    zone = ZoneInfo(timezone)
    location = CanonicalLocation(metadata["name"], metadata["latitude"], metadata["longitude"],
                                 timezone, "INMET-source-version")
    if max(m.end or m.start for m in observations) > checked_at:
        raise ValueError("observational source contains future timestamps")
    loaded = {}
    inputs = {}
    for model, path in archives.items():
        capture, payload = load_capture(path)
        if (any(abs(getattr(capture.location, f) - getattr(location, f)) > 0.0001
                for f in ("latitude", "longitude")) or capture.location.timezone != timezone):
            raise ValueError("capture and station source-version point differ")
        if not slot <= capture.collected_at < slot + timedelta(minutes=30):
            raise ValueError("capture outside declared decision slot")
        if capture.collected_at > checked_at:
            raise ValueError("capture follows evaluation clock")
        if model == "operational-baseline":
            if capture.selection_mode != "automatic" or payload.get("model_identity") != "unknown_auto_selection":
                raise ValueError("operational baseline identity differs")
            forecast = payload["forecast"]
            if (datetime.fromisoformat(forecast["fetched_at"]) != capture.collected_at
                    or forecast["location"] != asdict(capture.location)):
                raise ValueError("baseline payload and capture metadata differ")
            samples = None
        else:
            if capture.selection_mode != "explicit":
                raise ValueError("explicit model capture required")
            request = payload["request_parameters"]
            if model == "met-norway":
                if capture.provider != "met-norway" or capture.model != "ecmwf-ifs-global-unspecified":
                    raise ValueError("MET model identity differs")
                samples = met_norway_measurements(payload["response"])
            else:
                if capture.provider != "open-meteo" or capture.model != model or request.get("models") != model:
                    raise ValueError("requested model and archived identity differ")
                requested_run = request.get("run")
                expected_run = (capture.run_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M")
                                if capture.run_at else None)
                if requested_run != expected_run:
                    raise ValueError("requested run and archived identity differ")
                samples = open_meteo_measurements(payload["response"])
        loaded[model] = (capture, payload, samples)
        inputs[model] = {"archive_identity": path.stem, "payload_sha256": digest(payload),
                         "collected_at": capture.collected_at.isoformat(),
                         "run_at": capture.run_at.isoformat() if capture.run_at else None}
    source_end = datetime.combine(slot.astimezone(zone).date(), time.min, zone).astimezone(UTC)
    readiness = qualify_observation_window(
        metadata, observations, location, start=source_end - timedelta(days=7), end=source_end,
        checked_at=checked_at, min_coverage=0.9,
    )
    sections = []
    for lead in horizons:
        target_day = slot.astimezone(zone).date() + timedelta(days=lead)
        period = DatePeriod(target_day, target_day)
        rain = []
        variables = []
        for model, (capture, payload, samples) in loaded.items():
            if model == "operational-baseline":
                report = pair_baseline_rain(payload, raw, station)
                report["rows"] = [r for r in report["rows"] if r["date"] == target_day.isoformat()]
            else:
                assert samples is not None
                report = pair_station_rain(samples, location, raw, station, period,
                                           collected_at=capture.collected_at, model=model, run_at=capture.run_at)
            rain.append(report)
        rain_comparison = (compare_rain_models(rain, "operational-baseline", require_run=False)
                           if "operational-baseline" in loaded and len(rain) >= 2 else None)
        for target in ("gust_previous_hour_max", "temperature_instant", "humidity_instant"):
            capable = ["gfs_global", "ecmwf_ifs025", "icon_global"]
            if target != "gust_previous_hour_max":
                capable.append("met-norway")
            candidates = [m for m in capable if m in loaded]
            reports = []
            for model in candidates:
                capture, _, samples = loaded[model]
                assert samples is not None
                reports.append(pair_station_variable(samples, location, raw, station, period,
                                                       target=target, model=model,
                                                       collected_at=capture.collected_at,
                                                       run_at=capture.run_at))
            comparison = (compare_variable_reports(reports, "gfs_global")
                          if "gfs_global" in candidates and len(reports) >= 2 else None)
            variables.append({"target": target, "reference_kind": "experimental_model_not_public_v1",
                              "hourly_operational_baseline_available": False,
                              "planned_hourly_cases": int((
                                  datetime.combine(target_day + timedelta(days=1), time.min, zone).astimezone(UTC)
                                  - datetime.combine(target_day, time.min, zone).astimezone(UTC)
                              ).total_seconds() // 3600),
                              "participating_models": candidates,
                              "missing_supported_models": [m for m in capable if m not in loaded],
                              "observation_semantics_compatible": target == "gust_previous_hour_max",
                              "comparison": comparison})
        sections.append({"collection_lead_days": lead, "target_date": target_day.isoformat(),
                         "planned_daily_rain_cases": 1,
                         "forecast_rain_available": {r["model"]: any(
                             row["forecast_mm"] is not None and not any(
                                 reason in {"incomplete_forecast_interval", "incompatible_measurement_contract",
                                            "baseline_hourly_rain_coverage"} for reason in row["exclusions"]
                             ) for row in r["rows"]) for r in rain},
                         "missing_expected_arms": [m for m in MODELS if m not in loaded],
                         "rain": rain_comparison, "variables": variables})
    return {
        "schema": "climaprev-integrated-slot-evaluation-v1", "station": station,
        "station_point": asdict(location),
        "source_csv_sha256": hashlib.sha256(raw).hexdigest(), "slot_utc": slot.astimezone(UTC).isoformat(),
        "checked_at": checked_at.astimezone(UTC).isoformat(), "inputs": inputs,
        "evaluation_pipeline_sha256": pipeline_versions(),
        "observation_readiness": readiness, "horizons": sections,
        "pilot_activated": False, "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Point estimates on declared evidence, not independent confirmation.",
                        "Missing hourly baseline is not reconstructed from daily summaries.",
                        "Temperature hourly mean and unresolved humidity are not instantaneous observations.",
                        "No instrument calibration, uncertainty calculation, fitting or scheduling."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="append", default=[], help="model=explicit archive path")
    parser.add_argument("--station-csv", type=Path, required=True)
    parser.add_argument("--station", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--slot", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        archives = {}
        for item in args.archive:
            model, path = item.split("=", 1)
            if model in archives:
                raise ValueError("duplicate model argument")
            archives[model] = Path(path)
        result = evaluate_slot(archives, args.station_csv, args.station, timezone=args.timezone,
                               slot=datetime.fromisoformat(args.slot), checked_at=datetime.now(UTC))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(canonical_json(result) + "\n")
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as exc:
        parser.exit(2, f"integrated evaluation failed: {exc}\n")


if __name__ == "__main__":
    main()
