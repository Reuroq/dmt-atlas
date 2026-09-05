"""One-shot numerical closure; no render, promotion or acceptance rerun."""
from pathlib import Path
import ast
import hashlib
import json
import re
import statistics
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v31-integrity.json'
assert not OUT.exists()
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
bounds=read('centre-v31-bounds-check.json')
gpu=read('numeric-candidate-v31-check.json')
roots=read('centre-v31-first-root-check.json')
assert bounds['passed'] and gpu['passed'] and roots['passed']
assert roots['reference_rays']==360 and roots['unresolved_intervals']==0
assert gpu['rays']==38160 and not gpu['errors']
for receipt,key in [(bounds,'source_hashes'),(gpu,'files'),(roots,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
protected=bounds['protected_before']
assert protected==bounds['protected_after']
assert all(digest(n)==h for n,h in protected.items())
assert digest('continuum.js')==digest('continuum-v25.js')
assert digest('trip.js')==digest('trip-v18.js')
assert digest('latest.png')==digest('diagnostic-centre-v30-entry-motion.png')
scripts=['build_centre_candidate_v31.py','build_centre_v31_checks.py','field_centre_v31.py',
    'check_centre_v31_bounds.py','probe_numeric_candidate_v31.py',
    'audit_centre_v31_first_roots.py','render_centre_v31.py',Path(__file__).name]
for n in scripts:ast.parse((HERE/n).read_text(),filename=n)
subprocess.run(['node','--check',str(HERE/'continuum-v31-candidate.js')],check=True,capture_output=True)
for kind in ['candidate','leaves']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/f'gpu_probe_v31_{kind}.html').read_text())
    assert len(inline)==1
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js',dir=HERE) as temp:
        temp.write(inline[0]);temp.flush()
        subprocess.run(['node','--check',temp.name],check=True,capture_output=True)
cost=[]
for v in [30,31]:
    cases=read(f'numeric-candidate-v{v}-raw.json')
    iterations=[x for c in cases for x in c['hits'][2::4]]
    cost.append({'version':v,'rays':len(iterations),'mean_iterations':statistics.mean(iterations),
        'p95_iterations':sorted(iterations)[int(.95*len(iterations))],
        'max_iterations':max(iterations),
        'median_three_readbacks_seconds':statistics.median(c['gpu_three_readbacks_seconds'] for c in cases)})
cost_receipt={'method':'Read existing raw numerical evidence only; no historical probe replay. Low-resolution SwiftShader float-target readbacks, not HIGH full-frame or hardware-GPU benchmark.',
    'cases':cost,'conclusion':'v31 costs more than v30 in these samples despite tighter per-leaf bounds. Full HIGH90s settling is untested; no speedup claim.'}
