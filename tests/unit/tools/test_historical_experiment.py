from copy import deepcopy
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from climaprev.application.errors import WeatherDataInvalid
from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.models import DatePeriod
from climaprev.domain.risk_policy import ExperimentalRiskPolicy
from climaprev.tools.historical_data import normalize_hourly
from climaprev.tools.historical_experiment import (
    evaluate_snapshots,
    load_snapshot,
    save_snapshot,
    snapshot,
)


def payload(*, suffix="", zone="UTC", day=date(2026, 1, 1), gust=20.0):
    tz = ZoneInfo(zone)
    instant = datetime.combine(day, time.min, tz).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, tz).astimezone(UTC)
    times = []
    while instant < end:
        times.append(instant.astimezone(tz).replace(tzinfo=None).isoformat(timespec="minutes"))
        instant += timedelta(hours=1)
    return {"timezone": zone, "hourly_units": {
        f"temperature_2m{suffix}": "°C", f"precipitation{suffix}": "mm",
        f"wind_gusts_10m{suffix}": "km/h",
    }, "hourly": {
        "time": times, f"temperature_2m{suffix}": [25.0] * len(times),
        f"precipitation{suffix}": [0.0] * len(times),
        f"wind_gusts_10m{suffix}": [gust] * len(times),
    }}


def dataset():
    return snapshot({
        "latitude": 0.0, "longitude": 0.0, "start": "2026-01-01", "end": "2026-01-01",
        "lead_days": 1, "minimum_coverage": 1.0,
        "forecast_model": "gfs_global", "observed_model": "era5",
    }, payload(suffix="_previous_day1", gust=40), payload(gust=70), {},
        collected_at=datetime(2026, 2, 1, tzinfo=UTC))


@pytest.mark.parametrize("day,expected", [(date(2025, 3, 9), 23), (date(2025, 11, 2), 25)])
def test_civil_hour_coverage_includes_legitimate_repeated_dst_hours(day, expected) -> None:
    checked = normalize_hourly(payload(zone="America/New_York", day=day), DatePeriod(day, day))[day]
    assert checked.expected_hours == expected
    assert all(checked.eligible.values())
    assert checked.missing_fields == ()


def test_partial_rain_excludes_rain_without_dropping_valid_wind() -> None:
    data = dataset()
    data["forecast"]["hourly"]["precipitation_previous_day1"][0] = None
    report = evaluate_snapshots([data])
    assert report["eligible_overall_days"] == 0
    assert report["variants"]["R0"]["events"]["rain_daily"]["classification"]["cases"] == 0
    assert report["variants"]["R0"]["events"]["wind_gust"]["classification"]["cases"] == 1
    assert {r["event"] for r in report["excluded_events"]} == {"rain_daily", "rain_hourly"}
    assert report["variants"]["R0"]["overall"]["accuracy"] is None


def test_relaxed_coverage_never_scores_a_partial_sum_as_daily_rain() -> None:
    data = dataset()
    data["configuration"]["minimum_coverage"] = 0.9
    data["forecast"]["hourly"]["precipitation_previous_day1"][0] = None
    report = evaluate_snapshots([data])
    assert report["variants"]["R0"]["events"]["rain_daily"]["classification"]["cases"] == 0
    hourly = next(r for r in report["cases"] if r["event"] == "rain_hourly")
    assert hourly["quality"]["forecast_valid_hours"]["precipitation"] == 23


def test_candidates_and_calibration_share_frozen_target_and_paired_cases() -> None:
    data = dataset()
    report = evaluate_snapshots(
        [data], candidate=ExperimentalRiskPolicy(wind_gust_moderate_kmh=35, wind_gust_high_kmh=40),
        calibration=ForecastCalibration(profile_version="synthetic-test", enabled=True,
                                        wind_multiplier=2),
    )
    assert set(report["variants"]) == {"R0", "A", "B", "AB"}
    rows = [r for r in report["cases"] if r["event"] == "wind_gust"]
    assert {r["observed_level"] for r in rows} == {"high"}
    assert rows[0]["predicted_level"] == "moderate"
    assert all(r["predicted_level"] == "high" for r in rows[1:])
    assert len({r["case_id"] for r in rows}) == 1
    assert data == dataset()
    assert report["decision"] == "diagnostic_only_not_approved"


