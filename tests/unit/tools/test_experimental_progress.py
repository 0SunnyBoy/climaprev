import asyncio
import json
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest

from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.tools.experimental_archive import ForecastCapture
from climaprev.tools.experimental_baseline import collect_baseline
from climaprev.tools.experimental_campaign import (
    CampaignLedger,
    CampaignLimitExceeded,
    build_manifest,
    run_manifest,
)
from climaprev.tools.experimental_collection import collect_once
from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.experimental_pairing import pair_baseline_rain, pair_station_rain

LOCATION = CanonicalLocation("Belém", -1.4, -48.4, "America/Belem", "synthetic-station")


def forecast_payload(request):
    day = date.fromisoformat(request.url.params["start_date"])
    return {"timezone": "America/Belem",
            "daily": {"time": [day.isoformat()], "precipitation_sum": [24]},
            "hourly": {"time": [f"{day.isoformat()}T{i:02}:00" for i in range(24)],
                       "precipitation": [1] * 24}}


@pytest.mark.asyncio
async def test_baseline_uses_actual_production_request_and_preserves_unknown_selection(tmp_path):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=forecast_payload(request))

    day = datetime.now(UTC).date()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        report = await collect_baseline(client, LOCATION, DatePeriod(day, day), tmp_path)
    assert len(requests) == 1
    assert "models" not in requests[0].url.params
    assert requests[0].url.params["timezone"] == "auto"
    assert requests[0].url.params["temperature_unit"] == "celsius"
    assert "precipitation_probability_max" in requests[0].url.params["daily"]
    archive = json.loads(next(tmp_path.iterdir()).read_text())
    assert archive["metadata"]["selection_mode"] == "automatic"
    assert archive["metadata"]["model"] == "unknown"
    assert archive["metadata"]["run_at"] is None
    assert report["forecast"]["days"][0]["precipitation_sum_mm"] == 24
    assert report["risk"]["policy_version"] == "reference-v1"


@pytest.mark.asyncio
async def test_baseline_does_not_expand_public_window_to_d7(tmp_path):
    day = datetime.now(UTC).date() + timedelta(days=7)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail("no HTTP"))) as c:
        with pytest.raises(ValueError, match="public UTC window"):
            await collect_baseline(c, LOCATION, DatePeriod(day, day), tmp_path)


def test_automatic_identity_cannot_claim_explicit_model_or_run():
    now = datetime.now(UTC)
    capture = ForecastCapture("open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast",
                              LOCATION, now, now, now + timedelta(days=1), selection_mode="automatic")
    for change in ({"model": "gfs_global"}, {"run_at": now}, {"provider": "met-norway"}):
        with pytest.raises(ValueError):
            replace(capture, **change)


@pytest.mark.asyncio
async def test_explicit_run_uses_archive_endpoint_and_records_request_evidence(tmp_path):
    run = datetime(2026, 10, 20, tzinfo=UTC)
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"hourly_units": {"time": "unixtime", "precipitation": "mm"},
                                       "hourly": {"time": [1792882800], "precipitation": [1]}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as c:
        result = await collect_once(c, LOCATION, "gfs_global", tmp_path, run_at=run)
    assert requests[0].url.host == "single-runs-api.open-meteo.com"
    assert requests[0].url.params["run"] == "2026-10-20T00:00"
    assert result["run_identity_basis"] == "requested_single_run"
    archive = json.loads(next(tmp_path.iterdir()).read_text())
    assert archive["metadata"]["run_at"] == run.isoformat()


@pytest.mark.asyncio
@pytest.mark.parametrize("model,run", [
    ("met-norway", datetime(2026, 10, 20, tzinfo=UTC)),
    ("gfs_global", datetime(2026, 10, 20)),
    ("gfs_global", datetime(2099, 1, 1, tzinfo=UTC)),
    ("gfs_global", datetime(2026, 10, 20, 1, tzinfo=UTC)),
])
async def test_invalid_run_never_sends_http(tmp_path, model, run):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail("no HTTP"))) as c:
        with pytest.raises(ValueError):
            await collect_once(c, LOCATION, model, tmp_path, run_at=run)


def test_shared_ledger_counts_failures_deduplicates_and_resets_by_utc_day(tmp_path):
    path, now = tmp_path / "ledger.sqlite", datetime.now(UTC)
    one, two = CampaignLedger(path), CampaignLedger(path)
    assert one.reserve("job-1", "open-meteo", now, 1)
    one.finish("job-1", None, "SyntheticFailure")
    assert not two.reserve("job-1", "open-meteo", now, 1)
    with pytest.raises(CampaignLimitExceeded):
        two.reserve("job-2", "open-meteo", now, 1)
    assert two.reserve("job-2", "open-meteo", now + timedelta(days=1), 1)
    assert one.reserve("job-3", "met-norway", now, 1)


