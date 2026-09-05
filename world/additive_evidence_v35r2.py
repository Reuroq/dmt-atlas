"""Saved-evidence assessment; field imports occur only in explicit local replay."""
import ast
import math
import struct
from pathlib import Path
import root_reference_contract_v35r2 as contract
from additive_runtime_v35r2 import (HERE, require, read, digest, atomic_json, artifact,
    expected_cases, expected_keys, bijection, key, stage_receipt)


def finite_tree(value):
    if isinstance(value,dict):
        return all(finite_tree(v) for v in value.values())
    if isinstance(value,list):
        return all(finite_tree(v) for v in value)
    return not isinstance(value,float) or math.isfinite(value)


def words(values, raw, count):
    require(len(values)==len(raw)==count, 'Transport shape')
    require(all(type(v) is int and 0<=v<=0xffffffff for v in raw), 'Uint32 words required')
    decoded=[struct.unpack('<f',struct.pack('<I',v))[0] for v in raw]
    require(all(type(v) in (int,float) and math.isfinite(v) for v in values), 'Nonfinite float transport')
    require(all(math.isfinite(v) for v in decoded), 'Nonfinite word transport')
    # JSON may lose -0. Authoritative words, not float JSON, carry its sign.
    require(decoded==values, 'Float/word transport disagreement')
    return decoded


def transport(case):
    import numpy as np
    from gpu_csg_v35r2 import BASE_KEYS, EXPANDED_KEYS, expand_jets, replay
    require(key(case) in expected_cases())
    require(finite_tree(case))
    n=case['width']*case['height']*4
    names=('hits','gradientSlope','points','counts')
    require(set(case['words'])==set(names))
    for name in names:
        words(case[name],case['words'][name],n)
    leaves=case['leaves']
    keys=BASE_KEYS+EXPANDED_KEYS+['apertureA','apertureB','composed','cheapF','cheapA','cheapB']
    require(set(leaves)==set(keys+['words']) and set(leaves['words'])==set(keys))
    for name in keys:
        words(leaves[name],leaves['words'][name],n)
    exact=all(leaves['words'][a]==leaves['words'][b] for a,b in
              [('cheapF','parentF'),('cheapA','parentAxial'),('cheapB','childAxial')])
    # cheapB is the lower B aperture axial leaf; cheapF/A/B order is frozen.
    def array(name):
        return np.asarray(leaves['words'][name],dtype=np.uint32).view(np.float32).reshape(-1,4)
    base=np.stack([array(k) for k in BASE_KEYS],axis=1)
    expanded=np.stack([array(k) for k in EXPANDED_KEYS],axis=1)
    a,b,selected,_=replay(expanded)
    same=lambda x,y:bool(np.array_equal(x.view(np.uint32),y.view(np.uint32)))
    exact_replay=(same(expand_jets(base),expanded) and same(a,array('apertureA'))
                  and same(b,array('apertureB')) and same(selected,array('composed'))
                  and same(selected[:,:3].copy(),np.asarray(case['words']['gradientSlope'],dtype=np.uint32).view(np.float32).reshape(-1,4)[:,:3].copy()))
    return {'transport_passed':True,'exact_cheap_full_passed':exact,'exact_csg_replay_passed':exact_replay}


def nonroot_expression():
    source=ast.parse((HERE/'probe_numeric_candidate_v35r2.py').read_text())
    predicate=next(n.value for n in ast.walk(source) if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Subscript) and ast.unparse(t)=="summary['passed']" for t in n.targets))
    return ast.BoolOp(op=ast.And(),values=predicate.values[:-1])


def nonroot_summary(summary):
    # Transfer EVERY original conjunct, not a manually shortened acceptance list.
    names={'cheap_scalar_error':'cheap_scalar_error','cheap_gradient_error':'cheap_gradient_error',
        'cheap_full_error':'cheap_full_jet_error','count_valid':'count_invariants_passed',
        'lower_scalar_error':'lower_scalar_error','lower_gradient_error':'lower_gradient_error',
        'domination':'maximum_gpu_lower_minus_full','leaf_gradient_error':'max_all_leaf_gradient_error',
        'leaf_scalar_error':'max_all_leaf_scalar_error','csg_error':'max_csg_replay_error',
        'replay_error':'max_saved_gradient_replay_error','expanded_replay_error':'expanded_jet_replay_error',
        'aperture_replay_error':'aperture_replay_error'}
    expr=nonroot_expression()
    required={n.id for n in ast.walk(expr) if isinstance(n,ast.Name)}
    require(required==set(names)|{'summary'}, 'Nonroot predicate transfer drift')
    for name in names.values():
        if name=='count_invariants_passed':
            require(type(summary[name]) is bool)
        else:
            require(contract.finite(summary[name]))
    require(contract.finite(summary['max_bound_ratio']) and contract.finite(summary['max_field_cpu_gpu_difference']))
    require(type(summary['misses']) is int)
    namespace={name:summary[field] for name,field in names.items()}
    namespace['summary']=summary
    return bool(eval(compile(ast.fix_missing_locations(ast.Expression(expr)),'<frozen-nonroot>','eval'),{'__builtins__':{}},namespace))


