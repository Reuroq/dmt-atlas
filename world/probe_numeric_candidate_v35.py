"""Actual GLSL validation, unchanged v25 limits plus central/late-time coverage.
No injected journey state. Samples are not universal accuracy/convergence proof.
"""
import json
import time
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from verify import ARGS
from fidelity import digest
from field_centre_v35 import field, smooth_parts, expanded_leaves
from gpu_csg_v35 import BASE_KEYS, EXPANDED_KEYS, expand_jets, replay
from runtime_centre_v35 import fixture_gate, passed, one_shot
from cost_lifecycle_v35 import atomic_json, Lifecycle

HERE = Path(__file__).resolve().parent

def main():
    destination = HERE/'numeric-candidate-v35-check.json'
    assert not destination.exists(), 'One-shot probe already recorded'
    gate = fixture_gate()
    passed('centre-v35-bounds-check.json')
    journal = Lifecycle(HERE/'centre-v35-gpu-lifecycle')
    journal.record('browser_launch_started')
    errors, cases = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        journal.record('browser_launched')
        page = browser.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.goto((HERE/'gpu_probe_v35_candidate.html').as_uri())
        leaf_page=browser.new_page()
        leaf_page.on('pageerror',lambda e:errors.append(str(e)))
        leaf_page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        leaf_page.goto((HERE/'gpu_probe_v35_leaves.html').as_uri())
        for w,h,times in [(48,32,[2.4077,3.5242,4,4.895,8]), (49,33,[2.4077,3.5242,4,4.895,8,221,900])]:
            for z in [8,-6]:
                for t in times:
                    for high in [1,0]:
                        start = time.monotonic()
                        journal.record('case_started', width=w, height=h, z=z, time=t, high=high)
                        case = page.evaluate('a=>runCase(...a)', [z,t,high,w,h])
                        case['gpu_four_readbacks_seconds'] = time.monotonic()-start
                        case['leaves']=leaf_page.evaluate('c=>auditLeaves(c)',case)
                        assert not errors, 'Browser errors invalidate readbacks: '+repr(errors)
                        journal.record('case_completed', case=case)
                        cases.append(case)
                        print(f'GPU {w}x{h} z={z} t={t} high={high}: {case["gpu_three_readbacks_seconds"]:.2f}s', flush=True)
        journal.record('browser_close_started')
        browser.close()
        journal.record('browser_closed')
    atomic_json(HERE/'numeric-candidate-v35-raw.json', cases)
    summaries, root_errors = [], []
    for case in cases:
        z,t,high = case['z'],case['time'],case['high']
        camera = np.array([0,1.7,z])
        w,h = case['width'],case['height']
        i = np.arange(w*h)
        rays = np.stack([((i%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,
                         ((i//w+.5)/h*2-1)*np.tan(np.radians(34)), -np.ones(w*h)], axis=-1)
        rays /= np.linalg.norm(rays,axis=-1)[:,None]
        hits = np.array(case['hits']).reshape(-1,4)
        grad = np.array(case['gradientSlope']).reshape(-1,4)
        actual = np.array(case['points']).reshape(-1,4)[:,:3]
        points = camera+rays*hits[:,0,None]
        eps = 1e-4
        leaf_scalar=smooth_parts(actual,t,camera,high)
        leaf_fd=np.stack([(smooth_parts(actual+np.eye(3)[a]*eps,t,camera,high)-smooth_parts(actual-np.eye(3)[a]*eps,t,camera,high))/(2*eps) for a in range(3)],axis=-1)
        base_jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in BASE_KEYS],axis=1)
        jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in EXPANDED_KEYS],axis=1)
        lower_scalar=expanded_leaves(leaf_scalar)
        lower_fd=np.stack([(expanded_leaves(smooth_parts(actual+np.eye(3)[a]*eps,t,camera,high))-expanded_leaves(smooth_parts(actual-np.eye(3)[a]*eps,t,camera,high)))/(2*eps) for a in range(3)],axis=-1)
        lower_scalar_error=float(np.max(abs(lower_scalar-jets[:,:,3])))
        lower_gradient_error=float(np.max(abs(lower_fd-jets[:,:,:3])))
        expanded_replay_error=float(np.max(abs(expand_jets(base_jets)-jets)))
        aperture_a,aperture_b,selected,selected_ids=replay(jets)
        gpu_a=np.array(case['leaves']['apertureA'],dtype=np.float32).reshape(-1,4)
        gpu_b=np.array(case['leaves']['apertureB'],dtype=np.float32).reshape(-1,4)
        aperture_replay_error=float(max(np.max(abs(aperture_a-gpu_a)),np.max(abs(aperture_b-gpu_b))))
        domination=float(max(np.max(jets[:,1:5,3]-gpu_a[:,3,None]),np.max(jets[:,6:10,3]-gpu_b[:,3,None])))
        cheap_jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in ['cheapF','cheapA','cheapB']],axis=1)
        cheap_scalar=lower_scalar[:,[0,1,6]]
        cheap_fd=lower_fd[:,[0,1,6]]
        cheap_scalar_error=float(np.max(abs(cheap_scalar-cheap_jets[:,:,3])))
        cheap_gradient_error=float(np.max(abs(cheap_fd-cheap_jets[:,:,:3])))
        cheap_full_error=float(np.max(abs(cheap_jets-jets[:,[0,1,6]])))
        counts=np.array(case['counts']).reshape(-1,4)
        count_valid=bool(np.all(np.isfinite(counts)) and np.all(counts>=0)
            and np.all(counts==np.floor(counts)) and np.all(counts[:,0]==counts[:,1]+counts[:,2])
            and np.all(counts[:,0]<=hits[:,2]) and np.all(counts[:,3]<=14))
        composed=np.array(case['leaves']['composed']).reshape(-1,4)
        leaf_scalar_error=float(np.max(abs(leaf_scalar-base_jets[:,:,3])))
        leaf_gradient_error=float(np.max(abs(leaf_fd-base_jets[:,:,:3])))
        csg_error=float(np.max(abs(selected-composed)))
        replay_error=float(np.max(abs(composed[:,:3]-grad[:,:3])))
        finite = np.stack([(field(points+np.eye(3)[a]*eps,t,camera,high)-field(points-np.eye(3)[a]*eps,t,camera,high))/(2*eps) for a in range(3)],axis=-1)
        bound_ratio = np.max(np.abs(np.sum(finite*rays,axis=-1))/grad[:,3])
        for step in [.1,.2,.4]:
            q = points+step*rays
            directional = (field(q+eps*rays,t,camera,high)-field(q-eps*rays,t,camera,high))/(2*eps)
            bound_ratio = max(bound_ratio,float(np.max(np.abs(directional)/grad[:,3])))
        # Retain original six references; add central 3x3 including exact axis
        # for odd grids. Scan whole forward interval, not merely near GPU hit.
        indices = set(np.linspace(0,w*h-1,6,dtype=int).tolist())
        indices.update((h//2+dy)*w+w//2+dx for dy in [-1,0,1] for dx in [-1,0,1])
        references = []
        for index in sorted(indices):
            distances = np.arange(0,hits[index,0]+1,.003)
            values = field(camera+distances[:,None]*rays[index],t,camera,high)
            crossings = np.flatnonzero(values[:-1]*values[1:]<0)
            if not len(crossings):
                references.append({'ray':index,'missing_reference':True})
                continue
            k = crossings[0]
            lo,hi,lv = distances[k],distances[k+1],values[k]
            for _ in range(24):
                mid = (lo+hi)/2
                mv = field(camera+mid*rays[index],t,camera,high)
                if mv*lv>0: lo,lv = mid,mv
                else: hi = mid
            difference = float(abs((lo+hi)/2-hits[index,0]))
            root_errors.append(difference)
            references.append({'ray':index,'axis':bool(w%2 and h%2 and index==(h//2)*w+w//2),
                               'gpu_depth':hits[index,0],'reference_depth':(lo+hi)/2,'difference':difference})
        scalar = np.abs(field(points,t,camera,high)-hits[:,3])
        summary = {'z':z,'time':t,'high':high,'width':w,'height':h,'rays':len(i),
                   'misses':int(np.sum(hits[:,1]!=1)), 'max_iterations':float(hits[:,2].max()),
                   'max_gradient_error':float(np.max(np.abs(finite-grad[:,:3]))),
                   'max_bound_ratio':float(bound_ratio),'max_field_cpu_gpu_difference':float(scalar.max()),
                   'actual_points_field_difference':float(np.max(np.abs(field(actual,t,camera,high)-hits[:,3]))),
                   'worst_scalar_ray':int(scalar.argmax()),'references':references,
                   'gpu_three_readbacks_seconds':case['gpu_three_readbacks_seconds']}
        discrepancies=np.flatnonzero(np.max(abs(finite-grad[:,:3]),axis=1)>.005)
        summary.update({'max_all_leaf_scalar_error':leaf_scalar_error,
            'max_all_leaf_gradient_error':leaf_gradient_error,
            'max_csg_replay_error':csg_error,'max_saved_gradient_replay_error':replay_error,
            'composite_fd_discrepancies':[{'ray':int(j),'error':float(np.max(abs(finite[j]-grad[j,:3]))),'expanded_leaf_values':jets[j,:,3].tolist(),'selected_leaf':EXPANDED_KEYS[int(selected_ids[j])],'selected_one_sided_gradient':selected[j,:3].tolist()} for j in discrepancies]})
        summary.update({'selected_leaf_counts':{key:int(np.sum(selected_ids==i)) for i,key in enumerate(EXPANDED_KEYS)},
            'expanded_jet_replay_error':expanded_replay_error,'aperture_replay_error':aperture_replay_error})
        summary.update({'lower_scalar_error':lower_scalar_error,'lower_gradient_error':lower_gradient_error,
            'maximum_gpu_lower_minus_full':domination})
        summary.update({'cheap_scalar_error':cheap_scalar_error,'cheap_gradient_error':cheap_gradient_error,
            'cheap_full_jet_error':cheap_full_error,'count_invariants_passed':count_valid,
            'mean_cheap_calls':float(counts[:,0].mean()),'mean_full_trace_calls':float(counts[:,1].mean()),
            'mean_certified_skips':float(counts[:,2].mean()),'mean_refine_calls':float(counts[:,3].mean()),
            'gpu_four_readbacks_seconds':case['gpu_four_readbacks_seconds']})
        summary['passed'] = (cheap_scalar_error<.001 and cheap_gradient_error<.005
                             and cheap_full_error<.00001 and count_valid and lower_scalar_error<.001 and lower_gradient_error<.005 and domination<=0 and summary['misses']==0 and leaf_gradient_error<.005
                             and leaf_scalar_error<.001 and csg_error==0 and replay_error==0
                             and expanded_replay_error==0 and aperture_replay_error==0
                             and summary['max_bound_ratio']<=1.001 and summary['max_field_cpu_gpu_difference']<.001
                             and all(not r.get('missing_reference') and r['difference']<.03 for r in references))
        summaries.append(summary)
    out = {'method':'New v35 actual float GLSL rays plus five smooth-base and eleven signed/offset smooth-leaf jets at saved actual roots. Independent float64 scalar/leaf FD; exact float32 CSG selection and original normal replay. Composite FD disagreements retained at creases, not a unique-normal assertion. Original six plus central3x3 dense .003 first-crossing references, even/odd grids, HIGH/LOW, entry/deep, times2.4077/3.5242/4/4.895/8/221/900. Sampled evidence only; no universal convergence, filtering, realism or performance proof.',
           'limits':{'gradient':.005,'bound_ratio':1.001,'scalar':.001,'root':.03},
           'files':{name:digest(HERE/name) for name in ['continuum.js','trip.js','continuum-v25.js','continuum-v35-candidate.js','build_centre_v35.py','centre-v35-bound-design.json','centre-v35-fixture-integrity.json','gpu_csg_v35.py','runtime_centre_v35.py','cost_lifecycle_v35.py','centre-v35-bounds-check.json','centre-v35-gpu-started.json','gpu_probe_v35_leaves.html','gpu_probe_v35_candidate.html','probe_numeric_candidate_v35.py','field_centre_v35.py','numeric-candidate-v35-raw.json']},
           'errors':errors,'cases':summaries,'rays':sum(s['rays'] for s in summaries),
           'reference_rays':len(root_errors),'max_reference_difference':max(root_errors,default=None)}
    out['files'].update(journal.hashes())
    fixture_gate()
    out['passed'] = len(cases)==48 and sum(s['rays'] for s in summaries)==75996 and not errors and all(s['passed'] for s in summaries) and len(root_errors)==48*15
    atomic_json(destination,out)
    print(json.dumps({k:v for k,v in out.items() if k not in ['files','cases']}) ,flush=True)
    print(json.dumps({'failed_cases':[{k:v for k,v in s.items() if k not in ['references','composite_fd_discrepancies']} for s in summaries if not s['passed']], 'composite_fd_discrepancies':sum(len(s['composite_fd_discrepancies']) for s in summaries)}),flush=True)
    assert out['passed']

if __name__ == '__main__':
    one_shot('gpu', main)
