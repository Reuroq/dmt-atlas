"""Summarize completed observational evidence, without replaying a browser."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r3-timing'
OUT = HERE / (PREFIX + '-analysis.json')
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

build = read(PREFIX + '-build.json')
s = read(PREFIX + '-receipts.json')
assert s['protected_unchanged'] and s['source_unchanged']
assert digest(PREFIX + '-build.json') == s['build_sha256']
assert digest('run_centre_v33r3_timing.py') == s['runner_sha256']
for group in ['files', 'protected']:
    assert all(digest(n) == h for n, h in build[group].items())
for child, parent in [('trip-v33r3-timing.js', 'trip.js'), ('fractal-v33r3-timing.js', 'fractal.js')]:
    restored = re.sub(r'/\*TIMING_INSERT_(\d+)_BEGIN\*/.*?/\*TIMING_INSERT_\1_END\*/', '',
                      (HERE / child).read_text(), flags=re.S).encode()
    assert restored == (HERE / parent).read_bytes()

d = s['checkpoints'][-1]['diagnostics']
t = d['timing']
records = t['records']
assert t['dropped'] == s['stream_dropped'] == 0, 'Incomplete trace requires separate review'
assert all(a['ms'] <= b['ms'] for a, b in zip(records, records[1:]))
assert [e['sequence'] for e in records] == list(range(1, len(records) + 1))
events = Counter(e['event'] for e in records)
submissions = []
for e in records:
    if e['event'] != 'submission:begin':
        continue
    sid = e['submission']
    same = [r for r in records if r['submission'] == sid]
    end = next((r for r in same if r['event'] == 'submission:end'), None)
    retired = next((r for r in records if r['event'] == 'fence-retired' and
                    (r['fenceOwner'] or {}).get('submission') == sid), None)
    submissions.append({'id': sid, 'stage': e['stage'], 'animTime': e['animTime'],
        'beginMs': e['ms'], 'submissionMs': None if end is None else end['durationMs'],
        'passesMs': {r['event']: r['durationMs'] for r in same if r['event'].startswith('composite:') and r['event'].endswith(':end')},
        'flushMs': next((r['durationMs'] for r in same if r['event'] == 'flush:end'), None),
        'fenceRetiredMs': None if retired is None else retired['ms'],
        'fenceAgeAtRetirementMs': None if retired is None else retired['ageMs']})
pause = s['checkpoints'][0]['diagnostics']['timing']['exportMs']
after_pause = [e for e in records if e['ms'] >= pause]
polls = [e for e in after_pause if e['event'] == 'fence-poll:end']
decisions = [e for e in after_pause if e['event'] == 'render-decision']
owner = t['state']['fenceOwner']
analysis = {'diagnostic_only': True, 'receipt_sha256': digest(PREFIX + '-receipts.json'),
    'settle_passed': s['settle_passed'], 'failure_operation': s.get('failure', {}).get('operation'),
    'failure_seconds': s.get('failure', {}).get('operation_wall_seconds'),
    'errors': s['errors'], 'trace_records': len(records), 'trace_dropped': t['dropped'],
    'events': dict(events), 'raw_counts': t['counts'], 'submissions': submissions,
    'final': {k: v for k, v in d.items() if k != 'timing'}, 'timing_state': t['state'],
    'open_intervals': t['open'], 'exportMs': t['exportMs'],
    'pending_fence_age_ms': t['exportMs'] - owner['createdMs'] if owner else None,
    'after_pause': {'durationMs': t['exportMs'] - pause, 'sampled_poll_results': dict(Counter(e['result'] for e in polls)),
        'sampled_poll_max_ms': max((e['durationMs'] for e in polls), default=None),
        'decision_samples': len(decisions),
        'invalidated_decision_samples': sum(e['invalidated'] for e in decisions),
        'pending_fence_decision_samples': sum(e['fence'] for e in decisions),
        'submissions': sum(e['event'] == 'submission:begin' for e in after_pause),
        'invalidation_events': dict(Counter(e['event'] for e in after_pause if e['event'].startswith('invalidate:')))},
    'limits': s['limits']}
OUT.write_text(json.dumps(analysis, indent=2) + '\n')
print(json.dumps({k: analysis[k] for k in ['settle_passed', 'failure_seconds', 'trace_records', 'submissions',
      'timing_state', 'open_intervals', 'pending_fence_age_ms', 'after_pause']}, indent=2))
