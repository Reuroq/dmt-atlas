"""One-shot offline sin/cos factoring, fixture derivation and static checks."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path
from check_cost_lifecycle_v33r6 import check as check_lifecycle

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r6-build.json'
assert not OUT.exists()
created = []


def read(name):
    return (HERE / name).read_text()


def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def verify(group):
    for name, expected in group.items():
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


hold = json.loads(read('centre-v33r5-numerical-hold-integrity.json'))
assert hold['integrity_passed'] and not hold['capture_permitted']
for group in ['files', 'protected', 'display']:
    verify(hold[group])
parent = read('continuum-v33r5-candidate.js')
sin_body = re.search(r'float preciseSin\(float x\)\{\n(.*?)\n\}', parent, re.S).group(1)
cos_body = re.search(r'float preciseCos\(float x\)\{\n(.*?)\n\}', parent, re.S).group(1)
sin_expr = re.search(r' return (.*);', sin_body).group(1)
cos_expr = re.search(r' return (.*);', cos_body).group(1)
# Exactly the original reduction, fold thresholds, assignments and Horner
# expressions. The cosine sign updates do not alter the sine dependency graph.
cos_prefix = cos_body.split(' return ')[0]
sin_prefix = sin_body.split(' return ')[0]
assert cos_prefix.replace(';float s=1.;', ';').replace('{x=', 'x=').replace(';s=-1.;}', ';') == sin_prefix
helper = ('// Shared range reduction for the analytic jet; original polynomials unchanged.\n'
          'vec2 preciseSinCos(float x){\n' + cos_prefix +
          ' float sine=' + sin_expr + ';\n float cosine=' + cos_expr +
          ';\n return vec2(sine,cosine);\n}\n')
old_jc = 'vec4 jc(vec4 q){return vec4(-preciseSin(q.w)*q.xyz,preciseCos(q.w));}'
new_jc = 'vec4 jc(vec4 q){vec2 sc=preciseSinCos(q.w);return vec4(-sc.x*q.xyz,sc.y);}'
anchor = 'vec3 preciseCos(vec3 x)'
candidate = change(parent, anchor, helper + anchor)
candidate = change(candidate, old_jc, new_jc)
assert change(change(candidate, new_jc, old_jc), helper, '') == parent
assert candidate.split('   vec4 jm(', 1)[1] == parent.split('   vec4 jm(', 1)[1]
save('continuum-v33r6-candidate.js', candidate)
save_json('centre-v33r6-edits.json', [{'old': anchor, 'new': helper + anchor},
                                    {'old': old_jc, 'new': new_jc}])
save('field_centre_v33r6.py', read('field_centre_v33r5.py'))
assert digest('field_centre_v33r6.py') == digest('field_centre_v33r5.py')

# The experiment changes its shader, not its sparse-ray fixture or browser clock.
fixture_names = ['gpu_probe_v33r5_candidate.html', 'gpu_probe_v33r5_leaves.html',
                 'gpu_cost_v33r5_candidate.html', 'gpu_cost_v33r5_parent.html']
for name in fixture_names:
    source = read(name).replace('v33r5', 'v33r6')
    assert source.replace('v33r6', 'v33r5') == read(name)
    save(name.replace('v33r5', 'v33r6'), source)
for name in ['probe_numeric_candidate_v33r5.py', 'audit_centre_v33r5_first_roots.py',
             'render_centre_v33r5.py']:
    source = read(name).replace('v33r5', 'v33r6')
    source = source.replace('centre-v33r6-identifier-proof.json', 'centre-v33r6-factoring-proof.json')
    assert source.replace('centre-v33r6-factoring-proof.json', 'centre-v33r6-identifier-proof.json').replace('v33r6', 'v33r5') == read(name)
    save(name.replace('v33r5', 'v33r6'), source)

cost = read('measure_centre_v33r5_cost.py').replace('v33r5', 'v33r6')
cost_edits = []
def cost_change(old, new):
    global cost
    cost = change(cost, old, new)
    cost_edits.append({'old': old, 'new': new})

cost_change('from verify import ARGS', 'from verify import ARGS\nfrom cost_lifecycle_v33r6 import Lifecycle, atomic_json, install_signal_receipts, restore_signals')
cost_change("         Path(__file__).name]", "         'cost_lifecycle_v33r6.py', Path(__file__).name]")
cost_change("RAW.write_text(json.dumps({'started': True, 'pairs': [], 'source_hashes': source_hashes}) + '\\n')", """journal = Lifecycle(HERE / 'centre-v33r6-cost-lifecycle')
atomic_json(RAW, {'started': True, 'pairs': [], 'source_hashes': source_hashes})
journal.record('runner_started', source_hashes=source_hashes)
active = {'stage': 'browser_launch'}
old_signals = install_signal_receipts()""")
cost_change('        browser = p.chromium.launch(headless=True, args=ARGS)', "        journal.record('browser_launch_started')\n        browser = p.chromium.launch(headless=True, args=ARGS)\n        journal.record('browser_launched')")
cost_change('            page = browser.new_page()', "            active = {'stage': 'page_setup', 'arm': arm}\n            journal.record('page_setup_started', **active)\n            page = browser.new_page()")
cost_change('            pages[arm] = page', "            pages[arm] = page\n            journal.record('page_setup_completed', **active)")
old_timing = """                        start = time.monotonic()
                        case = pages[arm].evaluate('a=>runCase(...a)', [z, t, high, 49, 33])
                        case['outer_four_readbacks_seconds'] = time.monotonic() - start"""
cost_change(old_timing, """                        assert not errors, 'Browser errors invalidate this experiment: '+repr(errors)
                        active = {'stage': 'arm', 'pair': len(pairs)+1, 'arm': arm, 'time': t, 'z': z, 'high': high}
                        case = journal.arm(active, lambda: pages[arm].evaluate('a=>runCase(...a)', [z, t, high, 49, 33]))
                        assert not errors, 'Browser errors invalidate readbacks: '+repr(errors)""")
cost_change("                    RAW.write_text(json.dumps({'started': True, 'pairs': pairs, 'errors': errors,\n                                               'source_hashes': source_hashes}) + '\\n')", "                    atomic_json(RAW, {'started': True, 'pairs': pairs, 'errors': errors,\n                                      'source_hashes': source_hashes})\n                    journal.record('pair_completed', pair=len(pairs))")
cost_change('        browser.close()\nexcept Exception as exc:\n    failure = repr(exc)', """        active = {'stage': 'browser_close'}
        journal.record('browser_close_started')
        browser.close()
        journal.record('browser_closed')
