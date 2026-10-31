"""Diagnostic R0 on existing eligible dates; run from root with PYTHONPATH=src."""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from climaprev.tools.station_baseline import baseline_event

root = Path('docs/planejamento/reference-candidate-1/evidence')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path,
                    default=root/'baseline-observacional-2024-final-2026-10-19.json')
args = parser.parse_args()
manifest_path = root/'expansao-observacional-2024-2026-10-19.json'
summary_path = root/'sintese-observacional-2024-2026-10-19.json'
manifest = json.loads(manifest_path.read_text())
summary = json.loads(summary_path.read_text())
if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != summary['manifest_sha256']:
    raise ValueError('manifest changed')
groups = {(g['location'],g['month']):g for g in summary['groups']}
pooled = defaultdict(list)
strata = []
events = {'daily_rain':'rain_mm','gust':'gust_kmh',
          'heat':'temperature_max_c','cold':'temperature_min_c'}
for job in manifest['rows']:
    group = groups[(job['location'],job['month'])]
    reports = {}
    for kind, descriptor in job['reports'].items():
        path = Path(descriptor['path'].replace('\\','/'))
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != descriptor['sha256']:
            raise ValueError('comparison report changed')
        reports[kind] = json.loads(raw)
    for event, variable in events.items():
        eligible = set(group['variables'][variable]['common_dates'])
        report = reports['rain'] if event=='daily_rain' else reports['variables']['variables'][variable]
        cases = [{**row, 'location':job['location']} for row in report['cases']
                 if row['date'] in eligible]
        if {row['date'] for row in cases} != eligible:
            raise ValueError('eligible dates missing from comparison')
        result = baseline_event(event,cases)
        strata.append({'location':job['location'],'month':job['month'],
                       'lead_days':job['lead_days'],**result})
        pooled[(event,job['lead_days'])].extend(cases)
aggregates = []
for (event,lead), cases in sorted(pooled.items()):
    dates = sorted({date.fromisoformat(row['date']) for row in cases})
    segments = []
    for day in dates:
        if not segments or day != segments[-1][-1]+timedelta(days=1):
            segments.append([])
        segments[-1].append(day)
    aggregates.append({'lead_days':lead,**baseline_event(event,cases),
                       'unique_calendar_dates':len(dates),
                       'calendar_segment_days':[len(segment) for segment in segments],
                       'primary_block_days':7,
                       'all_segments_support_primary_block':all(len(s)>=7 for s in segments)})
report = {'schema':'climaprev-station-baseline-diagnostic-v1','aggregates':aggregates,
          'strata':strata,'source_legend':{'forecast':'GFS','observed':'ERA5 control','station':'INMET'},
          'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'summary_sha256':hashlib.sha256(summary_path.read_bytes()).hexdigest(),
          'algorithm_sha256':hashlib.sha256(Path('src/climaprev/tools/station_baseline.py').read_bytes()).hexdigest(),
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'omitted_events':{'hourly_rain':'Existing comparison reports lack paired model hourly maxima; no surrogate substituted.'},
          'scientific_approval':False,'calibration_ready':False,'targets_frozen':False,
          'limitations':['Descriptive post-collection R0 diagnostics, not a prespecified confirmatory trial.',
                         'No confidence intervals computed, no primary metric chosen from outcomes.',
                         'Gust/temperature sampling differs across station and models.',
                         'Counts share dates, locations and horizons; not independent sample sizes.']}
output = args.output
with output.open('x',encoding='utf-8') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False)
for row in aggregates:
    high=row['scores']['forecast']['detection'][1]
    print(row['event'],row['lead_days'],row['cases'],
          {key:high[key] for key in ('hits','misses','false_alarms','recall')})
