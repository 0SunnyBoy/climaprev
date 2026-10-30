from datetime import date, timedelta

import pytest

from climaprev.tools.experimental_criteria import RainCriteria
from climaprev.tools.experimental_uncertainty import (
    RainPair,
    evaluate_development_reports,
    evaluate_paired_rain,
)


def evaluate(rows, **overrides):
    options = {"criteria": RainCriteria(.05, 0., .9, 10, 2, 0., 0., .95),
                   "planned_cases": 40, "event_threshold_mm": 50., "block_days": 3,
                   "repetitions": 100, "seed": 42}
    options.update(overrides)
    return evaluate_paired_rain(rows, **options)


def test_known_improvement_reproducible_and_never_certifies_independence():
    rows = [RainPair(station, date(2024, 1, 1)+timedelta(days=i), 60.,
                     70.+i, 61.+i/10) for i in range(20) for station in ("A", "B")]
    result = evaluate(rows)
    assert result == evaluate(list(reversed(rows)))
    assert result["scores"]["mae"]["estimate"] == pytest.approx(-17.55)
    assert result["scores"]["mae"]["interval"][1] < 0
    assert result["scores"]["mae"]["calendar_dates"] == 20
    assert result["evidence"]["common_pairs"] == 40
    assert result["diagnostic"]["status"] == "inconclusive"
    assert "independent_test_not_established" in result["diagnostic"]["missing_requirements"]
    assert result["promotion_allowed"] is False


def test_empty_missing_and_no_events_remain_inconclusive():
    result = evaluate([])
    assert result["scores"] == {}
    assert result["evidence"]["baseline_mae"] is None
    assert result["diagnostic"]["common_coverage"] == 0
    rows = [RainPair("A", date(2024, 1, 1)+timedelta(days=i), 0., 1., 0.) for i in range(12)]
    result = evaluate(rows)
    assert result["scores"]["recall"]["interval"] is None
    assert result["scores"]["false_alarm"]["undefined_repetitions"] == 100


def test_calendar_gap_and_short_segment_suppress_interval():
    rows = [RainPair("A", date(2024, 1, day), 1., float(day), 0.) for day in (1, 2, 8, 9)]
    result = evaluate(rows)
    assert result["scores"]["mae"]["segment_lengths"] == (2, 2)
    assert result["scores"]["mae"]["interval"] is None


@pytest.mark.parametrize("overrides", [{"block_days": True}, {"repetitions": 1},
                                       {"seed": False}, {"event_threshold_mm": 0},
                                       {"planned_cases": 0}])
def test_invalid_parameters_rejected(overrides):
    with pytest.raises((ValueError, TypeError)):
        evaluate([RainPair("A", date(2024, 1, 1), 1., 2., 3.)], **overrides)


def test_duplicates_and_invalid_rain_rejected():
    row = RainPair("A", date(2024, 1, 1), 1., 2., 3.)
    with pytest.raises(ValueError, match="duplicate"):
        evaluate([row, row])
    with pytest.raises(ValueError, match="finite"):
        RainPair("A", date(2024, 1, 1), float("nan"), 2., 3.)


def development(variation=None):
    reports = []
    for model, forecast in (("baseline", 70.), ("candidate", 55.)):
        report = {
            "schema": "climaprev-station-rain-pairs-v2", "model": model,
            "station": {"code": "A", "latitude": 0, "longitude": 0},
            "location": {"latitude": 0, "longitude": 0, "timezone": "UTC"},
            "source_sha256": "a"*64, "collected_at": "2023-12-31T18:00:00+00:00",
            "run_at": "2023-12-31T00:00:00+00:00",
            "rows": [{"date": "2024-01-01", "start_utc": "2024-01-01T00:00:00+00:00",
                      "end_utc": "2024-01-02T00:00:00+00:00", "collection_lead_days": 1,
                      "forecast_mm": forecast, "observed_mm": 50.,
                      "exclusions": [], "eligible_exploratory": True}],
        }
        reports.append(report)
    if variation:
        variation(reports)
    return evaluate_development_reports(
        reports, baseline="baseline", candidate="candidate",
        planned_dates={"A": [date(2024, 1, 1), date(2024, 1, 2)],
                       "B": [date(2024, 1, 1), date(2024, 1, 2)]},
        development_start=date(2024, 1, 1), development_end=date(2024, 1, 31),
        allowed_sources={"a"*64}, lead_days=1,
        criteria=RainCriteria(.05, 0., .9, 10, 2, 0., 0., .95),
        event_threshold_mm=50., block_lengths=[1, 7], repetitions=20, seed=42,
    )


def test_report_bridge_preserves_fully_missing_station_and_calendar_dates():
    result = development()
    assert result["comparison"]["common_cases"] == 1
    assert result["aggregate_sensitivity"][0]["diagnostic"]["common_coverage"] == .25
    assert result["station_sensitivity"]["B"][0]["evidence"]["common_pairs"] == 0
    assert len(result["aggregate_sensitivity"]) == 2
    assert result["promotion_allowed"] is False


@pytest.mark.parametrize("variation", [
    lambda reports: reports[1].update(source_sha256="b"*64),
    lambda reports: reports[1].update(collected_at="2023-12-31T19:00:00+00:00"),
    lambda reports: reports[1]["rows"][0].update(date="2025-01-01"),
    lambda reports: reports[1]["rows"][0].update(observed_mm=49.),
    lambda reports: reports[1]["rows"].append(dict(reports[1]["rows"][0])),
])
def test_report_bridge_rejects_source_timing_partition_and_pair_inconsistency(variation):
    with pytest.raises(ValueError):
        development(variation)


def test_report_bridge_honors_upstream_exclusions():
    result = development(lambda reports: reports[1]["rows"][0].update(exclusions=["gap"]))
    assert result["aggregate_sensitivity"][0]["evidence"]["common_pairs"] == 0
