"""Offline station reconciliation, disabled pilot calendars and temporal partitions."""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_campaign import build_manifest
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
