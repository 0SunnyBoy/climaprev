"""Run from repository root with PYTHONPATH=src; diagnostic only, no target freeze."""
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

from climaprev.domain.models import DatePeriod
from climaprev.tools.inmet_observations import import_station
from climaprev.tools.observation_support import summarize_support

root = Path('docs/planejamento/reference-candidate-1/evidence')
source = root / 'sintese-observacional-2024-2026-10-19.json'
summary = json.loads(source.read_text(encoding='utf-8'))
manifest = root / 'expansao-observacional-2024-2026-10-19.json'
if hashlib.sha256(manifest.read_bytes()).hexdigest() != summary['manifest_sha256']:
    raise ValueError('execution manifest changed')
groups = []
for group in summary['groups']:
    code = group['station']
    raw = Path(f'.historical-reports/inmet/{code}-2024.csv').read_bytes()
    acquisition = json.loads((root / f'obtencao-inmet-{code.lower()}-2024-2026-10-19.json').read_text())
    if hashlib.sha256(raw).hexdigest() != acquisition['csv_sha256']:
        raise ValueError('station CSV changed')
    month = group['month']
    observations = import_station(raw, expected_station=code,
        period=DatePeriod(date(2024, month, 1), date(2024, month, 28)),
        timezone='America/Belem' if group['location']=='belem' else 'America/Sao_Paulo')
    dates = {variable: details['common_dates'] for variable, details in group['variables'].items()}
    result = summarize_support(observations, dates)
    groups.append({'location':group['location'], 'month':month, 'station':code,
                   'station_csv_sha256':acquisition['csv_sha256'], **result})
totals = {}
for event in groups[0]['events']:
    counts = Counter(low=0, moderate=0, high=0)
    for group in groups:
        counts.update(group['events'][event]['counts'])
    totals[event] = dict(counts)
report = {'schema':'climaprev-campaign-observation-support-v1', 'groups':groups,
          'totals_location_dates':totals,
          'input_summary_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'algorithm_sha256':hashlib.sha256(Path('src/climaprev/tools/observation_support.py').read_bytes()).hexdigest(),
          'scientific_approval':False, 'calibration_ready':False,
          'limitations':['Counts share calendar dates and must not be treated as independent events.',
                         'Source quality, measurement semantics and event sufficiency require review.',
                         'No classification target freeze, optimization or promotion was performed.']}
output = root / 'suporte-observacional-2024-2026-10-19.json'
with output.open('x',encoding='utf-8') as stream:
    json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps(totals))
