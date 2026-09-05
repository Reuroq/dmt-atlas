"""Distinct transport-only checks; never import or execute arithmetic main()."""
import ast
import hashlib
import importlib.metadata
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
import playwright._impl._js_handle as wire
import probe_centre_v34_staged_arithmetic_r2 as p

PREFIX = 'centre-v34-transport'
HISTORY = p.PREFIX + '-runtime-integrity.json'
SOURCES = ['probe_centre_v34_transport.py', 'run_centre_v34_transport_once.py',
           'prepare_centre_v34_transport.py', PREFIX + '.js', PREFIX + '-protocol.md']


def prior(display=False):
    m = p.read(HISTORY)
    for k in ('files', 'protected') + (('display',) if display else ()):
        p.verify(m[k])
    stem = p.PREFIX + '-runtime-close-once'
    r, launch = p.read(stem + '-exit.json'), p.read(stem + '-launch.json')
    assert r['actual_exit'] == 0 and r['launcher_error'] is None
    for key, name in [('log_sha256', stem + '.log'), ('launch_sha256', stem + '-launch.json'), ('manifest_sha256', HISTORY)]:
        assert r[key] == p.digest(name)
    assert launch['script_sha256'] == p.digest(launch['script'])
    assert launch['launcher_sha256'] == p.digest('run_centre_v34_staged_arithmetic_r2_runtime_close_once.py')
    assert launch['preparation_sha256'] == p.digest(p.PREFIX + '-preparation-integrity.json')
    return m


