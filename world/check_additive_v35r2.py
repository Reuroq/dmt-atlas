"""Static integration, synthetic transport/joins and actual foreground failure fixtures."""
import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
import additive_runtime_v35r2 as r
import additive_evidence_v35r2 as e
import root_reference_contract_v35r2 as contract


def rejected(callback):
    try:
        callback()
    except (AssertionError,ValueError,KeyError,TypeError,FileNotFoundError,FileExistsError,IndexError):
        return True
    raise AssertionError('Adversarial input accepted')


def node_hash(node):
    return hashlib.sha256(ast.dump(node).encode()).hexdigest()


def source_checks():
    recipes=r.read(r.PREFIX+'-derivation.json')
    require=r.require
    for item in recipes:
        target=(r.HERE/item['target']).read_text()
        require(hashlib.sha256(target.encode()).hexdigest()==item['target_sha256'])
        restored=target
        for old,new in reversed(item['edits']):
            require(restored.count(new)==1)
            restored=restored.replace(new,old,1)
        require(restored==(r.HERE/item['source']).read_text())
        require(hashlib.sha256(restored.encode()).hexdigest()==item['source_sha256'])
    original=ast.parse((r.HERE/'probe_numeric_candidate_v35r2.py').read_text())
    successor=ast.parse((r.HERE/'numeric_additive_v35r2.py').read_text())
    def assignment(tree,target):
        nodes=[n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(ast.unparse(t)==target for t in n.targets)]
        require(len(nodes)==1);return nodes[0]
    full=assignment(original,"summary['passed']")
    require(ast.dump(full)==ast.dump(assignment(successor,"summary['passed']")))
    nonroot=assignment(successor,"summary['non_reference_checks_passed']")
    require(ast.dump(nonroot)==ast.dump(e.nonroot_expression()))
    require(ast.dump(ast.BoolOp(op=ast.And(),values=nonroot.values+[full.values[-1]]))==ast.dump(full))
    def reference_loop(tree):
        return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and ast.unparse(n.target)=='index'
                    and ast.unparse(n.iter)=='sorted(indices)')
    scan=copy.deepcopy(reference_loop(successor))
    class StripScan(ast.NodeTransformer):
        def visit_Assign(self,node):
            names=[ast.unparse(t) for t in node.targets]
            if any(n=='scan' or n=='step' or n.startswith("step[") for n in names):return None
            return self.generic_visit(node)
        def visit_Expr(self,node):
            call=ast.unparse(node)
            if call.startswith('scans.record(') or call.startswith("scan['steps'].append("):return None
            return self.generic_visit(node)
    scan=StripScan().visit(scan)
    require(ast.dump(scan)==ast.dump(reference_loop(original)), 'Original .003 scan or 24 bisections changed')
    oldroot=ast.parse((r.HERE/'audit_centre_v35r2_first_roots.py').read_text())
    newroot=ast.parse((r.HERE/'global_additive_v35r2.py').read_text())
    def main(tree):return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    def global_block(tree):
        body=main(tree).body
        start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assign) and ast.unparse(n.targets[0])=='design')
        stop=next(i for i,n in enumerate(body) if isinstance(n,ast.For))
        return copy.deepcopy(body[start:stop+1])
    block=global_block(newroot)
    loop=block[-1]
    require(ast.unparse(loop.iter)=='expected_cases()')
    require(ast.unparse(loop.body[0])=='case, old = (case_map[identity], summary_map[identity])')
    loop.target=copy.deepcopy(global_block(oldroot)[-1].target)
    loop.iter=copy.deepcopy(global_block(oldroot)[-1].iter)
    loop.body=loop.body[1:]
    class StripJournal(ast.NodeTransformer):
        def visit_Expr(self,node):
            if ast.unparse(node).startswith('journal.record('):return None
            return self.generic_visit(node)
    block=[StripJournal().visit(n) for n in block]
    require(ast.dump(ast.Module(body=block,type_ignores=[]))==ast.dump(ast.Module(body=global_block(oldroot),type_ignores=[])),
            'Independent global domain/exclusions/left-first search changed')
    require('local' not in {n.id for n in ast.walk(newroot) if isinstance(n,ast.Name)})
    # Numerically independent schedule enumeration must match the frozen source.
    grid=next(ast.literal_eval(n.iter) for n in ast.walk(original) if isinstance(n,ast.For) and ast.unparse(n.target)=='(w, h, times)')
    enumerated=[(w,h,z,t,high) for w,h,times in grid for z in (8,-6) for t in times for high in (1,0)]
    require(enumerated==r.expected_cases() and len(enumerated)==48)
    require(sum(w*h for w,h,*_ in enumerated)==75996 and len(r.expected_keys())==720)
    # HTML changes must be ONLY word transport, with shader source byte-identical.
    html_checks=0
    for suffix in ('candidate','leaves'):
        old=(r.HERE/f'gpu_probe_v35r2_{suffix}.html').read_text()
        new=(r.HERE/f'gpu_probe_additive_v35r2_{suffix}.html').read_text()
        before=old[:old.index('window.runCase=' if suffix=='candidate' else 'window.auditLeaves=')]
        require(new.startswith(before))
        script=new[new.index('<script>')+8:new.rindex('</script>')]
        child=subprocess.run(['node','--check'],input=script,text=True,capture_output=True)
        require(child.returncode==0,child.stderr);html_checks+=1
    # Persistence order is explicit in the derived source and callback wrappers.
    text=(r.HERE/'numeric_additive_v35r2.py').read_text()
    require(text.index("/raw.json', cases)")<text.index('    for case in cases:'))
    require(text.index('atomic_json(destination,out)')<text.index('finish_numeric(out, cases'))
    local=(r.HERE/'local_additive_v35r2.py').read_text()
    require(local.index('atomic_json(path,record)')<local.index('validate_local(read(path)'))
    combination=(r.HERE/'combine_additive_v35r2.py').read_text()
    require(combination.index("atomic_json(artifact('combination','joined.json')")<combination.index('combined=contract.combine'))
    return {'reversible_sources':len(recipes),'html_node_syntax_checks':html_checks,
            'legacy_predicate_ast_sha256':node_hash(full),'nonroot_ast_sha256':node_hash(nonroot),
            'legacy_scan_ast_sha256':node_hash(scan),'global_algorithm_ast_sha256':node_hash(ast.Module(body=block,type_ignores=[])),
            'cases':48,'rays':75996,'reference_keys':720}


