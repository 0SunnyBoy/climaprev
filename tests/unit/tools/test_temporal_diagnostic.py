from datetime import UTC, date, datetime, timedelta

from climaprev.tools.temporal_diagnostic import daily_profile, nearest_peak_lag


def test_preceding_hours_include_next_midnight_and_keep_all_ties():
    start = datetime(2024, 4, 10, 3, tzinfo=UTC)
    series = {start + timedelta(hours=index): 1.0 for index in range(25)}
    series[start] = 99
    series[start + timedelta(hours=24)] = 7
    result = daily_profile(series, date(2024, 4, 10), "America/Belem", preceding=True)
    assert len(result["samples"]) == 24
    assert result["peak"] == 7
    assert result["peak_utc"] == ["2024-04-11T03:00:00+00:00"]
    instant = daily_profile(series, date(2024, 4, 10), "America/Belem", preceding=False)
    assert instant["peak"] == 99
    assert nearest_peak_lag(result, instant) == 24


def test_missing_hour_is_not_replaced_by_zero_and_no_peak_is_reported():
    result = daily_profile({}, date(2024, 1, 1), "UTC", preceding=True)
    assert not result["complete"]
    assert result["peak"] is None
    assert nearest_peak_lag(result, result) is None


def test_tied_peaks_are_preserved_and_nearest_lag_is_explicit():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    series = {start + timedelta(hours=index): 1.0 for index in range(24)}
    result = daily_profile(series, start.date(), "UTC", preceding=False, minimum=True)
    assert len(result["peak_utc"]) == 24
    assert nearest_peak_lag(result, result) == 0
