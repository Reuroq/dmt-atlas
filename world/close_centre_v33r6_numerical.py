"""Close completed one-shot numerical/cost evidence; no browser or capture."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r6-integrity.json'
assert not OUT.exists(), 'One-shot closure'

def read(name):
    return json.loads((HERE / name).read_text())

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

implementation = read('centre-v33r6-implementation.json')
assert implementation['static_passed']
for group in ['files', 'protected', 'display']:
    verify(implementation[group])
proof = read('centre-v33r6-factoring-proof.json')
bounds = read('centre-v33r6-bounds-check.json')
gpu = read('numeric-candidate-v33r6-check.json')
roots = read('centre-v33r6-first-root-check.json')
cost = read('centre-v33r6-cost-review.json')
raw = read('centre-v33r6-cost-raw.json')
groups = [implementation['files'], proof['source_hashes'], bounds['source_hashes'],
          gpu['files'], roots['source_hashes'], cost['source_hashes'], raw['source_hashes']]
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
assert all(cost[k] for k in ['complete', 'work_not_worse', 'measured_wall_not_worse', 'capture_cost_gate_passed'])
assert not cost['errors'] and cost['failure'] is None
assert raw['started'] and len(raw['pairs']) == len(cost['pairs']) == 12
assert not raw['errors'] and raw['failure'] is None
assert cost['protected_before'] == cost['protected_after'] == implementation['protected']
assert all(c['hits_bit_equal'] and c['counts_bit_equal'] and
           c['candidate_mean_prefix_evaluations'] < c['parent_mean_prefix_evaluations'] for c in cost['pairs'])
assert all(w['candidate_total'] <= w['parent_total'] and w['median_paired_ratio'] <= 1 for w in cost['wall'].values())
records = [read(str(p.relative_to(HERE))) for p in sorted((HERE / 'centre-v33r6-cost-lifecycle').glob('*.json'))]
assert [r['sequence'] for r in records] == list(range(len(records)))
counts = Counter(r['event'] for r in records)
assert counts['arm_started'] == counts['arm_completed'] == 24 and counts['pair_completed'] == 12
assert not any('failed' in r['event'] for r in records)
assert records[-1]['event'] == 'review_ready' and records[-1]['capture_cost_gate_passed']
starts = [r['identity'] for r in records if r['event'] == 'arm_started']
ends = [r for r in records if r['event'] == 'arm_completed']
assert starts == [r['identity'] for r in ends]
for record in ends:
    identity = record['identity']
    assert record['result'] == raw['pairs'][identity['pair'] - 1][identity['arm']]
logs = ['probe-numeric-v33r6-once.log', 'audit-first-roots-v33r6-once.log', 'measure-cost-v33r6-once.log']
exits = ['probe-numeric-v33r6-exit.json', 'audit-first-roots-v33r6-exit.json', 'measure-cost-v33r6-exit.json']
assert all(read(n)['exit_code'] == 0 for n in exits)
assert all((HERE / n).stat().st_size > 0 for n in logs)
assert not (HERE / 'centre-v33r6-gpu-failure.json').exists()
assert not list(HERE.glob('diagnostic-centre-v33r6*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'render_centre_v33r6.py').read_bytes().replace(b'v33r6', b'v33r3') == (HERE / 'render_centre_v33r3.py').read_bytes()

review_name = 'centre-v33r6-numerical-review.md'
archive_name = 'NOTES-before-centre-v33r6-numerical.md'
assert all(not (HERE / n).exists() for n in [review_name, archive_name])
next_step = ('Run render_centre_v33r6.py ONCE with a unique saved log and actual exit receipt. '
             'Passing centre-v33r6-integrity.json now binds numerical/cost evidence. Preserve the version-only original '
             '1200x800 HIGH/90000ms renderer, native controls and all acceptance limits; no prewarm or numerical/cost replay. '
             'Wait for renderer exit before inspecting any new PNG/JSON. View each NEW PNG exactly once; never historical PNGs. '
             'Record visual/temporal results or failure honestly, then close capture integrity and update README/status/NOTES once. '
             'Do not promote an unreviewed or GAME/CLOSE candidate; latest remains labelled REJECTED GAME v32 until a justified update.')
review = '''# v33r6 numerical and paired-cost closure — PASS

All three one-shot commands exited 0; their logs and exit receipts are bound.
Actual GLSL: 48 cases, 75,996 rays, 720 fixed-grid references PASS; zero misses,
browser errors or composite-FD discrepancies. Independent interval audit:
720 references PASS, zero unresolved intervals. Worst root differences are
0.0006198227703571035 (fixed grid) and 0.0006197967529288917 (interval).
Bounds are inherited through the recorded factoring proof, not rerun.

The balanced 12-pair cost run completed with 24 durable arm start/result pairs,
12 pair receipts and clean browser closure. Hits and counts match exactly;
candidate source-level prefix evaluation estimates decrease in every pair.
Three-readback totals: parent 31.531100s, candidate 13.664200s; median paired
ratio 0.726982. Outer four-readback totals: 34.416032s and 16.085737s; median
ratio 0.769175. Both unchanged total-and-median wall gates PASS. First-pair
three-readback times were 27.369800s and 10.676800s, included without warmup.

These are sparse SwiftShader observations, not a statistical speedup test,
GPU-only timing, compilation isolation, full-resolution performance prediction,
universal numerical proof or realism evidence. The comparison includes both
shared-jets changes since v33r3 and the new sin/cos factoring; it cannot isolate
the latter's effect. Lifecycle I/O is outside timing but may perturb host state.

Source/protected/display hashes and version-only original renderer equality
are verified. centre-v33r6-integrity.json permits the original capture once;
the renderer has NOT run. Zero new PNGs or inspections, no promotion. Latest
remains labelled REJECTED GAME v32 deep-motion; live/defaults/ledgers unchanged.
All19 realism, remaining source, coverage, route and full acceptance unfinished.

## Next

''' + next_step + '\n'
old_notes = (HERE / 'NOTES.md').read_bytes()
notes = old_notes.decode('utf-8-sig')
notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v33r6 numerical/cost CLOSED PASS; original capture pending', 1)
notes = notes.split('## Exact next bounded work')[0] + '''## v33r6 numerical/cost phase CLOSED — PASS; no replay
- probe_numeric_candidate_v33r6.py ONCE exit0:48cases/75996GPUrays/720fixed roots PASS;zero misses/errors/composite-FD discrepancies,worst root difference .000619823. Bounds inherited,not rerun.
- audit_centre_v33r6_first_roots.py ONCE exit0:720interval roots PASS,zero unresolved,worst difference .000619797. Both logs and actual exit receipts saved.
- measure_centre_v33r6_cost.py ONCE exit0:12balanced pairs/24durable arm results,clean lifecycle;exact hits/counts,lower prefix estimates,unchanged cost gates PASS. Three-readback totals31.531100→13.664200s,median ratio.726982;outer totals34.416032→16.085737s,median.769175. No warmup. Sparse composite timing,not isolated GPU/compilation or full-resolution speed evidence;cannot isolate factoring from shared-jets changes.
- close_centre_v33r6_numerical.py binds sources,numerical/cost/lifecycle/log/exit evidence and protected files in passing centre-v33r6-integrity.json. Original renderer version-only equality checked;capture NOT RUN. No new PNGs/inspections/promotion;latest remains labelled REJECTED GAME v32. README/status current;NOTES once,BOM preserved,prior notes archived verbatim.

## Exact next bounded work
''' + next_step + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r6 shared sin/cos reduction is prepared**.')
end = readme.index('No frame-pump change or limit relaxation.', start)
readme = readme[:start] + '''Isolated **v33r6 numerical and paired-cost gates PASS**. Actual GLSL
48 cases / 75,996 rays, 720 fixed-grid plus 720 interval roots, and all 12
balanced cost pairs passed with exact hits/counts and lower prefix estimates.
Both unchanged total-and-median wall gates pass; sparse SwiftShader timing
does not establish full-resolution performance or isolate the latest factoring.
Durable arm results and exit receipts are bound by the passing capture integrity.
Original HIGH/90s capture is next, not yet run. No new PNG or promotion.
See [numerical/cost closure](centre-v33r6-numerical-review.md).
''' + readme[end:]
(HERE / archive_name).write_bytes(old_notes)
(HERE / review_name).write_text(review)
readme_path.write_text(readme)
(HERE / 'status.txt').write_text('Isolated v33r6 numerical/cost CLOSED PASS:48cases/75996GPUrays/720fixed+720interval roots;12balanced cost pairs/24durable arm results,exact hits/counts,lower prefix estimates,total+median wall gates PASS. Passing integrity saved;original1200x800 HIGH/90s capture NOT RUN,next ONCE. No full-resolution performance/realism claim,no replay. Zero new PNGs/inspections/promotion;latest labelled REJECTED GAME v32;live/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
(HERE / 'NOTES.md').write_text(notes, encoding='utf-8-sig')
verify(implementation['protected'])
for group in groups:
    verify(group)
assert (HERE / archive_name).read_bytes() == old_notes
assert (HERE / 'NOTES.md').read_bytes().startswith(b'\xef\xbb\xbf')
files = set().union(*(set(group) for group in groups))
files.update(['centre-v33r6-implementation.json', 'centre-v33r6-factoring-proof.json',
              'centre-v33r6-bounds-check.json', 'numeric-candidate-v33r6-check.json',
              'centre-v33r6-first-root-check.json', 'centre-v33r6-cost-review.json',
              'centre-v33r6-cost-raw.json', 'close-centre-v33r6-implementation.log',
              review_name, archive_name, Path(__file__).name, *logs, *exits])
result = {'integrity_passed': True, 'numeric_passed': True, 'capture_cost_gate_passed': True,
          'capture_permitted': True, 'capture_run': False,
          'files': {n: digest(n) for n in sorted(files)}, 'protected': implementation['protected'],
          'display_before': implementation['display'],
          'display': {n: digest(n) for n in implementation['display']},
          'lifecycle_counts': dict(counts), 'wall': cost['wall'],
          'new_images': 0, 'inspections': 0, 'promoted': False}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['files', 'protected', 'display_before', 'display']}))
