"""Bind completed reach-only validation, then update phase notes once."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v33r2-integrity.json'
assert not OUT.exists()
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def save(name,value):
    assert not (HERE/name).exists(),name
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
bounds=read('centre-v33r2-bounds-check.json')
gpu=read('numeric-candidate-v33r2-check.json')
roots=read('centre-v33r2-first-root-check.json')
assert bounds['passed'] and gpu['passed'] and roots['passed']
assert gpu['rays']==38160 and not gpu['errors']
assert roots['reference_rays']==360 and roots['unresolved_intervals']==0
for receipt,key in [(bounds,'source_hashes'),(gpu,'files'),(roots,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
assert read('centre-v33r2-build.json')['sha256']==digest('continuum-v33r2-candidate.js')
protected=bounds['protected_before']
assert protected==bounds['protected_after']
assert all(digest(n)==h for n,h in protected.items())
assert digest('continuum.js')==digest('continuum-v25.js')
assert digest('trip.js')==digest('trip-v18.js')
assert digest('latest.png')==digest('diagnostic-centre-v32-deep-motion.png')

# Exact source invariance, independently of the builder's intended changes.
old=(HERE/'continuum-v33-candidate.js').read_text()
new=(HERE/'continuum-v33r2-candidate.js').read_text()
def section(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
assert old[:old.index('   void fieldParts(')]==new[:new.index('   void fieldPartsReach(')]
leaf_end='    b=offset(3.*jm(childShell,childShell)-.45*filtered(jc(childLocal),12.,p)+1.1*angular36+1.1*jm(inv,inv),.345);'
assert section(old,'    vec3 q=p-',leaf_end)==section(new,'    vec3 q=p-',leaf_end)
assert section(old,'   vec4 jmax(', '   vec4 traceSample(')==section(new,'   vec4 jmax(', '   vec4 traceSample(')
assert old[old.index('   vec3 spectrum('):]==new[new.index('   vec3 spectrum('):]
assert section((HERE/'field_centre_v33.py').read_text(),'def parts(', 'def analytic_bounds(')==section((HERE/'field_centre_v33r2.py').read_text(),'def parts(', 'def analytic_bounds(')

scripts=['build_centre_v33r2.py','build_centre_v33r2_checks.py','field_centre_v33r2.py',
    'check_centre_v33r2_bounds.py','probe_numeric_candidate_v33r2.py',
    'audit_centre_v33r2_first_roots.py','render_centre_v33r2.py',Path(__file__).name]
for name in scripts:ast.parse((HERE/name).read_text(),filename=name)
subprocess.run(['node','--check',str(HERE/'continuum-v33r2-candidate.js')],check=True,capture_output=True)
for kind in ['candidate','leaves']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/f'gpu_probe_v33r2_{kind}.html').read_text())
    assert len(inline)==1
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js',dir=HERE) as temp:
        temp.write(inline[0]);temp.flush()
        subprocess.run(['node','--check',temp.name],check=True,capture_output=True)

cost=[];raw=[]
for version in ['33','33r2']:
    cases=read(f'numeric-candidate-v{version}-raw.json');raw.append(cases)
    steps=np.concatenate([np.array(c['hits']).reshape(-1,4)[:,2] for c in cases])
    cost.append({'version':version,'mean_iterations':float(steps.mean()),
        'p95_iterations':float(np.percentile(steps,95)),'max_iterations':float(steps.max()),
        'median_readback_wall_seconds':float(np.median([c['gpu_three_readbacks_seconds'] for c in cases]))})
delta=[]
for a,b in zip(*raw):
    assert all(a[k]==b[k] for k in ['width','height','z','time','high'])
    delta.extend(abs(np.array(a['hits']).reshape(-1,4)[:,0]-np.array(b['hits']).reshape(-1,4)[:,0]))
cost_review={'cases':cost,'maximum_saved_ray_depth_delta':float(max(delta)),
    'source_hashes':{f'numeric-candidate-v{v}-raw.json':digest(f'numeric-candidate-v{v}-raw.json') for v in ['33','33r2']},
    'method':'Compare saved raw only; no v33 replay. Identical ray/camera/clock/detail grids.',
    'limits':'Sparse SwiftShader probes, not hardware-GPU benchmark or full-resolution capture acceptance.'}
metrics={'samples':sum(c['samples'] for c in bounds['cases']),
    'improved_sampled_steps':sum(c['improved_steps'] for c in bounds['cases']),
    'lower_gradient_ratio':max(c['lower_gradient_ratio'] for c in bounds['cases']),
    'lower_curvature_ratio':max(c['lower_curvature_ratio'] for c in bounds['cases']),
    'min_advanced_field':min(c['min_advanced_field'] for c in bounds['cases']),
    'gpu_lower_scalar_error':max(c['lower_scalar_error'] for c in gpu['cases']),
    'gpu_lower_gradient_error':max(c['lower_gradient_error'] for c in gpu['cases']),
    'gpu_lower_minus_full':max(c['maximum_gpu_lower_minus_full'] for c in gpu['cases']),
    'gpu_full_leaf_scalar_error':max(c['max_all_leaf_scalar_error'] for c in gpu['cases']),
    'gpu_full_leaf_gradient_error':max(c['max_all_leaf_gradient_error'] for c in gpu['cases']),
    'composite_fd_discrepancies':sum(len(c['composite_fd_discrepancies']) for c in gpu['cases']),
    'fixed_root_error':gpu['max_reference_difference'],
    'interval_root_error':roots['max_reference_difference']}
next_work=('Run prepared render_centre_v33r2.py ONCE:original1200x800 HIGH,90s settled waits, '
    'real entry/deep controls and fixed-pose>=3s temporal pairs. Wait for renderer exit before '
    'viewing each NEW PNG exactly once. Preserve any timeout/failure; no unchanged replay or '
    'relaxation. No promotion until realism and all other gates pass.')
review='''# v33r2 numerical phase — PASS; visually UNREVIEWED

## Change and preserved field

Reach-only successor to the v33 capture timeout, not a new visual design.
Eight smooth lower leaves omit nonnegative costs or use supporting lines of
squared shells. Certified lower reaches are MAXed with existing full reaches
per intersection; union remains MIN. See centre-v33r2-bounds.md for derivation.
Exact source checks preserve full leaf calculations, CSG, full-leaf bounds,
positiveReach, main hit loop, normals and materials. Independent float64 parts
are source-identical and return bit-identical values at all72000 sample points.
No root budget/tolerance, clearance, cap, controls or shared clock changed.

## Independent validation

72000 full/lower derivative and free-reach samples PASS;44503 longer steps,
none shorter. Each sampled lower leaf <= its full leaf.12000 corridor/inner
clearance samples and Gaussian derivative/attenuation checks PASS.
38160 actual GPU rays PASS,zero misses/browser errors. All eight actual GPU
lower jets match independent float64 scalar/FD checks within original.001/.005
limits, and satisfy sampled domination without a positive allowance. Full jets
retain original tests; exact CSG and saved normal replay match. Zero new
composite-FD discrepancies; the two historical v33 discrepancies stay preserved.
360 fixed-grid references and360 separate interval first roots PASS,zero
unresolved. Maximum interval depth difference is.000619796753. Fixed-grid
spacing remains.003 and reference acceptance.03, not a.003 acceptance tolerance.
Intervals use ordinary float64 arithmetic with outward pad, not formal directed
rounding. Sparse samples do not prove universal convergence or temporal AA.

## Cost and capture decision

Saved same-grid v33→v33r2 mean steps586.1908→166.9232,p95929→252.05,
max1220→476. Median three-readback wall.96923→.41567s. Maximum saved-ray depth
delta.0005645752. Old probes were not rerun. This materially reduces measured
sparse-ray cost, but does not establish full1200×800 settling or hardware-GPU
performance. A fresh original HIGH/90s attempt is justified, not passed.

## State

Builder's first invocation lacked numpy and failed before writes; the single
completed build used the installed numpy environment. Both completed builders,
bounds check, GPU probe and interval audit ran once. Renderer prepared NOT RUN.
Live v25/trip18/HUD,defaults,source/manual ledgers and earlier failures remain
unchanged. No new PNG; latest remains inspected labelled REJECTED GAME v32
deep-motion. No visual or source/coverage credit. All19 realism,remaining16
source gates,coverage,route and full acceptance remain open.

## Next

'''+next_work+'\n'
readme_path=HERE/'README.md';readme=readme_path.read_text()
previous='''Next:isolated v33r2 conservative lower-bound reach optimization preserving
the petal zero set;independent validation before another HIGH attempt.
Original1200x800/90s/root limits stay unchanged. No v33 replay,new image or
source/coverage credit;live/defaults/ledgers and latest v32 diagnostic unchanged.'''
assert readme.count(previous)==1
replacement='''Isolated **v33r2 reach-only optimization now passes numerical validation**:
72000 lower/full-leaf reach samples,38160GPU rays,360fixed+360interval roots,
zero misses/errors/unresolved intervals. The v33 surface/materials are unchanged.
Saved-ray mean steps586.19→166.92,median readback.969→.416s;this is not a
full-resolution or hardware-GPU result. See [v33r2 review](centre-v33r2-numerical-review.md).
Next:prepared render_centre_v33r2.py ONCE,original1200x800 HIGH/90s entry/deep
temporal pairs. No new image,visual/source credit or promotion;latest v32
diagnostic,live/defaults/ledgers unchanged. All remaining gates stay open.'''
status=(HERE/'status.txt').read_text()
assert status.startswith('Isolated v33 HIGH CAPTURE FAIL:')
notes_path=HERE/'NOTES.md';notes_bytes=notes_path.read_bytes()
assert notes_bytes.startswith(b'\xef\xbb\xbf')
archive=HERE/'NOTES-before-centre-v33r2.md';assert not archive.exists()
notes=notes_bytes.decode('utf-8-sig').splitlines()
notes[0]='# Active: REDIRECT4 — v33r2 REACH NUMERICAL PASS / VISUALLY UNREVIEWED; NEXT original HIGH pairs'
idx=next(i for i,line in enumerate(notes) if line.startswith('2. v33 capture phase CLOSED:'))
notes[idx]='2. v33r2 isolated reach-only numerical phase COMPLETE;v33 timeout preserved. Exact next:render_centre_v33r2.py ONCE,original1200x800 HIGH/90s settled waits and real entry/deep temporal pairs. View each NEW PNG once after exit;no unchanged replay.'
notes='\n'.join(notes)+'\n\n## Completed v33r2 reach-only numerical phase (do not replay)\n'
notes+='- Eight lower leaves:axial/angular cost omission and±supporting lines of squared shells. MAX certified reaches with full-leaf reaches;union MIN. Exact source/scalar invariance of v33 zero set,CSG,main loop,normals/materials verified. .00001 lower-leaf slack,not formal GPU roundoff proof. Original clearance,budgets,tolerances/no minimum step intact.\n'
notes+='- Completed build/check builders ONCE;first builder invocation failed pre-write for missing numpy,then installed environment used. Independent72000samples/12000clearance PASS;44503longer sampled steps,none shorter.38160GPU rays PASS,zero misses/errors,new composite-FD discrepancies0;old v33 discrepancies2 preserved.360fixed+360interval roots PASS,zero unresolved. Metrics:'+json.dumps(metrics,separators=(',',':'))+'.\n'
notes+='- Saved v33→v33r2 cost mean586.19→166.92,p95929→252.05,max1220→476,median readback.969→.416s,max saved depth delta.0005645752. No old replay. Sparse SwiftShader samples,not universal convergence/temporalAA/hardware-GPU or full-resolution acceptance.\n'
notes+='- close_centre_v33r2_numerical.py ONCE binds numerical/source/protected hashes,source invariance,AST/JS,review,cost and prepared renderer NOT RUN. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v33r2.md. No new PNG;latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers and old failures unchanged;no fidelity/unchanged acceptance rerun.\n'
notes+='- Exact next:'+next_work+' All19 realism,remaining16source gates,coverage,route/full unfinished;no completion marker.\n'
save('centre-v33r2-cost-review.json',cost_review)
assert not (HERE/'centre-v33r2-numerical-review.md').exists()
(HERE/'centre-v33r2-numerical-review.md').write_text(review)
readme_path.write_text(readme.replace(previous,replacement))
(HERE/'status.txt').write_text('Isolated v33r2 REACH NUMERICAL PASS:72000full/lower-leaf samples,12000clearance,38160GPU rays,360fixed+360interval roots,zero misses/errors/unresolved. Preserves v33 petal zero set/materials;mean saved-ray steps586.19→166.92,median readback.969→.416s,not full-resolution acceptance. Visually UNREVIEWED;v33 HIGH90s timeout preserved. Next render_centre_v33r2.py ONCE,original1200x800 HIGH/90s entry/deep pairs,real controls. No new PNG;latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
archive.write_bytes(notes_bytes)
notes_path.write_text('\ufeff'+notes)
files=list(dict.fromkeys(scripts+list(bounds['source_hashes'])+list(gpu['files'])+list(roots['source_hashes'])+[
    'centre-v33r2-build.json','centre-v33r2-bounds.md','centre-v33r2-cost-review.json',
    'centre-v33r2-numerical-review.md','centre-v33r2-first-root-check.json',
    'build-centre-v33r2.log','build-centre-v33r2-checks.log','check-centre-v33r2-bounds.log',
    'probe-numeric-candidate-v33r2.log','audit-centre-v33r2-first-roots.log',
    'centre-v33-integrity.json','diagnostic-centre-v33-integrity.json','diagnostic-centre-v33-review.md']))
save(OUT.name,{'integrity_passed':True,'numeric_passed':True,'visual_grade':'UNREVIEWED',
    'source_invariance_passed':True,'protected':protected,'files':{n:digest(n) for n in files},
    'metrics':metrics,'cost':cost_review,'next':next_work,
    'display':{n:digest(n) for n in ['README.md','status.txt','NOTES.md','latest.png']}})
print(json.dumps({'numeric_passed':True,'integrity_passed':True,'metrics':metrics,'cost':cost,'next':next_work}))
