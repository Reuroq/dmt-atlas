"""Distinct staged synthetic arithmetic. No field, image or acceptance execution."""
import hashlib
import json
import math
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v34-staged-arithmetic-r2'
HISTORY = 'centre-v34-staged-arithmetic-preparation-failure-integrity.json'
SEEDS = 'centre-v34-followup-seeds.json'
TEXTURE = 'centre-v34-followup-texture.f32'
HTML = 'gpu_centre_v34_staged_arithmetic_r2.html'
ARGS = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files']


def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name


def gate(prepared=True):
    freeze = read(PREFIX + '-freeze.json')
    verify(freeze['sources'])
    assert digest(HISTORY) == freeze['history_sha256']
    history = read(HISTORY)
    verify(history['files']); verify(history['protected'])
    assert not history['static_passed'] and history['static_actual_exit'] == 1
    prior = read('centre-v34-staged-arithmetic-static-once-exit.json')
    assert prior['actual_exit'] == 1 and prior['launcher_error'] is None
    assert prior['log_sha256'] == digest('centre-v34-staged-arithmetic-static-once.log')
    assert prior['launch_sha256'] == digest('centre-v34-staged-arithmetic-static-once-launch.json')
    if prepared:
        prep = read(PREFIX + '-preparation-integrity.json')
        verify(prep['files']); verify(prep['display']); verify(prep['protected'])
        assert prep['static_passed'] and not prep['runtime_run']
        assert read(PREFIX + '-static.json')['passed']
        receipt('static')
        receipt('close')
    else:
        verify(history['display'])


