from copy import deepcopy

from tests.unit.tools.test_audit_historical import sample
from tests.unit.tools.test_inmet_observations import station_csv

from climaprev.tools.compare_hourly_rain import compare_hourly_rain
from climaprev.tools.station_baseline import event_level


def test_maximum_uses_preceding_intervals_and_next_midnight_not_daily_sum():
    data = sample()
    data['forecast']['hourly']['precipitation_previous_day1'][0] = 999
    original = deepcopy(data)
    result = compare_hourly_rain(data,station_csv(),expected_station='A201')
    assert result['cases'] == [{'date':'2025-01-01','station':1.5,'forecast':24,'observed':24}]
    assert result['paired_days'] == 1
    assert data == original
    assert event_level('hourly_rain', 20.) == 'moderate'
    assert event_level('hourly_rain', 30.) == 'high'


def test_missing_boundary_cannot_publish_a_partial_maximum():
    result = compare_hourly_rain(sample(boundary=False),station_csv(),expected_station='A201')
    assert result['cases'] == []
    assert result['metrics']['forecast']['mae'] is None
    assert result['excluded_days'][0]['incomplete_sources'] == ['forecast','observed']


def test_missing_station_hour_excludes_both_model_comparisons():
    result = compare_hourly_rain(sample(),station_csv(missing=True),expected_station='A201')
    assert result['cases'] == []
    assert result['excluded_days'][0]['incomplete_sources'] == ['station']


def test_missing_model_hour_does_not_retain_an_otherwise_large_maximum():
    data = sample()
    data['forecast']['hourly']['precipitation_previous_day1'][12] = None
    result = compare_hourly_rain(data,station_csv(),expected_station='A201')
    assert result['cases'] == []
    assert result['excluded_days'][0]['incomplete_sources'] == ['forecast']