def predicate_checks():
    summary={'cheap_scalar_error':0.,'cheap_gradient_error':0.,'cheap_full_jet_error':0.,
        'count_invariants_passed':True,'lower_scalar_error':0.,'lower_gradient_error':0.,
        'maximum_gpu_lower_minus_full':0.,'max_all_leaf_gradient_error':0.,
        'max_all_leaf_scalar_error':0.,'max_csg_replay_error':0.,'max_saved_gradient_replay_error':0.,
        'expanded_jet_replay_error':0.,'aperture_replay_error':0.,'misses':0,
        'max_bound_ratio':1.,'max_field_cpu_gpu_difference':0.}
    r.require(e.nonroot_summary(summary))
    failures=0
    for field in summary:
        bad=dict(summary)
        bad[field]=False if field=='count_invariants_passed' else 10
        r.require(not e.nonroot_summary(bad),field);failures+=1
    # Preserve the legacy tolerance but do NOT use it as the new exact gate.
    summary['cheap_full_jet_error']=.000001
    r.require(e.nonroot_summary(summary))
    for field in ('cheap_scalar_error','max_bound_ratio','misses'):
        rejected(lambda field=field:e.nonroot_summary(dict(summary,**{field:True})));failures+=1
    return failures


def transport_checks():
    import numpy as np
    from gpu_csg_v35r2 import BASE_KEYS,EXPANDED_KEYS,expand_jets,replay
    w,h,z,t,high=r.expected_cases()[0];n=w*h
    base=np.zeros((n,5,4),dtype=np.float32)
    base[:,:,0]=np.float32(-0.0);base[:,:,3]=[4,-2,-3,.2,-.7]
    expanded=expand_jets(base);a,b,selected,_=replay(expanded)
    arrays=dict(zip(BASE_KEYS,[base[:,i,:] for i in range(5)]))
    arrays.update(zip(EXPANDED_KEYS,[expanded[:,i,:] for i in range(11)]))
    arrays.update(apertureA=a,apertureB=b,composed=selected,cheapF=expanded[:,0,:],cheapA=expanded[:,1,:],cheapB=expanded[:,6,:])
    leafwords={name:array.copy().view(np.uint32).ravel().tolist() for name,array in arrays.items()}
    case={'width':w,'height':h,'z':z,'time':t,'high':high,'leaves':{name:a.ravel().tolist() for name,a in arrays.items()}}
    case['leaves']['words']=leafwords;case['words']={}
    for name in ('hits','gradientSlope','points','counts'):
        array=selected.copy() if name=='gradientSlope' else np.zeros((n,4),dtype=np.float32)
        case[name]=array.ravel().tolist();case['words'][name]=array.view(np.uint32).ravel().tolist()
    r.require(all(e.transport(case).values()))
    bad=copy.deepcopy(case);bad['leaves']['words']['cheapF'][0]=0
    r.require(e.transport(bad)['exact_cheap_full_passed'] is False, 'Signed zero must differ')
    negatives=1
    for mutate in (
        lambda c:c['words']['hits'].pop(),
        lambda c:c['words']['points'].__setitem__(0,True),
        lambda c:c['words']['counts'].__setitem__(0,2**32),
        lambda c:c['words']['hits'].__setitem__(0,0x7fc00001),
        lambda c:c['points'].__setitem__(0,None),
        lambda c:c['points'].__setitem__(0,1),
        lambda c:c['leaves']['words'].pop('childAxial'),
    ):
        bad=copy.deepcopy(case);mutate(bad);rejected(lambda:e.transport(bad));negatives+=1
    # Exercise the actual JS ArrayBuffer mechanism through JSON, including -0/subnormal.
    values=[0,0x80000000,1,0x007fffff,0x00800000,0x3f800001,0x7f7fffff,0xff7fffff]
    js='const u=new Uint32Array('+json.dumps(values)+');const f=new Float32Array(u.buffer);process.stdout.write(JSON.stringify({floats:Array.from(f),words:Array.from(new Uint32Array(f.buffer))}));'
    child=subprocess.run(['node','-e',js],text=True,capture_output=True)
    r.require(child.returncode==0,child.stderr)
    result=json.loads(child.stdout);r.require(result['words']==values)
    e.words(result['floats'],result['words'],len(values))
    return {'negative_cases':negatives,'node_word_patterns':len(values),'field_samples':0}


