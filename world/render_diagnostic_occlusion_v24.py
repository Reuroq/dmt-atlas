"""One-shot synchronized HIGH diagnosis using real navigation, pause and walking."""
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-chrysanthemum-v24-occlusion'
assert not list(HERE.glob(PREFIX+'*.png')), 'Never overwrite diagnostic evidence'
errors = []
receipts = []
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = browser.new_page(viewport={'width':1800, 'height':800}, device_scale_factor=1)
    page.set_default_timeout(90000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.route('https://**/*', lambda r:r.abort())
    page.route('http://**/*', lambda r:r.abort())
    page.goto((HERE/'diagnostic-occlusion-v24.html').as_uri())
    page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    for stage in ['geometry', 'chrysanthemum']:
        page.locator('#next').click()
        page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=stage)
    for label in ['entry', 'deep']:
        if label == 'deep':
            page.locator('#pause').click()
            page.keyboard.down('w')
            try:
                page.wait_for_function('journeyDiagnostics().position[2]<=-6')
            finally:
                page.keyboard.up('w')
        page.locator('#pause').click()
        page.wait_for_function('!journeyDiagnostics().renderPending && journeyDiagnostics().renderedAnimTime===journeyDiagnostics().animTime')
        d = page.evaluate('journeyDiagnostics()')
        assert d['stage']=='chrysanthemum' and d['paused'] and d['detail']=='high'
        assert not d['missingEvidence'] and d['uncitedMeshes']==0 and not errors, errors
        png=HERE/f'{PREFIX}-{label}.png'
        page.screenshot(path=str(png))
        receipt={'diagnostic_only':True, 'file':png.name, 'capture_sha256':digest(png),
                 'capture_diagnostics':d, 'errors':list(errors),
                 'panel_resolution':[600,400], 'same_ray_projection_per_panel':True,
                 'material_ablation':True, 'max_steps':2048, 'depth_scale':60, 'miss_marker':'magenta in normal/depth panels',
                 'limits':'Current v23 visibility/recess ablation plus normals/depth; UI/postprocess still present; no realism credit',
                 'source_hashes':{name:digest(HERE/name) for name in ['continuum.js','continuum-v23.js','trip-v16.js','render_diagnostic_occlusion_v24.py','build_diagnostic_occlusion_v24.py','index.html','data.js','fidelity-data.js','vendor/three.min.js','diagnostic-occlusion-v24.js','diagnostic-occlusion-v24.html','fractal.js','trip.js']}}
        png.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
        receipts.append(receipt)
        print(json.dumps({'capture':png.name,'position':d['position'],'time':d['animTime'],'errors':errors}),flush=True)
    assert not errors, errors
    browser.close()
(HERE/f'{PREFIX}-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
