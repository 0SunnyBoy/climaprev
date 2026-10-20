from datetime import date

import pytest
from tests.unit.tools.test_inmet_observations import station_csv

from climaprev.tools.reconcile_station import observation_day_rain, reconcile


def test_complete_month_and_distinct_boundary_conventions():
    raw = station_csv(first_hour=0, count=744+13)
    # Change the first endpoint: timestamp grouping includes it; intervals do not.
    raw = raw.replace(b';1,5;10;30;20;', b';9,5;10;30;20;', 1)
    result = reconcile(raw, station='A201', month=date(2025, 1, 1),
                       published_rain_mm=1116)
    windows = result['windows']
    assert windows[0]['rain_mm'] == 1124
    assert windows[1]['rain_mm'] == 1116
    assert windows[2]['endpoints_valid'] == 744
    assert windows[2]['difference_from_bulletin_mm'] == 0
    assert windows[0]['daily_windows'][0]['rain_mm'] == 44
    assert windows[1]['daily_windows'][0]['rain_mm'] == 36
    assert windows[2]['daily_windows'][-1]['valid_hours'] == 24
    assert not result['scientific_approval']
    assert not result['calibration_ready']


def test_incomplete_month_does_not_publish_partial_total():
    result = reconcile(station_csv(), station='A201', month=date(2025, 1, 1),
                       published_rain_mm=417)
    assert all(window['rain_mm'] is None for window in result['windows'])
    assert all(window['missing'] for window in result['windows'])
    assert result['windows'][2]['daily_windows'][0]['rain_mm'] == 36
    assert result['windows'][2]['daily_windows'][1]['rain_mm'] is None


@pytest.mark.parametrize('total', [-1, float('nan'), float('inf')])
def test_invalid_published_total(total):
    with pytest.raises(ValueError):
        reconcile(station_csv(), station='A201', month=date(2025, 1, 1),
                  published_rain_mm=total)


def test_observation_day_uses_previous_year_and_labels_by_end_date():
    previous = station_csv(day=date(2024,12,31),first_hour=13,count=11)
    current = station_csv(first_hour=0,count=744)
    result = observation_day_rain(current,previous_raw=previous,station='A201',
                                  month=date(2025,1,1))
    assert result['days'][0]['date'] == '2025-01-01'
    assert result['days'][0]['start_utc'] == '2024-12-31T12:00:00+00:00'
    assert result['days'][0]['rain_mm'] == 36
    assert result['monthly_rain_mm'] == 1116
    assert len(result['parents']) == 2


def test_observation_day_missing_boundary_is_not_a_valid_month():
    previous = station_csv(day=date(2024,12,31),first_hour=14,count=10)
    current = station_csv(first_hour=0,count=744)
    result = observation_day_rain(current,previous_raw=previous,station='A201',
                                  month=date(2025,1,1))
    assert result['monthly_rain_mm'] is None
    assert result['days'][0]['missing_endpoints_utc'] == ['2024-12-31T13:00:00+00:00']


def test_overlapping_annual_parents_are_rejected():
    raw = station_csv()
    with pytest.raises(ValueError,match='overlapping'):
        observation_day_rain(raw,previous_raw=raw,station='A201',month=date(2025,1,1))
