"""Read-only pilot closure report: quota, missing attempts and observation tail."""

import argparse
import hashlib
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.tools.experimental_campaign import validate_target_calendar
from climaprev.tools.experimental_pilot_quota import audit_quota_progress
from climaprev.tools.experimental_protocol import validate_protocol
from climaprev.tools.historical_experiment import canonical_json, digest, read_json
from climaprev.tools.inmet_observations import parse_station_csv


def build_pilot_report(
    envelope: dict[str, Any], manifests: Sequence[dict[str, Any]], ledger: Path, *,
    now: datetime, observations: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Read declared history and explicit CSVs; never fit, collect, approve or schedule.

    Completion of the technical quota and truth tail is separate from scientific
    success. The caller must supply all seed and extension manifests.
    """
    protocol = validate_protocol(envelope)
    if (protocol["criteria"].get("adaptive_technical_pilot") is not True
            or protocol["criteria"].get("quota_per_station_model") != 14):
        raise ValueError("adaptive fourteen-capture pilot required")
    progress = audit_quota_progress(envelope, manifests, ledger, now=now)
    codes = {s["code"] for s in protocol["stations"]}
    sources = observations or {}
    if set(sources) - codes:
        raise ValueError("unexpected observational station")
    seed_dates = {datetime.fromisoformat(s).astimezone(UTC).date() for s in protocol["slots"]}
    quota_rows = []
    observation_rows = []
    tail_ends = []
    total = replacements = 0
    for station in protocol["stations"]:
        code = station["code"]
        accepted_days = set()
        for model in protocol["models"]:
            days = [date.fromisoformat(d) for d in progress["completed_dates"][code][model]]
            if len(days) > 14:
                raise ValueError("quota exceeded; reconcile history before closure")
            total += len(days)
            replacements += sum(day not in seed_dates for day in days)
            accepted_days.update(days)
            quota_rows.append({"station": code, "model": model, "accepted": len(days),
                               "remaining": 14-len(days), "capture_dates": [d.isoformat() for d in days]})
        targets = {day+timedelta(days=h) for day in accepted_days for h in protocol["horizons"]}
        zone = ZoneInfo(station["timezone"])
        hours = {}
        source_hash = None
        if code in sources:
            raw = sources[code].read_bytes()
            metadata, values = parse_station_csv(raw, expected_station=code)
            if any(abs(metadata[field]-station[field]) > .0001 for field in ("latitude", "longitude")):
                raise ValueError("observation point differs from pilot station")
            hours = {hour.endpoint: hour for hour in values}
            source_hash = hashlib.sha256(raw).hexdigest()
        due = pending = complete = expected_hours = valid_hours = 0
        missing_days = []
        for day in sorted(targets):
            start = datetime.combine(day, time.min, zone).astimezone(UTC)
            end = datetime.combine(day+timedelta(days=1), time.min, zone).astimezone(UTC)
            if end > now:
                pending += 1
                continue
            due += 1
            endpoints = []
            cursor = start+timedelta(hours=1)
            while cursor <= end:
                endpoints.append(cursor)
                cursor += timedelta(hours=1)
            valid = sum(stamp in hours and hours[stamp].rain_mm is not None for stamp in endpoints)
            expected_hours += len(endpoints)
            valid_hours += valid
            if valid == len(endpoints):
                complete += 1
            else:
                missing_days.append(day.isoformat())
        if targets:
            tail_ends.append(datetime.combine(max(targets)+timedelta(days=1), time.min, zone).astimezone(UTC))
        observation_rows.append({"station": code, "source_sha256": source_hash,
                                 "target_days": len(targets), "due_days": due,
                                 "pending_days": pending, "complete_due_days": complete,
                                 "incomplete_due_dates": missing_days,
                                 "expected_due_hours": expected_hours, "valid_due_hours": valid_hours,
                                 "due_hour_coverage": valid_hours/expected_hours if expected_hours else None})
    target = 14*len(quota_rows)
    quota_complete = total == target
    tail_end = max(tail_ends) if tail_ends else None
    tail_complete = bool(tail_end and now >= tail_end and all(
        row["source_sha256"] and row["pending_days"] == 0 and row["complete_due_days"] == row["due_days"]
        for row in observation_rows
    ))
    tail_elapsed = bool(tail_end and now >= tail_end)
    closure_status = ("collecting_forecasts" if not quota_complete else
                      "complete" if tail_complete else
                      "observation_gaps_after_tail" if tail_elapsed else "waiting_for_observation_tail")
    result = {
        "schema": "climaprev-technical-pilot-closure-v1", "checked_at": now.isoformat(),
        "protocol_sha256": envelope["sha256"], "manifest_sha256": [digest(m) for m in manifests],
        "analysis_module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "accepted_captures": total, "capture_target": target, "accepted_replacement_captures": replacements,
        "quota_complete": quota_complete, "quota_by_station_model": quota_rows,
        "operational_audit": progress["operational_audit"],
        "rejected_completed_jobs": progress["rejected_completed_jobs"],
        "observations": observation_rows, "actual_observation_tail_end": tail_end.isoformat() if tail_end else None,
        "observation_tail_complete": tail_complete,
        "observation_tail_elapsed": tail_elapsed, "closure_status": closure_status,
        "technical_pilot_complete": quota_complete and tail_complete,
        "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Missing supplied manifests cannot be discovered by this report.",
                        "Quota does not guarantee fourteen common dates across models.",
                        "Observation provenance/instruments and independent-event support are not certified.",
                        "Technical completion is not evidence of improved forecast accuracy."],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, help="seed target calendar")
    parser.add_argument("--manifest", type=Path, action="append", default=[])
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--observations", action="append", default=[], help="station=CSV")
    parser.add_argument("--now", type=datetime.fromisoformat)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        envelope = read_json(args.protocol)
        manifests = [read_json(p) for p in args.manifest]
        if args.calendar:
            seed = validate_target_calendar(read_json(args.calendar))
            if seed["protocol"] != envelope:
                raise ValueError("seed calendar and report protocol differ")
            manifests = seed["manifests"] + manifests
        if not manifests:
            raise ValueError("seed calendar or explicit manifests required")
        sources = {}
        for entry in args.observations:
            code, path = entry.split("=", 1)
            if code in sources:
                raise ValueError("duplicate observation station")
            sources[code] = Path(path)
        report = build_pilot_report(envelope, manifests,
                                    args.ledger, now=args.now or datetime.now(UTC), observations=sources)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(canonical_json(report)+"\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"pilot report failed: {error}\n")


if __name__ == "__main__":
    main()
