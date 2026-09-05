"""Prepare two-tier checks once; retain existing limits and add failed clock."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def save(name,source):
    assert not (HERE/name).exists(),name
    (HERE/name).write_text(source)
def change(source,old,new):
    assert source.count(old)==1,old[:100]
    return source.replace(old,new)

source=(HERE/'check_centre_v33r2_bounds.py').read_text().replace('v33r2','v33r3')
source=change(source,'analytic_bounds,lower_parts','analytic_bounds,lower_parts,cheap_parts')
source=change(source,'rng=np.random.default_rng(33002)','rng=np.random.default_rng(33003)')
source=change(source,'[4.,8.,221.,900.]','[4.,4.895,8.,221.,900.]')
source=change(source,'            free=field(p,t,camera,high,pixel)>1e-6', '''            cheap=cheap_parts(p,t,camera,pixel)
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
            free=field(p,t,camera,high,pixel)>1e-6''')
source=change(source,'            results.append(result)', '''            result.update({'cheap_scalar_equivalence':cheap_equivalence,
                'cheap_gradient_ratio':float(np.max(abs(cheap_slope)/cheap_L)),
                'cheap_curvature_ratio':float(np.max(abs(cheap_curve)/cheap_M)),
                'cheap_useful_segments':int(useful.sum()),'cheap_minimum_advanced_field':cheap_minimum,
                'clock_counts':{str(clock):int(np.sum(t==clock)) for clock in np.unique(t)}})
            result['passed'] &= (cheap_equivalence<1e-10 and result['cheap_gradient_ratio']<1
                and result['cheap_curvature_ratio']<1 and useful.sum()>0 and cheap_minimum>0)
            results.append(result)''')
save('check_centre_v33r3_bounds.py',source)

source=(HERE/'probe_numeric_candidate_v33r2.py').read_text().replace('v33r2','v33r3')
source=change(source,'compose_jets, lower_parts','compose_jets, lower_parts, cheap_parts')
source=change(source,'[(48,32,[4,8]), (49,33,[4,8,221,900])]','[(48,32,[4,4.895,8]), (49,33,[4,4.895,8,221,900])]')
source=change(source,"case['gpu_three_readbacks_seconds'] = time.monotonic()-start", "case['gpu_four_readbacks_seconds'] = time.monotonic()-start")
source=change(source,'        selected=compose_jets(jets)', '''        cheap_jets=np.stack([np.array(case['leaves'][key]).reshape(-1,4) for key in ['cheapF','cheapA','cheapB']],axis=1)
        cheap_scalar=cheap_parts(actual,t,camera)
        cheap_fd=np.stack([(cheap_parts(actual+np.eye(3)[a]*eps,t,camera)-cheap_parts(actual-np.eye(3)[a]*eps,t,camera))/(2*eps) for a in range(3)],axis=-1)
        cheap_scalar_error=float(np.max(abs(cheap_scalar-cheap_jets[:,:,3])))
        cheap_gradient_error=float(np.max(abs(cheap_fd-cheap_jets[:,:,:3])))
        cheap_full_error=float(np.max(abs(cheap_jets-np.concatenate([jets[:,:1],lower_jets[:,:2]],axis=1))))
        counts=np.array(case['counts']).reshape(-1,4)
        count_valid=bool(np.all(np.isfinite(counts)) and np.all(counts>=0)
            and np.all(counts==np.floor(counts)) and np.all(counts[:,0]==counts[:,1]+counts[:,2])
            and np.all(counts[:,0]<=hits[:,2]) and np.all(counts[:,3]<=14))
        selected=compose_jets(jets)''')
source=change(source,"        summary['passed'] = (lower_scalar_error", '''        summary.update({'cheap_scalar_error':cheap_scalar_error,'cheap_gradient_error':cheap_gradient_error,
            'cheap_full_jet_error':cheap_full_error,'count_invariants_passed':count_valid,
            'mean_cheap_calls':float(counts[:,0].mean()),'mean_full_trace_calls':float(counts[:,1].mean()),
            'mean_certified_skips':float(counts[:,2].mean()),'mean_refine_calls':float(counts[:,3].mean()),
            'gpu_four_readbacks_seconds':case['gpu_four_readbacks_seconds']})
        summary['passed'] = (cheap_scalar_error<.001 and cheap_gradient_error<.005
                             and cheap_full_error<.00001 and count_valid and lower_scalar_error''')
source=change(source,'len(root_errors)==24*15','len(root_errors)==32*15')
source=source.replace('times4/8/221/900','times4/4.895/8/221/900')
save('probe_numeric_candidate_v33r3.py',source)
source=(HERE/'audit_centre_v33r2_first_roots.py').read_text().replace('v33r2','v33r3')
source=change(source,'len(flat)==360','len(flat)==480')
source=change(source,"other_gpu_checks=not baseline['errors']", "other_gpu_checks=baseline['passed'] and not baseline['errors']")
save('audit_centre_v33r3_first_roots.py',source)
save('render_centre_v33r3.py',(HERE/'render_centre_v33r2.py').read_text().replace('v33r2','v33r3'))
print('Prepared expanded bounds/GPU/first-root gates and original HIGH renderer. None run.')
