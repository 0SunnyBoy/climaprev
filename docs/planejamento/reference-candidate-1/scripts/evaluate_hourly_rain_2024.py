"""Pair hourly maxima from preserved parents and append a diagnostic baseline event."""
import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

from climaprev.tools.compare_hourly_rain import compare_hourly_rain
from climaprev.tools.historical_experiment import canonical_json, load_snapshot
from climaprev.tools.station_baseline import baseline_event

root=Path('docs/planejamento/reference-candidate-1/evidence')
parent_path=root/'baseline-observacional-2024-final-2026-10-19.json'
parent=json.loads(parent_path.read_text())
summary_path=root/'sintese-observacional-2024-2026-10-19.json'
if hashlib.sha256(summary_path.read_bytes()).hexdigest()!=parent['summary_sha256']:
    raise ValueError('summary changed')
summary=json.loads(summary_path.read_text())
manifest_path=root/'expansao-observacional-2024-2026-10-19.json'
if hashlib.sha256(manifest_path.read_bytes()).hexdigest()!=summary['manifest_sha256']:
    raise ValueError('manifest changed')
manifest=json.loads(manifest_path.read_text())
campaign_path=root/'campanha-2024-etapas-1-a-5-reexecucao.json'
campaign=json.loads(campaign_path.read_text())
snapshot_root=Path('.historical-reports/candidate-1-expansion-2024')
outputs=Path('.historical-reports/inmet/hourly-rain-2024-2026-10-19')
outputs.mkdir(parents=True,exist_ok=True)
pooled=defaultdict(list)
strata=[]
reports=[]
for group in summary['groups']:
    station=group['station']
    raw=Path(f'.historical-reports/inmet/{station}-2024.csv').read_bytes()
    acquisition=json.loads((root/f'obtencao-inmet-{station.lower()}-2024-2026-10-19.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=acquisition['csv_sha256']:
        raise ValueError('station CSV changed')
    eligible=set(group['variables']['rain_mm']['common_dates'])
    for lead in (1,3,7):
        name=f"{group['location']}-2024-{group['month']:02d}-d{lead}"
        snapshot=load_snapshot(snapshot_root/f'{name}.inputs.json')
        snapshot_hash=hashlib.sha256(canonical_json(snapshot).encode()).hexdigest()
        if snapshot_hash!=campaign['parent_snapshots'][name]:
            raise ValueError('snapshot differs from campaign parent')
        dataset=deepcopy(snapshot)
        dataset['configuration']['end']=f"2024-{group['month']:02d}-28"
        result=compare_hourly_rain(dataset,raw,expected_station=station)
        result['parent_snapshot_sha256']=snapshot_hash
        path=outputs/f'{name}.json'
        data=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
        with path.open('xb') as stream:
            stream.write(data)
        reports.append({'path':path.as_posix(),'sha256':hashlib.sha256(data).hexdigest()})
        cases=[{**row,'location':group['location']} for row in result['cases'] if row['date'] in eligible]
        if {row['date'] for row in cases}!=eligible:
            raise ValueError('hourly coverage differs from frozen paired rain dates')
        strata.append({'location':group['location'],'month':group['month'],'lead_days':lead,
                       **baseline_event('hourly_rain',cases)})
        pooled[lead].extend(cases)
aggregates=[]
for lead,cases in sorted(pooled.items()):
    dates=sorted({date.fromisoformat(row['date']) for row in cases})
    segments=[]
    for day in dates:
        if not segments or day!=segments[-1][-1]+timedelta(days=1): segments.append([])
        segments[-1].append(day)
    aggregates.append({'lead_days':lead,**baseline_event('hourly_rain',cases),
                       'unique_calendar_dates':len(dates),
                       'calendar_segment_days':[len(segment) for segment in segments],
                       'primary_block_days':7,
                       'all_segments_support_primary_block':all(len(s)>=7 for s in segments)})
result=deepcopy(parent)
result.update(schema='climaprev-station-baseline-all-events-v2',
              aggregates=parent['aggregates']+aggregates,strata=parent['strata']+strata,
              omitted_events={},hourly_reports=reports,
              parent_baseline_sha256=hashlib.sha256(parent_path.read_bytes()).hexdigest(),
              campaign_sha256=hashlib.sha256(campaign_path.read_bytes()).hexdigest(),
              hourly_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              hourly_baseline_algorithm_sha256=hashlib.sha256(Path('src/climaprev/tools/station_baseline.py').read_bytes()).hexdigest())
result['limitations'].append('Previous four-event diagnostic retained as parent; hourly event adds daily maxima of aligned hourly accumulations, not rolling sub-hour extremes.')
with (root/'baseline-cinco-eventos-2024-2026-10-19.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False)
for row in aggregates:
    print(row['lead_days'],row['cases'],row['scores']['forecast']['detection'][1])
