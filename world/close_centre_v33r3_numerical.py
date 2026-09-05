"""Close passing one-shot numerical evidence; does not render or promote."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r3-integrity.json'
assert not OUT.exists()

def read(name):
    return json.loads((HERE / name).read_text())

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

implementation = read('centre-v33r3-implementation.json')
assert implementation['implementation_static_passed']
verify(implementation['files'])
protected = implementation['protected']
verify(protected)
bounds = read('centre-v33r3-bounds-check.json')
gpu = read('numeric-candidate-v33r3-check.json')
roots = read('centre-v33r3-first-root-check.json')
cost = read('centre-v33r3-cost-review.json')
for receipt, key in [(bounds, 'source_hashes'), (gpu, 'files'),
                     (roots, 'source_hashes'), (cost, 'source_hashes')]:
    verify(receipt[key])
assert bounds['passed'] and gpu['passed'] and roots['passed']
assert bounds['protected_before'] == bounds['protected_after'] == protected
assert len(bounds['cases']) == 12 and len(gpu['cases']) == 32
assert gpu['rays'] == 50772 and gpu['reference_rays'] == roots['reference_rays'] == 480
assert not gpu['errors'] and roots['unresolved_intervals'] == 0
assert sum(c['misses'] for c in gpu['cases']) == 0
assert all(c['count_invariants_passed'] for c in gpu['cases'])
assert cost['all_v33r3']['rays'] == 50772
assert cost['matched_v33r2']['rays'] == cost['matched_v33r3']['rays'] == 38160
assert not list(HERE.glob('diagnostic-centre-v33r3*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
scripts = [name for name in implementation['files'] if name.endswith('.py')]
scripts.append(Path(__file__).name)
for name in scripts:
    ast.parse((HERE / name).read_text(), filename=name)
subprocess.run(['node', '--check', str(HERE / 'continuum-v33r3-candidate.js')], check=True)

metrics = {
    'leaf_samples': sum(c['samples'] for c in bounds['cases']),
    'cheap_gradient_ratio': max(c['cheap_gradient_ratio'] for c in bounds['cases']),
    'cheap_curvature_ratio': max(c['cheap_curvature_ratio'] for c in bounds['cases']),
    'cheap_minimum_advanced_field': min(c['cheap_minimum_advanced_field'] for c in bounds['cases']),
    'gpu_rays': gpu['rays'],
    'max_leaf_scalar_error': max(c['max_all_leaf_scalar_error'] for c in gpu['cases']),
    'max_leaf_gradient_error': max(c['max_all_leaf_gradient_error'] for c in gpu['cases']),
    'max_cheap_scalar_error': max(c['cheap_scalar_error'] for c in gpu['cases']),
    'max_cheap_gradient_error': max(c['cheap_gradient_error'] for c in gpu['cases']),
    'max_cheap_full_jet_error': max(c['cheap_full_jet_error'] for c in gpu['cases']),
    'composite_fd_discrepancies': sum(len(c['composite_fd_discrepancies']) for c in gpu['cases']),
    'fixed_root_error': gpu['max_reference_difference'],
    'interval_root_error': roots['max_reference_difference'],
}
next_work = ('Run prepared render_centre_v33r3.py ONCE, original1200x800 HIGH/90s, '
    'real entry/deep controls and fixed-pose>=3s pairs. Wait for process exit before '
    'viewing each NEW PNG exactly once. Preserve failures without relaxing limits '
    'or replaying unchanged work. No visual grade or promotion before inspection.')
review = '''# v33r3 numerical closure — PASS; visuals UNREVIEWED

The unchanged one-shot bounds, GPU, independent first-root and saved-cost scripts
completed. 72,000 leaf/reach samples, 12,000 clearance samples, Gaussian filter
checks, 32 GLSL cases / 50,772 rays and 480 fixed-grid plus 480 interval roots pass.
Both grids include the prior failed clock4.895, HIGH/LOW and entry/deep.
Zero GPU misses, browser errors or unresolved intervals. Cheap/full count
invariants pass; composite finite-difference discrepancies at creases are retained.

The implementation receipt binds exact parent recovery after removing the two
insertions. Full scalar, materials, normals, cameras, filtering and budgets remain
unchanged. This closure checks all implementation, numerical and protected hashes,
Python AST and candidate JS syntax. Live v25/trip18/HUD, defaults and ledgers stay
unchanged. No renderer or acceptance rerun occurred in this phase.

## Numerical metrics

```json
''' + json.dumps(metrics, indent=2) + '\n```\n\n## Saved-ray cost\n\n```json\n' + json.dumps(
    {k: v for k, v in cost.items() if k != 'source_hashes'}, indent=2) + '''
```

Matched mean iterations increased166.92→170.71; v33r3 averages105.46 full trace
calls and57.80 certified skips. Median three-readback time increased.416→.488s.
These timings do not demonstrate a speedup, even though the fast path avoids
full evaluation on many iterations. Full-resolution settling remains unproven.

Ordinary float64 sampled/interval evidence is not a formal GPU roundoff proof,
universal convergence or temporal-antialiasing acceptance. Timing boundaries and
instrumentation differ from v33r2; timing is indicative, not a controlled benchmark.
Trace counters omit shaded-frame work. Only a fresh original full-resolution
capture can test the existing90s gate; no runtime or realism pass is inferred.

## Next

''' + next_work + '''

Latest remains the already inspected, labelled REJECTED GAME v32 deep-motion
diagnostic. Prior v33/v33r2 HIGH90s failures remain intact. All19 realism,
remaining source/coverage/route/full acceptance work is unfinished.
'''
review_path = HERE / 'centre-v33r3-numerical-review.md'
assert not review_path.exists()
notes_path = HERE / 'NOTES.md'
archive = HERE / 'NOTES-before-centre-v33r3-numerical.md'
assert not archive.exists()
notes = notes_path.read_text(encoding='utf-8-sig')
notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v33r3 NUMERICAL PASS; NEXT original HIGH capture', 1)
notes += '\n## Completed v33r3 numerical phase (do not replay)\n'
notes += '- Bounds/GPU/first-root/cost scripts ONCE exit0:72000leaf/reach+12000clearance,32cases/50772GPU rays,480fixed+480interval roots PASS;zero misses/errors/unresolved. Failed4.895 covered on both grids,HIGH/LOW,entry/deep. Metrics:' + json.dumps(metrics, separators=(',', ':')) + '.\n'
notes += '- Saved-cost metrics:' + json.dumps({k: cost[k] for k in ['matched_v33r2', 'matched_v33r3', 'all_v33r3', 'max_matched_depth_delta']}, separators=(',', ':')) + '. Timing boundaries/instrumentation differ;indicative only,counters omit shaded work,no full-resolution speed or realism pass.\n'
notes += '- close_centre_v33r3_numerical.py ONCE binds passing numerical/source/protected/cost evidence and prepared renderer;AST/JS pass. No capture/fidelity/acceptance rerun;zero new PNGs. latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers and historical failures unchanged. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v33r3-numerical.md.\n'
notes += '- Exact next:' + next_work + ' All19/source/coverage/route/full unfinished;no completion marker.\n'
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r3 two-tier marcher is implemented, numerically and visually')
end = readme.index('\n\nOld full defaults', start)
replacement = '''Isolated **v33r3 two-tier marcher passes numerical checks; visuals UNREVIEWED**.
72,000 leaf/reach samples,12,000 clearance samples,50,772 GPU rays and480 fixed
plus480 interval roots pass,including failed clock4.895. Zero misses/errors or
unresolved intervals. Saved cost is indicative only,not full-resolution acceptance.
Matched median readback time rose.416→.488s; no speedup is established.
See [numerical review](centre-v33r3-numerical-review.md). Next: prepared original
1200x800 HIGH/90s capture ONCE. Prior v33/v33r2 failures remain;no promotion.
Zero-set,root/control limits,live/defaults/ledgers and latest v32 diagnostic unchanged.'''
status = ('Isolated v33r3 NUMERICAL PASS:72000leaf/reach+12000clearance,32cases/50772GPU rays,480fixed+480interval roots,zero misses/errors/unresolved. Saved cost indicative only;visually UNREVIEWED. Next render_centre_v33r3.py ONCE,original1200x800 HIGH/90s entry/deep pairs,real controls. v33/v33r2 FAIL90s preserved;no unchanged replay,no promotion. No new PNG;latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')

review_path.write_text(review)
readme_path.write_text(readme[:start] + replacement + readme[end:])
(HERE / 'status.txt').write_text(status)
archive.write_bytes(notes_path.read_bytes())
notes_path.write_text(notes, encoding='utf-8-sig')
verify(protected)
files = set(implementation['files']) - {'README.md', 'status.txt', 'NOTES.md'}
for receipt, key in [(bounds, 'source_hashes'), (gpu, 'files'),
                     (roots, 'source_hashes'), (cost, 'source_hashes')]:
    files.update(receipt[key])
files.update(['centre-v33r3-implementation.json', 'centre-v33r3-bounds-check.json',
    'numeric-candidate-v33r3-check.json', 'centre-v33r3-first-root-check.json',
    'centre-v33r3-cost-review.json', review_path.name, Path(__file__).name,
    'check-centre-v33r3-bounds.log', 'probe-numeric-candidate-v33r3.log',
    'audit-centre-v33r3-first-roots.log', 'measure-centre-v33r3-cost.log', archive.name])
OUT.write_text(json.dumps({'integrity_passed': True, 'numeric_passed': True,
    'visual_grade': 'UNREVIEWED', 'source_invariance_passed': True,
    'protected': protected, 'files': {n: digest(n) for n in sorted(files)},
    'metrics': metrics, 'cost': cost, 'next': next_work,
    'display': {n: digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', 'latest.png']}}, indent=2) + '\n')
print(json.dumps({'integrity_passed': True, 'numeric_passed': True, 'metrics': metrics,
    'next': next_work}), flush=True)
