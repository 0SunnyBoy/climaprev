"""Explicit, disabled-by-default campaign batches and a shared local call ledger."""

import argparse
import asyncio
import hashlib
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from dataclasses import asdict
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_baseline import collect_baseline
from climaprev.tools.experimental_collection import MODEL_ORIGINS, MODELS, collect_once
from climaprev.tools.experimental_protocol import (
    aware_timestamp,
    execute_authorized,
    validate_protocol,
)
from climaprev.tools.historical_experiment import canonical_json, digest, read_json

_ORIGINS = MODEL_ORIGINS


class CampaignLimitExceeded(RuntimeError):
    """No request may be sent after the shared provider/day budget is spent."""


def pipeline_versions() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    files = ("tools/experimental_archive.py", "tools/experimental_baseline.py",
             "tools/experimental_collection.py", "tools/experimental_normalization.py",
             "tools/experimental_campaign.py", "tools/experimental_pairing.py",
             "tools/inmet_observations.py", "infrastructure/providers/open_meteo.py",
             "domain/risk_policy.py", "domain/risk_evaluator.py", "domain/verification.py",
             "tools/experimental_comparison.py", "tools/experimental_equivalence.py",
             "tools/experimental_observations.py", "tools/experimental_multivariable.py",
             "tools/experimental_evaluation.py", "tools/experimental_uncertainty.py",
             "tools/experimental_criteria.py", "domain/bootstrap.py", "tools/experimental_protocol.py",
             "tools/experimental_preparation.py", "tools/inmet_tempo_csv.py",
             "tools/experimental_pilot_quota.py")
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}


class CampaignLedger:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS captures (job TEXT PRIMARY KEY, provider TEXT, "
                       "day TEXT, status TEXT, artifact TEXT, error TEXT)")

    def reserve(self, job: str, provider: str, when: datetime, limit: int) -> bool:
        if (when.utcoffset() is None or isinstance(limit, bool)
                or not isinstance(limit, int) or limit < 1):
            raise ValueError("aware clock and positive call limit required")
        day = when.astimezone(UTC).date().isoformat()
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM captures WHERE job=?", (job,)).fetchone():
                return False
            used = db.execute("SELECT count(*) FROM captures WHERE provider=? AND day=?",
                              (provider, day)).fetchone()[0]
            if used >= limit:
                raise CampaignLimitExceeded("shared provider/day call budget exhausted")
            db.execute("INSERT INTO captures VALUES (?,?,?,'reserved',NULL,NULL)",
                       (job, provider, day))
        return True

    def finish(self, job: str, artifact: str | None, error: str | None) -> None:
        with closing(sqlite3.connect(self.path)) as db, db:
            changed = db.execute(
                "UPDATE captures SET status=?,artifact=?,error=? WHERE job=? AND status='reserved'",
                ("failed" if error else "completed", artifact, error, job),
            ).rowcount
            if changed != 1:
                raise ValueError("job must have exactly one active reservation")


def build_manifest(
    campaign: str, locations: list[CanonicalLocation], models: list[str], slot: datetime,
    *, enabled: bool = False, collection_authorized: bool = False, call_limit: int = 30,
    run_at: datetime | None = None, window_minutes: int = 30,
) -> dict[str, Any]:
    if (not campaign.strip() or slot.utcoffset() is None or not locations or not models
            or isinstance(call_limit, bool) or not isinstance(call_limit, int) or call_limit < 1):
        raise ValueError("campaign, points, models, aware slot and positive budget required")
    if any(model not in {*MODELS, "operational-baseline"} for model in models):
        raise ValueError("unsupported campaign model")
    if isinstance(window_minutes, bool) or not isinstance(window_minutes, int) or window_minutes < 1:
        raise ValueError("positive slot window required")
    slot = slot.astimezone(UTC)
    if run_at is not None:
        if run_at.utcoffset() is None:
            raise ValueError("model run needs an offset")
        run_at = run_at.astimezone(UTC)
        if (run_at > slot or run_at.hour not in {0, 6, 12, 18}
                or run_at.minute or run_at.second or run_at.microsecond):
            raise ValueError("unsupported run or run after collection slot")
    jobs: dict[str, dict[str, Any]] = {}
    for location in locations:
        for model in models:
            identity = {"campaign": campaign, "slot": slot.isoformat(), "model": model,
                        "latitude": location.latitude, "longitude": location.longitude,
                        "timezone": location.timezone}
            if run_at is not None and model not in {"met-norway", "operational-baseline"}:
                identity["run_at"] = run_at.isoformat()
            key = digest(identity)
            jobs.setdefault(key, {"key": key, "identity": identity,
                                  "location": asdict(location), "origin_family": _ORIGINS[model]})
    plan = {"schema": "climaprev-campaign-manifest-v1", "jobs": list(jobs.values()),
            "slot": slot.isoformat(), "expires": (slot + timedelta(minutes=window_minutes)).isoformat(),
            "enabled": enabled, "collection_authorized": collection_authorized,
            "provider_daily_call_limit": call_limit, "scientific_approval": False,
            "pipeline_versions": pipeline_versions()}
    return {"plan": plan, "plan_sha256": digest(plan)}


