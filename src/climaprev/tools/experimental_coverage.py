"""Read-only operational coverage against an explicitly supplied slot calendar."""

import sqlite3
from collections import Counter
from collections.abc import Sequence
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any

from climaprev.tools.historical_experiment import digest


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
