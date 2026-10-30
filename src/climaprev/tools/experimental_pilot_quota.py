"""Prospective replacement planning for a technical pilot, never backdating captures."""

import sqlite3
from collections.abc import Mapping, Sequence
from contextlib import closing
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import load_forecast_capture
from climaprev.tools.experimental_campaign import build_manifest
from climaprev.tools.experimental_coverage import audit_calendar
from climaprev.tools.experimental_normalization import (
    _number,
    complete_rain_total,
    met_norway_measurements,
    open_meteo_measurements,
)
from climaprev.tools.experimental_protocol import execute_authorized, validate_protocol


def audit_quota_progress(
    envelope: dict[str, Any], manifests: Sequence[dict[str, Any]], ledger: Path, *, now: datetime,
) -> dict[str, Any]:
    """Count only archived, on-slot, D1-complete captures in the supplied audit trail.

    Missing manifests cannot be discovered here. Preserve the original calendar
    and every prospective extension, including failed and absent attempts.
    """
    protocol = validate_protocol(envelope)
    operational = audit_calendar(manifests, ledger, now=now)
    if operational["unplanned_ledger_jobs"]:
        raise ValueError("quota ledger contains jobs outside the supplied history")
    points = {(s["latitude"], s["longitude"], s["timezone"]): s["code"] for s in protocol["stations"]}
    if len(points) != len(protocol["stations"]):
        raise ValueError("ambiguous station points")
    completed: dict[str, dict[str, list[str]]] = {
        s["code"]: {model: [] for model in protocol["models"]} for s in protocol["stations"]
    }
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        paths = dict(db.execute("SELECT job,artifact FROM captures WHERE status='completed'"))
    rejected = []
    for row in operational["jobs"]:
        identity = row["identity"]
        point = tuple(identity[field] for field in ("latitude", "longitude", "timezone"))
        model = identity["model"]
        if (identity["campaign"] != protocol["id"] or point not in points
                or model not in protocol["models"]):
            raise ValueError("unexpected campaign, point or model in quota history")
        if row["status"] != "completed":
            continue
        try:
            location = CanonicalLocation("quota-audit", point[0], point[1], point[2], "quota-audit")
            capture = load_forecast_capture(Path(paths[row["job"]]), model=model, location=location)
            metadata, payload = capture["metadata"], capture["payload"]
            collected = datetime.fromisoformat(metadata["collected_at"])
            slot = datetime.fromisoformat(identity["slot"])
            if (slot.astimezone(UTC).time() != time(18)
                    or slot < min(datetime.fromisoformat(s) for s in protocol["slots"])):
                raise ValueError("capture does not belong to the pilot daily schedule")
            if not slot <= collected <= now or collected >= slot + timedelta(minutes=protocol["slot_window_minutes"]):
                raise ValueError("capture outside its original slot")
            zone = ZoneInfo(point[2])
            day = slot.astimezone(zone).date() + timedelta(days=1)
            start = datetime.combine(day, time.min, zone).astimezone(UTC)
            end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
            if model == "operational-baseline":
                forecast = payload["forecast"]
                if (forecast["location"] != metadata["location"]
                        or datetime.fromisoformat(forecast["fetched_at"]) != collected):
                    raise ValueError("baseline payload identity differs")
                value = next((d["precipitation_sum_mm"] for d in forecast["days"] if d["date"] == day.isoformat()), None)
                if value is None:
                    raise ValueError("D1 rain unavailable")
                _number(value, "precipitation_mm")
            else:
                if model != "met-norway" and payload["request_parameters"].get("models") != model:
                    raise ValueError("forecast payload model differs")
                samples = (met_norway_measurements(payload["response"]) if model == "met-norway"
                           else open_meteo_measurements(payload["response"]))
                if complete_rain_total(samples, start, end) is None:
                    raise ValueError("D1 rain incomplete")
            dates = completed[points[point]][model]
            stamp = slot.astimezone(UTC).date().isoformat()
            if stamp in dates:
                raise ValueError("duplicate station/model day")
            dates.append(stamp)
        except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
            rejected.append({"job": row["job"], "reason": str(error)})
    for models in completed.values():
        for dates in models.values():
            dates.sort()
    return {"completed_dates": completed, "rejected_completed_jobs": rejected,
            "operational_audit": operational, "scientific_approval": False}


