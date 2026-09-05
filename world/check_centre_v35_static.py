"""Frozen v35 static closure: exact derivations, actual JS binding paths, no GPU."""
import ast
import hashlib
import json
import re
import subprocess
import v35_preparation as p
from build_centre_v35 import COPIES, EDITS, CONTROL


def durable_node(label, args, source=None):
    stem = p.PREFIX + '-static-node-' + label
    argv = ['node'] + args
    p.save(stem + '-launch.json', {'argv': argv, 'stdin_sha256':
        hashlib.sha256(source.encode()).hexdigest() if source is not None else None})
    if source is not None:
        p.write(stem + '.js', source)
    actual, error, stdout, stderr = None, None, '', ''
    try:
        result = subprocess.run(argv, input=source, text=True, capture_output=True, timeout=15, cwd=p.HERE)
        actual, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        error = repr(exc)
        decode = lambda value: value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
        stdout, stderr = decode(exc.stdout), decode(exc.stderr)
    except Exception as exc:
        error = repr(exc)
    p.write(stem + '-stdout.txt', stdout); p.write(stem + '-stderr.txt', stderr)
    p.save(stem + '-exit.json', {'actual_exit': actual, 'launcher_error': error,
        'stdout_sha256': p.digest(stem + '-stdout.txt'), 'stderr_sha256': p.digest(stem + '-stderr.txt'),
        'launch_sha256': p.digest(stem + '-launch.json')})
    assert actual == 0 and error is None, (label, 'see durable stdout/stderr')
    assert not stderr, label
    return stdout


