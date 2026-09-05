"""One-shot numerical closure; preserve live render and reviewed image."""
import ast
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v32-integrity.json'
assert not OUT.exists()
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
bounds=read('centre-v32-bounds-check.json')
gpu=read('numeric-candidate-v32-check.json')
roots=read('centre-v32-first-root-check.json')
assert bounds['passed'] and gpu['passed'] and roots['passed']
assert gpu['rays']==38160 and not gpu['errors']
assert roots['reference_rays']==360 and roots['unresolved_intervals']==0
for receipt,key in [(bounds,'source_hashes'),(gpu,'files'),(roots,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
assert read('centre-v32-build.json')['sha256']==digest('continuum-v32-candidate.js')
protected=bounds['protected_before']
assert protected==bounds['protected_after']
assert all(digest(n)==h for n,h in protected.items())
assert digest('continuum.js')==digest('continuum-v25.js')
assert digest('trip.js')==digest('trip-v18.js')
assert digest('latest.png')==digest('diagnostic-centre-v31-deep-motion.png')
scripts=['build_centre_candidate_v32.py','build_centre_v32_checks.py','field_centre_v32.py',
    'check_centre_v32_bounds.py','probe_numeric_candidate_v32.py',
    'audit_centre_v32_first_roots.py','render_centre_v32.py',Path(__file__).name]
for n in scripts:ast.parse((HERE/n).read_text(),filename=n)
subprocess.run(['node','--check',str(HERE/'continuum-v32-candidate.js')],check=True,capture_output=True)
for kind in ['candidate','leaves']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/f'gpu_probe_v32_{kind}.html').read_text())
    assert len(inline)==1
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js',dir=HERE) as temp:
        temp.write(inline[0]);temp.flush()
        subprocess.run(['node','--check',temp.name],check=True,capture_output=True)
cost=[]
for version in [31,32]:
    cases=read(f'numeric-candidate-v{version}-raw.json')
    iterations=np.concatenate([np.array(c['hits']).reshape(-1,4)[:,2] for c in cases])
    cost.append({'version':version,'mean_iterations':float(iterations.mean()),
        'p95_iterations':float(np.percentile(iterations,95)),'max_iterations':float(iterations.max()),
        'median_readback_wall_seconds':float(np.median([c['gpu_three_readbacks_seconds'] for c in cases]))})
(HERE/'centre-v32-cost-review.json').write_text(json.dumps({'cases':cost,
    'source_hashes':{f'numeric-candidate-v{v}-raw.json':digest(f'numeric-candidate-v{v}-raw.json') for v in [31,32]},
    'method':'Read saved raw only; no old probes replayed.',
    'limits':'Fewer iterations in these sparse rays, not a hardware-GPU benchmark or full-resolution90s settling pass.'},indent=2)+'\n')
