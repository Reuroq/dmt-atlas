"""Foreground, headless browser verification. No server or GUI required."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
errors = []
results = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files'])
    page = browser.new_page(viewport={'width': 1440, 'height': 960}, device_scale_factor=1)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto((HERE / 'index.html').as_uri(), wait_until='load')
    page.wait_for_function('window.worldDiagnostics && worldDiagnostics().renderReady')
    page.wait_for_timeout(900)
    page.screenshot(path=str(HERE / 'latest.png'))
    page.screenshot(path=str(HERE / 'entrance.png'))
    results['initial'] = page.evaluate('worldDiagnostics()')
    assert results['initial']['nodes'] == 172
    assert not results['initial']['missingExhibits'], results['initial']['missingExhibits']
    page.locator('#enterButton').click()
    page.keyboard.down('w')
    page.wait_for_timeout(700)
    page.keyboard.up('w')
    results['walk'] = page.evaluate('worldDiagnostics()')
    assert results['walk']['position'][2] < 18, results['walk']
    page.mouse.move(900, 420)
    page.mouse.down()
    page.mouse.move(1040, 460, steps=6)
    page.mouse.up()
    assert abs(page.evaluate('worldDiagnostics().yaw')) > .1
    page.keyboard.press('h')
    page.locator('#roomEvidence').click()
    assert page.locator('#panelContent h2').inner_text() == 'The Domed Cathedral'
    assert page.locator('#panelContent details.source').count() > 0
    results['cathedral_reports'] = page.locator('#reportList .report-link').count()
    page.locator('#closePanel').click()
    # Clicking an actual 3D exhibit must resolve a cited dossier, not only the UI links.
    page.locator('.room-button[data-index="1"]').click()
    page.wait_for_function('worldDiagnostics().renderReady')
    page.mouse.click(155, 535)
    assert page.locator('#panel').is_visible(), '3D exhibit picking failed'
    assert page.locator('#panelContent h2').inner_text() == 'Fractal lattices & jeweled tilings'
    assert page.locator('#panelContent details.source').count() > 0
    page.locator('#closePanel').click()
    results['rooms'] = []
    for i in range(8):
        page.locator(f'.room-button[data-index="{i}"]').click()
        page.wait_for_function('worldDiagnostics().renderReady')
        result = page.evaluate('worldDiagnostics()')
        assert result['pickables'] >= 8
        results['rooms'].append(result)
        if i in [2, 3, 5, 7]:
            page.screenshot(path=str(HERE / f'{result["room"]}.png'))
    page.locator('#atlasButton').click()
    assert page.locator('.index-item').count() == 172
    page.locator('#search').fill('machine elves')
    assert page.locator('.index-item').count() >= 1
    page.get_by_role('button', name='Self-transforming machine elves', exact=False).click()
    assert page.locator('#panelContent h2').inner_text() == 'Self-transforming machine elves'
    assert page.locator('#panelContent .art-link').count() > 0
    page.screenshot(path=str(HERE / 'evidence.png'))
    page.locator('#closePanel').click()
    page.locator('#methodButton').click()
    assert '6,025' in page.locator('#panelContent').inner_text()
    page.keyboard.press('Escape')
    assert page.locator('#panel').is_hidden()
    page.locator('#motionButton').click()
    assert page.evaluate('worldDiagnostics().reduced')
    page.locator('#tourButton').click()
    for i in range(8):
        assert page.locator('#tourLabel').inner_text() == f'CURATED ROUTE {i+1} / 8'
        page.locator('#tourNext').click()
    assert page.locator('#panel').is_visible()
    assert page.locator('#tourBar').is_hidden()
    page.locator('#closePanel').click()
    # Deep links resolve on direct file open, without an HTTP service.
    page.goto((HERE / 'index.html').as_uri() + '#space=garden')
    page.wait_for_function('window.worldDiagnostics && worldDiagnostics().room === "garden"')
    assert page.evaluate('worldDiagnostics().entered')
    mobile = browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,reduced_motion='reduce')
    mobile.on('pageerror', lambda e: errors.append(str(e)))
    mobile.goto((HERE / 'index.html').as_uri(),wait_until='load')
    mobile.wait_for_function('window.worldDiagnostics && worldDiagnostics().renderReady')
    mobile.screenshot(path=str(HERE / 'mobile.png'))
    mobile.locator('#enterButton').tap()
    assert mobile.locator('#touchControls').is_visible()
    assert mobile.evaluate('worldDiagnostics().reduced')
    assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
    mobile.locator('#atlasButton').tap()
    mobile.locator('#search').fill('void')
    assert mobile.locator('.index-item').count() >= 1
    mobile.locator('#closePanel').tap()
    mobile.close()
    # Rendering failure degrades to the full textual index with usable search.
    fallback = browser.new_page(viewport={'width':1000,'height':800})
    fallback.route('**/three.min.js', lambda route: route.fulfill(status=200,content_type='application/javascript',body=''))
    fallback.goto((HERE / 'index.html').as_uri(),wait_until='load')
    fallback.locator('#enterButton').click()
    assert fallback.locator('.index-item').count() == 172
    fallback.locator('#search').fill('Hyperspace')
    assert fallback.locator('.index-item').count() > 0
    fallback.close()
    browser.close()
results['errors'] = errors
(HERE / 'verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps({'errors': errors, 'rooms': [{k:r[k] for k in ['room','drawCalls','triangles','geometries']} for r in results['rooms']], 'checks':'desktop, mobile, movement, drag look, evidence, search, tour, reduced motion, deep links'},indent=2))
assert not errors, errors
