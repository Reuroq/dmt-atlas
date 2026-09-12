"""Drive the fly-brain bench headlessly, over HTTP, the way the live site serves it.

Not file:// - a Worker and a fetch both need a real origin, and testing the feature under a
scheme it will never run on would prove nothing. This serves world/ on a loopback port,
walks a traveller in, and checks the chain end to end.
"""
import http.server
import json
import functools
import pathlib
import socket
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
WORLD = HERE.parent
sys.path.insert(0, str(WORLD))
from verify import ARGS  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_response(self, code, message=None):
        self._code = code
        super().send_response(code, message)

    def end_headers(self):
        # The circuit ships pre-gzipped; without this header the browser hands the worker
        # compressed bytes and the parse fails on a bad magic number. Only on a real hit:
        # labelling a 404's HTML body as gzip produces ERR_CONTENT_DECODING_FAILED, which
        # hides the actual 404 behind a decoding error.
        if self.path.endswith('.gz') and getattr(self, '_code', 200) == 200:
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Type', 'application/octet-stream')
        super().end_headers()

    def log_message(self, *a):
        pass


def serve():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    handler = functools.partial(Handler, directory=str(WORLD))
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def main():
    httpd, port = serve()
    url = 'http://127.0.0.1:%d/flybrain/bench.html' % port
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': 1100, 'height': 700})
        pg.set_default_timeout(60000)
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errors.append('console: ' + m.text) if m.type == 'error' else None)
        pg.goto(url)
        pg.wait_for_function('window.benchState && benchState().loaded', timeout=60000)
        info = pg.evaluate('benchState().info')
        print('circuit loaded in the browser: %s neurons, %s connections (%s visual in, %s '
              'descending out)' % (info['neurons'], info['connections'], info['visual'],
                                   info['descending']))

        # Walk all the way in and hold, so every ladder gets the chance to finish.
        pg.wait_for_function('benchState().distance <= 1.3', timeout=60000)
        pg.wait_for_timeout(4000)
        state = pg.evaluate('benchState()')
        b.close()
    httpd.shutdown()

    print('\n%-9s %-11s %-9s %s' % ('being', 'descending', 'actions', 'currently doing (cited)'))
    ok = True
    for key, s in sorted(state['beings'].items()):
        done = '%d/%d' % (s['reached'], s['of'])
        if s['reached'] < s['of']:
            ok = False
        print('%-9s %-11.5f %-9s "%s"' % (key, s['descendingRate'], done, (s['says'] or '')[:58]))
    if errors:
        ok = False
        print('\nPAGE ERRORS: %s' % errors[:4])
    print('\n%s' % ('PASS - the connectome drove every being through all of its cited actions'
                    if ok else 'FAIL - see above'))
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
