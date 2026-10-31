import hashlib
import json
from pathlib import Path

from climaprev.domain.verification import numerical_pairs
from dataclasses import asdict

manifest_path = Path('docs/planejamento/reference-candidate-1/evidence/expansao-observacional-2024-2026-10-19.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
summary = {'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
           'groups': [], 'scientific_approval': False, 'calibration_ready': False}
for city in ('belem', 'brasilia', 'porto-alegre'):
    for month in (1, 4, 7, 10):
        rows = [row for row in manifest['rows'] if row['location']==city and row['month']==month]
        reports = {}
        for row in rows:
            reports[row['lead_days']] = {}
            for kind, descriptor in row['reports'].items():
                raw = Path(descriptor['path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != descriptor['sha256']:
                    raise ValueError('report hash mismatch')
                report = json.loads(raw)
                reports[row['lead_days']][kind] = report
        group = {'location': city, 'month': month, 'station': rows[0]['station'],
                 'station_metadata': reports[1]['rain']['station'],
                 'station_to_grid_distance_km': reports[1]['variables']['station_to_grid_distance_km'],
                 'variables': {}}
        for variable in ('rain_mm', 'gust_kmh', 'temperature_max_c', 'temperature_min_c'):
            cases = {}
            for lead in (1,3,7):
                report = reports[lead]['rain'] if variable=='rain_mm' else reports[lead]['variables']['variables'][variable]
                cases[lead] = {row['date']:row for row in report['cases']}
            common = sorted(set(cases[1]) & set(cases[3]) & set(cases[7]))
            group['variables'][variable] = {'common_dates': common, 'paired_days':len(common),
                'metrics': {str(lead):{source:asdict(numerical_pairs([
                    (cases[lead][day]['station'], cases[lead][day][source]) for day in common]))
                    for source in ('forecast','observed')} for lead in (1,3,7)}}
        summary['groups'].append(group)
summary['unique_location_dates_by_variable'] = {
    variable: sum(group['variables'][variable]['paired_days'] for group in summary['groups'])
    for variable in ('rain_mm', 'gust_kmh', 'temperature_max_c', 'temperature_min_c')}
output=Path('docs/planejamento/reference-candidate-1/evidence/sintese-observacional-2024-2026-10-19.json')
with output.open('x',encoding='utf-8') as stream:
    json.dump(summary, stream, ensure_ascii=False, indent=2, allow_nan=False)
print(json.dumps(summary['unique_location_dates_by_variable']))
for group in summary['groups']:
    if group['month']==1:
        print(group['location'],group['station_metadata'],group['station_to_grid_distance_km'])
