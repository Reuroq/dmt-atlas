"""One-shot saved numerical evidence gate; no GPU/CPU samples rerun."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v29-integrity.json'
assert not OUT.exists(), 'Preserve integrity receipt'
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def read(name):
    return json.loads((HERE/name).read_text())
bounds=read('centre-v29-bounds-check.json')
numeric=read('numeric-candidate-v29-check.json')
leaves=read('centre-v29-leaf-check.json')
assert bounds['passed'] and leaves['passed'] and not numeric['passed']
assert not numeric['errors'] and not leaves['errors']
for receipt,key in [(bounds,'source_hashes'),(numeric,'files'),(leaves,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
assert bounds['protected_before']==bounds['protected_after']==leaves['protected_before']==leaves['protected_after']
assert all(digest(n)==h for n,h in leaves['protected_after'].items())
assert numeric['rays']==38160 and numeric['reference_rays']==360
assert len(numeric['cases'])==len(leaves['cases'])==24
for n,l in zip(numeric['cases'],leaves['cases']):
    assert all(n[k]==l[k] for k in ['z','time','high','width','height'])
    assert n['misses']==0 and n['max_iterations']<(2048 if n['high'] else 1536)
    assert n['max_bound_ratio']<=1.001 and n['max_field_cpu_gpu_difference']<.001
    assert len(n['references'])==15 and all(not r.get('missing_reference') and r['difference']<.03 for r in n['references'])
    assert l['passed'] and l['max_all_leaf_gradient_error']<.005 and l['max_all_leaf_scalar_error']<.001
    assert l['max_composition_selection_error']<.005 and l['max_saved_gradient_replay_error']<.005
files=['centre-v29-bounds-check.json','numeric-candidate-v29-check.json','centre-v29-leaf-check.json',
    'continuum-v29-candidate.js','centre-v29-bounds.md','render_centre_v29.py',
    'centre-v29-numerical-review.md','NOTES.md','README.md','status.txt',Path(__file__).name]
out={'integrity_passed':True,'numeric_passed':True,'original_composite_fd_passed':False,
    'numeric_basis':'Fresh v29 smooth-leaf bounds/CSG interval samples; 38160 actual GPU rays and 360 first-crossing references; independent all-leaf float64 gradient/scalar audit at saved GPU roots and exact GPU-normal replay. CSG one-sided normal verification replaces mathematically inapplicable central differences across creases; old failures remain saved.',
    'candidate_promoted':False,'visual_review_pending':True,'overall_passed':False,
    'protected':leaves['protected_after'],'files':{n:digest(n) for n in files},
    'limits':'Sampled numerical evidence only; no new image, realism, full-resolution performance, smooth-motion, coverage, source, original45s exit or full acceptance pass.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print('PASS: v29 saved numerical evidence and protected assets verified. Fresh visual sequence pending; no promotion.')
