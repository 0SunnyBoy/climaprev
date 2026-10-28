from dataclasses import asdict
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_campaign import pipeline_versions
from climaprev.tools.experimental_preparation import (
    TemporalPartition,
    prepare_pilot,
    qualify_primary_pilot,
    reconcile_station,
    validate_partitions,
)

NOW = datetime(2026, 10, 28, 17, tzinfo=UTC)
POINT = CanonicalLocation("Synthetic", -1.4, -48.4, "America/Belem", "test")


def test_calendar_is_disabled_and_freezes_requested_run_per_slot():
    result = prepare_pilot([POINT], first_slot=NOW.replace(day=29, hour=18), days=14,
                            models=["gfs_global", "met-norway", "operational-baseline"],
                            campaign="synthetic", now=NOW)
    assert result["planned_jobs"] == 42
    assert not result["collection_enabled"]
    for manifest in result["manifests"]:
        plan = manifest["plan"]
        assert not plan["enabled"] and not plan["collection_authorized"]
        for job in plan["jobs"]:
            identity = job["identity"]
            if identity["model"] == "gfs_global":
                assert datetime.fromisoformat(identity["run_at"]).hour == 0
                assert (datetime.fromisoformat(identity["slot"])
                        - datetime.fromisoformat(identity["run_at"])) == timedelta(hours=18)
            else:
                assert "run_at" not in identity


@pytest.mark.parametrize("first,days", [(NOW - timedelta(days=1), 14),
                                       (NOW.replace(day=29, hour=12), 14),
                                       (NOW.replace(day=29, hour=18), True)])
def test_expired_wrong_hour_and_invalid_duration_rejected(first, days):
    with pytest.raises(ValueError):
        prepare_pilot([POINT], first_slot=first, days=days, models=["gfs_global"],
                      campaign="synthetic", now=NOW)


def test_current_catalogue_does_not_silently_replace_historical_coordinates():
    historical = {"code": "A201", "latitude": -1.411228, "longitude": -48.439512}
    current = {"CD_ESTACAO": "A201", "DC_NOME": "BELEM", "VL_LATITUDE": "-1.41111111",
               "VL_LONGITUDE": "-48.43944444", "CD_SITUACAO": "Operante", "DT_FIM_OPERACAO": None}
    result = reconcile_station(current, historical, timezone="America/Belem")
    assert result["catalogue_operational"]
    assert result["historical_pairing_requires_reconciliation"]
    assert not result["activation_ready"]
    assert historical["latitude"] == -1.411228


def partitions():
    return [TemporalPartition("development", date(2024, 1, 1), date(2026, 11, 18)),
            TemporalPartition("selection", date(2026, 12, 3), date(2026, 12, 31)),
            TemporalPartition("confirmation", date(2027, 1, 15), date(2028, 1, 14))]


def test_temporal_separation_does_not_claim_independence_or_actual_freeze():
    result = validate_partitions(partitions(), embargo_days=7, max_horizon_days=7,
                                  candidate_frozen_at=datetime(2027, 1, 7, 23, tzinfo=UTC))
    assert result["earliest_confirmatory_run"] == "2027-01-08T00:00:00+00:00"
    assert not result["prospective_independence_verified"]
    assert not result["confirmation_enabled"]


def test_freeze_after_first_d7_emission_is_rejected_even_before_first_target_day():
    with pytest.raises(ValueError, match="earliest confirmatory"):
        validate_partitions(partitions(), embargo_days=7, max_horizon_days=7,
                            candidate_frozen_at=datetime(2027, 1, 10, tzinfo=UTC))


def test_overlap_and_insufficient_embargo_are_rejected():
    parts = partitions()
    parts[1] = TemporalPartition("selection", date(2026, 11, 19), date(2026, 12, 31))
    with pytest.raises(ValueError, match="embargo"):
        validate_partitions(parts, embargo_days=7, max_horizon_days=7,
                            candidate_frozen_at=datetime(2027, 1, 7, tzinfo=UTC))


def test_target_dates_separated_but_first_test_run_overlaps_embargo_are_rejected():
    parts = partitions()
    parts[-1] = TemporalPartition("confirmation", date(2027, 1, 10), date(2028, 1, 9))
    with pytest.raises(ValueError, match="issuance"):
        validate_partitions(parts, embargo_days=7, max_horizon_days=7,
                            candidate_frozen_at=datetime(2027, 1, 2, tzinfo=UTC))


@pytest.mark.parametrize("problem", [None, "observations", "forecast", "pipeline"])
def test_primary_pilot_requires_fresh_observations_and_all_arms_without_activating(problem):
    calendar = prepare_pilot([POINT], first_slot=NOW.replace(day=29, hour=18), days=14,
                             models=["operational-baseline", "gfs_global", "ecmwf_ifs025",
                                     "icon_global", "met-norway"], campaign="synthetic", now=NOW)
    zone = ZoneInfo(POINT.timezone)
    end = datetime.combine(NOW.astimezone(zone).date(), datetime.min.time(), zone).astimezone(UTC)
    report = {
        "schema": "climaprev-integrated-slot-evaluation-v1", "station": "synthetic",
        "station_point": asdict(POINT), "evaluation_pipeline_sha256": pipeline_versions(),
        "observation_readiness": {"station_version_matches": True, "end_utc": end.isoformat(),
                                  "variables": {"precipitation_mm": {"coverage": 1}}},
        "horizons": [{"collection_lead_days": 1, "missing_expected_arms": [],
                      "forecast_rain_available": {m: True for m in (
                          "operational-baseline", "gfs_global", "ecmwf_ifs025", "icon_global", "met-norway")}}],
    }
    if problem == "observations":
        report["observation_readiness"]["variables"]["precipitation_mm"]["coverage"] = 0
    elif problem == "forecast":
        report["horizons"][0]["forecast_rain_available"]["gfs_global"] = False
    elif problem == "pipeline":
        report["evaluation_pipeline_sha256"] = {}
    result = qualify_primary_pilot(calendar, [report], operational_stations={"synthetic"},
                                    now=NOW, min_coverage=0.9)
    assert result["ready"] == (problem is None)
    assert not result["pilot_activated"] and not result["promotion_allowed"]
