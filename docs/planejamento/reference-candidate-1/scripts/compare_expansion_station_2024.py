"""Execute only the previously specified 2024 days 1–28; never fit a policy."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from climaprev.tools.compare_station import compare_station
from climaprev.tools.compare_station_variables import compare_variables
from climaprev.tools.historical_experiment import load_snapshot, canonical_json

root = Path('.historical-reports/candidate-1-expansion-2024')
destination = Path('.historical-reports/inmet/expansion-2024-2026-10-19')
destination.mkdir(parents=True, exist_ok=True)
rows = []
for location, station in [('belem', 'A201'), ('brasilia', 'A001'), ('porto-alegre', 'A801')]:
    raw = Path(f'.historical-reports/inmet/{station}-2024.csv').read_bytes()
    for month in (1, 4, 7, 10):
        for lead in (1, 3, 7):
            name = f'{location}-2024-{month:02d}-d{lead}'
            parent = load_snapshot(root / f'{name}.inputs.json')
            dataset = deepcopy(parent)
            dataset['configuration']['end'] = f'2024-{month:02d}-28'
            parent_hash = hashlib.sha256(canonical_json(parent).encode()).hexdigest()
            results = {}
            for kind, function in [('rain', compare_station), ('variables', compare_variables)]:
                report = function(dataset, raw, expected_station=station)
                report['evaluation_derivation'] = {
                    'parent_dataset_sha256': parent_hash,
                    'change': 'Evaluation end restricted to predefined day 28; day 29 kept as boundary.',
                    'scientific_approval': False,
                }
                path = destination / f'{name}-{kind}.json'
                data = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()
                if path.exists():
                    if path.read_bytes() != data:
                        raise ValueError(f'Existing report differs: {path}')
                else:
                    with path.open('xb') as stream:
                        stream.write(data)
                results[kind] = {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest()}
                if kind == 'rain':
                    results[kind]['paired_days'] = len(report['cases'])
                    results[kind]['excluded_days'] = len(report['excluded_days'])
                else:
                    results[kind]['paired_days_by_variable'] = {
                        key: len(value['cases']) for key, value in report['variables'].items()}
            rows.append({'location': location, 'station': station, 'month': month,
                         'lead_days': lead, 'reports': results})
manifest = {'schema': 'climaprev-station-expansion-execution-v1', 'rows': rows,
            'scientific_approval': False, 'calibration_ready': False,
            'execution_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
output = Path('docs/planejamento/reference-candidate-1/evidence/expansao-observacional-2024-2026-10-19.json')
with output.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, indent=2, ensure_ascii=False)
print(json.dumps({'jobs': len(rows), 'manifest': str(output)}))
