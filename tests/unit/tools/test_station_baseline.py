import pytest

from climaprev.tools.station_baseline import baseline_event, event_level


def test_baseline_reports_high_misses_false_alarms_and_direction():
    rows = [{'location': 'synthetic', 'date': str(i), 'station': station,
             'forecast': forecast, 'observed': station}
            for i, (station, forecast) in enumerate([(50., 0.), (0., 50.), (30., 30.)])]
    result = baseline_event('daily_rain', rows)
    score = result['scores']['forecast']
    assert score['confusion_matrix'] == ((0, 0, 1), (0, 1, 0), (1, 0, 0))
    assert score['detection'][1]['misses'] == 1
    assert score['detection'][1]['false_alarms'] == 1
    assert result['scores']['observed']['accuracy'] == 1
    assert not result['scientific_approval']


def test_no_high_support_keeps_recall_undefined():
    result = baseline_event('heat', [{'location':'x','date':'one','station':25.,
                                      'forecast':26.,'observed':25.}])
    assert result['scores']['forecast']['detection'][1]['recall'] is None
    assert event_level('cold', 0.) == 'high'
    assert event_level('cold', 5.) == 'moderate'


def test_duplicate_cases_cannot_inflate_scores():
    row = {'location':'x','date':'one','station':0.,'forecast':0.,'observed':0.}
    with pytest.raises(ValueError, match='duplicate'):
        baseline_event('daily_rain', [row, row])


@pytest.mark.parametrize('value', [float('nan'), float('inf'), True])
def test_nonfinite_values_cannot_be_low_risk(value):
    with pytest.raises(ValueError, match='finite'):
        event_level('daily_rain', value)
