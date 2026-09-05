"""Offline journey acceptance via real controls and read-only diagnostics. Foreground only.

Run node --check world/trip.js first. Optional --only desktop|mobile|paced|fallback.
No injected navigation or animation-clock shortcuts; paced completion runs in real time.
"""
import argparse
import io
import json
import time
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROUTE = ['onset', 'geometry', 'chrysanthemum', 'rush', 'membrane', 'waiting',
         'cathedral', 'contact', 'download', 'return', 'afterglow']
BRANCHES = ['workshop', 'garden', 'clinical', 'void']
ARGS = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
        '--allow-file-access-from-files']
results = {'errors': [], 'sections': {}}


def announce(message):
    print(message, flush=True)
    (HERE / 'status.txt').write_text(message + '\n', encoding='utf-8')


def diag(page):
    return page.evaluate('journeyDiagnostics()')


def open_page(browser, **options):
    page = browser.new_page(**options)
    page.set_default_timeout(20000)
    page.on('pageerror', lambda e: results['errors'].append(str(e)))
    page.on('console', lambda m: results['errors'].append(m.text) if m.type == 'error' else None)
    # Verify the journey needs no network, without fetching report/depiction links.
    page.route('https://**/*', lambda r: r.abort())
    page.route('http://**/*', lambda r: r.abort())
    page.goto((HERE / 'index.html').as_uri(), wait_until='load')
    page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
    return page


def stage(page, name):
    page.wait_for_function('(id) => journeyDiagnostics().stage === id && !journeyDiagnostics().transition', arg=name)
    return diag(page)


def next_stage(page, name, touch=False):
    if touch:
        page.locator('#next').tap()
    else:
        page.locator('#next').click()
    return stage(page, name)


def hold_until(page, key, condition, timeout=18000):
    page.keyboard.down(key)
    try:
        page.wait_for_function(condition, timeout=timeout)
    finally:
        page.keyboard.up(key)


def snapshot(page, name):
    page.screenshot(path=str(HERE / f'journey-{name}.png'))
    page.screenshot(path=str(HERE / 'latest.png'))


def evidence(page):
    d = diag(page)
    assert not d['missingEvidence'], d['missingEvidence']
    assert d['sourceCount'] > 0 and d['uncitedMeshes'] == 0, d
    assert all(a['evidence'] in d['evidence'] for a in d['actors']), d
    page.locator('#sources').click()
    text = page.locator('#evidenceContent').inner_text()
    assert 'Evidence entry unavailable' not in text and 'Unresolved citation' not in text, text
    assert page.locator('#evidenceContent .node').count() == len(d['evidence'])
    assert page.locator('#evidenceContent .source').count() > 0
    links = page.locator('#evidenceContent a').evaluate_all('(items) => items.map(a => a.href)')
    assert all(s.startswith(('https://', 'http://')) for s in links)
    page.locator('#closeEvidence').click()
    return {'stage': d['stage'], 'keys': d['evidence'], 'sources': d['sourceCount'],
            'links': len(links), 'drawCalls': d['drawCalls'], 'geometries': d['geometries']}


def still(page, field, seconds=.65):
    before = diag(page)[field]
    page.wait_for_timeout(seconds * 1000)
    assert diag(page)[field] == before, (field, before, diag(page)[field])


