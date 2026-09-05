"""One-shot native lateral/RAF/render timing diagnosis; no navigation injection."""
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, next_stage, diag, hold_until

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-lateral-v17'
assert not list(HERE.glob(PREFIX+'*')), 'Preserve evidence'
s = (HERE/'trip-v17-candidate.js').read_text()
def change(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
change('function syncMovement(){', '''const lateralTrace=window.lateralTrace=[];
function traceLateral(type,extra={}){if(lateralTrace.length<18000)lateralTrace.push({type,now:performance.now(),stage:stage.id,x:camera.position.x,keys:[...input],frames,pending:!!renderFence,...extra});}
for(const type of ['keydown','keyup'])addEventListener(type,e=>{if(['a','d'].includes(e.key))traceLateral('native-after',{event:type,stamp:e.timeStamp});});
function syncMovement(){''')
change('move(dt);if(!camera.position.equals(drawnPosition))', "traceLateral('move-before',{dt});move(dt);traceLateral('move-after',{dt});if(!camera.position.equals(drawnPosition))")
change('requestAnimationFrame(frame);const dt=', "requestAnimationFrame(frame);traceLateral('raf',{raf:now});const dt=")
change('  composite.render(scene,camera,', "  traceLateral('submit-before');composite.render(scene,camera,")
change('renderReady=true;frames++;', "renderReady=true;frames++;traceLateral('submit-after');")
change("const key=e.key.length===1?", "if(['a','d'].includes(e.key))traceLateral('native-before',{event:e.type,stamp:e.timeStamp});const key=e.key.length===1?")
change("addEventListener('keyup',e=>{syncMovement();", "addEventListener('keyup',e=>{if(['a','d'].includes(e.key))traceLateral('native-before',{event:e.type,stamp:e.timeStamp});syncMovement();")
(HERE/(PREFIX+'.js')).write_text(s)
(HERE/(PREFIX+'.html')).write_text((HERE/'index.html').read_text().replace('src="trip.js"',f'src="{PREFIX}.js"'))
out={'purpose':'Instrument original lateral boundary/centre condition, not full exit acceptance', 'errors':[], 'host':[]}
def host(label):
    out['host'].append({'label':label,'monotonic':time.monotonic()})
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=ARGS)
    page=browser.new_page(viewport={'width':1000,'height':700})
    page.set_default_timeout(90000)
    page.on('pageerror',lambda e:out['errors'].append(str(e)))
    page.on('console',lambda m:out['errors'].append(m.text) if m.type=='error' else None)
    try:
        page.goto((HERE/(PREFIX+'.html')).as_uri())
        page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        page.locator('#autoStart').uncheck()
        page.locator('#begin').click()
        next_stage(page,'geometry')
        next_stage(page,'chrysanthemum')
        # Match original pre-walk Sources-open/close operations.
        page.locator('#sources').click()
        page.locator('#evidenceContent .fidelity-target[open]').inner_text()
        page.locator('#closeEvidence').click()
        hold_until(page,'d','journeyDiagnostics().position[0] >= 3.9',timeout=15000)
        page.keyboard.down('d')
        page.wait_for_timeout(500)
        page.keyboard.up('d')
        out['boundary']=diag(page)
        assert 3.9 <= out['boundary']['position'][0] <= 4
        host('left-down-request')
        page.keyboard.down('a')
        host('left-down-return')
        try:
            page.wait_for_function("""() => {const d=journeyDiagnostics();if(d.position[0]<=0){lateralTrace.push({type:'centre-observed',now:performance.now(),x:d.position[0],frames:d.frames});return true;}return false;}""",timeout=15000,polling=25)
            host('centre-wait-return')
        finally:
            host('left-up-request')
            page.keyboard.up('a')
            host('left-up-return')
        out['after']=diag(page)
        out['centre_pass']=-3.2 <= out['after']['position'][0] <= 0
        page.locator('#pause').click()
    except Exception as exc:
        out['failure']=repr(exc)
    finally:
        out['trace']=page.evaluate('lateralTrace')
        browser.close()
out['files']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['trip-v17-candidate.js','continuum.js',PREFIX+'.js',PREFIX+'.html',Path(__file__).name]}
(HERE/(PREFIX+'.json')).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['trace','files','boundary','after']}),flush=True)
assert 'failure' not in out and not out['errors']
