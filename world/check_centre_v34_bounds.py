"""ONE-SHOT prospective v34 bounds/clearance/attachment fixture; not yet run.

72,000 base leaf/reach samples and 12,000 clearance samples, plus explicit cap
and clipped attachment checks. FD slopes below are sample evidence only;
actual analytic GLSL jets and first roots need their separate GPU fixture.
"""
import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np
from field_centre_v34 import PIXEL, smooth_parts, expanded_leaves, compose_expanded, field, analytic_bounds
from csg_interval_v34 import contract_checks

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-v34-bounds-check.json'
START = HERE/'centre-v34-bounds-started.json'
FAILURE = HERE/'centre-v34-bounds-failure.json'
TIMES = [2.4077, 3.5242, 4., 4.895, 8., 221., 900.]


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def verify(group):
    for name, expected in group.items():
        assert digest(name) == expected, name


def reach(value, slope, curvature):
    remaining = .95*np.maximum(value, 0)
    derivative = abs(slope)
    return np.minimum(.4, 2*remaining/np.maximum(
        1e-30, derivative+np.sqrt(derivative**2+2*curvature*remaining)))


def compose_reaches(values):
    # Identical MAX intersection / MIN union arrangement, no min step.
    return compose_expanded(values)


def attachment_checks():
    """Locate actual clipped shared-root bands, not just separation algebra.

    Parameterize local=2*pi*k before the cap; bisect parent-shell roots in
    radius. This samples existing scalar geometry, never browser navigation.
    No global connected-component/topology claim follows from these roots.
    """
    results = []
    angles = np.linspace(-np.pi, np.pi, 64, endpoint=False)
    radius = np.linspace(5.8, 16.6, 257)
    for t in TIMES:
        for camera_z in [8, -6]:
            camera = np.array([0., 1.7, camera_z])
            for high in [1, 0]:
                roots = []
                for theta in angles:
                    # Four local-root planes spanning the visible depth.
                    h6_mid = (11*np.exp(1j*(theta+.075*t))/np.sqrt(11**2+2.25))**6
                    ks = sorted(set(int(round((.62*z-.28*11+.12*h6_mid.imag-.19*t)/(2*np.pi)))
                                    for z in [-24., -16., -8., 0.]))
                    for k in ks:
                        def position(r):
                            h6 = (r*np.exp(1j*(theta+.075*t))/np.sqrt(r*r+2.25))**6
                            z = (2*np.pi*k+.28*r-.12*h6.imag+.19*t)/.62
                            return np.stack([r*np.cos(theta), 1.7+r*np.sin(theta), z], axis=-1)
                        points = position(radius)
                        values = smooth_parts(points, t, camera, high)[:, 3]
                        indices = np.flatnonzero(values[:-1]*values[1:] < 0)
                        if not len(indices):
                            continue
                        lo, hi = radius[indices].copy(), radius[indices+1].copy()
                        lv = values[indices]
                        for _ in range(32):
                            mid = (lo+hi)/2
                            mv = smooth_parts(position(mid), t, camera, high)[:, 3]
                            same = mv*lv > 0
                            lo = np.where(same, mid, lo)
                            lv = np.where(same, mv, lv)
                            hi = np.where(same, hi, mid)
                        root = position((lo+hi)/2)
                        v = smooth_parts(root, t, camera, high)
                        allowed = ((root[:, 2] >= -27.4) & (root[:, 2] <= 8)
                                   & (v[:, 0]+.3 < -.01) & (v[:, 2]+.28 < -.01))
                        if np.any(allowed):
                            roots.extend(root[allowed].tolist())
                root = np.array(roots).reshape(-1, 3)
                maximum = 1e9
                shared_error = 1e9
                if len(root):
                    v = smooth_parts(root, t, camera, high)
                    shared_error = float(np.max(abs(v[:, 3]-v[:, 4])))
                    # Interior occupancy of BOTH parent and child, including
                    # small 3D offsets: a finite band, not mere point contact.
                    maximum = -1e9
                    for offset in [np.zeros(3), *(.0001*np.eye(3)), *(-.0001*np.eye(3))]:
                        e = expanded_leaves(smooth_parts(root+offset, t, camera, high))
                        maximum = max(maximum, float(np.max(e[:, :10])))
                results.append({'time': t, 'camera_z': camera_z, 'high': high,
                                'clipped_root_count': len(root), 'root_sample': root[:6].tolist(),
                                'max_shared_shell_error': shared_error,
                                'max_parent_and_child_leaf_in_neighborhood': maximum,
                                'passed': len(root) > 0 and shared_error < 1e-8 and maximum < 0})
    return results


