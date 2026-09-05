"""Independent global search from depth zero. No local hints are accepted."""
import json
from pathlib import Path
import numpy as np
from field_centre_v35r2 import PIXEL,smooth_parts,expanded_leaves,compose_expanded
from csg_interval_v35r2 import enclosure
from additive_runtime_v35r2 import HERE, artifact, read, worker, Journal, expected_cases, bijection, key
from additive_evidence_v35r2 import finish_global


def main():
    baseline=read(artifact('numerical','legacy-check.json'))
    cases=read(artifact('numerical','raw.json'))
    case_map=bijection(expected_cases(),cases,key)
    summary_map=bijection(expected_cases(),baseline['cases'],key)
    journal=Journal(HERE/artifact('global','rays'))
    design=json.loads((HERE/'centre-v35r2-bound-design.json').read_text())
    H=np.array(design['declared_H'])@np.array([1.,PIXEL,PIXEL**2])
    expanded_hessian=H[np.array(design['expanded_leaf_ids'])]
    
    def composed(v):
        return compose_expanded(expanded_leaves(v))
    
    def lower_bound(left,right,width):
        return enclosure(left,right,width,expanded_hessian)[0]
    
    results=[]
    assert len(cases)==len(baseline['cases'])==48
    for identity in expected_cases():
        case,old=case_map[identity],summary_map[identity]
        assert all(case[k]==old[k] for k in ['z','time','high','width','height'])
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
            leaves=smooth_parts(points,t,camera,high)
            lower=lower_bound(leaves[:-1],leaves[1:],np.diff(distances))
            rho=np.linalg.norm(np.column_stack([points[:,0],points[:,1]-1.7,
                .85*np.minimum(points[:,2]+27.5,0)]),axis=1)
            # Free ball allows skipping axis segments without a radial Hessian claim.
            envelope_free=np.maximum(rho[:-1],rho[1:])+.003<5.45
            assert np.all(np.minimum(rho[:-1],rho[1:])[~envelope_free]-.003>=4.965), "Taylor domain"
            potential=np.flatnonzero((lower<=0)&~envelope_free)
            subdivisions=0;excluded=0;unresolved=[]
            def sample(depth):
                return smooth_parts(camera+depth*ray,t,camera,high)
            def first(lo,hi,lv,hv,depth=0):
                nonlocal subdivisions,excluded
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
            journal.record('independent_ray_saved', key=[w,h,z,t,high,index], result=result)
            case_results.append(result)
        result={k:case[k] for k in ['z','time','high','width','height']}
        result.update({'references':case_results,'passed':all(r['passed'] for r in case_results)})
        results.append(result)
        print(json.dumps({k:v for k,v in result.items() if k!='references'}),flush=True)
    
    finish_global(results, journal)


if __name__=='__main__':
    worker('global', main)