def desktop(browser):
    page = open_page(browser, viewport={'width': 1440, 'height': 960}, device_scale_factor=1)
    out = {'evidence': []}
    snapshot(page, 'entrance')
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    hold_until(page, 'w', 'journeyDiagnostics().position[2] < 4.8')
    assert not diag(page)['paced']
    page.mouse.move(900, 370)
    page.mouse.down()
    page.mouse.move(980, 400, steps=6)
    page.mouse.up()
    assert abs(diag(page)['yaw']) > .2 and abs(diag(page)['pitch']) > .05
    page.mouse.move(980, 400)
    page.mouse.down()
    page.mouse.move(900, 370, steps=6)
    page.mouse.up()
    assert abs(diag(page)['yaw']) < .01
    page.locator('#pause').click()
    for field in ['position', 'animTime', 'elapsed']:
        still(page, field)
    assert page.locator('#next').is_disabled()
    page.keyboard.down('w')
    still(page, 'position')
    page.keyboard.up('w')
    page.locator('#pause').click()
    page.keyboard.press('e')
    for field in ['position', 'animTime', 'elapsed']:
        still(page, field)
    page.keyboard.press('Escape')
    assert not page.locator('#evidence').is_visible() and not diag(page)['paused']
    out['evidence'].append(evidence(page))
    # Actual room exit, including the central lane past the coffee table.
    hold_until(page, 'w', "journeyDiagnostics().transition", timeout=22000)
    stage(page, 'geometry')
    for name in ROUTE[1:7]:
        if diag(page)['stage'] != name:
            next_stage(page, name)
        out['evidence'].append(evidence(page))
        if name in ['chrysanthemum', 'waiting']:
            snapshot(page, name)
        if name == 'waiting':
            hold_until(page, 'a', 'journeyDiagnostics().position[0] < -6.8')
            page.keyboard.down('w')
            page.wait_for_timeout(2800)
            page.keyboard.up('w')
            assert 6.19 <= diag(page)['position'][2] < 6.5, diag(page)
    # Columns have solid bases, but the side doorway remains reachable.
    hold_until(page, 'd', 'journeyDiagnostics().position[0] > 11.6')
    page.keyboard.down('d')
    page.wait_for_timeout(600)
    page.keyboard.up('d')
    assert diag(page)['position'][0] <= 11.86, diag(page)
    hold_until(page, 'a', 'journeyDiagnostics().position[0] < .1')
    hold_until(page, 'w', 'journeyDiagnostics().position[2] < 7.6')
    hold_until(page, 'a', 'journeyDiagnostics().transition')
    stage(page, 'garden')
    out['physicalSideDoor'] = True
    next_stage(page, 'cathedral')
    baseline_memory = diag(page)['geometries']
    for name in BRANCHES:
        announce(f'Checking optional path: {name}')
        page.locator('#pathsToggle').click()
        page.locator(f'[data-branch="{name}"]').click()
        d = stage(page, name)
        out['evidence'].append(evidence(page))
        if name != 'void':
            assert d['actors'] and all(a['joints'] >= 2 for a in d['actors'])
            if name in ['garden', 'clinical']:
                hold_until(page, 'w', 'journeyDiagnostics().position[2] < 4')
            else:
                hold_until(page, 'w', 'journeyDiagnostics().position[2] < 2')
            a = diag(page)['actors'][0]
            before = diag(page)['interactions']
            page.mouse.click(*a['screen'])
            assert diag(page)['interactions'] > before, (name, a)
            arm = diag(page)['actors'][0]['arm']
            page.wait_for_timeout(750)
            assert diag(page)['actors'][0]['arm'] != arm
            assert diag(page)['actors'][0]['engaged']
            snapshot(page, name)
        if name == 'clinical':
            page.keyboard.down('d')
            page.wait_for_timeout(3800)
            page.keyboard.up('d')
            assert 6.5 < diag(page)['position'][0] <= 6.81, diag(page)
        if name == 'void':
            page.keyboard.down('d')
            page.wait_for_timeout(6800)
            page.keyboard.up('d')
            assert diag(page)['position'][0] == 18
        next_stage(page, 'cathedral')
        assert diag(page)['geometries'] <= baseline_memory + 2, diag(page)
    snapshot(page, 'cathedral')
    for name in ROUTE[7:]:
        next_stage(page, name)
        out['evidence'].append(evidence(page))
        if name in ['contact', 'download']:
            hold_until(page, 'w', 'journeyDiagnostics().position[2] < 2')
            assert any(a['engaged'] for a in diag(page)['actors'])
        snapshot(page, name)
    assert set(diag(page)['visited']) == set(ROUTE + BRANCHES)
    assert page.locator('#stateText').inner_text() == 'Journey complete'
    out['complete'] = diag(page)
    page.locator('#next').click()
    assert page.locator('#welcome').is_visible()
    assert not diag(page)['entered'] and not diag(page)['interactions']
    page.locator('#begin').click()
    page.locator('#motion').click()
    page.locator('#pace').click()
    for field in ['position', 'animTime']:
        still(page, field)
    # Pixel equality catches elapsed-time-driven surface effects, not just frozen clock values.
    clip = {'x': 300, 'y': 150, 'width': 700, 'height': 340}
    a = Image.open(io.BytesIO(page.screenshot(clip=clip))).convert('RGB')
    page.wait_for_timeout(1000)
    b = Image.open(io.BytesIO(page.screenshot(clip=clip))).convert('RGB')
    assert ImageChops.difference(a, b).getbbox() is None, 'Reduced motion changed visible surfaces'
    hold_until(page, 'w', 'journeyDiagnostics().position[2] < 5.5')
    assert not diag(page)['paced'], 'Walking must leave paced mode'
    out['checks'] = ['keyboard', 'drag', 'pause', 'sources freeze', 'room exit', 'bench collision',
                     'column collision', 'cabinet collision', 'boundary', 'physical side portal',
                     'all branch returns', 'actor picking/proximity/animation', 'geometry disposal',
                     'full manual route', 'restart', 'reduced motion pixel stillness']
    page.close()
    return out


