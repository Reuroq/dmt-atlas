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
from field_centre_v31 import field, parts, compose_jets

HERE = Path(__file__).resolve().parent

def main():
    destination = HERE/'numeric-candidate-v31-check.json'
    assert not destination.exists(), 'One-shot probe already recorded'
    errors, cases = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        page = browser.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.goto((HERE/'gpu_probe_v31_candidate.html').as_uri())
        leaf_page=browser.new_page()
        leaf_page.on('pageerror',lambda e:errors.append(str(e)))
        leaf_page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        leaf_page.goto((HERE/'gpu_probe_v31_leaves.html').as_uri())
        for w,h,times in [(48,32,[4,8]), (49,33,[4,8,221,900])]:
            for z in [8,-6]:
                for t in times:
                    for high in [1,0]:
                        start = time.monotonic()
                        case = page.evaluate('a=>runCase(...a)', [z,t,high,w,h])
                        case['gpu_three_readbacks_seconds'] = time.monotonic()-start
                        case['leaves']=leaf_page.evaluate('c=>auditLeaves(c)',case)
                        cases.append(case)
                        print(f'GPU {w}x{h} z={z} t={t} high={high}: {case["gpu_three_readbacks_seconds"]:.2f}s', flush=True)
        browser.close()
    (HERE/'numeric-candidate-v31-raw.json').write_text(json.dumps(cases)+'\n')
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
        leaf_scalar=np.stack(parts(actual,t,camera,high),axis=1)
        leaf_fd=np.stack([(np.stack(parts(actual+np.eye(3)[a]*eps,t,camera,high),axis=1)-np.stack(parts(actual-np.eye(3)[a]*eps,t,camera,high),axis=1))/(2*eps) for a in range(3)],axis=-1)
        jets=np.stack([np.array(case['leaves'][key]).reshape(-1,4) for key in ['base','apertureA','apertureB']],axis=1)
        selected=compose_jets(jets)
        composed=np.array(case['leaves']['composed']).reshape(-1,4)
        leaf_scalar_error=float(np.max(abs(leaf_scalar-jets[:,:,3])))
        leaf_gradient_error=float(np.max(abs(leaf_fd-jets[:,:,:3])))
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
            'composite_fd_discrepancies':[{'ray':int(j),'error':float(np.max(abs(finite[j]-grad[j,:3]))),'actual_leaf_values':jets[j,:,3].tolist()} for j in discrepancies]})
        summary['passed'] = (summary['misses']==0 and leaf_gradient_error<.005
                             and leaf_scalar_error<.001 and csg_error==0 and replay_error==0
                             and summary['max_bound_ratio']<=1.001 and summary['max_field_cpu_gpu_difference']<.001
                             and all(not r.get('missing_reference') and r['difference']<.03 for r in references))
        summaries.append(summary)
    out = {'method':'New v31 actual float GLSL rays plus all smooth-leaf jets at saved actual roots. Independent float64 scalar/leaf FD; exact float32 CSG selection and original normal replay. Composite FD disagreements retained at creases, not a unique-normal assertion. Original six plus central3x3 dense .003 first-crossing references, even/odd grids, HIGH/LOW, entry/deep, times4/8/221/900. Sampled evidence only; no universal convergence, filtering, realism or performance proof.',
           'limits':{'gradient':.005,'bound_ratio':1.001,'scalar':.001,'root':.03},
           'files':{name:digest(HERE/name) for name in ['continuum.js','trip.js','continuum-v25.js','continuum-v31-candidate.js','build_centre_candidate_v31.py','build_centre_v31_checks.py','gpu_probe_v31_leaves.html','gpu_probe_v31_candidate.html','probe_numeric_candidate_v31.py','field_centre_v31.py','numeric-candidate-v31-raw.json']},
           'errors':errors,'cases':summaries,'rays':sum(s['rays'] for s in summaries),
           'reference_rays':len(root_errors),'max_reference_difference':max(root_errors,default=None)}
    out['passed'] = not errors and all(s['passed'] for s in summaries) and len(root_errors)==24*15
    destination.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['files','cases']}) ,flush=True)
    print(json.dumps({'failed_cases':[{k:v for k,v in s.items() if k not in ['references','composite_fd_discrepancies']} for s in summaries if not s['passed']], 'composite_fd_discrepancies':sum(len(s['composite_fd_discrepancies']) for s in summaries)}),flush=True)
    assert out['passed']

if __name__ == '__main__':
    main()