def references(cases):
    result=[]
    for case in cases:
        identity=key(case)
        for reference in case['references']:
            require(type(reference['ray']) is int)
            result.append({'key':list(identity)+( [reference['ray']] ), 'legacy':reference})
    return bijection(expected_keys(),result,lambda r:r['key'])


def validate_scan(scan, legacy, gpu):
    import numpy as np
    require(finite_tree(scan))
    distances=np.arange(0,gpu+1,.003).tolist()
    require(scan['distances']==distances and len(scan['values'])==len(distances))
    require(all(contract.finite(v) for v in scan['values']))
    values=scan['values']
    crossings=[i for i in range(len(values)-1) if values[i]*values[i+1]<0]
    if not crossings:
        require(legacy=={'ray':scan['key'][-1],'missing_reference':True} and scan['steps']==[])
        return
    require('missing_reference' not in legacy and len(scan['steps'])==24)
    i=crossings[0];lo,hi,lv=distances[i],distances[i+1],values[i]
    for step in scan['steps']:
        require(step['before']==[lo,hi,lv])
        mid=(lo+hi)/2;mv=step['value']
        require(step['mid']==mid and contract.finite(mv))
        if mv*lv>0:lo,lv=mid,mv
        else:hi=mid
        require(step['after']==[lo,hi,lv])
    require(legacy['gpu_depth']==gpu and legacy['reference_depth']==(lo+hi)/2)
    require(legacy['difference']==abs((lo+hi)/2-gpu))


def numeric_assessment(legacy, cases):
    case_map=bijection(expected_cases(),cases,key)
    summaries=bijection(expected_cases(),legacy['cases'],key)
    refs=references(legacy['cases'])
    require(legacy['errors']==[] and finite_tree(legacy))
    require(sum(c['width']*c['height'] for c in cases)==legacy['rays']==75996)
    scans=[read(str(p.relative_to(HERE)))['scan'] for p in sorted((HERE/artifact('numerical','scans')).glob('*.json'))]
    scan_map=bijection(expected_keys(),scans,lambda s:s['key'])
    exact=[]
    for identity in expected_cases():
        summary=summaries[identity]
        require(summary['rays']==identity[0]*identity[1])
        recalculated=nonroot_summary(summary)
        require(type(summary['non_reference_checks_passed']) is bool and summary['non_reference_checks_passed']==recalculated)
        old_root=all(not r.get('missing_reference') and r['difference']<.03 for r in summary['references'])
        require(type(summary['passed']) is bool and summary['passed']==(recalculated and old_root))
        exact.append(transport(case_map[identity]))
    for identity in expected_keys():
        gpu=case_map[identity[:5]]['hits'][4*identity[-1]]
        validate_scan(scan_map[identity],refs[identity]['legacy'],gpu)
    found=[r['legacy'] for r in refs.values() if not r['legacy'].get('missing_reference')]
    old_pass=all(c['passed'] for c in summaries.values()) and len(found)==720
    require(legacy['passed'] is old_pass and legacy['reference_rays']==len(found))
    ready=(all(nonroot_summary(c) for c in summaries.values()) and
           all(all(v is True for v in record.values()) for record in exact))
    return {'non_reference_checks_passed':ready,'original_fixed_grid_passed':old_pass,
            'exact_transport':exact,'reference_rays':720,'rays':75996,'cases':48,
            'numeric_passed':False,'root_certification_ready':False}


def finish_numeric(legacy, cases, scans, journal):
    # Both legacy verdict and raw GPU/scan data have been durably saved already.
    require(read(artifact('numerical','legacy-check.json'))==legacy)
    result=numeric_assessment(legacy,cases)
    result['legacy_sha256']=digest(artifact('numerical','legacy-check.json'))
    result['raw_sha256']=digest(artifact('numerical','raw.json'))
    result['scan_hashes']=scans.hashes()
    result['browser_hashes']=journal.hashes()
    atomic_json(artifact('numerical','result.json'),result)
    return result


def joined_inputs():
    raw=bijection(expected_cases(),read(artifact('numerical','raw.json')),key)
    legacy=references(read(artifact('numerical','legacy-check.json'))['cases'])
    return raw,legacy


