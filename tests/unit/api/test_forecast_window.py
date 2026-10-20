from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from climaprev.api.errors import ApplicationError
from climaprev.api.forecast_window import forecast_window, validate_public_period


@pytest.mark.parametrize("offset,local_day,hour,utc_day", [
    (-3, 20, 23, 21), (14, 21, 0, 20), (-12, 20, 23, 21), (0, 20, 0, 20),
])
def test_eligibility_uses_utc_instead_of_host_or_location_date(offset, local_day, hour, utc_day):
    clock = datetime(2026, 10, local_day, hour, tzinfo=timezone(timedelta(hours=offset)))
    first, last = forecast_window(clock)
    assert first == date(2026, 10, utc_day)
    assert last == first + timedelta(days=6)


def test_clock_must_be_aware_and_boundaries_include_year_transition():
    with pytest.raises(ValueError):
        forecast_window(datetime(2026, 1, 1))
    assert forecast_window(datetime(2026, 12, 31, tzinfo=UTC)) == (date(2026, 12, 31), date(2027, 1, 6))
    assert forecast_window(datetime(2026, 12, 31, tzinfo=UTC), horizon_days=14) == (
        date(2026, 12, 31), date(2027, 1, 13))


@pytest.mark.parametrize("start,end,allowed", [(0, 0, True), (0, 6, True), (6, 6, True),
                                             (-1, 0, False), (0, 7, False), (7, 7, False)])
def test_public_window_blocks_past_and_distant_dates(monkeypatch, start, end, allowed):
    today = date(2026, 10, 20)
    monkeypatch.setattr("climaprev.api.forecast_window.utc_today", lambda: today)
    if allowed:
        validate_public_period(today + timedelta(days=start), today + timedelta(days=end))
    else:
        with pytest.raises(ApplicationError) as error:
            validate_public_period(today + timedelta(days=start), today + timedelta(days=end))
        assert error.value.code == "INVALID_PERIOD"
