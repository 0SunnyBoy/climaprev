"""Offline station reconciliation, disabled pilot calendars and temporal partitions."""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_campaign import build_manifest, pipeline_versions
from climaprev.tools.historical_experiment import digest


def reconcile_station(
    current: dict[str, Any], historical: dict[str, Any], *, timezone: str,
) -> dict[str, Any]:
    """Expose differences rather than relabel a historical station snapshot."""
    code = current["CD_ESTACAO"]
    if code != historical["code"]:
        raise ValueError("different station identities")
    location = CanonicalLocation(current["DC_NOME"], float(current["VL_LATITUDE"]),
                                 float(current["VL_LONGITUDE"]), timezone, "INMET-current-catalogue")
    differences = {}
    for field in ("latitude", "longitude"):
        old = historical[field]
        if isinstance(old, bool) or not isinstance(old, (int, float)) or not isfinite(old):
            raise ValueError("invalid historical coordinate")
        delta = getattr(location, field) - old
        if delta:
            differences[field] = delta
    needs_reconciliation = any(abs(value) > 0.0001 for value in differences.values())
    operational = current.get("CD_SITUACAO") == "Operante" and not current.get("DT_FIM_OPERACAO")
    return {
        "station": code, "location": asdict(location), "catalogue_operational": operational,
        "coordinate_deltas_degrees": differences,
        "historical_pairing_requires_reconciliation": needs_reconciliation,
        "historical_metadata_sha256": digest(historical),
        "current_metadata_sha256": digest(current),
        "current_observation_quality_verified": False,
        "activation_ready": False,
    }


def prepare_pilot(
    locations: Sequence[CanonicalLocation], *, first_slot: datetime, days: int,
    models: list[str], campaign: str, now: datetime,
) -> dict[str, Any]:
    """Prepare future 18 UTC slots with explicit 00 UTC runs where supported."""
    if now.utcoffset() is None or first_slot.utcoffset() is None:
        raise ValueError("aware clocks required")
    first_slot = first_slot.astimezone(UTC)
    if (isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 31
            or first_slot <= now or first_slot.time() != time(18)):
        raise ValueError("future 18 UTC pilot with one to 31 days required")
    if len(set(locations)) != len(locations):
        raise ValueError("duplicate locations")
    manifests = []
    for offset in range(days):
        slot = first_slot + timedelta(days=offset)
        manifests.append(build_manifest(campaign, list(locations), models, slot,
                                         run_at=slot.replace(hour=0)))
    return {
        "schema": "climaprev-disabled-pilot-calendar-v1", "manifests": manifests,
        "days": days, "planned_jobs": sum(len(m["plan"]["jobs"]) for m in manifests),
        "calendar_sha256": digest(manifests), "collection_enabled": False,
        "notes": ["00 UTC is requested only for models supporting explicit runs.",
                  "Baseline automatic and MET Norway retain unknown run identity.",
                  "A preflight does not guarantee future provider availability.",
                  "Expired slots cannot be backfilled; schedule changes need a new calendar."],
    }


@dataclass(frozen=True, slots=True)
class TemporalPartition:
    name: str
    start: date
    end: date


def validate_partitions(
    partitions: Sequence[TemporalPartition], *, embargo_days: int, max_horizon_days: int,
    candidate_frozen_at: datetime,
) -> dict[str, Any]:
    """Check target-date separation and freeze before the earliest test run.

    Arithmetic separation is not proof of meteorological independence. Never
    inspect outcomes or classify an existing unknown dataset as independent.
    """
    if (isinstance(embargo_days, bool) or not isinstance(embargo_days, int) or embargo_days < 0
            or isinstance(max_horizon_days, bool) or not isinstance(max_horizon_days, int)
            or max_horizon_days < 1 or candidate_frozen_at.utcoffset() is None):
        raise ValueError("valid embargo, horizon and aware freeze required")
    if [part.name for part in partitions] != ["development", "selection", "confirmation"]:
        raise ValueError("three ordered partitions required")
    for index, part in enumerate(partitions):
        if part.start > part.end:
            raise ValueError("inverted partition")
        if index and (part.start - partitions[index - 1].end).days <= embargo_days:
            raise ValueError("overlap or insufficient embargo")
        if index and ((part.start - timedelta(days=max_horizon_days))
                      - partitions[index - 1].end).days <= embargo_days:
            raise ValueError("forecast issuance overlaps the previous partition embargo")
    earliest_run = datetime.combine(partitions[-1].start - timedelta(days=max_horizon_days),
                                    time.min, UTC)
    if candidate_frozen_at.astimezone(UTC).date() <= partitions[-2].end:
        raise ValueError("final freeze cannot precede completion of selection targets")
    if candidate_frozen_at.astimezone(UTC) >= earliest_run:
        raise ValueError("freeze must precede earliest confirmatory model run")
    return {
        "schema": "climaprev-temporal-partitions-check-v1",
        "partitions": [asdict(part) for part in partitions],
        "embargo_days": embargo_days, "max_horizon_days": max_horizon_days,
        "candidate_freeze_deadline": candidate_frozen_at.astimezone(UTC).isoformat(),
        "earliest_confirmatory_run": earliest_run.isoformat(),
        "prospective_independence_verified": False, "confirmation_enabled": False,
        "limitation": "Schedule validity does not establish data provenance or actual freezing.",
    }


