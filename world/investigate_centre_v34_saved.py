"""One-shot saved-readback investigation. No field, browser or root execution."""
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v34-saved-investigation.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rounding_cell(values):
    """Closed outer cell; boundary ties deliberately not evidence of feasibility."""
    values = np.asarray(values, dtype=np.float32)
    lo = np.nextafter(values, np.float32(-np.inf)).astype(np.float64)
    hi = np.nextafter(values, np.float32(np.inf)).astype(np.float64)
    return (lo + values.astype(float)) / 2, (hi + values.astype(float)) / 2


def main():
    assert not OUT.exists(), 'Do not replay completed investigation'
    manifest_path = HERE / 'centre-v34-numerical-failure-integrity.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['integrity_passed'] and not manifest['numeric_passed']
    assert not manifest['capture_permitted']
    for group in ['files', 'protected', 'display']:
        for name, expected in manifest[group].items():
            assert digest(HERE / name) == expected, name
    raw = json.loads((HERE / 'numeric-candidate-v34-raw.json').read_text())
    check = json.loads((HERE / 'numeric-candidate-v34-check.json').read_text())
    result = {
        'method': 'Saved readbacks only; no field evaluation, new scan, browser, roots, cost or capture.',
        'failure_manifest': digest(manifest_path),
        'script_sha256': digest(Path(__file__)),
        'numeric_passed': False, 'capture_permitted': False,
        'arithmetic': {}, 'missing_references': [],
    }
    for base_key, child_key, c1, c2 in [
        ('axial', 'childAxial', -.62, .20),
        ('angular', 'childAngular', -.90, .28),
    ]:
        base = np.concatenate([np.array(c['leaves'][base_key], dtype=np.float32).reshape(-1, 4) for c in raw])
        child = np.concatenate([np.array(c['leaves'][child_key], dtype=np.float32).reshape(-1, 4) for c in raw])
        expected = base.copy()
        expected[:, 3] += np.float32(c2)
        delta = child - expected
        mismatch = child[:, 3] != expected[:, 3]
        blo, bhi = rounding_cell(base[:, 3])
        clo, chi = rounding_cell(child[:, 3])
        # Test a necessary condition for constant folding, not a compiler diagnosis:
        # A=round(x+c1), B=round(x+fold(c1+c2)), with unknown REAL x.
        # Intersect inverse rounding cells; nonempty does not prove actual x exists
        # in the shader or that intermediate operations had these semantics.
        models = {}
        constants = {
            'sum_of_binary32_constants': float(np.float32(np.float32(c1) + np.float32(c2))),
            'rounded_decimal_sum': float(np.float32(c1 + c2)),
        }
        for label, folded in constants.items():
            lo = np.maximum(blo - float(np.float32(c1)), clo - folded)
            hi = np.minimum(bhi - float(np.float32(c1)), chi - folded)
            models[label] = {
                'folded_constant': folded,
                'disjoint_outer_cells_all': int(np.sum(lo > hi)),
                'disjoint_outer_cells_mismatches': int(np.sum((lo > hi) & mismatch)),
                'boundary_only_all': int(np.sum(lo == hi)),
                'strictly_overlapping_all': int(np.sum(lo < hi)),
                'interpretation': 'Disjoint refutes this restricted model; overlap is compatibility only, not attribution.',
            }
        ids = np.flatnonzero(mismatch)[:6]
        result['arithmetic'][child_key] = {
            'rays': len(base), 'mismatches_xyzw': np.count_nonzero(delta, axis=0).tolist(),
            'max_absolute_xyzw': np.max(np.abs(delta), axis=0).astype(float).tolist(),
            'restricted_constant_folding_models': models,
            'examples': [{'flat_ray': int(i), 'base': float(base[i, 3]),
                          'expected_offset': float(expected[i, 3]), 'saved_child': float(child[i, 3])} for i in ids],
        }
    identity = ['width', 'height', 'z', 'time', 'high']
    keys = ['parentF', 'parentAxial', 'parentAngular', 'parentPositive', 'parentNegative',
            'childF', 'childAxial', 'childAngular', 'childPositive', 'childNegative', 'backingF']
    for case, summary in zip(raw, check['cases']):
        assert all(case[k] == summary[k] for k in identity)
        for ref in summary['references']:
            if not ref.get('missing_reference'):
                continue
            i, w, h = ref['ray'], case['width'], case['height']
            hit = np.array(case['hits']).reshape(-1, 4)[i]
            grad = np.array(case['gradientSlope']).reshape(-1, 4)[i]
            point = np.array(case['points']).reshape(-1, 4)[i]
            counts = np.array(case['counts']).reshape(-1, 4)[i]
            ray = np.array([((i % w + .5) / w * 2 - 1) * np.tan(np.radians(34)) * 1.5,
                            ((i // w + .5) / h * 2 - 1) * np.tan(np.radians(34)), -1])
            ray /= np.linalg.norm(ray)
            cpu_point = np.array([0, 1.7, case['z']]) + hit[0] * ray
            jets = {k: np.array(case['leaves'][k]).reshape(-1, 4)[i].tolist() for k in keys}
            residual = float(hit[3])
            slope = float(np.dot(grad[:3], ray))
            result['missing_references'].append({
                **{k: case[k] for k in identity}, 'ray': i,
                'gpu_depth_hit_iterations_residual': hit.tolist(),
                'saved_gradient_directional_bound': grad.tolist(),
                'saved_point_footprint': point.tolist(), 'cpu_ray': ray.tolist(),
                'cpu_ray_point_minus_saved_gpu_point': (cpu_point - point[:3]).tolist(),
                'counts_cheap_full_skips_refinements': counts.tolist(),
                'termination_inference': 'No bisection branch: zero refinement calls and saved hit flag.' if counts[3] == 0 else 'Bisection branch recorded.',
                'saved_residual_over_cpu_ray_slope': abs(residual) / max(.00001, abs(slope)),
                'expanded_leaf_jets': jets,
                'not_recorded': ['GPU ray vector', 'termination-time sampleValue', 'pre-hit bracket/history',
                                 'CPU reference scan values or minimum', 'CPU leaves at missing reference'],
                'cause': 'Unresolved; local residual acceptance is not a first-root existence certificate.',
            })
    assert len(result['missing_references']) == 4
    assert [result['arithmetic'][k]['mismatches_xyzw'] for k in ['childAxial', 'childAngular']] == [
        [0, 0, 0, 36599], [0, 0, 0, 40662]]
    with OUT.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'arithmetic': result['arithmetic'], 'missing_reference_summary': [
        {k: v for k, v in r.items() if k not in ['expanded_leaf_jets', 'not_recorded']}
        for r in result['missing_references']]}))


if __name__ == '__main__':
    main()
