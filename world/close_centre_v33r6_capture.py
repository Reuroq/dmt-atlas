"""Close the original one-shot capture: one inspected GAME still, temporal timeout."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r6'
OUT = HERE / 'centre-v33r6-capture-integrity.json'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name

assert not OUT.exists()
ast.parse(Path(__file__).read_text())
gate = read('centre-v33r6-integrity.json')
s = read(PREFIX + '-receipts.json')
exit_receipt = read('render-centre-v33r6-once-exit.json')
assert gate['integrity_passed'] and gate['numeric_passed']
for hashes in [gate['files'], gate['protected'], gate['display'], s['source_hashes']]:
    verify(hashes)
assert exit_receipt['exit_code'] == 1
assert exit_receipt['command'] == 'python3 -u world/render_centre_v33r6.py'
assert exit_receipt['log'] == 'render-centre-v33r6-once.log'
assert not s['passed'] and s['protected_unchanged'] and not s['errors']
assert s['protected_before'] == s['protected_after'] == gate['protected']
assert len(s['receipts']) == 1
r = s['receipts'][0]
assert r['file'] == PREFIX + '-entry.png'
assert sorted(p.name for p in HERE.glob(PREFIX + '*.png')) == [r['file']]
assert read(PREFIX + '-entry.json') == r
assert digest(r['file']) == r['capture_sha256']
assert r['resolution'] == [1200, 800] and r['veil_opacity'] == 0
assert 0 < r['settle_seconds'] < 90 and not r['errors']
assert r['source_hashes'] == s['source_hashes']
first = r['capture_diagnostics']
failure = s['failure']
d = failure['diagnostics']
for diag in [first, d]:
    assert diag['stage'] == 'chrysanthemum' and diag['detail'] == 'high'
    assert diag['position'] == [0, 1.7, 8] and diag['yaw'] == diag['pitch'] == 0
    assert not diag['transition'] and not diag['missingEvidence'] and diag['uncitedMeshes'] == 0
assert first['paused'] and not first['renderPending']
assert first['animTime'] == first['renderedAnimTime']
assert failure['operation'] == 'entry real temporal advance and pause'
assert 'Timeout 90000ms exceeded' in failure['exception']
assert not d['paused'] and d['renderPending']
advance = d['animTime'] - first['animTime']
assert 0 < advance < 3
assert d['renderedAnimTime'] < d['animTime']
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'status.txt').read_text().startswith('Isolated v33r6 numerical/cost CLOSED PASS:')

reason = (
    'GAME (entry still only): disconnected oval/disc-like coloured pieces arranged in sparse radial '
    'chains across a predominantly black field. Rainbow bands give some pieces iridescent colour, '
    'but many read as flat coloured marks. Simple silhouettes, smooth interiors and repeated rows '
    'dominate; no convincing continuous curled petal surfaces or resolved nested fractal hierarchy. '
    'The centre is a dark gap rather than a legible folding flower. It reads as a procedural particle '
    'tunnel/game effect, not a recognisable immersive chrysanthemum. Black depth and multiple colours '
    'are visible, but do not establish source-specific dark-green layering or coverage. No motion '
    'claim can be made from this sole still.'
)
next_work = (
    'Design and implement a substantive isolated v34 geometry rebuild from the rejected v33r6, '
    'not another colour-only or arithmetic-only revision. First inspect only targeted petal-cell '
    'definitions and the existing chrysanthemum source conclusions; do not repeat corpus research. '
    'Aim for continuous curled parent laminae with readable overlapping petal depth, connected '
    'nested children and nonuniform scale hierarchy, retaining open black gaps rather than sparse '
    'oval chains or broad annular sheets. Plan a bounded cheaper field and conservative reach '
    'certificate together; preserve corridor/clearance, budgets, root gates and native controls. '
    'Close the implementation/proof phase before new one-shot numerical/cost and original '
    '1200x800 HIGH/90s capture gates. Do not replay v33r6, prewarm, relax limits or change the '
    'frame pump on this receipt. GAME requires rebuilding; no live promotion.'
)
limits = (
    'One inspected still is not a completed realism sequence. Temporal pair and deep views '
    'UNREVIEWED; no breathing/fold-over, temporal-AA, source/coverage, exit or full-acceptance credit. '
    'The timeout receipt does not isolate execution, compilation, queue or frame scheduling. '
    'Submitted/rendered clock labels and frames are not GPU-completion measurements. Sparse cost '
    'PASS remains valid but does not establish full-resolution performance or hardware-GPU speed.'
)
review = {
    'diagnostic_only': True, 'renderer_exit_code': 1, 'numeric_passed': True,
    'capture_gate_passed': False, 'entry_settle_passed': True,
    'visual_grade': 'GAME', 'visual_scope': 'entry still only',
    'temporal_grade': 'UNREVIEWED', 'deep_grade': 'UNREVIEWED',
    'new_images': 1, 'inspections': 1, 'inspection_method': 'view_image once after actual renderer exit',
    'inspected_image': r['file'], 'inspected_sha256': r['capture_sha256'],
    'reason': reason, 'failure': failure, 'observed_animation_advance': advance,
    'entry_settle_seconds': r['settle_seconds'], 'promotion': False,
    'latest_update': 'Byte-copy of inspected, visibly labelled ISOLATED v33r6 entry diagnostic; REJECTED GAME in README/status.',
    'limits': limits, 'next_work': next_work,
}
md = (
    '# v33r6 capture — entry REJECTED GAME; temporal gate FAIL90s\n\n'
    f'Original renderer ran ONCE, actual exit1 saved. Entry HIGH1200×800 settled in '
    f'{r["settle_seconds"]:.6f}s under unchanged90000ms; veil0, paused, renderPending=false, '
    f'equal clocks{first["animTime"]}, frame{first["frames"]}, position[0,1.7,8], yaw/pitch0. '
    'One PNG and receipt saved. Zero recorded browser errors, missing evidence or uncited meshes.\n\n'
    f'Native temporal advance timed out after {failure["operation_wall_seconds"]:.6f}s. '
    f'Animation advanced only{advance:.6f}s of required3; final unpaused clock{d["animTime"]}, '
    f'rendered clock{d["renderedAnimTime"]}, frame{d["frames"]}, renderPending=true. '
    'No second still, completed temporal pair, deep walk or deep capture was reached.\n\n'
    '## One-time visual inspection\n\n' + reason + '\n\n'
    'The sole NEW PNG was viewed exactly once after exit. No historical PNG was re-viewed. '
    'latest.png now byte-matches this inspected ISOLATED v33r6 entry diagnostic, explicitly '
    'REJECTED GAME here and in README/status; this is a diagnostic display update, not a live '
    'candidate promotion. Historical v32 PNGs remain immutable. Live/defaults/manual/source '
    'ledgers remain unchanged. No completed numerical/cost/acceptance checks were replayed.\n\n'
    '## Limits\n\n' + limits + '\n\n## Next\n\n' + next_work + '\n\n'
    'All19 realism, remaining16 source gates, coverage, route and full acceptance remain unfinished.\n'
)

notes_path = HERE / 'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE / 'NOTES-before-centre-v33r6-capture.md'
assert not archive.exists()
notes = original.decode('utf-8-sig')
notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v33r6 entry GAME; temporal FAIL90s; capture CLOSED', 1)
old_live = '- latest.png remains inspected labelled REJECTED GAME diagnostic-centre-v32-deep-motion.png. No new v33/v33r2/v33r3 PNGs. visual-chrysanthemum.png/json unchanged/stale. Manual/source ledgers and defaults immutable in diagnostic phases. No candidate promoted.'
assert notes.count(old_live) == 1
notes = notes.replace(old_live, '- latest.png now equals the once-inspected ISOLATED v33r6 entry diagnostic, REJECTED GAME; temporal/deep UNREVIEWED. Historical PNGs unchanged. visual-chrysanthemum.png/json unchanged/stale. Manual/source ledgers and defaults immutable; no candidate promoted.')
start = notes.index('## Exact next bounded work')
notes = notes[:start] + (
    '## v33r6 capture phase CLOSED — entry GAME; temporal FAIL90s; no replay\n'
    f'- render_centre_v33r6.py ONCE actual exit1, unique log/exit receipt saved. Original1200x800 HIGH/90000ms retained. Entry settled{r["settle_seconds"]:.6f}s; one PNG inspected once after exit. No browser errors/missing evidence/uncited meshes.\n'
    '- Entry GAME: sparse disconnected rainbow ovals/discs in radial chains, large black gaps, smooth simple interiors, no convincing continuous curled petals or resolved nested hierarchy. Rebuild,not promotion.\n'
    f'- Native entry temporal advance timed out{failure["operation_wall_seconds"]:.6f}s; advanced{advance:.6f}/3s. Final unpaused time{d["animTime"]},rendered{d["renderedAnimTime"]},frame{d["frames"]},renderPending=true. No temporal pair/deep controls reached;UNREVIEWED,no motion credit. Receipt does not isolate delay cause.\n'
    '- Numerical/cost PASS retained,not full-resolution performance. close_centre_v33r6_capture.py binds numerical/source/log/exit/PNG/review hashes. latest byte-copied from inspected ISOLATED v33r6 entry,REJECTED GAME in README/status;sole display-image change,not live promotion. Prior v32 image preserved. All other protected files unchanged. README/status current;NOTES once,BOM preserved,prior notes archived verbatim.\n'
    '\n## Exact next bounded work\n' + next_work + '\n\n'
    'All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'
)
readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('latest.png now shows the inspected1200×800 **ISOLATED v32 deep-motion diagnostic**,')
end = readme.index('\nCapture PASS: four HIGH frames', start)
readme = readme[:start] + (
    'latest.png now shows the once-inspected1200×800 **ISOLATED v33r6 entry diagnostic**, '
    'not live geometry. **REJECTED GAME**: sparse disconnected rainbow oval/disc chains, '
    'smooth simple interiors and little resolved nested flower detail. Entry settled58.754731s, '
    'but the native3s temporal advance timed out90.012559s; actual renderer exit1. '
    'One still only; temporal/deep views UNREVIEWED, no promotion. '
    'See [capture and visual review](diagnostic-centre-v33r6-review.md).\n\n'
    'Historical v32 (unchanged): [GAME visual review](diagnostic-centre-v32-review.md).\n'
) + readme[end:]
start = readme.index('Isolated **v33r6 numerical and paired-cost gates PASS**.')
end = readme.index('\n\nOld full defaults', start)
readme = readme[:start] + (
    'Isolated **v33r6 numerical and paired-cost gates PASS; full capture FAIL**. '
    '48cases/75,996rays,720fixed+720interval roots and12balanced cost pairs remain passed. '
    'Sparse SwiftShader timings do not establish full-resolution performance or isolate factoring. '
    'Original HIGH/90s capture ran ONCE: entry still GAME, temporal timeout, deep not reached. '
    'See [numerical/cost closure](centre-v33r6-numerical-review.md) and '
    '[capture review](diagnostic-centre-v33r6-review.md).\n'
    'Next: substantive continuous curled-petal geometry rebuild, not another colour/arithmetic-only '
    'revision. No frame-pump change, prewarm, replay or limit relaxation. Live/defaults/ledgers '
    'unchanged; latest is the inspected REJECTED GAME v33r6 entry diagnostic.'
) + readme[end:]
status = (
    'Isolated v33r6 capture CLOSED FAIL: entry settled58.754731s; sole NEW1200x800 HIGH PNG '
    'inspected once, REJECTED GAME (sparse rainbow oval chains, weak continuous/nested petals). '
    'Native3s temporal advance timeout90.012559s,only2.05s advanced;actual exit1 saved;'
    'temporal/deep UNREVIEWED. Numerical/cost PASS retained,not full-resolution performance. '
    'latest.png=inspected ISOLATED v33r6 entry diagnostic;no live promotion. '
    'Next substantive continuous curled-petal geometry rebuild;no replay/prewarm/relaxed gates. '
    'Live/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n'
)
for name in [PREFIX + '-review.md', PREFIX + '-review.json']:
    assert not (HERE / name).exists()
# Verify all pre-capture evidence before the explicitly recorded latest/display update.
verify(gate['files'])
verify(gate['protected'])
(HERE / (PREFIX + '-review.md')).write_text(md)
(HERE / (PREFIX + '-review.json')).write_text(json.dumps(review, indent=2) + '\n')
(HERE / 'latest.png').write_bytes((HERE / r['file']).read_bytes())
readme_path.write_text(readme)
(HERE / 'status.txt').write_text(status)
archive.write_bytes(original)
notes_path.write_text(notes, encoding='utf-8-sig')
protected = {n: h for n, h in gate['protected'].items() if n != 'latest.png'}
verify(protected)
verify(gate['files'])
verify(s['source_hashes'])
assert digest('latest.png') == r['capture_sha256']
assert digest('diagnostic-centre-v32-deep-motion.png') == gate['protected']['latest.png']
files = set(gate['files']) | set(s['source_hashes']) | {
    'centre-v33r6-integrity.json', PREFIX + '-receipts.json', PREFIX + '-entry.png',
    PREFIX + '-entry.json', PREFIX + '-review.md', PREFIX + '-review.json',
    'render-centre-v33r6-once.log', 'render-centre-v33r6-once-exit.json',
    'diagnostic-centre-v32-deep-motion.png', archive.name, Path(__file__).name,
}
OUT.write_text(json.dumps({
    'integrity_passed': True, 'numeric_passed': True, 'capture_gate_passed': False,
    'visual_grade': 'GAME', 'visual_scope': 'entry still only',
    'temporal_grade': 'UNREVIEWED', 'deep_grade': 'UNREVIEWED',
    'new_images': 1, 'inspections': 1, 'promotion': False,
    'protected_before': gate['protected'], 'protected': protected,
    'files': {n: digest(n) for n in sorted(files)},
    'display': {n: digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', 'latest.png']},
    'latest_source': r['file'], 'latest_diagnostic_only': True,
    'allowed_display_image_update': {'latest.png': {'before': gate['protected']['latest.png'], 'after': digest('latest.png')}},
    'next': next_work,
}, indent=2) + '\n')
print(json.dumps({'integrity_passed': True, 'capture_gate_passed': False,
    'files': len(files), 'protected': len(protected), 'new_images': 1,
    'inspections': 1, 'entry_grade': 'GAME', 'promotion': False}), flush=True)
