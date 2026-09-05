"""One-shot independent v32 leaf, reach, clearance and footprint samples."""
import hashlib
import json
from pathlib import Path
import numpy as np
from field_centre_v32 import PIXEL,parts,field,analytic_bounds
from fidelity import RENDER_FILES

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v32-bounds-check.json'
assert not OUT.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
protected=list(dict.fromkeys(RENDER_FILES+['data.js','fidelity-data.js',
    'fidelity-grades.json','realism-grades.json','latest.png',
    'visual-chrysanthemum.png','visual-chrysanthemum.json']))
before={n:digest(n) for n in protected}
rng=np.random.default_rng(32001)
n=6000
v=rng.normal(size=(n,3));v/=np.linalg.norm(v,axis=1)[:,None]
rho=rng.uniform(5.4,22,n)
p=v*rho[:,None];p[:,1]+=1.7;p[:,2]=-27.5-abs(p[:,2])/.85
angle=rng.uniform(-np.pi,np.pi,n//2)
p[:n//2,0]=rho[:n//2]*np.cos(angle)
p[:n//2,1]=1.7+rho[:n//2]*np.sin(angle)
p[:n//2,2]=rng.uniform(-27.8,12,n//2)
d=rng.normal(size=(n,3));d/=np.linalg.norm(d,axis=1)[:,None]
t=rng.choice([4.,8.,221.,900.],n)
eps=.001
results=[]
for pixel in [PIXEL,PIXEL*2,PIXEL*4]:
    L=16+8*pixel
    Ms=np.array([7,305,87])+np.array([1,190,65])*pixel+np.array([1,110,54])*pixel**2
    for z in [8,-6]:
        camera=np.array([0,1.7,z])
        for high in [1,0]:
            def leaves(q):
                return np.stack(parts(q,t,camera,high,pixel),axis=-1)
            centre,plus,minus=leaves(p),leaves(p+eps*d),leaves(p-eps*d)
            slopes=(plus-minus)/(2*eps)
            curvature=(plus-2*centre+minus)/eps**2
            def reach(v,deriv,M):
                r=.95*np.maximum(v,0);s=abs(deriv)
                return np.minimum(.4,2*r/np.maximum(1e-30,s+np.sqrt(s*s+2*M*r)))
            f,a,b=centre.T;df,da,db=slopes.T
            mf,ma,mb=Ms
            petals=np.maximum(reach(f,df,mf),np.maximum(reach(abs(a)-.10,np.sign(a)*da,ma),
                np.minimum(reach(.035+b,db,mb),reach(.035-b,-db,mb))))
            branches=np.maximum(reach(f+.38,df,mf),np.maximum(reach(abs(a)-.25,np.sign(a)*da,ma),reach(abs(b)-.014,np.sign(b)*db,mb)))
            step=np.minimum(np.minimum(petals,branches),reach(f+10,df,mf))
            free=field(p,t,camera,high,pixel)>1e-6
            minimum=1e9
            for fraction in [.25,.5,.75,1.]:
                values=field(p+d*(step*fraction)[:,None],t,camera,high,pixel)
                minimum=min(minimum,float(values[free].min()))
            result={'camera_z':z,'high':high,'pixelScale':pixel,'samples':n,
                'max_leaf_gradient_ratio':float(np.max(abs(slopes))/L),
                'max_leaf_curvature_ratio':float(np.max(abs(curvature)/Ms)),
                'free_samples':int(free.sum()),'min_advanced_field':minimum}
            result['passed']=result['max_leaf_gradient_ratio']<1 and result['max_leaf_curvature_ratio']<1 and minimum>=-1e-7
            results.append(result)
# Actual corridor (including side boundary), cap seam and full inner free ball.
corridor=np.column_stack([rng.uniform(-4,4,n),np.full(n,1.7),rng.uniform(-22,8,n)])
theta=rng.uniform(-np.pi,np.pi,n)
inner=np.column_stack([5.449*np.cos(theta),1.7+5.449*np.sin(theta),rng.uniform(-27.5,8,n)])
clearance=[]
for points,label in [(corridor,'walk corridor'),(inner,'rho5.449 before cap')]:
    values=field(points,t,np.array([0,1.7,8]),1)
    clearance.append({'region':label,'samples':n,'minimum_field':float(values.min()),'passed':bool(np.all(values>0))})
# Explicit Gaussian attenuation and derivative checks across footprint scale.
# This checks the filter, not a claim of alias-free visual motion at CSG rims.
delta=p-np.array([0,1.7,8]);filter_checks=[]
for k in [4,12,36]:
    weights=[]
    for pixel in [0,PIXEL,2*PIXEL,4*PIXEL]:
        q=k*pixel;w=np.exp(-.5*q*q*np.sum(delta*delta,axis=1))
        exact=-q*q*w*np.sum(delta*d,axis=1)
        wp=np.exp(-.5*q*q*np.sum((delta+eps*d)**2,axis=1))
        wm=np.exp(-.5*q*q*np.sum((delta-eps*d)**2,axis=1))
        error=float(np.max(abs((wp-wm)/(2*eps)-exact)))
        weights.append(w)
        filter_checks.append({'frequency':k,'pixelScale':pixel,'max_derivative_error':error,'passed':error<1e-7})
    assert np.all(np.diff(np.stack(weights),axis=0)<=0)
# Independently computed analytic coefficients, not shader-extracted constants.
analytic=analytic_bounds()
assert np.all(np.array(analytic['leaf_H_polynomials'])<np.array([[7,1,1],[305,190,110],[87,65,54]]))
assert max(analytic['leaf_L_constants'])<16
assert max(analytic['leaf_L_pixel'])<8
after={n:digest(n) for n in protected}
files=['continuum-v32-candidate.js','build_centre_candidate_v32.py','build_centre_v32_checks.py',
    'field_centre_v32.py','centre-v32-bounds.md',Path(__file__).name,
    'gpu_probe_v32_candidate.html','gpu_probe_v32_leaves.html','probe_numeric_candidate_v32.py']
out={'passed':all(r['passed'] for r in results+clearance+filter_checks) and before==after,
    'cases':results,'clearance':clearance,'filter':filter_checks,
    'analytic':analytic,
    'source_hashes':{n:digest(n) for n in files},'protected_before':before,'protected_after':after,
    'limitations':'Sampled smooth-leaf derivatives, four points per free-side reach, clear corridor and Gaussian filter only. Not interval proof, CSG temporal antialiasing proof, numerical GPU or realism acceptance.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'leaf_samples':len(results)*n,
    'max_gradient_ratio':max(r['max_leaf_gradient_ratio'] for r in results),
    'max_curvature_ratio':max(r['max_leaf_curvature_ratio'] for r in results),
    'minimum_advanced_field':min(r['min_advanced_field'] for r in results),
    'analytic':analytic,'clearance':clearance}))
assert out['passed']
