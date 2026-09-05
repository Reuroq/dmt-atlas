"""Original 45s real-input central exit, isolated from the failed lateral gate."""
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, next_stage, stage, diag, hold_until

HERE=Path(__file__).resolve().parent
OUT=HERE/'verification-exit-only-v17.json'
assert not OUT.exists(), 'Preserve evidence'
out={'passed':False,'errors':[],'exit_walk_timeout_ms':45000,
     'limits':'Exit only; lateral-return failure remains. No full acceptance or live promotion.'}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=ARGS)
    page=browser.new_page(viewport={'width':1000,'height':700})
    page.set_default_timeout(90000)
    page.on('pageerror',lambda e:out['errors'].append(str(e)))
    page.on('console',lambda m:out['errors'].append(m.text) if m.type=='error' else None)
    # Observe native events only; never set journey pose, clock, input or route.
    page.add_init_script('''window.inputTiming=[];
      for(const type of ['keydown','keyup'])addEventListener(type,e=>{
       if(e.key==='w')inputTiming.push({type,stamp:e.timeStamp,now:performance.now(),d:journeyDiagnostics()});
      });''')
    try:
        page.goto((HERE/'walk-clock-v17-candidate.html').as_uri())
        page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        page.locator('#autoStart').uncheck()
        page.locator('#begin').click()
        next_stage(page,'geometry')
        next_stage(page,'chrysanthemum')
        out['before']=diag(page)
        assert out['before']['detail']=='high' and not out['before']['paced']
        start=time.monotonic()
        hold_until(page,'w','journeyDiagnostics().transition',timeout=45000)
        out['exit_wall_seconds']=time.monotonic()-start
        out['destination']=stage(page,'rush')
        d=out['destination']
        assert d['stage']=='rush' and not d['missingEvidence'] and d['uncitedMeshes']==0
        assert out['exit_wall_seconds']<45
        out['passed']=not out['errors']
    except Exception as exc:
        out['failure']=repr(exc)
        out['failure_diagnostics']=diag(page)
    finally:
        out['input_timing']=page.evaluate('inputTiming')
        browser.close()
out['files']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['trip-v17-candidate.js','walk-clock-v17-candidate.html','continuum.js',Path(__file__).name]}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['before','destination','files','input_timing','failure_diagnostics']}))
assert out['passed']
