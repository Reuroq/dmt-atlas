"""Close saved transport evidence only; no browser, arithmetic or replay."""
import json
import os
import struct
import probe_centre_v34_transport as t

p = t.p
PREFIX = t.PREFIX


def write(name, data):
    with (p.HERE / name).open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def receipt(mode):
    stem = PREFIX + '-' + mode + '-once'
    r, launch = p.read(stem + '-exit.json'), p.read(stem + '-launch.json')
    assert r['actual_exit'] == 0 and r['launcher_error'] is None
    for key, name in [('log_sha256', stem + '.log'), ('launch_sha256', stem + '-launch.json')]:
        assert r[key] == p.digest(name)
    for key, name in [('freeze_sha256', PREFIX + '-freeze.json'),
                      ('script_sha256', 'probe_centre_v34_transport.py'),
                      ('launcher_sha256', 'run_centre_v34_transport_once.py')]:
        assert launch[key] == p.digest(name)
    assert launch['preparation_sha256'] == (p.digest(PREFIX + '-preparation-integrity.json') if mode == 'runtime' else None)
    return r


def decode(w):
    if 'n' in w: return w['n']
    if 's' in w: return w['s']
    if w.get('v') == '-0': return -0.0
    if w.get('v') == 'null': return None
    if 'a' in w: return [decode(x) for x in w['a']]
    raise AssertionError('Unexpected saved wire type')


