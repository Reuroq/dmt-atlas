"""Offline journey acceptance via real controls and read-only diagnostics. Foreground only.

Run node --check world/trip.js first. Optional --only desktop|mobile|paced|fallback.
No injected navigation or animation-clock shortcuts; paced completion runs in real time.
"""
import argparse
import io
import json
import time
from pathlib import Path
from fidelity import render_signature

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROUTE = ['onset', 'geometry', 'chrysanthemum', 'rush', 'membrane', 'waiting',
         'cathedral', 'contact', 'download', 'return', 'afterglow']
BRANCHES = ['workshop', 'garden', 'clinical', 'void']
ARGS = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
        '--allow-file-access-from-files']
results = {'errors': [], 'sections': {}, 'render_signature': render_signature()}


def announce(message):
    print(message, flush=True)
    (HERE / 'status.txt').write_text(message + '\n', encoding='utf-8')


def diag(page):
    return page.evaluate('journeyDiagnostics()')


def open_page(browser, **options):
    page = browser.new_page(**options)
    page.set_default_timeout(20000)
    page.on('pageerror', lambda e: results['errors'].append(str(e)))
    # The routes below deliberately abort every off-origin request so acceptance stays offline.
    # Chromium reports each abort as a console error ("Failed to load resource: net::ERR_FAILED"),
    # so counting those makes the harness fail on its own blocking. Harmless while the page had no
    # external references; once world/index.html gained the site GA tag (c978eea, the go-live
    # commit) every run tripped `assert not results['errors']`. d054f73 fixed exactly this in
    # render_visual.py and missed verify.py, which was already dead upstream and so never showed
    # it. Only this self-inflicted signature is ignored; real page and console errors still count.
    blocked = lambda t: 'Failed to load resource' in t and 'ERR_FAILED' in t
    page.on('console', lambda m: results['errors'].append(m.text)
            if m.type == 'error' and not blocked(m.text) else None)
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
        page.wait_for_function(condition, timeout=timeout, polling=25)
    except Exception as exc:
        raise AssertionError(f'Walking {key!r} toward {condition}: {diag(page)}') from exc
    finally:
        page.keyboard.up(key)


def settle_z(page, lo, hi, attempts=10):
    """Park the camera's z between lo and hi using short taps.

    hold_until cannot do this: it releases the key once the condition is met and the release
    handler credits the remaining held wall time, so it overshoots by a load-dependent amount
    (measured 0.119 on an idle machine, 1.056 under load). Short taps keep each correction
    smaller than the lane, so a narrow approach is reproducible instead of a coin flip.
    """
    for _ in range(attempts):
        z = diag(page)['position'][2]
        if lo <= z <= hi:
            return z
        page.keyboard.down('w' if z > hi else 's')
        page.wait_for_timeout(60)
        page.keyboard.up('w' if z > hi else 's')
    z = diag(page)['position'][2]
    assert lo <= z <= hi, ('could not park between', lo, hi, 'ended at', z, diag(page))
    return z


def snapshot(page, name):
    # Settle expensive software-rendered frames using the real pause control.
    entered = diag(page)['entered']
    resume = entered and not diag(page)['paused']
    if resume:
        page.locator('#pause').click()
    try:
        if entered:
            page.wait_for_function('!journeyDiagnostics().renderPending', timeout=90000)
        else:
            # Before begin() the welcome scene animates by design and togglePause() returns
            # early while `entered` is false, so nothing can freeze it: 6b6f046 forces
            # drawInvalidated true on every unfrozen frame, which pins renderPending true
            # forever. Waiting for a settled frame here could never return and timed out at
            # 90 s on the FIRST call, so the whole desktop suite has been dead since that
            # commit. A pre-entry capture only needs a completed frame, not a settled one.
            start = page.evaluate('journeyDiagnostics().frames')
            page.wait_for_function(
                '(n) => journeyDiagnostics().renderReady && journeyDiagnostics().frames > n + 1',
                arg=start, timeout=90000)
        capture = HERE / f'journey-{name}.png'
        page.screenshot(path=str(capture), timeout=90000)
        (HERE / 'latest.png').write_bytes(capture.read_bytes())
    finally:
        if resume:
            page.locator('#pause').click()


