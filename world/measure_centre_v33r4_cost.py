"""One new paired sparse-ray experiment, not a historical probe rerun.

Identical four-readback instrumentation, dimensions and clocks; alternating
parent/candidate order. First calls are included, with no warmup. No renderer
acceptance, GPU isolation, compiler isolation or hardware-speed claim.
"""
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright
from verify import ARGS

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r4-cost-review.json'
RAW = HERE / 'centre-v33r4-cost-raw.json'
assert not OUT.exists() and not RAW.exists(), 'One-shot paired experiment'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

for name, key in [('centre-v33r4-bounds-check.json', 'source_hashes'),
                  ('numeric-candidate-v33r4-check.json', 'files'),
                  ('centre-v33r4-first-root-check.json', 'source_hashes')]:
    receipt = read(name)
    assert receipt['passed'] and all(digest(n) == h for n, h in receipt[key].items())

implementation = read('centre-v33r4-implementation.json')
assert implementation['static_passed']
assert all(digest(n) == h for n, h in implementation['files'].items())
before = {n: digest(n) for n in implementation['protected']}
assert before == implementation['protected']
files = ['continuum-v33r3-candidate.js', 'continuum-v33r4-candidate.js',
         'gpu_cost_v33r4_parent.html', 'gpu_cost_v33r4_candidate.html',
         'centre-v33r4-implementation.json', 'centre-v33r4-bounds-check.json',
         'numeric-candidate-v33r4-check.json', 'centre-v33r4-first-root-check.json',
         Path(__file__).name]
source_hashes = {n: digest(n) for n in files}
pairs, errors = [], []
failure = None
limits = ('New balanced-order 12-pair sparse SwiftShader experiment. Same instrumentation and JS timing boundaries; '
          'no warmup or acceptance preconditioning. Includes first-call compilation/driver/readback costs. '
          'One pair per case, not a statistical speedup test. Does not isolate GPU execution, cold compilation, '
          'register pressure or shaded-frame cost; cannot predict original-resolution acceptance. '
          'Prefix counts are source-level evaluation estimates, not GPU instruction counts.')
# Persist a started receipt before any browser work; partial failures cannot be
# silently replayed or mistaken for a completed sample.
RAW.write_text(json.dumps({'started': True, 'pairs': [], 'source_hashes': source_hashes}) + '\n')
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        pages = {}
        for arm in ['parent', 'candidate']:
            page = browser.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.goto((HERE / f'gpu_cost_v33r4_{arm}.html').as_uri())
            pages[arm] = page
        for t in [2.4077, 3.5242, 4.895]:
            for z in [8, -6]:
                for high in [1, 0]:
                    order = ['parent', 'candidate'] if len(pairs) % 2 == 0 else ['candidate', 'parent']
                    pair = {'time': t, 'z': z, 'high': high, 'order': order, 'first_pair': not pairs}
                    for arm in order:
                        start = time.monotonic()
                        case = pages[arm].evaluate('a=>runCase(...a)', [z, t, high, 49, 33])
                        case['outer_four_readbacks_seconds'] = time.monotonic() - start
                        pair[arm] = case
                    pairs.append(pair)
                    RAW.write_text(json.dumps({'started': True, 'pairs': pairs, 'errors': errors,
                                               'source_hashes': source_hashes}) + '\n')
                    print(f'PAIR {len(pairs)}/12 z={z} t={t} high={high}: '
                          f'{pair["parent"]["gpu_three_readbacks_seconds"]:.3f} -> '
                          f'{pair["candidate"]["gpu_three_readbacks_seconds"]:.3f}s', flush=True)
        browser.close()
except Exception as exc:
    failure = repr(exc)

comparisons = []
for pair in pairs:
    old, new = pair['parent'], pair['candidate']
    old_counts = np.array(old['counts']).reshape(-1, 4)
    new_counts = np.array(new['counts']).reshape(-1, 4)
    # One final sheetSample is emitted by this probe. Shaded-frame evaluations
    # are deliberately not estimated from a probe that truncates shading.
    old_prefix = old_counts[:, 0] + old_counts[:, 1] + old_counts[:, 3] + 1
    new_prefix = new_counts[:, 0] + new_counts[:, 3] + 1
    comparisons.append({
        **{k: pair[k] for k in ['time', 'z', 'high', 'order', 'first_pair']},
        'hits_bit_equal': old['hits'] == new['hits'],
        'counts_bit_equal': old['counts'] == new['counts'],
        'max_depth_delta': float(np.max(abs(np.array(old['hits']).reshape(-1, 4)[:, 0] - np.array(new['hits']).reshape(-1, 4)[:, 0]))),
        'parent_mean_prefix_evaluations': float(old_prefix.mean()),
        'candidate_mean_prefix_evaluations': float(new_prefix.mean()),
        'parent_three_seconds': old['gpu_three_readbacks_seconds'],
        'candidate_three_seconds': new['gpu_three_readbacks_seconds'],
        'parent_outer_four_seconds': old['outer_four_readbacks_seconds'],
        'candidate_outer_four_seconds': new['outer_four_readbacks_seconds'],
    })
complete = failure is None and len(pairs) == 12 and not errors
work = complete and all(c['hits_bit_equal'] and c['counts_bit_equal'] and
                        c['candidate_mean_prefix_evaluations'] < c['parent_mean_prefix_evaluations'] for c in comparisons)
wall = {}
for boundary in ['three_seconds', 'outer_four_seconds']:
    parent = np.array([c['parent_' + boundary] for c in comparisons])
    candidate = np.array([c['candidate_' + boundary] for c in comparisons])
    if len(parent):
        wall[boundary] = {'parent_total': float(parent.sum()), 'candidate_total': float(candidate.sum()),
                          'median_paired_ratio': float(np.median(candidate / parent)),
                          'first_pair_parent': float(parent[0]), 'first_pair_candidate': float(candidate[0])}
not_slower = complete and all(w['candidate_total'] <= w['parent_total'] and w['median_paired_ratio'] <= 1 for w in wall.values())
after = {n: digest(n) for n in before}
unchanged = before == after and all(digest(n) == h for n, h in source_hashes.items())
result = {'complete': complete, 'work_not_worse': work, 'measured_wall_not_worse': not_slower,
          'capture_cost_gate_passed': bool(work and not_slower and unchanged),
          'pairs': comparisons, 'wall': wall, 'errors': errors, 'failure': failure,
          'protected_before': before, 'protected_after': after,
          'source_hashes': {**source_hashes, RAW.name: digest(RAW.name)}, 'limits': limits}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['complete', 'work_not_worse', 'measured_wall_not_worse',
                                      'capture_cost_gate_passed', 'wall', 'errors', 'failure']}), flush=True)
assert result['capture_cost_gate_passed'], 'Hold capture: inspect completed evidence; no replay/promotion'
