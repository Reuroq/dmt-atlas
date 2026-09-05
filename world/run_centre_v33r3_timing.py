"""One changed entry diagnostic at original HIGH/1200x800/90s. No capture retry."""
import ast
import hashlib
import json
import time
from collections import Counter, deque
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify import ARGS

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r3-timing'
OUT = HERE / (PREFIX + '-receipts.json')
assert not OUT.exists(), 'Preserve one-shot evidence'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

gate = json.loads((HERE / (PREFIX + '-build.json')).read_text())
for group in ['files', 'protected']:
    for name, expected in gate[group].items():
        assert digest(name) == expected, name
assert digest('centre-v33r3-capture-integrity.json') == gate['parent_gate']
ast.parse(Path(__file__).read_text())
stream = deque(maxlen=4096)
counts = Counter()
errors = []
summary = {'diagnostic_only': True, 'settle_passed': False, 'resolution': [1200, 800],
    'detail': 'high', 'settle_timeout_ms': 90000, 'native_controls': True,
    'new_images': 0, 'errors': errors, 'checkpoints': [],
    'build_sha256': digest(PREFIX + '-build.json'), 'runner_sha256': digest(Path(__file__).name),
    'protected_before': gate['protected'],
    'limits': 'Perturbative timestamp/console instrumentation. Submission wall time is not GPU execution time. A pending fence can include driver/queue/polling latency. No hardware-GPU, visual, temporal or full-acceptance claim.'}
operation, operation_start = 'initialization', time.monotonic()
host_start = operation_start

def save():
    summary['stream'] = list(stream)
    summary['stream_counts'] = dict(counts)
    summary['stream_dropped'] = max(0, sum(counts.values()) - len(stream))
    OUT.write_text(json.dumps(summary, indent=2) + '\n')

def mark(name):
    global operation, operation_start
    operation, operation_start = name, time.monotonic()
    summary['current_operation'] = name
    save()
    print(name, flush=True)

def console(message):
    if message.type == 'error':
        errors.append(message.text)
    elif message.text.startswith('DMT_TIMING '):
        event = json.loads(message.text[len('DMT_TIMING '):])
        counts[event['event']] += 1
        stream.append({'host_received_seconds': time.monotonic() - host_start, **event})

def checkpoint(page, label):
    d = page.evaluate('journeyDiagnostics(true)')
    summary['checkpoints'].append({'label': label, 'host_seconds': time.monotonic() - host_start, 'diagnostics': d})
    save()
    return d

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=ARGS)
        page = browser.new_page(viewport={'width': 1200, 'height': 800}, device_scale_factor=1)
        page.set_default_timeout(90000)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', console)
        page.route('https://**/*', lambda r: r.abort())
        page.route('http://**/*', lambda r: r.abort())
        try:
            mark('launch and real navigation')
            page.goto((HERE / (PREFIX + '.html')).as_uri())
            page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
            page.locator('#autoStart').uncheck()
            page.locator('#begin').click()
            for stage in ['geometry', 'chrysanthemum']:
                page.locator('#next').click()
                page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=stage)
            page.locator('#pause').click()
            d = checkpoint(page, 'paused entry before settle')
            assert d['stage'] == 'chrysanthemum' and d['paused'] and d['detail'] == 'high'
            assert d['position'] == [0, 1.7, 8] and d['yaw'] == d['pitch'] == 0
            assert not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes'] == 0
            summary['canvas'] = page.locator('#world').evaluate('(e)=>({width:e.width,height:e.height})')
            assert summary['canvas'] == {'width': 1200, 'height': 800}
            mark('entry settle')
            page.wait_for_function('!journeyDiagnostics().renderPending && journeyDiagnostics().renderedAnimTime===journeyDiagnostics().animTime')
            summary['settle_seconds'] = time.monotonic() - operation_start
            checkpoint(page, 'settled entry')
            assert not errors
            summary['settle_passed'] = True
        except Exception as exc:
            summary['failure'] = {'operation': operation,
                'operation_wall_seconds': time.monotonic() - operation_start, 'exception': repr(exc)}
            save()  # Stream survives even if the subsequent browser export fails.
            try:
                summary['failure']['diagnostics'] = checkpoint(page, 'failure export')
            except Exception as export_error:
                summary['failure']['export_error'] = repr(export_error)
            save()
            raise
        finally:
            browser.close()
finally:
    summary['protected_after'] = {n: digest(n) for n in gate['protected']}
    summary['protected_unchanged'] = summary['protected_after'] == gate['protected']
    summary['source_unchanged'] = all(digest(n) == h for n, h in gate['files'].items())
    save()
    print(json.dumps({'settle_passed': summary['settle_passed'],
        'protected_unchanged': summary['protected_unchanged'], 'source_unchanged': summary['source_unchanged'],
        'stream_records': len(stream), 'errors': errors}), flush=True)
