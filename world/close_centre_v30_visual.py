"""One-shot closure of the failed v30 visual sequence; no rerender or promotion."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import struct

HERE=Path(__file__).resolve().parent
PREFIX='diagnostic-centre-v30'
OUT=HERE/(PREFIX+'-integrity.json')
assert not OUT.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
r=json.loads((HERE/(PREFIX+'-receipts.json')).read_text())
assert not r['passed'] and r['protected_unchanged'] and not r['errors']
assert r['protected_before']==r['protected_after']
assert all(digest(n)==h for n,h in r['protected_after'].items())
assert all(digest(n)==h for n,h in r['source_hashes'].items())
gate=json.loads((HERE/'centre-v30-integrity.json').read_text())
assert gate['integrity_passed'] and gate['numeric_passed'] and not gate['promoted']
assert all(digest(n)==h for n,h in gate['files'].items())
assert len(r['receipts'])==2
for c,label in zip(r['receipts'],['entry','entry-motion']):
    assert c['file']==PREFIX+'-'+label+'.png'
    assert digest(c['file'])==c['capture_sha256']
    assert json.loads((HERE/c['file']).with_suffix('.json').read_text())==c
    header=(HERE/c['file']).read_bytes()[:24]
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==(1200,800)
    assert c['resolution']==[1200,800] and c['source_hashes']==r['source_hashes']
    assert not c['errors'] and c['veil_opacity']==0 and 0<=c['settle_seconds']<90
    d=c['capture_diagnostics']
    assert d['stage']=='chrysanthemum' and d['paused'] and d['detail']=='high'
    assert d['position']==[0,1.7,8] and d['yaw']==d['pitch']==0
    assert not d['renderPending'] and d['renderedAnimTime']==d['animTime']
    assert not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes']==0
first,second=[c['capture_diagnostics'] for c in r['receipts']]
assert second['animTime']-first['animTime']>=3
failure=r['failure'];d=failure['diagnostics']
assert failure['operation']=='deep settle' and d['stage']=='rush' and d['paused'] and d['transition']
assert not (HERE/(PREFIX+'-deep.png')).exists()
assert not (HERE/(PREFIX+'-deep-motion.png')).exists()
review='''# Isolated v30 — REJECTED, entry GAME; deep sequence failed

## New images inspected once, after renderer exit

Both `diagnostic-centre-v30-entry.png` and `-entry-motion.png` are fresh
1200×800 HIGH renders, inspected exactly once. Both are **GAME**.

The split-petal volume produces substantially more visible openings, lobes and
depth layers than the previous sheets. But the image still reads as a glossy
rainbow tunnel: large smooth balloon/cup forms around chunky repeated bead/block
bands, similar small round openings, and a circular perforated centre plate.
This is not convincing nested flower filigree or continuously resolving detail.
Fine features remain subordinate to large smooth patches; some small rims look
stair-stepped. Broad highlights give a lacquered plastic appearance rather than
the sharp, intricate jewel/iridescent material target. Saturation is strong but
largely organized into coarse repeated rainbow depth bands.

There are actual apertures and darker recesses, but a convincing spacious black
opening does not read clearly through the brightly filled tunnel. Geometric
aperture existence is not enough to promote the historical dark descriptor.
The centre is larger and perforated, yet still reads as a circular end plate.

Across the same-pose pair, lobes turn, apertures and the centre rearrange, and
colours shift. This is visible deformation, not evidence of convincing rhythmic
breathing or fold-over/self-revealing nested growth. Two widely separated frames
cannot establish smooth motion or temporal antialiasing of the numerical slivers.
Temporal realism remains GAME on this pair, not a pass inferred from changed pixels.

Answer to the recognition question: this reads as a synthetic glossy procedural
tunnel, not a replication that meets the owner's recognition bar. **Reject v30;
no promotion.** Deep realism is UNREVIEWED because no deep image was captured.

## Capture evidence and preserved failure

The one-shot `render_centre_v30.py` used normal controls, current trip18/HUD,
unchanged1200×800 HIGH and90-second settled guards. Entry settles40.0902s and
53.5850s; both within the guard, with zero pending frame, veil or evidence errors.
Pose[0,1.7,8], yaw/pitch0; animation times3.7873000004 and6.8372000004,
frames4 and8. Pair separation3.0499 animation seconds; operation101.8151 wall
seconds, including controls and rendering. These SwiftShader times do not
establish hardware-GPU performance or smoothness.

The held-W walk toward z−6 took25.8544s, then deep capture's stage assertion
failed: diagnostics already showed Rush, paused, transition active, reset entry
pose[0,1.7,8]. This is NOT a settled-timeout failure, a valid deep capture, or
an original45-second physical-exit acceptance result. The read-only observer
did not stop the held walk at its intended stage/position. Exact scheduling/
input-delivery causality is not established by this fixture. No injected pose,
route, clock or navigation shortcut was used. Error list empty, sequence FAIL.
Preserve the script, log, complete entry receipts and failure diagnostics;
do not replay the unchanged rejected candidate to obtain the missing deep pair.

## Display, integrity and next substantive work

latest.png now equals the inspected entry-motion PNG, visibly labelled
`ISOLATED v30 · synthesised diagnostic`. It is not promoted live geometry or a
full acceptance capture. All runtime assets, source/manual ledgers, numerical
receipts and default visual captures remain byte-identical. The earlier fixed
.003 reference failure and separate interval-audited numerical pass are intact.
No unchanged desktop acceptance or fidelity regeneration was run.

Build a substantive successor: replace the chunky repeated bead/block and
circular end-plate organization with branching flower-like nested folds at
multiple resolved scales; make black openings spatially readable and material
highlights precise. Changing pigment alone or adding tiny unresolved holes is
insufficient. Account for field/render cost and the retained deep-walk overshoot
when designing its real-input capture; do not inject state or relax waits/bounds.
New field requires new numerical/bounds/filtering checks and then fresh HIGH
entry/deep temporal evidence. Live v25 remains GAME with the passing trip18/HUD
repairs. All19 realism, remaining16 source gates, coverage, route and full
desktop/mobile/paced/fallback acceptance are unfinished. No completion marker.
'''
(HERE/(PREFIX+'-review.md')).write_text(review)
old_latest=digest('latest.png');new_latest=r['receipts'][-1]['file']
shutil.copyfile(HERE/new_latest,HERE/'latest.png')
assert digest('latest.png')==r['receipts'][-1]['capture_sha256']
assert all(digest(n)==h for n,h in r['protected_after'].items() if n!='latest.png')
readme_path=HERE/'README.md';readme=readme_path.read_text()
start=readme.index('latest.png now shows the freshly inspected1200×800 **live Chrysanthemum**,')
end=readme.index('\nOld full defaults',start)
readme=readme[:start]+'''latest.png now shows the freshly inspected1200×800 **ISOLATED v30 diagnostic**,
not live geometry. V30 is **rejected, GAME**: denser real apertures and changing
lobes, but a glossy chunky rainbow tunnel, repetitive bead/block bands, broad
smooth patches and a perforated circular end plate. Black depth and nested
flower detail remain unconvincing. The entry pair completed; the deep walk
overshot into Rush, so the full visual sequence FAILS and deep is UNREVIEWED.
No promotion or full acceptance. Next: substantive geometric successor plus
real-input capture that addresses the retained deep-walk failure.
See [v30 visual review and failure](diagnostic-centre-v30-review.md) and
[numerical evidence and limits](centre-v30-numerical-review.md).''' + readme[end:]
readme_path.write_text(readme)
status_path=HERE/'status.txt';assert 'Rendering isolated v30' in status_path.read_text()
status_path.write_text('Isolated v30 REJECTED: entry1200x800 HIGH pair GAME,glossy chunky rainbow tunnel,repetitive bead/block bands,circular perforated endplate,weak black depth/nested detail. Deep walk overshot to Rush; sequence FAIL,no deep PNG,zero browser errors. latest.png=inspected labelled v30 entry-motion diagnostic. Live v25/trip18/HUD unchanged,no promotion. Next substantive geometry successor plus deep-walk capture correction;all19/source/coverage/route/full acceptance unfinished.\n')
notes_path=HERE/'NOTES.md';archive=HERE/'NOTES-before-centre-v30-visual.md'
assert not archive.exists();archive.write_bytes(notes_path.read_bytes())
notes=notes_path.read_text(encoding='utf-8-sig')
notes=notes.replace('# Active: REDIRECT4 — isolated v30 numerics closed; NEXT fresh HIGH visual pairs; live v25 GAME',
    '# Active: REDIRECT4 — v30 REJECTED GAME; deep walk overshot; NEXT substantive successor',1)
start=notes.index('2. Isolated v30 substantive split-petal/branch volume BUILT;')
end=notes.index('\n3. Other18 realism targets',start)
notes=notes[:start]+'''2. v30 visual attempt CLOSED,REJECTED: both fresh1200×800 HIGH entry images GAME,inspected ONCE;deep walk overshot into Rush,no deep images,sequence FAIL. Never re-view/rerender unchanged. Exact next: substantive geometry successor replacing chunky bead/block bands and circular endplate with branching flower-like nested folds,resolved hierarchy,spatial black openings,precise materials;control field/render cost. Preserve/analyze deep-walk observer overshoot when building next real-input fixture,no injected pose/route/clock or relaxed guards. New field numerical/bounds/filtering checks then fresh HIGH entry/deep temporal inspection. diagnostic-centre-v30-review.md/integrity.json bind rejected visual evidence;latest is labelled v30 entry-motion diagnostic,not live.''' + notes[end:]
old='- v30 supersedes v29 for NEXT isolated visual inspection; v29 stays rejected.'
assert notes.count(old)==1
notes=notes.replace(old,'- v30 and v29 are both REJECTED; use targeted v30 code as the construction starting point,not a candidate to promote or rerender.')
notes+='''
## Closed v30 visual attempt — REJECTED; no replay
- render_centre_v30.py ONCE completed2 entry PNGs then exit1 at deep-stage assertion. Both full1200×800 HIGH,entry[0,1.7,8],yaw/pitch0,paused,settled,veil0,zero missing/uncited evidence/errors;times3.7873000004/6.8372000004,frames4/8,settles40.0902/53.5850s under90s. Pair3.0499 animation seconds,101.8151 wall seconds including controls/rendering;not hardware-GPU/smoothness proof.
- diagnostic-centre-v30-entry.png and -entry-motion.png each inspected ONCE after renderer exit:both GAME. Denser true apertures/lobes/layers,but glossy chunky rainbow tunnel,bead/block bands,large smooth balloon/cup patches,repetitive round micro-openings,stair-stepped small rims,broad plastic highlights,circular perforated centre plate. Weak readable black depth,nested flower filigree/resolved hierarchy. Visible lobe/aperture/colour changes do not establish convincing breathing/fold-over or temporal antialiasing. Reject,no promotion;do not re-view.
- Deep walk operation25.8544s overshot into Rush before fixture stopped:failure at deep settle assertion after1.4972s,paused+transition,reset[0,1.7,8],frame11/time8.5871000004,zero errors. NOT90s timeout or original45s exit acceptance. No deep PNGs;deep UNREVIEWED,sequence FAIL. Exact scheduling/input cause unproven. Preserve receipts/log/script;no unchanged rejected-candidate retry to fill missing pair. Next successor/capture must address real-input stopping under field/render cost;no injected state/shortcuts.
- close_centre_v30_visual.py validates2 image/receipt/protected/source hashes and failure,records review,then copies latest=inspected labelled ISOLATED v30 entry-motion. README/status/NOTES current;NOTES once,BOM retained,archive NOTES-before-centre-v30-visual.md. All live v25/trip18/HUD,defaults,manual/source ledgers,numerical evidence unchanged;old coarse-grid failure remains. No fidelity/unchanged desktop acceptance rerun. Next substantive rebuild;all19/source/coverage/route/full unfinished.
'''
notes_path.write_text(notes,encoding='utf-8-sig')
assert notes_path.read_bytes().startswith(b'\xef\xbb\xbf')
ast.parse(Path(__file__).read_text())
files=set(r['source_hashes'])|{PREFIX+'-receipts.json',PREFIX+'-review.md',
    'render-centre-v30.log','centre-v30-integrity.json',Path(__file__).name,
    'README.md','status.txt','NOTES.md','NOTES-before-centre-v30-visual.md','latest.png'}
for c in r['receipts']:files.update([c['file'],str(Path(c['file']).with_suffix('.json'))])
OUT.write_text(json.dumps({'integrity_passed':True,'visual_capture_sequence_passed':False,
    'valid_entry_temporal_pair':True,'entry_grade':'GAME','deep_grade':'UNREVIEWED; no capture',
    'candidate_rejected':True,'candidate_promoted':False,'overall_passed':False,
    'failure':failure,'errors':r['errors'],'live_sources_ledgers_and_defaults_unchanged':True,
    'latest_display_only':{'previous_sha256':old_latest,'copied_from':new_latest,'sha256':digest('latest.png')},
    'image_inspection':'Both new completed PNGs viewed once after renderer exit; no old image re-view',
    'files':{n:digest(n) for n in sorted(files)}},indent=2)+'\n')
print('Closed v30 visual attempt: entry GAME/rejected; deep absent/sequence FAIL; labelled latest updated; live unchanged.')
