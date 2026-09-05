"""Prepare changed-marcher checks once, retaining every original gate."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def save(name,source):
    assert not (HERE/name).exists(),name
    (HERE/name).write_text(source)
def change(source,old,new):
    assert source.count(old)==1,old[:80]
    return source.replace(old,new)

source=(HERE/'check_centre_v33_bounds.py').read_text().replace('v33','v33r2')
source=source.replace('PIXEL,parts,field,analytic_bounds','PIXEL,parts,field,analytic_bounds,lower_parts')
source=change(source,'rng=np.random.default_rng(33001)', '''from field_centre_v33 import parts as original_parts
build=json.loads((HERE/'centre-v33r2-build.json').read_text())
lower_H=np.array(build['lower_H_upper'])
lower_L=np.array(analytic_bounds()['lower_L_polynomials'])
rng=np.random.default_rng(33002)''')
source=change(source,'            f,a,b=centre.T;df,da,db=slopes.T', '''            assert np.array_equal(centre,np.stack(original_parts(p,t,camera,high,pixel),axis=-1))
            low=lower_parts(p,t,camera,high,pixel)
            low_plus=lower_parts(p+eps*d,t,camera,high,pixel)
            low_minus=lower_parts(p-eps*d,t,camera,high,pixel)
            low_slope=(low_plus-low_minus)/(2*eps)
            low_curve=(low_plus-2*low+low_minus)/eps**2
            low_M=lower_H@np.array([1,pixel,pixel**2])
            low_L=lower_L@np.array([1,pixel])
            low_reach=reach(low,low_slope,low_M)
            domination=float(np.max(low-centre[:,[1,2,1,2,1,1,2,2]]))
            f,a,b=centre.T;df,da,db=slopes.T''')
source=change(source,'            step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))', '''            old_step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))
            petals=np.maximum(petals,np.max(low_reach[:,[0,2,4,5]],axis=1))
            children=np.maximum(children,np.max(low_reach[:,[1,3,6,7]],axis=1))
            step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))
            assert np.all(step>=old_step)''')
source=change(source,"                'free_samples':int(free.sum()),'min_advanced_field':minimum}", '''                'free_samples':int(free.sum()),'min_advanced_field':minimum,
                'lower_gradient_ratio':float(np.max(abs(low_slope)/low_L)),
                'lower_curvature_ratio':float(np.max(abs(low_curve)/low_M)),
                'maximum_lower_minus_full':domination,
                'improved_steps':int(np.sum(step>old_step)),
                'mean_old_step':float(old_step.mean()),'mean_new_step':float(step.mean())}''')
source=change(source,"            results.append(result)", '''            result['passed'] &= result['lower_gradient_ratio']<1 and result['lower_curvature_ratio']<1 and domination<=0
            results.append(result)''')
source=change(source,"assert max(analytic['leaf_L_constants'])<185", "assert np.all(np.array(analytic['lower_H_polynomials'])<lower_H)\nassert max(analytic['leaf_L_constants'])<185")
source=source.replace("'build_centre_candidate_v33r2.py','build_centre_v33r2_checks.py'", "'build_centre_v33r2.py','build_centre_v33r2_checks.py'")
save('check_centre_v33r2_bounds.py',source)

source=(HERE/'probe_numeric_candidate_v33.py').read_text().replace('v33','v33r2')
source=source.replace('field, parts, compose_jets','field, parts, compose_jets, lower_parts')
source=change(source,"        selected=compose_jets(jets)", '''        lower_keys=['axA','axB','angA','angB','shellAp','shellAn','shellBp','shellBn']
        lower_jets=np.stack([np.array(case['leaves'][key]).reshape(-1,4) for key in lower_keys],axis=1)
        lower_scalar=lower_parts(actual,t,camera,high)
        lower_fd=np.stack([(lower_parts(actual+np.eye(3)[a]*eps,t,camera,high)-lower_parts(actual-np.eye(3)[a]*eps,t,camera,high))/(2*eps) for a in range(3)],axis=-1)
        lower_scalar_error=float(np.max(abs(lower_scalar-lower_jets[:,:,3])))
        lower_gradient_error=float(np.max(abs(lower_fd-lower_jets[:,:,:3])))
        domination=float(np.max(lower_jets[:,:,3]-jets[:,[1,2,1,2,1,1,2,2],3]))
        selected=compose_jets(jets)''')
source=change(source,"        summary['passed'] = (summary['misses']==0", '''        summary.update({'lower_scalar_error':lower_scalar_error,'lower_gradient_error':lower_gradient_error,
            'maximum_gpu_lower_minus_full':domination})
        summary['passed'] = (lower_scalar_error<.001 and lower_gradient_error<.005 and domination<=0 and summary['misses']==0''')
source=source.replace("'build_centre_candidate_v33r2.py'", "'build_centre_v33r2.py'")
save('probe_numeric_candidate_v33r2.py',source)
save('audit_centre_v33r2_first_roots.py',(HERE/'audit_centre_v33_first_roots.py').read_text().replace('v33','v33r2'))
save('render_centre_v33r2.py',(HERE/'render_centre_v33.py').read_text().replace('v33','v33r2'))
print('Prepared new lower-leaf checks, unchanged GPU/root gates and original HIGH fixture; none run.')
