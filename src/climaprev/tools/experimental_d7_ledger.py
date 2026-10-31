"""D7 reservations and conservative read-only coordination with the frozen pilot."""

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from climaprev.tools.experimental_d7_archive import _aware
from climaprev.tools.experimental_pilot_quota import audit_quota_progress
from climaprev.tools.experimental_protocol import (
    validate_protocol,
)


class ControlLedger:
    """Separate job and HTTP reservations. Failed/cancelled reservations are never retried."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS jobs (job TEXT PRIMARY KEY, status TEXT, artifact TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS requests (job TEXT PRIMARY KEY, day TEXT)")

    def reserve_job(self, job: str) -> bool:
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            return db.execute("INSERT OR IGNORE INTO jobs VALUES (?,'reserved',NULL)", (job,)).rowcount == 1

    def reserve_request(self, job: str, now: datetime, pilot_calls: int) -> None:
        if isinstance(pilot_calls, bool) or not isinstance(pilot_calls, int) or not 0 <= pilot_calls <= 30:
            raise ValueError("verified non-negative bounded pilot call count required")
        day = _aware(now).date().isoformat()
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT status FROM jobs WHERE job=?", (job,)).fetchone() != ("reserved",):
                raise ValueError("HTTP requires an active job reservation")
            used = db.execute("SELECT count(*) FROM requests WHERE day=?", (day,)).fetchone()[0]
            if used + pilot_calls >= 30:
                raise ValueError("combined provider/day budget exhausted")
            db.execute("INSERT INTO requests VALUES (?,?)", (job, day))

    def finish(self, job: str, status: str, artifact: str | None) -> None:
        with closing(sqlite3.connect(self.path)) as db, db:
            changed = db.execute("UPDATE jobs SET status=?,artifact=? WHERE job=? AND status='reserved'",
                                 (status, artifact, job)).rowcount
            if changed != 1:
                raise ValueError("job must have one active reservation")


def pilot_budget(
    protocol: dict[str, Any], manifests: Sequence[dict[str, Any]], ledger: Path, now: datetime,
) -> int:
    """Read only; no concurrent pilot calls permitted, even if its seed ends before its quota."""
    value = validate_protocol(protocol)
    if (value["criteria"].get("adaptive_technical_pilot") is not True
            or value["criteria"].get("quota_per_station_model") != 14):
        raise ValueError("adaptive pilot with fourteen-capture quota required")
    supplied_slots = {datetime.fromisoformat(m["plan"]["slot"]) for m in manifests}
    if not {datetime.fromisoformat(s) for s in value["slots"]} <= supplied_slots:
        raise ValueError("complete pilot seed history required")
    expected_pairs = {(s["latitude"], s["longitude"], s["timezone"], model)
                      for s in value["stations"] for model in value["models"]}
    for slot in value["slots"]:
        supplied_pairs = {
            tuple(job["identity"][field] for field in ("latitude", "longitude", "timezone", "model"))
            for manifest in manifests if datetime.fromisoformat(manifest["plan"]["slot"]) == datetime.fromisoformat(slot)
            for job in manifest["plan"]["jobs"]
        }
        if not expected_pairs <= supplied_pairs:
            raise ValueError("complete station/model seed universe required")
    progress = audit_quota_progress(protocol, manifests, ledger, now=now)
    if any(len(dates) != 14 for models in progress["completed_dates"].values() for dates in models.values()):
        raise ValueError("D7 waits until the active pilot forecast quota is complete")
    day = now.astimezone(UTC).date()
    if any(datetime.fromisoformat(m["plan"]["slot"]).date() >= day for m in manifests):
        raise ValueError("D7 waits until after all pilot manifest dates")
    with closing(sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("SELECT count(*) FROM captures WHERE status='reserved'").fetchone()[0]:
            raise ValueError("unresolved pilot reservation blocks D7")
        return int(db.execute("SELECT count(*) FROM captures WHERE provider='open-meteo' AND day=?",
                              (day.isoformat(),)).fetchone()[0])