review='''# v32 numerical phase — PASS; visually UNREVIEWED

## Changed construction

Local radius/depth curl coordinates replace v31's sparse radial fins. The
primary fold bends the 3x child, which bends the 9x HIGH fold; angular complex
harmonics deform these surfaces, with split cuts and connecting branch volumes.
This is a new zero set, not recolouring/widening v31. Materials remain unchanged.
See centre-v32-bounds.md and independent field_centre_v32.py for equations.
Construction names do not establish readable flower hierarchy or realism.

Clearance>=5.45,cap starts−27.5,walking x±4,entry8,exit−22. Per-leaf curvature
7+p+p² /305+190p+110p² /87+65p+54p²; global L16+8p. Explicit Gaussian jets
include primary amplitude2.15; rational core excludes the bright axial plate.
CSG cusp-safe reaches,2048/1536 budgets,14bisections,.00015 residual and
directional-depth gate retained; no forced minimum step or injected state.

## Completed checks — do not replay

- Independent72000 smooth-leaf/reach samples PASS: max gradient ratio.193856,
  curvature ratio.168824,min advanced free field1.108345e−5.12000 clearance
  samples and explicit Gaussian attenuation/derivative checks PASS.
- Actual GPU38160 rays across HIGH/LOW,even/odd grids,entry/deep,times4/8/221/900:
  zero misses/browser errors,max531iterations. All-leaf scalar<=.000087260,
  gradient<=.000279637,exact float32 CSG and saved-gradient replay error0.
  Eighteen composite-FD crease disagreements retained; not unique-normal proof.
- Original fixed-grid360/360 first roots PASS,max error.001408711. Grid spacing
  is .003; unchanged acceptance depth tolerance is .03 (not .003).
- Separate float64 interval-exclusion audit360/360 PASS,zero unresolved,max
  error.001408753. Earliest actual sign brackets<=1e−7. Ordinary arithmetic with
  outward pad1e−12,not formally directed-rounded intervals or universal proof.
- Python AST,candidate JS and both GPU inline scripts PASS. Evidence/protected
  hashes verified; no runtime,default captures or ledgers changed.

Saved v31→v32 rays: mean iterations133.22→67.64,p95 261→142,max1244→531;
median three-readback wall.259→.186s. No old probes replayed. Not a full-resolution
settling pass,hardware-GPU benchmark or smoothness/temporal-AA proof.

## Next phase

Run prepared render_centre_v32.py ONCE: real1200×800 HIGH entry/deep pairs,
>=3animation seconds at identical actual pose,90s settled limit. Native W with
read-only50ms timer observer,immediate key release then native Space pause;
retain stage/no-transition/deep z−8..−6 guards. Its45s walk wait is not the
original physical exit acceptance. V31's successful stop is not general proof.
Wait for renderer exit before opening PNG/JSON; inspect each NEW image ONCE,
adversarially grade,then bind receipts/review and update latest to inspected image.

No image generated this phase. latest.png still equals the inspected,labelled
REJECTED GAME v31 deep-motion diagnostic. V30/v31 rejected images and earlier
failures remain preserved. No promotion,fidelity or unchanged acceptance rerun.
All19 realism targets,other16 source gates,coverage,route and full acceptance
remain unfinished. No completion marker.
'''
(HERE/'centre-v32-numerical-review.md').write_text(review)
readme=(HERE/'README.md').read_text()
old='''Next:substantive v32 locally nested curled/branching petal volumes with depth
and resolved detail,not a recoloured/widened radial pinwheel. Live v25/trip18/HUD,
source/manual ledgers and all previous failed evidence remain unchanged.'''
assert readme.count(old)==1
new='''Isolated **v32 local curled-petal volumes** now pass72000 bounds/reach samples,
12000 clearance samples,38160 GPU rays and both360-ray first-root checks,
zero misses/browser errors. **Visually UNREVIEWED**,no promotion. Next:prepared
fresh HIGH entry/deep temporal capture with native timer-observed stop;90s
settling and full-resolution appearance remain untested. No new image yet.
See [v32 numerical review](centre-v32-numerical-review.md). Live v25/trip18/HUD,
source/manual ledgers and all previous failed evidence remain unchanged.'''
(HERE/'README.md').write_text(readme.replace(old,new))
(HERE/'status.txt').write_text('Isolated v32 local curled/branching petal volumes NUMERICAL PASS:72000 bounds/reach,12000 clearance,38160 GPU rays,360 fixed-grid plus interval first roots;zero misses/browser errors,max root error.001408753. Visually UNREVIEWED,no promotion. Next run prepared render_centre_v32.py ONCE for fresh1200x800 HIGH entry/deep pairs with native timer-observed stop and90s settling. latest.png remains inspected labelled REJECTED GAME v31 deep-motion;no new image. Live v25/trip18/HUD,defaults,ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
notes_path=HERE/'NOTES.md'
archive=HERE/'NOTES-before-centre-v32.md'
assert not archive.exists()
archive.write_bytes(notes_path.read_bytes())
lines=notes_path.read_text(encoding='utf-8-sig').splitlines()
lines[0]='# Active: REDIRECT4 — v32 NUMERICAL PASS / VISUALLY UNREVIEWED; NEXT fresh HIGH pairs'
for i,line in enumerate(lines):
    if line.startswith('2. v31 visual phase CLOSED'):
        lines[i]='2. v31 REJECTED GAME,never re-view/rerender. Substantive v32 local curled-petal successor numerical phase COMPLETE (below). Exact next:run prepared render_centre_v32.py ONCE,wait for exit,inspect each NEW1200x800 HIGH PNG ONCE,grade entry/deep temporal evidence. Retain native timer-observed controls,90s settled waits and all pose guards. No visual grade/promotion yet.'
notes='\n'.join(lines)+'\n\n'+'''## Completed v32 numerical phase (do not replay)
- build_centre_candidate_v32.py/build_centre_v32_checks.py ONCE:isolated local radius/depth curled-petal volumes replace sparse global fins. Parent curl C bends child D(3x),D bends HIGH E(9x);complex6/18/54 deformation,narrow split cuts,connecting branch volume. Materials unchanged;new zero set,not recolouring/widening. Visually UNREVIEWED,no source credit/promotion.
- field_centre_v32.py independent float64 evaluator/analytic_bounds();centre-v32-bounds.md prospective derivation. Clearance5.45,cap−27.5,x±4,entry8,exit−22;axial rational core excludes bright plate. H leaves7+p+p²/305+190p+110p²/87+65p+54p²,L16+8p. Primary Gaussian amplitude2.15 included. Cusp-safe reaches,2048/1536budgets,14bisections,.00015residual/directional gate unchanged,no minimum step.
- check_centre_v32_bounds.py ONCE PASS72000 samples,max gradient/curvature ratios.193856/.168824,min advanced1.108345e−5;12000 clearance and Gaussian checks PASS. probe_numeric_candidate_v32.py ONCE38160GPU rays,zero misses/errors,max531iterations;leaf scalar<=.000087260,gradient<=.000279637,exact CSG/replay0;18composite-FD crease disagreements retained. Fixed360roots PASS,max.001408711 (.003 GRID SPACING,.03 depth acceptance tolerance,not a.003 tolerance).
- audit_centre_v32_first_roots.py ONCE separate interval audit360PASS,zero unresolved,max.001408753,actual sign brackets<=1e−7;ordinary float64+pad,not formal interval/universal proof. Saved-ray costv31→32 mean133.22→67.64,p95 261→142,max1244→531,median readback wall.259→.186s;no GPU benchmark/full-resolution pass,old probes not replayed.
- render_centre_v32.py prepared NOT RUN:real1200x800 HIGH entry/deep pairs>=3anim seconds,90s settled waits,native timer-observed50ms W stop→immediate release→Space pause,stage/no transition/z−8..−6 guards. No injected state.45s walk wait is not original exit acceptance;v31 successful fixture not general proof. Next ONLY fresh v32 visual attempt,then review each new image once after exit.
- close_centre_v32_numerical.py ONCE binds evidence/protected/source hashes,AST/JS,review,cost,prepared renderer. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v32.md. No new image;latest remains inspected labelled REJECTED GAME v31 deep-motion. Live v25/trip18/HUD,defaults/manual/source ledgers immutable. No fidelity/unchanged acceptance rerun. All19/source/coverage/route/full unfinished.
'''
notes_path.write_text(notes,encoding='utf-8-sig')
files=list(dict.fromkeys(scripts+list(bounds['source_hashes'])+list(gpu['files'])+list(roots['source_hashes'])+[
    'centre-v32-build.json','centre-v32-cost-review.json','centre-v32-numerical-review.md',
    'centre-v32-first-root-check.json','check-centre-v32-bounds.log',
    'probe-numeric-candidate-v32.log','audit-centre-v32-first-roots.log']))
assert all(digest(n)==h for n,h in protected.items())
OUT.write_text(json.dumps({'integrity_passed':True,'numeric_passed':True,
    'visual_grade':'UNREVIEWED','promoted':False,'protected':protected,
    'files':{n:digest(n) for n in files},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md',archive.name]},
    'next':'Run render_centre_v32.py ONCE; wait for exit,inspect each new PNG once.'},indent=2)+'\n')
print(json.dumps({'integrity_passed':True,'numeric_passed':True,'visual_grade':'UNREVIEWED',
    'live_unchanged':True,'new_images':0,'next':'render_centre_v32.py ONCE'}))