def test_manifest_deduplicates_alias_points_and_marks_same_origin():
    now = datetime.now(UTC)
    plan = build_manifest("test", [LOCATION, replace(LOCATION, name="alias")],
                          ["gfs_global", "gfs_global", "ecmwf_ifs025", "met-norway"], now)["plan"]
    assert len(plan["jobs"]) == 3
    assert len({j["origin_family"] for j in plan["jobs"]}) == 2
    assert not plan["enabled"]
    assert not plan["collection_authorized"]


@pytest.mark.asyncio
async def test_disabled_future_expired_and_unauthorized_manifests_do_not_call(tmp_path):
    now = datetime.now(UTC)
    ledger = CampaignLedger(tmp_path / "ledger.sqlite")
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail("no HTTP"))) as c:
        disabled = build_manifest("test", [LOCATION], ["gfs_global"], now)
        assert await run_manifest(disabled, ledger, c, tmp_path, now=now) == []
        denied = build_manifest("test", [LOCATION], ["gfs_global"], now, enabled=True)
        with pytest.raises(ValueError, match="authorization"):
            await run_manifest(denied, ledger, c, tmp_path, now=now)
        for delta in (-1, 31):
            enabled = build_manifest("test", [LOCATION], ["gfs_global"], now,
                                     enabled=True, collection_authorized=True)
            assert await run_manifest(enabled, ledger, c, tmp_path,
                                      now=now + timedelta(minutes=delta)) == []
        changed = deepcopy(disabled)
        changed["plan"]["enabled"] = True
        with pytest.raises(ValueError, match="frozen"):
            await run_manifest(changed, ledger, c, tmp_path, now=now)


@pytest.mark.asyncio
async def test_concurrent_workers_share_budget_and_never_repeat_reserved_job(tmp_path):
    now = datetime.now(UTC)
    manifest = build_manifest("test", [LOCATION], ["gfs_global"], now,
                              enabled=True, collection_authorized=True)
    calls = []

    async def handle(request):
        calls.append(request)
        await asyncio.sleep(0)
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as c:
        await asyncio.gather(*(run_manifest(manifest, CampaignLedger(tmp_path / "ledger.sqlite"),
                                            c, tmp_path / "archives", now=now) for _ in range(2)))
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_pipeline_drift_cannot_reuse_a_frozen_manifest(tmp_path, monkeypatch):
    now = datetime.now(UTC)
    manifest = build_manifest("test", [LOCATION], ["gfs_global"], now,
                              enabled=True, collection_authorized=True)
    monkeypatch.setattr("climaprev.tools.experimental_campaign.pipeline_versions", dict)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail("no HTTP"))) as c:
        with pytest.raises(ValueError, match="pipeline"):
            await run_manifest(manifest, CampaignLedger(tmp_path / "ledger.sqlite"), c,
                                tmp_path, now=now)


@pytest.mark.asyncio
async def test_runner_forwards_frozen_run_without_falling_back_to_latest(tmp_path, monkeypatch):
    now = datetime(2026, 10, 20, 18, tzinfo=UTC)
    run = now.replace(hour=0)
    received = []

    async def collect(client, location, model, directory, *, run_at=None):
        received.append(run_at)
        return {"archive": "synthetic-archive"}

    monkeypatch.setattr("climaprev.tools.experimental_campaign.collect_once", collect)
    manifest = build_manifest("synthetic", [LOCATION], ["gfs_global"], now,
                              run_at=run, enabled=True, collection_authorized=True)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail("no HTTP"))) as c:
        result = await run_manifest(manifest, CampaignLedger(tmp_path / "ledger.sqlite"), c,
                                    tmp_path, now=now)
    assert received == [run]
    assert result[0]["status"] == "completed"


def synthetic_csv(day):
    header = ("REGIAO:;N\nUF:;PA\nESTACAO:;SYNTHETIC\nCODIGO (WMO):;A201\n"
              "LATITUDE:;-1,4\nLONGITUDE:;-48,4\nALTITUDE:;10\n"
              "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
              "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
              "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C);\n")
    start = datetime.combine(day, datetime.min.time(), UTC) + timedelta(hours=4)
    rows = []
    for index in range(24):
        stamp = start + timedelta(hours=index)
        rows.append(f"{stamp:%Y/%m/%d};{stamp:%H%M} UTC;1;10;30;20;\n")
    return (header + "".join(rows)).encode()


