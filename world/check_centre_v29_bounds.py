"""One-shot new smooth-leaf bounds and CSG first-entry interval samples."""
import hashlib
import json
from pathlib import Path
import numpy as np
from field_centre_v29 import PIXEL, parts, field
from fidelity import RENDER_FILES

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-v29-bounds-check.json'
assert not OUT.exists(), 'Preserve sampled evidence'
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

protected = list(dict.fromkeys(RENDER_FILES+['data.js','fidelity-data.js',
    'fidelity-grades.json','realism-grades.json','latest.png',
    'visual-chrysanthemum.png','visual-chrysanthemum.json']))
before = {n:digest(n) for n in protected}
rng = np.random.default_rng(29001)
n = 6000
v = rng.normal(size=(n,3));v /= np.linalg.norm(v,axis=1)[:,None]
rho = rng.uniform(4.5,16,n)
p = v*rho[:,None];p[:,1] += 1.7
p[:,2] = -27.5-np.abs(p[:,2])/.45
angle = rng.uniform(-np.pi,np.pi,n//2)
p[:n//2,0] = rho[:n//2]*np.cos(angle)
p[:n//2,1] = 1.7+rho[:n//2]*np.sin(angle)
p[:n//2,2] = rng.uniform(-27.8,12,n//2)
d = rng.normal(size=(n,3));d /= np.linalg.norm(d,axis=1)[:,None]
t = rng.choice([4.,8.,221.,900.],n)
L, M = 12+12*PIXEL, 100+160*PIXEL+400*PIXEL**2
eps = .001
results = []
for z in [8,-6]:
    camera = np.array([0,1.7,z])
    for high in [1,0]:
        def leaves(q):
            return np.stack(parts(q,t,camera,high),axis=-1)
        centre,plus,minus = leaves(p),leaves(p+eps*d),leaves(p-eps*d)
        slopes = (plus-minus)/(2*eps)
        curvature = (plus-2*centre+minus)/eps**2
        # Positive-reach composition independent of GLSL and using numerical
        # smooth leaf slopes. Guarded free-side samples only.
        def reach(values, derivatives):
            remaining=.95*np.maximum(values,0)
            slope=np.abs(derivatives)
            return np.minimum(.4,2*remaining/np.maximum(1e-30,slope+np.sqrt(slope*slope+2*M*remaining)))
        f,a,b=centre.T;df,da,db=slopes.T
        sa=reach(np.abs(f)-.14,np.sign(f)*df)
        sb=reach(np.abs(f-2.6)-.18,np.sign(f-2.6)*df)
        step=np.minimum(np.maximum(sa,reach(a,da)),np.maximum(sb,reach(b,db)))
        step=np.minimum(step,reach(6-f,-df))
        free=field(p,t,camera,high)>1e-6
        minimum=1e9
        for fraction in [.25,.5,.75,1.]:
            values=field(p+d*(step*fraction)[:,None],t,camera,high)
            minimum=min(minimum,float(values[free].min()))
        result={'camera_z':z,'high':high,'samples':n,
            'max_leaf_gradient_ratio':float(np.max(np.abs(slopes))/L),
            'max_leaf_curvature_ratio':float(np.max(np.abs(curvature))/M),
            'free_side_samples':int(free.sum()),'min_sampled_advanced_field':minimum}
        result['passed']=(result['max_leaf_gradient_ratio']<1 and result['max_leaf_curvature_ratio']<1 and minimum>=-1e-7)
        results.append(result)
after={n:digest(n) for n in protected}
files=['continuum-v29-candidate.js','build_centre_candidate_v29.py',
    'field_centre_v29.py','centre-v29-bounds.md',Path(__file__).name,
    'gpu_probe_v29_candidate.html','probe_numeric_candidate_v29.py']
out={'passed':all(r['passed'] for r in results) and before==after,
    'leaf_gradient_bound':L,'leaf_curvature_bound':M,'cases':results,
    'source_hashes':{n:digest(n) for n in files},'protected_before':before,'protected_after':after,
    'limitations':'Deterministic finite-difference smooth-leaf and four-point CSG interval samples, not universal proof; actual GPU gradients and first-root references still required. No renders or live promotion.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['source_hashes','protected_before','protected_after']}))
assert out['passed']
