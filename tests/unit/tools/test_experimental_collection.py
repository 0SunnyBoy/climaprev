import json
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from climaprev.application.errors import ProviderRateLimited
from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_collection import collect_once
from climaprev.tools.experimental_normalization import (
    Measurement,
    complete_rain_total,
    met_norway_measurements,
    open_meteo_measurements,
)


def om():
    return {"hourly_units": {"time": "unixtime", "precipitation": "mm"},
            "hourly": {"time": [1792882800, 1792886400], "precipitation": [None, 2]}}


def met():
    return {"properties": {"meta": {"units": {"wind_speed": "m/s", "precipitation_amount": "mm"}},
                           "timeseries": [
                               {"time": "2026-10-25T00:00:00Z", "data": {
                                   "instant": {"details": {"wind_speed": 10}},
                                   "next_1_hours": {"details": {"precipitation_amount": 1}},
                                   "next_6_hours": {"details": {"precipitation_amount": 99}}}},
                               {"time": "2026-10-25T01:00:00Z", "data": {
                                   "next_6_hours": {"details": {"precipitation_amount": 6}}}},
                               {"time": "2026-10-25T02:00:00Z", "data": {
                                   "next_6_hours": {"details": {"precipitation_amount": 99}}}},
                           ]}}


def test_open_meteo_rain_ends_at_timestamp_and_null_is_not_zero():
    result = open_meteo_measurements(om())
    assert result[0].value is None
    assert result[1].value == 2
    assert result[1].end - result[1].start == timedelta(hours=1)
    assert complete_rain_total(result, result[0].start, result[1].end) is None
    assert complete_rain_total(result, result[1].start, result[1].end) == 2


def test_met_rain_uses_shortest_nonoverlapping_period_and_converts_wind():
    result = met_norway_measurements(met())
    assert result[0].value == 36
    assert result[0].unit == "km/h"
    rain = [r for r in result if r.variable == "precipitation_mm"]
    assert [r.value for r in rain] == [1, 6]
    assert rain[0].end == rain[1].start
    assert complete_rain_total(result, rain[0].start, rain[-1].end) == 7
    assert complete_rain_total(result, rain[0].start, rain[-1].end - timedelta(hours=1)) is None


@pytest.mark.parametrize("kind", ["gap", "overlap", "null", "crossing", "empty"])
def test_incomplete_rain_is_not_silently_prorated(kind):
    start = datetime(2026, 10, 25, tzinfo=UTC)
    end = start + timedelta(hours=2)
    a = Measurement("precipitation_mm", start, start + timedelta(hours=1), 1, "mm", "sum")
    b = Measurement("precipitation_mm", a.end, end, 1, "mm", "sum")
    if kind == "gap":
        samples = [b]
    elif kind == "overlap":
        samples = [a, a, b]
    elif kind == "null":
        samples = [a, Measurement(b.variable, b.start, b.end, None, b.unit, b.semantics)]
    elif kind == "crossing":
        samples = [Measurement(a.variable, start - timedelta(hours=1), end, 1, "mm", "sum")]
    else:
        samples = []
    assert complete_rain_total(samples, start, end) is None


@pytest.mark.parametrize("change", ["unit", "length", "time", "negative", "nan"])
def test_open_meteo_invalid_contract_is_rejected(change):
    payload = om()
    if change == "unit":
        payload["hourly_units"]["precipitation"] = "inch"
    elif change == "length":
        payload["hourly"]["precipitation"] = [1]
    elif change == "time":
        payload["hourly"]["time"] = [2, 1]
    elif change == "negative":
        payload["hourly"]["precipitation"] = [-1, 1]
    else:
        payload["hourly"]["precipitation"] = [float("nan"), 1]
    with pytest.raises(ValueError):
        open_meteo_measurements(payload)


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["gfs_global", "ecmwf_ifs025", "icon_global", "met-norway"])
async def test_collection_preserves_request_identity_and_never_invents_run(tmp_path, model):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=met() if model == "met-norway" else om())

    location = CanonicalLocation("Belém", -1.4558, -48.5044, "America/Belem", "fixture")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        result = await collect_once(client, location, model, tmp_path)
    assert len(requests) == 1
    assert "ClimaPrev" in requests[0].headers["User-Agent"]
    assert result["run_at"] is None
    assert result["scientific_approval"] is False
    archive = json.loads(next(tmp_path.iterdir()).read_text())
    assert archive["payload"]["response"] == (met() if model == "met-norway" else om())
    if model != "met-norway":
        assert archive["payload"]["request_parameters"]["models"] == model


