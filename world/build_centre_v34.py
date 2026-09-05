"""One-shot v34 implementation assembly and static proof checks. No browser."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from field_centre_v34 import analytic_bounds

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-v34-build.json'
START = HERE/'centre-v34-build-started.json'
assert not OUT.exists() and not START.exists(), 'One-shot; preserve partial attempts'
created = []


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def verify(group):
    for name, expected in group.items():
        assert digest(name) == expected, name


def save(name, value):
    assert not (HERE/name).exists(), name
    with (HERE/name).open('x') as stream:
        stream.write(value)
    created.append(name)


def save_json(name, value):
    save(name, json.dumps(value, indent=2)+'\n')


prior = json.loads((HERE/'centre-v33r6-capture-integrity.json').read_text())
assert prior['integrity_passed'] and prior['visual_grade'] == 'GAME'
for group in ['files', 'protected', 'display']:
    verify(prior[group])
save_json(START.name, {'started': True, 'prior_capture': digest('centre-v33r6-capture-integrity.json'),
                      'builder': digest(Path(__file__).name),
                      'template': digest('centre-v34-field.glsl'),
                      'oracle': digest('field_centre_v34.py')})

calculus = analytic_bounds()
L, H = np.array(calculus['L']), np.array(calculus['H'])
# Coefficientwise conservative padding; this is NOT a GPU rounding guarantee.
declared_L, declared_H = np.ceil(1.05*L+1), np.ceil(1.05*H+1)
assert np.all(np.isfinite(L)) and np.all(np.isfinite(H))
assert np.all(L >= 0) and np.all(H >= 0)
assert np.all(declared_L > L) and np.all(declared_H > H)


def vector(values):
    return f'vec{len(values)}('+','.join(f'{x:.1f}' for x in values)+')'


def polynomial_function(name, ids):
    a = declared_H[ids]
    return (f'vec{len(ids)} {name}(){{float s=pixelScale;return '+
            '+'.join(vector(a[:, j])+['', '*s', '*s*s'][j] for j in range(3))+';}')


max_L = np.max(declared_L, axis=0)
functions = ('float raySlope(vec3 p,vec3 rd){return '+f'{max_L[0]:.1f}+{max_L[1]:.1f}*pixelScale;'+'}\n   '+
             polynomial_function('leafCurvature', [0, 3, 4])+'\n   '+
             polynomial_function('gateCurvature', [1, 2]))
template = (HERE/'centre-v34-field.glsl').read_text()
assert template.count('// @V34_BOUND_FUNCTIONS@') == 1
replacement = template.replace('// @V34_BOUND_FUNCTIONS@', functions)
parent = (HERE/'continuum-v33r6-candidate.js').read_text()
start = parent.index('   // Three smooth jets;')
end = parent.index('   vec3 spectrum(')
old = parent[start:end]
candidate = parent[:start]+replacement+parent[end:]
save('continuum-v34-candidate.js', candidate)
save_json('centre-v34-edits.json', [{'old': old, 'new': replacement}])
assert candidate.count(replacement) == 1
assert candidate.replace(replacement, old) == parent
assert candidate[:start] == parent[:start]
assert candidate.split('   vec3 spectrum(', 1)[1] == parent.split('   vec3 spectrum(', 1)[1]


def block(source, name):
    # Selected helpers contain no nested braces.
    return re.search(r'\b(?:vec4|float) '+name+r'\([^\n]*\)\{\n.*?\n   \}', source, re.S).group()


for name in ['compose', 'envelope', 'positiveReach']:
    assert block(candidate, name) == block(parent, name), name
# Full evaluation calls exactly the same cheap-part implementation.
assert replacement.count('cheapPartsShared(p,sharedJetsState,f,axA,axB);') == 2
assert not re.search(r'\b(?:r18|i18|r36|i36)\b', replacement)
assert 'positiveReach(a,' not in replacement and 'positiveReach(b,' not in replacement
assert 'jm(shell' not in replacement
trace = replacement.split('   vec4 traceSample(', 1)[1]
assert trace.count('positiveReach(') == 11
for text in ['offset(shellA,-.095)', 'offset(-shellA,-.095)',
             'offset(shellB,-.062)', 'offset(-shellB,-.062)',
             'positiveReach(axA,rd,gate.x)', 'positiveReach(axB,rd,gate.x)',
             'positiveReach(angA,rd,gate.y)', 'positiveReach(angB,rd,gate.y)',
             'positiveReach(f,rd,m.x)', 'positiveReach(offset(f,.3),rd,m.x)',
             'positiveReach(offset(f,10.),rd,m.x)']:
    assert trace.count(text) == 1, text
assert '.30*jm(offset(-cosLocal,1.),branchScale)' in replacement
assert .30*(1-.61)*(1+.24+.07) < .095+.062
assert 1-.24-.07 > 0

renderer = (HERE/'render_centre_v33r6.py').read_text().replace('v33r6', 'v34')
assert renderer.replace('v34', 'v33r6') == (HERE/'render_centre_v33r6.py').read_text()
save('render_centre_v34.py', renderer)
for name in [Path(__file__).name, 'field_centre_v34.py', 'render_centre_v34.py']:
    ast.parse((HERE/name).read_text(), filename=name)
node = subprocess.run(['node', '--check', str(HERE/'continuum-v34-candidate.js')],
                      text=True, capture_output=True)
assert node.returncode == 0, node.stderr

expanded_ids = [0, 1, 2, 3, 3, 0, 1, 2, 4, 4, 0]
save_json('centre-v34-bound-design.json', {
    'analytic': calculus, 'declared_L': declared_L.tolist(), 'declared_H': declared_H.tolist(),
    'expanded_leaf_groups': [5, 5, 1], 'expanded_leaf_ids': expanded_ids,
    'expanded_H': declared_H[expanded_ids].tolist(),
    'expanded_L': declared_L[expanded_ids].tolist(),
    'shader_functions': functions, 'coefficient_domination': True,
    'numeric_bounds_gate_run': False, 'gpu_roundoff_proof': False,
    'attachment': {'scale_range': [.69, 1.31], 'root_cos_local': 1,
                   'overlap_cos_local_at_least': .61, 'maximum_shift_in_band': .15327,
                   'combined_shell_halfwidths': .157,
                   'scope': 'Shell interval overlap where child silhouette and f+.3 permit; no global topology or visual claim'},
    'limits': 'Prospective real-arithmetic Taylor certificate, ordinary float64 coefficient calculation. No sampled bounds, GPU compile/root, runtime/cost, visual or temporal result.'})
for group in ['files', 'protected', 'display']:
    verify(prior[group])
save_json(OUT.name, {
    'implementation_checks_passed': True, 'reversal_recovers_parent_bytes': True,
    'materials_marcher_controls_suffix_byte_equal': True,
    'compose_envelope_positiveReach_byte_equal': True,
    'renderer_version_only': True, 'python_ast_passed': True, 'node_check_passed': True,
    'explicit_smooth_reach_leaves': 11, 'a_b_hessian_assumption_removed': True,
    'coefficient_padding_passed': True, 'conditional_attachment_inequality_passed': True,
    'browser_runs': 0, 'sampled_numerical_runs': 0, 'cost_runs': 0, 'capture_runs': 0,
    'files': {name: digest(name) for name in created+[
        Path(__file__).name, 'centre-v34-field.glsl', 'field_centre_v34.py']},
    'protected': prior['protected'], 'display_before_closure': prior['display'],
    'historical_capture_integrity': digest('centre-v33r6-capture-integrity.json'),
    'limits': 'Static checks only. CSG crease normals are selected one-sided jets. No actual GLSL compile, numerical convergence, cost, realism or promotion.'})
print(json.dumps({'implementation_checks_passed': True,
                  'smooth_leaf_H': declared_H.tolist(), 'smooth_leaf_L': declared_L.tolist(),
                  'files_created': len(created), 'browser_runs': 0}))
