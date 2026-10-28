"""Read-only operational coverage against an explicitly supplied slot calendar."""

import sqlite3
from collections import Counter
from collections.abc import Mapping, Sequence
from contextlib import closing
from datetime import datetime, timedelta
from math import isfinite
from pathlib import Path
from typing import Any

from climaprev.tools.experimental_archive import _file_sha256
from climaprev.tools.experimental_campaign import validate_target_calendar
from climaprev.tools.experimental_protocol import aware_timestamp
from climaprev.tools.historical_experiment import digest, read_json


def audit_calendar(
    manifests: Sequence[dict[str, Any]], ledger: Path, *, now: datetime,
) -> dict[str, Any]:
    """Count absent slots too; completion does not assert meteorological quality.

    The supplied manifests define the denominator. This cannot detect calendar
    entries omitted by the caller and never creates a ledger or retries jobs.
    """
    if now.utcoffset() is None:
        raise ValueError("aware audit clock required")
    planned: dict[str, tuple[dict[str, Any], str]] = {}
    identities = []
    for manifest in manifests:
        plan = manifest["plan"]
        if (plan.get("schema") != "climaprev-campaign-manifest-v1"
                or manifest["plan_sha256"] != digest(plan)):
            raise ValueError("invalid frozen campaign manifest")
        slot, expires = datetime.fromisoformat(plan["slot"]), datetime.fromisoformat(plan["expires"])
        if slot.utcoffset() is None or expires.utcoffset() is None or slot >= expires:
            raise ValueError("invalid slot interval")
        phase = "future" if now < slot else "open" if now < expires else "missed"
        if plan["enabled"] is not True or plan["collection_authorized"] is not True:
            phase = "inactive"
        identities.append(manifest["plan_sha256"])
        for job in plan["jobs"]:
            key, identity = job["key"], job["identity"]
            if key != digest(identity) or datetime.fromisoformat(identity["slot"]) != slot:
                raise ValueError("invalid planned job identity")
            if key in planned:
                raise ValueError("duplicate planned job")
            planned[key] = (identity, phase)
    # mode=ro fails if the operator supplied a missing database: never invent an
    # empty ledger that could disguise a path/configuration error as no captures.
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        captures = {row[0]: row[1:] for row in db.execute(
            "SELECT job,status,artifact,error FROM captures"
        )}
    rows = []
    for key, (identity, phase) in sorted(planned.items()):
        capture = captures.get(key)
        if capture is None:
            status = phase
        else:
            status, artifact, error = capture
            if (status not in {"reserved", "completed", "failed"}
                    or (status == "completed" and (not artifact or error))
                    or (status == "failed" and not error)):
                raise ValueError("invalid ledger outcome")
            if phase in {"future", "inactive"}:
                raise ValueError("ledger outcome precedes slot or belongs to an inactive plan")
            if status == "reserved" and phase == "missed":
                status = "unresolved_reservation"
        rows.append({"job": key, "identity": identity, "status": status})
    counts = dict(Counter(row["status"] for row in rows))
    due = sum(phase in {"open", "missed"} for _, phase in planned.values())
    return {
        "schema": "climaprev-operational-calendar-coverage-v1",
        "manifest_sha256": identities, "audited_at": now.isoformat(),
        "planned_jobs": len(planned), "due_jobs": due, "status_counts": counts,
        "completion_fraction_due": counts.get("completed", 0) / due if due else None,
        "unplanned_ledger_jobs": len(set(captures) - set(planned)), "jobs": rows,
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": [
            "Denominator is the supplied calendar; omitted manifests cannot be detected.",
            "Completed means ledger completion, not archive integrity or eligible forecast days.",
            "No observation coverage, skill estimate, retry or scheduling is performed.",
            "Reservations have no completion timestamp; delivery timeliness is not certified.",
        ],
    }


