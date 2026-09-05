"""Offline fixture contracts. No browser, v34 field samples or numerical gates."""
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from gpu_csg_v34 import BASE_KEYS, EXPANDED_KEYS, contract_checks

HERE = Path(__file__).resolve().parent


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def read(name):
    return (HERE/name).read_text()


def runtime_contracts():
    import runtime_centre_v34 as runtime
    import run_centre_v34_gate_once as launcher
    checks = []
    old_runtime = runtime.HERE, runtime.fixture_gate, runtime.digest
    old_launcher = launcher.HERE, launcher.GATES, launcher.fixture_gate, launcher.passed, launcher.digest
    old_argv = sys.argv
    try:
        with tempfile.TemporaryDirectory(prefix='v34-fixture-contract-', dir=HERE) as directory:
            target = Path(directory)
            runtime.HERE = launcher.HERE = target
            runtime.fixture_gate = launcher.fixture_gate = lambda: {}
            runtime.digest = launcher.digest = lambda name: hashlib.sha256((target/name).read_bytes()).hexdigest()
            (target/'centre-v34-fixture-integrity.json').write_text('{}\n')
            def fail():
                raise RuntimeError('synthetic receipt contract')
            try:
                runtime.one_shot('synthetic', fail)
            except RuntimeError:
                pass
            else:
                raise AssertionError('failure swallowed')
            start = target/'centre-v34-synthetic-started.json'
            failed = target/'centre-v34-synthetic-failure.json'
            assert start.exists() and json.loads(failed.read_text())['passed'] is False
            frozen = start.read_bytes(), failed.read_bytes()
            try:
                runtime.one_shot('synthetic', lambda: None)
            except AssertionError:
                pass
            else:
                raise AssertionError('partial attempt replayed')
            assert frozen == (start.read_bytes(), failed.read_bytes())
            checks.append('new runtime failure durable; partial retry rejected without overwrite')
            (target/'fake.py').write_text("print('synthetic child; no field or browser')\nraise SystemExit(7)\n")
            launcher.GATES = {'synthetic': ('fake.py', [])}
            sys.argv = ['launcher', 'synthetic']
            assert launcher.main() == 7
            exit_file = target/'run-centre-v34-synthetic-once-exit.json'
            receipt = json.loads(exit_file.read_text())
            assert receipt['actual_exit'] == 7
            assert receipt['log_sha256'] == launcher.digest('run-centre-v34-synthetic-once.log')
            try:
                launcher.main()
            except AssertionError:
                pass
            else:
                raise AssertionError('foreground launch replayed')
            checks.append('foreground actual nonzero child exit and log hash saved; repeat blocked')
            launcher.GATES = {'blocked': ('fake.py', [('failed.json', 'source_hashes')])}
            launcher.passed = lambda *args: (_ for _ in ()).throw(AssertionError('failed prerequisite'))
            sys.argv = ['launcher', 'blocked']
            try:
                launcher.main()
            except AssertionError:
                pass
            else:
                raise AssertionError('prerequisite bypassed')
            assert not list(target.glob('*blocked*'))
            checks.append('failed prerequisite prevents launch/log creation')
    finally:
        runtime.HERE, runtime.fixture_gate, runtime.digest = old_runtime
        launcher.HERE, launcher.GATES, launcher.fixture_gate, launcher.passed, launcher.digest = old_launcher
        sys.argv = old_argv
    return checks


