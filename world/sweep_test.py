"""Turn the camera all the way round at every stage and catch the frames that break.

Reported from actually using it: parts of the environment turn into black triangles when you
turn. Nothing in the suite could have caught that, because everything captured a single fixed
forward view. A renderer bug that only appears at certain angles is invisible to a test that
only ever looks one way.

HOW IT DECIDES. Counting dark pixels does not work, and it took two wrong versions to see why.
The void is legitimately 97% black and the garden looking up at its night sky is legitimately
9%, while the cathedral bug was 4.9% - so no threshold on "how much" separates a hole from a
dark room, and comparing an angle to its stage's median just flags every scene that is darker
overhead than underfoot.

What distinguishes them is SHAPE and FLATNESS, not amount. Two filters, and both are needed:

  enclosed - a sky, a ceiling and the void all reach the edge of the frame; a hole punched in
             the geometry is surrounded by lit scene on every side.
  flat     - nothing was drawn in a hole, so it is one exact colour. Measured on real frames:
             the cathedral's clipped triangle had a per-channel colour deviation of 1.54,
             while the workshop's black machinery - enclosed, dark, and perfectly correct -
             had 7.12. Shading is what a real object has and a hole does not.

Enclosure alone flagged the workshop, the garden, the void and three more, all of which look
right. No per-stage baseline and no threshold on total darkness are needed.

    python clip_test.py     <- the exact test for the bug this file was written to chase
    python sweep_test.py                  every route stage and branch
    python sweep_test.py --stage cathedral --save
"""
import argparse
import io
import pathlib
import statistics
import sys

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import ARGS, ROUTE, BRANCHES  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

YAWS = 24                 # full turn, every 15 degrees
PITCHES = (-0.55, 0.0, 0.55)
# Both extremes matter: the clipped cathedral triangle only showed at pitch -0.55, looking
# down. A sweep that only looked level would have missed it exactly like everything else did.
DARK = 26                 # 8-bit level at or below which a pixel counts as black
# An enclosed dark blob bigger than this fraction of the frame is a hole. The cathedral's
# clipped triangle was 4.85% of the frame and entirely interior.
# Raised from 0.4% after the garden proved the point: sky seen through gaps in its canopy is
# enclosed, dark and flat, i.e. identical to a clipping hole in every image statistic, and it
# measures 1.6% of frame. The exact test for this bug class is clip_test.py, which asks the
# scene graph instead of guessing from pixels. This stays as a coarse backstop for anything
# large enough to be unmistakable - the real bug was 4.85%.
MIN_HOLE = 0.03
# Max per-channel std inside the blob for it to count as "nothing was drawn here". Measured:
# real hole 1.54, correct dark machinery 7.12.
MAX_HOLE_STD = 3.0
# An angle is bad if its dark fraction is this far above the stage's own median, in absolute
# terms AND as a multiple. Both, so a stage that is 1% dark does not fail for hitting 4%.
# A single clipped triangle covered 4.85% of the screen against a 0.3% median - 16x the
# normal darkness - but an absolute floor of 10 points called that fine, and the first run
# PASSED on a frame with an unmistakable black triangle in the middle of it. The floor exists
# so a stage that is 1% dark does not fail for hitting 3%; it never needed to be 10 points.
EXCESS_ABS = 0.015
EXCESS_RATIO = 3.0


def analyse(png):
    """Total darkness, and the biggest dark region that does NOT reach the frame edge.

    The second number is the one that matters. Sky, ceilings and the void all touch the
    border; a hole punched in the middle of lit geometry does not.
    """
    from scipy import ndimage
    a = np.asarray(Image.open(io.BytesIO(png)).convert('RGB'), dtype=np.uint8)
    dark = a.max(axis=2) <= DARK
    total = float(dark.mean())
    labels, n = ndimage.label(dark)
    if not n:
        return total, 0.0
    edge = set(labels[0, :].tolist()) | set(labels[-1, :].tolist())         | set(labels[:, 0].tolist()) | set(labels[:, -1].tolist())
    sizes = ndimage.sum(dark, labels, range(1, n + 1))
    biggest = 0.0
    for lab, sz in zip(range(1, n + 1), sizes):
        if lab in edge or sz / dark.size < MIN_HOLE:
            continue
        px = a[labels == lab]
        if float(px.std(axis=0).max()) > MAX_HOLE_STD:
            continue        # shaded, so something was drawn there - an object, not a hole
        biggest = max(biggest, sz)
    return total, float(biggest) / dark.size


