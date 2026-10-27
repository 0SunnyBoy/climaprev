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