def main():
    assert not any(path.exists() for path in [OUT, START, FAILURE]), 'One-shot; preserve partial attempt'
    gate = json.loads((HERE/'centre-v34-fixture-integrity.json').read_text())
    assert gate['static_passed'] and gate['fixtures_complete'] and not gate['numerical_run']
    for group in ['files', 'protected', 'display']:
        verify(gate[group])
    before = {name: digest(name) for name in gate['protected']}
    save(START, {'started': True, 'fixture_manifest': digest('centre-v34-fixture-integrity.json')})
    design = json.loads((HERE/'centre-v34-bound-design.json').read_text())
    H = np.array(design['declared_H']); L = np.array(design['declared_L'])
    ids = np.array(design['expanded_leaf_ids'])
    analytic = analytic_bounds()
    assert np.all(H > np.array(analytic['H'])) and np.all(L > np.array(analytic['L']))
    rng = np.random.default_rng(34001)
    n = 6000
    direction = rng.normal(size=(n, 3)); direction /= np.linalg.norm(direction, axis=1)[:, None]
    rho = rng.uniform(5.4, 22, n)
    p = direction*rho[:, None]; p[:, 1] += 1.7; p[:, 2] = -27.5-abs(p[:, 2])/.85
    theta = rng.uniform(-np.pi, np.pi, n//2)
    p[:n//2, 0] = rho[:n//2]*np.cos(theta)
    p[:n//2, 1] = 1.7+rho[:n//2]*np.sin(theta)
    p[:n//2, 2] = rng.uniform(-27.8, 12, n//2)
    d = rng.normal(size=(n, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    t = rng.choice(TIMES, n)
    eps = .001
    results = []
    cap_checks = []
    for pixel in [PIXEL, PIXEL*2, PIXEL*4]:
        M, limit = H@np.array([1, pixel, pixel**2]), L@np.array([1, pixel])
        for z in [8, -6]:
            camera = np.array([0., 1.7, z])
            for high in [1, 0]:
                def leaves(q):
                    return smooth_parts(q, t, camera, high, pixel)
                centre, plus, minus = leaves(p), leaves(p+eps*d), leaves(p-eps*d)
                slope = (plus-minus)/(2*eps)
                curvature = (plus-2*centre+minus)/eps**2
                e = expanded_leaves(centre)
                # Offsets have zero derivative; negative shells flip signs.
                sign = np.array([1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1])
                r = reach(e, slope[:, ids]*sign, M[ids])
                step = compose_reaches(r)
                fast = np.minimum(np.minimum(np.maximum(r[:, 0], r[:, 1]),
                                             np.maximum(r[:, 5], r[:, 6])), r[:, 10])
                scalar = field(p, t, camera, high, pixel)
                replay_error = float(np.max(abs(compose_expanded(e)-scalar)))
                free, useful = scalar > 1e-6, fast > .08
                min_full = min_cheap = 1e9
                for fraction in [.25, .5, .75, 1.]:
                    fv = field(p+d*(step*fraction)[:, None], t, camera, high, pixel)
                    cv = field(p+d*(fast*fraction)[:, None], t, camera, high, pixel)
                    if np.any(free):
                        min_full = min(min_full, float(fv[free].min()))
                    if np.any(useful):
                        min_cheap = min(min_cheap, float(cv[useful].min()))
                result = {'camera_z': z, 'high': high, 'pixelScale': pixel, 'samples': n,
                          'max_leaf_gradient_ratio': float(np.max(abs(slope)/limit)),
                          'max_leaf_curvature_ratio': float(np.max(abs(curvature)/M)),
                          'min_advanced_field': min_full, 'cheap_minimum_advanced_field': min_cheap,
                          'free_samples': int(free.sum()), 'cheap_useful_segments': int(useful.sum()),
                          'cheap_exceeds_full': float(np.max(fast-step)), 'csg_replay_error': replay_error,
                          'clock_counts': {str(clock): int(np.sum(t == clock)) for clock in TIMES}}
                result['passed'] = bool(result['max_leaf_gradient_ratio'] < 1
                    and result['max_leaf_curvature_ratio'] < 1 and min_full >= -1e-7
                    and min_cheap > 0 and np.any(useful) and np.any(free)
                    and np.all(scalar[useful] > 0) and result['cheap_exceeds_full'] <= 1e-10
                    and replay_error < 1e-12)
                results.append(result)
                # Deliberate cap-join straddles at the exact envelope threshold.
                cp = p.copy(); cp[:, 2] = -27.5
                radial_xy = np.linalg.norm(cp[:, :2]-[0, 1.7], axis=1)
                cp[:, :2] = [0, 1.7]+(cp[:, :2]-[0, 1.7])*(5.365/radial_xy)[:, None]
                c0, c1, c2 = leaves(cp), leaves(cp+[0, 0, eps]), leaves(cp-[0, 0, eps])
                ratio = float(np.max(abs((c1-2*c0+c2)/eps**2)/M))
                cap_checks.append({'camera_z': z, 'high': high, 'pixelScale': pixel,
                                   'samples': n, 'max_hessian_ratio': ratio, 'passed': ratio < 1})
    corridor = np.column_stack([rng.uniform(-4, 4, n), np.full(n, 1.7), rng.uniform(-22, 8, n)])
    angle = rng.uniform(-np.pi, np.pi, n)
    inner = np.column_stack([5.449*np.cos(angle), 1.7+5.449*np.sin(angle), rng.uniform(-27.5, 8, n)])
    clearance = []
    for points, label in [(corridor, 'walk corridor'), (inner, 'rho5.449 before cap')]:
        values = field(points, t, np.array([0., 1.7, 8]), 1)
        clearance.append({'region': label, 'samples': n, 'minimum_field': float(values.min()),
                          'passed': bool(np.all(values > 0))})
    filter_checks = []
    delta = p-np.array([0, 1.7, 8])
    for k in [4, 6, 9]:
        weights = []
        for pixel in [0, PIXEL, 2*PIXEL, 4*PIXEL]:
            q = k*pixel
            w = np.exp(-.5*q*q*np.sum(delta*delta, axis=1))
            exact = -q*q*w*np.sum(delta*d, axis=1)
            wp = np.exp(-.5*q*q*np.sum((delta+eps*d)**2, axis=1))
            wm = np.exp(-.5*q*q*np.sum((delta-eps*d)**2, axis=1))
            error = float(np.max(abs((wp-wm)/(2*eps)-exact)))
            weights.append(w)
            filter_checks.append({'frequency': k, 'pixelScale': pixel,
                                  'max_derivative_error': error, 'passed': error < 1e-7})
        assert np.all(np.diff(np.stack(weights), axis=0) <= 0)
    attachment = attachment_checks()
    after = {name: digest(name) for name in before}
    verify(gate['display'])
    passed = all(x['passed'] for x in results+cap_checks+clearance+filter_checks+attachment) and before == after
    out = {'passed': passed, 'cases': results, 'clearance': clearance, 'cap_join': cap_checks,
           'attachment': attachment, 'filter': filter_checks, 'synthetic_interval_contract': contract_checks(),
           'base_leaf_reach_samples': sum(x['samples'] for x in results),
           'clearance_samples': sum(x['samples'] for x in clearance),
           'protected_before': before, 'protected_after': after,
           'source_hashes': {name: digest(name) for name in [Path(__file__).name,
               'field_centre_v34.py', 'csg_interval_v34.py', 'continuum-v34-candidate.js',
               'centre-v34-bound-design.json', 'centre-v34-fixture-integrity.json', START.name]},
           'limits': 'Sampled float64/FD smooth-leaf reaches, cap join and local clipped shell overlap only. Not actual GPU jets, interval roundoff proof, global topology, antialiasing, cost or realism.'}
    assert out['base_leaf_reach_samples'] == 72000 and out['clearance_samples'] == 12000
    save(OUT, out)
    print(json.dumps({'passed': passed, 'base_leaf_reach_samples': 72000,
                      'clearance_samples': 12000, 'attachment_groups': len(attachment)}))
    assert passed, 'Hold: preserve failed one-shot; no replay'


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        if START.exists() and not FAILURE.exists() and not OUT.exists():
            save(FAILURE, {'passed': False, 'exception': repr(exc), 'traceback': traceback.format_exc()})
        raise
