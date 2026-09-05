"""Static-only, reversible derivation. Does not import a field or launch a browser."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREFIX='centre-v35r2-additive'


def derive(source, target, edits):
    original=(HERE/source).read_text()
    text=original
    for old,new in edits:
        assert old != new and text.count(old)==1, (target,old[:100],text.count(old))
        text=text.replace(old,new,1)
    reversed_text=text
    for old,new in reversed(edits):
        assert reversed_text.count(new)==1, (target,'reverse',new[:100])
        reversed_text=reversed_text.replace(new,old,1)
    assert reversed_text==original
    with (HERE/target).open('x') as stream:
        stream.write(text)
    return {'source':source,'target':target,'edits':edits,
            'source_sha256':hashlib.sha256(original.encode()).hexdigest(),
            'target_sha256':hashlib.sha256(text.encode()).hexdigest()}


def build():
    recipes=[]
    p=PREFIX
    # Add word transport outside the original shader/render/readback statements.
    recipes.append(derive('gpu_probe_v35r2_candidate.html','gpu_probe_additive_v35r2_candidate.html',[
        ('const output={z,time,high,width,height};','const output={z,time,high,width,height,words:{}};'),
        ("  output[['hits','gradientSlope','points','counts'][mode]]=Array.from(pixels);",
         "  output[['hits','gradientSlope','points','counts'][mode]]=Array.from(pixels);\n  output.words[['hits','gradientSlope','points','counts'][mode]]=Array.from(new Uint32Array(pixels.buffer));")]))
    leaves=(HERE/'gpu_probe_v35r2_leaves.html').read_text()
    line=next(s for s in leaves.splitlines() if s.startswith('  result[['))
    recipes.append(derive('gpu_probe_v35r2_leaves.html','gpu_probe_additive_v35r2_leaves.html',[
        ('new Float32Array(caseData.points)','new Float32Array(new Uint32Array(caseData.words.points).buffer)'),
        ('const result={};','const result={words:{}};'),
        (line,line+'\n'+line.replace('result[[','result.words[[').replace('Array.from(pixels)','Array.from(new Uint32Array(pixels.buffer))'))]))
    old=(HERE/'probe_numeric_candidate_v35r2.py').read_text()
    tree=ast.parse(old)
    predicate=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Subscript) and ast.unparse(t)=="summary['passed']" for t in n.targets))
    nonroot=ast.unparse(ast.BoolOp(op=ast.And(),values=predicate.values[:-1]))
    old_files=next(s for s in old.splitlines() if "'files':{name:digest" in s)
    new_files=old_files.replace("'centre-v35r2-bounds-check.json'",repr(p+'-bounds/result.json'))
    new_files=new_files.replace("'centre-v35r2-gpu-started.json'",repr(p+'-numerical/started.json'))
    new_files=new_files.replace("'numeric-candidate-v35r2-raw.json'",repr(p+'-numerical/raw.json'))
    new_files=new_files.replace("'probe_numeric_candidate_v35r2.py'","'numeric_additive_v35r2.py','additive_runtime_v35r2.py','additive_evidence_v35r2.py'")
    new_files=new_files.replace("'gpu_probe_v35r2_leaves.html'","'gpu_probe_additive_v35r2_leaves.html'").replace("'gpu_probe_v35r2_candidate.html'","'gpu_probe_additive_v35r2_candidate.html'")
    recipes.append(derive('probe_numeric_candidate_v35r2.py','numeric_additive_v35r2.py',[
        ('from runtime_centre_v35r2 import fixture_gate, passed, one_shot\nfrom cost_lifecycle_v35r2 import atomic_json, Lifecycle',
         'from additive_runtime_v35r2 import fixture_gate, stage_receipt, worker, atomic_json, Journal as Lifecycle\nfrom additive_evidence_v35r2 import transport, finish_numeric'),
        ("    destination = HERE/'numeric-candidate-v35r2-check.json'",f"    destination = HERE/'{p}-numerical/legacy-check.json'"),
        ("    passed('centre-v35r2-bounds-check.json')","    stage_receipt('bounds')"),
        ("    journal = Lifecycle(HERE/'centre-v35r2-gpu-lifecycle')",f"    journal = Lifecycle(HERE/'{p}-numerical/browser')\n    scans = Lifecycle(HERE/'{p}-numerical/scans')"),
        ("page.goto((HERE/'gpu_probe_v35r2_candidate.html').as_uri())","page.goto((HERE/'gpu_probe_additive_v35r2_candidate.html').as_uri())"),
        ("leaf_page.goto((HERE/'gpu_probe_v35r2_leaves.html').as_uri())","leaf_page.goto((HERE/'gpu_probe_additive_v35r2_leaves.html').as_uri())"),
        ("                        case['leaves']=leaf_page.evaluate('c=>auditLeaves(c)',case)",
         "                        journal.record('gpu_readback_saved', case=case)\n                        case['leaves']=leaf_page.evaluate('c=>auditLeaves(c)',case)\n                        journal.record('leaf_readback_saved', case=case)"),
        ("    atomic_json(HERE/'numeric-candidate-v35r2-raw.json', cases)",f"    atomic_json(HERE/'{p}-numerical/raw.json', cases)"),
        ('    for case in cases:\n        z,t,high', '    for case in cases:\n        transport(case)\n        z,t,high'),
        ('            crossings = np.flatnonzero(values[:-1]*values[1:]<0)',
         "            scan = {'key':[w,h,z,t,high,index], 'distances':distances.tolist(), 'values':values.tolist(), 'steps':[]}\n            crossings = np.flatnonzero(values[:-1]*values[1:]<0)"),
        ("                references.append({'ray':index,'missing_reference':True})", "                scans.record('legacy_scan_saved', scan=scan)\n                references.append({'ray':index,'missing_reference':True})"),
        ('                if mv*lv>0: lo,lv = mid,mv\n                else: hi = mid',
         "                step = {'before':[lo,hi,lv], 'mid':mid, 'value':float(mv)}\n                if mv*lv>0: lo,lv = mid,mv\n                else: hi = mid\n                step['after']=[lo,hi,lv]; scan['steps'].append(step)"),
        ('            difference = float(abs((lo+hi)/2-hits[index,0]))',
         "            scans.record('legacy_scan_saved', scan=scan)\n            difference = float(abs((lo+hi)/2-hits[index,0]))"),
        ("        summary['passed'] = (cheap_scalar_error", "        summary['non_reference_checks_passed'] = ("+nonroot+")\n        summary['passed'] = (cheap_scalar_error"),
        (old_files,new_files),
        ('    assert out[\'passed\']',"    result = finish_numeric(out, cases, scans, journal)\n    assert result['non_reference_checks_passed']"),
        ("    one_shot('gpu', main)","    worker('numerical', main)")]))
    bounds=(HERE/'check_centre_v35r2_bounds.py').read_text()
    entrance=bounds[bounds.index("    gate = json.loads((HERE/'centre-v35r2-fixture-integrity.json')"):bounds.index('    before =')]
    footer=bounds[bounds.index("if __name__ == '__main__':"):]
    oldhash="'centre-v35r2-bound-design.json', 'centre-v35r2-fixture-integrity.json', START.name]"
    recipes.append(derive('check_centre_v35r2_bounds.py','bounds_additive_v35r2.py',[
        ("OUT = HERE/'centre-v35r2-bounds-check.json'",f"OUT = HERE/'{p}-bounds/result.json'"),
        ("START = HERE/'centre-v35r2-bounds-started.json'",f"START = HERE/'{p}-bounds/bounds-started.json'"),
        ("FAILURE = HERE/'centre-v35r2-bounds-failure.json'",f"FAILURE = HERE/'{p}-bounds/bounds-failure.json'"),
        (entrance,"    from additive_runtime_v35r2 import fixture_gate\n    gate = fixture_gate()\n"),
        ('def save(path, value):\n    with path.open(\'x\') as stream:\n        json.dump(value, stream, indent=2)\n        stream.write(\'\\n\'); stream.flush(); os.fsync(stream.fileno())',
         'def save(path, value):\n    from additive_runtime_v35r2 import atomic_json\n    atomic_json(path, value)'),
        (oldhash,"'centre-v35r2-bound-design.json', 'centre-v35r2-fixture-integrity.json', str(START.relative_to(HERE)), 'additive_runtime_v35r2.py']"),
        (footer,"if __name__ == '__main__':\n    from additive_runtime_v35r2 import worker\n    worker('bounds', main)\n")]))
    roots=(HERE/'audit_centre_v35r2_first_roots.py').read_text()
    # The full domain, exclusions, first recursion, traversal and result stay verbatim.
    block=roots[roots.index("    design=json.loads"):roots.index('    other_gpu_checks=')]
    block=block.replace("    for case,old in zip(cases,baseline['cases']):",
        "    for identity in expected_cases():\n        case,old=case_map[identity],summary_map[identity]")
    block=block.replace('            case_results.append(result)',
        "            journal.record('independent_ray_saved', key=[w,h,z,t,high,index], result=result)\n            case_results.append(result)")
    global_text='''"""Independent global search from depth zero. No local hints are accepted."""
import json
from pathlib import Path
import numpy as np
from field_centre_v35r2 import PIXEL,smooth_parts,expanded_leaves,compose_expanded
from csg_interval_v35r2 import enclosure
from additive_runtime_v35r2 import HERE, artifact, read, worker, Journal, expected_cases, bijection, key
from additive_evidence_v35r2 import finish_global


def main():
    baseline=read(artifact('numerical','legacy-check.json'))
    cases=read(artifact('numerical','raw.json'))
    case_map=bijection(expected_cases(),cases,key)
    summary_map=bijection(expected_cases(),baseline['cases'],key)
    journal=Journal(HERE/artifact('global','rays'))
'''+block+'''    finish_global(results, journal)


if __name__=='__main__':
    worker('global', main)
'''
    # Whole-file replacement is retained with a separate exact algorithm-block audit.
    recipes.append(derive('audit_centre_v35r2_first_roots.py','global_additive_v35r2.py',[(roots,global_text)]))
    with (HERE/(PREFIX+'-derivation.json')).open('x') as stream:
        json.dump(recipes,stream,indent=2);stream.write('\n')
    print('Derived five sources, reversible; no field/browser/runtime stage')


if __name__=='__main__':
    build()
