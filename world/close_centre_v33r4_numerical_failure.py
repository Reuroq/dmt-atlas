"""Close the one-shot GLSL compilation failure without replay or promotion."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r4-numerical-failure-integrity.json'
assert not OUT.exists()

def read(name):
    return json.loads((HERE / name).read_text())

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

implementation = read('centre-v33r4-implementation.json')
for key in ['files', 'protected', 'display']:
    verify(implementation[key])
bounds = read('centre-v33r4-bounds-check.json')
gpu = read('numeric-candidate-v33r4-check.json')
verify(bounds['source_hashes'])
verify(gpu['files'])
assert bounds['passed'] and not gpu['passed']
assert bounds['protected_before'] == bounds['protected_after'] == implementation['protected']
assert len(gpu['cases']) == 48 and gpu['rays'] == 75996
assert gpu['reference_rays'] == 0 and all(not c['passed'] for c in gpu['cases'])
assert len(gpu['errors']) == 2
assert all("'common' : Illegal use of reserved word" in e for e in gpu['errors'])
assert sum(c['misses'] for c in gpu['cases']) == gpu['rays']
for name in ['centre-v33r4-first-root-check.json', 'centre-v33r4-cost-raw.json',
             'centre-v33r4-cost-review.json', 'centre-v33r4-integrity.json']:
    assert not (HERE / name).exists(), name
assert not list(HERE.glob('diagnostic-centre-v33r4*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')

metrics = {'bounds_exit': 0, 'gpu_probe_exit': 1,
           'leaf_reach_samples': sum(c['samples'] for c in bounds['cases']),
           'clearance_samples': sum(c['samples'] for c in bounds['clearance']),
           'attempted_cases': len(gpu['cases']), 'attempted_rays': gpu['rays'],
           'validated_gpu_rays': 0, 'reference_roots': gpu['reference_rays'],
           'browser_shader_errors': len(gpu['errors']),
           'first_root_runs': 0, 'cost_runs': 0, 'capture_runs': 0,
           'new_images': 0, 'inspections': 0}
review = '''# v33r4 numerical phase — GLSL compilation FAIL

The prepared checks ran sequentially once: bounds exit 0, GLSL probe exit 1.
Bounds retain their sampled PASS: 72,000 leaf/reach and 12,000 clearance samples.
The browser emitted two shader errors (candidate and leaf-audit programs):
`ERROR: 0:123: 'common' : Illegal use of reserved word`, followed by syntax error.
The shared-jet parameter/local identifier is reserved in GLSL. Static JS/AST and
expression checks did not compile the embedded shader and did not detect it.

All 48 attempted cases / 75,996 ray slots failed; zero reference roots were found.
Readbacks after failed compilation are not valid field, gradient, work or timing
measurements. They establish neither a marcher numerical failure nor performance.
The saved raw/check JSON and log are immutable failure evidence. No replay.

Independent first-root audit, paired cost experiment and full-resolution capture
were NOT run because the GLSL prerequisite failed. No passing numerical integrity
gate was created. No PNG exists to inspect or copy. latest.png remains the labelled
REJECTED GAME v32 deep-motion image; stale defaults, live v25/trip18/HUD, sources,
manual grades and protected evidence are unchanged. No promotion or realism credit.

Next: create a new isolated revision with only whole-token `common` renamed to a
non-reserved identifier in the candidate and derived fixtures. Preserve v33r4
failure evidence; verify exact token-reversal and identical expressions/control.
Use new filenames/receipts and reject compiler errors before treating readbacks as
measurements. Do not replay unchanged completed bounds or historical probes. Bind
inherited bounds only after proving scalar equivalence. The new revision still
needs actual GLSL, independent root and balanced cost gates before the unchanged
1200x800 HIGH/90000ms renderer. No prewarm or frame-pump changes.

All19 realism, remaining16 source gates, coverage, route/full acceptance unfinished.
'''
review_name = 'centre-v33r4-numerical-failure-review.md'
assert not (HERE / review_name).exists()
archive = HERE / 'NOTES-before-centre-v33r4-numerical-failure.md'
assert not archive.exists()
notes_path = HERE / 'NOTES.md'
old_notes = notes_path.read_bytes()
notes = old_notes.decode('utf-8-sig')
notes = notes.replace('# Active: REDIRECT4 — v33r4 implementation CLOSED; validation next',
                      '# Active: REDIRECT4 — v33r4 numerical CLOSED; GLSL compile FAIL', 1)
assert '## Exact next bounded work' in notes
notes = notes.split('## Exact next bounded work')[0] + '''## v33r4 numerical phase CLOSED — compile FAIL; no replay
- check_centre_v33r4_bounds.py ONCE exit0:72000leaf/reach+12000clearance PASS. probe_numeric_candidate_v33r4.py ONCE exit1:two shader compilation errors, `common` is reserved GLSL (line123 in compiled fragment). JS/AST checks had not compiled shaders.
- 48attempted cases/75996ray slots,all failed,zero reference roots. Readbacks after failed compilation are INVALID numerical/work/timing evidence;not a marcher convergence or speed result. Raw/check/log preserved. Independent first-root,cost,capture NOT RUN because prerequisite failed.
- close_centre_v33r4_numerical_failure.py binds implementation/numerical/protected/display hashes and failure review. No passing centre-v33r4-integrity.json,no new PNG or inspection,no promotion. latest still labelled REJECTED GAME v32 deep-motion;live/defaults/ledgers unchanged. README/status current;NOTES once,BOM preserved,old notes archived.

## Exact next bounded work
Create a new isolated identifier-only revision (v33r5): replace whole-token `common` with a non-reserved shared-jet identifier in candidate and derived fixtures. Preserve every v33r4 artifact. Prove exact token reversal,unchanged expressions/control/materials and inherited scalar/bounds equivalence;do not rerun unchanged completed bounds. New GPU fixture must fail on shader errors before accepting readbacks;use unique filenames/receipts. Run new actual GLSL then independent first-roots then balanced cost sequentially,once each,with saved logs and gate inspection. Preserve48cases/75996rays/720fixed+720interval references and clocks2.4077/3.5242/4.895,both grids,HIGH/LOW,entry/deep. Cost must retain identical instrumentation/boundaries,12balanced pairs,no warmup;hold on changed hits/counters,worse inferred prefix work or total/median paired wall cost. Only passing numerical+cost integrity permits new version-only original1200x800 HIGH/90000ms capture. No frame-pump changes,prewarming,relaxed gates or promotion on failure.

All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.
'''
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r4 shared-prefix implementation is complete**')
end = readme.index('No frame-pump change or limit relaxation.', start)
readme = readme[:start] + '''Isolated **v33r4 FAILS GLSL compilation**: `common` is a reserved shader
identifier. Bounds PASS; all48 GPU cases are invalid after compilation failure.
First-root/cost/capture held; no new PNG, speedup or realism claim. Failure preserved
in [numerical review](centre-v33r4-numerical-failure-review.md). Next is a separately
versioned identifier-only correction, retaining all gates and historical evidence.
''' + readme[end:]
status = ('Isolated v33r4 numerical CLOSED: bounds PASS; GLSL compile FAIL (reserved common identifier), '
          '48 attempted cases/75996 ray slots INVALID, zero roots. First-root/cost/capture NOT RUN; '
          'failure preserved, no replay/promotion. Next isolated identifier-only v33r5 fix plus original gates. '
          'latest.png remains labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD/defaults/ledgers '
          'unchanged;all19/source/coverage/route/full unfinished.\n')
(HERE / review_name).write_text(review)
archive.write_bytes(old_notes)
readme_path.write_text(readme)
(HERE / 'status.txt').write_text(status)
notes_path.write_text(notes, encoding='utf-8-sig')
verify(implementation['protected'])
files = set(implementation['files']) - {'README.md', 'status.txt', 'NOTES.md'}
files.update(bounds['source_hashes'])
files.update(gpu['files'])
files.update(['centre-v33r4-implementation.json', 'centre-v33r4-bounds-check.json',
              'numeric-candidate-v33r4-check.json', 'check-centre-v33r4-bounds.log',
              'probe-numeric-candidate-v33r4.log', review_name, archive.name, Path(__file__).name])
result = {'integrity_passed': True, 'numeric_passed': False,
          'capture_cost_gate_passed': False, 'visual_grade': 'UNREVIEWED',
          'failure': 'GLSL reserved identifier common; no compiled candidate or leaf program',
          'metrics': metrics, 'protected': implementation['protected'],
          'files': {n: digest(n) for n in sorted(files)},
          'display': {n: digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', 'latest.png']}}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'integrity_passed': True, 'numeric_passed': False,
                  'files': len(files), 'protected': len(implementation['protected']), 'metrics': metrics}))
