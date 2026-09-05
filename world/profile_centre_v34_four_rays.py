"""New local float64 profiles only; never replay the old forward reference scan."""
import numpy as np
from centre_v34_followup_common import HERE, PREFIX, LEAVES, read, save, digest, runtime_gate


def sign(value):
    return int(np.sign(value))


def refine(evaluate, lo, hi, lv, hv, steps=24):
    """Retain strict original bracket; exact midpoint zeros become zero endpoints."""
    assert lv * hv < 0
    original = {'depths': [lo, hi], 'values': [lv, hv], 'signs': [sign(lv), sign(hv)]}
    history, zeros = [], []
    for _ in range(steps):
        mid = (lo + hi)/2
        mv = float(evaluate(mid))
        assert np.isfinite(mv)
        history.append({'depth': mid, 'value': mv})
        if mv == 0:
            zeros.append(mid)
        if mv * lv > 0:
            lo, lv = mid, mv
        else:
            hi, hv = mid, mv
    assert lv * hv <= 0
    return {'original': original, 'final': {'depths': [lo, hi], 'values': [lv, hv],
            'signs': [sign(lv), sign(hv)], 'width': hi-lo},
            'bisections': history, 'sampled_exact_zeros': zeros,
            'orientation': 'enter' if original['values'][0] > 0 else 'exit'}


def grid_comparison(brackets, step):
    """Algebraic grid-index comparison; not a root-isolation or first-root proof."""
    pairs = []
    for left, right in zip(brackets, brackets[1:]):
        if left['orientation'] != 'enter' or right['orientation'] != 'exit':
            continue
        outer_lo = left['final']['depths'][0]
        outer_hi = right['final']['depths'][1]
        k = int(np.floor(outer_lo / step))
        enclosed = k * step < outer_lo < outer_hi < (k+1) * step
        pairs.append({'enter_bracket': left['final'], 'exit_bracket': right['final'],
             'outer_width_bound': outer_hi-outer_lo, 'old_grid_indices': [k, k+1],
             'old_grid_positions_algebraic_only': [k*step, (k+1)*step],
             'both_crossings_enclosed_between_grid_positions': bool(enclosed),
             'interpretation': 'Two local sign crossings; if enclosed, evidence about old scan resolution only. Additional unsampled crossings and earlier roots remain unexcluded.'})
    return pairs