(HERE/'centre-v31-cost-review.json').write_text(json.dumps(cost_receipt,indent=2)+'\n')
review='''# v31 numerical phase — passed; visuals UNREVIEWED

The isolated candidate replaces Cartesian rose-product bands with smooth complex
6/18/54-fold swept petal fins. Parent phase changes bend physical child surfaces;
thin split petals and transverse branches leave real gaps. A smooth core keeps
both bright families off the exact axis; that ray reaches recessed dark backing.
No angular seam, tiled-cell field, fake miss opening or live promotion.

See centre-v31-bounds.md for the independent complex derivative derivation,
clearance4.9, unchanged exit−22/cap−27.5, Gaussian jets and per-leaf reaches.
The current 2048/1536 budgets,14bisections,.00015residual and directional-depth
gate remain unchanged. No minimum step or numerical tolerance was relaxed.

## New checks

- Bounds/reach:72000 samples PASS; max gradient ratio.226596, curvature ratio
  .148542; minimum sampled advanced field8.50925e−6. Corridor/free-radius12000
  samples and Gaussian attenuation/derivative checks PASS.
- GPU:38160 rays, zero misses/errors; all actual leaf scalar errors<=.000172370,
  gradient errors<=.000566538; exact float32 CSG selection and gradient replay.
  Fourteen composite finite-difference crease disagreements remain recorded;
  they are not assertions of a differentiable CSG surface.
- Original fixed .003 reference:all360 PASS, max first-root error.003195637
  under unchanged.03. Offline left-first interval exclusion independently
  passes all360, zero unresolved, max.003195633. This uses ordinary float64
  with an outward pad, not directed-rounding interval arithmetic/universal proof.
- Python AST, candidate JS and both inline GPU probes pass syntax checks.
  Live runtime, source/manual ledgers, default images/receipts and latest match
  the protected hashes. No fidelity or unchanged desktop acceptance replay.

## Cost and prepared capture

Per-leaf curvature11/22/140 removes the unnecessarily shared160 bound, but
the changed shape is MORE costly overall in the saved numerical samples:
mean iterations133.22 versus59.23, p95 261 versus113, maximum1244 versus249;
median three-readback wall time.259s versus.194s. See centre-v31-cost-review.json.
These are low-resolution SwiftShader probes, not actual full-resolution frames
or a hardware benchmark. Do not claim a speedup or a passed90s settled gate.

render_centre_v31.py is prepared, NOT RUN. It retains actual1200×800 HIGH,
entry/deep same-pose pairs at least3animation seconds apart and90s settled waits.
Deep stop now uses50ms read-only timer polling rather than RAF polling. It
releases native W immediately after the stop handle resolves, then uses native
Space to pause before fetching the captured diagnostic snapshot. The snapshot
is read-only; no pose/input/clock injection. Wrong stage or z outside−8..−6 fails.
The walk wait is45s, not an exit-acceptance claim. This removes an observer's
RAF dependency; it does NOT prove the exact cause of the preserved v30 overshoot.

Two generated-script preparation corrections were made before their use:
the interval audit dropped a nonexistent inherited v30-specific adverse-receipt
filename; the capture snapshots the observed stop without a diagnostic roundtrip
before keyup. Original builders remain hashed and were not replayed.

## Next / display

Run the prepared fresh v31 capture once. Wait for process exit, then inspect
each completed new PNG exactly once, grade still/temporal evidence adversarially
and keep failures. If full-resolution cost or deep stopping fails, address the
observed failure in a changed successor; never relax limits or retry unchanged.

No new image exists in this phase. latest.png remains the already-inspected,
labelled ISOLATED v30 entry-motion diagnostic, GAME; v30 remains rejected.
Live v25/trip18/HUD unchanged. All19 realism, remaining16 source gates,
coverage, route and full acceptance remain unfinished. No completion marker.
'''
(HERE/'centre-v31-numerical-review.md').write_text(review)
readme=HERE/'README.md'
text=readme.read_text()
text=text.replace('## Current build — v25 geometry / v16 controls','## Current build — v25 geometry / v18 controls')
anchor='[numerical evidence and limits](centre-v30-numerical-review.md).'
assert text.count(anchor)==1
text=text.replace(anchor,anchor+'''

The isolated **v31 swept hierarchical flower** now passes the new numerical
checks:72000 bound/reach samples,12000 clearance samples,38160 GPU rays and
both independent360-ray first-root checks. **Visually UNREVIEWED**, no promotion.
Its sampled cost is higher than v30 despite per-leaf bounds; full HIGH90s
settling remains untested. The next fresh capture uses timer-observed native
deep stopping and unchanged HIGH/temporal limits. No new PNG this phase;
latest remains the labelled rejected v30 image above.
See [v31 numerical review and next capture](centre-v31-numerical-review.md).
''')
readme.write_text(text)
(HERE/'status.txt').write_text('Isolated v31 swept6/18/54-fold petal successor NUMERICAL PASS:72000 bounds/reach,12000 clearance,38160 GPU rays,360 fixed-grid plus interval first roots;zero browser errors. Visually UNREVIEWED,no promotion. Sampled cost higher than v30;HIGH90s settling/deep stop untested. Next run prepared render_centre_v31.py ONCE for fresh1200x800 HIGH entry/deep pairs with timer-observed native stop. latest.png remains inspected labelled v30 entry-motion GAME;v30 rejected/deep overshoot preserved. Live v25/trip18/HUD,defaults,ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
notes_path=HERE/'NOTES.md'
original=notes_path.read_bytes()
archive=HERE/'NOTES-before-centre-v31.md'
assert not archive.exists()
archive.write_bytes(original)
notes=original.decode('utf-8-sig')
lines=notes.splitlines()
lines[0]='# Active: REDIRECT4 — v31 NUMERICAL PASS / VISUALLY UNREVIEWED; NEXT fresh HIGH pairs'
for i,line in enumerate(lines):
    if line.startswith('2. v30 visual attempt CLOSED,REJECTED:'):
        lines[i]='2. v30 remains REJECTED GAME,deep overshoot preserved;never re-view/rerender. Substantive v31 successor and numerical phase COMPLETE (below). Exact next: run prepared render_centre_v31.py ONCE,wait for exit,inspect each new completed PNG ONCE,adversarially grade HIGH entry/deep temporal evidence. New timer-based real-input stopping is untested;no injected state or relaxed guards. Full-resolution field cost remains a concern. No promotion before visual gates.'
notes='\n'.join(lines)+'\n\n'+'''## Completed v31 numerical phase (do not replay)
- Isolated continuum-v31-candidate.js replaces Cartesian rose products with regularized complex6/18/54-fold swept petal fins,nested phase bending,thin split/branch CSG and deeper dark backing. Smooth core excludes bright axial endplate. Actual geometry,not pigment-only;UNREVIEWED. Source audit unchanged. build_centre_candidate_v31.py/build_centre_v31_checks.py ran ONCE.
- field_centre_v31.py independent float64 complex evaluator and analytic_bounds();centre-v31-bounds.md derives smooth harmonic L/H,Gaussian jets,clearance4.9,cap−27.5,exit−22,x±4. Per-leaf M11+2p+2p²/22+13p+10p²/140+140p+170p²;global L12+10p. CSG cusp handling,budgets2048/1536,14bisections,.00015residual/directional gate unchanged;no forced minimum.
- check_centre_v31_bounds.py ONCE PASS72000 reach/derivative samples,max ratios.226596/.148542,min advanced8.50925e−6;12000 clearance and Gaussian checks PASS. probe_numeric_candidate_v31.py ONCE38160 GPU rays,zero misses/browser errors;all leaf scalar<=.000172370,gradient<=.000566538,exact CSG/replay0;14 composite-FD crease disagreements retained. Original fixed.003 first-root360/360 PASS,max.003195637. audit_centre_v31_first_roots.py ONCE independently passes360,zero unresolved,max.003195633;ordinary float64 with pad,not formal interval/universal proof.
- Cost review reads saved v30/v31 raw only,no rerun:mean iterations59.23→133.22,p95 113→261,max249→1244;median3readback wall.194→.259s. New shape is MORE costly despite per-leaf bounds;no speedup/GPU benchmark. Full1200x800 HIGH90s settling untested;must preserve failures,not relax limits.
- render_centre_v31.py prepared NOT RUN:HIGH1200x800 entry/deep pairs>=3anim seconds,90s settled,actual controls. Deep uses read-only50ms timer polling,immediate nativeW release then nativeSpace pause;stop handle snapshot fetched afterward,assert stage/no transition/z−8..−6;walk wait45s is NOT original exit acceptance. Removes RAF observer dependency,not proven cause of v30 overshoot. No pose/input/clock injection. Pre-use corrections removed nonexistent inherited adverse-receipt filename from audit and diagnostic roundtrip before keyup from fixture;builders preserved,not replayed.
- close_centre_v31_numerical.py ONCE binds receipt/source/protected hashes,AST/JS checks,cost/review and prepared capture. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v31.md. No new images;latest remains inspected labelled rejected v30 entry-motion GAME. Live v25/trip18/HUD,defaults/manual/source ledgers immutable. No fidelity/unchanged desktop acceptance or promotion. Exact next fresh v31 visual attempt only;all19/source/coverage/route/full unfinished.
'''
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
assert all(digest(n)==h for n,h in protected.items())
files=set(scripts+['continuum-v31-candidate.js','gpu_probe_v31_candidate.html','gpu_probe_v31_leaves.html',
    'centre-v31-build.json','centre-v31-bounds.md','centre-v31-bounds-check.json',
    'numeric-candidate-v31-check.json','numeric-candidate-v31-raw.json','centre-v31-first-root-check.json',
    'centre-v31-cost-review.json','centre-v31-numerical-review.md','check-centre-v31-bounds.log',
    'probe-numeric-candidate-v31.log','audit-centre-v31-first-roots.log'])
OUT.write_text(json.dumps({'integrity_passed':True,'numeric_passed':True,'visual_grade':'UNREVIEWED',
    'protected':protected,'files':{n:digest(n) for n in sorted(files)},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md','NOTES-before-centre-v31.md']},
    'next':'Run prepared render_centre_v31.py ONCE; wait for exit then inspect each new completed PNG ONCE. No live promotion or overall completion.'},indent=2)+'\n')
print('v31 numerical phase closed: sampled PASS,visual UNREVIEWED,cost concern retained;live/latest/defaults unchanged.')
