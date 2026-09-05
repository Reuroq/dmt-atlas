"""One-shot 1200x800 HIGH entry/deep pairs; normal controls, failure receipts."""
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS
from fidelity import RENDER_FILES, render_signature

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v34'
HTML = PREFIX+'.html'
CANDIDATE = 'continuum-v34-candidate.js'
assert not list(HERE.glob(PREFIX+'*')), 'Preserve one-shot evidence'
gate=json.loads((HERE/'centre-v34-integrity.json').read_text())
assert gate['integrity_passed'] and gate['numeric_passed']

def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

protected = list(dict.fromkeys(RENDER_FILES+['data.js','fidelity-data.js',
    'fidelity-grades.json','realism-grades.json','latest.png',
    'visual-chrysanthemum.png','visual-chrysanthemum.json']))
before = {n: digest(n) for n in protected}
assert before==gate['protected']
assert all(digest(n)==h for n,h in gate['files'].items()), 'Numerical-phase evidence changed'
html = (HERE/'index.html').read_text()
assert html.count('src="continuum.js"') == 1
html = html.replace('src="continuum.js"', f'src="{CANDIDATE}"')
html = html.replace('A reported-pattern interpretation', 'ISOLATED v34 · synthesised diagnostic')
(HERE/HTML).write_text(html)
sources = {n: digest(n) for n in dict.fromkeys(RENDER_FILES+[HTML,CANDIDATE,
    Path(__file__).name,'data.js','fidelity-data.js'])}
errors, receipts, timings = [], [], []
summary = {'diagnostic_only': True, 'live_render_signature': render_signature(),
    'source_hashes': sources, 'protected_before': before, 'receipts': receipts,
    'timings': timings, 'errors': errors, 'passed': False,
    'limits': 'Two separated frames are not a temporal antialiasing proof. SwiftShader wall times are not hardware-GPU benchmarks. No pose, route or clock injection.'}
operation = 'initialization'
operation_start = time.monotonic()

def save():
    (HERE/(PREFIX+'-receipts.json')).write_text(json.dumps(summary, indent=2)+'\n')

def mark(name):
    global operation, operation_start
    operation, operation_start = name, time.monotonic()
    summary['current_operation'] = name
    save()
    print(name, flush=True)

def diag(page):
    return page.evaluate('journeyDiagnostics()')

def capture(page, label):
    mark(label+' settle')
    page.wait_for_function('!journeyDiagnostics().renderPending && journeyDiagnostics().renderedAnimTime===journeyDiagnostics().animTime')
    settle = time.monotonic()-operation_start
    d = diag(page)
    assert d['stage']=='chrysanthemum' and d['paused'] and d['detail']=='high'
    assert not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes']==0 and not errors
    mark(label+' screenshot')
    png = PREFIX+'-'+label+'.png'
    page.screenshot(path=str(HERE/png))
    receipt = {'diagnostic_only': True, 'file': png, 'capture_sha256': digest(png),
        'resolution': [1200,800], 'capture_diagnostics': d, 'source_hashes': sources,
        'errors': list(errors), 'settle_seconds': settle,
        'screenshot_seconds': time.monotonic()-operation_start,
        'veil_opacity': page.locator('#veil').evaluate('(e)=>Number(getComputedStyle(e).opacity)')}
    assert receipt['veil_opacity']==0
    (HERE/png).with_suffix('.json').write_text(json.dumps(receipt, indent=2)+'\n')
    receipts.append(receipt)
    save()
    print(json.dumps({'captured': png,'position': d['position'],'animTime': d['animTime'],
        'frames': d['frames'],'settle_seconds': settle}), flush=True)
    return d

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        page = browser.new_page(viewport={'width':1200,'height':800}, device_scale_factor=1)
        page.set_default_timeout(90000)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type=='error' else None)
        page.route('https://**/*', lambda r: r.abort())
        page.route('http://**/*', lambda r: r.abort())
        try:
            mark('launch and real navigation')
            page.goto((HERE/HTML).as_uri())
            page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
            page.locator('#autoStart').uncheck()
            page.locator('#begin').click()
            for stage in ['geometry','chrysanthemum']:
                page.locator('#next').click()
                page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=stage)
            page.locator('#pause').click()
            timings.append({'operation': operation, 'wall_seconds': time.monotonic()-operation_start,
                'excludes_gpu_settling': True})
            for label in ['entry','deep']:
                if label=='deep':
                    mark('real walk to z -6; timer-observed stop and native pause')
                    before_walk=diag(page)
                    page.keyboard.press('Space')
                    page.keyboard.down('w')
                    try:
                        # RAF polling can wait behind an expensive frame while
                        # the independent movement timer keeps integrating input.
                        # This is a fixture change, not a proven cause of v30.
                        stop_handle=page.wait_for_function('()=>{const d=journeyDiagnostics();return d.stage!=="chrysanthemum" || d.position[2]<=-6 ? d : false;}', polling=50, timeout=45000)
                    finally:
                        page.keyboard.up('w')
                    page.keyboard.press('Space')
                    stopped=diag(page)
                    observed_stop=stop_handle.json_value()
                    stop_handle.dispose()
                    timings.append({'operation': operation, 'wall_seconds': time.monotonic()-operation_start,
                        'before':before_walk,'observed_stop':observed_stop,'after_release_pause':stopped,
                        'polling_ms':50,'native_controls':True})
                    save()
                    assert stopped['stage']=='chrysanthemum' and not stopped['transition']
                    assert -8<=stopped['position'][2]<=-6, 'Deep stop overshoot; do not accept wrong pose'
                first = capture(page, label)
                mark(label+' real temporal advance and pause')
                start = time.monotonic()
                page.keyboard.press('Space')
                page.wait_for_function('(t)=>journeyDiagnostics().animTime>=t', arg=first['animTime']+3, polling=50)
                page.keyboard.press('Space')
                second = capture(page, label+'-motion')
                wall = time.monotonic()-start
                assert all(first[k]==second[k] for k in ['position','yaw','pitch','stage','detail'])
                assert second['animTime']-first['animTime']>=3
                timings.append({'operation': label+' temporal pair including controls, settle and screenshot',
                    'wall_seconds': wall,'animation_seconds': second['animTime']-first['animTime'],
                    'completed_frames': second['frames']-first['frames'],
                    'frames_per_wall_second': (second['frames']-first['frames'])/wall})
            summary['passed'] = len(receipts)==4 and not errors
        except Exception as exc:
            summary['failure'] = {'operation': operation, 'operation_wall_seconds': time.monotonic()-operation_start,
                'exception': repr(exc)}
            try:
                summary['failure']['diagnostics'] = diag(page)
            except Exception as diagnostic_error:
                summary['failure']['diagnostics_error'] = repr(diagnostic_error)
            save()
            raise
        finally:
            browser.close()
finally:
    summary['protected_after'] = {n: digest(n) for n in protected}
    summary['protected_unchanged'] = summary['protected_after']==before
    save()
    print(json.dumps({'passed': summary['passed'], 'protected_unchanged': summary['protected_unchanged'],
        'capture_count': len(receipts), 'timings': timings}), flush=True)