def test_snapshot_replay_is_deterministic_and_checks_integrity(tmp_path: Path) -> None:
    path = tmp_path / "inputs.json"
    data = dataset()
    save_snapshot(path, data)
    assert evaluate_snapshots([data]) == evaluate_snapshots([load_snapshot(path)])
    changed = deepcopy(data)
    changed["configuration"]["lead_days"] = 3
    with pytest.raises(ValueError, match="replace"):
        save_snapshot(path, changed)
    path.write_text(path.read_text().replace('"lead_days":1', '"lead_days":3'))
    with pytest.raises(ValueError, match="checksum"):
        load_snapshot(path)


def test_overlapping_inputs_are_deduplicated_and_conflicting_inputs_rejected() -> None:
    data = dataset()
    assert evaluate_snapshots([data, deepcopy(data)])["requested_unique_days"] == 1
    changed = deepcopy(data)
    changed["forecast"]["hourly"]["wind_gusts_10m_previous_day1"][0] = 90
    with pytest.raises(ValueError, match="conflicting"):
        evaluate_snapshots([data, changed])


def test_temporal_partitions_require_protocol_and_exclude_other_periods() -> None:
    protocol = {"splits": {
        "adjustment": {"start": "2025-01-01", "end": "2025-06-30"},
        "validation": {"start": "2025-07-01", "end": "2025-12-31"},
        "test": {"start": "2026-01-01", "end": "2026-01-31"},
    }}
    with pytest.raises(ValueError, match="protocol"):
        evaluate_snapshots([dataset()], partition="test")
    report = evaluate_snapshots([dataset()], protocol=protocol, partition="adjustment")
    assert report["requested_unique_days"] == 0
    assert report["outside_partition_days"] == 1
    assert evaluate_snapshots([dataset()], protocol=protocol, partition="test")[
        "eligible_overall_days"] == 1
    protocol["splits"]["test"]["start"] = "2025-12-31"
    with pytest.raises(ValueError, match="disjoint"):
        evaluate_snapshots([dataset()], protocol=protocol, partition="test")


def test_target_mutation_and_timezone_mismatch_are_rejected() -> None:
    data = dataset()
    data["reference"]["policy"]["wind_gust_high_kmh"] = 80
    with pytest.raises(ValueError, match="checksum"):
        evaluate_snapshots([data])
    data = dataset()
    data["observed"]["timezone"] = "America/Belem"
    with pytest.raises(ValueError, match="timezones"):
        evaluate_snapshots([data])


def test_algorithm_changes_require_explicit_migration() -> None:
    data = dataset()
    data["algorithms_sha256"]["domain/risk_evaluator.py"] = "0" * 64
    with pytest.raises(ValueError, match="algorithms"):
        evaluate_snapshots([data])


def test_duplicate_hours_and_invalid_units_do_not_create_fake_coverage() -> None:
    raw = payload()
    raw["hourly"]["time"][1] = raw["hourly"]["time"][0]
    period = DatePeriod(date(2026, 1, 1), date(2026, 1, 1))
    with pytest.raises(WeatherDataInvalid, match="duplicated"):
        normalize_hourly(raw, period)
    raw = payload()
    raw["hourly_units"] = {"temperature_2m": "°C", "precipitation": "mm",
                           "wind_gusts_10m": "m/s"}
    with pytest.raises(WeatherDataInvalid, match="units"):
        normalize_hourly(raw, period)
    raw = payload()
    raw.pop("hourly_units")
    with pytest.raises(WeatherDataInvalid, match="units"):
        normalize_hourly(raw, period)


def test_missing_day_is_reported_and_negative_rain_is_rejected() -> None:
    raw = payload()
    period = DatePeriod(date(2026, 1, 1), date(2026, 1, 2))
    days = normalize_hourly(raw, period)
    assert not any(days[period.end].eligible.values())
    raw["hourly"]["precipitation"][0] = -1
    with pytest.raises(WeatherDataInvalid, match="negative"):
        normalize_hourly(raw, period)


