"""The closed loop: spec -> validate -> render -> measure -> verdict. No human in the middle.

A model runs this, reads the verdict, edits the JSON, runs it again. It never has to look at
the picture, because the picture is reported as numbers and compared against the ranges the
spec itself declared in `expect`.

    python build_room.py library
    python build_room.py --all
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
WORLD = HERE.parent
sys.path.insert(0, str(WORLD))
sys.path.insert(0, str(HERE))
from validate import primitives, atlas_keys, check  # noqa: E402
from verify import ARGS  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

MEASURE = pathlib.Path(r'C:\Users\dwayn\testing1\Polymarket\single_deepseek\dmt_measure.py')


def render(room, width=1200, height=800, settle=3.0):
    """One settled frame from the bench, plus the scene's own account of itself."""
    errors = []
    shot = HERE / ('preview-%s.png' % room)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=ARGS)
        pg = b.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
        pg.set_default_timeout(60000)
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        blocked = lambda t: 'Failed to load resource' in t and 'ERR_FAILED' in t
        pg.on('console', lambda m: errors.append('console: ' + m.text)
              if m.type == 'error' and not blocked(m.text) else None)
        pg.route('https://**/*', lambda r: r.abort())
        pg.route('http://**/*', lambda r: r.abort())
        pg.goto((HERE / 'preview.html').as_uri() + '?room=' + room)
        pg.wait_for_function('window.roomDiagnostics')
        pg.wait_for_timeout(int(settle * 1000))
        diag = pg.evaluate('roomDiagnostics()')
        pg.screenshot(path=str(shot))
        b.close()
    return diag, shot, errors


def measure(shot):
    if not MEASURE.exists():
        return None, 'dmt_measure.py not found at %s' % MEASURE
    out = subprocess.run([sys.executable, str(MEASURE), str(shot), '--json',
                          str(shot.with_suffix('.measure.json'))],
                         capture_output=True, text=True, cwd=MEASURE.parent)
    path = shot.with_suffix('.measure.json')
    if out.returncode or not path.exists():
        return None, (out.stderr or out.stdout)[-200:]
    rows = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(rows, dict):
        rows = rows.get('frames') or list(rows.values())
    row = rows[0]
    axes = {a: row.get(a, (row.get('axes') or {}).get(a))
            for a in ('VARIETY', 'DETAIL', 'DEPTH', 'MATERIAL')}
    return axes, None


def run(room, grammar, keys):
    spec_path = HERE / 'rooms' / (room + '.json')
    print('=== %s ===' % room)
    problems = check(spec_path, grammar, keys)
    if problems:
        print('  INVALID - not rendered:')
        for p in problems:
            print('   -', p)
        return False
    print('  spec valid')

    started = time.time()
    diag, shot, errors = render(room)
    if diag.get('error'):
        print('  BUILD FAILED in the page: %s' % diag['error'])
        return False
    if errors:
        print('  PAGE ERRORS: %s' % errors[:3])
        return False
    print('  built %d primitives, %d drawables, %d uncited, %d triangles (%.1fs)'
          % (len(diag['builtPrimitives']), diag['drawables'], diag['uncited'],
             diag['triangles'], time.time() - started))
    if diag['uncited']:
        print('  FAIL: %d drawables carry no evidence' % diag['uncited'])
        return False
    if diag['drawables'] < 4:
        print('  FAIL: %d drawables is an empty room' % diag['drawables'])
        return False

    axes, err = measure(shot)
    if err:
        print('  could not measure: %s' % err)
        return False

    ok = True
    for axis, (lo, hi) in (diag.get('expect') or {}).items():
        v = axes.get(axis)
        inside = v is not None and lo <= v <= hi
        ok &= inside
        print('  %-9s %.3f   expected %.2f..%.2f   %s'
              % (axis, v if v is not None else -1, lo, hi, 'ok' if inside else 'OUTSIDE'))
    for axis, v in axes.items():
        if axis not in (diag.get('expect') or {}):
            print('  %-9s %.3f   (not declared)' % (axis, v))
    print('  VERDICT: %s  ->  %s' % ('meets its own spec' if ok else 'outside declared ranges',
                                     shot.name))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rooms', nargs='*')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    grammar, keys = primitives(), atlas_keys()
    rooms = a.rooms or ([p.stem for p in sorted((HERE / 'rooms').glob('*.json'))] if a.all else [])
    if not rooms:
        ap.error('name a room, or --all')
    results = [run(r, grammar, keys) for r in rooms]
    print('\n%d/%d room(s) meet their own spec' % (sum(results), len(results)))
    raise SystemExit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