async def run_manifest(
    manifest: dict[str, Any], ledger: CampaignLedger, client: httpx.AsyncClient,
    directory: Path, *, now: datetime,
) -> list[dict[str, Any]]:
    plan = manifest["plan"]
    if plan.get("schema") != "climaprev-campaign-manifest-v1":
        raise ValueError("unsupported campaign schema")
    if manifest["plan_sha256"] != digest(plan):
        raise ValueError("campaign manifest differs from frozen identity")
    if plan["pipeline_versions"] != pipeline_versions():
        raise ValueError("campaign pipeline differs from frozen versions")
    if plan["enabled"] is not True:
        return []
    if plan["collection_authorized"] is not True or now.utcoffset() is None:
        raise ValueError("explicit collection authorization and aware clock required")
    if not datetime.fromisoformat(plan["slot"]) <= now < datetime.fromisoformat(plan["expires"]):
        return []  # Never backfill a missed slot with newer data under its old identity.
    reports = []
    for job in plan["jobs"]:
        identity, key = job["identity"], job["key"]
        if key != digest(identity):
            raise ValueError("job identity differs")
        location = CanonicalLocation(**job["location"])
        if any(getattr(location, field) != identity[field]
               for field in ("latitude", "longitude", "timezone")):
            raise ValueError("job location differs from frozen identity")
        model = identity["model"]
        provider = "met-norway" if model == "met-norway" else "open-meteo"
        if not ledger.reserve(key, provider, now, plan["provider_daily_call_limit"]):
            reports.append({"job": key, "status": "already_reserved_no_retry"})
            continue
        try:
            if model == "operational-baseline":
                first = now.astimezone(UTC).date()
                result = await collect_baseline(client, location,
                                                DatePeriod(first, first + timedelta(days=6)), directory)
            else:
                run = datetime.fromisoformat(identity["run_at"]) if identity.get("run_at") else None
                result = await collect_once(client, location, model, directory, run_at=run)
        except (ValueError, TypeError, OverflowError, httpx.HTTPError, ProviderPermanentError,
                ProviderTransientError, WeatherDataInvalid) as error:
            ledger.finish(key, None, type(error).__name__)
            reports.append({"job": key, "status": "failed", "error": type(error).__name__})
        else:
            ledger.finish(key, result["archive"], None)
            reports.append({"job": key, "status": "completed", "result": result})
    return reports


