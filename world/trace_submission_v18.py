"""Foreground visual iteration: real controls, offline, no navigation/time injection."""
import argparse
import base64
import hashlib
import sys
import json
import time
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
from verify import ARGS, ROUTE, BRANCHES, evidence
from fidelity import render_signature, digest

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--stage', default='chrysanthemum', choices=ROUTE + BRANCHES)
parser.add_argument('--width', type=int, default=1200)
parser.add_argument('--height', type=int, default=800)
parser.add_argument('--lower', action='store_true')
parser.add_argument('--walk', type=float, default=0, help='Seconds of real forward walking before capture')
parser.add_argument('--walk-to-z', type=float, help='Hold the real forward key until this observed z coordinate; no pose injection')
parser.add_argument('--check-stillness', action='store_true', help='Check paused/reduced canvas pixels and detail-toggle route preservation')
parser.add_argument('--check-sources', action='store_true', help='Check the current scene evidence and report-to-render table through real Sources controls')
parser.add_argument('--capture-transition', action='store_true', help='Pause during real onward passage and capture its signal seam')
parser.add_argument('--temporal-seconds', type=float, default=0, help='Capture two paused HIGH frames separated by at least this much real animation')
parser.add_argument('--exit-sequence', action='store_true', help='Capture real onward fade and the settled destination after the scene capture')
parser.add_argument('--capture-name', help='Stable iteration filename prefix, without an extension')
args = parser.parse_args()
if args.walk and args.walk_to_z is not None:
    parser.error('Choose timed walking or observed-position walking, not both')
if args.capture_name and (Path(args.capture_name).name != args.capture_name or any(c in args.capture_name for c in '/\\:')):
    parser.error('Capture name must be a filename, not a path')
if args.capture_name and any((HERE / f'{args.capture_name}{suffix}.png').exists() for suffix in ['', '-motion', '-exit', '-destination']):
    parser.error('Stable capture prefix already exists; choose a new iteration name')
if args.temporal_seconds < 0 or (args.temporal_seconds and (args.lower or args.check_stillness or args.capture_transition)):
    parser.error('Temporal pairs require HIGH detail and a separate settled-scene run')
if args.exit_sequence and (args.check_stillness or args.capture_transition or args.lower):
    parser.error('Exit sequences require HIGH detail and a settled-scene run')
if args.capture_transition and args.check_stillness:
    parser.error('Capture transitions separately from settled-scene stillness checks')
errors = []
exported_frames = {}
probe_hashes = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['diagnostic-submission-v18.js','diagnostic-submission-v18.html','trace_submission_v18.py']}
def on_failure(kind, value, tb):
    (HERE/'submission-v18-failure.json').write_text(json.dumps({'exception':str(value),'browser_errors':errors,'probe_hashes':probe_hashes},indent=2)+'\n')
    sys.__excepthook__(kind,value,tb)