def main():
    manifest = PREFIX + '-runtime-integrity.json'
    assert not (p.HERE / manifest).exists()
    t.prior()
    prep = p.read(PREFIX + '-preparation-integrity.json')
    for key in ('files', 'protected', 'display'): p.verify(prep[key])
    freeze = p.read(PREFIX + '-freeze.json')
    p.verify(freeze['sources']); assert freeze['environment'] == t.environment()
    receipts = {mode: receipt(mode) for mode in ('static', 'runtime')}
    p.save(PREFIX + '-runtime-close-started.json', {'saved_only': True})
    result = p.read(PREFIX + '-result.json')
    p.verify(result['events'])
    names = list(result['events'])
    assert names == [PREFIX + '-event-' + str(i).zfill(3) + '.json' for i in range(26)]
    assert set(names) == {f.name for f in p.HERE.glob(PREFIX + '-event-*')}
    events, previous = [], None
    for name in names:
        e = p.read(name)
        assert e['previous_sha256'] == previous
        previous = p.digest(name); events.append(e)
    expected = ['inputs', 'browser-launch-intent', 'browser-launched']
    expected += ['case-intent', 'case-result', 'assessment'] * 7
    expected += ['page-closed', 'browser-closed']
    assert [e['kind'] for e in events] == expected
    assert events[0]['payload'] == {'environment': freeze['environment'], 'texture_sha256': p.digest(p.TEXTURE)}
    assert events[1]['payload'] == {'headless': True, 'args': p.ARGS}
    assert events[2]['payload']['version']
    assert events[-2]['payload'] == events[-1]['payload'] == {}
    offline = p.read(PREFIX + '-offline-wire.json')
    assert offline['environment'] == freeze['environment']
    cases = offline['cases']
    assert [(c['name'], c['mode']) for c in cases] == [
        ('original', 'float'), ('original', 'bits'), ('original', 'json'),
        ('mixed', 'float'), ('mixed', 'bits'), ('mixed', 'json'), ('local', 'local')]
    raw = (p.HERE / p.TEXTURE).read_bytes()
    original = list(struct.unpack('<' + 'I' * (len(raw) // 4), raw))
    assert len(original) == 1024 and original.count(0) == 905
    source_bits = {'original': original,
                   'mixed': [0, 0x80000000, 0x3f800000, 0xbf800000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff],
                   'local': [0, 0x80000000, 0x3f800000, 0xbf800000]}
    assessments, counts = [], []
    for i, case in enumerate(cases):
        intent, observed, assessment = [e['payload'] for e in events[3 + i * 3:6 + i * 3]]
        # JSON text comparison retains the sign of zero, unlike Python numeric equality.
        assert json.dumps(intent, sort_keys=True) == json.dumps(case, sort_keys=True)
        assert case['sourceBits'] == source_bits[case['name']]
        payload = decode(case['wire']['value'])
        if case['mode'] == 'bits': wire_bits = payload
        elif case['mode'] == 'local': wire_bits = source_bits['local']
        else:
            if case['mode'] == 'json': payload = json.loads(payload)
            wire_bits = [p.bit(x) for x in payload]
        assert wire_bits == case['wireDecodedBits']
        for key in ('ingressBits', 'cpuBits', 'jsonRoundtripBits'):
            assert len(observed[key]) == len(wire_bits)
            assert all(type(b) is int and 0 <= b <= 0xffffffff for b in observed[key])
        a = t.validate(case, observed)
        assert a == assessment
        assessments.append(a)
        counts.append({'name': case['name'], 'mode': case['mode'], 'components': len(wire_bits),
                       'source_sign_changes': len(a['changedSourceIndices']),
                       'json_negative_zero_losses': wire_bits.count(0x80000000)})
    assert assessments == result['assessments']
    assert [len(a['changedSourceIndices']) for a in assessments] == [905, 0, 0, 1, 0, 0, 0]
    assert result['failure'] is None and result['messages'] == [] and result['transport_passed'] is True
    assert result['arithmetic_support'] is False and result['capture_permitted'] is False and result['new_images'] == 0
    next_work = ('Verify centre-v34-transport-runtime-integrity.json files/protected/display and runtime-close-once '
                 'actual-exit0 receipt hashes. Then prepare a DISTINCT staged arithmetic successor, never edit/replay r2: '
                 'uint32 texture ingress reconstructed through Uint32Array/Float32Array, strict source/request/CPU bits, '
                 'immediate resource identities and exception-continuing cleanup with renderer disposal. Preserve frozen '
                 'original texture/shader arithmetic, rational oracle, 126-stage GL localization, saved full readbacks '
                 'before assessment, both-leaf exact literal/uniform support criterion, and one-shot receipts. '
                 'Static preparation first; no browser arithmetic until its closure. Original exact-jet/716-of-720 '
                 'and all roots/cost/visual/source/coverage/route/full acceptance gates remain; no candidate promotion.')
    summary = ('Distinct transport runtime CLOSED actual exit0; 7 cases/26 chained events verified. Browser ingress '
               'and CPU arrays reproduce the installed serializer defect: original float list changes 905 positive-zero '
               'signs, mixed float list changes one; all nonzeros exact. Uint32 and JSON-text input arms preserve every '
               'source bit, including signed zero; JS-local control exact. JSON stringify/parse erases negative-zero '
               'signs as expected. Float-list arms remain inexact diagnostic failures, not exact-transport passes. '
               'No browser messages; page/browser close recorded. This is new transport evidence, not a historical '
               'wire capture, GPU arithmetic, GPU cleanup or visual result. Five fake cleanup cases remain offline-only.')
    review = {'saved_evidence_verified': True, 'events': len(events), 'cases': counts,
              'receipts': receipts, 'browser_version': events[2]['payload']['version'],
              'messages': [], 'page_closed': True, 'browser_closed': True,
              'transport_protocol_passed': True, 'all_transport_arms_exact': False,
              'arithmetic_support': False, 'capture_permitted': False, 'new_images': 0,
              'interpretation': summary, 'next_work': next_work}
    p.save(PREFIX + '-runtime-review.json', review)
    write(PREFIX + '-runtime-review.md', ('# Transport-only runtime closure\n\n' + summary +
          '\n\nSaved-only closure independently decodes wire values, checks frozen texture uint32 bits, '
          'all ingress/CPU/JSON-roundtrip components, exact event order/hash chain and launch/log/source/exit receipts. '
          'Current display is verified against transport preparation, not the superseded r2 display snapshot. '
          'Frozen r2 fatal-input/fatal-disposal and original numerical failures remain unchanged. '
          'latest.png remains the inspected REJECTED GAME v33r6 entry; no new image or acceptance.\n\n'
          '## Next bounded phase\n\n' + next_work + '\n').encode())
    notes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes.startswith(b'\xef\xbb\xbf')
    before, old_next = notes.decode('utf-8-sig').split('## Exact next bounded work\n')
    assert 'run_centre_v34_transport_once.py runtime ONCE' in old_next
    new_notes = ('# Active: REDIRECT4 — transport runtime CLOSED; uint32 transport exact\n' + before.split('\n', 1)[1] +
                 '## Distinct transport runtime CLOSED — protocol PASS; float route inexact\n- ' + summary +
                 '\n- Verified preparation969 evidence/16protected/4display and static/runtime actual-exit0 receipts. '
                 'Frozen evidence unchanged; prior display archived; NOTES once/BOM retained. '
                 'latest unchanged inspected REJECTED GAME v33r6; all19 unfinished.\n\n'
                 '## Exact next bounded work\n' + next_work + '\n')
    readme = (p.HERE / 'README.md').read_text()
    anchors = [line for line in readme.splitlines() if line.startswith('Distinct [transport-only preparation]')]
    assert len(anchors) == 1
    replacement = ('Distinct [transport-only runtime](centre-v34-transport-runtime-review.md) is **CLOSED; protocol PASS, '
                   'actual exit0**. Seven cases confirm 905 original float-list zero-sign changes; uint32 and JSON-text '
                   'ingress preserve strict bits. JSON stringify loses negative zero. Browser closes cleanly; '
                   'no arithmetic, GPU cleanup or visual claim. Frozen numerical failures remain.')
    assert 'transport preparation CLOSED static PASS' in (p.HERE / 'status.txt').read_text()
    updates = {'NOTES.md': b'\xef\xbb\xbf' + new_notes.encode(),
               'README.md': readme.replace(anchors[0], replacement, 1).encode(),
               'status.txt': (summary + ' latest unchanged inspected REJECTED GAME v33r6; all19 unfinished. ' + next_work + '\n').encode()}
    archives = {}
    for name in updates:
        archive = name + '-before-' + PREFIX + '-runtime'
        write(archive, (p.HERE / name).read_bytes()); archives[archive] = p.digest(name)
    for name, data in updates.items():
        with (p.HERE / name).open('wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
    files = dict(prep['files'])
    files.update({f.name: p.digest(f.name) for f in p.HERE.glob(PREFIX + '-*')
                  if f.is_file() and not f.name.startswith(PREFIX + '-runtime-close-once')})
    files.update(archives)
    for name in ('close_centre_v34_transport_runtime.py', 'run_centre_v34_transport_runtime_close_once.py'):
        files[name] = p.digest(name)
    p.verify(files); p.verify(prep['protected'])
    assert p.digest('latest.png') == prep['display']['latest.png']
    display = {name: p.digest(name) for name in prep['display']}
    p.save(manifest, {'files': files, 'protected': prep['protected'], 'display': display,
                     'prior_display': prep['display'], 'archived_display': archives,
                     'runtime_run': True, 'actual_exit': 0, 'saved_evidence_verified': True,
                     'transport_protocol_passed': True, 'all_transport_arms_exact': False,
                     'arithmetic_support': False, 'capture_permitted': False, 'new_images': 0})
    for key in ('files', 'protected', 'display'): p.verify(p.read(manifest)[key])
    print('Transport saved-only closure PASS:', len(files), 'evidence hashes; 7 cases/26 events; no arithmetic support')


if __name__ == '__main__':
    main()
