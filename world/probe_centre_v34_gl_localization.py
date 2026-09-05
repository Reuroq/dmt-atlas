"""New infrastructure controls only. No arithmetic probe, field, images or acceptance."""
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v34-gl-localization'
HISTORY = 'centre-v34-followup-runtime-integrity.json'
ARGS = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files']


def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name


def gate(prepared=True):
    freeze = read(PREFIX + '-freeze.json')
    verify(freeze['sources'])
    assert digest(HISTORY) == freeze['history_sha256']
    history = read(HISTORY)
    verify(history['files']); verify(history['protected'])
    stem = 'centre-v34-followup-runtime-close-once'
    receipt = read(stem + '-exit.json')
    launch = read(stem + '-launch.json')
    assert receipt['actual_exit'] == 0
    assert receipt['log_sha256'] == digest(stem + '.log')
    assert receipt['launch_sha256'] == digest(stem + '-launch.json')
    assert launch['script_sha256'] == digest(launch['script'])
    if prepared:
        prep = read(PREFIX + '-preparation-integrity.json')
        verify(prep['files']); verify(prep['display'])
        assert prep['static_passed'] and not prep['runtime_run']
        assert read(PREFIX + '-static.json')['passed']
    else:
        verify(history['display'])


def expected(name):
    values = []
    for i in range(128):
        values += ([255, 0, 255, 255] if name == 'byte-constant' else
                   [.125, -.5, 2, 1] if name == 'float-constant' else
                   [(i - 64) / 32, -.25 if name == 'float-row0' else .75, i / 128, 1])
    return values


def assess(result):
    """Evidence is saved BEFORE assessment; optional query errors are retained, not passes."""
    s = result['step']
    if result['before']['errors'] or not result['before']['drained'] or result['skipped']:
        return 'fatal-precondition'
    if not result['after']['drained'] or result['contextLost']:
        return 'fatal-context'
    if result['after']['errors'] or result['exception']:
        return 'query-error' if s.get('query') else 'fatal-operation'
    v = result['value']
    if s['op'] == 'framebuffer-status' and v['status'] != v['completeEnum']:
        return 'fatal-framebuffer'
    if s['op'] == 'framebuffer-binding' and not v['bound']:
        return 'fatal-framebuffer'
    if s['op'] in ('compile', 'render') and v['callbacks']:
        return 'fatal-shader'
    if s['op'] == 'program-link' and not v['linked']:
        return 'fatal-shader'
    if s['op'].startswith('read-'):
        want = expected(s['name'])
        bits = want if s['name'] == 'byte-constant' else [struct.unpack('<I', struct.pack('<f', x))[0] for x in want]
        if v['expected'] != want or v['values'] != want or v['bits'] != bits:
            return 'fatal-readback'
    return 'ok'


def main():
    gate()
    launch = read(PREFIX + '-once-launch.json')
    assert launch['child_pid_parent'] == os.getppid(), 'Use the frozen foreground launcher'
    assert launch['preparation_sha256'] == digest(PREFIX + '-preparation-integrity.json')
    save(PREFIX + '-started.json', {'pid': os.getpid(), 'launch_sha256': digest(PREFIX + '-once-launch.json')})
    from playwright.sync_api import sync_playwright
    events, classifications, errors = [], [], []
    browser = page = None
    failure = None

    def event(kind, payload):
        n = PREFIX + '-event-' + str(len(events)).zfill(3) + '.json'
        save(n, {'kind': kind, 'payload': payload, 'previous_sha256': digest(events[-1]) if events else None})
        events.append(n)

    try:
        with sync_playwright() as pw:
            try:
                event('browser-launch-intent', {'args': ARGS})
                browser = pw.chromium.launch(headless=True, args=ARGS)
                event('browser-launched', {'version': browser.version})
                page = browser.new_page()
                page.on('pageerror', lambda e: errors.append({'kind': 'pageerror', 'text': str(e)}))
                page.on('console', lambda m: errors.append({'kind': 'console', 'type': m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
                page.goto((HERE / 'gpu_centre_v34_gl_localization.html').as_uri(), wait_until='load')
                plan = page.evaluate('localizationPlan()')
                assert plan == read(PREFIX + '-static.json')['plan'], 'Plan changed'
                event('plan', plan)
                for step in plan:
                    event('step-intent', step)
                    result = page.evaluate('s=>localizationStep(s)', step)
                    event('step-result', result)
                    classification = assess(result)
                    classifications.append({'step': step, 'classification': classification})
                    event('assessment', classifications[-1])
                    if classification.startswith('fatal'):
                        raise RuntimeError(classification + ': ' + json.dumps(step))
            finally:
                if page is not None:
                    try:
                        event('dispose-intent', {})
                        result = page.evaluate("localizationStep({op:'dispose'})")
                        event('dispose-result', result)
                        if assess(result) != 'ok':
                            failure = 'Resource disposal failed; see durable evidence'
                    except Exception as exc:
                        event('dispose-failure', {'error': str(exc)})
                        failure = 'Resource disposal incomplete'
                    try:
                        page.close(); event('page-closed', {})
                    finally:
                        if browser is not None:
                            browser.close(); event('browser-closed', {})
                elif browser is not None:
                    browser.close(); event('browser-closed', {})
    except Exception as exc:
        failure = str(exc)
        event('failure', {'error': failure})
    query_errors = [r for r in classifications if r['classification'] == 'query-error']
    complete = failure is None and len(classifications) == len(read(PREFIX + '-static.json')['plan'])
    clean = complete and not query_errors and not errors
    save(PREFIX + '-result.json', {'complete': complete, 'infrastructure_clean': clean,
         'failure': failure, 'query_errors': query_errors, 'browser_messages': errors,
         'classifications': classifications, 'events': {n: digest(n) for n in events},
         'numeric_passed': False, 'synthetic_uniform_candidate_supported': False,
         'first_root_certified': False, 'capture_permitted': False, 'new_images': 0})
    print('Infrastructure diagnostic complete:', complete, 'clean:', clean, 'query errors:', len(query_errors), flush=True)
    return 0 if clean else 1


if __name__ == '__main__':
    sys.exit(main())
