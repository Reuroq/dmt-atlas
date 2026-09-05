"""Synthetic adversarial contracts and AST-only schedule/source inspection."""
import ast
import copy
import hashlib
import math
from pathlib import Path
import root_reference_contract_v35r2 as c

HERE = Path(__file__).resolve().parent


def source_anchors():
    gpu_name = 'probe_numeric_candidate_v35r2.py'
    root_name = 'audit_centre_v35r2_first_roots.py'
    gpu = ast.parse((HERE/gpu_name).read_text())
    roots = ast.parse((HERE/root_name).read_text())
    assignments = [n for n in ast.walk(gpu) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                           and t.value.id == 'summary' and isinstance(t.slice, ast.Constant)
                           and t.slice.value == 'passed' for t in n.targets)]
    assert len(assignments) == 1
    predicate = assignments[0].value
    assert isinstance(predicate, ast.BoolOp) and isinstance(predicate.op, ast.And)
    last = predicate.values[-1]
    assert isinstance(last, ast.Call) and isinstance(last.func, ast.Name) and last.func.id == 'all'
    assert 'missing_reference' in ast.unparse(last) and 'references' in ast.unparse(last)
    # Only the final root conjunct is separated; every other original condition
    # is carried as a complete AST expression, not a hand-selected list of gates.
    nonroot = ast.BoolOp(op=ast.And(), values=predicate.values[:-1])
    reconstructed = ast.BoolOp(op=ast.And(), values=nonroot.values+[last])
    assert ast.dump(reconstructed) == ast.dump(predicate)
    assert 'cheap_full_error < 1e-05' in ast.unparse(nonroot)
    first = [n for n in ast.walk(roots) if isinstance(n, ast.FunctionDef) and n.name == 'first']
    assert len(first) == 1
    recursion = ast.unparse(first[0])
    assert all(s in recursion for s in ('depth >= 32', 'hi - lo <= 1e-07', 'fl > 0 and fh < 0', 'if unresolved:', 'lower_bound(lv, hv, hi - lo) > 0'))
    grids = [ast.literal_eval(n.iter) for n in ast.walk(gpu) if isinstance(n, ast.For)
             and isinstance(n.target, ast.Tuple) and [v.id for v in n.target.elts] == ['w','h','times']]
    assert len(grids) == 1
    expected, rays, cases = [], 0, 0
    for w,h,times in grids[0]:
        ids = {i*(w*h-1)//5 for i in range(6)}
        ids.update((h//2+dy)*w+w//2+dx for dy in (-1,0,1) for dx in (-1,0,1))
        assert len(ids) == 15
        for z in (8,-6):
            for t in times:
                for high in (1,0):
                    cases += 1; rays += w*h
                    expected.extend((w,h,z,t,high,index) for index in sorted(ids))
    assert cases == 48 and rays == 75996 and len(expected) == len(set(expected)) == 720
    historical = [(48,32,8,4.895,0,839),(48,32,-6,8,0,745),
                  (49,33,-6,8,1,807),(49,33,-6,8,1,809)]
    assert all(key in expected for key in historical)
    sha = lambda node: hashlib.sha256(ast.dump(node).encode()).hexdigest()
    return {'gpu_source':gpu_name,'root_source':root_name,
            'full_case_predicate':ast.unparse(predicate),'full_case_predicate_ast_sha256':sha(predicate),
            'nonroot_predicate':ast.unparse(nonroot),'nonroot_predicate_ast_sha256':sha(nonroot),
            'legacy_reference_conjunct':ast.unparse(last),'global_first_recursion_ast_sha256':sha(first[0]),
            'additional_strict_gate_required':'cheap_full_jet_error == 0 plus exact binary32 replay',
            'expected_keys':[list(k) for k in expected],'historical_missing_keys':[list(k) for k in historical],
            'cases':cases,'rays':rays,'field_samples':0}


def synthetic_record(key):
    first = 10+math.sqrt(2)/1000
    second = 10+math.sqrt(3)/1000
    field = lambda x:(x-first)*(x-second)
    assert field(10)>0 and field(10.003)>0
    gpu = first+.000001
    samples = [[gpu+(i-80)*.00005,field(gpu+(i-80)*.00005)] for i in range(161)]
    brackets = []
    for index in range(160):
        lo,lv = samples[index]; hi,hv = samples[index+1]
        if not c.strict(lv,hv):
            continue
        record = {'index':index,'entering':lv>0 and hv<0,'steps':[]}
        for _ in range(24):
            mid = (lo+hi)/2; mv = field(mid)
            assert mv != 0
            step = {'before':[lo,hi,lv,hv],'mid':mid,'value':mv}
            if (mv>0)==(lv>0):lo,lv=mid,mv
            else:hi,hv=mid,mv
            step['after']=[lo,hi,lv,hv];record['steps'].append(step)
        record['final']=[lo,hi,lv,hv];brackets.append(record)
    assert len(brackets)==2 and [b['entering'] for b in brackets]==[True,False]
    lo,hi=first-2e-8,first+2e-8
    return {'key':list(key),'gpu_depth':gpu,'legacy':{'ray':key[-1],'missing_reference':True},
            'local':{'samples':samples,'brackets':brackets},
            'independent':{'passed':True,'unresolved':[],'first_bracket':[lo,hi,field(lo),field(hi)],
                           'difference':abs((lo+hi)/2-gpu)}}


def check():
    anchors=source_anchors(); keys=anchors['expected_keys']
    good=synthetic_record(keys[0]);assert c.validate_ray(good)
    mutations={
        'missing-independent':lambda r:r.pop('independent'),
        'independent-false':lambda r:r['independent'].update(passed=False),
        'unresolved-despite-pass':lambda r:r['independent'].update(unresolved=[{'lo':0}]),
        'wrong-independent-sign':lambda r:r['independent']['first_bracket'].__setitem__(2,-1),
        'wrong-independent-width':lambda r:r['independent']['first_bracket'].__setitem__(1,r['independent']['first_bracket'][0]+.00001),
        'earlier-outside-local-cell':lambda r:r['independent'].update(first_bracket=[r['gpu_depth']-.001,r['gpu_depth']-.001+5e-8,1,-1],difference=abs((r['gpu_depth']-.001+r['gpu_depth']-.001+5e-8)/2-r['gpu_depth'])),
        'claimed-difference':lambda r:r['independent'].update(difference=0),
        'boolean-difference':lambda r:r['independent'].update(difference=False),
        'nan-depth':lambda r:r.update(gpu_depth=float('nan')),
        'infinite-global':lambda r:r['independent']['first_bracket'].__setitem__(0,float('inf')),
        'sampled-zero':lambda r:r['local']['samples'][4].__setitem__(1,0),
        'boolean-sample':lambda r:r['local']['samples'][4].__setitem__(1,True),
        'missing-exit-crossing':lambda r:r['local']['brackets'].pop(),
        'duplicate-local-bracket':lambda r:r['local']['brackets'].append(copy.deepcopy(r['local']['brackets'][0])),
        'wrong-local-order':lambda r:r['local']['brackets'].reverse(),
        'wrong-local-orientation':lambda r:r['local']['brackets'][0].update(entering=False),
        'missing-refinement':lambda r:r['local']['brackets'][0]['steps'].pop(),
        'wrong-midpoint':lambda r:r['local']['brackets'][0]['steps'][0].update(mid=10),
        'refinement-zero':lambda r:r['local']['brackets'][0]['steps'][0].update(value=0),
        'wrong-refinement-transition':lambda r:r['local']['brackets'][0]['steps'][0]['after'].__setitem__(2,42),
        'wrong-final':lambda r:r['local']['brackets'][0]['final'].__setitem__(0,0),
        'truncated-grid':lambda r:r['local']['samples'].pop(),
        'changed-grid':lambda r:r['local']['samples'][4].__setitem__(0,0),
        'boolean-ray':lambda r:r['legacy'].update(ray=False),
    }
    for name,mutate in mutations.items():
        bad=copy.deepcopy(good);mutate(bad);assert not c.validate_ray(bad),name
    found=copy.deepcopy(good)
    depth=sum(found['independent']['first_bracket'][:2])/2
    found['legacy']={'ray':keys[0][-1],'reference_depth':depth,'gpu_depth':found['gpu_depth'],
                     'difference':abs(depth-found['gpu_depth'])}
    assert c.validate_ray(found)
    for name,mutate in {
        'legacy-too-far':lambda r:r['legacy'].update(reference_depth=20,difference=abs(20-r['gpu_depth'])),
        'legacy-difference-lie':lambda r:r['legacy'].update(difference=0),
        'legacy-boolean-gpu':lambda r:r['legacy'].update(gpu_depth=True),
        'legacy-false-missing-flag':lambda r:r['legacy'].update(missing_reference=False),
    }.items():
        bad=copy.deepcopy(found);mutate(bad);assert not c.validate_ray(bad),name
    records=[]
    for key in keys:
        r=copy.deepcopy(good);r['key']=key;r['legacy']['ray']=key[-1];records.append(r)
    result=c.combine(keys,records)
    assert result['additive_reference_contract_passed'] and result['numeric_passed'] is False
    assert result['original_fixed_grid_passed'] is False and len(result['legacy_missing_keys'])==720
    for name,expected,items in [
        ('missing-record',keys,records[:-1]),('duplicate-record',keys,records[:-1]+[records[0]]),
        ('extra-record',keys,records+[records[0]]),('duplicate-expected',keys[:-1]+[keys[0]],records),
        ('wrong-expected',keys[:-1]+[[1,2,3,4,5,6]],records)]:
        assert not c.combine(expected,items)['additive_reference_contract_passed'],name
    mismatch=copy.deepcopy(records[0]);mismatch['legacy']['ray']=-1
    assert not c.combine(keys,[mismatch]+records[1:])['additive_reference_contract_passed']
    return {'static_passed':True,'ray_negative_cases':28,'coverage_negative_cases':6,
            'synthetic_complete_records':720,'narrow_crossings':2,'coarse_sign_changes':0,
            'global_provenance_validated':False,'numeric_passed':False,'browser_runs':0,'field_samples':0,
            'anchors':anchors}
