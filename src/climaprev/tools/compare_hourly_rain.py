"""Compare daily maxima of aligned complete hourly rain intervals, without fitting."""

import hashlib
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from climaprev.domain.models import DatePeriod
from climaprev.domain.verification import numerical_pairs
from climaprev.tools.audit_historical import audit_snapshot
from climaprev.tools.historical_experiment import canonical_json
from climaprev.tools.inmet_observations import import_station


def compare_hourly_rain(dataset: dict[str, Any], raw: bytes, *,
                        expected_station: str) -> dict[str, Any]:
    config = dataset['configuration']
    audit = audit_snapshot(dataset)
    station = import_station(raw, expected_station=expected_station,
        period=DatePeriod(date.fromisoformat(config['start']), date.fromisoformat(config['end'])),
        timezone=config['timezone'])
    sources = {name:{row['date']:row for row in source['days']}
               for name, source in audit['sources'].items()}
    cases, excluded = [], []
    for row in station['days']:
        when = row['date']
        field = row['fields']['rain_mm']
        values = {'station':field['max_hourly_mm'],
                  **{name:days[when]['civil_preceding_hour_max_mm']
                     for name, days in sources.items()}}
        missing = [name for name,value in values.items() if value is None]
        if missing:
            excluded.append({'date':when, 'incomplete_sources':missing,
                             'missing_endpoints_utc':{
                                 'station':field['missing_endpoints_utc'],
                                 **{name:days[when]['missing_interval_endpoints']
                                    for name,days in sources.items()}}})
        else:
            cases.append({'date':when, **values})
    return {'schema':'climaprev-station-hourly-rain-max-v1',
            'convention':station['convention'], 'configuration':config,
            'meaning':'Maximum hourly accumulation within the complete civil day, '
                      'not a daily sum, instantaneous rate or rolling sub-hour extreme.',
            'station':station['station'], 'station_source_sha256':station['source_sha256'],
            'snapshot_dataset_sha256':hashlib.sha256(canonical_json(dataset).encode()).hexdigest(),
            'source_sha256':{str(path.name):hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (Path(__file__),Path(__file__).with_name('audit_historical.py'),
                                          Path(__file__).with_name('inmet_observations.py'))},
            'cases':cases, 'paired_days':len(cases), 'excluded_days':excluded,
            'unit':'mm',
            'metrics':{name:asdict(numerical_pairs([(row['station'],row[name]) for row in cases]))
                       for name in ('forecast','observed')},
            'scientific_approval':False, 'calibration_ready':False,
            'limitations':['Grid maxima and station maxima have different spatial representativeness.',
                           'Complete hours are required even when the available maximum is large.',
                           'No fitting, target freeze or promotion; sources retain previous semantics.']}
