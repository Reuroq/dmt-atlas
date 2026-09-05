"""Close saved v34 numerical failure; no field, browser, root or cost execution."""
import hashlib
import json
from pathlib import Path

import numpy as np
from gpu_csg_v34 import BASE_KEYS, EXPANDED_KEYS, expand_jets

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v34-numerical-failure'


def read(name):
    return json.loads((HERE / name).read_text())


def digest(name):
    with (HERE / name).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    archive = 'NOTES-before-centre-v34-numerical-failure.md'
    new_names = [archive, PREFIX + '-review.md', PREFIX + '-analysis.json',
                 PREFIX + '-integrity.json', PREFIX + '-started.json']
    assert not any((HERE / n).exists() for n in new_names), 'Never replay closure'
    fixture = read('centre-v34-fixture-integrity.json')
    assert fixture['integrity_passed'] and fixture['fixtures_complete']
    for group in ['files', 'protected', 'display']:
        verify(fixture[group])
    bounds = read('centre-v34-bounds-check.json')
    gpu = read('numeric-candidate-v34-check.json')
    verify(bounds['source_hashes'])
    verify(gpu['files'])
    assert bounds['passed'] and not gpu['passed']
    assert bounds['protected_before'] == bounds['protected_after'] == fixture['protected']
    assert bounds['base_leaf_reach_samples'] == 72000 and bounds['clearance_samples'] == 12000
    for key, count in [('cases', 12), ('clearance', 2), ('cap_join', 12), ('filter', 12), ('attachment', 28)]:
        assert len(bounds[key]) == count and all(c['passed'] for c in bounds[key]), key
    prior_prefix = 'close-centre-v34-numerical-failure-once'
    prior_exit = read(prior_prefix + '-exit.json')
    prior_launch = read(prior_prefix + '-launch.json')
    assert prior_exit['actual_exit'] == 1
    assert prior_exit['log_sha256'] == digest(prior_prefix + '.log')
    assert prior_exit['launch_sha256'] == digest(prior_prefix + '-launch.json')
    assert prior_launch['script_sha256'] == digest('close_centre_v34_numerical_failure.py')
    receipts = ['close_centre_v34_numerical_failure.py', prior_prefix + '.log',
                prior_prefix + '-exit.json', prior_prefix + '-launch.json']
    for label, expected_exit, script in [('bounds', 0, 'check_centre_v34_bounds.py'),
                                         ('gpu', 1, 'probe_numeric_candidate_v34.py')]:
        prefix = f'run-centre-v34-{label}-once'
        result, launch = read(prefix + '-exit.json'), read(prefix + '-launch.json')
        assert result['actual_exit'] == expected_exit and result['script'] == script
        assert result['log_sha256'] == digest(prefix + '.log')
        assert result['launch_sha256'] == digest(prefix + '-launch.json')
        assert launch['script'] == script and launch['script_sha256'] == digest(script)
        assert launch['fixture_manifest'] == digest('centre-v34-fixture-integrity.json')
        start_name = f'centre-v34-{label}-started.json'
        assert read(start_name)['fixture_manifest'] == launch['fixture_manifest']
        receipts.extend([prefix + '.log', prefix + '-exit.json', prefix + '-launch.json', start_name])
    failure = read('centre-v34-gpu-failure.json')
    assert failure['passed'] is False and failure['failure'] == 'AssertionError()'
    assert 'AssertionError' in (HERE / 'run-centre-v34-gpu-once.log').read_text()
    blocked_patterns = ['centre-v34-first-root*', 'centre-v34-roots-*', 'centre-v34-cost-*',
                        'run-centre-v34-roots-once*', 'run-centre-v34-cost-once*',
                        'diagnostic-centre-v34*', 'centre-v34-integrity.json']
    for pattern in blocked_patterns:
        assert not list(HERE.glob(pattern)), pattern

    raw = read('numeric-candidate-v34-raw.json')
    cases = gpu['cases']
    assert len(raw) == len(cases) == 48 and gpu['rays'] == 75996 and not gpu['errors']
    assert all(not c['passed'] and c['misses'] == 0 for c in cases)
    lifecycle = sorted((HERE / 'centre-v34-gpu-lifecycle').glob('*.json'))
    assert len(lifecycle) == 100
    events = [read(p.relative_to(HERE).as_posix()) for p in lifecycle]
    expected_events = ['browser_launch_started', 'browser_launched'] + ['case_started', 'case_completed'] * 48 + ['browser_close_started', 'browser_closed']
    assert [e['event'] for e in events] == expected_events
    assert [e['sequence'] for e in events] == list(range(100))
    assert len({e['pid'] for e in events}) == 1
    assert all(a['monotonic'] <= b['monotonic'] for a, b in zip(events, events[1:]))
    counts = np.zeros(11, dtype=np.int64)
    maxima = np.zeros(11)
    per_case = []
    missing = []
    identity = ['width', 'height', 'z', 'time', 'high']
    for i, (r, c) in enumerate(zip(raw, cases)):
        assert events[3 + 2*i]['case'] == r, i
        assert all(events[2 + 2*i][k] == r[k] == c[k] for k in identity), i
        n = r['width'] * r['height']
        assert c['rays'] == n and len(c['references']) == 15
        base = np.stack([np.asarray(r['leaves'][k], dtype=np.float32).reshape(n, 4) for k in BASE_KEYS], axis=1)
        jets = np.stack([np.asarray(r['leaves'][k], dtype=np.float32).reshape(n, 4) for k in EXPANDED_KEYS], axis=1)
        diff = np.abs(expand_jets(base) - jets)
        assert np.isfinite(diff).all()
        cc = np.count_nonzero(diff, axis=(0, 2))
        mm = diff.max(axis=(0, 2))
        counts += cc
        maxima = np.maximum(maxima, mm)
        assert float(mm.max()) == c['expanded_jet_replay_error'] > 0
        per_case.append({**{k: c[k] for k in identity},
                         'mismatching_components': dict(zip(EXPANDED_KEYS, map(int, cc))),
                         'max_absolute_error': dict(zip(EXPANDED_KEYS, map(float, mm)))})
        for ref in c['references']:
            if ref.get('missing_reference'):
                missing.append({**{k: c[k] for k in identity}, 'ray': ref['ray']})
    assert counts.tolist() == [0, 0, 0, 0, 0, 0, 36599, 40662, 0, 0, 0]
    assert maxima[6] == 1.1920928955078125e-7 and maxima[7] == 5.960464477539063e-8
    assert [(m['width'], m['height'], m['z'], m['time'], m['high'], m['ray']) for m in missing] == [
        (48, 32, 8, 4.895, 0, 839), (48, 32, -6, 8, 0, 745),
        (49, 33, -6, 8, 1, 807), (49, 33, -6, 8, 1, 809)]
    found = [ref for c in cases for ref in c['references'] if not ref.get('missing_reference')]
    assert len(found) == gpu['reference_rays'] == 716
    assert max(r['difference'] for r in found) == gpu['max_reference_difference'] < .03
    exact = ['max_csg_replay_error', 'max_saved_gradient_replay_error', 'aperture_replay_error', 'cheap_full_jet_error']
    thresholds = {'max_all_leaf_scalar_error': .001, 'max_all_leaf_gradient_error': .005,
                  'cheap_scalar_error': .001, 'cheap_gradient_error': .005,
                  'lower_scalar_error': .001, 'lower_gradient_error': .005,
                  'max_field_cpu_gpu_difference': .001}
    assert all(all(c[k] == 0 for k in exact) and all(c[k] < v for k, v in thresholds.items())
               and c['count_invariants_passed'] and c['maximum_gpu_lower_minus_full'] <= 0
               and c['max_bound_ratio'] <= 1.001 for c in cases)
    analysis = {'numeric_passed': False, 'method': 'Saved receipts/readbacks only; float32 replay, no field samples or runtime.',
                'actual_exits': {'bounds': 0, 'gpu': 1}, 'cases': 48, 'rays': 75996,
                'browser_errors': 0, 'gpu_misses': 0, 'failed_expanded_replay_cases': 48,
                'mismatching_components': dict(zip(EXPANDED_KEYS, map(int, counts))),
                'max_absolute_error': dict(zip(EXPANDED_KEYS, map(float, maxima))),
                'per_case': per_case, 'fixed_references_found': 716, 'fixed_references_expected': 720,
                'missing_references': missing, 'worst_found_reference_difference': gpu['max_reference_difference'],
                'other_saved_gates_passed': True, 'exact_replay_keys': exact,
                'threshold_maxima': {k: max(c[k] for c in cases) for k in thresholds},
                'lifecycle_events': 100, 'durable_completed_cases': 48, 'browser_closed': True,
                'independent_interval_roots_run': False, 'cost_run': False, 'capture_run': False,
                'causes': 'Unresolved for expanded replay differences and missing fixed references; no inference of harmless rounding, tangency, missed surface or oracle bug.'}

    original = (HERE / 'NOTES.md').read_bytes()
    assert original.startswith(b'\xef\xbb\xbf')
    notes = original.decode('utf-8-sig')
    assert notes.startswith('# Active: REDIRECT4 — v34 fixtures COMPLETE; numerical gates next; no runtime')
    assert notes.count('## Exact next bounded work') == 1
    readme = (HERE / 'README.md').read_text()
    paragraphs = readme.split('\n')
    matches = [i for i, p in enumerate(paragraphs) if p.startswith('Isolated **v34 lamina rebuild implementation/proof CLOSED; runtime untested**.')]
    assert len(matches) == 1
    assert (HERE / 'status.txt').read_text().startswith('Isolated v34 fixtures COMPLETE/static PASS:')
    review = '''# v34 numerical phase CLOSED — FAIL; downstream held

The foreground bounds run exited **0**; the foreground GPU run exited **1** at
its final `assert out['passed']`. Both actual exits, launch records and log hashes
are verified. No probe was rerun for this closure. The first closure attempt exited 1 at a
README paragraph-boundary assertion before any documentation/output write. Its
source/log/launch/actual exit are preserved and bound. This r2 closure uses the
unique README line; numerical checks and limits are unchanged.

Bounds retain sampled PASS: 72,000 leaf/reach and 12,000 clearance samples;
12 cap, 12 filter and 28 attachment groups pass. This is not a universal proof.

The GPU completed 48 cases / 75,996 rays, with no recorded browser errors or GPU
misses. All 48 cases fail exact expanded-jet replay. Saved float32 readbacks show
36,599 mismatching childAxial components (maximum 1.1920928955078125e-7) and
40,662 childAngular components (maximum 5.960464477539063e-8). The other nine
expanded leaves match exactly. The equality requirement is unchanged; small
differences are not waived or diagnosed as harmless rounding.

Composite, aperture, saved-gradient and cheap/full jet replay are exact.
Recorded smooth-leaf gradient/scalar, directional-bound, lower-field domination
and count checks pass. These partial results do not turn the failed gate into PASS.

Only 716/720 fixed-grid references were found; their worst depth difference is
0.0011048514545066723 (limit <0.03). Missing references:

| Grid | Camera | Time | Mode | Ray |
| --- | --- | --- | --- | --- |
| 48×32 | entry z=8 | 4.895 | LOW | 839 |
| 48×32 | deep z=-6 | 8 | LOW | 745 |
| 49×33 | deep z=-6 | 8 | HIGH | 807 |
| 49×33 | deep z=-6 | 8 | HIGH | 809 |

The saved missing flags mean the original 0.003-spaced scan found no strict
adjacent-sample sign change from depth zero to GPU depth+1. No new scan was run.
They do not prove absence of a surface, tangency, a marcher error or an oracle bug.
The replay differences and missing-reference causes remain unresolved.

All 100 durable lifecycle events are bound, with 48 started/completed pairs
matching the raw cases and a browser-closed event. This establishes recorded
completion, not numerical success. Independent interval roots, matched cost and
capture did NOT run. No performance, temporal or v34 realism claim is possible.

The failure integrity manifest binds fixture evidence, protected files, numerical
receipts, raw cases, lifecycle, launch/log/actual exits and this saved-evidence
analysis. It is NOT `centre-v34-integrity.json` and never authorizes capture.
Historical fixture/display hashes remain in their immutable manifest; pre-closure
NOTES are archived byte-for-byte with BOM. README/status/NOTES now describe failure.
latest.png remains the once-inspected REJECTED GAME v33r6 entry diagnostic;
there is no new image to inspect or substitute. Live/defaults/source/manual
ledgers remain unchanged; all19/source/coverage/route/full acceptance unfinished.

Next: bounded read-only source/saved-evidence investigation of the two failure
classes, separately. Preserve every v34 artifact and original gate. Do not run
dependent gates or replay failed/completed probes. Establish a justified change
before preparing a new isolated revision and new one-shot experiment.
'''
    next_work = ('Investigate expanded-jet arithmetic and the four fixed-grid missing references separately using targeted source and saved evidence only; causes unresolved. Preserve all v34 fixtures/probes/receipts and exact original limits. No v34 replay, dependent interval roots/cost/capture, promotion or frame-pump change. Establish a justified isolated revision and distinct new experiment before any new runtime. All19/source/coverage/route/full acceptance remain unfinished.\n')
    section = '''## v34 numerical phase CLOSED — FAIL; no replay
- Foreground bounds ONCE actual exit0:72000leaf/reach+12000clearance and12cap/12filter/28attachment groups PASS. GPU ONCE actual exit1:48cases/75996rays,zero recorded browser errors/GPU misses,all48 fail exact expanded-jet replay.
- Saved childAxial36599 mismatching components,max1.1920928955078125e-7;childAngular40662,max5.960464477539063e-8;other9expanded leaves exact. Composite/aperture/saved-gradient/cheap-full replay exact;recorded gradient/scalar/bound/count gates PASS. Equality not relaxed;cause unresolved.
- Fixed references716/720,worst found difference.0011048514545066723. Missing48x32 entry4.895LOW ray839;48x32 deep8LOW745;49x33 deep8HIGH807/809. Original scan found no strict sign change;no new scan or cause inference. Independent interval roots,cost,capture NOT RUN.
- Initial closure exit1 at README paragraph-boundary assertion before writes;source/log/exit preserved. Revised close_centre_v34_numerical_failure_r2.py uses unique README line and verifies saved evidence and100lifecycle events/48completed cases/browser close;centre-v34-numerical-failure-integrity.json binds fixture/protected/numerical/log/actual-exit/lifecycle/review hashes. NOT passing centre-v34-integrity.json;capture blocked. No browser/field sampling/PNG/inspection/acceptance rerun in closure. README/status current;latest still inspected REJECTED GAME v33r6 entry. NOTES once,BOM preserved,prior bytes archived;live/defaults/ledgers unchanged.

'''
    notes = notes.split('## Exact next bounded work')[0] + section + '## Exact next bounded work\n' + next_work
    notes = notes.replace('# Active: REDIRECT4 — v34 fixtures COMPLETE; numerical gates next; no runtime',
                          '# Active: REDIRECT4 — v34 numerical CLOSED FAIL; downstream blocked', 1)
    paragraphs[matches[0]] = ('Isolated **v34 numerical phase CLOSED — FAIL**. Bounds ONCE actual exit0:72,000leaf/reach+12,000clearance PASS. GPU ONCE actual exit1:48cases/75,996rays,zero recorded browser errors/GPU misses;all48 fail exact expanded-jet replay (childAxial/childAngular). Only716/720fixed references found;both failure causes unresolved. Other saved scalar/gradient/bound/count and composite/aperture/normal replay gates pass but do not override failure. Independent interval roots,matched cost,capture NOT RUN. See [saved-evidence failure review](centre-v34-numerical-failure-review.md) and [failure integrity](centre-v34-numerical-failure-integrity.json). Historical [fixture scope](centre-v34-fixtures-review.md) remains unchanged. No passing numerical authorization,no v34 image,no promotion/replay/prewarm/limit relaxation. Live/defaults/ledgers unchanged;latest remains the inspected REJECTED GAME v33r6 entry diagnostic. All19/source/coverage/route/full acceptance unfinished.')
    status = ('Isolated v34 numerical CLOSED FAIL:bounds ONCE actual exit0,72000leaf/reach+12000clearance PASS;GPU ONCE actual exit1,48cases/75996rays,zero browser errors/GPU misses,all48 expanded-jet replay FAIL(childAxial/childAngular). Fixed references716/720;causes unresolved. Independent interval roots/cost/capture NOT RUN;no replay or downstream execution. Saved evidence/log/exit/lifecycle/fixture/protected integrity verified. latest.png remains inspected REJECTED GAME v33r6 entry,not v34. Live/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished;no promotion or relaxed limits.\n')

    save(PREFIX + '-started.json', {'started': True, 'fixture_manifest': digest('centre-v34-fixture-integrity.json'), 'new_runtime': False})
    with (HERE / archive).open('xb') as stream:
        stream.write(original)
    save(PREFIX + '-analysis.json', analysis)
    with (HERE / (PREFIX + '-review.md')).open('x') as stream:
        stream.write(review)
    (HERE / 'README.md').write_text('\n'.join(paragraphs))
    (HERE / 'status.txt').write_text(status)
    (HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
    for group in ['files', 'protected']:
        verify(fixture[group])
    verify(gpu['files'])
    verify(bounds['source_hashes'])
    assert digest('latest.png') == fixture['display']['latest.png']
    assert digest(archive) == fixture['display']['NOTES.md']
    files = set(fixture['files']) | set(gpu['files']) | set(bounds['source_hashes']) | set(receipts)
    files.update(['centre-v34-fixture-integrity.json', 'centre-v34-bounds-check.json',
                  'numeric-candidate-v34-check.json', 'centre-v34-gpu-failure.json',
                  Path(__file__).name, *[n for n in new_names if not n.endswith('-integrity.json')]])
    files.update(p.relative_to(HERE).as_posix() for p in lifecycle)
    save(PREFIX + '-integrity.json', {'integrity_passed': True, 'numeric_passed': False,
         'capture_permitted': False, 'phase': 'CLOSED FAILURE',
         'files': {n: digest(n) for n in sorted(files)}, 'protected': fixture['protected'],
         'fixture_display_snapshot': fixture['display'],
         'display': {n: digest(n) for n in fixture['display']},
         'new_runtime_runs': 0, 'new_images': 0, 'limits': 'Evidence integrity only; no numerical, performance or realism PASS.'})
    print(json.dumps({'integrity_passed': True, 'numeric_passed': False, 'capture_permitted': False,
                      'files': len(files), 'protected': len(fixture['protected']), 'saved_cases': 48}))


if __name__ == '__main__':
    main()