def development_fixture():
    from dataclasses import asdict

    from tests.support.experiment import protocol_fixture

    from climaprev.tools.experimental_candidate import register_candidate
    from climaprev.tools.historical_experiment import digest

    protocol = protocol_fixture()
    protocol["protocol"]["splits"] = {
        "adjustment": {"start": "2025-01-01", "end": "2025-06-30"},
        "validation": {"start": "2026-01-01", "end": "2026-01-31"},
        "test": {"start": "2027-01-01", "end": "2027-01-31"}}
    configurations = []
    for multiplier in (1, 1.75):
        configurations.append({"policy": asdict(ExperimentalRiskPolicy()),
                               "calibration": asdict(ForecastCalibration(profile_version=f"fixture-{multiplier}",
                                                                         enabled=True, wind_multiplier=multiplier)),
                               "normalization": {"version": "fixture", "sha256": "a" * 64},
                               "models": {"gfs_global": "b" * 64}})
    protocol["protocol"]["criteria"]["development"] = {
        "configurations": sorted(digest(c) for c in configurations), "event": "wind_gust",
        "metric": "mae", "direction": "min", "tie_break": "configuration_sha256_ascending"}
    protocol["sha256"] = digest(protocol["protocol"])
    candidates = [register_candidate(protocol=protocol, code_version="fixture", **c) for c in configurations]
    adjustment = dataset()
    adjustment["configuration"].update(start="2025-01-01", end="2025-01-01")
    adjustment["forecast"] = payload(suffix="_previous_day1", day=date(2025, 1, 1), gust=40)
    adjustment["observed"] = payload(day=date(2025, 1, 1), gust=70)
    return protocol, candidates, adjustment


def test_development_selects_known_validation_optimum_without_test_access():
    from climaprev.tools.compare_historical import select_development

    protocol, candidates, adjustment = development_fixture()
    accesses = []
    def canary():
        accesses.append("test")
        pytest.fail("independent test was accessed")
    result = select_development(protocol, candidates, loaders={"adjustment": lambda: [adjustment],
                                "validation": lambda: [dataset()], "test": canary}, mode="diagnostic")
    assert result["selected_candidate_sha256"] == candidates[1]["sha256"]
    assert next(s for s in result["scores"] if s["candidate_sha256"] == candidates[1]["sha256"])["validation_score"] == 0
    assert result["test_accesses"] == 0
    assert accesses == []
    assert result["promotion_allowed"] is False


def test_predeclared_tie_rule_is_stable_under_option_order():
    from climaprev.tools.compare_historical import configuration_fingerprint, select_development

    protocol, candidates, adjustment = development_fixture()
    zero = dataset()
    zero["forecast"]["hourly"]["wind_gusts_10m_previous_day1"] = [0] * 24
    loaders = {"adjustment": lambda: [adjustment], "validation": lambda: [zero]}
    expected = min(candidates, key=configuration_fingerprint)["sha256"]
    result = select_development(protocol, list(reversed(candidates)), loaders=loaders, mode="diagnostic")
    assert result["selected_candidate_sha256"] == expected


def test_undeclared_option_is_refused_before_loading_any_partition():
    from climaprev.tools.compare_historical import select_development
    from climaprev.tools.historical_experiment import digest

    protocol, candidates, _ = development_fixture()
    candidates[0]["candidate"]["models"]["gfs_global"] = "c" * 64
    candidates[0]["sha256"] = digest(candidates[0]["candidate"])
    with pytest.raises(ValueError, match="declared"):
        select_development(protocol, candidates, loaders={}, mode="diagnostic")


def test_real_development_without_e2_has_zero_partition_reads():
    from climaprev.tools.compare_historical import select_development

    protocol, candidates, _ = development_fixture()
    with pytest.raises(ValueError, match="E2"):
        select_development(protocol, candidates, loaders={})


def test_missing_partition_or_rule_cannot_fall_back_to_test():
    from climaprev.tools.compare_historical import select_development

    protocol, candidates, _ = development_fixture()
    with pytest.raises(ValueError, match="loaders"):
        select_development(protocol, candidates, loaders={"test": lambda: [dataset()]}, mode="diagnostic")