def qualify_primary_pilot(
    calendar: dict[str, Any], reports: Sequence[dict[str, Any]], *,
    operational_stations: set[str], now: datetime, min_coverage: float,
) -> dict[str, Any]:
    """Readiness gate for primary rain, without changing or running a calendar.

    Secondary-variable incompatibility remains explicit but does not invent a
    requirement that forecast observations from tomorrow already be available.
    Recent completed observation windows and D1 forecast availability are used.
    """
    if (now.utcoffset() is None or isinstance(min_coverage, bool) or not 0 < min_coverage <= 1
            or calendar.get("schema") != "climaprev-disabled-pilot-calendar-v1"
            or calendar["calendar_sha256"] != digest(calendar["manifests"])):
        raise ValueError("valid calendar, aware clock and coverage required")
    reasons = []
    expected_points = set()
    required_models = {"operational-baseline", "gfs_global", "ecmwf_ifs025", "icon_global", "met-norway"}
    for manifest in calendar["manifests"]:
        plan = manifest["plan"]
        if manifest["plan_sha256"] != digest(plan):
            raise ValueError("invalid manifest integrity")
        if plan["pipeline_versions"] != pipeline_versions():
            reasons.append("calendar_pipeline_outdated")
        if datetime.fromisoformat(plan["slot"]) <= now:
            reasons.append("calendar_contains_elapsed_slots")
        models_by_point: dict[tuple[Any, ...], set[str]] = {}
        for job in plan["jobs"]:
            if job["key"] != digest(job["identity"]):
                raise ValueError("invalid job identity")
            point = (job["identity"]["latitude"], job["identity"]["longitude"],
                     job["identity"]["timezone"])
            expected_points.add(point)
            models_by_point.setdefault(point, set()).add(job["identity"]["model"])
        if any(models != required_models for models in models_by_point.values()):
            reasons.append("calendar_forecast_arms_incomplete")
    seen = set()
    for report in reports:
        if report.get("schema") != "climaprev-integrated-slot-evaluation-v1":
            raise ValueError("integrated evaluation reports required")
        station = report["station"]
        if station in seen:
            raise ValueError("duplicate station evaluation")
        seen.add(station)
        if report.get("evaluation_pipeline_sha256") != pipeline_versions():
            reasons.append(f"{station}:evaluation_pipeline_outdated")
        readiness = report["observation_readiness"]
        point = tuple(report["station_point"][field] for field in ("latitude", "longitude", "timezone"))
        if point not in expected_points:
            raise ValueError("station evaluation does not belong to the calendar")
        expected_points.remove(point)
        if station not in operational_stations or not readiness["station_version_matches"]:
            reasons.append(f"{station}:station_metadata_not_ready")
        if readiness["variables"]["precipitation_mm"]["coverage"] < min_coverage:
            reasons.append(f"{station}:recent_rain_observations_incomplete")
        expected_end = datetime.combine(now.astimezone(ZoneInfo(point[2])).date(), time.min,
                                        ZoneInfo(point[2])).astimezone(UTC)
        if datetime.fromisoformat(readiness["end_utc"]) != expected_end:
            reasons.append(f"{station}:observation_window_outdated")
        day1 = next((row for row in report["horizons"] if row["collection_lead_days"] == 1), None)
        if (day1 is None or day1["missing_expected_arms"]
                or set(day1["forecast_rain_available"]) != required_models
                or not all(day1["forecast_rain_available"].values())):
            reasons.append(f"{station}:primary_forecast_arms_not_ready")
    if expected_points or not reports:
        reasons.append("station_evaluations_missing")
    return {"schema": "climaprev-primary-pilot-readiness-v1", "ready": not reasons,
            "blockers": sorted(set(reasons)), "pilot_activated": False,
            "scientific_approval": False, "promotion_allowed": False,
            "scope": "primary_rain_technical_pilot_not_secondary_variable_certification"}
