"""One-shot closure after four actual image inspections; no runtime promotion."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import struct

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v32'
OUT = HERE / (PREFIX + '-integrity.json')
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

summary = read(PREFIX + '-receipts.json')
gate = read('centre-v32-integrity.json')
assert summary['passed'] and summary['protected_unchanged'] and not summary['errors']
assert gate['integrity_passed'] and gate['numeric_passed']
assert summary['protected_before'] == summary['protected_after'] == gate['protected']
for hashes in [gate['protected'], gate['files'], summary['source_hashes']]:
    assert all(digest(n) == h for n, h in hashes.items())
receipts = summary['receipts']
labels = ['entry', 'entry-motion', 'deep', 'deep-motion']
assert [r['file'] for r in receipts] == [PREFIX+'-'+s+'.png' for s in labels]
for r in receipts:
    assert digest(r['file']) == r['capture_sha256']
    assert read(Path(r['file']).with_suffix('.json')) == r
    assert struct.unpack('>II', (HERE/r['file']).read_bytes()[16:24]) == (1200, 800)
    d = r['capture_diagnostics']
    assert d['stage'] == 'chrysanthemum' and d['detail'] == 'high' and d['paused']
    assert not d['renderPending'] and not d['transition'] and not d['missingEvidence']
    assert d['uncitedMeshes'] == 0 and d['animTime'] == d['renderedAnimTime']
    assert r['settle_seconds'] <= 90 and r['veil_opacity'] == 0 and not r['errors']
for a, b in [(receipts[0], receipts[1]), (receipts[2], receipts[3])]:
    da, db = a['capture_diagnostics'], b['capture_diagnostics']
    assert all(da[k] == db[k] for k in ['position', 'yaw', 'pitch', 'stage', 'detail'])
    assert db['animTime'] - da['animTime'] >= 3
walk = next(t for t in summary['timings'] if 'polling_ms' in t)
assert walk['wall_seconds'] < 45 and walk['polling_ms'] == 50 and walk['native_controls']
assert -8 <= walk['after_release_pause']['position'][2] <= -6

reasons = {
    'entry': 'A readable concentric sixfold flower and enclosure replace sparse spokes, but chunky blue pod-like lobes and gold cut tabs dominate. Huge smooth magenta/purple outer patches, broad plastic highlights, hard-cut/stair-stepped rims and only a few coarse layers. Tiny black axial hole; apertures mostly expose more coloured sheet. No overwhelming resolved recursive petal hierarchy.',
    'entry-motion': 'Large blue/green pods rotate and opening/tab shapes change; the flower remains a glossy rainbow tunnel. Broad continuous annular bands, repeated chunky fins and large smooth surfaces overwhelm the small inner details. Cut-looking edges and smeared white highlights do not read as intricate jewel/chrome geometry.',
    'deep': 'Approach enlarges balloon-like blue/green scalloped sheets rather than revealing finer petal structure. A small inner flower has red tubes and gold tabs, but the surrounding field is mostly smooth ramps with blunt holes and dark doubled/stair-stepped rims. Insufficient black depth, branching filigree or nested density; strongly plastic/game-like.',
    'deep-motion': 'The inner opening develops blue eyelet-like cups and gold cut fins while broad outer lobes bend and change colour. Large smooth patches and hard sheet seams persist; nesting is only a few coarse concentric levels, not per-pixel intricacy. Tiny black centre and washed/smeared specular streaks fail the spatial/material realism bar.'
}
temporal = ('Both fixed-pose pairs visibly change lobe orientation, apertures, inner forms and colour. '
            'This is more than pigment alone, but two coarse flower states do not establish convincing '
            'continuous recursive unfolding/breathing, smoothness or temporal antialiasing.')
next_work = ('Build an isolated v33 with many individually tapered, curled petal cells across angular, '
             'radial and depth coordinates, with spatially resolved child petals and open inter-layer gaps. '
             'Replace the broad continuous annular membrane topology; do not merely recolour it or add '
             'small harmonic ripples. Re-derive bounds/filtering and independently validate the changed '
             'field before new HIGH pairs. Preserve clearance, real controls and existing root budgets/tolerances.')
review = {
    'question': 'Would someone who has had this experience recognise this, or does it read as a game?',
    'diagnostic_only': True, 'overall_grade': 'GAME', 'rejected': True, 'promotion': False,
    'inspection_method': 'Each of four NEW PNGs viewed exactly once with view_image after renderer exit0.',
    'frames': [{'file': r['file'], 'sha256': r['capture_sha256'], 'inspections': 1,
                'grade': 'GAME', 'reasons': reasons[label]} for r, label in zip(receipts, labels)],
    'temporal_grade': 'GAME', 'temporal_observation': temporal,
    'capture_gate_passed': True, 'timings': summary['timings'],
    'source_or_coverage_credit': False, 'next_work': next_work,
    'limits': 'Visual judgement, not witness validation. No hardware-GPU benchmark, temporal-AA proof, original physical-exit or full acceptance claim.'
}
settles = [r['settle_seconds'] for r in receipts]
pairs = [t for t in summary['timings'] if 'animation_seconds' in t]
metrics = (f'Four 1200×800 HIGH frames; zero browser errors, settled and paused, veil0, '
           f'zero missingEvidence/uncited meshes. Settles {min(settles):.4f}–{max(settles):.4f}s <90s. '
           f'Entry [0,1.7,8], deep {receipts[2]["capture_diagnostics"]["position"]}, yaw/pitch0. '
           f'Fixed-pose pair separation {pairs[0]["animation_seconds"]:.4f}/'
           f'{pairs[1]["animation_seconds"]:.4f} animation seconds; '
           f'{pairs[0]["wall_seconds"]:.4f}/{pairs[1]["wall_seconds"]:.4f} wall seconds including controls/rendering. '
           f'Native timer-observed deep stop {walk["wall_seconds"]:.4f}s; no injected state.')
md = '# v32 visual review — REJECTED GAME\n\n'
md += review['question'] + '\n\nAll four read as a game. No promotion.\n\n'
for label in labels:
    md += f'## {label} — GAME\n\n{reasons[label]}\n\n'
md += '## Motion and capture evidence\n\n' + temporal + '\n\n' + metrics + '\n\n'
md += ('Numerical checks remain passed, not visual proof. Native stop success is specific to this fixture, '
       'not original45s physical exit/full acceptance or a proven cause of v30 overshoot. '
       'SwiftShader wall times are not hardware-GPU performance. Two separated frames are not a temporal-AA proof.\n\n')
md += ('Each new PNG inspected once after renderer exit0; no historical image re-viewed. '
       'latest.png is the inspected, visibly labelled ISOLATED v32 deep-motion diagnostic, not live geometry. '
       'Live v25/trip18/HUD, defaults and source/manual ledgers unchanged. No source/coverage credit '
       'or unchanged acceptance/fidelity rerun. All19 realism targets, remaining16 source gates, '
       'coverage, route and full acceptance remain open.\n\n## Next structural work\n\n' + next_work + '\n')

# Check all planned documentation anchors and one-shot destinations before writes.
readme_path = HERE/'README.md'
readme = readme_path.read_text()
start = readme.index('latest.png now shows the inspected1200×800 **ISOLATED v31 deep-motion diagnostic**,')
end = readme.index('\nOld full defaults', start)
replacement = '''latest.png now shows the inspected1200×800 **ISOLATED v32 deep-motion diagnostic**,
not live geometry. **V32 is rejected, GAME** in all four fresh entry/deep frames:
chunky glossy pods/scalloped sheets, large smooth colour ramps, cut-looking rims,
tiny black centre and too little resolved nested flower detail. Form and colour
change at fixed poses but do not establish convincing recursive unfolding.
See [v32 visual review](diagnostic-centre-v32-review.md).

Capture PASS: four HIGH frames settled25.10–31.53s under90s,zero browser errors;
native timer-observed deep stop z−6.0576 in4.4211s. This is fixture evidence,
not full physical-exit acceptance, temporal-AA proof or a hardware-GPU benchmark.
[V32 numerical checks](centre-v32-numerical-review.md) remain passed, not realism.
No promotion or source/coverage credit. Live v25/trip18/HUD,defaults,manual/source
ledgers and earlier failed evidence remain unchanged. Next:isolated v33 discrete
tapered/curled petal cells with resolved child geometry and open depth gaps,
replacing broad annular sheets; independently validate the changed field first.
'''
notes_path = HERE/'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE/'NOTES-before-centre-v32-visual.md'
assert not archive.exists()
for name in [PREFIX+'-review.json', PREFIX+'-review.md']:
    assert not (HERE/name).exists()
lines = original.decode('utf-8-sig').splitlines()
lines[0] = '# Active: REDIRECT4 — v32 REJECTED GAME; NEXT substantive v33 petal-cell geometry'
idx = next(i for i, line in enumerate(lines) if line.startswith('2. v31 REJECTED GAME,'))
lines[idx] = ('2. v32 visual phase CLOSED:all4 HIGH entry/deep frames GAME; no promotion or replay. '
              'Exact next:substantive isolated v33 tapered/curled petal cells with resolved child geometry '
              'and open depth gaps, replacing broad annular sheets; numerical validation before fresh visuals.')
notes = '\n'.join(lines) + '\n\n## Closed v32 visual attempt — REJECTED; no replay\n'
notes += '- render_centre_v32.py ONCE exit0. ' + metrics + ' Not full exit acceptance/general reliability.\n'
notes += ('- All4 diagnostic-centre-v32 entry/entry-motion/deep/deep-motion PNGs inspected exactly ONCE after exit. '
          'ALL GAME:coarse concentric flower/enclosure restored,but chunky glossy pods/balloon sheets, '
          'large smooth ramps,cut tabs/doubled stair-stepped rims,small black axial hole,weak open depth and '
          'resolved nested hierarchy. Deep approach enlarges coarse surfaces. '+temporal+' No source credit/promotion.\n')
notes += ('- close_centre_v32_visual.py ONCE binds4 receipts/PNGs/numerical/source/protected hashes, '
          'review,json/integrity;latest=inspected labelled ISOLATED v32 deep-motion. README/status current; '
          'NOTES once,BOM preserved,archive NOTES-before-centre-v32-visual.md. Live v25/trip18/HUD, '
          'defaults/manual/source ledgers and numeric evidence unchanged. No fidelity/unchanged acceptance rerun.\n')
notes += '- Exact next: ' + next_work + ' Other18 realism,remaining16 source gates,coverage,route/full acceptance remain open;no completion marker.\n'
ast.parse((HERE/Path(__file__).name).read_text())
(HERE/(PREFIX+'-review.json')).write_text(json.dumps(review, indent=2)+'\n')
(HERE/(PREFIX+'-review.md')).write_text(md)
shutil.copyfile(HERE/receipts[-1]['file'], HERE/'latest.png')
readme_path.write_text(readme[:start]+replacement+readme[end:])
(HERE/'status.txt').write_text('Isolated v32 REJECTED GAME:all4 fresh1200x800 HIGH entry/deep frames chunky glossy pods/scalloped sheets,large smooth ramps,cut rims,weak nested detail/black depth. Capture PASS,zero errors,settles25.10–31.53s<90s,pairs3.0834/3.1999anim seconds. Native timer-observed deep stop z-6.0576 in4.4211s PASS;not original exit/full acceptance. latest.png=inspected labelled v32 deep-motion diagnostic. Live v25/trip18/HUD,defaults/ledgers unchanged,no promotion. Next substantive v33 tapered curled petal cells with resolved children/open gaps,not broad annular sheets;all19/source/coverage/route/full unfinished.\n')
archive.write_bytes(original)
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
protected = {n:h for n,h in gate['protected'].items() if n != 'latest.png'}
assert all(digest(n) == h for n,h in protected.items())
assert digest('latest.png') == receipts[-1]['capture_sha256']
files = [Path(__file__).name, 'render_centre_v32.py', 'render-centre-v32.log',
         'centre-v32-integrity.json', PREFIX+'.html', PREFIX+'-receipts.json',
         PREFIX+'-review.json', PREFIX+'-review.md']
files += [n for r in receipts for n in [r['file'], str(Path(r['file']).with_suffix('.json'))]]
OUT.write_text(json.dumps({
    'integrity_passed': True, 'capture_gate_passed': True, 'visual_grade': 'GAME',
    'rejected': True, 'promotion': False, 'protected': protected,
    'files': {n:digest(n) for n in files},
    'display': {'latest.png': digest('latest.png'), 'source': receipts[-1]['file'], 'diagnostic_only': True},
    'documentation': {n:digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', archive.name]}
}, indent=2)+'\n')
print('v32 visual closure PASS:4 GAME,rejected;capture/deep stop PASS;latest labelled diagnostic;live/defaults/ledgers unchanged.')
