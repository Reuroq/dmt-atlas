"""Prepare and freeze a new isolated uniform-offset candidate; STATIC ONLY."""
import ast
import v35r2_preparation as p

COPIES = [
    'continuum-v34-candidate.js', 'continuum-v34-unshared-reference.js',
    'field_centre_v34.py', 'csg_interval_v34.py', 'gpu_csg_v34.py',
    'centre-v34-bound-design.json', 'check_centre_v34_bounds.py',
    'cost_lifecycle_v34.py', 'runtime_centre_v34.py', 'run_centre_v34_gate_once.py',
    'gpu_probe_v34_candidate.html', 'gpu_probe_v34_leaves.html',
    'gpu_cost_v34_candidate.html', 'gpu_cost_v34_parent.html',
    'probe_numeric_candidate_v34.py', 'audit_centre_v34_first_roots.py',
    'measure_centre_v34_cost.py', 'render_centre_v34.py',
]
EDITS = [
    ('time:{value:0},high:{value:1}',
     'childAxialOffset:{value:Math.fround(.20)},childAngularOffset:{value:Math.fround(.28)},time:{value:0},high:{value:1}'),
    ('uniform float time,high,pixelScale;',
     'uniform float time,high,pixelScale;\n   uniform float childAxialOffset,childAngularOffset;'),
    ('axB=offset(axA,.20);', 'axB=offset(axA,childAxialOffset);'),
    ('angB=offset(angA,.28);', 'angB=offset(angA,childAngularOffset);'),
]
CONTROL = ['v35r2_preparation.py', 'build_centre_v35r2.py', 'check_centre_v35r2_static.py',
           'check_centre_v35r2_uniforms.cjs', 'run_centre_v35r2_preparation_once.py',
           'close_centre_v35r2_preparation.py']


def main():
    assert not (p.HERE / (p.PREFIX + '-freeze.json')).exists(), 'Never replay builder'
    prior = p.history()
    delta = {}
    for base in COPIES:
        name = base.replace('v34', 'v35r2')
        text = (p.HERE / base).read_text().replace('v34', 'v35r2')
        edits = EDITS if name.startswith('continuum-') else []
        if name == 'runtime_centre_v35r2.py':
            edits = [('def fixture_gate():\n',
                      'def fixture_gate():\n    from v35r2_preparation import closed\n    closed()\n')]
        for before, after in edits:
            assert text.count(before) == 1, (name, before)
            text = text.replace(before, after, 1)
        if name.endswith('.py'):
            ast.parse(text, filename=name)
        p.write(name, text)
        delta[name] = {'base': base, 'base_sha256': p.digest(base), 'edits': edits, 'sha256': p.digest(name)}
    p.save(p.PREFIX + '-source-delta.json', delta)
    failure = p.read('centre-v35-preparation-failure-finalization.json')
    p.verify(failure['files'])
    extras = list(failure['files']) + ['centre-v35-preparation-failure.json',
        'prepare_centre_v35_static_r2.py', 'centre-v35-static-r2-source-delta.json',
        'centre-v35-preparation-failure-finalization.json', 'centre-v35r2-prefreeze-amendments.json']
    extras += [path.name for path in p.HERE.glob('centre-v35-static-r2-prepare-once*') if path.is_file()]
    sources = list(delta) + CONTROL + [p.PREFIX + '-source-delta.json'] + extras
    p.save(p.PREFIX + '-freeze.json', {
        'sources': {name: p.digest(name) for name in sources},
        'history_sha256': p.digest(p.HISTORY), 'runtime_run': False,
        'support': 'Both-leaf synthetic exact uniform support; NOT actual-field correctness',
        'protected': prior['protected'], 'display': prior['display'],
    })
    print('v35r2 isolated candidate and 18 derived sources frozen; no runtime')


if __name__ == '__main__':
    main()