def join_and_local_checks():
    from check_root_reference_contract_v35r2 import synthetic_record
    from local_additive_v35r2 import build_record
    import local_additive_v35r2 as local_module
    keys=r.expected_keys()
    records=[{'key':list(k)} for k in keys]
    r.bijection(keys,records,lambda x:x['key'])
    for bad in (records[:-1],records+[records[0]],records[:-1]+[records[0]],records[:-1]+[{'key':[1,2,3,4,5,6]}]):
        rejected(lambda bad=bad:r.bijection(keys,bad,lambda x:x['key']))
    bad=copy.deepcopy(records);bad[0]['key'][4]=True
    rejected(lambda:r.bijection(keys,bad,lambda x:x['key']))
    # New local runner executes against a synthetic oracle only, never the field.
    good=synthetic_record(keys[0]);gpu=good['gpu_depth']
    def synthetic(depth,identity,camera,ray):
        value=(depth-(10+math.sqrt(2)/1000))*(depth-(10+math.sqrt(3)/1000))
        return {'depth':depth,'full':value,'point':(camera+depth*ray).tolist(),
                'base_leaves':[value]*5,'expanded_leaves':[value]*11,'active_groups':[0,1,2],'active_leaves':list(range(11))}
    import math
    old_scalar,old_digest=local_module.scalar_record,local_module.digest
    local_module.scalar_record=synthetic;local_module.digest=lambda _: 'synthetic-not-source-proof'
    n=keys[0][0]*keys[0][1]*4;case={'hits':[gpu,1,1,0]*(n//4),'points':[0.]*n,'words':{'points':[0]*n}}
    try:
        record=build_record(keys[0],case,good['legacy'])
    finally:
        local_module.scalar_record=old_scalar;local_module.digest=old_digest
    r.require(e.validate_local(record,replay_oracle=False))
    r.require(len(record['local']['brackets'])==2)
    mutations=(
        lambda r:r['local']['full_records'][0]['expanded_leaves'].pop(),
        lambda r:r['local']['brackets'][0]['full_steps'][0]['midpoint'].update(full=42),
        lambda r:r['local']['brackets'][0]['full_steps'].pop(),
        lambda r:r['local']['brackets'].pop(),
        lambda r:r['local']['samples'][0].__setitem__(1,0),
    )
    # Leaf shape is validated independently of the oracle in the saved replay path.
    negatives=0
    for mutate in mutations:
        bad=copy.deepcopy(record);mutate(bad)
        rejected(lambda:e.validate_local(bad,replay_oracle=False));negatives+=1
    joined=[]
    for identity in keys:
        item=copy.deepcopy(good);item['key']=list(identity);item['legacy']['ray']=identity[-1];joined.append(item)
    result=contract.combine(keys,joined)
    r.require(result['additive_reference_contract_passed'] and not result['numeric_passed'])
    independent=good['independent']
    r.require(e.global_valid(independent,gpu))
    global_negatives=0
    for mutate in (
        lambda x:x.update(passed=False), lambda x:x.update(unresolved=[{'lo':0}]),
        lambda x:x.update(difference=False), lambda x:x.update(difference=0),
        lambda x:x['first_bracket'].__setitem__(2,-1),
        lambda x:x['first_bracket'].__setitem__(1,x['first_bracket'][0]+1e-6),
        lambda x:x['first_bracket'].__setitem__(0,float('nan')),
    ):
        bad=copy.deepcopy(independent);mutate(bad)
        r.require(not e.global_valid(bad,gpu));global_negatives+=1
    return {'join_negative_cases':5,'local_negative_cases':negatives,
            'global_negative_cases':global_negatives,'complete_synthetic_join':720}


def lifecycle_checks():
    """Real child exits against synthetic gates; no numerical worker is launched."""
    import run_additive_v35r2_once as launcher
    root=r.HERE/(r.PREFIX+'-static-fixtures');root.mkdir()
    runtime=(r.HERE/'additive_runtime_v35r2.py').read_bytes()
    launch_source=(r.HERE/'run_additive_v35r2_once.py').read_bytes()
    old_here,old_eligibility,old_argv,old_gate=r.HERE,r.eligibility,sys.argv[:],r.fixture_gate
    results=[]
    callbacks={
        'success':"r.atomic_json(r.artifact('bounds','result.json'),{'passed':True})",
        'false-result':"r.atomic_json(r.artifact('bounds','result.json'),{'passed':False})",
        'exception':"raise RuntimeError('synthetic failure')",
        'partial':"(r.directory('bounds')/'raw.json.pending').write_text('partial');raise RuntimeError('synthetic partial')",
        'signal':"import os,signal;os.kill(os.getpid(),signal.SIGTERM)",
        'late-exit':"r.atomic_json(r.artifact('bounds','result.json'),{'passed':True})",
    }
    try:
        for label,callback in callbacks.items():
            here=root/label;here.mkdir();r.HERE=here
            (here/'additive_runtime_v35r2.py').write_bytes(runtime)
            (here/'run_additive_v35r2_once.py').write_bytes(launch_source)
            (here/r.MANIFEST).write_text('{}')
            script="import additive_runtime_v35r2 as r\nr.eligibility=lambda stage:{}\nr.fixture_gate=lambda:{}\ndef callback():\n    "+callback+"\nr.worker('bounds',callback)\n"
            if label=='late-exit':script+='raise SystemExit(7)\n'
            (here/r.SCRIPTS['bounds']).write_text(script)
            r.eligibility=lambda stage:{};sys.argv=['synthetic-launcher','bounds']
            code=launcher.main()
            r.require((code==0)==(label=='success'))
            if label=='success':r.stage_receipt('bounds')
            else:rejected(lambda:r.stage_receipt('bounds'))
            rejected(launcher.main)  # Existing successful OR failed/partial name cannot rerun.
            results.append({'scenario':label,'actual_exit':r.read(r.artifact('bounds','exit.json'))['actual_exit']})
        r.HERE=root/'success'
        receipt=r.read(r.artifact('bounds','exit.json'))
        (r.directory('bounds')/'result.json').write_text('{"passed":false}')
        rejected(lambda:r.stage_receipt('bounds'))
        # Restore the successful fixture bytes exactly, retaining mutation proof separately.
        (r.directory('bounds')/'result.json').write_text('{"passed":true}\n')
        r.require(r.inventory('bounds',('exit.json',))==receipt['files'])
        r.stage_receipt('bounds')
        r.fixture_gate=lambda:{}
        r.eligibility=old_eligibility
        r.require(set(r.eligibility('numerical'))=={'bounds'})
        for stage in ('local','global','combination'):
            rejected(lambda stage=stage:r.eligibility(stage))
        # Missing fresh numerical readiness cannot be replaced by legacy baseline PASS.
        (r.HERE/'numeric-candidate-v35r2-check.json').write_text('{"passed":true}')
        rejected(lambda:r.eligibility('global'))
        # Falsified actual-exit bool must not be treated as numeric zero.
        exit_path=r.directory('bounds')/'exit.json';original=exit_path.read_bytes()
        bad=copy.deepcopy(receipt);bad['actual_exit']=False;exit_path.write_text(json.dumps(bad))
        rejected(lambda:r.stage_receipt('bounds'));exit_path.write_bytes(original)
    finally:
        r.HERE=old_here;r.eligibility=old_eligibility;sys.argv=old_argv;r.fixture_gate=old_gate
    return {'actual_foreground_children':results,'replay_rejections':6,'tamper_rejections':1,
            'eligibility_rejections':4,'boolean_exit_rejections':1,
            'synthetic_gate_override':True,'field_samples':0,'browser_runs':0}


def check():
    result={'source':source_checks(),'nonroot_negative_cases':predicate_checks(),
            'transport':transport_checks(),'join_local':join_and_local_checks(),'lifecycle':lifecycle_checks()}
    r.require('field_centre_v35r2' not in sys.modules, 'Static suite imported a field module')
    result.update(static_passed=True,field_samples=0,browser_runs=0,numeric_passed=False)
    return result