def evidence(page):
    d = diag(page)
    assert not d['missingEvidence'], d['missingEvidence']
    assert d['sourceCount'] > 0, d
    # uncitedMeshes can never be non-zero: build() stamps the scene bundle onto every drawable
    # that lacks its own keys, so this asserts the stamp still runs - NOT that anything is
    # traceable to a specific entry. Never quote it as evidence of provenance coverage.
    assert d['uncitedMeshes'] == 0, d
    # The real, falsifiable checks. A drawable carrying a key that resolves to no atlas node is
    # a broken citation and must fail. The generic/specific split is REPORTED, not asserted:
    # stages legitimately sit at 100% generic (afterglow is 159 drawables / 1 evidence set) and
    # authoring per-furnishing provenance by inference would be fabrication (HANDOFF.md D7).
    assert d['danglingMeshEvidence'] == 0, d
    assert d['genericMeshes'] + d['specificMeshes'] > 0, d
    assert all(a['evidence'] in d['evidence'] for a in d['actors']), d
    page.locator('#sources').click()
    # openEvidence() is async now: the report trail (data-reports.js, 3.35 MB) is fetched
    # on idle rather than up front, and the drawer awaits it if a reader gets there first.
    # Reading innerText immediately would race an empty drawer.
    page.wait_for_function("() => document.querySelectorAll('#evidenceContent .node').length > 0",
                           timeout=30000)
    text = page.locator('#evidenceContent').inner_text()
    assert 'Evidence entry unavailable' not in text and 'Unresolved citation' not in text, text
    assert page.locator('#evidenceContent .node').count() == len(d['evidence'])
    assert page.locator('#evidenceContent .source').count() > 0
    assert page.locator('#evidenceContent .fidelity').count() == 1
    assert page.locator('#evidenceContent .fidelity-target[open] tbody tr').count() == 15
    assert 'What reports say / what the render shows' in text
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
    # SwiftShader is a CPU renderer; exercise the real lower-detail control for walking tests.
    # High-detail visuals are captured separately by render_visual.py.
    page.locator('#detail').click()
    assert diag(page)['detail'] == 'low'
    out['detail'] = 'low'
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
    # The garden side door is the portal at x -22, z 9, width 5, but the band's centre is
    # NOT walkable - a column base blocks it, and a strafe from z 9.36 stops dead at
    # x -11.85. The clear lane is around z 7.5, which is what the 7.6 target below has
    # always encoded. A single hold overshoots it by a load-dependent amount, so park
    # with taps instead: at z 6.544 the strafe reaches the wall and the portal never
    # fires. Nothing about the door changed here, only the reliability of the approach.
    hold_until(page, 'w', 'journeyDiagnostics().position[2] < 8.4')
    settle_z(page, 7.0, 7.8)
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
            # Articulation is per-builder, not universal. workshop uses create(), which pushes a
            # pair of arm joints. garden (createContactBeing, "continuous implicit body") and
            # clinical (createClinicalBeing, "solid insectoid examiner") deliberately push none.
            # Both landed in decc304 on Sep 6 - the day AFTER 6b6f046 blinded this suite at its
            # first snapshot - so the old blanket `joints >= 2` never once ran against them and
            # would have failed if it had. Assert what is actually true: every branch has a being,
            # and an articulated one is articulated in pairs (a lone joint is a broken rig).
            assert d['actors'], (name, d)
            assert all(a['joints'] == 0 or a['joints'] >= 2 for a in d['actors']), (name, d)
            out.setdefault('branchActors', {})[name] = [
                {'kind': a['kind'], 'joints': a['joints']} for a in d['actors']]
            if name in ['garden', 'clinical']:
                hold_until(page, 'w', 'journeyDiagnostics().position[2] < 4')
            else:
                hold_until(page, 'w', 'journeyDiagnostics().position[2] < 2')
            visible = [(i, a) for i, a in enumerate(diag(page)['actors'])
                       if 35 < a['screen'][0] < page.viewport_size['width'] - 35
                       and 80 < a['screen'][1] < page.viewport_size['height'] - 120]
            assert visible, (name, diag(page))
            actor_index, a = min(visible, key=lambda pair: abs(pair[1]['screen'][0] - page.viewport_size['width'] / 2))
            before = diag(page)['interactions']
            page.mouse.click(*a['screen'])
            assert diag(page)['interactions'] > before, (name, a)
            arm = diag(page)['actors'][actor_index]['arm']
            page.wait_for_timeout(750)
            if arm is None:
                # A continuous-body being has no arm joint, so `arm` is undefined and the old
                # `!= arm` compared undefined to undefined and could only ever FAIL - it never
                # ran, because the suite died upstream before decc304 introduced these beings.
                # Engagement is still checked below; their surface animation is shader-driven
                # and this suite measures NO per-actor motion for them. Recorded, not faked.
                out.setdefault('unarticulatedBeings', []).append(
                    {'branch': name, 'kind': a['kind'], 'motionCovered': False})
            else:
                assert diag(page)['actors'][actor_index]['arm'] != arm, (name, a)
            assert diag(page)['actors'][actor_index]['engaged'], (name, a)
            snapshot(page, name)
        if name == 'workshop':
            # Factory stations must block lateral walking but leave the original exit lane open.
            hold_until(page, 'w', 'journeyDiagnostics().position[2] < .7')
            hold_until(page, 'd', 'journeyDiagnostics().position[0] > 4.1')
            page.keyboard.down('d')
            page.wait_for_timeout(700)
            page.keyboard.up('d')
            assert 4.1 < diag(page)['position'][0] <= 4.41, diag(page)
            hold_until(page, 'a', 'journeyDiagnostics().position[0] < .1')
            hold_until(page, 'w', 'journeyDiagnostics().transition')
            stage(page, 'cathedral')
            out['workshopStationCollision'] = True
            out['workshopPhysicalExit'] = True
        if name == 'garden':
            # New lateral stairs and terrace must be solid without closing the path.
            hold_until(page, 'd', 'journeyDiagnostics().position[0] > 6.5')
            page.keyboard.down('d')
            page.wait_for_timeout(700)
            page.keyboard.up('d')
            assert 6.5 < diag(page)['position'][0] <= 6.81, diag(page)
            hold_until(page, 'a', 'journeyDiagnostics().position[0] < .1')
            hold_until(page, 'w', 'journeyDiagnostics().position[2] < .7')
            hold_until(page, 'd', 'journeyDiagnostics().position[0] > 5.1')
            page.keyboard.down('d')
            page.wait_for_timeout(700)
            page.keyboard.up('d')
            assert 5.1 < diag(page)['position'][0] <= 5.41, diag(page)
            hold_until(page, 'a', 'journeyDiagnostics().position[0] < .1')
            hold_until(page, 'w', 'journeyDiagnostics().transition')
            stage(page, 'cathedral')
            out['gardenTerraceCollision'] = True
            out['gardenPhysicalExit'] = True
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
        if name not in ['garden', 'workshop']:
            next_stage(page, 'cathedral')
        assert diag(page)['geometries'] <= baseline_memory + 2, diag(page)
    snapshot(page, 'cathedral')
    for name in ROUTE[7:]:
        next_stage(page, name)
        out['evidence'].append(evidence(page))
        if name in ['contact', 'download']:
            hold_until(page, 'w', 'journeyDiagnostics().position[2] < 2')
            # Proximity engages a being within 8 units (animateBeings). A bare assert here
            # said nothing about WHICH stage or how far away the beings actually were.
            # Sampling immediately after the walk RACES the page: movement measures held wall
            # time, so hold_until's keyboard.up() advances the camera inside the key handler,
            # after the last animation frame. Engagement is evaluated per frame, so the final
            # step that brings a being inside 8 units can land with no frame left to notice.
            # Under SwiftShader only ~2 frames render across the whole walk, which is why this
            # failed on one run and passed on the next. Give it one more frame, then assert.
            page.wait_for_function('(n) => journeyDiagnostics().frames > n',
                                   arg=diag(page)['frames'], timeout=20000)
            d_eng = diag(page)
            assert any(a['engaged'] for a in d_eng['actors']), (
                name, d_eng['position'],
                [(a['kind'], a['dist'], a['engaged']) for a in d_eng['actors']])
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


