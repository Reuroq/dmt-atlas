"""Static checks and synthetic contracts only: zero field samples or browsers."""
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
from centre_v34_followup_common import HERE, PREFIX, SOURCES, digest, read, save, frozen, compare_arm


def main():
    frozen()
    save(PREFIX + '-static-started.json', {'inputs_sha256': digest(PREFIX + '-inputs.json')})
    checks = []
    for name in SOURCES:
        if name.endswith('.py'):
            tree = ast.parse((HERE / name).read_text(), filename=name)
            assert not any(isinstance(n, ast.ImportFrom) and n.module == 'field_centre_v34' for n in tree.body)
    checks.append('Python AST; oracle imported only inside profile runtime')
    import prepare_centre_v34_followup as prepare
    import profile_centre_v34_four_rays as profile
    import run_centre_v34_followup_once as launcher
    seeds = read(PREFIX + '-seeds.json')
    texture = np.frombuffer((HERE / (PREFIX + '-texture.f32')).read_bytes(), dtype='<f4').reshape(2, 128, 4)
    assert np.isfinite(texture).all() and np.all(texture[:, :, 1:] == 0)
    for leaf in seeds['leaves']:
        n = leaf['count']; x = np.asarray(leaf['values'], dtype=np.float32)
        assert 0 < n <= 128 and len(np.unique(x.view(np.uint32))) == n
        assert x.view(np.uint32).tolist() == leaf['bits']
        assert texture[leaf['row'], :n, 0].view(np.uint32).tolist() == leaf['bits']
        assert np.all(texture[leaf['row'], n:, :] == 0)
        assert len(leaf['selected_cells']) == 12
        for cell in leaf['selected_cells']:
            lo, hi = cell['closed_outer_inverse_cell']
            low, high, feasible = prepare.representable(np.array(lo), np.array(hi))
            assert bool(feasible) == cell['contains_binary32']
            assert bool(cell['chosen_predecessors']) == bool(feasible)
            assert all(lo <= v <= hi and v == float(np.float32(v)) for v in cell['chosen_predecessors'])
        for label in ['domain-low', 'domain-high', 'parent-cancellation', 'folded-child-cancellation', 'zero']:
            assert all(any(label + ':' + relation in labels for labels in leaf['labels']) for relation in ['previous', 'value', 'next'])
        parent = np.float32(x + np.float32(leaf['c1']))
        child = np.float32(parent + np.float32(leaf['c2']))
        folded = np.float32(x + np.float32(leaf['folded']))
        rows = np.stack([x, parent, child, folded], axis=-1)
        assert compare_arm(rows, x, leaf['c1'], leaf['c2'])['exact']
        wrong = rows.copy(); wrong[0, 2] = np.nextafter(wrong[0, 2], np.float32(np.inf))
        assert not compare_arm(wrong, x, leaf['c1'], leaf['c2'])['exact']
        assert compare_arm(wrong, x, leaf['c1'], leaf['c2'])['failed_indices'] == [0]
    low, high, possible = prepare.representable(np.array(1.+2**-25), np.array(1.+2**-24))
    assert not bool(possible)
    checks.append('Frozen binary texture, non-favourable cell selection records, neighbours, exact replay and one-ULP rejection')
    rays = read(PREFIX + '-rays.json')
    original = read('centre-v34-saved-investigation.json')['missing_references']
    assert rays['rays'] == original
    assert rays['spacing'] == .00005 and rays['half_width'] == .004 and rays['sample_count'] == 161
    assert rays['bisections'] == 24 and rays['old_grid_step'] == .003 and not rays['old_grid_replay']
    for ray in original:
        i, w, h = ray['ray'], ray['width'], ray['height']
        direction = np.array([((i%w+.5)/w*2-1)*np.tan(np.radians(34))*1.5,
                              ((i//w+.5)/h*2-1)*np.tan(np.radians(34)), -1.])
        direction /= np.linalg.norm(direction)
        assert np.array_equal(direction, ray['cpu_ray'])
        depths = ray['gpu_depth_hit_iterations_residual'][0] + np.arange(-80,81)*rays['spacing']
        assert len(depths) == 161 and depths[80] == ray['gpu_depth_hit_iterations_residual'][0]
    for f, expected_orientation in [(lambda x: x-.123456789, 'exit'), (lambda x: .123456789-x, 'enter'), (lambda x: x-.5, 'exit')]:
        result = profile.refine(f, 0., 1., f(0.), f(1.))
        assert len(result['bisections']) == 24 and result['orientation'] == expected_orientation
        assert result['final']['width'] == 2**-24
        assert result['final']['values'][0] * result['final']['values'][1] <= 0
    zero = profile.refine(lambda x: x-.5, 0., 1., -.5, .5)
    assert zero['sampled_exact_zeros'] == [.5]
    try:
        profile.refine(lambda x: 1., 0., 1., 1., 1.)
    except AssertionError:
        pass
    else:
        raise AssertionError('Non-bracket accepted')
    bracket = lambda lo, hi, o: {'orientation': o, 'final': {'depths': [lo, hi]}}
    assert profile.grid_comparison([bracket(.001,.0011,'enter'),bracket(.0019,.002,'exit')],.003)[0]['both_crossings_enclosed_between_grid_positions']
    assert not profile.grid_comparison([bracket(.001,.0011,'enter'),bracket(.0039,.004,'exit')],.003)[0]['both_crossings_enclosed_between_grid_positions']
    assert not profile.grid_comparison([bracket(.001,.0011,'exit'),bracket(.0019,.002,'enter')],.003)
    checks.append('Four ray identities/CPU directions; 161 depths; synthetic strict/exit/zero/24-bisection and algebraic-grid contracts')
    # Node parses and executes only shader-string construction with a fake window.
    node = r'''
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(process.argv[1],'utf8');
const source=html.split('<script>')[1].split('</script>')[0];
const context={window:{}};vm.createContext(context);vm.runInContext(source,context);
for(let leaf=0;leaf<2;leaf++){
 const literal=context.window.shaderSource(leaf,'literal'), uniform=context.window.shaderSource(leaf,'uniform');
 const token=leaf===0?'offset(parent,.20)':'offset(parent,.28)';
 if(literal.split(token).length!==2||literal.replace(token,'offset(parent,secondOffset)')!==uniform)throw Error('Not second-offset-only');
 if(!literal.includes('precision highp float;')||!literal.includes('vec4 offset(vec4 a,float b){return vec4(a.xyz,a.w+b);}'))throw Error('Precision/helper drift');
}
process.stdout.write('Shader JS syntax and literal-to-uniform-only arms PASS\n');
'''
    result = subprocess.run(['node', '-e', node, str(HERE/'gpu_centre_v34_offsets.html')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    checks.append(result.stdout.strip() + '; no GLSL or browser execution')
    # Exercise the actual foreground launcher on a tiny synthetic child; all files under world/.
    with tempfile.TemporaryDirectory(prefix=PREFIX+'-static-', dir=HERE) as directory:
        root = Path(directory)
        (root/'fake.py').write_text("print('synthetic child')\nraise SystemExit(7)\n")
        launcher.HERE = root
        launcher.historical = lambda: None
        launcher.TASKS = {'prepare':'fake.py'}
        launcher.digest = lambda name: __import__('hashlib').sha256((root/name).read_bytes()).hexdigest() if (root/name).exists() else 'synthetic-launcher'
        def fake_save(name, value):
            with (root/name).open('x') as stream:
                json.dump(value, stream)
        launcher.save = fake_save
        sys.argv = ['synthetic', 'prepare']
        assert launcher.main() == 7
        receipt = json.loads((root/(PREFIX+'-prepare-once-exit.json')).read_text())
        assert receipt['actual_exit'] == 7
        assert receipt['log_sha256'] == launcher.digest(PREFIX+'-prepare-once.log')
        try:
            launcher.main()
        except AssertionError:
            pass
        else:
            raise AssertionError('Launcher allowed replay')
    checks.append('Actual foreground launcher synthetic exit7/log binding and replay refusal; no retry')
    frozen()
    save(PREFIX + '-static-check.json', {'static_passed': True, 'checks': checks,
         'inputs_sha256': digest(PREFIX + '-inputs.json'), 'new_field_samples': 0, 'new_browser_runs': 0,
         'numeric_passed': False, 'capture_permitted': False})
    print('\n'.join(checks), flush=True)


if __name__ == '__main__':
    main()
