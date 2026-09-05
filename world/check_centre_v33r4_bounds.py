"""One-shot independent v33r4 leaf, reach, clearance and footprint samples."""
import hashlib
import json
from pathlib import Path
import numpy as np
from field_centre_v33r4 import PIXEL,parts,field,analytic_bounds,lower_parts,cheap_parts
from fidelity import RENDER_FILES

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v33r4-bounds-check.json'
assert not OUT.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
protected=list(dict.fromkeys(RENDER_FILES+['data.js','fidelity-data.js',
    'fidelity-grades.json','realism-grades.json','latest.png',
    'visual-chrysanthemum.png','visual-chrysanthemum.json']))
before={n:digest(n) for n in protected}
from field_centre_v33 import parts as original_parts
build=json.loads((HERE/'centre-v33r4-build.json').read_text())
lower_H=np.array(build['lower_H_upper'])
lower_L=np.array(analytic_bounds()['lower_L_polynomials'])
rng=np.random.default_rng(33003)
n=6000
v=rng.normal(size=(n,3));v/=np.linalg.norm(v,axis=1)[:,None]
rho=rng.uniform(5.4,22,n)
p=v*rho[:,None];p[:,1]+=1.7;p[:,2]=-27.5-abs(p[:,2])/.85
angle=rng.uniform(-np.pi,np.pi,n//2)
p[:n//2,0]=rho[:n//2]*np.cos(angle)
p[:n//2,1]=1.7+rho[:n//2]*np.sin(angle)
p[:n//2,2]=rng.uniform(-27.8,12,n//2)
d=rng.normal(size=(n,3));d/=np.linalg.norm(d,axis=1)[:,None]
t=rng.choice([2.4077,3.5242,4.,4.895,8.,221.,900.],n)
eps=.001
results=[]
for pixel in [PIXEL,PIXEL*2,PIXEL*4]:
    L=185+148*pixel
    Ms=np.array([4,388,4321])+np.array([1,522,6236])*pixel+np.array([1,468,4990])*pixel**2
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
            assert np.array_equal(centre,np.stack(original_parts(p,t,camera,high,pixel),axis=-1))
            low=lower_parts(p,t,camera,high,pixel)
            low_plus=lower_parts(p+eps*d,t,camera,high,pixel)
            low_minus=lower_parts(p-eps*d,t,camera,high,pixel)
            low_slope=(low_plus-low_minus)/(2*eps)
            low_curve=(low_plus-2*low+low_minus)/eps**2
            low_M=lower_H@np.array([1,pixel,pixel**2])
            low_L=lower_L@np.array([1,pixel])
            low_reach=reach(low,low_slope,low_M)
            domination=float(np.max(low-centre[:,[1,2,1,2,1,1,2,2]]))
            f,a,b=centre.T;df,da,db=slopes.T
            mf,ma,mb=Ms
            petals=np.maximum(reach(f,df,mf),reach(a,da,ma))
            children=np.maximum(reach(f+.3,df,mf),reach(b,db,mb))
            old_step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))
            petals=np.maximum(petals,np.max(low_reach[:,[0,2,4,5]],axis=1))
            children=np.maximum(children,np.max(low_reach[:,[1,3,6,7]],axis=1))
            step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))
            assert np.all(step>=old_step)
            cheap=cheap_parts(p,t,camera,pixel)
            cheap_plus=cheap_parts(p+eps*d,t,camera,pixel)
            cheap_minus=cheap_parts(p-eps*d,t,camera,pixel)
            cheap_slope=(cheap_plus-cheap_minus)/(2*eps)
            cheap_curve=(cheap_plus-2*cheap+cheap_minus)/eps**2
            cheap_M=np.array([mf,low_M[0],low_M[1]])
            cheap_L=np.array([analytic_bounds()['leaf_L_constants'][0]+pixel*analytic_bounds()['leaf_L_pixel'][0],low_L[0],low_L[1]])
            cheap_equivalence=float(np.max(abs(cheap-np.column_stack([f,low[:,:2]]))))
            cr=reach(cheap,cheap_slope,cheap_M)
            fast=np.minimum(np.minimum(np.maximum(cr[:,0],cr[:,1]),
                np.maximum(reach(cheap[:,0]+.3,cheap_slope[:,0],mf),cr[:,2])),
                reach(cheap[:,0]+10,cheap_slope[:,0],mf))
            useful=fast>.08
            cheap_minimum=1e9
            for fraction in [.25,.5,.75,1.]:
                advanced=field(p+d*(fast*fraction)[:,None],t,camera,high,pixel)
                cheap_minimum=min(cheap_minimum,float(advanced[useful].min()))
            assert np.all(fast<=step+1e-10), 'Cheap certificate must not exceed full MAX reach'
            assert np.all(field(p[useful],t[useful],camera,high,pixel)>0)
            free=field(p,t,camera,high,pixel)>1e-6
            minimum=1e9
            for fraction in [.25,.5,.75,1.]:
                values=field(p+d*(step*fraction)[:,None],t,camera,high,pixel)
                minimum=min(minimum,float(values[free].min()))
            result={'camera_z':z,'high':high,'pixelScale':pixel,'samples':n,
                'max_leaf_gradient_ratio':float(np.max(abs(slopes))/L),
                'max_leaf_curvature_ratio':float(np.max(abs(curvature)/Ms)),
                'free_samples':int(free.sum()),'min_advanced_field':minimum,
                'lower_gradient_ratio':float(np.max(abs(low_slope)/low_L)),
                'lower_curvature_ratio':float(np.max(abs(low_curve)/low_M)),
                'maximum_lower_minus_full':domination,
                'improved_steps':int(np.sum(step>old_step)),
                'mean_old_step':float(old_step.mean()),'mean_new_step':float(step.mean())}
            result['passed']=result['max_leaf_gradient_ratio']<1 and result['max_leaf_curvature_ratio']<1 and minimum>=-1e-7
            result['passed'] &= result['lower_gradient_ratio']<1 and result['lower_curvature_ratio']<1 and domination<=0
            result.update({'cheap_scalar_equivalence':cheap_equivalence,
                'cheap_gradient_ratio':float(np.max(abs(cheap_slope)/cheap_L)),
                'cheap_curvature_ratio':float(np.max(abs(cheap_curve)/cheap_M)),
                'cheap_useful_segments':int(useful.sum()),'cheap_minimum_advanced_field':cheap_minimum,
                'clock_counts':{str(clock):int(np.sum(t==clock)) for clock in np.unique(t)}})
            result['passed'] &= (cheap_equivalence<1e-10 and result['cheap_gradient_ratio']<1
                and result['cheap_curvature_ratio']<1 and useful.sum()>0 and cheap_minimum>0)
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
assert np.all(np.array(analytic['leaf_H_polynomials'])<np.array([[4,1,1],[388,522,468],[4321,6236,4990]]))
assert np.all(np.array(analytic['lower_H_polynomials'])<lower_H)
assert max(analytic['leaf_L_constants'])<185
assert max(analytic['leaf_L_pixel'])<148
after={n:digest(n) for n in protected}
files=['continuum-v33r4-candidate.js','build_centre_v33r4.py','build_centre_v33r4_checks.py',
    'field_centre_v33r4.py','centre-v33r4-bounds.md',Path(__file__).name,
    'gpu_probe_v33r4_candidate.html','gpu_probe_v33r4_leaves.html','probe_numeric_candidate_v33r4.py']
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