@pytest.mark.asyncio
async def test_429_does_not_retry_or_write_an_archive(tmp_path):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(429)

    location = CanonicalLocation("Belém", -1.45, -48.5, "America/Belem", "fixture")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(ProviderRateLimited):
            await collect_once(client, location, "gfs_global", tmp_path)
    assert len(requests) == 1
    assert not list(tmp_path.iterdir())


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["gfs_global", "ecmwf_ifs025"])
async def test_d7_collection_covers_entire_local_day_west_of_utc(tmp_path, monkeypatch, model):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 23, 12, tzinfo=UTC)

    monkeypatch.setattr("climaprev.tools.experimental_collection.datetime", Clock)

    def handle(request):
        count = int(request.url.params["forecast_days"]) * 24
        midnight = datetime(2026, 10, 23, tzinfo=UTC)
        return httpx.Response(200, json={
            "hourly_units": {"time": "unixtime", "precipitation": "mm"},
            "hourly": {"time": [int((midnight + timedelta(hours=i)).timestamp())
                                for i in range(count)], "precipitation": [1] * count},
        })

    location = CanonicalLocation("Belém", -1.45, -48.5, "America/Belem", "fixture")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        report = await collect_once(client, location, model, tmp_path)
    assert report["rain_coverage"]["D+7"]["rain_total_mm"] == 24
    assert report["rain_coverage"]["D+7"]["complete_rain_interval"]


@pytest.mark.parametrize("kind", ["unit", "humidity", "naive", "duplicate"])
def test_met_rejects_malformed_measurements(kind):
    payload = met()
    props = payload["properties"]
    if kind == "unit":
        props["meta"]["units"]["wind_speed"] = "knots"
    elif kind == "humidity":
        props["meta"]["units"]["relative_humidity"] = "%"
        props["timeseries"][0]["data"]["instant"]["details"]["relative_humidity"] = 101
    elif kind == "naive":
        props["timeseries"][0]["time"] = "2026-10-25T00:00:00"
    else:
        props["timeseries"][1]["time"] = props["timeseries"][0]["time"]
    with pytest.raises(ValueError):
        met_norway_measurements(payload)


@pytest.mark.parametrize("problem,reason", [
    ("none", None), ("missing", "variable_absent"),
    ("d7", "interval_incomplete"), ("partial", "interval_incomplete"),
    ("unit", "unit_mismatch"),
])
def test_capability_is_per_variable_and_complete_target_interval(problem, reason):
    from climaprev.tools.experimental_collection import assess_capability

    start = datetime(2030, 1, 1, tzinfo=UTC)
    samples = [Measurement("precipitation_mm", start + timedelta(hours=i),
                           start + timedelta(hours=i + 1), 1, "mm", "previous_hour_sum")
               for i in range(24)]
    target = start
    if problem == "missing":
        samples = []
    elif problem == "d7":
        target += timedelta(days=7)
    elif problem == "partial":
        samples.pop()
    elif problem == "unit":
        samples[0] = Measurement(samples[0].variable, samples[0].start, samples[0].end,
                                 1, "inch", samples[0].semantics)
    result = assess_capability("gfs_global", samples, variable="precipitation_mm", unit="mm",
                               semantics="previous_hour_sum", start=target,
                               end=target + timedelta(days=1))
    assert result["declared_supported"] is True
    assert result["eligible"] is (reason is None)
    assert result["variable"] == "precipitation_mm"
    if reason:
        assert reason in result["reasons"]
    else:
        assert result["reasons"] == []


def test_unsupported_gust_is_not_invented_for_met_adapter():
    from climaprev.tools.experimental_collection import assess_capability

    start = datetime(2030, 1, 1, tzinfo=UTC)
    result = assess_capability("met-norway", [], variable="gust_kmh", unit="km/h",
                               semantics="previous_hour_max", start=start,
                               end=start + timedelta(days=1))
    assert result["declared_supported"] is False
    assert result["eligible"] is False
    assert "variable_not_supported_by_adapter" in result["reasons"]


