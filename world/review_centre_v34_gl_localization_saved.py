"""One saved-only review; never launches a browser or samples a field."""
import struct
from collections import Counter
from probe_centre_v34_gl_localization import HERE, PREFIX, digest, gate, read, save, verify


def main():
    output = PREFIX + '-saved-review.json'
    assert not (HERE / output).exists(), 'Never replay a completed review'
    gate()
    receipt = read(PREFIX + '-once-exit.json')
    launch = read(PREFIX + '-once-launch.json')
    assert receipt['actual_exit'] == 1 and receipt['launcher_error'] is None
    assert receipt['log_sha256'] == digest(PREFIX + '-once.log')
    assert receipt['launch_sha256'] == digest(PREFIX + '-once-launch.json')
    assert launch['script_sha256'] == digest(launch['script'])
    assert launch['launcher_sha256'] == digest('run_centre_v34_gl_localization_once.py')
    assert launch['preparation_sha256'] == digest(PREFIX + '-preparation-integrity.json')
    assert read(PREFIX + '-started.json')['launch_sha256'] == receipt['launch_sha256']
    result = read(PREFIX + '-result.json')
    verify(result['events'])
    names = list(result['events'])
    assert names == [PREFIX + '-event-' + str(i).zfill(3) + '.json' for i in range(358)]
    assert set(names) == {p.name for p in HERE.glob(PREFIX + '-event-*.json')}
    events = [read(n) for n in names]
    for i, event in enumerate(events):
        assert event['previous_sha256'] == (digest(names[i-1]) if i else None)
    assert [e['kind'] for e in events[:3]] == ['browser-launch-intent', 'browser-launched', 'plan']
    plan = read(PREFIX + '-static.json')['plan']
    assert events[2]['payload'] == plan and len(plan) == 117
    classifications, readbacks, queries, framebuffers = [], [], [], []
    for i, step in enumerate(plan):
        intent, event, assessment = events[3+i*3:6+i*3]
        assert [e['kind'] for e in (intent, event, assessment)] == ['step-intent', 'step-result', 'assessment']
        assert intent['payload'] == step
        r = event['payload']; v = r['value']; op = step['op']
        assert r['step'] == step and r['before'] == {'errors': [], 'drained': True}
        assert not r['skipped'] and not r['contextLost'] and r['exception'] is None
        is_query_error = op == 'translated-source'
        assert r['after'] == {'errors': [1282] if is_query_error else [], 'drained': True}
        classification = {'step': step, 'classification': 'query-error' if is_query_error else 'ok'}
        assert assessment['payload'] == classification
        classifications.append(classification)
        if is_query_error:
            assert v == {'source': '', 'skipped': False}
            queries.append({'step': step, 'event': names[4+i*3], 'error': 1282})
        if op == 'shader-is': assert v == {'isShader': True}
        if op == 'shader-deleted': assert v == {'deleted': True}
        if op == 'shader-compiled': assert v == {'compiled': True}
        if op == 'program-link': assert v == {'linked': True}
        if op in ('compile', 'render'): assert v == {'callbacks': []}
        if op == 'framebuffer-status':
            assert v == {'status': 36053, 'completeEnum': 36053}
            framebuffers.append(names[4+i*3])
        if op == 'framebuffer-binding': assert v == {'bound': True}
        if op.startswith('read-'):
            name = step['name']; want = []
            for x in range(128):
                want.extend([255, 0, 255, 255] if name == 'byte-constant' else
                            [0.125, -0.5, 2, 1] if name == 'float-constant' else
                            [x / 32 - 2, -0.25 if name == 'float-row0' else 0.75, x / 128, 1])
            bits = want if name == 'byte-constant' else [struct.unpack('<I', struct.pack('<f', x))[0] for x in want]
            assert v['values'] == v['expected'] == want and v['bits'] == bits
            assert v['method'] == op and v['sentinel'] not in v['values']
            readbacks.append({'step': step, 'event': names[4+i*3], 'exact_components': len(want)})
    assert classifications == result['classifications']
    assert result['query_errors'] == [c for c in classifications if c['classification'] == 'query-error']
    assert Counter(c['classification'] for c in classifications) == {'ok': 109, 'query-error': 8}
    assert len(readbacks) == len(queries) == len(framebuffers) == 8
    tail = events[354:]
    assert [e['kind'] for e in tail] == ['dispose-intent', 'dispose-result', 'page-closed', 'browser-closed']
    d = tail[1]['payload']
    assert d['step'] == {'op': 'dispose'} and d['exception'] is None
    assert not d['skipped'] and not d['contextLost']
    assert d['before'] == d['after'] == {'errors': [], 'drained': True}
    assert d['value'] == {'resourcesDisposed': 16, 'rendererDisposed': True}
    messages = result['browser_messages']
    assert len(messages) == 13 and all(m['kind'] == 'console' and m['type'] == 'warning' for m in messages)
    assert sum('getTranslatedShaderSource: attempt to use a deleted object' in m['text'] for m in messages) == 8
    assert sum('GPU stall due to ReadPixels' in m['text'] for m in messages) == 4
    assert sum('deprecated' in m['text'] for m in messages) == 1
    assert result['complete'] and not result['infrastructure_clean'] and result['failure'] is None
    for key in ('numeric_passed', 'synthetic_uniform_candidate_supported', 'first_root_certified', 'capture_permitted'):
        assert result[key] is False
    assert result['new_images'] == 0
    save(output, {'saved_evidence_verified': True, 'actual_exit': 1, 'stages': 117,
                  'events': 358, 'exact_readbacks': readbacks, 'query_errors': queries,
                  'framebuffer_events': framebuffers, 'browser_warning_count': 13,
                  'localization': 'Only translated-source calls raised GL1282; browser reports deleted objects',
                  'old_failure_cause_proven': False, 'numeric_passed': False,
                  'synthetic_uniform_candidate_supported': False, 'capture_permitted': False,
                  'new_images': 0, 'result_sha256': digest(PREFIX + '-result.json')})
    print('Saved-only review verified: 358 events, 117 stages, 8 exact readbacks, 8 query errors; actual exit1 retained')


if __name__ == '__main__':
    main()