def assets(browser):
    """Every same-origin asset the page references must be COMMITTED, not merely on disk.

    No browser test can catch this class of failure: the file is present locally, so file://
    acceptance and every local run pass, while production 404s because the file was never
    added. That is exactly what happened to world/hud-alpha-ramp-v18.png - .gitignore carries
    a blanket `world/*.png`, the #hud::before readability scrim that references it shipped in
    6b6f046, and the asset never did. Found on 2026-09-11 by fetching the DEPLOYED page; this
    check exists so the next one is caught here instead.
    """
    import re
    import subprocess
    referenced = set()
    for name in ['index.html', 'trip.css', 'fidelity.css', 'evidence.html']:
        text = (HERE / name).read_text(encoding='utf-8', errors='ignore')
        referenced |= set(re.findall(r'url\("([^"]+)"\)', text))
        referenced |= set(re.findall(r'(?:src|href)="([^"]+)"', text))
    # trip.js injects data-reports.js at runtime, so it appears in no markup. A dynamic
    # src that was never committed 404s exactly like a static one.
    referenced |= set(re.findall(r"\.src\s*=\s*'([^']+)'", (HERE / 'trip.js').read_text(encoding='utf-8')))
    # Normalise: references are relative to world/ and may use ./ or ../, so compare
    # repo-relative paths rather than naive string concatenation.
    import posixpath
    local = sorted({posixpath.normpath('world/' + r) for r in referenced
                    if not r.startswith(('http', '//', '#', '/', 'data:', 'mailto:'))})
    listing = subprocess.run(['git', 'ls-files'], cwd=HERE.parent,
                             capture_output=True, text=True, check=True)
    tracked = set(listing.stdout.splitlines())
    missing = [r for r in local if r not in tracked]
    assert not missing, ('referenced but not committed - these 404 in production', missing)
    absent = [r for r in local if not (HERE.parent / r).exists()]
    assert not absent, ('referenced but not on disk', absent)
    return {'referencedSameOrigin': len(local), 'allCommitted': True}


