"""Prospective D7 adapter/policy control; never modifies the active pilot or its hashes."""

import argparse
import asyncio
import hashlib
from collections.abc import Callable, Sequence
from dataclasses import asdict, replace
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy, policy_fingerprint
from climaprev.infrastructure.providers.open_meteo import OpenMeteoForecastClient
from climaprev.tools.experimental_campaign import pipeline_versions
from climaprev.tools.experimental_d7_archive import ControlTransport, _aware, write_once
from climaprev.tools.experimental_d7_ledger import ControlLedger, pilot_budget
from climaprev.tools.experimental_normalization import complete_rain_total, open_meteo_measurements
from climaprev.tools.experimental_protocol import (
    execute_authorized,
    partition_for,
    validate_protocol,
)
from climaprev.tools.historical_experiment import canonical_json, digest, read_json

SCHEMA = "climaprev-d7-control-calendar-v1"
SCOPE = "adapter_policy_d7_epoch_two_day_transport_v1"


def _utc() -> datetime:
    return datetime.now(UTC)


def _versions() -> dict[str, str]:
    names = ("experimental_d7_control.py", "experimental_d7_archive.py", "experimental_d7_ledger.py")
    return {**pipeline_versions(), **{
        "tools/" + name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        for name in names
    }}


def _jobs(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    protocol = validate_protocol(envelope)
    if (protocol["criteria"].get("control_scope") != SCOPE
            or protocol["criteria"].get("execution_scope") != "secondary_exploratory_only"
            or protocol["models"] != ["operational-baseline"] or protocol["horizons"] != [7]
            or protocol["variables"] != [{"name": "precipitation_mm", "unit": "mm",
                                          "semantics": "previous_hour_sum", "aggregation": "sum"}]
            or protocol["slot_window_minutes"] != 30
            or protocol["provider_daily_call_limit"] != 30):
        raise ValueError("dedicated D7 exploratory protocol and bounded budget required")
    jobs = []
    if len(protocol["slots"]) > 366 or len(protocol["stations"]) > 20:
        raise ValueError("bounded calendar required")
    slots = [_aware(datetime.fromisoformat(stamp)) for stamp in protocol["slots"]]
    if len(set(slots)) != len(slots):
        raise ValueError("duplicate UTC slot instants")
    points = [(s["latitude"], s["longitude"], s["timezone"]) for s in protocol["stations"]]
    if len(set(points)) != len(points):
        raise ValueError("ambiguous station points")
    for slot in sorted(slots):
        if slot.time() != time(18):
            raise ValueError("D7 slots must be at 18 UTC")
        for station in protocol["stations"]:
            zone = ZoneInfo(station["timezone"])
            target = slot.astimezone(zone).date() + timedelta(days=7)
            if partition_for(envelope, target) != "adjustment":
                raise ValueError("this collector is restricted to development targets")
            identity = {"protocol_sha256": envelope["sha256"], "station": station,
                        "slot": slot.isoformat(), "target_date": target.isoformat(),
                        "start_utc": datetime.combine(target, time.min, zone).astimezone(UTC).isoformat(),
                        "end_utc": datetime.combine(target + timedelta(days=1), time.min, zone)
                        .astimezone(UTC).isoformat()}
            jobs.append({"key": digest(identity), **identity})
    return jobs


def build_control_calendar(
    envelope: dict[str, Any], *, now: datetime, enabled: bool = False,
    approvals: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Freeze the whole prospective universe; never authorizes the pilot's protocol."""
    now = _aware(now)
    if not isinstance(enabled, bool):
        raise TypeError("explicit boolean enabled required")
    jobs = _jobs(envelope)
    if any(datetime.fromisoformat(job["slot"]) <= now for job in jobs):
        raise ValueError("all slots must be strictly future when planning")
    if enabled:
        execute_authorized(envelope, "collection", lambda _: None, approvals=approvals)
    plan = {"schema": SCHEMA, "protocol": envelope, "planned_at": now.isoformat(),
            "enabled": enabled, "jobs": jobs, "versions": _versions(),
            "scientific_approval": False, "promotion_allowed": False}
    return {"plan": plan, "sha256": digest(plan)}


def _validate_calendar(envelope: dict[str, Any]) -> dict[str, Any]:
    plan = envelope["plan"]
    expected = build_control_calendar(plan["protocol"], now=datetime.fromisoformat(plan["planned_at"]),
                                      enabled=False)["plan"]
    expected["enabled"] = plan["enabled"]
    if (not isinstance(plan["enabled"], bool) or plan != expected
            or envelope["sha256"] != digest(plan)):
        raise ValueError("D7 calendar or implementation differs from frozen identity")
    return cast(dict[str, Any], plan)


async def _capture_job(
    job: dict[str, Any], versions: dict[str, str], control: ControlLedger,
    pilot_calls: int, client: httpx.AsyncClient, directory: Path, settings: Settings,
    clock: Callable[[], datetime],
) -> dict[str, Any]:
    slot = datetime.fromisoformat(job["slot"])
    expiry = slot + timedelta(minutes=30)
    target = date.fromisoformat(job["target_date"])
    def before_send(
        
    ) -> None:
        current = _aware(clock())
        if not slot <= current < expiry:
            raise ValueError("slot expired before HTTP")
        control.reserve_request(job["key"], current, pilot_calls)

    transport = ControlTransport(client, job, directory, before_send, clock)
    data: dict[str, Any] = {"schema": "climaprev-d7-control-capture-v1", "job": job,
                            "versions": versions, "control_scope": SCOPE,
                            "model_identity": "unknown_auto_selection", "run_at": None,
                            "scientific_approval": False, "promotion_allowed": False,
                            "forecast": None, "risk": None, "rain_eligible_exploratory": False}
    status = "failed"
    try:
        station = job["station"]
        location = CanonicalLocation(station["name"], station["latitude"], station["longitude"],
                                     station["timezone"], "frozen-D7-protocol")
        async with httpx.AsyncClient(transport=transport) as adapter_client:
            forecast = await OpenMeteoForecastClient(adapter_client, settings).forecast(
                location, DatePeriod(target, target))
        finished = _aware(clock())
        forecast = replace(forecast, fetched_at=finished)
        data.update({"forecast": asdict(forecast),
                     "risk": asdict(RiskEvaluator().evaluate(forecast, RiskPolicy())),
                     "policy_sha256": policy_fingerprint(RiskPolicy())})
        assert transport.payload is not None
        samples = open_meteo_measurements(transport.payload)
        total = complete_rain_total(samples, datetime.fromisoformat(job["start_utc"]),
                                    datetime.fromisoformat(job["end_utc"]))
        data.update({"rain_interval_total_mm": total,
                     "returned_grid": {k: transport.payload.get(k) for k in ("latitude", "longitude", "elevation")},
                     "requested_point": {k: station[k] for k in ("latitude", "longitude")},
                     "rain_eligible_exploratory": total is not None
                     and forecast.days[0].precipitation_sum_mm is not None
                     and slot <= finished < min(expiry, datetime.fromisoformat(job["start_utc"]))})
        status = "completed" if data["rain_eligible_exploratory"] else "ineligible"
    except (ValueError, TypeError, KeyError, OverflowError, OSError, httpx.HTTPError,
            ProviderPermanentError, ProviderTransientError, WeatherDataInvalid) as error:
        data["error_type"] = type(error).__name__
    finally:
        data.update({"status": status, "request": transport.record})
        archive_id = digest(data)
        envelope = {"capture": data, "sha256": archive_id}
        artifact = directory / (archive_id + ".json")
        try:
            write_once(artifact, canonical_json(envelope).encode())
            control.finish(job["key"], status, str(artifact.resolve()))
        except BaseException:
            control.finish(job["key"], "archive_failed", None)
            raise
    return {"job": job["key"], "status": status, "archive": str(artifact)}


async def run_control_calendar(
    calendar: dict[str, Any], *, pilot_protocol: dict[str, Any],
    pilot_manifests: Sequence[dict[str, Any]], pilot_ledger: Path, ledger: Path,
    directory: Path, client: httpx.AsyncClient, approvals: Sequence[dict[str, Any]] = (),
    clock: Callable[[], datetime] = _utc,
) -> list[dict[str, Any]]:
    plan = _validate_calendar(calendar)
    if not plan["enabled"]:
        return []
    execute_authorized(plan["protocol"], "collection", lambda _: None, approvals=approvals)
    pilot_workspace = pilot_ledger.resolve().parent
    if (ledger.resolve().is_relative_to(pilot_workspace)
            or directory.resolve().is_relative_to(pilot_workspace)
            or pilot_protocol["sha256"] == plan["protocol"]["sha256"]):
        raise ValueError("D7 workspace and protocol must be separate from pilot")
    settings = Settings(additional_retries=0)
    if settings.forecast_base_url.rstrip("/") != "https://api.open-meteo.com":
        raise ValueError("only the standard public provider is allowed")
    reports = []
    for job in plan["jobs"]:
        slot = datetime.fromisoformat(job["slot"])
        expiry = slot + timedelta(minutes=30)
        now = _aware(clock())
        if not slot <= now < expiry:
            continue  # No old slot is reinterpreted as a new forecast.
        pilot_calls = pilot_budget(pilot_protocol, pilot_manifests, pilot_ledger, now)
        target = date.fromisoformat(job["target_date"])
        if not now.date() <= target <= now.date() + timedelta(days=13):
            raise ValueError("D7 target outside public 14-date UTC window")
        control = ControlLedger(ledger)
        if not control.reserve_job(job["key"]):
            reports.append({"job": job["key"], "status": "already_reserved_no_retry"})
            continue

        reports.append(await _capture_job(
            job, plan["versions"], control, pilot_calls, client, directory, settings, clock))
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "run"))
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--approval", action="append", type=Path, default=[])
    parser.add_argument("--calendar", type=Path)
    parser.add_argument("--pilot-protocol", type=Path)
    parser.add_argument("--pilot-manifest", action="append", type=Path, default=[])
    parser.add_argument("--pilot-ledger", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--archives", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a new file")
    approvals = [read_json(p) for p in args.approval]
    if args.mode == "plan":
        result = build_control_calendar(read_json(args.protocol), now=_utc(), enabled=args.enable,
                                        approvals=approvals)
    else:
        if not all((args.calendar, args.pilot_protocol, args.pilot_manifest,
                    args.pilot_ledger, args.ledger, args.archives)):
            parser.error("run requires calendar, pilot protocol/history/ledger, own ledger and archives")
        calendar = read_json(args.calendar)
        if calendar["plan"]["protocol"] != read_json(args.protocol):
            parser.error("calendar and protocol differ")

        async def run() -> list[dict[str, Any]]:
            async with httpx.AsyncClient(timeout=15) as client:
                return await run_control_calendar(
                    calendar, pilot_protocol=read_json(args.pilot_protocol),
                    pilot_manifests=[read_json(p) for p in args.pilot_manifest],
                    pilot_ledger=args.pilot_ledger, ledger=args.ledger, directory=args.archives,
                    client=client, approvals=approvals)

        result = {"reports": asyncio.run(run()), "scientific_approval": False}
    write_once(args.output, canonical_json(result).encode())


if __name__ == "__main__":
    main()