def sweep(pg, stage, yaws=YAWS, save_dir=None):
    """Every angle at this stage, with the scene paused so a slow frame cannot masquerade as
    a hole in the geometry."""
    rows = []
    for pi, pitch in enumerate(PITCHES):
        for yi in range(yaws):
            yaw = (yi / yaws) * 2 * np.pi
            pg.evaluate("([y,p]) => window.__setView && window.__setView(y,p)", [float(yaw), float(pitch)])
            pg.wait_for_function('!journeyDiagnostics().renderPending', timeout=45000)
            png = pg.screenshot()
            total, hole = analyse(png)
            rows.append({'yaw': round(float(np.degrees(yaw))), 'pitch': pitch,
                         'dark': total, 'hole': hole, 'png': png})
    return rows


def judge(stage, rows):
    med = statistics.median([r['dark'] for r in rows])
    bad = [r for r in rows if r['hole'] >= MIN_HOLE]
    return med, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', action='append')
    ap.add_argument('--save', action='store_true')
    ap.add_argument('--yaws', type=int, default=YAWS,
                    help='angles around; fewer is faster, 8 still caught the known bug')
    a = ap.parse_args()
    # Visit in ROUTE order and take the branches while standing at the cathedral, because the
    # journey only moves forward: asking for a branch after walking past the cathedral leaves
    # #pathsToggle hidden and the click hangs. The first run of this file did exactly that.
    asked = set(a.stage) if a.stage else set(ROUTE + BRANCHES)
    stages = [s for s in ROUTE if s in asked]
    branch_here = [s for s in BRANCHES if s in asked]
    if branch_here and 'cathedral' not in stages:
        stages.insert(0, 'cathedral')   # needed to reach them, swept for free

    failures = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': 1100, 'height': 740}, device_scale_factor=1)
        pg.set_default_timeout(90000)
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)[:140]))
        blocked = lambda t: 'Failed to load resource' in t and 'ERR_FAILED' in t
        pg.on('console', lambda m: errors.append(m.text[:140])
              if m.type == 'error' and not blocked(m.text) else None)
        pg.route('https://**/*', lambda r: r.abort())
        pg.route('http://**/*', lambda r: r.abort())
        pg.goto((HERE / 'index.html').as_uri())
        pg.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        pg.locator('#autoStart').uncheck()
        pg.locator('#begin').click()

        print('%-14s %-8s %s' % ('stage', 'dark', 'largest ENCLOSED dark region (a hole)'))
        queue = []
        for st in stages:
            queue.append(st)
            if st == 'cathedral':
                queue.extend(branch_here)
        for stage in queue:
            target = 'cathedral' if stage in BRANCHES else stage
            here = pg.evaluate('journeyDiagnostics().stage')
            if here != target:
                order = ROUTE[ROUTE.index(here) + 1:ROUTE.index(target) + 1] if here in ROUTE else []
                for n in order:
                    pg.locator('#next').click()
                    pg.wait_for_function(
                        "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=n)
            if stage in BRANCHES:
                pg.locator('#pathsToggle').click()
                pg.locator('[data-branch="%s"]' % stage).click()
                pg.wait_for_function(
                    "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=stage)

            pg.locator('#pause').click()
            rows = sweep(pg, stage, a.yaws)
            pg.locator('#pause').click()

            med, bad = judge(stage, rows)
            worst = sorted(rows, key=lambda r: -r['hole'])[:3]
            print('%-14s %6.1f%%  %s' % (
                stage, med * 100,
                '  '.join('yaw %3d pitch %+.2f hole %4.2f%%' % (r['yaw'], r['pitch'], r['hole'] * 100)
                          for r in worst)))
            if bad:
                failures.append((stage, med, bad))
                if a.save:
                    for r in bad[:4]:
                        (HERE / ('sweep-%s-y%03d-p%+.2f.png' % (stage, r['yaw'], r['pitch']))
                         ).write_bytes(r['png'])
            if stage in BRANCHES:
                pg.locator('#next').click()
                pg.wait_for_function("()=>!journeyDiagnostics().transition")
        b.close()

    print('')
    if failures:
        for stage, med, bad in failures:
            print('%s: %d of %d angles have a hole in the geometry (dark region enclosed by scene)'
                  % (stage, len(bad), a.yaws * len(PITCHES)))
            for r in bad[:6]:
                print('    yaw %3d  pitch %+.2f  enclosed dark blob = %.2f%% of frame'
                      % (r['yaw'], r['pitch'], r['hole'] * 100))
    print('%s' % ('FAIL - the geometry has holes at some camera angles' if failures
                  else 'PASS - no enclosed hole at any angle of any stage'))
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
