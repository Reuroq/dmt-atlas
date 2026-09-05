"""Close the one-shot HIGH timeout without replaying or promoting anything."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r3'
OUT = HERE / 'centre-v33r3-capture-integrity.json'
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

gate = read('centre-v33r3-integrity.json')
s = read(PREFIX + '-receipts.json')
assert gate['integrity_passed'] and gate['numeric_passed']
for hashes in [gate['files'], gate['protected'], gate['display'], s['source_hashes']]:
    verify(hashes)
assert not s['passed'] and s['protected_unchanged'] and not s['errors']
assert s['protected_before'] == s['protected_after'] == gate['protected']
assert not s['receipts'] and not list(HERE.glob(PREFIX + '*.png'))
failure = s['failure']
d = failure['diagnostics']
assert failure['operation'] == 'entry settle'
assert 'Timeout 90000ms exceeded' in failure['exception']
assert d['stage'] == 'chrysanthemum' and d['detail'] == 'high' and d['paused']
assert d['position'] == [0, 1.7, 8] and d['yaw'] == d['pitch'] == 0
assert d['renderPending'] and not d['transition']
assert d['animTime'] == d['renderedAnimTime']
assert not d['missingEvidence'] and d['uncitedMeshes'] == 0
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'status.txt').read_text().startswith('Isolated v33r3 NUMERICAL PASS:')
ast.parse(Path(__file__).read_text())

next_work = (
    'Build an isolated read-only full-resolution timing diagnostic of v33r3 before another marcher change. '
    'Instrument existing render submission and fence polling/retirement with stage, animation clock, '
    'invalidation state and monotonic timestamps; separate synchronous submission from pending-fence time '
    'and invalidation starvation. Use bounded in-memory records, export even on failure, and verify '
    'instrumentation removal restores source byte-for-byte. Native controls and read-only journeyDiagnostics '
    'only; no pose, route or clock injection, extra blocking readbacks, gl.finish or acceptance bypass. '
    'Run the substantively instrumented diagnostic ONCE at original1200x800 HIGH/90s; preserve limits '
    'and timeout evidence. Do not replay unchanged captures/probes. Treat instrumentation as perturbative '
    'and do not infer hardware-GPU performance or realism. Choose the next optimization only from evidence; '
    'independently revalidate any changed marcher before a fresh capture.'
)
reason = (
    f'First HIGH entry settle timed out after {failure["operation_wall_seconds"]:.6f}s '
    'under unchanged90000ms. No screenshot reached; zero PNGs or inspections. '
    f'Paused entry[0,1.7,8],yaw/pitch0,frame{d["frames"]},time/rendered{d["animTime"]}, '
    'renderPending=true; no transition,missing evidence,uncited meshes or recorded browser errors. '
    'Entry temporal advance and deep controls were not reached.'
)
review = {
    'diagnostic_only': True, 'renderer_exit_code': 1,
    'capture_gate_passed': False, 'numeric_passed': True, 'visual_grade': 'UNREVIEWED',
    'new_images': 0, 'inspections': 0, 'failure': failure, 'reason': reason,
    'next_work': next_work,
    'limits': 'SwiftShader timeout, not exact profiling diagnosis or hardware-GPU benchmark. No visual, temporal, source, coverage, physical-exit or full-acceptance credit.'
}
md = '# v33r3 HIGH capture — FAIL90s; visually UNREVIEWED\n\n' + reason + '''

The prepared renderer ran ONCE and exited1. Original1200×800 HIGH/90s,
native controls and all source/protected hashes were retained. No retry,
limit relaxation, runtime promotion or unchanged acceptance rerun occurred.
No new image exists, so latest.png remains the previously inspected and labelled
REJECTED GAME v32 deep-motion diagnostic. Existing visual defaults and ledgers
remain unchanged; no new visual grade is assigned.

Numerical PASS remains valid, but does not establish full-resolution acceptance.
The saved sparse-ray timings did not establish a speedup. renderPending combines
invalidation and fence state; the saved receipt does not distinguish their causes.
Equal submitted/rendered clock labels are not proof of GPU completion.

## Next

''' + next_work + '\n\nAll19 realism, remaining16 source gates, coverage, route and full acceptance remain unfinished.\n'

notes_path = HERE / 'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE / 'NOTES-before-centre-v33r3-capture.md'
assert not archive.exists()
notes = '''# Active: REDIRECT4 — v33r3 HIGH FAIL90s; next isolated timing diagnostic

## Rules / authority
- Read REDIRECT4/3/2; all19 must be RECOGNISE plus every source/coverage/route/full acceptance gate. GAME/CLOSE requires rebuilding. Numerical/descriptor passes are not realism. No completion marker yet.
- Linux /home/clawd/dmt-atlas; all writes world/; no git, agents, background tasks/services, web searches, GUI or downloads. Targeted bounded rg before selected ranges; do not repeat corpus/atlas exploration. NOTES once per phase, preserve BOM.
- Headless Chromium/SwiftShader: PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. numpy/PIL if needed: PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages. Direct file:// uses bundled Three0.160.1/data. No screen.cmd here; view_image each NEW image exactly ONCE after renderer exit. Never re-view historical PNGs or replay completed one-shot builders/probes/acceptance.
- Real keyboard/touch/drag/buttons only; journeyDiagnostics read-only, no pose/input/route/clock injection. Preserve strict pixel equality, centre tolerance−3.2..0, original45s exit,1200×800 HIGH/90s settled waits. No unchanged desktop acceptance reruns.
- Full prior notes archived verbatim in NOTES-before-centre-v33r3-capture.md; search only needed sections. Historical failures and inspected images remain immutable.

## Stable live state / open gates
- Live continuum.js==continuum-v25.js; trip.js==trip-v18.js. Input-pump v18 fixed native movement integration; original centre/45s exit and reduced-mobile controls passed. Deterministic hud-alpha-ramp-v18.png corrected original9457 one-bit HUD composition failure: static21/21 and original affected HIGH6/6 passed. These completed checks must not be replayed; no full acceptance claim.
- latest.png remains inspected labelled REJECTED GAME diagnostic-centre-v32-deep-motion.png. No new v33/v33r2/v33r3 PNGs. visual-chrysanthemum.png/json unchanged/stale. Manual/source ledgers and defaults immutable in diagnostic phases. No candidate promoted.
- WORLD_DATA:172 entries,103 sources,14309 reports. Route onset→geometry→chrysanthemum→rush→membrane→waiting→cathedral→contact→download→return→afterglow; Workshop/Garden/Clinical/Void return to Cathedral. Route221s editorial. Waiting→Cathedral41/reverse64 and Contact→Download12/reverse129 are prose adjacency counts,not measured durations. Route audit pending.
- Chrysanthemum source audit complete:70 fixed-order candidates of480,50include/20exclude in chrysanthemum-source-batch2.md/json. Top15 flower20,patterns17,multicolour14,fractals8,tunnel8,spinning6,luminous5,transforming5,dark4,green4,purple-pink4,vivid4,beings3,breathing3,folding3;weight108. Counts not independent witnesses/prevalence. Retain dark green l3xvln,layered entrance5ngny9 and justified extension dny4gl. No recollection/re-audit.
- Garden27 exhausted4/23 and Workshop76 exhausted28/48;historical coverage84.1/85.4%,images stale. Other16 source gates incomplete. Frozen corpus/passages/queue/lexicon/ledger unchanged;15 supplements(4Garden/11Workshop). Read only selected VISUAL_RESEARCH.json entries.
- Chrysanthemum live GAME,historical coverage84.7% FAIL(top10 dark ABSENT). v29/v30/v31/v32 isolated visuals all rejected GAME: broad sheets or sparse radial forms,button-like centre,sparse resolved hierarchy,smeared highlights; changed pixels not convincing breathing/fold-over. Rebuild geometry,not just colour/noise. Detailed visual reasons and each one-time inspection are preserved in diagnostic-centre-v*-review.md and archived notes.
- Preserve x bounds±4,entryz8,exit−22,closing geometry beyond−27.5,clearance≥4,HIGH2048/LOW1536 budgets,14bisections,.00015 residual/directional gate,no minimum step. Preserve native movement/collisions/portals,being interactions,Sources,paused/reduced idle,restart,paced mode,shader LOW. Onset/afterglow/dark Void are source-specific density exceptions.

## v33r3 numerical phase CLOSED — do not replay
- Isolated two-tier marcher preserves v33 scalar/materials: cheap f/axial-only lower jets certify free reaches>.08 before full v33r2 field evaluation; intersectionMAX/unionMIN,.4 cap; bracket history cleared only on certified skip. .08 is branch selector,not minimum step. Two-insertion reversal recovers parent exactly; AST/JS PASS.
- Bounds/GPU/independent first-root/cost ONCE exit0:72000leaf/reach+12000clearance,32cases/50772GPUrays,480fixed+480interval roots PASS;zero misses/errors/unresolved/composite-FD discrepancies. Failed4.895 covered both grids,HIGH/LOW,entry/deep. Worst root error≈.000620;cheap/full jets exactly match.
- No speedup established:matched mean iterations166.92→170.71;median3-readbacks.416→.488s. Mean full trace calls105.46,certified skips57.80. Timing boundaries/instrumentation differ;not controlled benchmark or full-resolution performance. Sampled/ordinary float64 evidence is not universal convergence or GPU roundoff proof.
- centre-v33r3-integrity.json binds34 numerical files,17 protected files and prepared renderer. Historical display hashes are snapshots before this capture closure. Prior v33/r2 entry HIGH90s failures remain; no replay.

## v33r3 capture phase CLOSED — FAIL90s; no replay
''' + '- render_centre_v33r3.py ONCE exit1. ' + reason + '''
- close_centre_v33r3_capture_failure.py verifies numerical/source/protected/display hashes,records diagnostic-centre-v33r3-review.md/json and centre-v33r3-capture-integrity.json. README/status current;NOTES rewritten once,BOM preserved,prior notes archived. No new PNG to inspect or copy;latest unchanged and labelled. No fidelity/acceptance rerun or promotion.
- Numerical PASS retained;full-resolution gate FAIL,visual/temporal UNREVIEWED. renderPending combines invalidation and fence state;receipt does not distinguish cause. Submitted clock equality is not GPU completion. Do not assume more marcher arithmetic is the sole bottleneck.

## Exact next bounded work
''' + next_work + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'

readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r3 two-tier marcher passes numerical checks; visuals UNREVIEWED**.')
end = readme.index('\n\nOld full defaults', start)
replacement = '''Isolated **v33r3 two-tier marcher passes numerical checks but FAILS the
original HIGH90s entry settling gate** (90.0188s). Zero PNGs or recorded browser
errors; visuals **UNREVIEWED**, no promotion. Sparse-ray cost did not establish
a speedup. See [numerical review](centre-v33r3-numerical-review.md) and
[capture failure](diagnostic-centre-v33r3-review.md).
Next: isolated submission/fence/invalidation timing diagnostic at unchanged
1200x800 HIGH/90s before another optimization. Prior failures remain;no replay.
Live/defaults/ledgers and latest inspected REJECTED GAME v32 diagnostic unchanged.'''
status = ('Isolated v33r3 HIGH CAPTURE FAIL:entry settle90.0188s under unchanged90000ms;'
    'renderPending=true,zero recorded browser errors,zero PNGs;visually UNREVIEWED,no promotion. '
    'Numerical PASS retained,no speedup established. Next isolated read-only submission/fence/invalidation '
    'timing diagnostic at original1200x800 HIGH/90s;no unchanged capture/probe replay. '
    'latest.png remains inspected labelled REJECTED GAME v32 deep-motion. '
    'Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')

for suffix in ['-review.md', '-review.json']:
    assert not (HERE / (PREFIX + suffix)).exists()
(HERE / (PREFIX + '-review.md')).write_text(md)
(HERE / (PREFIX + '-review.json')).write_text(json.dumps(review, indent=2) + '\n')
readme_path.write_text(readme[:start] + replacement + readme[end:])
(HERE / 'status.txt').write_text(status)
archive.write_bytes(original)
notes_path.write_text(notes, encoding='utf-8-sig')
verify(gate['protected'])
verify(gate['files'])
files = set(gate['files']) | set(s['source_hashes']) | {
    'centre-v33r3-integrity.json', PREFIX + '-receipts.json', PREFIX + '-review.md',
    PREFIX + '-review.json', 'render-centre-v33r3.log', archive.name, Path(__file__).name}
OUT.write_text(json.dumps({
    'integrity_passed': True, 'numeric_passed': True, 'capture_gate_passed': False,
    'visual_grade': 'UNREVIEWED', 'new_images': 0, 'inspections': 0,
    'protected': gate['protected'], 'files': {n: digest(n) for n in sorted(files)},
    'display': {n: digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', 'latest.png']},
    'next': next_work}, indent=2) + '\n')
print('v33r3 capture failure closure PASS; zero PNGs, no promotion; next isolated timing diagnostic.')
