"""Saved-only closure of the immutable r2 runtime failure. No browser or sampling."""
import json
import os
from collections import Counter
import probe_centre_v34_staged_arithmetic_r2 as p


def main():
    p.gate()
    prefix = p.PREFIX
    prep = p.read(prefix + '-preparation-integrity.json')
    manifest = prefix + '-runtime-integrity.json'
    assert not (p.HERE / manifest).exists()
    p.save(prefix + '-runtime-close-started.json', {'saved_only': True})
    receipt = p.read(prefix + '-runtime-once-exit.json')
    launch = p.read(prefix + '-runtime-once-launch.json')
    assert receipt['actual_exit'] == 1 and receipt['launcher_error'] is None
    assert receipt['log_sha256'] == p.digest(prefix + '-runtime-once.log')
    assert receipt['launch_sha256'] == p.digest(prefix + '-runtime-once-launch.json')
    assert launch['preparation_sha256'] == p.digest(prefix + '-preparation-integrity.json')
    assert launch['script_sha256'] == p.digest(launch['script'])
    assert launch['launcher_sha256'] == p.digest('run_centre_v34_staged_arithmetic_r2_once.py')
    assert launch['freeze_sha256'] == p.digest(prefix + '-freeze.json')
    assert p.read(prefix + '-started.json')['launch_sha256'] == receipt['launch_sha256']
    r = p.read(prefix + '-result.json')
    p.verify(r['events'])
    names = [prefix + '-event-' + str(i).zfill(3) + '.json' for i in range(28)]
    assert list(r['events']) == names
    assert sorted(f.name for f in p.HERE.glob(prefix + '-event-*')) == names
    events = [p.read(n) for n in names]
    for i, e in enumerate(events):
        assert e['previous_sha256'] == (p.digest(names[i-1]) if i else None)
    kinds = ['inputs', 'browser-launch-intent', 'browser-launched', 'plan']
    kinds += ['step-intent', 'step-result', 'assessment'] * 6
    kinds += ['dispose-intent', 'dispose-result', 'dispose-assessment', 'page-closed', 'browser-closed', 'failure']
    assert [e['kind'] for e in events] == kinds
    assert events[0]['payload']['seeds_sha256'] == p.digest(p.SEEDS)
    assert events[0]['payload']['texture_sha256'] == p.digest(p.TEXTURE)
    assert events[1]['payload']['args'] == p.ARGS
    plan = events[3]['payload']
    assert plan == p.read(prefix + '-static.json')['plan'] and len(plan) == 126
    texels = p.inputs()
    leaves = p.read(p.SEEDS)['leaves']
    assessments = []
    for i in range(6):
        intent, result, assessment = [e['payload'] for e in events[4+3*i:7+3*i]]
        request = dict(plan[i])
        if request['op'] == 'shared':
            request['data'] = texels
        assert intent == request and result['step'] == intent
        if 'data' in intent:
            assert [p.bit(x) for x in intent['data']] == [p.bit(x) for x in texels]
        assert result['before'] == result['after'] == {'errors': [], 'drained': True}
        assert result['exception'] is None and not result['skipped'] and not result['contextLost']
        assert p.assess(result, leaves, texels, {}) == assessment
        assert assessment['classification'] == ('fatal-input' if i == 5 else 'ok')
        assessments.append(assessment)
    assert assessments == r['assessments']
    shared = events[20]['payload']
    actual = shared['value']['input']
    expected_bits = [p.bit(x) for x in texels]
    assert len(actual['values']) == len(actual['bits']) == 1024
    assert actual['values'] == texels
    differences = [i for i, (a, b) in enumerate(zip(actual['bits'], expected_bits)) if a != b]
    zero_indices = [i for i, b in enumerate(expected_bits) if b == 0]
    assert differences == zero_indices and len(differences) == 905
    assert all(actual['bits'][i] == 0x80000000 for i in differences)
    assert [p.bit(x) for x in actual['values']] == actual['bits']
    assert [p.bit(x) for x in shared['step']['data']] == actual['bits']
    assert {k:v for k,v in shared['value'].items() if k != 'input'} == {
        'width': 128, 'height': 1, 'textureHeight': 2, 'targetType': 1015}
    disposal = events[23]['payload']
    assert disposal['before'] == disposal['after'] == {'errors': [], 'drained': True}
    assert disposal['exception'] is None and not disposal['contextLost'] and not disposal['skipped']
    assert disposal['value'] == {'resourcesDisposed': 3, 'rendererDisposed': True}
    assert p.assess(disposal, leaves, texels, {}) == events[24]['payload']
    assert events[24]['payload']['classification'] == 'fatal-disposal'
    assert events[25]['payload'] == events[26]['payload'] == {}
    assert events[27]['payload']['error'] == r['failure'] == 'fatal-input: {"op": "shared"}'
    for flag in ('complete', 'infrastructure_clean', 'synthetic_uniform_candidate_supported',
                 'numeric_passed', 'first_root_certified', 'capture_permitted'):
        assert r[flag] is False
    assert r['new_images'] == 0 and not p.supported(assessments, False)
    assert len(r['browser_messages']) == 1
    warning = r['browser_messages'][0]
    assert warning['kind'] == 'console' and warning['type'] == 'warning' and 'deprecated' in warning['text']
    review = {
        'saved_evidence_verified': True, 'actual_exit': 1, 'launcher_error': None,
        'events': 28, 'planned_stages': 126, 'completed_stages': 6,
        'classifications': dict(Counter(a['classification'] for a in assessments)),
        'input_components': 1024, 'input_numeric_mismatches': 0,
        'input_bit_mismatches': 905, 'positive_to_negative_zero_indices': differences,
        'nonzero_components_bit_exact': 119, 'returned_request_has_same_zero_sign_changes': True,
        'all_executed_gl_intervals_clean': True, 'arithmetic_arms': 0, 'readbacks': 0,
        'disposal_report': disposal['value'], 'disposal_classification': 'fatal-disposal',
        'page_and_browser_closed': True, 'synthetic_uniform_candidate_supported': False,
        'interpretation': 'Input identity failed before rendering. Zero-sign changes are already present in the returned request and CPU Float32Array bits; exact transport origin is not localized. No GPU arithmetic or compiler inference.'}
    next_work = ('Verify centre-v34-staged-arithmetic-r2-runtime-integrity.json files/protected/display and '
                 'runtime-close-once actual-exit0 receipt (hashes for launch/log/script included in receipt). '
                 'Prepare a distinct transport-only investigation of positive/negative-zero serialization and '
                 'partial resource-disposal accounting. Preserve r2; no replay or relaxed bit equality. '
                 'No new arithmetic browser run, v35, field/roots/cost/capture/acceptance until separately justified preparation.')
    paragraph = ('Frozen r2 runtime ONCE actual exit1, no launcher error: 6/126 stages and 28 hash-chained events. '
                 'Shared input failed exact bits: all 905 positive zeros became negative zeros; 119 nonzero components '
                 'bit-exact, numeric values equal. Returned request and CPU Float32Array already show the changed signs; '
                 'transport origin not localized. Every executed GL interval clean. No material/compile/render/readback '
                 'or arithmetic arm reached. Cleanup reported 3 resources and renderer disposed; fixed expected count8 '
                 'produced fatal-disposal. Page/browser close recorded; final failure string retains fatal-input. '
                 'One deprecation warning, no page/console errors. No arithmetic support or evidence against the hypothesis.')
    review_text = ('# Staged arithmetic r2 runtime CLOSED — input failure; no arithmetic results\n\n' + paragraph +
                  '\n\nSaved-only review verifies preparation, actual-exit receipts, full event chain, ordering and '
                  'replayed assessments. It does not run a browser or alter the frozen attempt. Three resources were '
                  'registered in shared setup; five materials were never reached. The disposal count classification '
                  'is retained, not silently repaired; it alone does not establish a resource leak.\n\n'
                  'Original exact-jet/716-of-720 reference failures remain. No field equality, earliest roots, cost, '
                  'image, realism or acceptance claim. latest.png remains inspected REJECTED GAME v33r6.\n\n'
                  '## Next bounded phase\n\n' + next_work + '\n')
    notes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes.startswith(b'\xef\xbb\xbf')
    body = notes.decode('utf-8-sig')
    before, old_next = body.split('## Exact next bounded work\n')
    assert 'run_centre_v34_staged_arithmetic_r2_once.py runtime ONCE' in old_next
    before = before.split('\n', 1)[1]
    new_notes = ('# Active: REDIRECT4 — staged arithmetic r2 runtime CLOSED input FAIL; no arithmetic results\n' +
                 before + '## Staged arithmetic r2 runtime CLOSED — input FAIL; no replay\n- ' + paragraph +
                 '\n- Saved-only closure verifies receipts/events/assessments and preserves all failures. '
                 'Protected/display hashes verified; prior display archived; NOTES once/BOM retained. '
                 'latest unchanged inspected REJECTED GAME v33r6; no new image, promotion or acceptance run. '
                 'All19 realism/source/coverage/route/full acceptance unfinished.\n\n## Exact next bounded work\n' + next_work + '\n')
    readme = (p.HERE / 'README.md').read_text()
    matching = [line for line in readme.splitlines() if line.startswith('Distinct [staged arithmetic r2 preparation]')]
    assert len(matching) == 1
    replacement = ('Distinct [staged arithmetic r2 runtime](centre-v34-staged-arithmetic-r2-runtime-review.md) '
                   'is **CLOSED input FAIL; actual exit1**. All 905 positive-zero inputs changed sign before rendering; '
                   'GL intervals clean, no arithmetic arms/readbacks. Partial cleanup count failure and browser close '
                   'retained. No retry, support, v35 or visual progress; prior numerical/realism failures remain.')
    assert 'r2 preparation CLOSED static PASS' in (p.HERE / 'status.txt').read_text()
    updates = {'NOTES.md': b'\xef\xbb\xbf' + new_notes.encode(),
               'README.md': readme.replace(matching[0], replacement, 1).encode(),
               'status.txt': ('Isolated v34 numerical FAIL retained. Staged arithmetic r2 runtime CLOSED actual exit1: '
                              'fatal-input, 905 positive-to-negative zeros, 6/126 stages, 28events; no arithmetic results. '
                              'Cleanup count failure retained, browser closed. latest unchanged inspected REJECTED GAME v33r6; '
                              'live/defaults/ledgers unchanged; all19 unfinished. ' + next_work + '\n').encode()}
    archives = {}
    for name in updates:
        archive = name + '-before-' + prefix + '-runtime'
        assert not (p.HERE / archive).exists()
        archives[archive] = p.digest(name)
    p.save(prefix + '-runtime-review.json', review)
    with (p.HERE / (prefix + '-runtime-review.md')).open('x') as f:
        f.write(review_text); f.flush(); os.fsync(f.fileno())
    for name, content in updates.items():
        with (p.HERE / (name + '-before-' + prefix + '-runtime')).open('xb') as f:
            f.write((p.HERE / name).read_bytes()); f.flush(); os.fsync(f.fileno())
        with (p.HERE / name).open('wb') as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
    files = dict(prep['files'])
    files.update({f.name:p.digest(f.name) for f in p.HERE.glob(prefix + '-*') if f.is_file()
                  and not f.name.startswith(prefix + '-runtime-close-once')})
    files.update(archives)
    for name in ('close_centre_v34_staged_arithmetic_r2_runtime.py', 'run_centre_v34_staged_arithmetic_r2_runtime_close_once.py'):
        files[name] = p.digest(name)
    p.verify(files); p.verify(prep['protected'])
    assert p.digest('latest.png') == prep['display']['latest.png']
    display = {name:p.digest(name) for name in prep['display']}
    p.save(manifest, {'phase': 'r2 runtime CLOSED input FAIL; no arithmetic results',
                     'files': files, 'protected': prep['protected'], 'display': display,
                     'prior_display': prep['display'], 'archived_display': archives,
                     'runtime_run': True, 'actual_exit': 1, 'saved_evidence_verified': True,
                     'synthetic_uniform_candidate_supported': False, 'numeric_passed': False,
                     'capture_permitted': False, 'new_images': 0})
    p.verify(p.read(manifest)['files']); p.verify(display)
    print('Saved-only closure verified:', len(files), 'evidence files; runtime actual exit1 retained')


if __name__ == '__main__':
    main()
