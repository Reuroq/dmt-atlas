"""One-shot all-leaf GPU audit at SAVED roots. No ray marches or renders replayed.

Nonsmooth CSG derivatives are verified from independently checked smooth jets
and exact float32 branch selection. Original composite-FD failures stay intact.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from verify import ARGS
from field_centre_v29 import parts

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v29-leaf-check.json'
assert not OUT.exists(), 'Preserve leaf-audit evidence'
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

bounds=json.loads((HERE/'centre-v29-bounds-check.json').read_text())
assert bounds['passed']
assert all(digest(n)==h for n,h in bounds['source_hashes'].items())
original=json.loads((HERE/'numeric-candidate-v29-check.json').read_text())
assert not original['passed'], 'This audit explicitly records the failed baseline'
cases=json.loads((HERE/'numeric-candidate-v29-raw.json').read_text())
assert all(digest(n)==h for n,h in original['files'].items())
protected={n:digest(n) for n in bounds['protected_after']}
assert protected==bounds['protected_after']
errors,raw,results=[],[],[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=ARGS)
    page=browser.new_page()
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.goto((HERE/'gpu_probe_v29_leaves.html').as_uri())
    for case,old in zip(cases,original['cases']):
        output=page.evaluate('c=>auditLeaves(c)',{k:case[k] for k in ['z','time','high','width','height','points']})
        raw.append(output)
        p=np.array(case['points']).reshape(-1,4)[:,:3]
        cam=np.array([0,1.7,case['z']]);t=case['time'];high=case['high'];eps=1e-4
        scalar=np.stack(parts(p,t,cam,high),axis=1)
        gradient=np.stack([(np.stack(parts(p+np.eye(3)[i]*eps,t,cam,high),axis=1)-np.stack(parts(p-np.eye(3)[i]*eps,t,cam,high),axis=1))/(2*eps) for i in range(3)],axis=-1)
        jets=np.stack([np.array(output[k]).reshape(-1,4) for k in ['base','apertureA','apertureB']],axis=1)
        f,a,b=jets[:,0],jets[:,1],jets[:,2]
        shellA=f.copy();shellA[:,:3]*=np.sign(f[:,3,None]);shellA[:,3]=abs(f[:,3])-.14
        shellB=f.copy();shellB[:,:3]*=np.sign(f[:,3,None]-2.6);shellB[:,3]=abs(f[:,3]-2.6)-.18
        first=np.where((shellA[:,3]>a[:,3])[:,None],shellA,a)
        second=np.where((shellB[:,3]>b[:,3])[:,None],shellB,b)
        backing=-f.copy();backing[:,3]+=6
        selected=np.where((second[:,3]<first[:,3])[:,None],second,first)
        selected=np.where((backing[:,3]<selected[:,3])[:,None],backing,selected)
        composed=np.array(output['composed']).reshape(-1,4)
        original_gradient=np.array(case['gradientSlope']).reshape(-1,4)[:,:3]
        # CSG threshold arithmetic above is float64 applied to float32 leaf
        # values. Report mismatches; never permit arbitrary alternate normals.
        selection_error=float(np.max(abs(selected-composed)))
        replay_error=float(np.max(abs(composed[:,:3]-original_gradient)))
        # Locate the original central-difference disagreements, rather than
        # hiding them behind the corrected smooth-leaf derivative test.
        ray_i=np.arange(len(p));w,h=case['width'],case['height']
        rays=np.stack([((ray_i%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,((ray_i//w+.5)/h*2-1)*np.tan(np.radians(34)),-np.ones(len(p))],axis=-1)
        rays/=np.linalg.norm(rays,axis=1)[:,None]
        old_points=cam+rays*np.array(case['hits']).reshape(-1,4)[:,0,None]
        from field_centre_v29 import field
        old_fd=np.stack([(field(old_points+np.eye(3)[i]*eps,t,cam,high)-field(old_points-np.eye(3)[i]*eps,t,cam,high))/(2*eps) for i in range(3)],axis=-1)
        discrepancies=np.flatnonzero(np.max(abs(old_fd-original_gradient),axis=1)>.005)
        adverse=[]
        for i in discrepancies:
            adverse.append({'ray':int(i),'old_composite_fd_error':float(np.max(abs(old_fd[i]-original_gradient[i]))),
                'inner_shell_minus_aperture':float(shellA[i,3]-a[i,3]),
                'outer_shell_minus_aperture':float(shellB[i,3]-b[i,3]),
                'verified_selected_gradient_error':float(np.max(abs(selected[i,:3]-original_gradient[i])))})
        result={k:case[k] for k in ['z','time','high','width','height']}
        result.update({'roots':len(p),'max_all_leaf_scalar_error':float(np.max(abs(jets[:,:,3]-scalar))),
            'max_all_leaf_gradient_error':float(np.max(abs(jets[:,:,:3]-gradient))),
            'max_composition_selection_error':selection_error,'max_saved_gradient_replay_error':replay_error,
            'original_composite_fd_discrepancies':adverse})
        result['passed']=(result['max_all_leaf_scalar_error']<.001 and result['max_all_leaf_gradient_error']<.005
            and selection_error<.005 and replay_error<.005 and old['misses']==0
            and old['max_bound_ratio']<=1.001 and old['max_field_cpu_gpu_difference']<.001
            and all(not r.get('missing_reference') and r['difference']<.03 for r in old['references']))
        results.append(result)
        print(json.dumps({k:v for k,v in result.items() if k!='original_composite_fd_discrepancies'}),flush=True)
    browser.close()
(HERE/'centre-v29-leaf-raw.json').write_text(json.dumps(raw)+'\n')
files=['continuum-v29-candidate.js','centre-v29-bounds-check.json','numeric-candidate-v29-check.json',
    'numeric-candidate-v29-raw.json','field_centre_v29.py','gpu_probe_v29_leaves.html',
    'centre-v29-leaf-raw.json',Path(__file__).name]
after={n:digest(n) for n in protected}
result={'passed':not errors and all(r['passed'] for r in results) and protected==after,
    'method':'Actual GPU smooth jets at all saved root coordinates, independent float64 finite differences of EVERY smooth leaf, CPU CSG selection replay using actual GPU leaf values, and agreement with original GPU composite normals. Original ray/reference evidence is reused, never rerun. CSG derivative is one selected one-sided surface normal at a crease, not a nonexistent unique gradient there.',
    'limits':original['limits'],'original_composite_fd_passed':original['passed'],
    'cases':results,'errors':errors,'source_hashes':{n:digest(n) for n in files},
    'protected_before':protected,'protected_after':after,'candidate_promoted':False,
    'limitations':'Finite-difference central stencils across a CSG crease are not analytic surface normals. The original failures remain saved. This branch-aware audit keeps scalar/gradient/bound/first-root tolerances unchanged; no visual, performance, universal numerical or original-exit pass is claimed.'}
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'errors':errors,'cases':len(results)}))
assert result['passed']
