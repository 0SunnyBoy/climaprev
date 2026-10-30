import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast


def capture():
    return ForecastCapture(
        provider="open-meteo", model="gfs_global", endpoint="https://api.open-meteo.com/v1/forecast",
        location=CanonicalLocation("Belém", -1.45, -48.5, "America/Belem", "station-fixture"),
        collected_at=datetime(2026, 10, 24, 6, tzinfo=UTC),
        run_at=datetime(2026, 10, 24, 0, tzinfo=UTC),
        valid_start=datetime(2026, 10, 25, 3, tzinfo=UTC),
        valid_end=datetime(2026, 10, 26, 3, tzinfo=UTC),
    )


def test_preserves_missing_values_chronology_and_idempotent_archive(tmp_path):
    payload = {"hourly": {"precipitation": [None, 0, 2.5]}}
    path = archive_forecast(tmp_path, capture(), payload)
    report = json.loads(path.read_text())
    assert report["payload"] == payload
    assert report["metadata"]["run_lead_hours"] == 27
    assert report["metadata"]["collection_lead_hours"] == 21
    assert report["metadata"]["timing_issues"] == []
    assert report["scientific_approval"] is False
    assert archive_forecast(tmp_path, capture(), payload) == path
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.parametrize("change", [
    {"model": "icon_global"}, {"run_at": datetime(2026, 10, 23, 18, tzinfo=UTC)},
    {"location": CanonicalLocation("Brasília", -15.8, -47.9, "America/Sao_Paulo", "fixture")},
    {"provider": "met-norway", "endpoint": "https://api.met.no/weatherapi/locationforecast/2.0/compact"},
])
def test_model_run_provider_and_location_never_share_archive(tmp_path, change):
    first = archive_forecast(tmp_path, capture(), {})
    assert archive_forecast(tmp_path, replace(capture(), **change), {}) != first


def test_changed_payload_is_preserved_separately_and_corruption_is_not_overwritten(tmp_path):
    path = archive_forecast(tmp_path, capture(), {"value": 1})
    assert archive_forecast(tmp_path, capture(), {"value": 2}) != path
    path.write_text("corrupted")
    with pytest.raises(ValueError, match="differs"):
        archive_forecast(tmp_path, capture(), {"value": 1})
    assert path.read_text() == "corrupted"


def test_unknown_run_and_late_capture_remain_explicit_not_approved(tmp_path):
    late = replace(capture(), run_at=None, collected_at=capture().valid_start)
    report = json.loads(archive_forecast(tmp_path, late, {}).read_text())
    assert report["metadata"]["timing_issues"] == ["model_run_unknown", "collected_not_before_target"]
    assert report["metadata"]["run_lead_hours"] is None
    assert not report["scientific_approval"]


def test_lead_uses_elapsed_time_across_daylight_saving_transition(tmp_path):
    zone = ZoneInfo("America/New_York")
    shifted = replace(capture(), run_at=datetime(2026, 10, 31, 0, tzinfo=zone),
                      collected_at=datetime(2026, 10, 31, 6, tzinfo=zone),
                      valid_start=datetime(2026, 11, 2, 0, tzinfo=zone),
                      valid_end=datetime(2026, 11, 3, 0, tzinfo=zone))
    report = json.loads(archive_forecast(tmp_path, shifted, {}).read_text())
    assert report["metadata"]["run_lead_hours"] == 49
    assert report["metadata"]["collection_lead_hours"] == 43


@pytest.mark.parametrize("change", [
    {"endpoint": "http://api.open-meteo.com/v1/forecast"},
    {"endpoint": "https://api.open-meteo.com.evil.test/v1/forecast"},
    {"endpoint": "https://user:password@api.open-meteo.com/v1/forecast"},
    {"endpoint": "https://api.open-meteo.com/v1/forecast?apikey=synthetic"},
    {"model": "best_match"}, {"collected_at": datetime(2026, 10, 24)},
    {"valid_end": capture().valid_start},
    {"run_at": capture().collected_at + timedelta(seconds=1)},
])
def test_rejects_invalid_identity_or_time(change):
    with pytest.raises(ValueError):
        replace(capture(), **change)


@pytest.mark.parametrize("payload", [{"v": float("nan")}, {"v": "x" * (4 * 1024 * 1024)}])
def test_invalid_or_oversized_payload_creates_no_archive(tmp_path, payload):
    with pytest.raises(ValueError):
        archive_forecast(tmp_path, capture(), payload)
    assert not list(tmp_path.iterdir())


def test_evidence_roundtrip_binds_protocol_inputs_and_code_without_overwrite(tmp_path):
    from climaprev.tools.experimental_archive import load_evidence, save_evidence
    from climaprev.tools.historical_experiment import digest

    parent = tmp_path / "input.json"
    parent.write_text('{"fixture":42}')
    path = tmp_path / "result.json"
    protocol_hash = digest({"fixture": "protocol"})
    report = save_evidence(path, protocol_sha256=protocol_hash, parents={"source": parent},
                           code_version="synthetic-revision", payload={"mae": 1.5})
    assert report["payload"] == {"mae": 1.5}
    assert report["protocol_sha256"] == protocol_hash
    assert report["code_version"] == "synthetic-revision"
    assert load_evidence(path) == report
    assert save_evidence(path, protocol_sha256=protocol_hash, parents={"source": parent},
                         code_version="synthetic-revision", payload={"mae": 1.5}) == report
    before = path.read_bytes()
    with pytest.raises(ValueError, match="overwrite"):
        save_evidence(path, protocol_sha256=protocol_hash, parents={"source": parent},
                      code_version="synthetic-revision", payload={"mae": 0})
    assert path.read_bytes() == before


def test_evidence_rejects_changed_parent(tmp_path):
    from climaprev.tools.experimental_archive import load_evidence, save_evidence
    from climaprev.tools.historical_experiment import digest

    parent = tmp_path / "input.csv"
    parent.write_text("synthetic-original")
    path = tmp_path / "result.json"
    save_evidence(path, protocol_sha256=digest({}), parents={"source": parent},
                  code_version="synthetic", payload={})
    parent.write_text("synthetic-changed")
    with pytest.raises(ValueError, match="parent"):
        load_evidence(path)


def test_evidence_rejects_missing_code_version_without_writing(tmp_path):
    from climaprev.tools.experimental_archive import save_evidence
    from climaprev.tools.historical_experiment import digest

    path = tmp_path / "absent.json"
    with pytest.raises(ValueError, match="code"):
        save_evidence(path, protocol_sha256=digest({}), parents={}, code_version="", payload={})
    assert not path.exists()