def fallback(browser):
    page = browser.new_page(viewport={'width': 1000, 'height': 800})
    # Simulate an actual unavailable WebGL context, not application navigation.
    page.add_init_script('''const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
        return kind.startsWith('webgl') || kind === 'experimental-webgl' ? null : original.call(this, kind, ...args);
      };''')
    page.goto((HERE / 'index.html').as_uri(), wait_until='load')
    assert page.locator('#failure').is_visible()
    # c978eea (go-live) added a second link, "The DMT Atlas" -> /, beside the evidence escape
    # hatch, so a bare '#failure a' is now two elements and raises a strict-mode violation
    # instead of checking anything. That commit broke this file twice - the GA tag it also
    # added made the offline routes log console errors - and neither showed, because 6b6f046
    # had already killed the run a day earlier. Assert the escape hatch is present among the
    # links, then click that one specifically.
    hrefs = page.locator('#failure a').evaluate_all('els => els.map(a => a.getAttribute("href"))')
    assert 'evidence.html' in hrefs, hrefs
    page.locator('#failure a[href="evidence.html"]').click()
    assert page.url.endswith('/evidence.html')
    page.close()
    return {'unavailableWebGL': 'visible fallback and working local evidence link'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', choices=['desktop', 'mobile', 'paced', 'fallback', 'assets'])
    args = parser.parse_args()
    sections = [args.only] if args.only else ['assets', 'desktop', 'mobile', 'paced', 'fallback']
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
