"""Reduced-idle rendering must not stop the real paced route clock."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, open_page, diag, stage, results
from fidelity import render_signature

path = Path(__file__).resolve().parent / 'verification-idle-pace-v16.json'
assert not path.exists(), 'Preserve prior check'
out = {'render_signature': render_signature(), 'passed': False}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = open_page(browser, viewport={'width': 760, 'height': 700}, reduced_motion='reduce')
    try:
        if diag(page)['detail'] != 'low':
            page.locator('#detail').click()
        page.locator('#autoStart').check()
        page.locator('#begin').click()
        page.wait_for_function('!journeyDiagnostics().renderPending')
        before = diag(page)
        page.wait_for_timeout(1500)
        during = diag(page)
        out.update(before=before, during=during)
        assert during['paced'] and during['reduced'] and during['elapsed'] > before['elapsed']
        assert during['frames'] == before['frames'] and during['position'] == before['position']
        page.set_default_timeout(30000)
        stage(page, 'geometry')
        page.wait_for_function('journeyDiagnostics().renderReady && !journeyDiagnostics().renderPending')
        after = diag(page)
        out['after'] = after
        assert after['animTime'] == before['animTime'] and after['frames'] > before['frames']
        assert not results['errors'], results['errors']
        out['passed'] = True
    except Exception as exc:
        out.update(failure=str(exc), diagnostics=diag(page))
        raise
    finally:
        path.write_text(json.dumps(out, indent=2) + '\n')
        browser.close()
print('PASS: reduced idle keeps elapsed time and automatically transitions onset to geometry')