def geometry(identity, gpu_depth):
    import numpy as np
    w,h,z,t,high,index=identity
    camera=np.array([0,1.7,z])
    ray=np.array([((index%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,
                  ((index//w+.5)/h*2-1)*np.tan(np.radians(34)),-1])
    ray/=np.linalg.norm(ray)
    return camera,ray


def scalar_record(depth, identity, camera, ray):
    import numpy as np
    from field_centre_v35r2 import field, smooth_parts, expanded_leaves, compose_expanded
    _,_,_,t,high,_=identity
    point=camera+depth*ray
    base=smooth_parts(point,t,camera,high)
    leaves=expanded_leaves(base)
    full=float(field(point,t,camera,high))
    # Store all tying branches, not a false unique active derivative at a crease.
    groups=[float(max(leaves[:5])),float(max(leaves[5:10])),float(leaves[10])]
    active_groups=[i for i,v in enumerate(groups) if v==min(groups)]
    active=[i for group in active_groups for i in
            (range(5) if group==0 else range(5,10) if group==1 else [10]) if leaves[i]==groups[group]]
    require(full==float(compose_expanded(leaves)))
    require(np.all(np.isfinite(leaves)) and math.isfinite(full))
    return {'depth':depth,'point':point.tolist(),'full':full,'base_leaves':base.tolist(),
            'expanded_leaves':leaves.tolist(),'active_groups':active_groups,'active_leaves':active}


def validate_local(record, replay_oracle=True):
    require(finite_tree(record))
    identity=tuple(record['key']);gpu=record['gpu_depth']
    require(identity in expected_keys() and contract.finite(gpu) and gpu>=.004)
    local=record['local'];samples=local['samples'];full=local['full_records']
    details=full+[s['midpoint'] for b in local['brackets'] for s in b['full_steps']]
    for detail in details:
        require(contract.finite(detail['depth']) and contract.finite(detail['full']))
        for field,size in (('point',3),('base_leaves',5),('expanded_leaves',11)):
            require(len(detail[field])==size and all(contract.finite(v) for v in detail[field]))
        for field,size in (('active_groups',3),('active_leaves',11)):
            require(detail[field] and all(type(v) is int and 0<=v<size for v in detail[field]))
            require(detail[field]==sorted(set(detail[field])))
    expected=[gpu+(i-80)*.00005 for i in range(161)]
    require(len(samples)==len(full)==161)
    for depth,sample,detail in zip(expected,samples,full):
        require(sample==[depth,detail['full']] and detail['depth']==depth)
        require(contract.finite(sample[1]) and sample[1]!=0, 'Local sampled zero unresolved')
    observed=[i for i in range(160) if contract.strict(samples[i][1],samples[i+1][1])]
    require(observed and [b['index'] for b in local['brackets']]==observed)
    require(all(contract.bracket_valid(b,samples) for b in local['brackets']))
    for bracket in local['brackets']:
        require(len(bracket['full_steps'])==24)
        lo,hi=full[bracket['index']],full[bracket['index']+1]
        for step,detail in zip(bracket['steps'],bracket['full_steps']):
            require(detail['before']==[lo,hi])
            mid=detail['midpoint']
            require([mid['depth'],mid['full']]==[step['mid'],step['value']])
            if (mid['full']>0)==(lo['full']>0):lo=mid
            else:hi=mid
            require(detail['after']==[lo,hi])
    if replay_oracle:
        camera,ray=geometry(identity,gpu)
        require(record['camera']==camera.tolist() and record['ray']==ray.tolist())
        unique=full+[s['midpoint'] for b in local['brackets'] for s in b['full_steps']]
        for detail in unique:
            require(detail==scalar_record(detail['depth'],identity,camera,ray), 'Saved local oracle replay')
    return True


def finish_global(results, journal):
    atomic_json(artifact('global','raw.json'),results)
    cases=bijection(expected_cases(),results,key)
    raw,legacy=joined_inputs()
    records=[]
    for identity in expected_cases():
        for item in cases[identity]['references']:
            records.append({'key':list(identity)+[item['ray']],'independent':item})
    all_rays=bijection(expected_keys(),records,lambda r:r['key'])
    passed=[]
    for identity in expected_keys():
        item=all_rays[identity]['independent'];gpu=raw[identity[:5]]['hits'][4*identity[-1]]
        require(item['original_reference']==legacy[identity]['legacy'] and item['gpu_depth']==gpu)
        passed.append(global_valid(item,gpu))
    out={'global_roots_passed':all(passed),'numeric_passed':False,'reference_rays':720,
         'records':records,'ray_hashes':journal.hashes(),'raw_sha256':digest(artifact('global','raw.json'))}
    atomic_json(artifact('global','result.json'),out)
    require(out['global_roots_passed'], 'Independent global result failed')


def global_valid(item,gpu):
    try:
        lo,hi,lv,hv=item['first_bracket']
        return (all(contract.finite(v) for v in (lo,hi,lv,hv,gpu,item['difference']))
                and 0<=lo<hi and hi-lo<=1e-7 and lv>0 and hv<0
                and item['difference']==abs((lo+hi)/2-gpu) and item['difference']<.03
                and item['unresolved']==[] and item['passed'] is True)
    except (ValueError,TypeError,KeyError):
        return False
