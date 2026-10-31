from copy import deepcopy

import pytest
from tests.unit.tools.test_collect_campaign import protocol
from tests.unit.tools.test_spatial_plan import sources

from climaprev.tools.collect_spatial import collect_spatial, validate_payload
from climaprev.tools.spatial_plan import spatial_plan


def payload(params):
    fields = params["hourly"].split(",")
    return {"latitude": -1.5, "longitude": -48.5, "elevation": params["elevation"],
            "timezone": params["timezone"],
            "hourly_units": {field: "mm" if field.startswith("precipitation") else
                             "km/h" if field.startswith("wind_gusts") else "°C"
                             for field in fields},
            "hourly": {"time": ["2024-01-01T00:00"],
                       **{field: [1.0] for field in fields}}}


@pytest.mark.asyncio
async def test_preflight_then_resume_without_network_and_reject_drift(tmp_path, monkeypatch):
    plan = spatial_plan(protocol(), sources())
    calls = []

    async def get_json(self, url, params):
        calls.append(params)
        return payload(params)

    async def no_sleep(seconds):
        pass

    monkeypatch.setattr("climaprev.tools.collect_spatial.AsyncJsonHttpClient.get_json", get_json)
    monkeypatch.setattr("climaprev.tools.collect_spatial.asyncio.sleep", no_sleep)
    result = await collect_spatial(plan, plan, tmp_path, preflight_only=True)
    assert result["preflight_passed"]
    assert not result["complete"]
    assert len(calls) == 4
    repeated = await collect_spatial(plan, plan, tmp_path, preflight_only=True)
    assert result == repeated
    assert len(calls) == 4
    altered = deepcopy(plan)
    altered["requests"][0]["parameters"]["forecast"]["elevation"] = 99
    with pytest.raises(ValueError, match="verified"):
        await collect_spatial(altered, plan, tmp_path)


@pytest.mark.asyncio
async def test_preflight_failure_stops_expansion_without_snapshot(tmp_path, monkeypatch):
    plan = spatial_plan(protocol(), sources())
    calls = []

    async def get_json(self, url, params):
        calls.append(params)
        return {**payload(params), "elevation": 999}

    monkeypatch.setattr("climaprev.tools.collect_spatial.AsyncJsonHttpClient.get_json", get_json)
    result = await collect_spatial(plan, plan, tmp_path)
    assert not result["preflight_passed"]
    assert len(result["failures"]) == 1
    assert len(calls) == 1
    assert not list(tmp_path.glob("*.inputs.json"))


@pytest.mark.parametrize("field,value", [("elevation", True), ("latitude", 91),
                                        ("longitude", float("nan")), ("timezone", "UTC"),
                                        ("hourly", {})])
def test_invalid_provider_metadata_rejected(field, value):
    plan = spatial_plan(protocol(), sources())
    params = plan["requests"][0]["parameters"]["forecast"]
    with pytest.raises(ValueError):
        validate_payload({**payload(params), field: value}, params, 1)
