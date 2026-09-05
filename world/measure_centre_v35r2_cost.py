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
from cost_lifecycle_v35r2 import Lifecycle, atomic_json, install_signal_receipts, restore_signals

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v35r2-cost-review.json'
RAW = HERE / 'centre-v35r2-cost-raw.json'
assert not OUT.exists() and not RAW.exists(), 'One-shot paired experiment'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

for name, key in [('centre-v35r2-bounds-check.json', 'source_hashes'),
                  ('numeric-candidate-v35r2-check.json', 'files'),
                  ('centre-v35r2-first-root-check.json', 'source_hashes')]:
    receipt = read(name)
    assert receipt['passed'] and all(digest(n) == h for n, h in receipt[key].items())

from runtime_centre_v35r2 import fixture_gate
implementation = fixture_gate()
assert implementation['static_passed']
assert all(digest(n) == h for n, h in implementation['files'].items())
before = {n: digest(n) for n in implementation['protected']}
assert before == implementation['protected']
files = ['continuum-v35r2-unshared-reference.js', 'continuum-v35r2-candidate.js',
         'gpu_cost_v35r2_parent.html', 'gpu_cost_v35r2_candidate.html',
         'centre-v35r2-fixture-integrity.json', 'centre-v35r2-bounds-check.json',
         'numeric-candidate-v35r2-check.json', 'centre-v35r2-first-root-check.json',
         'cost_lifecycle_v35r2.py', 'runtime_centre_v35r2.py', Path(__file__).name]
source_hashes = {n: digest(n) for n in files}
pairs, errors = [], []
failure = None
limits = ('Identical NEW v35r2 geometry/march; parent means unshared reference, candidate means retained common jets. Not a v35r2-v33r6 speedup. New balanced-order 12-pair sparse SwiftShader experiment. Same instrumentation and JS timing boundaries; '
          'no warmup or acceptance preconditioning. Includes first-call compilation/driver/readback costs. '
          'One pair per case, not a statistical speedup test. Does not isolate GPU execution, cold compilation, '
          'register pressure or shaded-frame cost; cannot predict original-resolution acceptance. '
          'Prefix counts are source-level evaluation estimates, not GPU instruction counts. '
          'Per-arm receipt I/O is outside both timed boundaries, but can perturb between-arm host/cache/queue state. '
          'Catchable failures are recorded; a hard kill leaves the last durable lifecycle event incomplete, with unknown cause.')
# Persist a started receipt before any browser work; partial failures cannot be
# silently replayed or mistaken for a completed sample.
journal = Lifecycle(HERE / 'centre-v35r2-cost-lifecycle')
atomic_json(RAW, {'started': True, 'pairs': [], 'source_hashes': source_hashes})
journal.record('runner_started', source_hashes=source_hashes)
active = {'stage': 'browser_launch'}
old_signals = install_signal_receipts()
try:
    with sync_playwright() as p:
        journal.record('browser_launch_started')
        browser = p.chromium.launch(headless=True, args=ARGS)
        journal.record('browser_launched')
        pages = {}
        for arm in ['parent', 'candidate']:
            active = {'stage': 'page_setup', 'arm': arm}
            journal.record('page_setup_started', **active)
            page = browser.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.goto((HERE / f'gpu_cost_v35r2_{arm}.html').as_uri())
            pages[arm] = page
            journal.record('page_setup_completed', **active)
        for t in [2.4077, 3.5242, 4.895]:
            for z in [8, -6]:
                for high in [1, 0]:
                    order = ['parent', 'candidate'] if len(pairs) % 2 == 0 else ['candidate', 'parent']
                    pair = {'time': t, 'z': z, 'high': high, 'order': order, 'first_pair': not pairs}
                    for arm in order:
                        assert not errors, 'Browser errors invalidate this experiment: '+repr(errors)
                        active = {'stage': 'arm', 'pair': len(pairs)+1, 'arm': arm, 'time': t, 'z': z, 'high': high}
                        case = journal.arm(active, lambda: pages[arm].evaluate('a=>runCase(...a)', [z, t, high, 49, 33]))
                        assert not errors, 'Browser errors invalidate readbacks: '+repr(errors)
                        pair[arm] = case
                    pairs.append(pair)
                    atomic_json(RAW, {'started': True, 'pairs': pairs, 'errors': errors,
                                      'source_hashes': source_hashes})
                    journal.record('pair_completed', pair=len(pairs))
                    print(f'PAIR {len(pairs)}/12 z={z} t={t} high={high}: '
                          f'{pair["parent"]["gpu_three_readbacks_seconds"]:.3f} -> '
                          f'{pair["candidate"]["gpu_three_readbacks_seconds"]:.3f}s', flush=True)
        active = {'stage': 'browser_close'}
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
    journal.record('browser_phase_finished', failure=failure, complete_pairs=len(pairs), last_active=active)

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
        'gradients_bit_equal': old['gradientSlope'] == new['gradientSlope'],
        'points_bit_equal': old['points'] == new['points'],
        'max_depth_delta': float(np.max(abs(np.array(old['hits']).reshape(-1, 4)[:, 0] - np.array(new['hits']).reshape(-1, 4)[:, 0]))),
        'parent_mean_prefix_evaluations': float(old_prefix.mean()),
        'candidate_mean_prefix_evaluations': float(new_prefix.mean()),
        'parent_three_seconds': old['gpu_three_readbacks_seconds'],
        'candidate_three_seconds': new['gpu_three_readbacks_seconds'],
        'parent_outer_four_seconds': old['outer_four_readbacks_seconds'],
        'candidate_outer_four_seconds': new['outer_four_readbacks_seconds'],
    })
events=[json.loads(p.read_text()) for p in sorted(journal.directory.glob('*.json'))]
lifecycle_complete=(sum(e['event']=='arm_completed' for e in events)==24
    and sum(e['event']=='arm_started' for e in events)==24
    and any(e['event']=='browser_closed' for e in events)
    and not any(e['event'].endswith('_failed') for e in events))
balanced=sum(p['order']==['parent','candidate'] for p in pairs)==6 and sum(p['order']==['candidate','parent'] for p in pairs)==6
complete = failure is None and len(pairs) == 12 and not errors and lifecycle_complete and balanced
work = complete and all(c['hits_bit_equal'] and c['counts_bit_equal'] and c['gradients_bit_equal'] and c['points_bit_equal'] and
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
journal.record('review_ready', complete=complete, capture_cost_gate_passed=bool(work and not_slower and unchanged))
fixture_gate()
result = {'lifecycle_complete':lifecycle_complete,'balanced_order':balanced,'complete': complete, 'work_not_worse': work, 'measured_wall_not_worse': not_slower,
          'capture_cost_gate_passed': bool(work and not_slower and unchanged),
          'pairs': comparisons, 'wall': wall, 'errors': errors, 'failure': failure,
          'protected_before': before, 'protected_after': after,
          'source_hashes': {**source_hashes, **journal.hashes(), RAW.name: digest(RAW.name)}, 'limits': limits}
atomic_json(OUT, result)
print(json.dumps({k: result[k] for k in ['complete', 'work_not_worse', 'measured_wall_not_worse',
                                      'capture_cost_gate_passed', 'wall', 'errors', 'failure']}), flush=True)
assert result['capture_cost_gate_passed'], 'Hold capture: inspect completed evidence; no replay/promotion'
