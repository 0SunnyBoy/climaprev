import json
import multiprocessing
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from tests.support.experiment import approval_fixture, protocol_fixture

from climaprev.tools.experimental_campaign import (
    CampaignLedger,
    CampaignLimitExceeded,
    build_target_calendar,
)
from climaprev.tools.experimental_coverage import audit_calendar
from climaprev.tools.historical_experiment import canonical_json, digest

SLOT = datetime(2030, 1, 1, tzinfo=UTC)


def active_calendar(*, enabled=True, limit=30):
    envelope = protocol_fixture()
    envelope["protocol"]["models"] = ["gfs_global"]
    envelope["protocol"]["horizons"] = [1]
    envelope["protocol"]["provider_daily_call_limit"] = limit
    envelope["sha256"] = digest(envelope["protocol"])
    return build_target_calendar(envelope, enabled=enabled, approvals=[approval_fixture(envelope)])


def reserve_process(path, capture, queue):
    ledger = CampaignLedger(Path(path))
    reserved = ledger.reserve("shared-job", "open-meteo", SLOT, 1)
    if reserved:
        Path(capture).write_text("synthetic-capture")
        ledger.finish("shared-job", str(capture), None)
    queue.put(reserved)


def test_two_processes_produce_exactly_one_persisted_capture(tmp_path):
    ledger, capture = tmp_path / "ledger.sqlite", tmp_path / "capture.json"
    CampaignLedger(ledger)
    ctx = multiprocessing.get_context("fork")
    queue = ctx.Queue()
    workers = [ctx.Process(target=reserve_process, args=(str(ledger), str(capture), queue))
               for _ in range(2)]
    try:
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(10)
            assert worker.exitcode == 0
        assert sorted([queue.get(timeout=2), queue.get(timeout=2)]) == [False, True]
        assert capture.read_text() == "synthetic-capture"
        with sqlite3.connect(ledger) as db:
            assert db.execute("SELECT status,artifact FROM captures").fetchall() == [
                ("completed", str(capture)),
            ]
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join()
        queue.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["disabled", "expired"])
async def test_disabled_or_expired_calendar_never_calls_provider(tmp_path, mode):
    from climaprev.tools.experimental_campaign import run_calendar

    calendar = active_calendar(enabled=mode != "disabled")
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    now = SLOT + timedelta(hours=1) if mode == "expired" else SLOT
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: pytest.fail("no HTTP"))) as c:
        assert await run_calendar(calendar, ledger, c, tmp_path, now=now) == []
    with sqlite3.connect(ledger.path) as db:
        assert db.execute("SELECT count(*) FROM captures").fetchone()[0] == 0


@pytest.mark.asyncio
async def test_failed_job_is_not_retried_on_restart_or_backfilled_after_expiry(tmp_path):
    from climaprev.tools.experimental_campaign import run_calendar

    calendar = active_calendar()
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    calls = []

    def fail(request):
        calls.append(request)
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(fail)) as c:
        first = await run_calendar(calendar, ledger, c, tmp_path / "archive", now=SLOT)
        second = await run_calendar(calendar, ledger, c, tmp_path / "archive", now=SLOT)
        expired = await run_calendar(calendar, ledger, c, tmp_path / "archive", now=SLOT + timedelta(hours=1))
    assert first[0]["status"] == "failed"
    assert second[0]["status"] == "already_reserved_no_retry"
    assert expired == []
    assert len(calls) == 1
    assert not (tmp_path / "archive").exists()


@pytest.mark.asyncio
async def test_calendar_budget_uses_the_controlled_utc_clock(tmp_path):
    from climaprev.tools.experimental_campaign import run_calendar

    calendar = active_calendar(limit=1)
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    assert ledger.reserve("already-spent", "open-meteo", SLOT, 1)
    ledger.finish("already-spent", None, "synthetic-failure")
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: pytest.fail("no HTTP"))) as c:
        with pytest.raises(CampaignLimitExceeded):
            await run_calendar(calendar, ledger, c, tmp_path, now=SLOT)


class SyntheticInterruption(BaseException):
    pass


@pytest.mark.asyncio
async def test_interruption_preserves_visible_reservation_and_does_not_repeat_http(tmp_path):
    from climaprev.tools.experimental_campaign import run_calendar

    calendar = active_calendar()
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    calls = []

    def interrupted(request):
        calls.append(request)
        raise SyntheticInterruption

    async with httpx.AsyncClient(transport=httpx.MockTransport(interrupted)) as c:
        with pytest.raises(SyntheticInterruption):
            await run_calendar(calendar, ledger, c, tmp_path, now=SLOT)
        second = await run_calendar(calendar, ledger, c, tmp_path, now=SLOT)
    result = audit_calendar(calendar["calendar"]["manifests"], ledger.path,
                            now=SLOT + timedelta(hours=1))
    assert second[0]["status"] == "already_reserved_no_retry"
    assert len(calls) == 1
    assert result["status_counts"] == {"unresolved_reservation": 1}


def test_disabled_cli_does_not_create_ledger_or_capture_directory(tmp_path):
    path = tmp_path / "calendar.json"
    path.write_text(canonical_json(active_calendar(enabled=False)))
    ledger, output = tmp_path / "absent.sqlite", tmp_path / "absent-archive"
    result = subprocess.run([sys.executable, "-m", "climaprev.tools.experimental_campaign",
                             "--calendar", str(path), "--ledger", str(ledger),
                             "--output", str(output)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["enabled"] is False
    assert not ledger.exists()
    assert not output.exists()
