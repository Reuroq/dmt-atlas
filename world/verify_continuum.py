"""Focused real-control regression for the new volume; not full route acceptance."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS, open_page, diag, stage, next_stage, hold_until, results
from fidelity import render_signature

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--walk-timeout-ms', type=int, default=45000,
                    help='Wall-clock allowance for the real exit walk; increase only for slow software rendering')
args = parser.parse_args()
assert args.walk_timeout_ms > 0
out = {'render_signature': render_signature(), 'checks': [], 'passed': False,
       'exit_walk_timeout_ms': args.walk_timeout_ms}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = open_page(browser, viewport={'width': 1000, 'height': 700})
    page.set_default_timeout(90000)
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    next_stage(page, 'geometry')
    next_stage(page, 'chrysanthemum')
    assert diag(page)['detail'] == 'high'
    hold_until(page, 'd', 'journeyDiagnostics().position[0] >= 3.9', timeout=15000)
    page.keyboard.down('d')
    page.wait_for_timeout(500)
    page.keyboard.up('d')
    assert 3.9 <= diag(page)['position'][0] <= 4
    out['checks'].append('HIGH right walking boundary preserved inside minimum volume radius')
    hold_until(page, 'a', 'journeyDiagnostics().position[0] <= 0', timeout=15000)
    # Key release may arrive one capped movement frame after crossing centre.
    # This is a walking check, not a high-frame-rate assumption; restart below resets pose.
    assert -3.2 <= diag(page)['position'][0] <= 0
    before = diag(page)
    page.mouse.move(500, 300)
    page.mouse.down()
    page.mouse.move(620, 340, steps=5)
    page.mouse.up()
    after = diag(page)
    assert after['yaw'] != before['yaw'] and after['pitch'] != before['pitch']
    out['checks'].append('Actual drag-look changes both camera axes')
    # Restart through real controls to restore a straight walking direction.
    page.locator('#restart').click()
    stage(page, 'onset')
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    next_stage(page, 'geometry')
    next_stage(page, 'chrysanthemum')
    assert not diag(page)['paced']
    hold_until(page, 'w', 'journeyDiagnostics().transition', timeout=args.walk_timeout_ms)
    destination = stage(page, 'rush')
    assert destination['stage'] == 'rush' and not destination['missingEvidence'] and destination['uncitedMeshes'] == 0
    out['checks'].append('Central physical exit reaches Rush with cited geometry; no navigation injection')
    out['errors'] = results['errors']
    out['passed'] = not out['errors']
    browser.close()
(HERE / 'verification-continuum.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
assert out['passed'], out
print(json.dumps(out), flush=True)
