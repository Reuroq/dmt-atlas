"""One-shot synthetic literal/uniform GPU arithmetic experiment, not acceptance."""
import numpy as np
from centre_v34_followup_common import (
    HERE, PREFIX, ARGS, read, save, digest, runtime_gate, compare_arm)


def main():
    runtime_gate()
    stem = PREFIX + '-arithmetic'
    save(stem + '-started.json', {'inputs_sha256': digest(PREFIX + '-inputs.json')})
    from playwright.sync_api import sync_playwright
    inputs = read(PREFIX + '-seeds.json')
    texels = np.frombuffer((HERE / (PREFIX + '-texture.f32')).read_bytes(), dtype='<f4')
    events, errors, arms = [], [], []

    def event(name, **payload):
        record = {'event': name, **payload}
        save(stem + '-event-' + str(len(events)).zfill(2) + '.json', record)
        events.append(record)

    browser = page = None
    failure = None
    try:
        with sync_playwright() as playwright:
            try:
                event('browser_launch_started')
                browser = playwright.chromium.launch(headless=True, args=ARGS)
                event('browser_launched', version=browser.version)
                page = browser.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
                page.goto((HERE / 'gpu_centre_v34_offsets.html').as_uri())
                backend = page.evaluate('data=>setupMicroprobe(data)', texels.astype(float).tolist())
                event('shared_texture_and_target_ready', backend=backend)
                assert backend['three'] == '160' and backend['precision'] == 'highp'
                assert backend['highFloat']['precision'] == 23
                for leaf in inputs['leaves']:
                    for arm in ['literal', 'uniform']:
                        identity = {'leaf': leaf['row'], 'arm': arm, 'second': leaf['c2']}
                        event('arm_started', **identity)
                        result = page.evaluate('a=>runMicroprobeArm(a)', identity)
                        # Save all 128 texels, including labelled padding, before interpretation.
                        event('arm_completed', result=result)
                        assert not errors, repr(errors)
                        rows = np.asarray(result['pixels'], dtype=np.float32).reshape(128, 4)
                        assert np.isfinite(rows).all()
                        comparison = compare_arm(rows[:leaf['count']], leaf['values'], leaf['c1'], leaf['c2'])
                        arms.append({'name': leaf['name'], 'arm': arm, 'readback': result, 'comparison': comparison})
            finally:
                if page is not None:
                    try:
                        event('shader_reports', reports=page.evaluate('()=>getMicroprobeShaderReports()'))
                        event('resources_closed', result=page.evaluate('()=>closeMicroprobe()'))
                    except BaseException as exc:
                        errors.append('resource-close: ' + repr(exc))
                if browser is not None:
                    event('browser_close_started')
                    browser.close()
                    event('browser_closed')
    except BaseException as exc:
        failure = repr(exc)
        event('experiment_failed', failure=failure)
    complete = len(arms) == 4 and not errors and failure is None
    # Diagnostic success only: actual-field equality remains wholly untested.
    supported = complete and all(
        next(a for a in arms if a['name'] == leaf['name'] and a['arm'] == 'literal')['comparison']['child_vs_saved_microprobe_parent_mismatches'] > 0
        and all(next(a for a in arms if a['name'] == leaf['name'] and a['arm'] == 'literal')['comparison']['bit_mismatches_per_channel'][i] == 0 for i in [0, 1, 3])
        and next(a for a in arms if a['name'] == leaf['name'] and a['arm'] == 'uniform')['comparison']['exact']
        for leaf in inputs['leaves'])
    save(stem + '-result.json', {'complete': complete, 'failure': failure, 'errors': errors,
         'arms': arms, 'events': events, 'synthetic_uniform_candidate_supported': bool(supported),
         'interpretation': 'Synthetic arithmetic only; not recovered intermediates, compiler attribution, actual-field equality, roots, cost or realism.',
         'numeric_passed': False, 'capture_permitted': False,
         'inputs_sha256': digest(PREFIX + '-inputs.json')})
    print('Arithmetic complete:', complete, 'synthetic candidate supported:', supported, flush=True)
    if not complete:
        raise RuntimeError('Incomplete arithmetic experiment; preserve failure, never replay')


if __name__ == '__main__':
    main()