def environment():
    path = Path(wire.__file__)
    return {'playwright_version': importlib.metadata.version('playwright'),
            'serializer_path': str(path), 'serializer_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def fixtures():
    mixed = [0, 0x80000000, 0x3f800000, 0xbf800000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff]
    return {'original': p.inputs(), 'mixed': [struct.unpack('<f', struct.pack('<I', b))[0] for b in mixed]}


def cases():
    out = []
    for name, values in fixtures().items():
        want = [p.bit(x) for x in values]
        for mode, payload in [('float', values), ('bits', want), ('json', json.dumps(values, allow_nan=False))]:
            serialized = wire.serialize_argument(payload)
            decoded = wire.parse_value(serialized['value'])
            if mode == 'bits': decoded = [struct.unpack('<f', struct.pack('<I', b))[0] for b in decoded]
            elif mode == 'json': decoded = json.loads(decoded)
            out.append({'name': name, 'mode': mode, 'payload': payload, 'wire': serialized,
                        'sourceBits': want, 'wireDecodedBits': [p.bit(x) for x in decoded]})
    out.append({'name': 'local', 'mode': 'local', 'payload': None, 'wire': wire.serialize_argument(None),
                'sourceBits': [0, 0x80000000, 0x3f800000, 0xbf800000],
                'wireDecodedBits': [0, 0x80000000, 0x3f800000, 0xbf800000]})
    return out


def validate(case, result):
    want = case['wireDecodedBits']
    assert result['ingressBits'] == want and result['cpuBits'] == want
    assert result['negativeZeroIndices'] == [i for i, b in enumerate(want) if b == 0x80000000]
    assert result['jsonRoundtripBits'] == [0 if b == 0x80000000 else b for b in want]
    changed = [i for i, (a, b) in enumerate(zip(case['sourceBits'], want)) if a != b]
    if case['mode'] == 'float':
        assert changed == [i for i, b in enumerate(case['sourceBits']) if b == 0]
        assert all(want[i] == 0x80000000 for i in changed)
    else:
        assert not changed
    return {'name': case['name'], 'mode': case['mode'], 'changedSourceIndices': changed, 'exactTransport': not changed}


def check():
    prior(True)
    for name in SOURCES:
        if name.endswith('.py'): ast.parse((p.HERE / name).read_text())
    cs = cases()
    p.save(PREFIX + '-offline-wire.json', {'environment': environment(), 'cases': cs})
    # Node receives the saved serializer output, not raw Python floats. Decode only the actual wire types used here.
    js = r'''
const fs=require('fs'), assert=require('assert');
eval(fs.readFileSync(process.argv[1], 'utf8'));
const cases=JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).cases;
function decode(w) {
 if ('n' in w) return w.n;
 if ('s' in w) return w.s;
 if (w.v === '-0') return -0;
 if (w.v === 'null') return null;
 if ('a' in w) return w.a.map(decode);
 throw Error('unexpected wire type');
}
const results=cases.map(c=>transportProbe.inspect(c.mode,decode(c.wire.value)));
const accounting=[];
for (const [count,failResource,failRenderer] of [[0,false,false],[3,false,false],[8,false,false],[3,true,false],[3,false,true]]) {
 const calls=[], entries=Array.from({length:count},(_,i)=>({id:'r'+i,resource:{dispose(){calls.push('r'+i);if(failResource&&i===1)throw Error('injected resource');}}}));
 const result=transportProbe.cleanup(entries,{dispose(){calls.push('renderer');if(failRenderer)throw Error('injected renderer');}},'fatal-input');
 assert.deepStrictEqual(calls,[...entries.map(e=>e.id),'renderer']);
 assert.deepStrictEqual(result.attempted,result.registered);
 assert.deepStrictEqual(result.succeeded,entries.filter((e,i)=>!(failResource&&i===1)).map(e=>e.id));
 assert.strictEqual(result.complete,!failResource&&!failRenderer);
 assert.strictEqual(result.rendererDisposed,!failRenderer);
 assert.strictEqual(result.errors.length,Number(failResource)+Number(failRenderer));
 assert.strictEqual(result.primaryFailure,'fatal-input');
 accounting.push(result);
}
assert.throws(()=>transportProbe.cleanup([{id:'x'},{id:'x'}],null),/duplicate/);
assert.throws(()=>transportProbe.inspect('bits',[-1]),/uint32/);
assert.throws(()=>transportProbe.inspect('bits',[0.5]),/uint32/);
assert.throws(()=>transportProbe.inspect('bits',[4294967296]),/uint32/);
process.stdout.write(JSON.stringify({results,accounting}));
'''
    argv = ['node', '-e', js, str(p.HERE / (PREFIX + '.js')), str(p.HERE / (PREFIX + '-offline-wire.json'))]
    p.save(PREFIX + '-node-launch.json', {'argv': argv})
    with (p.HERE / (PREFIX + '-node-stdout.json')).open('x') as out, (p.HERE / (PREFIX + '-node-stderr.log')).open('x') as err:
        code = subprocess.run(argv, stdout=out, stderr=err, timeout=30).returncode
        for f in (out, err): f.flush(); os.fsync(f.fileno())
    p.save(PREFIX + '-node-exit.json', {'actual_exit': code})
    assert code == 0
    results = p.read(PREFIX + '-node-stdout.json')
    assert len(results['results']) == len(cs)
    assessments = [validate(c, r) for c, r in zip(cs, results['results'])]
    assert len(assessments[0]['changedSourceIndices']) == 905
    old_shared = p.read(p.PREFIX + '-event-020.json')['payload']
    old_dispose = p.read(p.PREFIX + '-event-023.json')['payload']
    assert old_shared['value']['input']['bits'] == cs[0]['wireDecodedBits']
    assert old_dispose['value'] == {'resourcesDisposed': 3, 'rendererDisposed': True}
    old_html = (p.HERE / p.HTML).read_text()
    shared_source = old_html.split("case 'shared': {", 1)[1].split("case 'material':", 1)[0]
    assert shared_source.count('resources.push(') == 3
    assert all('resources.push(' + name + ')' in shared_source for name in ('target', 'texture', 'geometry'))
    # Prove strict comparison detects a sign-only defect in the proposed bit route.
    bad = dict(results['results'][1]); bad['cpuBits'] = list(bad['cpuBits']); bad['cpuBits'][0] ^= 0x80000000
    try: validate(cs[1], bad)
    except AssertionError: pass
    else: raise AssertionError('one-bit mutation accepted')
    p.save(PREFIX + '-static.json', {'passed': True, 'browser_run': False, 'assessments': assessments,
           'accounting_cases': len(results['accounting']), 'interpretation': 'Installed Python serializer changes positive float zero to wire -0. Offline reproduction, not historical wire capture or browser/GPU evidence.'})
    print('Transport offline PASS: original 905 zero signs localized at installed serializer; strict bit alternatives and 5 fake cleanup cases pass')


def runtime():
    prior()
    prep = p.read(PREFIX + '-preparation-integrity.json')
    for key in ('files', 'protected', 'display'): p.verify(prep[key])
    assert prep['static_passed'] and not prep['runtime_run']
    launch = p.read(PREFIX + '-runtime-once-launch.json')
    assert launch['preparation_sha256'] == p.digest(PREFIX + '-preparation-integrity.json')
    assert not list(p.HERE.glob(PREFIX + '-event-*'))
    assert not (p.HERE / (PREFIX + '-result.json')).exists()
    from playwright.sync_api import sync_playwright
    events = {}
    def event(kind, payload):
        name = PREFIX + '-event-' + str(len(events)).zfill(3) + '.json'
        p.save(name, {'kind': kind, 'payload': payload, 'previous_sha256': next(reversed(events.values())) if events else None})
        events[name] = p.digest(name)
    errors, assessments, failure = [], [], None
    event('inputs', {'environment': environment(), 'texture_sha256': p.digest(p.TEXTURE)})
    try:
        with sync_playwright() as pw:
            browser = page = None
            try:
                event('browser-launch-intent', {'headless': True, 'args': p.ARGS})
                browser = pw.chromium.launch(headless=True, args=p.ARGS)
                event('browser-launched', {'version': browser.version})
                page = browser.new_page()
                page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))
                page.on('console', lambda e: errors.append({'kind': 'console', 'type': e.type, 'text': e.text}))
                page.set_default_timeout(15000)
                page.set_content('<!doctype html><title>Transport-only diagnostic</title>')
                page.add_script_tag(content=(p.HERE / (PREFIX + '.js')).read_text())
                for case in cases():
                    event('case-intent', case)
                    result = page.evaluate('c => transportProbe.inspect(c.mode,c.payload)', {'mode': case['mode'], 'payload': case['payload']})
                    event('case-result', result)
                    assessment = validate(case, result)
                    assessments.append(assessment); event('assessment', assessment)
            finally:
                for name, resource in [('page', page), ('browser', browser)]:
                    if resource is not None:
                        try: resource.close(); event(name + '-closed', {})
                        except Exception as e:
                            errors.append({'kind': name + '-close-failure', 'text': str(e)})
                            event(name + '-close-failure', {'error': str(e)})
        assert not errors, errors
        assert len(assessments) == 7
    except Exception as e:
        failure = str(e); event('failure', {'error': failure})
    p.save(PREFIX + '-result.json', {'events': events, 'assessments': assessments, 'messages': errors,
           'failure': failure, 'transport_passed': failure is None, 'arithmetic_support': False,
           'capture_permitted': False, 'new_images': 0})
    p.verify(events)
    if failure is not None: raise RuntimeError(failure)
    print('Transport-only runtime complete; no arithmetic/GL/field/visual evidence')


if __name__ == '__main__':
    freeze = p.read(PREFIX + '-freeze.json')
    p.verify(freeze['sources'])
    assert freeze['environment'] == environment()
    assert freeze['history_sha256'] == p.digest(HISTORY)
    {'static': check, 'runtime': runtime}[sys.argv[1]]()
