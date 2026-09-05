"""One-shot isolated full-resolution candidate review; real controls only."""
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS
from fidelity import RENDER_FILES, render_signature

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v27r2'
HTML = PREFIX + '.html'
SCRIPT = Path(__file__).name
CANDIDATE = 'continuum-v27r2-candidate.js'
assert not list(HERE.glob(PREFIX + '*')), 'Preserve one-shot evidence'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

protected = list(dict.fromkeys(RENDER_FILES + ['data.js', 'fidelity-data.js',
    'fidelity-grades.json', 'realism-grades.json', 'latest.png',
    'visual-chrysanthemum.png', 'visual-chrysanthemum.json']))
before = {name: digest(name) for name in protected}
html = (HERE / 'index.html').read_text()
assert html.count('src="continuum.js"') == 1
html = html.replace('src="continuum.js"', f'src="{CANDIDATE}"')
html = html.replace('A reported-pattern interpretation', 'ISOLATED v27r2 · synthesised diagnostic')
(HERE / HTML).write_text(html)
sources = {name: digest(name) for name in dict.fromkeys(RENDER_FILES + [HTML, SCRIPT, CANDIDATE, 'data.js', 'fidelity-data.js'])}
receipts, timings, errors = [], [], []
summary = {'diagnostic_only': True, 'live_render_signature': render_signature(),
    'source_hashes': sources, 'protected_before': before, 'receipts': receipts,
    'timings': timings, 'errors': errors, 'passed': False,
    'limits': 'Isolated candidate, not a live acceptance or descriptor grade. SwiftShader wall times are not hardware-GPU predictions. Two separated frames cannot prove temporal antialiasing.'}

def diag(page):
    return page.evaluate('journeyDiagnostics()')

def capture(page, label):
    page.wait_for_function('!journeyDiagnostics().renderPending && journeyDiagnostics().renderedAnimTime===journeyDiagnostics().animTime')
    d = diag(page)
    assert d['stage'] == 'chrysanthemum' and d['paused'] and d['detail'] == 'high'
    assert not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes'] == 0 and not errors
    png = PREFIX + '-' + label + '.png'
    start = time.monotonic()
    page.screenshot(path=str(HERE / png))
    receipt = {'diagnostic_only': True, 'file': png, 'capture_sha256': digest(png),
        'resolution': [1200, 800], 'capture_diagnostics': d, 'source_hashes': sources,
        'errors': list(errors), 'screenshot_seconds': time.monotonic() - start,
        'veil_opacity': page.locator('#veil').evaluate('(e)=>Number(getComputedStyle(e).opacity)')}
    assert receipt['veil_opacity'] == 0
    (HERE / png).with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n')
    receipts.append(receipt)
    print(json.dumps({'captured': png, 'position': d['position'], 'animTime': d['animTime'], 'frames': d['frames']}), flush=True)
    return d

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        page = browser.new_page(viewport={'width': 1200, 'height': 800}, device_scale_factor=1)
        page.set_default_timeout(90000)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.route('https://**/*', lambda r: r.abort())
        page.route('http://**/*', lambda r: r.abort())
        start = time.monotonic()
        page.goto((HERE / HTML).as_uri())
        page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        page.locator('#autoStart').uncheck()
        page.locator('#begin').click()
        for stage in ['geometry', 'chrysanthemum']:
            page.locator('#next').click()
            page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=stage)
            print('Reached ' + stage, flush=True)
        page.locator('#pause').click()
        timings.append({'operation': 'launch and real navigation to entry pause', 'wall_seconds': time.monotonic() - start})
        for label in ['entry', 'deep']:
            if label == 'deep':
                start = time.monotonic()
                page.locator('#pause').click()
                page.keyboard.down('w')
                try:
                    page.wait_for_function('journeyDiagnostics().stage!=="chrysanthemum" || journeyDiagnostics().position[2]<=-6')
                finally:
                    page.keyboard.up('w')
                page.locator('#pause').click()
                timings.append({'operation': 'real walk to z -6 and pause', 'wall_seconds': time.monotonic() - start})
            first = capture(page, label)
            start = time.monotonic()
            page.locator('#pause').click()
            page.wait_for_function('(t)=>journeyDiagnostics().animTime>=t', arg=first['animTime'] + 3)
            page.locator('#pause').click()
            second = capture(page, label + '-motion')
            wall = time.monotonic() - start
            assert all(first[k] == second[k] for k in ['position', 'yaw', 'pitch', 'stage', 'detail'])
            assert second['animTime'] - first['animTime'] >= 3
            timings.append({'operation': label + ' temporal pair including controls, settle and screenshot',
                'wall_seconds': wall, 'animation_seconds': second['animTime'] - first['animTime'],
                'completed_frames': second['frames'] - first['frames'],
                'frames_per_wall_second': (second['frames'] - first['frames']) / wall})
        browser.close()
    summary['passed'] = len(receipts) == 4 and not errors
except Exception as exc:
    summary['failure'] = repr(exc)
    raise
finally:
    summary['protected_after'] = {name: digest(name) for name in protected}
    summary['protected_unchanged'] = summary['protected_after'] == before
    (HERE / (PREFIX + '-receipts.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'passed': summary['passed'], 'protected_unchanged': summary['protected_unchanged'], 'timings': timings}), flush=True)