def test_station_pairing_preserves_day_boundary_and_rejects_municipal_substitution():
    day = date(2024, 1, 1)
    start = datetime(2024, 1, 1, 3, tzinfo=UTC)
    samples = [Measurement("precipitation_mm", start + timedelta(hours=i),
                            start + timedelta(hours=i+1), 2, "mm", "previous_hour_sum")
               for i in range(24)]
    report = pair_station_rain(samples, LOCATION, synthetic_csv(day), "A201", DatePeriod(day, day),
                               collected_at=start - timedelta(days=1), model="synthetic")
    assert report["rows"][0]["observed_mm"] == 24
    assert report["rows"][0]["forecast_mm"] == 48
    assert report["rows"][0]["eligible_exploratory"]
    assert not report["scientific_approval"]
    with pytest.raises(ValueError, match="coordinates"):
        pair_station_rain(samples, replace(LOCATION, latitude=-1.45), synthetic_csv(day),
                           "A201", DatePeriod(day, day), collected_at=start, model="synthetic")
    missing = pair_station_rain(samples[:-1], LOCATION, synthetic_csv(day), "A201",
                                DatePeriod(day, day), collected_at=start, model="synthetic")
    assert missing["rows"][0]["forecast_mm"] is None
    assert not missing["rows"][0]["eligible_exploratory"]
    assert not missing["rows"][0]["collected_before_target"]


@pytest.mark.parametrize("changes,reason", [
    ({"semantics": "instant"}, "forecast_semantics"),
    ({"unit": "m"}, "forecast_unit"),
    ({"value": True}, "forecast_invalid_value"),
    ({"value": -1}, "forecast_invalid_value"),
])
def test_rain_pairing_rejects_incompatible_forecast_measurements(changes, reason):
    day = date(2024, 1, 1)
    start = datetime(2024, 1, 1, 3, tzinfo=UTC)
    samples = [Measurement("precipitation_mm", start + timedelta(hours=i),
                            start + timedelta(hours=i+1), 2, "mm", "previous_hour_sum")
               for i in range(24)]
    samples[0] = replace(samples[0], **changes)
    result = pair_station_rain(samples, LOCATION, synthetic_csv(day), "A201", DatePeriod(day, day),
                               collected_at=start - timedelta(days=1), model="synthetic")
    row = result["rows"][0]
    assert row["forecast_mm"] is None
    assert row["observed_mm"] == 24
    assert reason in row["measurement_contract_exclusions"]
    assert "incompatible_measurement_contract" in row["exclusions"]
    assert not row["eligible_exploratory"]


def test_six_hour_forecast_pairs_with_real_observation_sums_without_proration():
    day = date(2024, 1, 1)
    start = datetime(2024, 1, 1, 3, tzinfo=UTC)
    samples = [Measurement("precipitation_mm", start + timedelta(hours=i),
                            start + timedelta(hours=i+6), 12, "mm", "next_6_hours_sum")
               for i in range(0, 24, 6)]
    result = pair_station_rain(samples, LOCATION, synthetic_csv(day), "A201", DatePeriod(day, day),
                               collected_at=start - timedelta(days=1), model="synthetic")
    row = result["rows"][0]
    assert row["forecast_mm"] == 48
    assert row["observed_mm"] == 24
    assert not row["measurement_contract_exclusions"]
    assert row["eligible_exploratory"]


@pytest.mark.parametrize("missing", [False, True])
def test_daily_baseline_pairs_without_inventing_hourly_values(missing):
    day = date(2024, 1, 1)
    baseline = {"model_identity": "unknown_auto_selection", "forecast": {
        "location": asdict(LOCATION), "period": {"start": day, "end": day},
        "fetched_at": datetime(2023, 12, 31, tzinfo=UTC),
        "days": [{"date": day, "precipitation_sum_mm": None if missing else 48}],
        "missing_fields": [],
    }}
    result = pair_baseline_rain(baseline, synthetic_csv(day), "A201")
    assert result["model"] == "operational-baseline"
    assert result["run_at"] is None
    assert result["rows"][0]["observed_mm"] == 24
    assert result["rows"][0]["forecast_mm"] == (None if missing else 48)
    assert result["rows"][0]["eligible_exploratory"] is (not missing)
    assert "forecast_samples_sha256" not in result
    assert not result["scientific_approval"]
