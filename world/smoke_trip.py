"""Foreground smoke render of the new journey; full acceptance follows separately."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files'])
    page=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.goto((HERE/'index.html').as_uri(),wait_until='load')
    page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
    page.screenshot(path=str(HERE/'journey-entrance.png'))
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    for stage in ['geometry','chrysanthemum','rush','membrane','waiting','cathedral']:
        page.locator('#next').click()
        page.wait_for_function('(id)=>journeyDiagnostics().stage===id && !journeyDiagnostics().transition',arg=stage)
        if stage in ['chrysanthemum','waiting','cathedral']:
            page.screenshot(path=str(HERE/f'journey-{stage}.png'))
    page.screenshot(path=str(HERE/'latest.png'))
    result=page.evaluate('journeyDiagnostics()')
    browser.close()
(HERE/'smoke-trip.json').write_text(json.dumps({'errors':errors,'result':result},indent=2),encoding='utf-8')
print(json.dumps({'errors':errors,'stage':result['stage'],'drawCalls':result['drawCalls'],'missingEvidence':result['missingEvidence']}))
assert not errors,errors