def layout(page):
    return page.evaluate('''() => {
      const controls = [...document.querySelectorAll('button, #welcome input')]
        .filter(e => e.getClientRects().length && !e.closest('dialog'));
      const errors = [];
      for (const e of controls) {
        const r = e.getBoundingClientRect();
        if (r.left < 0 || r.top < 0 || r.right > innerWidth + 1 || r.bottom > innerHeight + 1)
          errors.push('offscreen: ' + e.textContent);
        const top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
        if (!e.contains(top)) errors.push('obscured: ' + e.textContent);
      }
      if (document.documentElement.scrollWidth > innerWidth) errors.push('horizontal overflow');
      return errors;
    }''')


def mobile(browser):
    page = open_page(browser, viewport={'width': 390, 'height': 844}, device_scale_factor=1,
                     is_mobile=True, has_touch=True, reduced_motion='reduce')
    assert not layout(page), layout(page)
    page.locator('#autoStart').uncheck()
    page.locator('#begin').tap()
    assert diag(page)['reduced'] and page.locator('#touchControls').is_visible()
    assert not layout(page), layout(page)
    # Real Chromium touch events, including a held directional button and a look drag.
    cdp = page.context.new_cdp_session(page)
    box = page.locator('[data-move="forward"]').bounding_box()
    point = {'x': box['x'] + box['width']/2, 'y': box['y'] + box['height']/2}
    before = diag(page)['position'][2]
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [point]})
    page.wait_for_timeout(800)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    assert diag(page)['position'][2] < before - .5
    still(page, 'position')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 100, 'y': 240}]})
    for i in range(1, 6):
        page.wait_for_timeout(50)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 100 + 14*i, 'y': 240 + 4*i}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    page.wait_for_timeout(350)
    assert abs(diag(page)['yaw']) > .1
    for name in ROUTE[1:7]:
        next_stage(page, name, touch=True)
    page.locator('#pathsToggle').tap()
    assert not layout(page), layout(page)
    snapshot(page, 'mobile-paths')
    page.locator('[data-branch="garden"]').tap()
    stage(page, 'garden')
    snapshot(page, 'mobile-garden')
    page.locator('#sources').tap()
    assert page.locator('#evidence').is_visible()
    assert page.locator('#closeEvidence').is_visible()
    page.locator('#closeEvidence').tap()
    next_stage(page, 'cathedral', touch=True)
    for width, height in [(360, 640), (844, 390)]:
        page.set_viewport_size({'width': width, 'height': height})
        page.locator('#pathsToggle').tap()
        assert not layout(page), (width, height, layout(page))
        snapshot(page, f'mobile-{width}x{height}')
        page.locator('#pathsToggle').tap()
    page.locator('#restart').tap()
    assert not layout(page), layout(page)
    page.close()
    return {'checks': ['system reduced motion', 'touch walk/release', 'touch look', 'sources',
                       'branch return', 'unobscured controls at 390x844, 360x640, 844x390']}