@pytest.mark.parametrize("kind,expected", [
    ("unknown", "unknown"), ("requested", "requested_only"),
    ("verified", "verified"), ("updated", "unknown"),
])
def test_run_evidence_never_confuses_collection_update_and_initialization(kind, expected):
    from climaprev.tools.experimental_collection import describe_run

    now = datetime(2030, 1, 1, 6, tzinfo=UTC)
    run = now - timedelta(hours=6)
    kwargs = {}
    if kind == "requested":
        kwargs["requested_run"] = run
    elif kind == "verified":
        kwargs.update(verified_run=run, verification_reference="synthetic-provider-record")
    elif kind == "updated":
        kwargs["updated_at"] = now - timedelta(minutes=10)
    result = describe_run(now, **kwargs)
    assert result["basis"] == expected
    assert result["run_at"] == (run.isoformat() if kind == "verified" else None)
    assert result["collected_at"] == now.isoformat()
    if kind == "requested":
        assert result["requested_run_at"] == run.isoformat()
    if kind == "updated":
        assert result["updated_at"] == (now - timedelta(minutes=10)).isoformat()


def test_initialization_after_collection_and_unreferenced_verification_are_rejected():
    from climaprev.tools.experimental_collection import describe_run

    now = datetime(2030, 1, 1, tzinfo=UTC)
    with pytest.raises(ValueError, match="collection"):
        describe_run(now, requested_run=now + timedelta(seconds=1))
    with pytest.raises(ValueError, match="reference"):
        describe_run(now, verified_run=now)


@pytest.mark.parametrize("model,family", [
    ("gfs_global", "NOAA-GFS"), ("icon_global", "DWD-ICON"),
    ("ecmwf_ifs025", "ECMWF-IFS"), ("met-norway", "ECMWF-IFS"),
    ("operational-baseline", "automatic-unknown"),
])
def test_catalog_preserves_source_family_per_adapter(model, family):
    from climaprev.tools.experimental_collection import source_catalog

    result = source_catalog([model])
    assert result["models"] == [{"model": model, "origin_family": family}]


def test_catalog_does_not_count_shared_or_unknown_origin_as_independent_models():
    from climaprev.tools.experimental_collection import source_catalog

    result = source_catalog(["ecmwf_ifs025", "met-norway", "operational-baseline", "met-norway"])
    assert len(result["models"]) == 3
    assert result["known_family_count"] == 1
    assert result["unknown_origin_models"] == ["operational-baseline"]
    assert result["independence_proven"] is False


@pytest.mark.parametrize("kind", ["instant", "interval", "null", "empty", "gap"])
def test_measurement_contract_preserves_instants_intervals_and_missing_values(kind):
    from climaprev.tools.experimental_normalization import validate_measurements

    start = datetime(2030, 1, 1, tzinfo=UTC)
    if kind == "instant":
        samples = [Measurement("temperature_c", start, None, 25, "°C", "instant")]
        unit, semantics = "°C", "instant"
    else:
        samples = [Measurement("precipitation_mm", start, start + timedelta(hours=1),
                               None if kind == "null" else 1, "mm", "previous_hour_sum")]
        unit, semantics = "mm", "previous_hour_sum"
    if kind == "empty":
        samples = []
    assert validate_measurements(samples, unit=unit, semantics=semantics) == samples
    if kind == "null":
        assert samples[0].value is None
    if kind == "gap":
        assert complete_rain_total(samples, start, start + timedelta(hours=2)) is None


@pytest.mark.parametrize("kind", ["unit", "semantics", "naive", "instant_interval", "nan", "duplicate"])
def test_measurement_contract_rejects_false_equivalence(kind):
    from climaprev.tools.experimental_normalization import validate_measurements

    start = datetime(2030, 1, 1, tzinfo=UTC)
    sample = Measurement("temperature_c", start, None, 25, "°C", "instant")
    from dataclasses import replace

    if kind == "unit":
        sample = replace(sample, unit="°F")
    elif kind == "semantics":
        sample = replace(sample, semantics="previous_hour_max")
    elif kind == "naive":
        sample = replace(sample, start=datetime(2030, 1, 1))
    elif kind == "instant_interval":
        sample = replace(sample, end=start + timedelta(hours=1))
    elif kind == "nan":
        sample = replace(sample, value=float("nan"))
    with pytest.raises(ValueError, match="measurement|contract"):
        validate_measurements([sample, sample] if kind == "duplicate" else [sample],
                              unit="°C", semantics="instant")
