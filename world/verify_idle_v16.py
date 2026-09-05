"""Focused reduced-idle invalidation checks using only real input; not full acceptance."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, open_page, diag, next_stage, hold_until, results
from fidelity import render_signature, digest

HERE = Path(__file__).resolve().parent
OUT = HERE / 'verification-idle-v16.json'
assert not OUT.exists(), 'Preserve prior checks'
out = {'render_signature': render_signature(), 'trip_sha256': digest(HERE / 'trip.js'),
       'checks': [], 'observations': [], 'passed': False}

def idle(page):
    page.wait_for_function('''() => { const d=journeyDiagnostics();
        return d.renderReady && !d.transition && !d.renderPending && d.renderedAnimTime===d.animTime; }''')
    before = diag(page)
    page.wait_for_timeout(850)
    after = diag(page)
    out['last_idle_comparison'] = {'before': before, 'after': after}
    for field in ['frames', 'animTime', 'position', 'yaw', 'pitch', 'interactions']:
        assert before[field] == after[field], 'Idle changed ' + field
    assert not after['renderPending']
    out['observations'].append(after)
    return after

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = open_page(browser, viewport={'width': 760, 'height': 900},
                     has_touch=True, is_mobile=True, reduced_motion='reduce')
    page.set_default_timeout(90000)
    try:
        page.locator('#autoStart').uncheck()
        page.locator('#begin').click()
        if diag(page)['detail'] != 'low':
            page.locator('#detail').click()
        before = idle(page)
        assert before['reduced'] and before['detail'] == 'low'
        hold_until(page, 'w', 'journeyDiagnostics().position[2] < 5.5')
        after = idle(page)
        assert after['position'][2] < before['position'][2] and after['frames'] > before['frames']
        assert after['animTime'] == before['animTime']
        out['checks'].append('Reduced keyboard walking redraws then idles with fixed animation')

        cdp = page.context.new_cdp_session(page)
        box = page.locator('[data-move="back"]').bounding_box()
        point = {'x': box['x'] + box['width']/2, 'y': box['y'] + box['height']/2}
        before = after
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [point]})
        page.wait_for_timeout(800)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        after = idle(page)
        assert after['position'][2] > before['position'][2] + .5 and after['frames'] > before['frames']
        out['checks'].append('Real touch walking redraws then idles')
        before = after
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 100, 'y': 240}]})
        for i in range(1, 6):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 100+14*i, 'y': 240+4*i}]})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        after = idle(page)
        assert after['yaw'] != before['yaw'] and after['pitch'] != before['pitch'] and after['frames'] > before['frames']
        out['checks'].append('Real touch look redraws both axes then idles')

        for name in ['geometry', 'chrysanthemum', 'rush', 'membrane', 'waiting']:
            before = after
            next_stage(page, name)
            after = idle(page)
            assert after['frames'] > before['frames'] and not after['missingEvidence'] and after['uncitedMeshes'] == 0
        out['checks'].append('Reduced button transitions rebuild and settle, including equal entry poses')
        before = after
        actor = after['actors'][0]
        page.mouse.click(*actor['screen'])
        after = idle(page)
        assert after['interactions'] > before['interactions'] and after['frames'] > before['frames']
        assert after['position'] == before['position'] and after['animTime'] == before['animTime']
        out['checks'].append('Fixed-pose being click invalidates the reduced view then idles')

        page.locator('#sources').click()
        idle(page)
        page.locator('#closeEvidence').click()
        idle(page)
        out['checks'].append('Sources open/close preserve idle reduced view')
        page.locator('#motion').click()
        page.wait_for_function('(f)=>journeyDiagnostics().frames>f+1', arg=after['frames'])
        assert diag(page)['animTime'] > after['animTime']
        page.locator('#pause').click()
        idle(page)
        out['checks'].append('Motion resumes animation/submissions and pause drains them')
        page.locator('#motion').click()
        page.locator('#pause').click()
        idle(page)
        page.locator('#restart').click()
        after = idle(page)
        assert after['stage'] == 'onset' and not after['entered'] and after['interactions'] == 0
        out['checks'].append('Restart rebuilds a settled reduced welcome scene')
        out['errors'] = results['errors']
        assert not out['errors'], out['errors']
        out['passed'] = True
    except Exception as exc:
        out['failure'] = str(exc)
        out['failure_diagnostics'] = diag(page)
        raise
    finally:
        OUT.write_text(json.dumps(out, indent=2) + '\n')
        browser.close()
print(json.dumps({'passed': out['passed'], 'checks': out['checks']}))