def paced(browser):
    # Smaller framebuffer keeps software rendering close to normal browser frame cadence.
    page = open_page(browser, viewport={'width': 800, 'height': 600}, device_scale_factor=1)
    page.locator('#begin').click()
    assert diag(page)['paced']
    page.wait_for_timeout(900)
    assert diag(page)['position'][2] < 6.5
    page.locator('#pause').click()
    for field in ['elapsed', 'animTime', 'position']:
        still(page, field)
    page.locator('#pause').click()
    page.locator('#sources').click()
    still(page, 'elapsed')
    page.locator('#closeEvidence').click()
    started = time.monotonic()
    observed = []
    while time.monotonic() - started < 600:
        d = diag(page)
        if not d['transition'] and d['stage'] not in observed:
            observed.append(d['stage'])
            announce(f'Paced journey acceptance: {d["stage"]}')
            assert not d['missingEvidence']
            if d['stage'] == 'chrysanthemum':
                # Timed passage continues with user-selected still views.
                page.locator('#motion').click()
                still(page, 'position')
                still(page, 'animTime')
            if d['stage'] == 'rush':
                page.locator('#motion').click()
            if d['stage'] == 'afterglow':
                break
        page.wait_for_timeout(1000)
    assert observed == ROUTE, observed
    assert diag(page)['visited'] == ROUTE and diag(page)['paced']
    out = {'observed': observed, 'wallSeconds': round(time.monotonic() - started, 1), 'complete': diag(page)}
    snapshot(page, 'paced-complete')
    page.close()
    return out


def fallback(browser):
    page = browser.new_page(viewport={'width': 1000, 'height': 800})
    # Simulate an actual unavailable WebGL context, not application navigation.
    page.add_init_script('''const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
        return kind.startsWith('webgl') || kind === 'experimental-webgl' ? null : original.call(this, kind, ...args);
      };''')
    page.goto((HERE / 'index.html').as_uri(), wait_until='load')
    assert page.locator('#failure').is_visible()
    assert page.locator('#failure a').get_attribute('href') == 'evidence.html'
    page.locator('#failure a').click()
    assert page.url.endswith('/evidence.html')
    page.close()
    return {'unavailableWebGL': 'visible fallback and working local evidence link'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', choices=['desktop', 'mobile', 'paced', 'fallback'])
    args = parser.parse_args()
    sections = [args.only] if args.only else ['desktop', 'mobile', 'paced', 'fallback']
    destination = HERE / (f'verification-{args.only}.json' if args.only else 'verification.json')
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=ARGS)
            for name in sections:
                announce(f'Verifying journey: {name}')
                results['sections'][name] = globals()[name](browser)
                assert not results['errors'], results['errors']
                destination.write_text(json.dumps(results, indent=2), encoding='utf-8')
            browser.close()
        results['passed'] = True
        announce('Journey acceptance passed: ' + ', '.join(sections))
    except Exception as e:
        results['passed'] = False
        results['failure'] = str(e)
        announce('Journey acceptance needs a fix: ' + str(e)[:180])
        raise
    finally:
        destination.write_text(json.dumps(results, indent=2), encoding='utf-8')
