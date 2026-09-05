"""Close one-shot v33 numerical evidence; no live promotion or visual grade."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v33-integrity.json'
assert not OUT.exists()
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
bounds=read('centre-v33-bounds-check.json')
gpu=read('numeric-candidate-v33-check.json')
roots=read('centre-v33-first-root-check.json')
assert bounds['passed'] and gpu['passed'] and roots['passed']
assert gpu['rays']==38160 and not gpu['errors']
assert roots['reference_rays']==360 and roots['unresolved_intervals']==0
for receipt,key in [(bounds,'source_hashes'),(gpu,'files'),(roots,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
assert read('centre-v33-build.json')['sha256']==digest('continuum-v33-candidate.js')
protected=bounds['protected_before']
assert protected==bounds['protected_after']
assert all(digest(n)==h for n,h in protected.items())
assert digest('continuum.js')==digest('continuum-v25.js')
assert digest('trip.js')==digest('trip-v18.js')
assert digest('latest.png')==digest('diagnostic-centre-v32-deep-motion.png')
scripts=['build_centre_candidate_v33.py','build_centre_v33_checks.py','field_centre_v33.py',
    'check_centre_v33_bounds.py','probe_numeric_candidate_v33.py',
    'audit_centre_v33_first_roots.py','render_centre_v33.py',Path(__file__).name]
for n in scripts:ast.parse((HERE/n).read_text(),filename=n)
subprocess.run(['node','--check',str(HERE/'continuum-v33-candidate.js')],check=True,capture_output=True)
for kind in ['candidate','leaves']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/f'gpu_probe_v33_{kind}.html').read_text())
    assert len(inline)==1
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js',dir=HERE) as temp:
        temp.write(inline[0]);temp.flush()
        subprocess.run(['node','--check',temp.name],check=True,capture_output=True)
cost=[]
for version in [32,33]:
    cases=read(f'numeric-candidate-v{version}-raw.json')
    iterations=np.concatenate([np.array(c['hits']).reshape(-1,4)[:,2] for c in cases])
    cost.append({'version':version,'mean_iterations':float(iterations.mean()),
        'p95_iterations':float(np.percentile(iterations,95)),'max_iterations':float(iterations.max()),
        'median_readback_wall_seconds':float(np.median([c['gpu_three_readbacks_seconds'] for c in cases]))})
cost_review={'cases':cost,
    'source_hashes':{f'numeric-candidate-v{v}-raw.json':digest(f'numeric-candidate-v{v}-raw.json') for v in [32,33]},
    'method':'Read saved raw only; no old probes replayed.',
    'limits':'Materially higher sparse-ray cost. Not hardware-GPU benchmark or proof of full-resolution timeout; unchanged90s HIGH capture gate remains required.'}
metrics={
    'leaf_samples':sum(c['samples'] for c in bounds['cases']),
    'gradient_bound_ratio':max(c['max_leaf_gradient_ratio'] for c in bounds['cases']),
    'curvature_bound_ratio':max(c['max_leaf_curvature_ratio'] for c in bounds['cases']),
    'min_advanced_field':min(c['min_advanced_field'] for c in bounds['cases']),
    'max_leaf_scalar_error':max(c['max_all_leaf_scalar_error'] for c in gpu['cases']),
    'max_leaf_gradient_error':max(c['max_all_leaf_gradient_error'] for c in gpu['cases']),
    'composite_fd_discrepancies':sum(len(c['composite_fd_discrepancies']) for c in gpu['cases']),
    'fixed_root_error':gpu['max_reference_difference'],
    'interval_root_error':roots['max_reference_difference']}
next_work=('Run prepared render_centre_v33.py ONCE with original1200x800 HIGH,90s settled waits, '
    'real entry/deep controls and fixed-pose>=3s temporal pairs. Wait for exit before viewing '
    'each NEW PNG exactly once. Record any timeout/failure without changing limits or replaying '
    'unchanged work. If cost prevents capture, preserve evidence and build an isolated '
    'nonnegative-cost lower-bound reach optimization, preserving this zero set; independently '
    'revalidate that changed marcher before another capture. No visual grade or promotion yet.')
review='''# v33 numerical phase — PASS; visually UNREVIEWED

## Structural replacement

Broad annular membranes are removed. Separate parent/child volumetric cells use
squared curled shells plus nonnegative angular and axial costs. Parent cells
have12 angular maxima; child cells have36 and3x radial/depth subdivision.
Costs close and taper the rims, leaving actual free gaps. Parent curl and twist
feed child coordinates; HIGH adds further shell folding. LOW retains both cell
families. This is geometry, not recolouring; it is NOT yet visual realism.

Existing audited sources only. Materials,live v25/trip18/HUD,default captures,
manual/source ledgers and earlier rejected/failed evidence remain unchanged.

## Prospective safety and independent evidence

See centre-v33-bounds.md and independent field_centre_v33.py. Clearance>=5.8,
conservative envelope5.445,cap−27.5,x±4,entry8,exit−22; bright axis excluded
for r<=2.78. Full Gaussian product derivatives and harmonic amplitudes included.
Three smooth leaves,monotone union/intersection; no absolute-band cusps.
H polynomials:(4,1,1),(388,522,468),(4321,6236,4990); L185+148pixel.
Unchanged2048/1536 iterations,14bisections,.00015 residual,directional-depth
gate,no forced minimum step. Analytic bounds apply to ideal scalar functions;
GPU float/trig accuracy is separately sampled,not formally certified.

72000 leaf/reach samples and12000 corridor/free-ball samples PASS; Gaussian
attenuation/derivative checks PASS. 38160 actual GPU rays PASS,zero misses or
browser errors. Exact float32 CSG selection and saved-normal replay are equal.
Even/odd grids,HIGH/LOW,entry/deep,times4/8/221/900. Fixed360 first roots and
independent interval360 first roots PASS; zero unresolved intervals. Original
.003 is scan spacing,not the .03 root acceptance tolerance.
'''
review+='\nMeasured metrics:\n\n```json\n'+json.dumps(metrics,indent=2)+'\n```\n'
review+='''
Two composite finite-difference discrepancies remain recorded,not hidden;
all smooth-leaf checks passed. Ordinary float64 interval arithmetic+pad is
not directed-rounding proof,universal convergence or temporal-AA evidence.

## Cost and next gate

Saved v32→v33 mean iterations67.64→586.19,p95929 versus142,max1220 versus531.
Median three-readback wall time .186→.969s. This substantial cost increase is
a concern for full-resolution90s settling,not proof of a timeout and not a
hardware-GPU benchmark. No HIGH visual capture has been attempted.

'''+next_work+'''

No new PNG. latest.png remains the inspected,labelled ISOLATED REJECTED GAME
v32 deep-motion diagnostic; it does not depict v33. No fidelity or unchanged
acceptance rerun. All19 realism targets,remaining16 source gates,coverage,
route and full acceptance remain open. No completion marker.
'''
# Verify documentation anchors before the one-write NOTES update.
readme_path=HERE/'README.md'
readme=readme_path.read_text()
old='''ledgers and earlier failed evidence remain unchanged. Next:isolated v33 discrete
tapered/curled petal cells with resolved child geometry and open depth gaps,
replacing broad annular sheets; independently validate the changed field first.'''
assert readme.count(old)==1
new='''ledgers and earlier failed evidence remain unchanged.

Isolated **v33 closed tapered/curled petal cells** now pass72000 bounds/reach
samples,12000 clearance samples,38160 GPU rays and both360-ray first-root
checks;zero misses/browser errors. **Visually UNREVIEWED**,no promotion or new
image. Sparse-ray mean steps rise67.64→586.19;90s full-resolution settling is
untested. Next:one guarded HIGH entry/deep temporal capture attempt,unchanged
limits. See [v33 numerical review](centre-v33-numerical-review.md).'''
notes_path=HERE/'NOTES.md'
original=notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive=HERE/'NOTES-before-centre-v33.md'
assert not archive.exists()
assert not (HERE/'centre-v33-cost-review.json').exists()
assert not (HERE/'centre-v33-numerical-review.md').exists()
assert (HERE/'status.txt').read_text().startswith('Isolated v32 REJECTED GAME:')
lines=original.decode('utf-8-sig').splitlines()
lines[0]='# Active: REDIRECT4 — v33 NUMERICAL PASS / VISUALLY UNREVIEWED; NEXT guarded HIGH pairs'
idx=next(i for i,line in enumerate(lines) if line.startswith('2. v32 visual phase CLOSED:'))
lines[idx]='2. v33 closed petal-cell numerical phase COMPLETE; v32 remains REJECTED GAME. Exact next:guarded render_centre_v33.py ONCE,original1200x800 HIGH/90s limits. Cost concern below. Wait for exit,view each NEW PNG once;no replay of closed evidence.'
notes='\n'.join(lines)+'\n\n## Completed v33 numerical phase (do not replay)\n'
notes+='- One-shot builders created isolated12-fold tapered curled parent cells and36-fold3x radial/depth child cells. Squared shells+nonnegative angular/axial costs close rims,replace annular sheets with actual gaps. HIGH additional folding,LOW both families. Materials/sources unchanged. Visually UNREVIEWED,no promotion.\n'
notes+='- Independent field_centre_v33.py and centre-v33-bounds.md:clearance5.8,retained envelope5.445,cap−27.5,axis exclusion2.78. H(4,1,1)/(388,522,468)/(4321,6236,4990);L185+148pixel. Gaussian cross terms included. Original2048/1536,14bisections,.00015residual/directional gate,no minimum step.\n'
notes+='- check_centre_v33_bounds.py ONCE PASS72000 leaf/reach+12000 clearance;probe_numeric_candidate_v33.py ONCE PASS38160GPU rays,zero misses/errors,exact CSG/replay0;2composite-FD discrepancies retained. audit_centre_v33_first_roots.py ONCE360PASS,zero unresolved. Metrics:'+json.dumps(metrics,separators=(',',':'))+'. Samples/ordinary float64 intervals,not universal or temporal-AA proof.\n'
notes+='- Saved-ray costv32→33 mean67.64→586.19,p95142→929,max531→1220,median3-readback wall.186→.969s. Materially slower;not hardware-GPU benchmark or proven90s full-resolution timeout. No old probe replayed. Prepared renderer NOT RUN.\n'
notes+='- close_centre_v33_numerical.py ONCE binds numerical/source/protected hashes,AST/JS,review,cost and prepared renderer. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v33.md. No new PNG;latest remains inspected,labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults and ledgers unchanged. No fidelity/unchanged acceptance rerun.\n'
notes+='- Exact next: '+next_work+' All19 realism,remaining16 source gates,coverage,route/full acceptance remain open;no completion marker.\n'
(HERE/'centre-v33-cost-review.json').write_text(json.dumps(cost_review,indent=2)+'\n')
(HERE/'centre-v33-numerical-review.md').write_text(review)
readme_path.write_text(readme.replace(old,new))
(HERE/'status.txt').write_text('Isolated v33 closed tapered/curled parent+child petal cells NUMERICAL PASS:72000 leaf/reach,12000 clearance,38160GPU rays,360fixed+360interval roots,zero misses/errors. Visually UNREVIEWED,no promotion. Cost concern:mean586.19steps vs67.64;90s full-resolution settling untested. Next guarded render_centre_v33.py ONCE,original1200x800 HIGH entry/deep temporal pairs and90s limits;preserve any failure. latest.png remains inspected labelled REJECTED GAME v32 deep-motion,no new PNG. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
archive.write_bytes(original)
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
files=list(dict.fromkeys(scripts+list(bounds['source_hashes'])+list(gpu['files'])+list(roots['source_hashes'])+[
    'centre-v33-build.json','centre-v33-cost-review.json','centre-v33-numerical-review.md',
    'centre-v33-bounds-check.json','centre-v33-first-root-check.json',
    'check-centre-v33-bounds.log','probe-numeric-candidate-v33.log','audit-centre-v33-first-roots.log']))
assert all(digest(n)==h for n,h in protected.items())
OUT.write_text(json.dumps({'integrity_passed':True,'numeric_passed':True,
    'visual_grade':'UNREVIEWED','promoted':False,'protected':protected,
    'files':{n:digest(n) for n in files},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md',archive.name]},
    'next':next_work},indent=2)+'\n')
print('v33 numerical closure PASS;visually UNREVIEWED,cost concern recorded,no new images/live changes;next guarded HIGH attempt.')
