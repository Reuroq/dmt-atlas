"""Offline first-entry interval audit of every saved reference ray; no GPU replay.

Retains failed fixed-grid receipt. Uses independent float64 leaves with their
prospective analytic curvature bound to exclude intervals, then refines the
first possible occupied interval. This is not a floating-point interval library.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from field_centre_v30 import PIXEL,parts

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v30-first-root-check-r2.json'
assert not OUT.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
baseline=json.loads((HERE/'numeric-candidate-v30-check.json').read_text())
assert all(digest(n)==h for n,h in baseline['files'].items())
bounds=json.loads((HERE/'centre-v30-bounds-check.json').read_text())
assert bounds['passed'] and all(digest(n)==h for n,h in bounds['source_hashes'].items())
cases=json.loads((HERE/'numeric-candidate-v30-raw.json').read_text())
M=160+250*PIXEL+600*PIXEL**2

def composed(v):
    f,a,b=np.moveaxis(v,-1,0)
    return np.minimum(np.minimum(np.maximum(f,np.maximum(abs(a)-.19,.10-abs(b))),
        np.maximum(f+.32,np.maximum(abs(a)-.40,abs(b)-.055))),f+9)

def lower_bound(left,right,width):
    # Linear-interpolant departure <= M*h²/8 for every smooth leaf.
    # Extra numerical pad only makes exclusion harder, never hides a root.
    pad=M*np.asarray(width)**2/8+1e-12
    lo=np.minimum(left,right)-np.asarray(pad)[...,None]
    hi=np.maximum(left,right)+np.asarray(pad)[...,None]
    fl=lo[...,0]
    al=np.maximum(0,np.maximum(lo[...,1],-hi[...,1]))
    bl=np.maximum(0,np.maximum(lo[...,2],-hi[...,2]))
    bu=np.maximum(-lo[...,2],hi[...,2])
    return np.minimum(np.minimum(np.maximum(fl,np.maximum(al-.19,.10-bu)),
        np.maximum(fl+.32,np.maximum(al-.40,bl-.055))),fl+9)

results=[]
for case,old in zip(cases,baseline['cases']):
    z,t,high=case['z'],case['time'],case['high'];w,h=case['width'],case['height']
    camera=np.array([0,1.7,z]);hits=np.array(case['hits']).reshape(-1,4)
    case_results=[]
    for reference in old['references']:
        index=reference['ray']
        ray=np.array([((index%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,
            ((index//w+.5)/h*2-1)*np.tan(np.radians(34)),-1])
        ray/=np.linalg.norm(ray)
        distances=np.arange(0,hits[index,0]+1,.003)
        points=camera+distances[:,None]*ray
        leaves=np.stack(parts(points,t,camera,high),axis=-1)
        lower=lower_bound(leaves[:-1],leaves[1:],np.diff(distances))
        rho=np.linalg.norm(np.column_stack([points[:,0],points[:,1]-1.7,
            .85*np.minimum(points[:,2]+27.5,0)]),axis=1)
        # Free ball allows skipping axis segments without a radial Hessian claim.
        envelope_free=np.maximum(rho[:-1],rho[1:])+.003<5.48
        potential=np.flatnonzero((lower<=0)&~envelope_free)
        subdivisions=0;excluded=0;unresolved=[]
        def sample(depth):
            return np.array(parts(camera+depth*ray,t,camera,high))
        def first(lo,hi,lv,hv,depth=0):
            global subdivisions,excluded
            if lower_bound(lv,hv,hi-lo)>0:
                excluded+=1;return None
            fl,fh=float(composed(lv)),float(composed(hv))
            if hi-lo<=1e-7:
                if fl>0 and fh<0:return [lo,hi,fl,fh]
                # No forced root, no acceptance of a tiny residual as crossing.
                unresolved.append({'lo':lo,'hi':hi,'values':[fl,fh]})
                return None
            if depth>=32:raise AssertionError('Refinement budget exhausted')
            subdivisions+=1
            mid=(lo+hi)/2;mv=sample(mid)
            left=first(lo,mid,lv,mv,depth+1)
            if left is not None:return left
            if unresolved:return None
            return first(mid,hi,mv,hv,depth+1)
        bracket=None
        for k in potential:
            bracket=first(distances[k],distances[k+1],leaves[k],leaves[k+1])
            if bracket is not None or unresolved:break
        difference=None if bracket is None else abs((bracket[0]+bracket[1])/2-hits[index,0])
        result={'ray':index,'gpu_depth':hits[index,0],'original_reference':reference,
            'first_bracket':bracket,'difference':difference,'subdivisions':subdivisions,
            'refined_intervals_excluded':excluded,'coarse_intervals':len(distances)-1,
            'potential_intervals':len(potential),'unresolved':unresolved,
            'passed':bool(bracket is not None and not unresolved and difference<.03)}
        case_results.append(result)
    result={k:case[k] for k in ['z','time','high','width','height']}
    result.update({'references':case_results,'passed':all(r['passed'] for r in case_results)})
    results.append(result)
    print(json.dumps({k:v for k,v in result.items() if k!='references'}),flush=True)

other_gpu_checks=not baseline['errors'] and all(c['misses']==0 and c['max_all_leaf_gradient_error']<.005
    and c['max_all_leaf_scalar_error']<.001 and c['max_csg_replay_error']==0
    and c['max_saved_gradient_replay_error']==0 and c['max_field_cpu_gpu_difference']<.001
    and c['max_bound_ratio']<=1.001 for c in baseline['cases'])
flat=[r for c in results for r in c['references']]
files=['numeric-candidate-v30-check.json','numeric-candidate-v30-raw.json',
    'centre-v30-first-root-adverse.json','centre-v30-bounds-check.json',
    'field_centre_v30.py',Path(__file__).name]
out={'passed':other_gpu_checks and all(c['passed'] for c in results) and len(flat)==360,
    'other_gpu_checks_passed':other_gpu_checks,'original_fixed_grid_passed':baseline['passed'],
    'cases':results,'reference_rays':len(flat),
    'max_reference_difference':max((r['difference'] for r in flat if r['difference'] is not None),default=None),
    'unresolved_intervals':sum(len(r['unresolved']) for r in flat),
    'source_hashes':{n:digest(n) for n in files},
    'method':'Independent float64 CSG interval exclusion from smooth-leaf linear-interpolation error M*h²/8; envelope excludes singular axis. Refine earliest potential interval left-first to actual positive/negative bracket <=1e-7. Original .003 grid FAIL retained. No GPU replay, changed tolerance, forced root or minimum step.',
    'limits':'Analytic leaf bounds plus ordinary float64 arithmetic with1e-12 outward pad, not formally directed-rounding interval proof. Sparse saved rays only; grazing tangencies without sign change may be unresolved and fail. No temporal filtering or realism credit.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['cases','source_hashes']}),flush=True)
assert out['passed']