def receipt(label):
    stem = PREFIX + '-' + label + '-once'
    r, launch = read(stem + '-exit.json'), read(stem + '-launch.json')
    assert r['actual_exit'] == 0 and r['launcher_error'] is None
    assert r['launch_sha256'] == digest(stem + '-launch.json')
    assert r['log_sha256'] == digest(stem + '.log')
    assert launch['script_sha256'] == digest(launch['script'])
    assert launch['launcher_sha256'] == digest('run_centre_v34_staged_arithmetic_r2_once.py')
    assert launch['freeze_sha256'] == digest(PREFIX + '-freeze.json')


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def bit(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


def inputs():
    return list(struct.unpack('<1024f', (HERE / TEXTURE).read_bytes()))


def expected(leaf, xs):
    """Independent of JS/GPU: each addition rounded separately to binary32."""
    out = []
    c1, c2 = f32(leaf['c1']), f32(leaf['c2'])
    for x in xs:
        parent = f32(x + c1)
        out.extend([x, parent, f32(parent + c2), f32(x + f32(c1 + c2))])
    return out


def compare(values, leaf, xs):
    want = expected(leaf, xs)
    mismatches = [i for i, (x, y) in enumerate(zip(values, want)) if bit(x) != bit(y)]
    replay = [i for i in range(len(xs)) if bit(values[4*i+2]) != bit(f32(values[4*i+1] + f32(leaf['c2'])))]
    return {'expected': want, 'expected_bits': [bit(x) for x in want],
            'bit_mismatches_per_channel': [sum(i % 4 == c for i in mismatches) for c in range(4)],
            'numeric_mismatches_per_channel': [sum(values[i] != want[i] for i in range(c, len(want), 4)) for c in range(4)],
            'mismatched_components': mismatches, 'child_vs_saved_microprobe_parent_mismatches': len(replay),
            'child_vs_parent_failed_indices': replay, 'exact': not mismatches and not replay}


def assess(r, leaves, texels, readbacks):
    """Caller durably saves the complete result before invoking this function."""
    def result(code, **payload):
        return {'step': r['step'], 'classification': code, **payload}
    if r['before']['errors'] or not r['before']['drained'] or r['skipped']:
        return result('fatal-precondition')
    if not r['after']['drained'] or r['contextLost']:
        return result('fatal-context')
    if r['after']['errors'] or r['exception']:
        return result('fatal-operation')
    s, v = r['step'], r['value']; op = s['op']
    if op == 'renderer' and v != {'three': '160', 'webgl2': True, 'precision': 'highp'}:
        return result('fatal-backend')
    if op == 'metadata' and v['highFloat']['precision'] != 23:
        return result('fatal-backend')
    if op == 'float-extension' and not v['supported']:
        return result('fatal-backend')
    if op == 'dispose' and (not v['rendererDisposed'] or v['resourcesDisposed'] != 8):
        return result('fatal-disposal')
    if op == 'shared' and (v['input']['values'] != texels or v['input']['bits'] != [bit(x) for x in texels]
                           or (v['width'], v['height'], v['textureHeight'], v['targetType']) != (128, 1, 2, 1015)):
        return result('fatal-input')
    if op == 'framebuffer-status' and (v['status'] != 36053 or v['completeEnum'] != 36053):
        return result('fatal-framebuffer')
    if op == 'framebuffer-binding' and not v['bound']:
        return result('fatal-framebuffer')
    if op == 'bind' and v != {'width': 128, 'height': 1, 'type': 1015}:
        return result('fatal-framebuffer')
    if ((op in ('compile', 'render') and v['callbacks']) or
        (op == 'program-reference' and not all(v.get(k) for k in ('present', 'vertexPresent', 'fragmentPresent'))) or
        (op == 'program-link' and not v['linked']) or (op == 'shader-is' and not v['isShader']) or
        (op == 'shader-compiled' and not v['compiled']) or (op == 'shader-source' and not v['source'])):
        return result('fatal-shader')
    if op == 'material' and s['name'] != 'float-control':
        leaf = leaves[s['leaf']]; u = v['uniforms']
        if (u['textureRow'] != leaf['row'] or bit(u['secondOffset']) != bit(leaf['c2']) or
            u['secondOffsetBits'] != bit(leaf['c2'])):
            return result('fatal-uniform')
    if op.startswith('read-'):
        values, bits = v['values'], v['bits']
        if (v['method'] != op or v['sentinel'] != -123.75 or len(values) != 512 or len(bits) != 512 or
            any(type(x) not in (float, int) or not math.isfinite(x) or x == -123.75 for x in values)):
            return result('fatal-readback')
        # JSON loses negative-zero signs; retained uint32 bits remain authoritative.
        for x, b in zip(values, bits):
            if type(b) is not int or not 0 <= b <= 0xffffffff:
                return result('fatal-readback')
            decoded = struct.unpack('<f', struct.pack('<I', b))[0]
            if not math.isfinite(decoded) or decoded != x or (x != 0 and bit(x) != b):
                return result('fatal-readback')
        values = [struct.unpack('<f', struct.pack('<I', b))[0] for b in bits]
        key = (s['name'], s.get('arm'))
        if op == 'read-raw' and (key not in readbacks or bits != readbacks[key]):
            return result('fatal-transport-disagreement')
        if op == 'read-three':
            readbacks[key] = bits
        if s['name'] == 'float-control':
            want = [.125, -.5, 2., 1.] * 128
            return result('ok' if bits == [bit(x) for x in want] else 'fatal-control')
        leaf = leaves[s['leaf']]; count = leaf['count']
        unique = compare(values[:4*count], leaf, leaf['values'])
        all_texels = compare(values, leaf, texels[s['leaf']*512:(s['leaf']+1)*512:4])
        return result('ok' if all_texels['exact'] else 'arithmetic-mismatch', unique=unique, all_texels=all_texels)
    return result('ok')


def supported(assessments, clean):
    if not clean:
        return False
    for name in ('childAxial', 'childAngular'):
        for method in ('read-three', 'read-raw'):
            arms = {a['step']['arm']: a['unique'] for a in assessments
                    if a['step'].get('name') == name and a['step']['op'] == method and 'unique' in a}
            if set(arms) != {'literal', 'uniform'}:
                return False
            literal = arms['literal']
            if not (literal['child_vs_saved_microprobe_parent_mismatches'] > 0 and
                    all(literal['bit_mismatches_per_channel'][i] == 0 for i in (0, 1, 3)) and arms['uniform']['exact']):
                return False
    return True


def run_steps(page, plan, event, leaves, texels, assessments):
    readbacks = {}
    for step in plan:
        request = dict(step)
        if step['op'] == 'shared':
            request['data'] = texels
        event('step-intent', request)
        try:
            r = page.evaluate('s=>arithmeticStep(s)', request)
        except Exception as exc:
            event('step-exception', {'step': request, 'error': str(exc)})
            raise
        event('step-result', r)
        assert r['step'] == request, 'Returned identity changed'
        a = assess(r, leaves, texels, readbacks)
        assessments.append(a); event('assessment', a)
        if a['classification'].startswith('fatal'):
            raise RuntimeError(a['classification'] + ': ' + json.dumps(step))


def main():
    gate()
    launch = read(PREFIX + '-runtime-once-launch.json')
    assert launch['child_pid_parent'] == os.getppid(), 'Use frozen foreground launcher'
    assert launch['preparation_sha256'] == digest(PREFIX + '-preparation-integrity.json')
    save(PREFIX + '-started.json', {'pid': os.getpid(), 'launch_sha256': digest(PREFIX + '-runtime-once-launch.json')})
    from playwright.sync_api import sync_playwright
    events, assessments, messages = [], [], []
    browser = page = None
    failure = None
    leaves, texels = read(SEEDS)['leaves'], inputs()

    def event(kind, payload):
        n = PREFIX + '-event-' + str(len(events)).zfill(3) + '.json'
        save(n, {'kind': kind, 'payload': payload, 'previous_sha256': digest(events[-1]) if events else None})
        events.append(n)

    try:
        with sync_playwright() as pw:
            try:
                event('inputs', {'seeds_sha256': digest(SEEDS), 'texture_sha256': digest(TEXTURE),
                                'synthetic_not_recovered_gpu_intermediates': True, 'translated_queries': 'omitted by protocol'})
                event('browser-launch-intent', {'args': ARGS})
                browser = pw.chromium.launch(headless=True, args=ARGS)
                event('browser-launched', {'version': browser.version})
                page = browser.new_page()
                page.on('pageerror', lambda e: messages.append({'kind': 'pageerror', 'text': str(e)}))
                page.on('console', lambda m: messages.append({'kind': 'console', 'type': m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
                page.goto((HERE / HTML).as_uri(), wait_until='load')
                plan = page.evaluate('arithmeticPlan()')
                assert plan == read(PREFIX + '-static.json')['plan']
                event('plan', plan)
                run_steps(page, plan, event, leaves, texels, assessments)
            finally:
                if page is not None:
                    try:
                        event('dispose-intent', {})
                        r = page.evaluate("arithmeticStep({op:'dispose'})")
                        event('dispose-result', r)
                        a = assess(r, leaves, texels, {})
                        event('dispose-assessment', a)
                        if a['classification'] != 'ok':
                            failure = 'Resource disposal failed; see durable evidence'
                    except Exception as exc:
                        event('dispose-failure', {'error': str(exc)}); failure = 'Resource disposal incomplete'
                    try:
                        page.close(); event('page-closed', {})
                    finally:
                        if browser is not None:
                            browser.close(); event('browser-closed', {})
                elif browser is not None:
                    browser.close(); event('browser-closed', {})
    except Exception as exc:
        failure = str(exc); event('failure', {'error': failure})
    complete = failure is None and len(assessments) == len(read(PREFIX + '-static.json')['plan'])
    clean = complete and not any(m['kind'] == 'pageerror' or m.get('type') == 'error' for m in messages)
    support = supported(assessments, clean)
    save(PREFIX + '-result.json', {'complete': complete, 'infrastructure_clean': clean, 'failure': failure,
         'browser_messages': messages, 'assessments': assessments, 'events': {n: digest(n) for n in events},
         'synthetic_uniform_candidate_supported': support, 'numeric_passed': False,
         'first_root_certified': False, 'capture_permitted': False, 'new_images': 0,
         'interpretation': 'Synthetic evidence only; not compiler attribution, field equality, roots, cost or realism.'})
    print('Staged arithmetic complete:', complete, 'infrastructure clean:', clean, 'synthetic support:', support, flush=True)
    return 0 if clean else 1


if __name__ == '__main__':
    sys.exit(main())
