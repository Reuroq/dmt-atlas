"""Close completed numerical evidence and an interrupted cost attempt; no replay."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r5-numerical-hold-integrity.json'
assert not OUT.exists()

def read(name):
    return json.loads((HERE / name).read_text())

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

implementation = read('centre-v33r5-implementation.json')
assert implementation['static_passed']
for group in ['files', 'protected', 'display']:
    verify(implementation[group])
proof = read('centre-v33r5-identifier-proof.json')
bounds = read('centre-v33r5-bounds-check.json')
gpu = read('numeric-candidate-v33r5-check.json')
roots = read('centre-v33r5-first-root-check.json')
raw_cost = read('centre-v33r5-cost-raw.json')
groups = [implementation['files'], proof['source_hashes'], bounds['source_hashes'],
          gpu['files'], roots['source_hashes'], raw_cost['source_hashes']]
for group in groups:
    verify(group)
assert proof['passed'] and bounds['passed'] and bounds['inherited']
assert bounds['new_bounds_runs'] == 0
assert bounds['protected_before'] == bounds['protected_after'] == implementation['protected']
assert gpu['passed'] and not gpu['errors'] and len(gpu['cases']) == 48
assert gpu['rays'] == 75996 and gpu['reference_rays'] == roots['reference_rays'] == 720
assert roots['passed'] and roots['unresolved_intervals'] == 0
assert sum(c['misses'] for c in gpu['cases']) == 0
assert all(c['count_invariants_passed'] for c in gpu['cases'])
assert sum(len(c['composite_fd_discrepancies']) for c in gpu['cases']) == 0
assert raw_cost['started'] and raw_cost['pairs'] == []
assert (HERE / 'measure-cost-v33r5-once.log').stat().st_size == 0
for name in ['centre-v33r5-cost-review.json', 'centre-v33r5-integrity.json',
             'centre-v33r5-gpu-failure.json']:
    assert not (HERE / name).exists(), name
assert not list(HERE.glob('diagnostic-centre-v33r5*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'render_centre_v33r5.py').read_bytes().replace(b'v33r5', b'v33r3') == (HERE / 'render_centre_v33r3.py').read_bytes()
build = read('build-centre-v33r5.log')
assert build['static_passed'] and build['renamed_tokens'] == 19
processes = subprocess.run(['ps', '-eo', 'pid,ppid,stat,etime,args'],
                          check=True, capture_output=True, text=True).stdout.splitlines()
active = [line for line in processes if any(token.endswith('/measure_centre_v33r5_cost.py')
          or token == 'measure_centre_v33r5_cost.py' for token in line.split()[4:])]
assert not active, active

metrics = {'gpu_cases': 48, 'gpu_rays': 75996, 'fixed_grid_roots': 720,
           'interval_roots': 720, 'misses': 0, 'browser_errors': 0,
           'unresolved_intervals': 0, 'composite_fd_discrepancies': 0,
           'max_fixed_grid_difference': gpu['max_reference_difference'],
           'max_interval_difference': roots['max_reference_difference'],
           'required_cost_pairs': 12, 'saved_cost_pairs': 0}
observation = {'cost_status': 'INCOMPLETE', 'started_receipt_present': True,
               'saved_pairs': 0, 'cost_log_bytes': 0, 'cost_review_present': False,
               'process_check': 'ps -eo pid,ppid,stat,etime,args; exact script argument match',
               'matching_cost_processes': active, 'exit_code': None,
               'session_observation': 'write_stdin reported Unknown process id 50621 after new harness input',
               'cause': 'Undetermined; no termination or exit receipt was captured',
               'interpretation': 'Not a measured slowdown, numerical failure, or compile failure',
               'action': 'Hold capture. Preserve partial attempt; no replay or promotion.'}
review_name = 'centre-v33r5-numerical-hold-review.md'
observation_name = 'centre-v33r5-cost-interruption.json'
archive_name = 'NOTES-before-centre-v33r5-numerical-hold.md'
for name in [review_name, observation_name, archive_name]:
    assert not (HERE / name).exists(), name
review = '''# v33r5 numerical PASS; cost INCOMPLETE — capture held

The GPU probe and independent first-root audit each ran once, exit 0, with
separate saved logs. All 48 cases / 75,996 rays and 720 fixed-grid plus 720
interval-audited roots passed. There were no misses, recorded browser errors,
unresolved intervals or composite finite-difference discrepancies. Worst root
depth difference was about 0.000620. Bounds inherit the completed v33r4 sampled
72,000 leaf/reach and 12,000 clearance checks through exact identifier/scalar
equivalence; no bounds rerun. This is sampled numerical evidence, not universal
convergence, directed-rounding proof, performance acceptance or visual realism.

The prepared balanced 12-pair cost experiment was invoked once. Its started
receipt persists with zero complete pairs; its log is empty and no cost review
exists. After new harness input, the execution session was unavailable and a
process-list check found no cost-runner process. No exit status or termination
cause was captured. A first arm may have run; no arm result is persisted. This
does not establish shader failure or a measured cost regression. Hits/counters,
prefix work and total/median paired wall costs cannot be compared. Cost gate
is unvalidated and capture remains blocked. Do not replay this partial attempt.

The hold integrity receipt binds numerical/implementation evidence, the build
log (previously unbound), all three run logs, cost-started receipt, observation,
this review, prior notes and protected files. It is NOT the passing
centre-v33r5-integrity.json required by the renderer. The prepared renderer is
byte-identical to v33r3 after version substitution. No capture, PNG, inspection,
promotion, prewarm or frame-pump change occurred. latest.png still represents
the labelled REJECTED GAME v32 deep-motion diagnostic. Live files, source/grade
ledgers and stale default Chrysanthemum evidence remain unchanged.

Next bounded phase: offline analysis for a substantive new isolated shader
optimization, and a cost-runner design with per-arm lifecycle/failure receipts
outside timed boundaries. Preserve all v33r5 evidence; do not merely rename and
replay its one-shot cost experiment. Any new candidate must preserve scalar,
material, movement and marcher contracts and independently earn the unchanged
numerical and 12-pair balanced cost gates before original HIGH/90s capture.
All 19 realism grades, remaining source/coverage gates, route and full acceptance
remain unfinished. No completion marker.
'''
old_notes = (HERE / 'NOTES.md').read_bytes()
notes = old_notes.decode('utf-8-sig')
notes = notes.replace('# Active: REDIRECT4 — v33r5 implementation CLOSED; numerical gates next',
                      '# Active: REDIRECT4 — v33r5 numerical PASS; cost INCOMPLETE, capture held', 1)
assert '## Exact next bounded work' in notes
notes = notes.split('## Exact next bounded work')[0] + '''## v33r5 numerical phase CLOSED — numerical PASS; cost INCOMPLETE
- probe_numeric_candidate_v33r5.py ONCE exit0:48cases/75996rays/720fixed-grid roots PASS;zero misses/browser errors/composite-FD discrepancies. Worst root difference .000619823. Saved probe-numeric-v33r5-once.log.
- audit_centre_v33r5_first_roots.py ONCE exit0:720interval roots PASS,zero unresolved;worst difference .000619797. Saved audit-first-roots-v33r5-once.log. Bounds inherited,not rerun.
- measure_centre_v33r5_cost.py invoked ONCE;started raw receipt exists,0/12complete pairs,empty measure-cost-v33r5-once.log,no cost review. Execution session unavailable after harness input;ps found no runner. Exit/cause UNKNOWN,no saved arm results. Not evidence of compile failure or slowdown;cost comparisons unvalidated. Preserve partial attempt,no replay.
- close_centre_v33r5_numerical_hold.py binds implementation/numerical/partial-cost evidence and all logs,including previously unbound build-centre-v33r5.log. Hold receipt centre-v33r5-numerical-hold-integrity.json is NOT passing centre-v33r5-integrity.json;capture blocked. Renderer version-only equality verified;never run.
- Zero new PNG/inspection/promotion;latest still labelled REJECTED GAME v32. Live/defaults/ledgers unchanged. README/status current;NOTES once,BOM preserved,prior notes archived verbatim.

## Exact next bounded work
Offline analyze a substantive new isolated shader optimization and design per-arm lifecycle/failure receipts outside cost timing boundaries. Preserve all v33r5 evidence;do not rename/replay its partial one-shot experiment or rerun its completed numerical/bounds checks. No measured cost result exists,so do not infer slowdown,compile failure or alter the frame pump. Any new candidate requires exact scalar/material/march preservation and unchanged numerical+balanced12-pair cost gates;only passing closure permits version-only original1200x800 HIGH/90000ms capture. No prewarm,relaxed gates or promotion.

All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.
'''
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r5 identifier-only correction is prepared**')
end = readme.index('No frame-pump change or limit relaxation.', start)
readme = readme[:start] + '''Isolated **v33r5 numerical gates PASS; cost is INCOMPLETE**. Actual GLSL
48 cases / 75,996 rays and 720 fixed-grid plus 720 interval roots pass with no
misses or unresolved intervals. Bounds inherited, not rerun. The one-shot cost
attempt stopped with a started receipt but 0/12 saved pairs and no exit receipt;
cause unknown, no slowdown claim. Original HIGH/90s capture remains blocked.
No new PNG or promotion. See [numerical and cost hold](centre-v33r5-numerical-hold-review.md).
''' + readme[end:]
status = ('Isolated v33r5 numerical CLOSED: GLSL48cases/75996rays/720fixed+720interval roots PASS; '
          'bounds inherited. Cost attempt INCOMPLETE:0/12saved pairs,process gone,exit/cause unknown; '
          'no replay,capture blocked,no passing capture integrity. Zero new PNGs/inspections/promotion. '
          'latest.png remains labelled REJECTED GAME v32 deep-motion;live v25/trip18/HUD/defaults/ledgers unchanged; '
          'all19/source/coverage/route/full unfinished.\n')
(HERE / archive_name).write_bytes(old_notes)
(HERE / review_name).write_text(review)
(HERE / observation_name).write_text(json.dumps(observation, indent=2) + '\n')
readme_path.write_text(readme)
(HERE / 'status.txt').write_text(status)
(HERE / 'NOTES.md').write_text(notes, encoding='utf-8-sig')
verify(implementation['protected'])
for group in groups:
    verify(group)
assert (HERE / archive_name).read_bytes() == old_notes
assert (HERE / 'NOTES.md').read_bytes().startswith(b'\xef\xbb\xbf')
files = set().union(*(set(group) for group in groups))
files.update(['centre-v33r5-implementation.json', 'numeric-candidate-v33r5-check.json',
              'centre-v33r5-first-root-check.json', 'centre-v33r5-cost-raw.json',
              'build-centre-v33r5.log', 'probe-numeric-v33r5-once.log',
              'audit-first-roots-v33r5-once.log', 'measure-cost-v33r5-once.log',
              review_name, observation_name, archive_name, Path(__file__).name])
result = {'integrity_passed': True, 'numeric_passed': True,
          'capture_cost_gate_passed': False, 'cost_status': 'INCOMPLETE',
          'capture_permitted': False, 'metrics': metrics,
          'files': {n: digest(n) for n in sorted(files)},
          'protected': implementation['protected'],
          'display_before': implementation['display'],
          'display': {n: digest(n) for n in implementation['display']},
          'new_images': 0, 'inspections': 0, 'promoted': False}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['files', 'protected', 'display_before', 'display']}))