def main():
    runtime_gate()
    stem = PREFIX + '-profiles'
    save(stem + '-started.json', {'inputs_sha256': digest(PREFIX + '-inputs.json')})
    from field_centre_v34 import field, smooth_parts, expanded_leaves, compose_expanded
    frozen = read(PREFIX + '-rays.json')
    assert frozen['oracle_sha256'] == digest('field_centre_v34.py')
    profiles = []
    try:
        for index, ray in enumerate(frozen['rays']):
            camera = np.array([0., 1.7, ray['z']], dtype=np.float64)
            direction = np.array(ray['cpu_ray'], dtype=np.float64)
            hit = ray['gpu_depth_hit_iterations_residual'][0]
            depths = hit + np.arange(-80, 81, dtype=np.float64) * frozen['spacing']

            def sample(points):
                leaves = expanded_leaves(smooth_parts(points, ray['time'], camera, ray['high']))
                full = field(points, ray['time'], camera, ray['high'])
                assert np.array_equal(full, compose_expanded(leaves))
                assert np.isfinite(leaves).all() and np.isfinite(full).all()
                return np.concatenate([np.asarray(full)[..., None], leaves], axis=-1)

            points = camera + depths[:, None] * direction
            values = sample(points)
            saved_point = np.array(ray['saved_point_footprint'][:3], dtype=np.float64)
            at_gpu = sample(saved_point)
            gpu_parent, gpu_child = int(np.argmax(at_gpu[1:6])), int(np.argmax(at_gpu[6:11]))+5
            gpu_group = int(np.argmin([at_gpu[gpu_parent+1], at_gpu[gpu_child+1], at_gpu[11]]))
            gpu_active = [gpu_parent, gpu_child, 10][gpu_group]
            parent = np.argmax(values[:, 1:6], axis=1)
            child = np.argmax(values[:, 6:11], axis=1) + 5
            groups = np.stack([values[np.arange(161), parent+1], values[np.arange(161), child+1], values[:, 11]], axis=-1)
            selected = np.argmin(groups, axis=1)
            active = np.choose(selected, [parent, child, np.full(161, 10)])
            samples = [{'depth': float(d), 'point': p.tolist(), 'full': float(v[0]),
                        'expanded': dict(zip(LEAVES, v[1:].tolist())),
                        'selected_branch': ['parent', 'child', 'backing'][int(g)],
                        'active_leaf': LEAVES[int(a)],
                        'branch_ties': np.flatnonzero(gs == np.min(gs)).tolist()}
                       for d, p, v, g, a, gs in zip(depths, points, values, selected, active, groups)]
            # Durable full profile BEFORE adaptive bisections.
            save(stem + '-ray-' + str(index) + '-samples.json', {
                'identity': {k: ray[k] for k in ['width', 'height', 'z', 'time', 'high', 'ray']},
                'point_arithmetic': 'float64 camera + saved CPU ray * depth; NOT saved GPU points',
                'tie_convention': 'First indexed maximum/minimum for diagnostic labels only, not GPU normal selection.',
                'samples': samples, 'exact_saved_gpu_point_float64_oracle': {
                    'point': saved_point.tolist(), 'full': float(at_gpu[0]),
                    'expanded': dict(zip(LEAVES, at_gpu[1:].tolist())),
                    'selected_branch': ['parent', 'child', 'backing'][gpu_group], 'active_leaf': LEAVES[gpu_active]},
                'cpu_centre_point_minus_saved_gpu_point': (points[80]-saved_point).tolist(),
                'saved_gpu_expanded_jets': ray['expanded_leaf_jets']})
            channels = {}
            for column, name in enumerate(['full'] + LEAVES):
                v = values[:, column]
                indices = np.flatnonzero(v[:-1]*v[1:] < 0)
                brackets = []
                for i in indices:
                    evaluations = []
                    def evaluate(depth):
                        point = camera + depth*direction
                        value = sample(point)
                        pa, ch = int(np.argmax(value[1:6])), int(np.argmax(value[6:11]))+5
                        branch = int(np.argmin([value[pa+1], value[ch+1], value[11]]))
                        evaluations.append({'depth': depth, 'point': point.tolist(), 'full': float(value[0]),
                            'expanded': dict(zip(LEAVES, value[1:].tolist())),
                            'selected_branch': ['parent', 'child', 'backing'][branch],
                            'active_leaf': LEAVES[[pa, ch, 10][branch]]})
                        return value[column]
                    bracket = refine(evaluate, float(depths[i]), float(depths[i+1]),
                                     float(v[i]), float(v[i+1]), frozen['bisections'])
                    bracket['midpoint_full_profiles'] = evaluations
                    brackets.append(bracket)
                minima = np.flatnonzero((v[1:-1] <= v[:-2]) & (v[1:-1] <= v[2:])) + 1
                channels[name] = {'brackets': brackets,
                    'sampled_exact_zero_indices': np.flatnonzero(v == 0).tolist(),
                    'sampled_local_minima': [{'index': int(i), 'depth': float(depths[i]), 'value': float(v[i])} for i in minima],
                    'sampled_minimum_index': int(np.argmin(v)),
                    'sign_change_or_zero_indices': (np.flatnonzero(np.sign(v[:-1]) != np.sign(v[1:]))+1).tolist(),
                    'status': 'local strict brackets observed' if len(brackets) else 'UNRESOLVED: no sampled strict bracket; no tangency/absence/oracle conclusion'}
            result = {'ray': ray['ray'], 'channels': channels,
                'active_leaf_change_indices': (np.flatnonzero(active[:-1] != active[1:])+1).tolist(),
                'branch_change_indices': (np.flatnonzero(selected[:-1] != selected[1:])+1).tolist(),
                'old_grid_algebra': grid_comparison(channels['full']['brackets'], frozen['old_grid_step']),
                'first_root_certified': False}
            save(stem + '-ray-' + str(index) + '-brackets.json', result)
            profiles.append(result)
            print('Local ray', ray['ray'], 'full brackets', len(channels['full']['brackets']), flush=True)
    except BaseException as exc:
        save(stem + '-failure.json', {'failure': repr(exc), 'completed_rays': len(profiles)})
        raise
    save(stem + '-result.json', {'complete': len(profiles) == 4, 'profiles': profiles,
        'oracle_sha256': digest('field_centre_v34.py'), 'inputs_sha256': digest(PREFIX + '-inputs.json'),
        'numeric_passed': False, 'capture_permitted': False, 'first_root_certified': False,
        'old_full_forward_scan_replayed': False, 'dependent_independent_gate_run': False})


if __name__ == '__main__':
    main()
