"""Close the new offline implementation phase; no numerical/cost/capture run."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r6-implementation.json'
assert not OUT.exists()


def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def verify(group):
    for name, expected in group.items():
        assert digest(name) == expected, name


build = read('centre-v33r6-build.json')
hold = read('centre-v33r5-numerical-hold-integrity.json')
assert build['static_passed'] and build['browser_runs'] == 0
for receipt in [build, hold]:
    for group in ['files', 'protected', 'display']:
        verify(receipt[group])
assert build['protected'] == hold['protected']
assert read('build-centre-v33r6.log')['static_passed']
proof = read('centre-v33r6-factoring-proof.json')
bounds = read('centre-v33r6-bounds-check.json')
lifecycle = read('centre-v33r6-lifecycle-check.json')
assert proof['passed'] and bounds['passed'] and lifecycle['passed']
verify(proof['source_hashes'])
verify(bounds['source_hashes'])
assert bounds['inherited'] and bounds['new_bounds_runs'] == 0
for name in ['centre-v33r6-gpu-started.json', 'centre-v33r6-gpu-failure.json',
             'numeric-candidate-v33r6-check.json', 'centre-v33r6-first-root-check.json',
             'centre-v33r6-cost-raw.json', 'centre-v33r6-cost-review.json',
             'centre-v33r6-cost-lifecycle', 'centre-v33r6-integrity.json']:
    assert not (HERE / name).exists(), name
assert not list(HERE.glob('diagnostic-centre-v33r6*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'render_centre_v33r6.py').read_bytes().replace(b'v33r6', b'v33r3') == (HERE / 'render_centre_v33r3.py').read_bytes()

next_step = '''Run probe_numeric_candidate_v33r6.py ONCE with a unique saved log; wait for actual exit before checkpointing. Only PASS permits audit_centre_v33r6_first_roots.py ONCE, then measure_centre_v33r6_cost.py ONCE with its per-arm lifecycle journal. Environment: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. No bounds rerun. Preserve48cases/75996rays/720fixed+720interval roots and12balanced cost pairs against v33r3, unchanged hit/count/prefix/total-and-median wall gates. Inspect every exit/receipt; do not replay partial attempts. Only numerical+cost PASS permits creating centre-v33r6-integrity.json (integrity_passed,numeric_passed,capture_cost_gate_passed,files,protected) and the version-only original1200x800 HIGH/90000ms render ONCE. No prewarm, frame-pump change, relaxed gates or promotion.'''
review = '''# v33r6 implementation CLOSED — runtime pending

## Isolated shader change

`jc` previously invoked separate sine/cosine helpers, each doing identical angle
reduction, fold comparisons and squaring. A new `preciseSinCos` computes that
shared prefix once and evaluates the two original Horner polynomials unchanged.
The cosine sign assignments have no dependency on the sine result. Two edits
reverse exactly to v33r5. Everything after `jc`, including field expressions,
gradients, material/shading, certificates, marcher budgets and hit acceptance,
is byte-identical. Existing standalone sin/cos functions remain unchanged.
No frame-pump, camera, movement, source or live-default change.

This is substantive shared arithmetic/control factoring, not an identifier-only
retry. Its benefit is unmeasured: the compiler may already eliminate duplicated
work, and new code shape/register use may worsen cost. No speedup is claimed.

## Offline evidence

Source dependency-graph checks and exact reversal PASS; the independent scalar
oracle is byte-identical. 26,149 boundary/seeded JavaScript float64 inputs,
including signed zero, matched both original outputs bit-for-bit. JS/AST and
fixture derivation checks PASS. This is NOT GLSL compilation or float32 evidence.
Bounds inherit the prior sampled checks through expression equivalence; zero
new bounds runs. New unchanged 48-case/75,996-ray GPU and 720-fixed/720-interval
root fixtures are prepared, not run. All actual GPU/compiler gates remain open.

## Cost-runner lifecycle

The new candidate is compared against v33r3 using the same 12 balanced pairs,
dimensions, four readbacks, JS/outer timing boundaries and acceptance formulas.
Per-arm start is fsync'd before the first outer clock; completion saves the full
result after the second clock and before the next arm. Exceptions and catchable
SIGTERM/SIGHUP/SIGINT save failure events. Page setup, browser close, partial raw
summary and review-ready events provide additional lifecycle evidence. All new
receipt I/O is outside timing; it can still perturb between-arm host/cache/queue
state. No warmup, new timeout, watchdog, frame-pump edit or preconditioning.

Offline checks PASS for clock/I/O order, result roundtrip, replay rejection,
exception/interrupt/signal propagation and actual self-SIGTERM with handler
restoration. No browser was launched. SIGKILL, container loss, repeated signals
or storage failure cannot guarantee a terminal receipt. A last started event
without completion means INCOMPLETE/unknown, never an inferred slowdown.

## Held state / next gate

v33r5 numerical PASS and its interrupted cost evidence remain unchanged and
must not be replayed. v33r6 numerical/cost/capture are NOT RUN. The renderer is
version-only equivalent to the original v33r3 renderer and remains blocked.
No new PNG, inspection, visual grade, source/coverage update or promotion.
latest.png remains the labelled REJECTED GAME v32 deep-motion image; this is
not new visual progress. All19 realism and remaining source/coverage/route/full
acceptance remain unfinished. No completion marker.

''' + next_step + '\n'

review_name = 'centre-v33r6-implementation-review.md'
archive_name = 'NOTES-before-centre-v33r6-implementation.md'
for name in [review_name, archive_name]:
    assert not (HERE / name).exists()
old_notes = (HERE / 'NOTES.md').read_bytes()
notes = old_notes.decode('utf-8-sig')
assert notes.startswith('# Active: REDIRECT4 — v33r5 numerical PASS; cost INCOMPLETE, capture held')
notes = notes.replace('# Active: REDIRECT4 — v33r5 numerical PASS; cost INCOMPLETE, capture held',
                      '# Active: REDIRECT4 — v33r6 implementation CLOSED; runtime gates pending', 1)
notes = notes.split('## Exact next bounded work')[0] + '''## v33r6 implementation phase CLOSED — no runtime yet
- Substantive isolated jc sin/cos factoring: one shared angle reduction/fold/q, both original Horner polynomials unchanged. Two reversible edits recover v33r5 exactly; field/material/certificate/march suffix and scalar oracle byte-identical. No cheap/full/frame-pump change.
- Source dependency-graph/JS/AST/fixture checks PASS;26149JSfloat64 boundary/seeded inputs bit-equal,not GPUfloat32 evidence. Compiler may already share work;register/code-shape costs unknown,no speedup claim. Bounds inherited through expression equivalence,zero reruns.
- Prepared unchanged48cases/75996rays/720fixed+720interval numerical gates and12balanced cost pairs against v33r3. New runner saves durable per-arm start/full result/failure and browser lifecycle outside both timing boundaries;unchanged work/wall gates,no prewarm. Offline failure injection incl self-SIGTERM PASS. Hard kill/storage loss can still leave incomplete cause-unknown receipts;never replay.
- build_centre_v33r6.py ONCE exit0; build-centre-v33r6.log bound by centre-v33r6-implementation.json. All v33r5 hold/partial evidence preserved. Version-only original renderer prepared,never run. No passing centre-v33r6-integrity.json.
- Zero browser/numerical/cost/capture runs,new PNGs/inspections/promotion. README/status current;NOTES once,BOM preserved,prior notes archived verbatim. latest remains labelled REJECTED GAME v32;live/defaults/ledgers unchanged.

## Exact next bounded work
''' + next_step + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
anchor = 'No frame-pump change or limit relaxation.'
assert readme.count(anchor) == 1
readme = readme.replace(anchor, '''Isolated **v33r6 shared sin/cos reduction is prepared**. Exact source factoring,
scalar checks and offline per-arm lifecycle failure checks pass; actual GLSL,
independent roots and the unchanged balanced cost gates are pending. No browser
run or measured speedup. See [implementation checkpoint](centre-v33r6-implementation-review.md).
''' + anchor)
(HERE / archive_name).write_bytes(old_notes)
(HERE / review_name).write_text(review)
readme_path.write_text(readme)
(HERE / 'status.txt').write_text('Isolated v33r6 implementation CLOSED:shared sin/cos reduction,exact factoring/static+lifecycle checks PASS;GPU numerical/cost/capture NOT RUN,bounds inherited. v33r5 numerical PASS/cost INCOMPLETE preserved,no replay. Zero new PNGs/inspections/promotion;latest remains labelled REJECTED GAME v32 deep-motion;live v25/trip18/HUD/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
(HERE / 'NOTES.md').write_text(notes, encoding='utf-8-sig')
verify(build['files'])
verify(hold['files'])
verify(hold['protected'])
assert (HERE / archive_name).read_bytes() == old_notes
assert (HERE / 'NOTES.md').read_bytes().startswith(b'\xef\xbb\xbf')
files = set(build['files']) | {'centre-v33r6-build.json', 'build-centre-v33r6.log',
    'centre-v33r5-numerical-hold-integrity.json', review_name, archive_name, Path(__file__).name}
result = {'static_passed': True, 'numeric_status': 'NOT_RUN', 'cost_status': 'NOT_RUN',
          'capture_permitted': False, 'browser_runs': 0, 'new_images': 0, 'promoted': False,
          'files': {n: digest(n) for n in sorted(files)}, 'protected': hold['protected'],
          'display_before': hold['display'], 'display': {n: digest(n) for n in hold['display']}}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['files', 'protected', 'display_before', 'display']}))
