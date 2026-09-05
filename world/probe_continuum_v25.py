"""One-shot actual GLSL GPU samples against independent double-precision field.
Isolated numerical harness, not injected journey state or visual acceptance.
"""
import json
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from verify import ARGS
from fidelity import digest

HERE=Path(__file__).resolve().parent
PIXEL=2*np.tan(np.radians(34))/800

def field(p,t,camera,high):
    p=np.asarray(p,dtype=float)
    footprint=np.linalg.norm(p-camera,axis=-1)*PIXEL
    x,y,z=p[...,0],p[...,1]-1.7,p[...,2]
    r2=x*x+y*y;cap=np.minimum(z+27.5,0)
    u=np.sqrt(r2+.2025*cap*cap)-7
    a=np.arctan2(y,x)-t*.065;pole=r2/(r2+4);cw=cap*cap/(cap*cap+4)
    warp=2.6*np.cos(.85*x)*np.cos(.85*y)+.75*np.sin(1.7*x+t*.19)*np.cos(1.7*y-t*.17)
    v=z*.72+(1.8+.22*np.sin(t*.61))*u-t*.57+cw*warp
    petal=8*a+.32*np.sin(v*.5+t*.31)
    f=u-1.18*np.sin(v+.65*pole*np.cos(petal))-.4*pole*np.cos(petal+.6*np.sin(v))
    f-=.28*cw*np.cos(1.7*x+.4*np.sin(v))*np.cos(1.7*y-.4*np.cos(v))
    chart=pole*np.sin(petal)+cw*(np.sin(.8*x)+np.cos(.8*y))
    for amplitude,fv,fc,frequency in [(.18,2.7,2,30),(.08,5.7,-4,64)]+([(.035,12.1,7,130)] if high else []):
        f-=amplitude*np.exp(-.5*(footprint*frequency)**2)*np.sin(fv*v+fc*chart)
    return f

def main():
    destination=HERE/'continuum-v25-gpu-check.json'
    assert not destination.exists(), 'One-shot probe already recorded'
    errors=[];cases=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=ARGS)
        page=browser.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        page.goto((HERE/'gpu_probe_v25.html').as_uri())
        for z in [8,-6]:
            for t in [4,8]:
                for high in [1,0]:
                    result=page.evaluate('a=>runCase(...a)',[z,t,high]);cases.append(result)
                    print(f'GPU z={z} t={t} high={high}',flush=True)
        browser.close()
    (HERE/'continuum-v25-gpu-raw.json').write_text(json.dumps(cases)+'\n')
    summaries=[];root_errors=[]
    for case in cases:
        z,t,high=case['z'],case['time'],case['high'];camera=np.array([0,1.7,z])
        w,h=case['width'],case['height'];i=np.arange(w*h)
        rays=np.stack([((i%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,
                       ((i//w+.5)/h*2-1)*np.tan(np.radians(34)),-np.ones(w*h)],axis=-1)
        rays/=np.linalg.norm(rays,axis=-1)[:,None]
        hits=np.array(case['hits']).reshape(-1,4);grad=np.array(case['gradientSlope']).reshape(-1,4)
        points=camera+rays*hits[:,0,None]
        eps=1e-4
        finite=np.stack([(field(points+np.eye(3)[axis]*eps,t,camera,high)-field(points-np.eye(3)[axis]*eps,t,camera,high))/(2*eps) for axis in range(3)],axis=-1)
        # Actual shader analytic gradients, not a second copy of its derivative.
        gradient_error=np.max(np.abs(finite-grad[:,:3]))
        bound_ratio=np.max(np.abs(np.sum(finite*rays,axis=-1))/grad[:,3])
        # Probe derivative at interior points of the NEXT bound segment too.
        for step in [.1,.2,.4]:
            q=points+step*rays
            directional=(field(q+eps*rays,t,camera,high)-field(q-eps*rays,t,camera,high))/(2*eps)
            bound_ratio=max(bound_ratio,float(np.max(np.abs(directional)/grad[:,3])))
        references=[]
        for index in np.linspace(0,w*h-1,6,dtype=int):
            distances=np.arange(0,hits[index,0]+1,.003)
            values=field(camera+distances[:,None]*rays[index],t,camera,high)
            crossings=np.flatnonzero(values[:-1]*values[1:]<0)
            if not len(crossings):
                references.append({'ray':int(index),'missing_reference':True});continue
            k=crossings[0];lo,hi=distances[k],distances[k+1];lv=values[k]
            for _ in range(24):
                mid=(lo+hi)/2;mv=field(camera+mid*rays[index],t,camera,high)
                if mv*lv>0:lo=mid;lv=mv
                else:hi=mid
            difference=float(abs((lo+hi)/2-hits[index,0]));root_errors.append(difference)
            references.append({'ray':int(index),'gpu_depth':hits[index,0],'reference_depth':(lo+hi)/2,'difference':difference})
        summary={'z':z,'time':t,'high':high,'rays':len(i),'misses':int(np.sum(hits[:,1]!=1)),
                 'max_iterations':float(hits[:,2].max()),'max_gradient_error':float(gradient_error),
                 'max_bound_ratio':float(bound_ratio),'max_field_cpu_gpu_difference':float(np.max(np.abs(field(points,t,camera,high)-hits[:,3]))),
                 'references':references}
        summaries.append(summary)
    out={'method':'Actual float GLSL rays/gradients; independent float64 finite differences and .003 first-sign-crossing references. Sparse samples, not universal convergence or visual proof. New local hit tolerance may stop short of exact roots.',
         'files':{name:digest(HERE/name) for name in ['continuum.js','continuum-v25.js','gpu_probe_v25.html','probe_continuum_v25.py','continuum-v25-gpu-raw.json']},
         'errors':errors,'cases':summaries,'rays':sum(s['rays'] for s in summaries),
         'reference_rays':len(root_errors),'max_reference_difference':max(root_errors,default=None)}
    out['passed']=not errors and all(s['misses']==0 and s['max_gradient_error']<.005 and s['max_bound_ratio']<=1.001 and s['max_field_cpu_gpu_difference']<.001 and not any(r.get('missing_reference') for r in s['references']) for s in summaries) and len(root_errors)==48 and max(root_errors)<.03
    destination.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':out['passed'],'rays':out['rays'],'max_reference_difference':out['max_reference_difference'],
                      'cases':[{k:v for k,v in s.items() if k!='references'} for s in summaries]}),flush=True)
    assert out['passed']

if __name__=='__main__':main()