def build_target_calendar(
    envelope: dict[str, Any], *, enabled: bool = False,
    approvals: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Expand the complete protocol universe without collecting data or reading outcomes."""
    protocol = validate_protocol(envelope)
    if not isinstance(enabled, bool):
        raise TypeError("calendar enabled must be boolean")
    if enabled:
        execute_authorized(envelope, "collection", lambda _: None, approvals=approvals)
    slots = [aware_timestamp(value) for value in protocol["slots"]]
    if len(set(slots)) != len(slots):
        raise ValueError("duplicate calendar slots")
    locations = [CanonicalLocation(station["name"], station["latitude"], station["longitude"],
                                   station["timezone"], "explicit-station-registry")
                 for station in protocol["stations"]]
    manifests, targets = [], []
    for slot in sorted(slots):
        manifest = build_manifest(
            protocol["id"], locations, protocol["models"], slot, enabled=enabled,
            collection_authorized=enabled, call_limit=protocol["provider_daily_call_limit"],
            window_minutes=protocol["slot_window_minutes"],
        )
        manifests.append(manifest)
        for station, location in zip(protocol["stations"], locations, strict=True):
            zone = ZoneInfo(location.timezone)
            for model in protocol["models"]:
                job = next(job for job in manifest["plan"]["jobs"]
                           if job["identity"]["model"] == model
                           and job["identity"]["latitude"] == location.latitude
                           and job["identity"]["longitude"] == location.longitude
                           and job["identity"]["timezone"] == location.timezone)
                for variable in protocol["variables"]:
                    for lead in protocol["horizons"]:
                        day = slot.astimezone(zone).date() + timedelta(days=lead)
                        start = datetime.combine(day, time.min, zone).astimezone(UTC)
                        end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
                        identity = {"protocol_sha256": envelope["sha256"], "job": job["key"],
                                    "station": station["code"], "variable": variable["name"],
                                    "unit": variable["unit"], "semantics": variable["semantics"],
                                    "aggregation": variable["aggregation"],
                                    "start_utc": start.isoformat(), "end_utc": end.isoformat()}
                        targets.append({"key": digest(identity), **identity, "model": model,
                                        "slot": slot.isoformat(), "date": day.isoformat(),
                                        "collection_lead_days": lead, "active": enabled})
    data = {"schema": "climaprev-target-calendar-v1", "protocol": envelope,
            "enabled": enabled, "approvals": list(approvals),
            "manifests": manifests, "targets": targets}
    return {"calendar": data, "sha256": digest(data)}


def validate_target_calendar(envelope: dict[str, Any]) -> dict[str, Any]:
    data = envelope.get("calendar")
    if (not isinstance(data, dict) or data.get("schema") != "climaprev-target-calendar-v1"
            or envelope.get("sha256") != digest(data)):
        raise ValueError("invalid calendar schema or hash")
    expected = build_target_calendar(data["protocol"], enabled=data["enabled"],
                                     approvals=data["approvals"])
    if expected != envelope:
        raise ValueError("calendar differs from the complete frozen targets or pipeline")
    return data


async def run_calendar(
    calendar: dict[str, Any], ledger: CampaignLedger, client: httpx.AsyncClient,
    directory: Path, *, now: datetime,
) -> list[dict[str, Any]]:
    """Run only authorized current slots; restart never retries an existing reservation."""
    data = validate_target_calendar(calendar)
    if not data["enabled"]:
        return []
    execute_authorized(data["protocol"], "collection", lambda _: None, approvals=data["approvals"])
    reports = []
    for manifest in data["manifests"]:
        reports.extend(await run_manifest(manifest, ledger, client, directory, now=now))
    return reports


async def _run_cli(args: argparse.Namespace) -> dict[str, Any]:
    calendar = read_json(args.calendar)
    data = validate_target_calendar(calendar)
    if not data["enabled"]:
        return {"calendar_sha256": calendar["sha256"], "enabled": False, "jobs": []}
    execute_authorized(data["protocol"], "collection", lambda _: None, approvals=data["approvals"])
    ledger = CampaignLedger(args.ledger)
    async with httpx.AsyncClient(trust_env=False, follow_redirects=False) as client:
        reports = await run_calendar(calendar, ledger, client, args.output, now=datetime.now(UTC))
    return {"calendar_sha256": calendar["sha256"], "enabled": True,
            "jobs": [{"job": report["job"], "status": report["status"],
                      "error": report.get("error"),
                      "archive": report.get("result", {}).get("archive")}
                     for report in reports], "scientific_approval": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(canonical_json(asyncio.run(_run_cli(args))))
    except (OSError, ValueError, TypeError, KeyError, OverflowError, CampaignLimitExceeded) as error:
        parser.exit(2, f"campaign execution failed: {error}\n")


if __name__ == "__main__":
    main()
