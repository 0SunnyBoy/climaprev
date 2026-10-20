import hashlib
from datetime import date

import pytest
from tests.unit.tools.test_collect_campaign import protocol
from tests.unit.tools.test_inmet_observations import station_csv

from climaprev.tools.spatial_plan import STATIONS, spatial_plan


def sources(year=2024):
    result = {}
    for city, code in STATIONS.items():
        raw = station_csv(day=date(year, 1, 1)).replace(b"A201", code.encode())
        result[city] = (raw, hashlib.sha256(raw).hexdigest())
    return result


def test_pairs_change_only_horizontal_coordinates_and_preserve_parent():
    parent = protocol()
    plan = spatial_plan(parent, sources())
    assert plan["snapshot_count"] == 72
    assert plan["maximum_http_calls_without_retries"] == 144
    for control, station in zip(plan["requests"][::2], plan["requests"][1::2], strict=True):
        assert control["pair"] == station["pair"]
        for provider in ("forecast", "observed"):
            left, right = control["parameters"][provider], station["parameters"][provider]
            assert {k: v for k, v in left.items() if k not in {"latitude", "longitude"}} == {
                k: v for k, v in right.items() if k not in {"latitude", "longitude"}}
            assert left["cell_selection"] == "nearest"
            assert left["elevation"] == 10
            assert left["end_date"].endswith("-29")
    assert parent == protocol()
    assert not plan["collection_executed"]
    assert not plan["candidate_fitting_executed"]


@pytest.mark.parametrize("invalid", ["checksum", "identity", "year", "holdout", "fit", "months"])
def test_invalid_sources_or_scope_fail_before_requests(invalid):
    parent, data = protocol(), sources()
    if invalid == "checksum":
        raw, _ = data["belem"]
        data["belem"] = (raw, "0" * 64)
    elif invalid == "identity":
        data["belem"] = data["brasilia"]
    elif invalid == "year":
        data = sources(2025)
    elif invalid == "holdout":
        parent["initial_adjustment_collection"]["year"] = 2025
    elif invalid == "fit":
        parent["authorization"]["candidate_fitting_allowed"] = True
    else:
        parent["initial_adjustment_collection"]["months"] = [4, 7, 10]
    with pytest.raises(ValueError):
        spatial_plan(parent, data)