def plan_quota_slot(
    envelope: dict[str, Any], completed_dates: Mapping[str, Mapping[str, Sequence[str]]],
    *, slot: datetime, now: datetime, enabled: bool = False,
    approvals: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Plan only station/model pairs still below fourteen distinct daily captures.

    Dates must come from audited completed archives with eligible D1 forecasts,
    not attempts, reservations or fabricated counters. This function checks date
    consistency but cannot authenticate caller-supplied receipt declarations.
    A replacement has its own new slot and target dates. Original failed slots
    must remain in the coverage denominator. This is not a confirmatory calendar.
    """
    protocol = validate_protocol(envelope)
    if (protocol["criteria"].get("adaptive_technical_pilot") is not True
            or protocol["criteria"].get("quota_per_station_model") != 14):
        raise ValueError("explicit adaptive technical-pilot protocol required")
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be boolean")
    if slot.utcoffset() is None or now.utcoffset() is None:
        raise ValueError("aware slot and planning clocks required")
    slot, now = slot.astimezone(UTC), now.astimezone(UTC)
    first = min(datetime.fromisoformat(s) for s in protocol["slots"])
    if (slot.time() != time(18) or slot < first
            or now >= slot + timedelta(minutes=protocol["slot_window_minutes"])):
        raise ValueError("future or still-open daily 18 UTC slot required; no backfill")
    if enabled:
        execute_authorized(envelope, "collection", lambda _: None, approvals=approvals)
    codes = {station["code"] for station in protocol["stations"]}
    if set(completed_dates) - codes:
        raise ValueError("unexpected station receipt")
    remaining: dict[str, dict[str, int]] = {}
    manifests = []
    quota_complete = True
    for station in protocol["stations"]:
        code = station["code"]
        receipts = completed_dates.get(code, {})
        if set(receipts) - set(protocol["models"]):
            raise ValueError("unexpected model receipt")
        needed = []
        remaining[code] = {}
        for model in protocol["models"]:
            dates = [date.fromisoformat(value) for value in receipts.get(model, ())]
            if (len(set(dates)) != len(dates) or len(dates) > 14
                    or any(day < first.date() or day > slot.date() for day in dates)):
                raise ValueError("duplicate, excess or out-of-pilot capture dates")
            remaining[code][model] = 14 - len(dates)
            quota_complete &= len(dates) == 14
            if len(dates) < 14 and slot.date() not in dates:
                needed.append(model)
        if needed:
            location = CanonicalLocation(station["name"], station["latitude"],
                                         station["longitude"], station["timezone"],
                                         "adaptive-technical-pilot-protocol")
            manifests.append(build_manifest(
                protocol["id"], [location], needed, slot, enabled=enabled,
                collection_authorized=enabled, call_limit=protocol["provider_daily_call_limit"],
                window_minutes=protocol["slot_window_minutes"],
            ))
    adjustment_end = date.fromisoformat(protocol["splits"]["adjustment"]["end"])
    return {
        "schema": "climaprev-adaptive-technical-pilot-slot-v1",
        "protocol_sha256": envelope["sha256"], "slot": slot.isoformat(),
        "manifests": manifests, "remaining": remaining,
        "quota_complete": quota_complete,
        "requested_jobs": sum(len(m["plan"]["jobs"]) for m in manifests),
        "requires_partition_replan": slot.date() + timedelta(days=max(protocol["horizons"])) > adjustment_end,
        "confirmation_enabled": False, "scientific_approval": False, "promotion_allowed": False,
    }
