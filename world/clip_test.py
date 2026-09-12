"""Does any geometry cross the camera's clip planes? Asked of the scene, not of the pixels.

The reported bug was black triangles appearing as you turn. The cause was geometric: the
raymarched enclosures are boxes up to 240 units drawn from the inside, so their far corners sat
220 units from a camera with a 180-unit far plane. The GPU clips the triangle partway through
and you see the clear colour through the cut.

I tried to catch it from screenshots five times and every version was wrong, because a hole in
the geometry and a legitimate dark background are the same pixels:

  v1  walked the camera between captures      -> measured my own movement
  v2  held the camera, compared frames        -> measured the animated room
  v3  compared each angle to its stage median -> flagged night skies and dark ceilings
  v4  required the dark region to be enclosed -> flagged the workshop's black machinery
  v5  also required it to be flat             -> flagged sky seen through gaps in foliage

The garden's canopy gaps are enclosed, dark and perfectly flat. They are indistinguishable
from a clipping hole in every image statistic, because in both cases you are looking at
background through an opening. So stop guessing from pixels: the failure is that geometry
crosses a clip plane, which the scene can be asked directly.

Exact, instant, and no false positives - it reports the same quantity the GPU uses to decide.

    python clip_test.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import ARGS, ROUTE, BRANCHES  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

# Ask in the page, where the scene graph and the camera actually live.
PROBE = """() => {
  const cam = window.__camera, scene = window.__scene, T = window.THREE;
  if (!cam || !scene) return {error: 'scene not exposed'};
  cam.updateMatrixWorld();
  const out = [];
  scene.traverse(o => {
    if (!(o.isMesh || o.isPoints || o.isLine) || !o.geometry) return;
    if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
    const bs = o.geometry.boundingSphere;
    if (!bs) return;
    const c = bs.center.clone().applyMatrix4(o.matrixWorld);
    // Radius has to be scaled the way the object is, or a scaled mesh reports a sphere that
    // does not contain it.
    const s = new T.Vector3();
    o.matrixWorld.decompose(new T.Vector3(), new T.Quaternion(), s);
    const r = bs.radius * Math.max(Math.abs(s.x), Math.abs(s.y), Math.abs(s.z));
    const d = c.distanceTo(cam.position);
    out.push({name: o.name || o.type, far: d + r, near: d - r, radius: r});
  });
  return {far: cam.far, near: cam.near, objects: out};
}"""


def main():
    failures = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': 1000, 'height': 700}, device_scale_factor=1)
        pg.set_default_timeout(90000)
        pg.route('https://**/*', lambda r: r.abort())
        pg.route('http://**/*', lambda r: r.abort())
        pg.goto((HERE / 'index.html').as_uri())
        pg.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
        pg.locator('#autoStart').uncheck()
        pg.locator('#begin').click()

        print('%-14s %-7s %-9s %s' % ('stage', 'far', 'worst reach', 'verdict'))
        order = []
        for st in ROUTE:
            order.append(st)
            if st == 'cathedral':
                order.extend(BRANCHES)
        for stage in order:
            target = 'cathedral' if stage in BRANCHES else stage
            here = pg.evaluate('journeyDiagnostics().stage')
            if here in ROUTE and here != target:
                for n in ROUTE[ROUTE.index(here) + 1:ROUTE.index(target) + 1]:
                    pg.locator('#next').click()
                    pg.wait_for_function(
                        "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=n)
            if stage in BRANCHES:
                pg.locator('#pathsToggle').click()
                pg.locator('[data-branch="%s"]' % stage).click()
                pg.wait_for_function(
                    "(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition", arg=stage)

            r = pg.evaluate(PROBE)
            if r.get('error'):
                print('cannot probe the scene: %s' % r['error'])
                raise SystemExit(2)
            over = [o for o in r['objects'] if o['far'] > r['far']]
            worst = max((o['far'] for o in r['objects']), default=0)
            print('%-14s %-7.0f %-9.1f %s' % (
                stage, r['far'], worst,
                'ok' if not over else 'CLIPPED: %d object(s) reach past the far plane' % len(over)))
            if over:
                failures.append((stage, r['far'], sorted(over, key=lambda o: -o['far'])[:3]))
            if stage in BRANCHES:
                pg.locator('#next').click()
                pg.wait_for_function("()=>!journeyDiagnostics().transition")
        b.close()

    print('')
    for stage, far, objs in failures:
        print('%s: far plane %.0f, but geometry reaches:' % (stage, far))
        for o in objs:
            print('    %-28s out to %.1f  (radius %.1f)' % (o['name'][:28], o['far'], o['radius']))
    print('%s' % ('FAIL - geometry crosses the far plane; it will be cut mid-triangle'
                  if failures else 'PASS - all geometry fits inside the camera clip planes'))
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
