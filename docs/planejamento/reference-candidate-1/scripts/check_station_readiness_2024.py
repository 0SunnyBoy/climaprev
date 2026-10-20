"""Report technical blockers; never choose or approve scientific acceptance criteria."""
import argparse
import hashlib
import json
from pathlib import Path

root = Path('docs/planejamento/reference-candidate-1/evidence')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline', type=Path,
                    default=root/'baseline-cinco-eventos-2024-2026-10-19.json')
parser.add_argument('--output', type=Path,
                    default=root/'preflight-cinco-eventos-2024-2026-10-19.json')
args=parser.parse_args()
baseline_path = args.baseline
protocol_path = root.parent/'protocolo-etapas-1-a-5.json'
baseline = json.loads(baseline_path.read_text())
protocol = json.loads(protocol_path.read_text())
block_days = protocol['uncertainty_plan']['primary_block_days']
events = []
for row in baseline['aggregates']:
    high = row['scores']['forecast']['detection'][1]
    support = high['hits']+high['misses']
    events.append({'event':row['event'],'lead_days':row['lead_days'],
                   'high_support':support,
                   'support_state':'absent' if not support else 'present_sufficiency_not_approved',
                   'calendar_segments':row['calendar_segment_days'],
                   'shorter_than_primary_block':[n for n in row['calendar_segment_days'] if n<block_days],
                   'primary_block_days':block_days,
                   'confidence_interval_status':'not_computed',
                   'reason':'Primary-metric approval and adequate segments required; no post-hoc exclusions.'})
report = {'schema':'climaprev-station-readiness-proposal-v1',
          'status':'technical_preflight_not_scientific_approval', 'events':events,
          'unresolved_acceptance':protocol['future_acceptance_gates'],
          'baseline_sha256':hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
          'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
          'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'candidate_fitting_authorized':False,'scientific_approval':False,
          'automatic_promotion_allowed':False}
with args.output.open('x',encoding='utf-8') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False)
print('Preflight recorded; acceptance criteria remain unresolved, fitting disabled.')
