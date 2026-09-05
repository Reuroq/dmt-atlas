"""One-shot identifier-only correction and static closure. No browser/bounds replay."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r5-implementation.json'
assert not OUT.exists()
created = []

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return (HERE / name).read_text()

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

def save(name, source):
    assert not (HERE / name).exists(), name
    (HERE / name).write_text(source)
    created.append(name)

def save_json(name, data):
    save(name, json.dumps(data, indent=2) + '\n')

def change(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new)

failure = json.loads(read('centre-v33r4-numerical-failure-integrity.json'))
for key in ['files', 'protected', 'display']:
    verify(failure[key])
assert failure['integrity_passed'] and not failure['numeric_passed']
parent = read('continuum-v33r4-candidate.js')
assert not re.search(r'\bsharedJetsState\b', parent)
candidate, count = re.subn(r'\bcommon\b', 'sharedJetsState', parent)
assert count > 0
assert re.sub(r'\bsharedJetsState\b', 'common', candidate).encode() == (HERE / 'continuum-v33r4-candidate.js').read_bytes()
save('continuum-v33r5-candidate.js', candidate)
save('field_centre_v33r5.py', read('field_centre_v33r4.py'))
assert digest('field_centre_v33r5.py') == digest('field_centre_v33r4.py') == digest('field_centre_v33r3.py')

# This callback is invoked by bundled Three r160 on failed LINK_STATUS inside
# renderer.render, before readRenderTargetPixels. No compile/prewarm render added.
guard = '''
// v33r5 fail-closed guard: shader failure aborts before any readback.
renderer.debug.checkShaderErrors=true;
renderer.debug.onShaderError=(gl,program,vertex,fragment)=>{
 throw new Error('GLSL_COMPILE_OR_LINK_FAILED: '+JSON.stringify({
  program:gl.getProgramInfoLog(program),vertex:gl.getShaderInfoLog(vertex),fragment:gl.getShaderInfoLog(fragment)}));
};
'''
fixture_proofs = {}
for stem in ['gpu_probe_v33r4_candidate.html', 'gpu_probe_v33r4_leaves.html',
             'gpu_cost_v33r4_parent.html', 'gpu_cost_v33r4_candidate.html']:
    original = read(stem)
    versioned = original.replace('v33r4', 'v33r5')
    renamed = re.sub(r'\bcommon\b', 'sharedJetsState', versioned)
    source = change(renamed, 'const target=', guard + 'const target=')
    restored = re.sub(r'\bsharedJetsState\b', 'common', source.replace(guard, '')).replace('v33r5', 'v33r4')
    assert restored == original
    name = stem.replace('v33r4', 'v33r5')
    save(name, source)
    fixture_proofs[name] = {'parent': stem, 'reversal_exact': True, 'guard_before_render': True}

numeric = read('probe_numeric_candidate_v33r4.py').replace('v33r4', 'v33r5')
numeric = change(numeric, "'build_centre_v33r5_checks.py'", "'centre-v33r5-identifier-proof.json','centre-v33r5-bounds-check.json','centre-v33r5-gpu-started.json'")
numeric = change(numeric, "    errors, cases = [], []", '''    started = HERE/'centre-v33r5-gpu-started.json'
    assert not started.exists(), 'Do not replay a partial GPU run'
    gate = json.loads((HERE/'centre-v33r5-implementation.json').read_text())
    assert gate['static_passed']
    for group in ['files', 'protected', 'display']:
        assert all(digest(HERE/n)==h for n,h in gate[group].items()), group
    started.write_text(json.dumps({'started':True,'implementation_sha256':digest(HERE/'centre-v33r5-implementation.json')})+'\\n')
    errors, cases = [], []''')
numeric = change(numeric, "                        cases.append(case)", "                        assert not errors, 'Browser errors invalidate readbacks: '+repr(errors)\n                        cases.append(case)")
numeric = change(numeric, "if __name__ == '__main__':\n    main()", '''if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        failure_path = HERE/'centre-v33r5-gpu-failure.json'
        if not failure_path.exists():
            failure_path.write_text(json.dumps({'passed':False,'failure':repr(exc),
                'readbacks_accepted':False,'action':'Hold first-roots/cost/capture; preserve this run, no replay'})+'\\n')
        raise''')
save('probe_numeric_candidate_v33r5.py', numeric)
roots = read('audit_centre_v33r4_first_roots.py').replace('v33r4', 'v33r5')
roots = change(roots, "assert all(digest(n)==h for n,h in baseline['files'].items())", "assert baseline['passed'] and not baseline['errors']\nassert all(digest(n)==h for n,h in baseline['files'].items())")
save('audit_centre_v33r5_first_roots.py', roots)
save('measure_centre_v33r5_cost.py', read('measure_centre_v33r4_cost.py').replace('v33r4', 'v33r5'))
save('render_centre_v33r5.py', read('render_centre_v33r4.py').replace('v33r4', 'v33r5'))

# Retain the prior exact v33r3 restoration as a second independent static check.
restored = re.sub(r'\bsharedJetsState\b', 'common', candidate)
for edit in reversed(json.loads(read('centre-v33r4-edits.json'))):
    restored = change(restored, edit['new'], edit['old'])
assert restored.encode() == (HERE / 'continuum-v33r3-candidate.js').read_bytes()
for anchor in ['vec4 sampleValue=vec4(0.);', 'p=ro+rd*distanceAlong;\n     float bound=',
    'float fastStep=cheapReach(p,rd,sharedJetsState);', 'distanceAlong+=fastStep;havePrevious=false;',
    'float safeStep;sampleValue=traceSample(p,rd,sharedJetsState,safeStep);',
    'float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;', '    vec3 color;']:
    assert candidate.count(anchor) == 1, anchor
for name in created + [Path(__file__).name]:
    if name.endswith('.py'):
        ast.parse(read(name), filename=name)
    elif name.endswith('.js'):
        subprocess.run(['node', '--check', str(HERE / name)], check=True)
    elif name.endswith('.html'):
        inline = re.findall(r'<script>([\s\S]*?)</script>', read(name))
        assert len(inline) == 1
        subprocess.run(['node', '--check'], input=inline[0], text=True, check=True)
# Guard contract with a failing fake GL link, not an actual shader compilation.
subprocess.run(['node'], input='const renderer={debug:{}};'+guard+'''
let readback=false, failed=false;
try { renderer.debug.onShaderError({getProgramInfoLog:()=>"bad link",getShaderInfoLog:()=>"bad shader"},0,1,2); readback=true; }
catch(e) { failed=e.message.startsWith('GLSL_COMPILE_OR_LINK_FAILED:'); }
if(!failed||readback||!renderer.debug.checkShaderErrors)process.exit(1);
''', text=True, check=True)

proof_files = ['continuum-v33r4-candidate.js', 'continuum-v33r5-candidate.js',
    'continuum-v33r3-candidate.js', 'centre-v33r4-edits.json',
    'field_centre_v33r4.py', 'field_centre_v33r5.py', Path(__file__).name]
save_json('centre-v33r5-identifier-proof.json', {
    'passed': True, 'replacement': {'from':'common','to':'sharedJetsState','whole_token_count':count},
    'candidate_token_reversal_byte_exact': True, 'v33r3_edit_reversal_byte_exact': True,
    'scalar_oracle_byte_exact': True, 'expressions_control_materials_unchanged': True,
    'fixture_reversal': fixture_proofs, 'js_ast_passed': True, 'anchors_unique': True,
    'guard_fake_link_failure_contract_passed': True, 'actual_glsl_run': False,
    'source_hashes': {n:digest(n) for n in proof_files}})
bounds = json.loads(read('centre-v33r4-bounds-check.json'))
assert bounds['passed']
verify(bounds['source_hashes'])
assert sum(c['samples'] for c in bounds['cases']) == 72000
assert sum(c['samples'] for c in bounds['clearance']) == 12000
inherited = dict(bounds)
inherited.update({'inherited': True, 'new_bounds_runs': 0,
    'inheritance_basis': 'Exact whole-token alpha-renaming reversal; unchanged scalar oracle and expressions. Prior sampled bounds only, not universal/roundoff proof.',
    'source_hashes': {**bounds['source_hashes'], **{n:digest(n) for n in [
        'centre-v33r4-bounds-check.json', 'centre-v33r4-numerical-failure-integrity.json',
        'centre-v33r5-identifier-proof.json', 'continuum-v33r5-candidate.js', 'field_centre_v33r5.py', Path(__file__).name]}}})
save_json('centre-v33r5-bounds-check.json', inherited)

next_step = ('Run probe_numeric_candidate_v33r5.py ONCE with unique log, inspect exit/receipts; '
    'only PASS permits audit_centre_v33r5_first_roots.py ONCE, then measure_centre_v33r5_cost.py ONCE. '
    'Use PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages '
    'PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. No bounds rerun. Preserve48cases/75996rays/720fixed+720interval roots; '
    'cost12balanced pairs,identical boundaries,no warmup. Hold on changed hits/counters,worse inferred prefix work '
    'or total/median paired wall cost. Close centre-v33r5-integrity.json only on numerical+cost PASS '
    '(integrity_passed,numeric_passed,capture_cost_gate_passed,files,protected); only then version-only '
    'render_centre_v33r5.py original1200x800 HIGH/90000ms ONCE. No frame-pump change,prewarm,relaxed gates or promotion on failure.')
save('centre-v33r5-implementation-review.md', '''# v33r5 implementation CLOSED — runtime pending

Only the whole-token GLSL identifier `common` became `sharedJetsState` in the
isolated candidate. Exact reverse substitution recovers v33r4 byte-for-byte;
the prior seven reverse edits still recover v33r3. Expressions, control flow,
materials, scalar oracle and renderer settings are unchanged. JS/AST and
instrumentation-anchor checks PASS. This is not an actual GLSL compilation PASS.

The four derived GPU fixtures have exactly reversible version/token edits and
an identical Three shader-error callback that throws within render before any
readback. Its fake-link failure contract passes; no browser or warmup was run.
The numerical runner persists a started receipt and holds on browser errors;
exceptions receive a separate failure receipt. Historical v33r4 evidence remains
immutable. Bounds are inherited via exact scalar/expression equivalence:
72,000 leaf/reach plus 12,000 clearance samples, zero new bounds runs.

All 48 cases / 75,996 rays / 720 fixed + 720 interval roots remain required.
The new 12-pair balanced cost runner retains its instrumentation, timing
boundaries and strict gates. No timing or speedup claim. No PNG/inspection or
promotion; latest remains labelled REJECTED GAME v32 deep-motion.

## Next

''' + next_step + '\n')
verify(failure['files'])
verify(failure['protected'])
verify(failure['display'])
assert not list(HERE.glob('diagnostic-centre-v33r5*'))
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')

readme = read('README.md')
start = readme.index('Isolated **v33r4 FAILS GLSL compilation**')
end = readme.index('No frame-pump change or limit relaxation.', start)
readme = readme[:start] + '''Isolated **v33r5 identifier-only correction is prepared**; exact reversal and
static checks PASS. v33r4 GLSL failure is preserved. Unchanged sampled bounds are
inherited, not rerun. Actual GLSL, independent roots and balanced cost gates remain
pending before any original1200x800 HIGH/90s capture. No speedup/realism claim.
See [implementation and next gates](centre-v33r5-implementation-review.md).
''' + readme[end:]
old_notes = (HERE / 'NOTES.md').read_bytes()
save('NOTES-before-centre-v33r5-implementation.md', old_notes.decode('utf-8'))
notes = old_notes.decode('utf-8-sig')
notes = change(notes, '# Active: REDIRECT4 — v33r4 numerical CLOSED; GLSL compile FAIL',
    '# Active: REDIRECT4 — v33r5 implementation CLOSED; numerical gates next')
notes = notes.split('## Exact next bounded work')[0] + '''## v33r5 implementation CLOSED — no runtime yet
- Identifier-only whole-token common→sharedJetsState in isolated candidate; exact reversal recovers v33r4 bytes,then seven prior reverse edits recover v33r3. Scalar oracle identical. Expressions/control/materials/renderer unchanged;JS/AST/anchors PASS,not actual GLSL.
- Four derived GPU fixtures add identical fail-closed shader callback inside render,before readback;fake-link contract PASS. GPU runner has persistent started/failure receipts and browser-error hold. No browser,prewarm or numerical run.
- centre-v33r5-bounds-check.json explicitly inherits v33r4 72000leaf/reach+12000clearance via exact alpha-renaming/scalar proof;zero new bounds runs. All v33r4 artifacts preserved.
- Prepared48cases/75996rays/720fixed+720interval roots and12balanced cost pairs,unchanged timing/work gates. centre-v33r5-implementation.json binds files/protected/display. No PNG/inspection/promotion;latest still REJECTED GAME v32. NOTES once,BOM preserved,prior notes archived.

## Exact next bounded work
''' + next_step + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'
(HERE / 'README.md').write_text(readme)
(HERE / 'status.txt').write_text('Isolated v33r5 implementation CLOSED:identifier-only fix,exact reversal/static PASS;bounds inherited with scalar equivalence,not rerun. GLSL/first-roots/cost PENDING;zero browser runs/PNGs. v33r4 failure preserved. No speedup,promotion or frame-pump change. latest.png remains labelled REJECTED GAME v32 deep-motion;live v25/trip18/HUD/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
(HERE / 'NOTES.md').write_text(notes, encoding='utf-8-sig')
verify(failure['files'])
verify(failure['protected'])
files = created + [Path(__file__).name, 'centre-v33r4-numerical-failure-integrity.json']
save_json(OUT.name, {'static_passed': True, 'numerical_run_count': 0, 'browser_run_count': 0,
    'new_bounds_runs': 0, 'new_images': 0, 'inspections': 0,
    'exact_reversal': True, 'exact_expression_checks': True,
    'files': {n:digest(n) for n in files}, 'protected': failure['protected'],
    'display': {n:digest(n) for n in failure['display']}, 'next': next_step})
print(json.dumps({'static_passed':True,'renamed_tokens':count,'files':len(files),
    'protected':len(failure['protected']),'browser_runs':0,'bounds_runs':0,'new_images':0}))
