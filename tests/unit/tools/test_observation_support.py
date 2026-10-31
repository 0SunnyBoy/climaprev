from copy import deepcopy
from datetime import date

import pytest
from tests.unit.tools.test_inmet_observations import station_csv

from climaprev.domain.models import DatePeriod
from climaprev.tools.inmet_observations import import_station
from climaprev.tools.observation_support import summarize_support


def inputs():
    observations = import_station(station_csv(), expected_station='A201',
                                  period=DatePeriod(date(2025, 1, 1), date(2025, 1, 1)),
                                  timezone='America/Belem')
    dates = {key: ['2025-01-01'] for key in observations['days'][0]['fields']}
    return observations, dates


def test_v1_boundaries_include_exact_high_values_and_reverse_cold_direction():
    observations, dates = inputs()
    fields = observations['days'][0]['fields']
    for variable, value in [('rain_mm', 50), ('gust_kmh', 61),
                            ('temperature_max_c', 40), ('temperature_min_c', 0)]:
        fields[variable]['value'] = value
    fields['rain_mm']['max_hourly_mm'] = 30
    result = summarize_support(observations, dates)
    assert all(event['counts'] == {'low': 0, 'moderate': 0, 'high': 1}
               for event in result['events'].values())
    assert not result['scientific_approval']


def test_no_high_support_does_not_approve_detection_or_sufficiency():
    observations, dates = inputs()
    result = summarize_support(observations, dates)
    assert all(not event['high_support_present'] for event in result['events'].values())
    assert all(not event['sample_sufficiency_approved'] for event in result['events'].values())


def test_duplicate_dates_cannot_inflate_support():
    observations, dates = inputs()
    dates['rain_mm'] *= 2
    with pytest.raises(ValueError, match='duplicate'):
        summarize_support(observations, dates)


@pytest.mark.parametrize('invalid', [None, float('nan'), True])
def test_incomplete_or_nonfinite_values_are_not_low_risk(invalid):
    observations, dates = inputs()
    original = deepcopy(observations)
    observations['days'][0]['fields']['gust_kmh']['value'] = invalid
    with pytest.raises(ValueError, match='invalid'):
        summarize_support(observations, dates)
    assert original['days'][0]['fields']['gust_kmh']['value'] == 36
