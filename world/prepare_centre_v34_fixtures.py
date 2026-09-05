"""Prepare new v34 fixtures once. No browser or scalar field evaluation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
created = []


def read(name):
    return (HERE/name).read_text()


def save(name, value):
    with (HERE/name).open('x') as stream:
        stream.write(value)
    created.append(name)


def change(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new, 1)


def main():
    start = HERE/'centre-v34-fixture-build-started.json'
    assert not start.exists()
    prior = json.loads(read('centre-v34-offline-fixtures.json'))
    for group in ['files', 'protected', 'display']:
        for name, want in prior[group].items():
            assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == want, name
    save(start.name, json.dumps({'started': True, 'no_numerical_run': True})+'\n')
    # Candidate remains immutable. Only the reference's full trace differs.
    candidate = read('continuum-v34-candidate.js')
    call = 'fieldPartsReachShared(p,sharedJetsState,f,a,b,axA,axB,angA,angB,shellA,shellB);'
    unshared = change(candidate, call, 'fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);')
    save('continuum-v34-unshared-reference.js', unshared)
    for name in ['cost_lifecycle_v33r6.py', 'check_cost_lifecycle_v33r6.py']:
        save(name.replace('v33r6', 'v34'), read(name).replace('v33r6', 'v34'))
    probe = read('gpu_probe_v33r6_candidate.html').replace('v33r6', 'v34')
    save('gpu_probe_v34_candidate.html', probe)
    save('gpu_cost_v34_candidate.html', probe)
    save('gpu_cost_v34_parent.html', probe.replace('continuum-v34-candidate.js', 'continuum-v34-unshared-reference.js'))
    leaves = read('gpu_probe_v33r6_leaves.html').replace('v33r6', 'v34')
    old = leaves[leaves.index(' gl_FragColor='):leaves.index('\n}`;')]
    expressions = ['f', 'axA', 'angA', 'shellA', 'shellB',
        'f', 'axA', 'angA', 'offset(shellA,-.095)', 'offset(-shellA,-.095)',
        'offset(f,.3)', 'axB', 'angB', 'offset(shellB,-.062)', 'offset(-shellB,-.062)',
        'offset(f,10.)', 'a', 'b', 'compose(f,a,b,layer)', 'cheapF', 'cheapA', 'cheapB']
    expression = ' gl_FragColor='+''.join(f'probeMode<{i}.5?{e}:' for i,e in enumerate(expressions[:-1]))+expressions[-1]+';'
    leaves = change(leaves, old, expression)
    leaves = change(leaves, 'mode<15', 'mode<22')
    old_keys = "['base','apertureA','apertureB','composed','axA','axB','angA','angB','shellAp','shellAn','shellBp','shellBn','cheapF','cheapA','cheapB']"
    from gpu_csg_v34 import BASE_KEYS, EXPANDED_KEYS
    leaves = change(leaves, old_keys, json.dumps(BASE_KEYS+EXPANDED_KEYS+['apertureA','apertureB','composed','cheapF','cheapA','cheapB']))
    save('gpu_probe_v34_leaves.html', leaves)

    source = read('probe_numeric_candidate_v33r6.py').replace('v33r6', 'v34')
    source = change(source, 'from field_centre_v34 import field, parts, compose_jets, lower_parts, cheap_parts',
        'from field_centre_v34 import field, smooth_parts, expanded_leaves\n'
        'from gpu_csg_v34 import BASE_KEYS, EXPANDED_KEYS, expand_jets, replay\n'
        'from runtime_centre_v34 import fixture_gate, passed, one_shot\n'
        'from cost_lifecycle_v34 import atomic_json, Lifecycle')
    begin = source.index("    started = HERE/'centre-v34-gpu-started.json'")
    end = source.index('    errors, cases = [], []', begin)
    source = source[:begin]+'''    gate = fixture_gate()
    passed('centre-v34-bounds-check.json')
    journal = Lifecycle(HERE/'centre-v34-gpu-lifecycle')
    journal.record('browser_launch_started')
'''+source[end:]
    source = change(source, '        browser = p.chromium.launch(headless=True, args=ARGS)',
        "        browser = p.chromium.launch(headless=True, args=ARGS)\n        journal.record('browser_launched')")
    source = change(source, "                        case = page.evaluate('a=>runCase(...a)', [z,t,high,w,h])",
        "                        journal.record('case_started', width=w, height=h, z=z, time=t, high=high)\n"
        "                        case = page.evaluate('a=>runCase(...a)', [z,t,high,w,h])")
    source = change(source, '                        cases.append(case)',
        "                        journal.record('case_completed', case=case)\n                        cases.append(case)")
    source = change(source, '        browser.close()',
        "        journal.record('browser_close_started')\n        browser.close()\n        journal.record('browser_closed')")
    source = change(source, "    (HERE/'numeric-candidate-v34-raw.json').write_text(json.dumps(cases)+'\\n')",
        "    atomic_json(HERE/'numeric-candidate-v34-raw.json', cases)")
    begin = source.index('        leaf_scalar=np.stack(parts(')
    end = source.index("        counts=np.array(case['counts'])", begin)
    source = source[:begin]+'''        leaf_scalar=smooth_parts(actual,t,camera,high)
        leaf_fd=np.stack([(smooth_parts(actual+np.eye(3)[a]*eps,t,camera,high)-smooth_parts(actual-np.eye(3)[a]*eps,t,camera,high))/(2*eps) for a in range(3)],axis=-1)
        base_jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in BASE_KEYS],axis=1)
        jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in EXPANDED_KEYS],axis=1)
        lower_scalar=expanded_leaves(leaf_scalar)
        lower_fd=np.stack([(expanded_leaves(smooth_parts(actual+np.eye(3)[a]*eps,t,camera,high))-expanded_leaves(smooth_parts(actual-np.eye(3)[a]*eps,t,camera,high)))/(2*eps) for a in range(3)],axis=-1)
        lower_scalar_error=float(np.max(abs(lower_scalar-jets[:,:,3])))
        lower_gradient_error=float(np.max(abs(lower_fd-jets[:,:,:3])))
        expanded_replay_error=float(np.max(abs(expand_jets(base_jets)-jets)))
        aperture_a,aperture_b,selected,selected_ids=replay(jets)
        gpu_a=np.array(case['leaves']['apertureA'],dtype=np.float32).reshape(-1,4)
        gpu_b=np.array(case['leaves']['apertureB'],dtype=np.float32).reshape(-1,4)
        aperture_replay_error=float(max(np.max(abs(aperture_a-gpu_a)),np.max(abs(aperture_b-gpu_b))))
        domination=float(max(np.max(jets[:,1:5,3]-gpu_a[:,3,None]),np.max(jets[:,6:10,3]-gpu_b[:,3,None])))
        cheap_jets=np.stack([np.array(case['leaves'][key],dtype=np.float32).reshape(-1,4) for key in ['cheapF','cheapA','cheapB']],axis=1)
        cheap_scalar=lower_scalar[:,[0,1,6]]
        cheap_fd=lower_fd[:,[0,1,6]]
        cheap_scalar_error=float(np.max(abs(cheap_scalar-cheap_jets[:,:,3])))
        cheap_gradient_error=float(np.max(abs(cheap_fd-cheap_jets[:,:,:3])))
        cheap_full_error=float(np.max(abs(cheap_jets-jets[:,[0,1,6]])))
'''+source[end:]
    source = change(source, '        selected=compose_jets(jets)\n', '')
    source = change(source, 'leaf_scalar-jets[:,:,3]', 'leaf_scalar-base_jets[:,:,3]')
    source = change(source, 'leaf_fd-jets[:,:,:3]', 'leaf_fd-base_jets[:,:,:3]')
    source = change(source, "'actual_leaf_values':jets[j,:,3].tolist()",
        "'expanded_leaf_values':jets[j,:,3].tolist(),'selected_leaf':EXPANDED_KEYS[int(selected_ids[j])],'selected_one_sided_gradient':selected[j,:3].tolist()")
    source = change(source, "        summary.update({'lower_scalar_error'",
        "        summary.update({'selected_leaf_counts':{key:int(np.sum(selected_ids==i)) for i,key in enumerate(EXPANDED_KEYS)},\n"
        "            'expanded_jet_replay_error':expanded_replay_error,'aperture_replay_error':aperture_replay_error})\n"
        "        summary.update({'lower_scalar_error'")
    source = change(source, 'and leaf_scalar_error<.001 and csg_error==0 and replay_error==0',
        'and leaf_scalar_error<.001 and csg_error==0 and replay_error==0\n'
        '                             and expanded_replay_error==0 and aperture_replay_error==0')
    source = change(source, "'centre-v34-factoring-proof.json'", "'centre-v34-bound-design.json','centre-v34-fixture-integrity.json','gpu_csg_v34.py','runtime_centre_v34.py','cost_lifecycle_v34.py'")
    source = change(source, "'build_centre_v34.py',", "'build_centre_v34.py',")
    source = change(source, "    out['passed'] = not errors", "    out['files'].update(journal.hashes())\n    fixture_gate()\n    out['passed'] = len(cases)==48 and sum(s['rays'] for s in summaries)==75996 and not errors")
    source = change(source, "    destination.write_text(json.dumps(out,indent=2)+'\\n')", '    atomic_json(destination,out)')
    source = source[:source.index("if __name__ == '__main__':")]+"if __name__ == '__main__':\n    one_shot('gpu', main)\n"
    source = source.replace('all smooth-leaf jets', 'five smooth-base and eleven signed/offset smooth-leaf jets')
    save('probe_numeric_candidate_v34.py', source)

    audit = read('audit_centre_v33r6_first_roots.py').replace('v33r6', 'v34')
    audit = change(audit, 'from field_centre_v34 import PIXEL,parts',
        'from field_centre_v34 import PIXEL,smooth_parts,expanded_leaves,compose_expanded\n'
        'from csg_interval_v34 import enclosure\n'
        'from runtime_centre_v34 import fixture_gate,one_shot\n'
        'from cost_lifecycle_v34 import atomic_json')
    begin = audit.index('M=4321+')
    end = audit.index('\nresults=[]', begin)
    audit = audit[:begin]+'''design=json.loads((HERE/'centre-v34-bound-design.json').read_text())
H=np.array(design['declared_H'])@np.array([1.,PIXEL,PIXEL**2])
expanded_hessian=H[np.array(design['expanded_leaf_ids'])]

def composed(v):
    return compose_expanded(expanded_leaves(v))

def lower_bound(left,right,width):
    return enclosure(left,right,width,expanded_hessian)[0]
'''+audit[end:]
    audit = change(audit, 'np.stack(parts(points,t,camera,high),axis=-1)', 'smooth_parts(points,t,camera,high)')
    audit = change(audit, 'np.array(parts(camera+depth*ray,t,camera,high))', 'smooth_parts(camera+depth*ray,t,camera,high)')
    audit = change(audit, '        potential=np.flatnonzero((lower<=0)&~envelope_free)',
        '        assert np.all(np.minimum(rho[:-1],rho[1:])[~envelope_free]-.003>=4.965), "Taylor domain"\n'
        '        potential=np.flatnonzero((lower<=0)&~envelope_free)')
    audit = change(audit, 'for case,old in zip(cases,baseline[\'cases\']):',
        "assert len(cases)==len(baseline['cases'])==48\nfor case,old in zip(cases,baseline['cases']):\n"
        "    assert all(case[k]==old[k] for k in ['z','time','high','width','height'])")
    audit = change(audit, "    'field_centre_v34.py',Path(__file__).name]",
        "    'field_centre_v34.py','csg_interval_v34.py','centre-v34-bound-design.json',\n"
        "    'runtime_centre_v34.py','cost_lifecycle_v34.py','centre-v34-fixture-integrity.json',\n"
        "    'centre-v34-first-root-started.json',Path(__file__).name]")
    audit = change(audit, "OUT.write_text(json.dumps(out,indent=2)+'\\n')", 'fixture_gate()\natomic_json(OUT,out)')
    audit = audit.replace('CSG interval exclusion from smooth-leaf', 'CSG interval exclusion expanding five bases to eleven signed leaves before endpoint extrema and smooth-leaf')
    # Turn the original top-level one-shot audit into a guarded callback.
    begin = audit.index('baseline=json.loads')
    body = audit[begin:]
    body = body.replace('            global subdivisions,excluded', '            nonlocal subdivisions,excluded')
    audit = audit[:begin]+'def main():\n'+''.join('    '+line+'\n' for line in body.splitlines())
    audit += "\nif __name__ == '__main__':\n    one_shot('first-root', main)\n"
    save('audit_centre_v34_first_roots.py', audit)

    cost = read('measure_centre_v33r6_cost.py').replace('v33r6', 'v34')
    cost = change(cost, "implementation = read('centre-v34-implementation.json')",
        "from runtime_centre_v34 import fixture_gate\nimplementation = fixture_gate()")
    cost = cost.replace('continuum-v33r3-candidate.js', 'continuum-v34-unshared-reference.js')
    cost = cost.replace('centre-v34-implementation.json', 'centre-v34-fixture-integrity.json')
    cost = change(cost, "         'cost_lifecycle_v34.py', Path(__file__).name]",
        "         'cost_lifecycle_v34.py', 'runtime_centre_v34.py', Path(__file__).name]")
    cost = change(cost, "        'counts_bit_equal': old['counts'] == new['counts'],",
        "        'counts_bit_equal': old['counts'] == new['counts'],\n"
        "        'gradients_bit_equal': old['gradientSlope'] == new['gradientSlope'],\n"
        "        'points_bit_equal': old['points'] == new['points'],")
    cost = change(cost, "c['hits_bit_equal'] and c['counts_bit_equal'] and",
        "c['hits_bit_equal'] and c['counts_bit_equal'] and c['gradients_bit_equal'] and c['points_bit_equal'] and")
    cost = change(cost, 'complete = failure is None and len(pairs) == 12 and not errors',
        "events=[json.loads(p.read_text()) for p in sorted(journal.directory.glob('*.json'))]\n"
        "lifecycle_complete=(sum(e['event']=='arm_completed' for e in events)==24\n"
        "    and sum(e['event']=='arm_started' for e in events)==24\n"
        "    and any(e['event']=='browser_closed' for e in events)\n"
        "    and not any(e['event'].endswith('_failed') for e in events))\n"
        "balanced=sum(p['order']==['parent','candidate'] for p in pairs)==6 and sum(p['order']==['candidate','parent'] for p in pairs)==6\n"
        'complete = failure is None and len(pairs) == 12 and not errors and lifecycle_complete and balanced')
    cost = change(cost, "result = {'complete': complete", "fixture_gate()\nresult = {'lifecycle_complete':lifecycle_complete,'balanced_order':balanced,'complete': complete")
    cost = change(cost, "limits = ('New balanced-order", "limits = ('Identical NEW v34 geometry/march; parent means unshared reference, candidate means retained common jets. Not a v34-v33r6 speedup. New balanced-order")
    save('measure_centre_v34_cost.py', cost)
    save('centre-v34-fixture-build.json', json.dumps({'prepared': True, 'numerical_run': False,
        'files': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in created},
        'unshared_edit': {'old': call, 'new': 'fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);'}}, indent=2)+'\n')
    print(json.dumps({'prepared': True, 'created_files':len(created), 'numerical_run':False}))


if __name__ == '__main__':
    main()
