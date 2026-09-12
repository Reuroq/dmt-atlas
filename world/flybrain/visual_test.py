"""Do the beings actually LOOK different as they climb their ladder?

Every test written for this module so far checked state: descending rate, which rung, how many
cited actions were reached. All of them passed while the beings stood perfectly still on the
live site, because none of them ever looked at a pixel. Reported behaviour is not behaviour.

This walks a traveller in, captures the being's own screen region at each rung it reaches, and
measures how much of that region actually changed. A being whose pixels do not move has not
performed anything, whatever the caption says.

    python visual_test.py              the four depicted beings
    python visual_test.py --save       also write the crops for a human to look at
"""
import argparse
import functools
import http.server
import pathlib
import socket
import sys
import threading

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
WORLD = HERE.parent
sys.path.insert(0, str(WORLD))
from verify import ARGS, ROUTE  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

# A being's patch must change MORE than an empty patch of the same scene does. Without that
# control the test is worthless: the room's shaders animate continuously, so between two
# captures seconds apart ~90% of ANY region changes, and a statue scores the same as a dancer.
# Two earlier versions of this file passed for exactly that reason - first because the camera
# had moved, then because the background had.
# The pixel-ratio test could never pass and it took a third rewrite to see why: the room's
# shaders change ~96% of ANY patch over seven seconds, so a being region can at most reach
# 100% and no multiple of the control is achievable. A saturated control is not a control.
#
# "Did the being move?" is a question about the transforms the renderer draws from, so ask
# those. Pixels are still captured with --save so a human can look, but the verdict comes from
# geometry, which is what actually determines what gets drawn.
MIN_POSE_DELTA = {
    'x': 0.05, 'z': 0.05,      # metres of ground travel
    'y': 0.05,                 # body ride height
    'leanX': 0.05, 'arm': 0.08, 'spread': 0.05,   # radians
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_response(self, code, message=None):
        self._code = code
        super().send_response(code, message)

    def end_headers(self):
        # Exactly what production sends - no Content-Encoding. A kinder test server is how
        # this feature shipped broken once already.
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


def control_crop(img, actors, w, h, pad=110):
    """A patch of the same frame with no being in it, to measure what the ROOM alone does."""
    import random
    rng = random.Random(7)
    for _ in range(400):
        cx = rng.randint(pad, w - pad)
        cy = rng.randint(pad, h - int(pad * 1.4))
        if all((cx - a['screen'][0]) ** 2 + (cy - a['screen'][1]) ** 2 > (pad * 2.2) ** 2
               for a in actors):
            return img.crop((cx - pad, cy - pad, cx + pad, cy + int(pad * 1.4)))
    return None


def crop_for(img, actor, w, h, pad=110):
    """The being's own patch of screen, not the whole frame - a whole-frame diff is dominated
    by the animated room and would call a statue alive."""
    x, y = actor['screen']
    x0, x1 = max(0, int(x - pad)), min(w, int(x + pad))
    y0, y1 = max(0, int(y - pad)), min(h, int(y + pad * 1.4))
    if x1 - x0 < 30 or y1 - y0 < 30:
        return None
    return img.crop((x0, y0, x1, y1))


def diff(a, b):
    if a is None or b is None or a.size != b.size:
        return 0.0, 0.0
    x = np.asarray(a.convert('RGB'), dtype=np.int16)
    y = np.asarray(b.convert('RGB'), dtype=np.int16)
    d = np.abs(x - y).max(axis=2)
    return float((d > 18).mean()), float(d.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--save', action='store_true')
    ap.add_argument('--stage', default='contact')
    a = ap.parse_args()

    httpd, port = serve()
    shots = {}
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': 1280, 'height': 860}, device_scale_factor=1)
        pg.set_default_timeout(120000)
        pg.on('pageerror', lambda e: errors.append(str(e)[:140]))
        pg.goto('http://127.0.0.1:%d/index.html' % port)
        pg.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        pg.locator('#autoStart').uncheck()
        pg.locator('#begin').click()
        for n in ROUTE[1:ROUTE.index(a.stage) + 1]:
            pg.locator('#next').click()
            pg.wait_for_function(
                "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=n)
        pg.wait_for_timeout(1200)
        pg.locator('#flybrain').click()
        pg.wait_for_function("() => document.getElementById('flybrain').textContent"
                             ".indexOf('on') > -1", timeout=120000)

        # Freeze the scene clock at each sample so the ONLY thing that can differ between two
        # captures is the being's pose, not the room breathing behind it.
        def capture(tag):
            pg.locator('#pause').click()
            pg.wait_for_function('!journeyDiagnostics().renderPending', timeout=60000)
            raw = pg.screenshot()
            pg.locator('#pause').click()
            d = pg.evaluate('journeyDiagnostics()')
            st = pg.evaluate('FlyBrain.state()')
            import io as _io
            shots[tag] = (Image.open(_io.BytesIO(raw)), d['actors'], st)

        # CRITICAL: do not walk between the two captures. The first version of this test did,
        # and 94% of the pixels changed because the being got nearer and bigger - it measured
        # the camera, not the being, and passed while they stood still. The camera is held
        # perfectly still and the ladder is climbed by injecting drive directly, so the only
        # thing that can differ between the two frames is the pose.
        capture('far')
        pg.evaluate("""() => {
          window.__holdIds = Object.keys(FlyBrain.state());
          window.__hold = setInterval(() => {
            const d = {};
            (window.__holdIds || []).forEach(k => { d[k] = 0.5; });
            FlyBrain.tick(d, 24);
          }, 16);
        }""")
        pg.wait_for_timeout(7000)
        pg.evaluate('clearInterval(window.__hold)')
        pg.wait_for_timeout(400)
        capture('near')
        b.close()
    httpd.shutdown()

    (far_img, far_actors, far_state) = shots['far']
    (near_img, near_actors, near_state) = shots['near']
    w, h = far_img.size

    # Same camera for both frames, so any difference is the being itself.
    assert far_actors and near_actors
    print('camera held still: %s -> %s' % (
        [round(v, 2) for v in shots['far'][1][0]['screen']],
        [round(v, 2) for v in shots['near'][1][0]['screen']]))
    ctrl_frac, ctrl_mean = diff(control_crop(far_img, far_actors, w, h),
                                control_crop(near_img, near_actors, w, h))
    print('control patch with no being in it: %.1f%% of pixels changed - the room alone.' % (ctrl_frac * 100))
    print('That is why the verdict below is geometry, not pixels.')
    print('')
    print('%-11s %-9s %-9s %-9s %s'
          % ('being', 'rung low', 'rung high', 'pixels', 'verdict (from the drawn transforms)'))
    ok = True
    any_checked = False
    for i, fa in enumerate(far_actors):
        if i >= len(near_actors):
            continue
        key = fa['kind'] + '#' + str(i)
        fs, ns = far_state.get(key), near_state.get(key)
        if not fs or not ns:
            continue
        c_far = crop_for(far_img, fa, w, h)
        c_near = crop_for(near_img, near_actors[i], w, h)
        frac, _ = diff(c_far, c_near)
        any_checked = True
        pf, pn = fa.get('pose') or {}, (near_actors[i].get('pose') or {})
        deltas = {k: abs(pn.get(k, 0) - pf.get(k, 0)) for k in MIN_POSE_DELTA}
        moved_on = [k for k, v in deltas.items() if v >= MIN_POSE_DELTA[k]]
        moved = len(moved_on) >= 2
        ok &= moved
        detail = ' '.join('%s%+.2f' % (k, pn.get(k, 0) - pf.get(k, 0))
                          for k in ('x', 'z', 'y', 'leanX', 'arm', 'spread'))
        print('%-11s %-9s %-9s %6.1f%%   %s'
              % (key, fs['rung'], ns['rung'], frac * 100,
                 ('moved on ' + ','.join(moved_on)) if moved else 'STOOD STILL'))
        print('            %s' % detail)
        if a.save and c_far and c_near:
            c_far.save(HERE / ('pose-%s-far.png' % key.replace('#', '')))
            c_near.save(HERE / ('pose-%s-near.png' % key.replace('#', '')))

    if not any_checked:
        ok = False
        print('no beings were compared - the capture found none on screen')
    if errors:
        ok = False
        print('page errors: %s' % errors[:3])
    print('\n%s' % ('PASS - every being visibly changed as it climbed its ladder'
                    if ok else 'FAIL - a being whose pixels do not move has not performed anything'))
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