def check():
    build = json.loads(read('centre-v34-fixture-build.json'))
    assert build['prepared'] and not build['numerical_run']
    assert all(digest(n) == h for n,h in build['files'].items())
    names = list(build['files'])+['gpu_csg_v34.py','runtime_centre_v34.py',
        'run_centre_v34_gate_once.py','prepare_centre_v34_fixtures.py',Path(__file__).name]
    parsed = []
    for name in names:
        if name.endswith('.py'):
            ast.parse(read(name),filename=name); parsed.append(name)
    # Inherit completed lifecycle evidence through exact source equivalence.
    for name in ['cost_lifecycle', 'check_cost_lifecycle']:
        assert read(name+'_v34.py').replace('v34','v33r6') == read(name+'_v33r6.py')
    inherited = json.loads(read('centre-v33r6-lifecycle-check.json'))
    assert inherited['passed']
    candidate, reference = read('continuum-v34-candidate.js'), read('continuum-v34-unshared-reference.js')
    edit = build['unshared_edit']
    assert candidate.count(edit['old']) == 1
    assert candidate.replace(edit['old'],edit['new'],1) == reference
    trace = candidate[candidate.index('   vec4 traceSample('):candidate.index('   void main(){')]
    assert trace.count(edit['old']) == 1
    candidate_html = read('gpu_cost_v34_candidate.html')
    assert candidate_html == read('gpu_probe_v34_candidate.html')
    assert read('gpu_cost_v34_parent.html').replace('continuum-v34-unshared-reference.js','continuum-v34-candidate.js') == candidate_html
    parent_fixture = read('gpu_probe_v33r6_candidate.html').replace('v33r6','v34')
    assert candidate_html == parent_fixture, 'Instrumentation and clock boundaries changed'
    # Extract the material's literal shader; run only JS string transformations.
    fragment = re.search(r'fragmentShader:`([\s\S]*?)`',candidate).group(1)
    assert '${' not in fragment
    anchors = ['uniform float time,high,pixelScale;', 'vec4 sampleValue=vec4(0.);',
        'p=ro+rd*distanceAlong;\n     float bound=', 'float fastStep=cheapReach(p,rd,sharedJetsState);',
        'distanceAlong+=fastStep;havePrevious=false;',
        'float safeStep;sampleValue=traceSample(p,rd,sharedJetsState,safeStep);',
        'float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;', '    vec3 color;', '   void main(){']
    assert all(fragment.count(a)==1 for a in anchors)
    shaders, guarded = {}, []
    for name in ['gpu_probe_v34_candidate.html','gpu_probe_v34_leaves.html',
                 'gpu_cost_v34_candidate.html','gpu_cost_v34_parent.html']:
        html = read(name)
        inline = re.findall(r'<script>([\s\S]*?)</script>',html)
        assert len(inline)==1
        subprocess.run(['node','--check'],input=inline[0],text=True,check=True,capture_output=True)
        guard = html[html.index('renderer.debug.checkShaderErrors'):html.index('const target=')]
        js = 'const renderer={debug:{}};'+guard+'''
let readback=false,failed=false;
try{renderer.debug.onShaderError({getProgramInfoLog:()=>"bad link",getShaderInfoLog:()=>"bad shader"},0,1,2);readback=true;}
catch(e){failed=e.message.startsWith('GLSL_COMPILE_OR_LINK_FAILED:');}
if(!failed||readback)throw Error('guard did not fail closed');
'''
        subprocess.run(['node'],input=js,text=True,check=True,capture_output=True)
        guarded.append(name)
        start = 'let shader=' if name.endswith('leaves.html') else 'let fragment='
        transform = html[html.index(start):html.index('material.needsUpdate=true;')]
        original = fragment if name!='gpu_cost_v34_parent.html' else re.search(r'fragmentShader:`([\s\S]*?)`',reference).group(1)
        js = 'const material={fragmentShader:'+json.dumps(original)+'};\n'+transform+'\nprocess.stdout.write(material.fragmentShader);'
        shaders[name] = subprocess.run(['node'],input=js,text=True,check=True,capture_output=True).stdout
    assert shaders['gpu_cost_v34_candidate.html'] == shaders['gpu_probe_v34_candidate.html']
    assert shaders['gpu_cost_v34_candidate.html'].replace(edit['old'],edit['new'],1) == shaders['gpu_cost_v34_parent.html']
    instrumented = shaders['gpu_probe_v34_candidate.html']
    assert all(instrumented.count(s)==1 for s in ['iterations+=1.;','cheapCalls+=1.;','fullCalls+=1.;','certifiedSkips+=1.;','refineCalls+=1.;'])
    leaves = read('gpu_probe_v34_leaves.html')
    assert 'mode<22' in leaves
    keys = re.search(r'result\[(\[.*?\])\[mode\]\]',leaves).group(1)
    assert json.loads(keys) == BASE_KEYS+EXPANDED_KEYS+['apertureA','apertureB','composed','cheapF','cheapA','cheapB']
    expressions = ['f','axA','angA','shellA','shellB','f','axA','angA',
        'offset(shellA,-.095)','offset(-shellA,-.095)','offset(f,.3)','axB','angB',
        'offset(shellB,-.062)','offset(-shellB,-.062)','offset(f,10.)',
        'a','b','compose(f,a,b,layer)','cheapF','cheapA','cheapB']
    output = re.search(r'gl_FragColor=(.*?);',shaders['gpu_probe_v34_leaves.html']).group(1)
    assert output == ''.join(f'probeMode<{i}.5?{e}:' for i,e in enumerate(expressions[:-1]))+expressions[-1]
    for name in ['continuum-v34-candidate.js','continuum-v34-unshared-reference.js']:
        subprocess.run(['node','--check',str(HERE/name)],check=True,capture_output=True)
    # Enumerate the runner's literal schedule without evaluating the field.
    tree = ast.parse(read('probe_numeric_candidate_v34.py'))
    grids = [ast.literal_eval(n.iter) for n in ast.walk(tree) if isinstance(n,ast.For)
             and isinstance(n.target,ast.Tuple) and [a.id for a in n.target.elts]==['w','h','times']]
    assert len(grids)==1
    cases = [(w,h,t,z,high) for w,h,times in grids[0] for z in [8,-6] for t in times for high in [1,0]]
    assert len(cases)==48 and sum(w*h for w,h,*_ in cases)==75996
    references = 0
    for w,h,*_ in cases:
        import numpy as np
        ids=set(np.linspace(0,w*h-1,6,dtype=int).tolist())
        ids.update((h//2+dy)*w+w//2+dx for dy in [-1,0,1] for dx in [-1,0,1])
        assert len(ids)==15
        references += len(ids)
    assert references==720
    root = read('audit_centre_v34_first_roots.py')
    assert 'enclosure(left,right,width,expanded_hessian)[0]' in root
    assert 'parts(' not in root.replace('smooth_parts(', '')
    assert all(s in root for s in ['hi-lo<=1e-7','difference<.03','not unresolved','depth>=32','len(flat)==720','>=4.965'])
    assert all(s not in root for s in ['4321','6236','4990','np.maximum(f,a)'])
    cost = read('measure_centre_v34_cost.py')
    assert all(s in cost for s in ['len(pairs) == 12','len(pairs) % 2','for t in [2.4077, 3.5242, 4.895]',
        'for z in [8, -6]','for high in [1, 0]',"w['candidate_total'] <= w['parent_total']", "w['median_paired_ratio'] <= 1",
        "c['hits_bit_equal'] and c['counts_bit_equal']", 'old_counts[:, 0] + old_counts[:, 1] + old_counts[:, 3] + 1',
        'new_counts[:, 0] + new_counts[:, 3] + 1','lifecycle_complete and balanced'])
    synthetic = contract_checks()
    contracts = runtime_contracts()
    return {'static_passed': True, 'python_ast_files':parsed, 'js_syntax_files':6,
        'shader_guard_fake_failures':guarded, 'instrumented_shader_hashes':
        {n:hashlib.sha256(s.encode()).hexdigest() for n,s in shaders.items()},
        'candidate_reference_exact_single_reversal':True,'identical_cost_instrumentation':True,
        'cases':len(cases),'gpu_rays':75996,'fixed_references':references,'interval_references':720,
        'cost_pairs':12,'balanced_order':True,'synthetic_csg':synthetic,'runtime_contracts':contracts,
        'lifecycle_contracts_inherited':{'receipt':'centre-v33r6-lifecycle-check.json',
            'sha256':digest('centre-v33r6-lifecycle-check.json'),'exact_version_only_source_equivalence':True},
        'browser_runs':0,'actual_glsl_runs':0,'v34_field_samples':0,
        'limits':'JS syntax/string transformations and synthetic contracts only; actual GLSL, numerical bounds, roots, cost and realism untested.'}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