sys.excepthook=on_failure
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=ARGS)
    page = browser.new_page(viewport={'width': args.width, 'height': args.height}, device_scale_factor=1)
    page.set_default_timeout(90000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.route('https://**/*', lambda r: r.abort())
    page.route('http://**/*', lambda r: r.abort())
    page.goto((HERE / 'diagnostic-submission-v18.html').as_uri())
    page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
    if args.lower:
        page.locator('#detail').click()
    page.locator('#autoStart').uncheck()
    page.locator('#begin').click()
    target = 'cathedral' if args.stage in BRANCHES else args.stage
    for name in ROUTE[1:ROUTE.index(target) + 1]:
        page.locator('#next').click()
        page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=name)
        print('Rendered ' + name, flush=True)
        if errors:
            break
    if args.stage in BRANCHES and not errors:
        page.locator('#pathsToggle').click()
        page.locator(f'[data-branch="{args.stage}"]').click()
        page.wait_for_function('(s)=>journeyDiagnostics().stage===s && !journeyDiagnostics().transition', arg=args.stage)
    if args.walk:
        page.keyboard.down('w')
        page.wait_for_timeout(args.walk * 1000)
        page.keyboard.up('w')
    if args.walk_to_z is not None:
        assert args.walk_to_z < page.evaluate('journeyDiagnostics().position[2]'), 'Forward target must be ahead'
        page.keyboard.down('w')
        try:
            page.wait_for_function('(g)=>journeyDiagnostics().stage!==g.stage || journeyDiagnostics().position[2]<=g.z',
                                   arg={'stage': args.stage, 'z': args.walk_to_z})
        finally:
            page.keyboard.up('w')
        assert page.evaluate('journeyDiagnostics().stage') == args.stage, 'Walk left the requested stage'
    start = page.evaluate('journeyDiagnostics().frames')
    begin = time.perf_counter()
    page.wait_for_timeout(2500)
    result = page.evaluate('journeyDiagnostics()')
    fps = (result['frames'] - start) / (time.perf_counter() - begin)
    if args.capture_transition:
        page.locator('#next').click()
    page.locator('#pause').click()
    if args.capture_transition:
        result = page.evaluate('journeyDiagnostics()')
        assert result['transition'] and result['paused'], 'Transition completed before pause'
    checks = []
    if args.check_stillness:
        def frozen(label):
            # Both paused and idle reduced views must drain pending work. No
            # minimum submission count: a settled view need not redraw at all.
            page.wait_for_function('''() => { const d=journeyDiagnostics();
                return (d.paused || d.reduced) && !d.transition && !d.renderPending &&
                d.renderedAnimTime===d.animTime; }''')
            before = page.evaluate('journeyDiagnostics()')
            probe_before = page.evaluate('submissionProbe.snapshot()')
            # Canvas-sized screenshots include the HUD's advancing progress bar.
            # Compare the unobstructed environment/actor area, as verify.py does.
            clip = {'x': 100, 'y': 110, 'width': args.width - 200, 'height': args.height - 420}
            started = time.monotonic()
            a = Image.open(BytesIO(page.screenshot(clip=clip))).convert('RGB')
            first_seconds = time.monotonic() - started
            settled = page.evaluate('journeyDiagnostics()')
            probe_settled = page.evaluate('submissionProbe.snapshot()')
            page.wait_for_timeout(800)
            started = time.monotonic()
            b = Image.open(BytesIO(page.screenshot(clip=clip))).convert('RGB')
            second_seconds = time.monotonic() - started
            after = page.evaluate('journeyDiagnostics()')
            probe_after = page.evaluate('submissionProbe.snapshot()')
            snapshots = [probe_before,probe_settled,probe_after]
            # Export immutable submitted bytes only AFTER both screenshots.
            for snapshot in snapshots:
                r=snapshot['latest']
                assert r and not snapshot['pending'] and r['frame']==snapshot['diagnostics']['frames'], 'PBO frame association'
                frame=r['frame']
                if frame not in exported_frames:
                    started_export=time.monotonic()
                    data=page.evaluate('(f)=>submissionProbe.exportFrame(f)',frame)
                    raw=base64.b64decode(data['base64'])
                    assert len(raw)==r['width']*r['height']*4
                    filename=f'diagnostic-submission-v18-frame-{frame}.rgba'
                    (HERE/filename).write_bytes(raw)
                    exported_frames[frame]={'record':data['record'],'sha256':hashlib.sha256(raw).hexdigest(),'file':filename,'export_seconds':time.monotonic()-started_export}
                snapshot['submitted_bytes']=exported_frames[frame]
            raw= (HERE/exported_frames[probe_before['latest']['frame']]['file']).read_bytes()
            r=probe_before['latest']
            raw_image=Image.frombytes('RGBA',(r['width'],r['height']),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            assert (r['width'],r['height'])==(args.width,args.height), 'HIGH 1:1 crop required'
            raw_crop=raw_image.crop((clip['x'],clip['y'],clip['x']+clip['width'],clip['y']+clip['height'])).convert('RGB')
            raw_comparisons=[]
            for shot in [a,b]:
                diff=ImageChops.difference(raw_crop,shot)
                raw_comparisons.append({'changed_pixels':sum(any(p) for p in diff.getdata()),'bbox':diff.getbbox(),'max_channel_delta':max(max(p) for p in diff.getdata())})
            difference = ImageChops.difference(a, b)
            if args.capture_name:
                stem = args.capture_name + '-' + '-'.join(label.split())
                (HERE / (stem + '-trace.json')).write_text(json.dumps({
                    'label': label, 'before': before, 'settled': settled, 'after': after,
                    'submission_snapshots':snapshots,'raw_to_screenshots':raw_comparisons,
                    'probe_hashes':probe_hashes,'browser_errors':list(errors),
                    'screenshot_max_channel_delta':max(max(p) for p in difference.getdata()),
                    'submission_events':page.evaluate('submissionProbe.events()'),
                    'screenshot_seconds': [first_seconds, second_seconds],
                    'difference_bbox': difference.getbbox(),
                    'changed_pixels': sum(any(pixel) for pixel in difference.getdata()),
                    'render_signature': render_signature()
                }, indent=2) + '\n')
                if difference.getbbox() is not None:
                    a.save(HERE / (stem + '-before.png'))
                    b.save(HERE / (stem + '-after.png'))
            for snapshot in snapshots:
                r=snapshot['latest']
                assert r['alphaMin']==255 and r['alphaMax']==255 and r['nonzeroRGB']>0, 'Invalid/transparent PBO readback'
                assert r['queueError']==0 and r['retrieveError']==0 and r['queueBindingRestored'] and r['retrieveBindingRestored'], 'PBO state/error'
                assert r['time']==snapshot['diagnostics']['renderedAnimTime'], 'PBO time association'
            print(label+': '+str(raw_comparisons),flush=True)
            for d in [before, settled, after]:
                assert not d['renderPending'] and d['renderedAnimTime'] == d['animTime'], label + ': unsettled view'
                for field in ['animTime', 'position', 'yaw', 'pitch', 'detail', 'frames']:
                    assert d[field] == before[field], label + ': changed ' + field
            assert difference.getbbox() is None, label + ': canvas changed'
            checks.append(label)
        frozen('paused pixel stillness')
        before_resize = page.evaluate('journeyDiagnostics().frames')
        page.set_viewport_size({'width': args.width - 20, 'height': args.height})
        page.wait_for_function('(f)=>journeyDiagnostics().frames>f', arg=before_resize)
        before_restore = page.evaluate('journeyDiagnostics().frames')
        page.set_viewport_size({'width': args.width, 'height': args.height})
        page.wait_for_function('(f)=>journeyDiagnostics().frames>f', arg=before_restore)
        frozen('paused resize restores stable canvas')
        page.locator('#motion').click()
        page.locator('#pause').click()
        frozen('reduced-motion pixel stillness')
        before = page.evaluate('journeyDiagnostics()')
        for _ in range(2):
            page.locator('#detail').click()
            after = page.evaluate('journeyDiagnostics()')
            for field in ['stage', 'routeIndex', 'position', 'yaw', 'pitch', 'visited', 'entities', 'interactions', 'animTime']:
                assert before[field] == after[field], 'Detail toggle changed ' + field
        assert before['detail'] == after['detail']
        checks.append('detail toggle preserves route and pose')
        frozen('restored-detail reduced pixel stillness')
        page.locator('#pause').click()
    suffix = '-lower' if args.lower else ''
    if args.check_sources:
        evidence(page)
        checks.append('Sources fidelity table and existing provenance')
    if args.capture_transition:
        suffix += '-transition'
    path = HERE / f'visual-{args.stage}{suffix}.png'
    prefix = args.capture_name or path.stem
    sequence = []
    def capture(label):
        page.wait_for_function('!journeyDiagnostics().renderPending && journeyDiagnostics().renderedAnimTime===journeyDiagnostics().animTime')
        capture_diagnostics = page.evaluate('journeyDiagnostics()')
        assert capture_diagnostics['paused'], 'Capture must be paused'
        assert not capture_diagnostics['missingEvidence'] and capture_diagnostics['uncitedMeshes'] == 0, 'Uncited capture geometry'
        if args.temporal_seconds or args.exit_sequence:
            assert capture_diagnostics['detail'] == 'high', 'Temporal review needs actual HIGH detail'
        image_path = HERE / f'{prefix}{label}.png'
        page.screenshot(path=str(image_path))
        # Isolated diagnostic; display updated only after review.
        receipt = {'errors': list(errors), 'fps_swiftshader': round(fps, 2), 'checks': list(checks), 'diagnostics': result,
                   'capture_diagnostics': capture_diagnostics, 'render_signature': render_signature(),
                   'probe_hashes':probe_hashes, 'submission_snapshot':page.evaluate('submissionProbe.snapshot()'),
                   'capture_sha256': digest(image_path), 'file': image_path.name,
                   'veil_opacity': page.locator('#veil').evaluate('(e)=>Number(getComputedStyle(e).opacity)')}
        image_path.with_suffix('.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        sequence.append(receipt)
        print('Captured ' + image_path.name, flush=True)
        return capture_diagnostics
    first = capture('')
    if args.temporal_seconds:
        page.locator('#pause').click()
        page.wait_for_function('(t)=>journeyDiagnostics().animTime>=t', arg=first['animTime'] + args.temporal_seconds)
        page.locator('#pause').click()
        second = capture('-motion')
        assert second['stage'] == first['stage'] and second['position'] == first['position']
        assert second['animTime'] - first['animTime'] >= args.temporal_seconds
    if args.exit_sequence:
        page.locator('#pause').click()
        page.locator('#next').click()
        page.locator('#pause').click()
        fading = capture('-exit')
        assert fading['transition'], 'Exit finished before transition capture'
        page.locator('#pause').click()
        page.wait_for_function('!journeyDiagnostics().transition')
        page.locator('#pause').click()
        destination = capture('-destination')
        assert destination['stage'] != first['stage']
    if len(sequence) > 1:
        (HERE / f'{prefix}-sequence.json').write_text(json.dumps(sequence, indent=2), encoding='utf-8')
    # Preserve default captures.
    print(json.dumps({'stage': result['stage'], 'fps_swiftshader': round(fps, 2), 'errors': errors, 'checks': checks, 'missingEvidence': result['missingEvidence'], 'render': str(path)}), flush=True)
    browser.close()
assert not errors, errors
assert not result['missingEvidence'], result['missingEvidence']
