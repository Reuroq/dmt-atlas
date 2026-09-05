"""Freeze synthetic texture and four saved rays; no field or browser execution."""
import numpy as np
from centre_v34_followup_common import HERE, PREFIX, SOURCES, HISTORY, digest, read, save, historical


def cell(v):
    v = np.asarray(v, dtype=np.float32)
    return ((np.nextafter(v, np.float32(-np.inf)).astype(float) + v.astype(float))/2,
            (np.nextafter(v, np.float32(np.inf)).astype(float) + v.astype(float))/2)


def representable(lo, hi):
    low = np.float32(lo)
    low = np.where(low.astype(float) < lo, np.nextafter(low, np.float32(np.inf)), low)
    high = np.float32(hi)
    high = np.where(high.astype(float) > hi, np.nextafter(high, np.float32(-np.inf)), high)
    return low, high, low <= high


def main():
    assert not (HERE / (PREFIX + '-inputs.json')).exists(), 'Never replay preparation'
    historical()
    save(PREFIX + '-prepare-started.json', {'historical_manifest': digest(HISTORY)})
    raw = read('numeric-candidate-v34-raw.json')
    investigation = read('centre-v34-saved-investigation.json')
    texture = np.zeros((2, 128, 4), dtype='<f4')
    seeds = {'synthetic_not_recovered_gpu_intermediates': True, 'leaves': []}
    for row, (base, child, c1, c2, domain) in enumerate([
        ('axial', 'childAxial', -.62, .20, [-1., 1.]),
        ('angular', 'childAngular', -.90, .28, [0., 2.]),
    ]):
        a = np.concatenate([np.asarray(c['leaves'][base], dtype=np.float32).reshape(-1, 4)[:, 3] for c in raw])
        b = np.concatenate([np.asarray(c['leaves'][child], dtype=np.float32).reshape(-1, 4)[:, 3] for c in raw])
        mismatch = np.flatnonzero(b != np.float32(a + np.float32(c2)))
        folded = np.float32(np.float32(c1) + np.float32(c2))
        alo, ahi = cell(a); blo, bhi = cell(b)
        lo = np.maximum(alo - float(np.float32(c1)), blo - float(folded))
        hi = np.minimum(ahi - float(np.float32(c1)), bhi - float(folded))
        low, high, feasible = representable(lo, hi)
        selected = mismatch[np.linspace(0, len(mismatch)-1, 12, dtype=int)]
        values, labels, records = [], [], []

        def add(v, label):
            for relation, x in [('previous', np.nextafter(np.float32(v), np.float32(-np.inf))),
                                ('value', np.float32(v)),
                                ('next', np.nextafter(np.float32(v), np.float32(np.inf)))]:
                assert np.isfinite(x)
                bit = int(x.view(np.uint32))
                if bit not in [int(y.view(np.uint32)) for y in values]:
                    values.append(x); labels.append([])
                labels[[int(y.view(np.uint32)) for y in values].index(bit)].append(label + ':' + relation)

        for i in selected:
            record = {'flat_ray': int(i), 'saved_parent': float(a[i]), 'saved_child': float(b[i]),
                      'closed_outer_inverse_cell': [float(lo[i]), float(hi[i])],
                      'contains_binary32': bool(feasible[i]), 'chosen_predecessors': []}
            if feasible[i]:
                middle = np.clip(np.float32((lo[i] + hi[i])/2), low[i], high[i])
                for v in [low[i], middle, high[i]]:
                    record['chosen_predecessors'].append(float(v))
                    add(v, 'inverse-cell-' + str(i))
            records.append(record)
        for label, value in [('domain-low', domain[0]), ('domain-high', domain[1]),
                             ('parent-cancellation', -np.float32(c1)),
                             ('folded-child-cancellation', -folded), ('zero', 0.)]:
            add(value, label)
        assert 0 < len(values) <= 128
        texture[row, :len(values), 0] = values
        seeds['leaves'].append({'name': child, 'row': row, 'c1': float(np.float32(c1)),
            'c2': float(np.float32(c2)), 'folded': float(folded), 'theoretical_real_domain': domain,
            'selection': '12 evenly indexed saved mismatches, before representability filtering; all chosen cells retained',
            'outer_cell_caveat': 'Closed cells include ties; representability is not exact replay or recovered arithmetic.',
            'all_pairs': len(a), 'mismatches': len(mismatch),
            'all_no_binary32_flat_rays': np.flatnonzero(~feasible).tolist(),
            'mismatching_no_binary32_flat_rays': mismatch[~feasible[mismatch]].tolist(),
            'selected_cells': records, 'count': len(values), 'values': [float(x) for x in values],
            'bits': [int(x.view(np.uint32)) for x in values], 'labels': labels,
            'padding': 'Remaining texels contain +0 and are recorded but excluded from the unique-input count.'})
    with (HERE / (PREFIX + '-texture.f32')).open('xb') as stream:
        stream.write(texture.tobytes())
    save(PREFIX + '-seeds.json', seeds)
    rays = investigation['missing_references']
    assert len(rays) == 4 and [r['ray'] for r in rays] == [839, 745, 807, 809]
    save(PREFIX + '-rays.json', {'source_sha256': digest('centre-v34-saved-investigation.json'),
         'oracle_sha256': digest('field_centre_v34.py'), 'rays': rays,
         'spacing': .00005, 'half_width': .004, 'sample_count': 161, 'bisections': 24,
         'old_grid_step': .003, 'old_grid_origin': 0., 'old_grid_replay': False})
    files = SOURCES + [PREFIX + x for x in ['-texture.f32', '-seeds.json', '-rays.json', '-prepare-started.json']]
    save(PREFIX + '-inputs.json', {'historical_manifest': digest(HISTORY),
         'files': {name: digest(name) for name in files}, 'new_field_samples': 0, 'new_browser_runs': 0,
         'numeric_passed': False, 'capture_permitted': False})
    print('Frozen inputs:', [(s['name'], s['count'], len(s['all_no_binary32_flat_rays'])) for s in seeds['leaves']], flush=True)


if __name__ == '__main__':
    main()
