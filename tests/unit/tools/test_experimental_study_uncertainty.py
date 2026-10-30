"""Uncertainty preserves paired dates, gaps and undefined support."""

from datetime import UTC, datetime, timedelta

import pytest
from tests.support.experiment import variable_report

from climaprev.tools.experimental_comparison import compare_variable_models, paired_uncertainty


def comparison(errors: list[float], *, stations: int = 1) -> dict:
    reports = []
    for index, error in enumerate(errors):
        day = datetime(2030, 1, 1, tzinfo=UTC) + timedelta(days=index)
        slot = day - timedelta(days=1)
        for station in range(stations):
            for model, value in (("v1", error), ("candidate", 1)):
                report = variable_report(model, [value], [0])
                report["station"]["code"] = str(station)
                report["rows"][0].update(date=day.date().isoformat(), start_utc=day.isoformat(),
                                         end_utc=(day + timedelta(days=1)).isoformat())
                report.update(collection_slot=slot.isoformat(),
                              collection_deadline=(slot + timedelta(minutes=30)).isoformat(),
                              collected_at=(slot + timedelta(minutes=5)).isoformat())
                reports.append(report)
    return compare_variable_models(reports, "v1")


def uncertainty(value: dict, block: int = 2) -> dict:
    return paired_uncertainty(value, block_days=block, repetitions=100, seed=7, confidence=0.95)


def test_seeded_interval_and_point_estimate_are_reproducible() -> None:
    value = comparison([2, 4, 6, 8, 10, 12])
    result = uncertainty(value)
    score = result["groups"][0]["models"]["candidate"]
    assert score["estimate"] == pytest.approx(1 - 1 / 7)
    assert score["interval"][0] < score["interval"][1]
    assert result == uncertainty(value)
    assert result["promotion_allowed"] is False


def test_two_locations_on_same_date_are_resampled_together() -> None:
    one, two = uncertainty(comparison([2, 4, 6, 8])), uncertainty(comparison([2, 4, 6, 8], stations=2))
    assert one["groups"][0]["models"] == two["groups"][0]["models"]
    assert two["groups"][0]["models"]["candidate"]["calendar_dates"] == 4


def test_short_segments_have_no_interval_with_reason() -> None:
    score = uncertainty(comparison([2, 4]), block=7)["groups"][0]["models"]["candidate"]
    assert score["interval"] is None
    assert score["effective_block_days"] == [2]
    assert "short_calendar_segment" in score["interval_reasons"]


def test_perfect_baseline_discloses_undefined_replicates() -> None:
    score = uncertainty(comparison([0, 0]), block=1)["groups"][0]["models"]["candidate"]
    assert score["estimate"] is None
    assert score["undefined_repetitions"] == 100
    assert score["interval"] is None
    assert "undefined_repetitions" in score["interval_reasons"]


def test_degenerate_interval_does_not_claim_support() -> None:
    score = uncertainty(comparison([2, 2, 2]), block=1)["groups"][0]["models"]["candidate"]
    assert score["estimate"] == 0.5
    assert score["interval"] is None
    assert score["interval_reasons"] == ["degenerate_sampling_distribution"]


def test_empty_common_sample_is_reported_without_bootstrap() -> None:
    value = compare_variable_models([variable_report("v1", [None], [0]),
                                     variable_report("candidate", [1], [0])], "v1")
    score = uncertainty(value)["groups"][0]["models"]["candidate"]
    assert score["interval"] is None
    assert score["interval_reasons"] == ["no_common_cases"]
