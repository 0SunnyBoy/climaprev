from collections import Counter
from datetime import date, timedelta

import pytest

from climaprev.domain.bootstrap import bootstrap_dates


def test_resampling_keeps_date_clusters_and_calendar_windows_together():
    days = [date(2024, month, day) for month in (1, 4) for day in range(1, 11)]
    cases = [(day, location, lead) for day in days for location in range(3) for lead in (1, 3, 7)]

    def statistic(sample):
        counts = Counter(day for day, _, _ in sample)
        assert all(count % 9 == 0 for count in counts.values())
        assert sum(count for day, count in counts.items() if day.month == 1) == 90
        assert sum(count for day, count in counts.items() if day.month == 4) == 90
        return sum(day.day for day, _, _ in sample)/len(sample)

    result = bootstrap_dates(cases, day=lambda row: row[0], statistic=statistic,
                             block_days=3, repetitions=100, seed=42)
    assert result == bootstrap_dates(cases, day=lambda row: row[0], statistic=statistic,
                                    block_days=3, repetitions=100, seed=42)
    assert result.segment_lengths == (10, 10)
    assert result.interval is not None
    assert result.interval[0] < result.estimate < result.interval[1]


def test_short_segment_is_disclosed_and_does_not_produce_interval():
    cases = [date(2024, 1, 1)+timedelta(days=i) for i in range(3)]
    score = bootstrap_dates(cases, day=lambda day: day, statistic=lambda rows: 1., repetitions=10)
    assert score.effective_block_days == (3,)
    assert score.interval is None


def test_missing_event_support_is_not_converted_into_zero():
    cases = [date(2024, 1, 1)+timedelta(days=i) for i in range(10)]
    score = bootstrap_dates(cases, day=lambda day: day, statistic=lambda rows: None,
                            repetitions=10)
    assert score.estimate is None
    assert score.undefined_repetitions == 10
    assert score.interval is None


def test_nonfinite_statistic_is_rejected():
    with pytest.raises(ValueError, match='finite'):
        bootstrap_dates([date(2024, 1, 1)], day=lambda day: day,
                        statistic=lambda rows: float('nan'))


def test_degenerate_interval_is_inconclusive():
    cases = [date(2024, 1, 1)+timedelta(days=i) for i in range(14)]
    score = bootstrap_dates(cases, day=lambda day: day, statistic=lambda rows: 1.,
                            repetitions=10)
    assert score.estimate == 1
    assert score.interval is None