def _capture_identity(path: Path, identity: dict[str, Any]) -> dict[str, Any]:
    capture = read_json(path)
    if (capture.get("schema") != "climaprev-experimental-archive-v1"
            or capture.get("payload_sha256") != digest(capture["payload"])
            or path.stem != digest(capture)):
        raise ValueError("capture identity differs")
    metadata = capture["metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("capture metadata must be an object")
    expected_model = {"met-norway": "ecmwf-ifs-global-unspecified",
                      "operational-baseline": "unknown"}.get(identity["model"], identity["model"])
    if metadata["model"] != expected_model:
        raise ValueError("capture model differs from job")
    for field in ("latitude", "longitude", "timezone"):
        if metadata["location"][field] != identity[field]:
            raise ValueError("capture location differs from job")
    aware_timestamp(metadata["collected_at"])
    return metadata


def _pair_quality(row: dict[str, Any], variable: str) -> bool:
    if row.get("eligible_exploratory") is not True or row.get("exclusions") != []:
        return False
    for field in ("forecast", "observed"):
        value = row.get(field)
        if (isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
                or not variable.startswith("temperature") and value < 0
                or variable == "humidity_pct" and value > 100):
            return False
    return True


def audit_target_coverage(
    calendar: dict[str, Any], ledger: Path, reports: Sequence[dict[str, Any]], *,
    now: datetime, observation_files: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Link immutable captures and observation hashes to versioned pair-quality reports.

    This does not re-run meteorological aggregation or certify source authenticity.
    Confirmatory readiness is not scientific approval; E2 still gates evaluation.
    """
    data = validate_target_calendar(calendar)
    operational = audit_calendar(data["manifests"], ledger, now=now)
    states = {row["job"]: row for row in operational["jobs"]}
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        captures = {row[0]: row[1] for row in db.execute("SELECT job,artifact FROM captures")}
    pairs: dict[tuple[str, str, str, str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for report in reports:
        if report.get("schema") != "climaprev-variable-pairs-v1":
            raise ValueError("target coverage requires versioned variable pairs")
        for row in report["rows"]:
            key = (report["model"], report["station"]["code"], report["variable"],
                   aware_timestamp(row["start_utc"]).isoformat(),
                   aware_timestamp(row["end_utc"]).isoformat())
            pairs.setdefault(key, []).append((report, row))
    sources = observation_files or {}
    rows = []
    due = eligible = confirmatory = 0
    for target in data["targets"]:
        reasons = []
        is_due = target["active"] and aware_timestamp(target["end_utc"]) <= now
        due += int(is_due)
        state = states[target["job"]]
        capture_path = Path(captures[target["job"]]) if captures.get(target["job"]) else None
        metadata = None
        if not target["active"]:
            reasons.append("inactive")
        elif not is_due:
            reasons.append("target_not_due")
        if state["status"] != "completed":
            reasons.append("capture_not_completed")
        elif capture_path is not None:
            try:
                metadata = _capture_identity(capture_path, state["identity"])
            except (OSError, ValueError, TypeError, KeyError):
                reasons.append("capture_missing_or_invalid")
        else:
            reasons.append("capture_missing_or_invalid")
        key = (target["model"], target["station"], target["variable"],
               target["start_utc"], target["end_utc"])
        slot = aware_timestamp(target["slot"])
        expiry = slot + timedelta(
            minutes=data["protocol"]["protocol"]["slot_window_minutes"])
        candidates = [(report, row) for report, row in pairs.get(key, [])
                      if slot <= aware_timestamp(report["collected_at"]) < expiry]
        if len(candidates) > 1:
            raise ValueError("duplicate pair reports for a planned target")
        comparable = False
        if not candidates:
            reasons.append("paired_report_missing")
        else:
            report, row = candidates[0]
            if not _pair_quality(row, target["variable"]):
                reasons.append("pair_quality_exclusion")
            if report["unit"] != target["unit"] or report["aggregation"] != target["aggregation"]:
                reasons.append("pair_contract_mismatch")
            station_plan = next(station for station in data["protocol"]["protocol"]["stations"]
                                if station["code"] == target["station"])
            location_matches = report.get("location", {}).get("timezone") == station_plan["timezone"]
            for point in (report.get("location", {}), report.get("station", {})):
                for field in ("latitude", "longitude"):
                    value = point.get(field)
                    if (isinstance(value, bool) or not isinstance(value, (int, float))
                            or not isfinite(value) or abs(value - station_plan[field]) > 0.0001):
                        location_matches = False
            if not location_matches:
                reasons.append("pair_location_mismatch")
            if capture_path is None or report.get("capture_sha256") != capture_path.stem:
                reasons.append("pair_capture_mismatch")
            if metadata is not None and (aware_timestamp(report["collected_at"])
                                         != aware_timestamp(metadata["collected_at"])):
                reasons.append("pair_capture_time_mismatch")
            source = sources.get(target["station"])
            try:
                if source is None or _file_sha256(source) != report["source_sha256"]:
                    reasons.append("observation_source_mismatch")
            except OSError:
                reasons.append("observation_source_mismatch")
            comparable = (report["forecast_semantics"].removeprefix("observed_")
                          == report["observed_semantics"].removeprefix("observed_")
                          or bool(report.get("equivalence_reference")))
            comparable = comparable and row.get("eligible_confirmatory") is True
        ok = is_due and not reasons
        eligible += int(ok)
        confirmatory += int(ok and comparable)
        rows.append({"key": target["key"], "target": target, "operational_status": state["status"],
                     "eligible_exploratory": ok, "eligible_confirmatory": ok and comparable,
                     "reasons": reasons})
    return {"schema": "climaprev-target-coverage-v1", "calendar_sha256": calendar["sha256"],
            "protocol_sha256": data["protocol"]["sha256"], "planned_targets": len(rows),
            "due_targets": due, "eligible_exploratory_targets": eligible,
            "eligible_confirmatory_targets": confirmatory,
            "exploratory_coverage_fraction": eligible / due if due else None,
            "rows": rows, "operational": operational,
            "input_reports_sha256": [digest(report) for report in reports],
            "scientific_approval": False}
