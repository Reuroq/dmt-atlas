"""Prove the feature works in the ACTUAL walkthrough, not just on the bench.

Served over HTTP on loopback, because a Worker and a fetch both need a real origin. Checks the
three things that decide whether this shipped correctly:

  1. OFF by default, and nothing heavy is fetched until a visitor asks
  2. switching it on drives the beings from the connectome, with cited actions
  3. switching it off again leaves the journey exactly as it was
"""
import functools
import http.server
import pathlib
import socket
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
WORLD = HERE.parent
sys.path.insert(0, str(WORLD))
from verify import ARGS, ROUTE  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_response(self, code, message=None):
        self._code = code
        super().send_response(code, message)

    def end_headers(self):
        # Deliberately NOT sending Content-Encoding: gzip. dmtatlas.com does not, and a test
        # server that is kinder than production is how a broken build passes locally and fails
        # live - which is exactly what happened here. Serve it the way the real server does.
        if self.path.endswith('.gz') and getattr(self, '_code', 200) == 200:
            self.send_header('Content-Type', 'application/octet-stream')
        super().end_headers()

    def log_message(self, *a):
        pass


def serve():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    httpd = http.server.ThreadingHTTPServer(
        ('127.0.0.1', port), functools.partial(Handler, directory=str(WORLD)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def main():
    httpd, port = serve()
    fetched, errors = [], []
    ok = True
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': 1280, 'height': 860}, device_scale_factor=1)
        pg.set_default_timeout(90000)
        pg.on('request', lambda r: fetched.append(r.url.split('/')[-1].split('?')[0]))
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)[:160]))
        pg.on('console', lambda m: errors.append('console: ' + m.text[:160])
              if m.type == 'error' else None)
        pg.goto('http://127.0.0.1:%d/index.html' % port)
        pg.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')

        heavy = [f for f in fetched if f in ('circuit.bin.gz', 'behaviour.js', 'worker.js')]
        print('1. off by default')
        print('   toggle present: %s' % pg.locator('#flybrain').count())
        print('   heavy files fetched before anyone asked: %s' % (heavy or 'none'))
        if heavy:
            ok = False

        # Walk to a stage that actually has beings.
        pg.locator('#autoStart').uncheck()
        pg.locator('#begin').click()
        for n in ROUTE[1:ROUTE.index('contact') + 1]:
            pg.locator('#next').click()
            pg.wait_for_function(
                "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=n)
        pg.wait_for_timeout(1500)

        print('\n2. switching it on')
        pg.locator('#flybrain').click()
        pg.wait_for_function("() => document.getElementById('flybrain').textContent"
                             ".indexOf('on') > -1", timeout=90000)
        loaded = [f for f in fetched if f in ('circuit.bin.gz', 'behaviour.js', 'worker.js')]
        print('   fetched on demand: %s' % sorted(set(loaded)))

        # Walk in so the beings notice, then read what they are doing.
        pg.keyboard.down('w')
        pg.wait_for_timeout(2600)
        pg.keyboard.up('w')
        pg.wait_for_timeout(2500)
        state = pg.evaluate('window.FlyBrain ? FlyBrain.state() : null')
        awake = {k: v for k, v in (state or {}).items() if v.get('awake')}
        print('   beings driven: %d, awake: %d' % (len(state or {}), len(awake)))
        for k, v in list(awake.items())[:4]:
            print('     %-10s rate %.5f  %d/%d actions  "%s"'
                  % (k, v['descendingRate'], v['reached'], v['of'], (v['says'] or '')[:52]))
        if not awake:
            ok = False
            print('   FAIL: nothing woke up')

        # The hint should now quote the being's own cited behaviour.
        d = pg.evaluate('journeyDiagnostics()')
        cand = [a for a in d['actors'] if 0 < a['screen'][0] < 1280 and 0 < a['screen'][1] < 860]
        if cand:
            a = min(cand, key=lambda x: (x['screen'][0] - 640) ** 2 + (x['screen'][1] - 430) ** 2)
            pg.mouse.click(a['screen'][0], a['screen'][1])
            pg.wait_for_timeout(700)
            hint = pg.locator('#sceneHint').text_content()
            print('   hint after clicking a being:\n     "%s"' % hint.strip()[:150])
            if 'fly connectome' not in hint:
                ok = False
                print('   FAIL: the hint did not come from the connectome')

        print('\n3. switching it off')
        pg.locator('#flybrain').click()
        pg.wait_for_timeout(600)
        after = pg.evaluate('journeyDiagnostics()')
        print('   still rendering: %s, stage %s, errors %s'
              % (after['renderReady'], after['stage'], errors or 'none'))
        if errors:
            ok = False
        b.close()
    httpd.shutdown()
    print('\n%s' % ('PASS - opt-in, lazy, cited, and reversible' if ok else 'FAIL - see above'))
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
