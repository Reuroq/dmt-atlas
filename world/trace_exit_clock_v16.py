"""One-shot short real-input timing diagnosis, NOT a repeat of the exit gate."""
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, next_stage, diag

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-exit-clock-v16'
assert not list(HERE.glob(PREFIX+'*')), 'Preserve evidence'
source = (HERE/'trip.js').read_text()
assert source == (HERE/'trip-v16.js').read_text()
needle = 'requestAnimationFrame(frame);const dt=Math.min((now-lastFrame)/1000,1);lastFrame=now;'
assert source.count(needle) == 1
source = source.replace(needle, '''requestAnimationFrame(frame);
 const raw=(now-lastFrame)/1000,dt=Math.min(raw,1);lastFrame=now;
 window.exitClockTrace.push({now,raw,dt,stage:stage.id,keys:[...input],paused,transition:!!transition,z:camera.position.z});''')
source = 'window.exitClockTrace=[];\n'+source
(HERE/(PREFIX+'.js')).write_text(source)
html = (HERE/'index.html').read_text().replace('src="trip.js"', f'src="{PREFIX}.js"')
(HERE/(PREFIX+'.html')).write_text(html)
out = {'errors': [], 'purpose': 'Six-second real forward hold, not original exit gate'}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = browser.new_page(viewport={'width':1000,'height':700})
    page.set_default_timeout(90000)
    page.on('pageerror', lambda e: out['errors'].append(str(e)))
    page.on('console', lambda m: out['errors'].append(m.text) if m.type=='error' else None)
    try:
        page.goto((HERE/(PREFIX+'.html')).as_uri())
        page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        page.locator('#autoStart').uncheck()
        page.locator('#begin').click()
        next_stage(page,'geometry')
        next_stage(page,'chrysanthemum')
        out['before']=diag(page)
        page.keyboard.down('w')
        page.wait_for_timeout(6000)
        page.keyboard.up('w')
        out['after']=diag(page)
        page.locator('#pause').click()
        out['trace']=page.evaluate('exitClockTrace')
        held=[r for r in out['trace'] if r['stage']=='chrysanthemum' and 'forward' in r['keys']]
        out['held_frames']=len(held)
        out['raw_held_seconds']=sum(r['raw'] for r in held)
        out['integrated_held_seconds']=sum(r['dt'] for r in held)
        out['dropped_held_seconds']=sum(max(0,r['raw']-r['dt']) for r in held)
    except Exception as exc:
        out['failure']=str(exc)
    finally:
        browser.close()
out['files']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['trip.js','continuum.js',PREFIX+'.js',PREFIX+'.html',Path(__file__).name]}
(HERE/(PREFIX+'.json')).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['trace','before','after','files']}),flush=True)
assert 'failure' not in out and not out['errors']