except BaseException as exc:
    failure = repr(exc)
    journal.record('runner_failed', active=active, failure=failure, errors=errors)
finally:
    restore_signals(old_signals)
    atomic_json(RAW, {'started': True, 'pairs': pairs, 'errors': errors,
                      'failure': failure, 'last_active': active, 'source_hashes': source_hashes})
    journal.record('browser_phase_finished', failure=failure, complete_pairs=len(pairs), last_active=active)""")
cost_change("result = {'complete': complete", "journal.record('review_ready', complete=complete, capture_cost_gate_passed=bool(work and not_slower and unchanged))\nresult = {'complete': complete")
cost_change("'source_hashes': {**source_hashes, RAW.name: digest(RAW.name)}", "'source_hashes': {**source_hashes, **journal.hashes(), RAW.name: digest(RAW.name)}")
cost_change("OUT.write_text(json.dumps(result, indent=2) + '\\n')", 'atomic_json(OUT, result)')
cost_change("          'Prefix counts are source-level evaluation estimates, not GPU instruction counts.')", "          'Prefix counts are source-level evaluation estimates, not GPU instruction counts. '\n          'Per-arm receipt I/O is outside both timed boundaries, but can perturb between-arm host/cache/queue state. '\n          'Catchable failures are recorded; a hard kill leaves the last durable lifecycle event incomplete, with unknown cause.')")
restored = cost
for edit in reversed(cost_edits):
    restored = change(restored, edit['new'], edit['old'])
assert restored.replace('v33r6', 'v33r5') == read('measure_centre_v33r5_cost.py')
save('measure_centre_v33r6_cost.py', cost)
save_json('centre-v33r6-cost-edits.json', cost_edits)

for name in created + ['cost_lifecycle_v33r6.py', 'check_cost_lifecycle_v33r6.py', Path(__file__).name]:
    if name.endswith('.py'):
        ast.parse(read(name), filename=name)
    elif name.endswith('.js'):
        subprocess.run(['node', '--check', str(HERE / name)], check=True)
    elif name.endswith('.html'):
        inline = re.findall(r'<script>([\s\S]*?)</script>', read(name))
        assert len(inline) == 1
        subprocess.run(['node', '--check'], input=inline[0], text=True, check=True)

def js_body(body):
    return re.sub(r'\bfloat\b', 'let', body)

js = 'const TAU=6.28318530718,floor=Math.floor;\n'
js += 'function ps(x){' + js_body(sin_body) + '}\n'
js += 'function pc(x){' + js_body(cos_body) + '}\n'
js += 'function pair(x){' + js_body(helper.split('vec2 preciseSinCos(float x){\n')[1].rsplit('\n}', 1)[0]).replace('vec2(sine,cosine)', '[sine,cosine]') + '}\n'
js += '''let samples=[0,-0],seed=12345;
for(let k=-1024;k<=1024;k++)for(const eps of [-1e-10,0,1e-10])samples.push(k*1.57079632679+eps);
for(let i=0;i<20000;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;samples.push((seed/4294967296-.5)*20000);}
for(const x of samples){const p=pair(x);if(!Object.is(p[0],ps(x))||!Object.is(p[1],pc(x)))throw Error('factoring mismatch '+x);}
process.stdout.write(JSON.stringify({passed:true,samples:samples.length,bitMismatches:0,arithmetic:'JS float64; not GPU evidence'}));
'''
sampled = json.loads(subprocess.run(['node'], input=js, text=True, check=True, capture_output=True).stdout)
save_json('centre-v33r6-lifecycle-check.json', check_lifecycle())
proof_names = ['continuum-v33r5-candidate.js', 'continuum-v33r6-candidate.js',
               'centre-v33r6-edits.json', 'field_centre_v33r5.py', 'field_centre_v33r6.py', Path(__file__).name]
save_json('centre-v33r6-factoring-proof.json', {
    'passed': True, 'parent_reversal_exact': True, 'field_material_march_suffix_exact': True,
    'unchanged_scalar_oracle': True, 'reduction_fold_and_polynomials_exact': True,
    'change': 'jc uses one shared reduction/fold/q and both unchanged Horner polynomials; replaces two reductions/folds/q per jc source evaluation.',
    'limits': 'Dependency-graph equivalence for finite inputs under the same arithmetic semantics, not GPU compiler/roundoff/performance proof. Compiler may already eliminate duplicate work.',
    'sampled_double_check': sampled, 'cost_edits_reversible': True,
    'source_hashes': {n: digest(n) for n in proof_names}})
bounds = json.loads(read('centre-v33r5-bounds-check.json'))
assert bounds['passed'] and bounds['inherited']
verify(bounds['source_hashes'])
inherited = dict(bounds)
inherited.update({'inherited': True, 'new_bounds_runs': 0,
    'inheritance_basis': 'Unchanged scalar oracle and exact original sin/cos dependency graphs after common reduction factoring. Existing sampled bounds only; new GPU numerical gates still required.',
    'source_hashes': {**bounds['source_hashes'], **{n: digest(n) for n in [
        'centre-v33r5-bounds-check.json', 'centre-v33r6-factoring-proof.json', *proof_names]}}})
save_json('centre-v33r6-bounds-check.json', inherited)
for group in ['files', 'protected', 'display']:
    verify(hold[group])
result = {'static_passed': True, 'browser_runs': 0, 'new_bounds_runs': 0,
          'numeric_passed': False, 'capture_permitted': False, 'sampled_double_check': sampled,
          'files': {n: digest(n) for n in created + ['cost_lifecycle_v33r6.py', 'check_cost_lifecycle_v33r6.py', Path(__file__).name]},
          'protected': hold['protected'], 'display': hold['display'],
          'prior_hold_sha256': digest('centre-v33r5-numerical-hold-integrity.json')}
save_json(OUT.name, result)
print(json.dumps({k: v for k, v in result.items() if k not in ['files', 'protected', 'display']}))