def main():
    freeze = p.frozen(); p.receipt('build')
    delta = p.read(p.PREFIX + '-source-delta.json')
    assert list(delta) == [n.replace('v34', 'v35') for n in COPIES]
    for name, entry in delta.items():
        assert p.digest(entry['base']) == entry['base_sha256']
        source = (p.HERE / entry['base']).read_text().replace('v34', 'v35')
        for before, after in entry['edits']:
            assert source.count(before) == 1
            source = source.replace(before, after, 1)
        assert source == (p.HERE / name).read_text() and p.digest(name) == entry['sha256'], name
        if name.startswith('continuum-'):
            assert entry['edits'] == [list(e) for e in EDITS]
        elif name != 'runtime_centre_v35.py':
            assert not entry['edits'], name
    parsed = []
    for name in freeze['sources']:
        if name.endswith('.py'):
            ast.parse((p.HERE / name).read_text(), filename=name); parsed.append(name)
    # Unchanged scalar, Hessian/CSG and numerical gates are inherited through
    # complete source equivalence, not assertions about a few selected strings.
    inherited = p.read('centre-v34-fixture-check.json')
    assert inherited['static_passed'] and inherited['gpu_rays'] == 75996
    assert inherited['fixed_references'] == inherited['interval_references'] == 720
    assert inherited['cost_pairs'] == 12
    assert p.read('centre-v34-launcher-exit-check.json')['passed']
    assert p.read('centre-v33r6-lifecycle-check.json')['passed']
    candidate = (p.HERE / 'continuum-v35-candidate.js').read_text()
    reference = (p.HERE / 'continuum-v35-unshared-reference.js').read_text()
    before = 'fieldPartsReachShared(p,sharedJetsState,f,a,b,axA,axB,angA,angB,shellA,shellB);'
    after = 'fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);'
    assert candidate.count(before) == 1 and candidate.replace(before, after, 1) == reference
    for stem in ('candidate', 'unshared-reference'):
        durable_node('syntax-' + stem, ['--check', str(p.HERE / ('continuum-v35-' + stem + '.js'))])
    durable_node('syntax-harness', ['--check', str(p.HERE / 'check_centre_v35_uniforms.cjs')])
    fixtures = ['gpu_probe_v35_candidate.html', 'gpu_probe_v35_leaves.html',
                'gpu_cost_v35_candidate.html', 'gpu_cost_v35_parent.html']
    snapshots = {}
    for name in fixtures:
        html = (p.HERE / name).read_text()
        inline = re.findall(r'<script>([\s\S]*?)</script>', html)
        assert len(inline) == 1
        durable_node('syntax-' + name, ['--check'], inline[0])
        dependencies = re.findall(r'<script src="([^"]+)"></script>', html)
        expected = 'continuum-v35-unshared-reference.js' if name.endswith('parent.html') else 'continuum-v35-candidate.js'
        assert dependencies == ['vendor/three.min.js', expected]
        result = durable_node('bindings-' + name, ['check_centre_v35_uniforms.cjs', expected, name])
        snapshots[name] = json.loads(result)
    for stem in ('candidate', 'unshared-reference'):
        name = 'continuum-v35-' + stem + '.js'
        snapshots[name] = json.loads(durable_node('bindings-' + stem, ['check_centre_v35_uniforms.cjs', name]))
    assert snapshots[fixtures[0]] == snapshots[fixtures[2]]
    a, b = snapshots[fixtures[2]]['fragmentShader'], snapshots[fixtures[3]]['fragmentShader']
    assert a.replace(before, after, 1) == b
    for name, snapshot in snapshots.items():
        original = candidate if name != fixtures[3] and 'unshared-reference' not in name else reference
        if name.endswith('.html'):
            html = (p.HERE / name).read_text()
            start = 'let shader=' if 'leaves' in name else 'let fragment='
            transform = html[html.index(start):html.index('material.needsUpdate=true;')]
            # Independently transform the old literal shader and undo only the
            # new uniform declarations/usages: every other shader byte is equal.
            base_name = delta[name]['base']
            old_html = (p.HERE / base_name).read_text()
            old_transform = old_html[old_html.index(start):old_html.index('material.needsUpdate=true;')]
            old_candidate = original
            for old, new in reversed(EDITS):
                assert old_candidate.count(new) == 1
                old_candidate = old_candidate.replace(new, old, 1)
            fragment = re.search(r'fragmentShader:`([\s\S]*?)`', old_candidate).group(1)
            script = 'const material={fragmentShader:' + json.dumps(fragment) + '};\n' + old_transform + '\nprocess.stdout.write(material.fragmentShader);'
            old_result = durable_node('baseline-transform-' + name, [], script)
            new_result = snapshot['fragmentShader']
            for old, new in reversed(EDITS[1:]):
                assert new_result.count(new) == 1
                new_result = new_result.replace(new, old, 1)
            assert new_result == old_result, name
    # Renderer remains the exact version-only original; no reduced render gate.
    render = (p.HERE / 'render_centre_v35.py').read_text()
    assert render.replace('v35', 'v34') == (p.HERE / 'render_centre_v34.py').read_text()
    tree = ast.parse((p.HERE / 'probe_numeric_candidate_v35.py').read_text())
    grids = [ast.literal_eval(n.iter) for n in ast.walk(tree) if isinstance(n, ast.For)
             and isinstance(n.target, ast.Tuple) and [a.id for a in n.target.elts] == ['w', 'h', 'times']]
    assert len(grids) == 1
    cases = [(w, h, z, t, high) for w, h, times in grids[0] for z in (8, -6) for t in times for high in (1, 0)]
    assert len(cases) == 48 and sum(w*h for w,h,*_ in cases) == 75996
    p.frozen()
    p.save(p.PREFIX + '-static.json', {'static_passed': True, 'python_ast_files': parsed,
        'derived_files': len(delta), 'binding_paths': list(snapshots), 'quality_modes_per_path': 2,
        'binding_negative_cases': 36, 'exact_shader_reversal': True,
        'cases': len(cases), 'gpu_rays': 75996, 'fixed_references': 720, 'interval_references': 720,
        'cost_pairs': 12, 'scalar_oracle_and_gates_version_only': True,
        'inherited_contract_receipts': {name: p.digest(name) for name in [
            'centre-v34-fixture-check.json', 'centre-v34-launcher-exit-check.json', 'centre-v33r6-lifecycle-check.json']},
        'browser_runs': 0, 'actual_glsl_runs': 0, 'field_samples': 0,
        'numeric_passed': False, 'root_failure_fixed': False, 'capture_permitted': False})
    print('Static PASS: 18 exact derivations, six high/low binding paths, 36 negative cases; no field or browser run')


if __name__ == '__main__':
    main()
