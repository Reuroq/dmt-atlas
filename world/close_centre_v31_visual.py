"""Close one inspected visual attempt; reject geometry, preserve controls/evidence."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import struct

HERE=Path(__file__).resolve().parent
PREFIX='diagnostic-centre-v31'
OUT=HERE/(PREFIX+'-integrity.json')
assert not OUT.exists()
def digest(n):return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
summary=read(PREFIX+'-receipts.json')
gate=read('centre-v31-integrity.json')
assert summary['passed'] and summary['protected_unchanged'] and not summary['errors']
assert summary['protected_before']==summary['protected_after']==gate['protected']
for hashes in [gate['protected'],gate['files'],summary['source_hashes']]:
    assert all(digest(n)==h for n,h in hashes.items())
receipts=summary['receipts']
assert len(receipts)==4
for r in receipts:
    assert digest(r['file'])==r['capture_sha256']
    assert read(Path(r['file']).with_suffix('.json'))==r
    assert struct.unpack('>II',(HERE/r['file']).read_bytes()[16:24])==(1200,800)
    d=r['capture_diagnostics']
    assert d['stage']=='chrysanthemum' and d['detail']=='high' and d['paused']
    assert not d['renderPending'] and not d['transition'] and not d['missingEvidence']
    assert d['uncitedMeshes']==0 and d['animTime']==d['renderedAnimTime']
    assert r['settle_seconds']<=90 and r['veil_opacity']==0 and not r['errors']
for a,b in [(receipts[0],receipts[1]),(receipts[2],receipts[3])]:
    da,db=a['capture_diagnostics'],b['capture_diagnostics']
    assert all(da[k]==db[k] for k in ['position','yaw','pitch','stage','detail'])
    assert db['animTime']-da['animTime']>=3
walk=next(t for t in summary['timings'] if 'polling_ms' in t)
assert walk['wall_seconds']<45 and walk['polling_ms']==50
assert -8<=walk['after_release_pause']['position'][2]<=-6
reasons={
    'entry':'Sparse broad rainbow ribbons/spokes and a tiny central star; huge empty black wedges; smooth colour ramps dominate, very little resolved nested branch or curled-petal detail; reads as a flat pinwheel/screensaver, not an immersive folding flower.',
    'entry-motion':'Spokes rotate/bend and bands change, but the same sparse pinwheel dominates. Thin sharp slivers, broad featureless strips and weak depth/material cues; no convincing recursive fold-over.',
    'deep':'Closer pose enlarges smooth radial strips around the same small star. Still overwhelmingly empty wedges; apparent nesting is a few needle-like side strips, not dense flower hierarchy or jewelled detail.',
    'deep-motion':'Curves and colour bands shift, but flat ribbon spokes/large empty wedges remain. No persuasive chrome/jewel material, spatial enclosure or overwhelming nested detail.'}
grades=[]
for r,label in zip(receipts,['entry','entry-motion','deep','deep-motion']):
    grades.append({'file':r['file'],'sha256':r['capture_sha256'],'inspections':1,
        'inspection_method':'view_image once after renderer exit0','grade':'GAME','reasons':reasons[label]})
review={'question':'Would someone who has had this experience recognise this, or does it read as a game?',
    'answer':'It reads as a sparse procedural pinwheel/screensaver. GAME; rebuild.',
    'overall_grade':'GAME','rejected':True,'promotion':False,'frames':grades,
    'temporal_grade':'GAME','temporal_observation':'Visible bending/rotation and colour changes at fixed poses, but no convincing recursive unfolding. Two separated stills do not prove smooth continuous motion or temporal antialiasing.',
    'capture_gate_passed':True,'source_or_coverage_credit':False,
    'control_result':'Native W stopped at z-6.02048000183107 in4.4033088023s, timer polling50ms; no transition. Successful changed fixture, not full navigation/exit acceptance or proof of v30 failure cause.',
    'cost':'All four HIGH1200x800 settled42.8501–47.6407s under90s. Temporal pair wall92.9307/87.6591s including controls/rendering; not hardware-GPU/smooth-motion evidence.',
    'next':'v32 must abandon sparse global radial-fin topology: build locally nested curled/branching petal volumes with overlapping depth and resolved geometric hierarchy, separated by readable narrow black openings. Not recolouring, widening these ribbons, tiny decorative holes or revisiting rejected bands. Validate changed field, then fresh HIGH temporal inspection.'}
(HERE/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n')
md='''# v31 visual attempt — REJECTED / GAME

All four fresh1200×800 HIGH captures were inspected exactly once after renderer
exit0. They read as sparse rainbow ribbon spokes / a flat pinwheel screensaver,
not a recognisable densely unfolding chrysanthemum. Large empty black wedges
replace the required resolved flower hierarchy. The centre is a small star;
broad smooth colour ramps and needle-like strips have weak spatial/material cues.
The shader's numerical6/18/54 hierarchy is not convincing visible nested detail.

| Frame | Grade | Main failure |
| --- | --- | --- |
| entry | GAME | Sparse spokes, tiny star, huge void wedges, flat rainbow ramps |
| entry-motion | GAME | Same pinwheel with bent/rotated strips; little recursive unfolding |
| deep | GAME | Larger smooth strips; little depth, enclosure or nested petal detail |
| deep-motion | GAME | Changed curves/colour, still sparse and flat; weak jewel/chrome cues |

Visible changes across3.1666/3.0666animation seconds at identical respective
poses do not establish convincing fold-over, continuous smoothness or temporal
antialiasing. Both temporal pairs remain GAME. No source/coverage credit is
granted merely because the background is now black. Rebuild; no promotion.

## What passed (and what did not)

The capture sequence passes:zero browser errors,settled frames,veil0,zero missing
evidence/uncited meshes. Entry[0,1.7,8],deep[0,1.7,−6.02048000183107],HIGH,
paused,no transition. Times3.1475/6.3141/6.8308/9.8974,frames4/8/10/14.
Settles47.6406/47.0131/42.8501/44.2981seconds,all under unchanged90s.
Pair wall92.9307/87.6591seconds includes controls and GPU settling; these are
SwiftShader results, not hardware-GPU speed or a smooth-animation claim.

Changed real-input fixture passes its stop in4.4033seconds using native W,
50ms read-only timer polling, immediate release then native Space pause.
This removes the RAF-observer dependency and worked in this run. It does not
prove the exact cause of preserved v30 overshoot, general stopping reliability,
or the original45s physical-exit/full navigation acceptance. Live controls unchanged.

All numerical evidence, original failures, default images and source/manual
ledgers remain immutable. No fidelity or unchanged desktop acceptance rerun.
latest.png is now the inspected, labelled ISOLATED v31 deep-motion diagnostic;
it is not live geometry. Live v25/trip18/HUD remains unchanged.

## Exact next

Do not rerender/re-view rejected v31. Build substantive v32: abandon the sparse
global radial-fin topology for locally nested curled/branching petal volumes,
overlapping in depth with resolved geometric hierarchy and readable narrow black
openings. Not recolouring/widening these ribbons or adding decorative tiny holes.
Retain independent field/bounds checks and native timer-observed capture controls;
then inspect fresh HIGH entry/deep pairs under unchanged limits. All19 realism,
remaining16 source gates,coverage,route/full acceptance remain unfinished.
'''
(HERE/(PREFIX+'-review.md')).write_text(md)
shutil.copyfile(HERE/receipts[-1]['file'],HERE/'latest.png')
readme=HERE/'README.md'
text=readme.read_text()
start=text.index('latest.png now shows the freshly inspected1200×800 **ISOLATED v30 diagnostic**,')
end=text.index('\nOld full defaults',start)
text=text[:start]+'''latest.png now shows the inspected1200×800 **ISOLATED v31 deep-motion diagnostic**,
not live geometry. **V31 is rejected, GAME** in all four fresh entry/deep frames:
sparse flat rainbow ribbon spokes,large empty black wedges,tiny central star,
weak spatial/material cues and almost no resolved nested flower detail.
Both temporal pairs change visibly but remain GAME. No promotion or source/
coverage credit. See [v31 visual review](diagnostic-centre-v31-review.md).

The new capture sequence passed:four HIGH frames settled42.85–47.64s under90s,
zero browser errors;native timer-observed deep walk stopped at z−6.02048 in4.4033s.
That is a successful fixture run,not full acceptance or proof of v30's overshoot
cause. V30 remains rejected and its failure is preserved. The numerical v31
checks also remain passed;they do not imply visual realism or hardware-GPU speed.
See [numerical evidence](centre-v31-numerical-review.md).

Next:substantive v32 locally nested curled/branching petal volumes with depth
and resolved detail,not a recoloured/widened radial pinwheel. Live v25/trip18/HUD,
source/manual ledgers and all previous failed evidence remain unchanged.
'''+text[end:]
readme.write_text(text)
(HERE/'status.txt').write_text('Isolated v31 REJECTED GAME:all4 fresh1200x800 HIGH entry/deep frames sparse flat rainbow ribbon spokes,large empty black wedges,tiny star,weak depth/material/nested detail. Capture PASS,zero errors,settles42.85–47.64s<90s,pairs3.1666/3.0666anim seconds. Native timer-observed deep stop z-6.02048 in4.4033s PASS;not full exit acceptance or v30 cause proof. latest.png=inspected labelled v31 deep-motion diagnostic. Live v25/trip18/HUD,defaults/ledgers unchanged,no promotion. Next substantive v32 local nested curled-petal volumes,not radial ribbons;all19/source/coverage/route/full unfinished.\n')
notes_path=HERE/'NOTES.md'
original=notes_path.read_bytes()
archive=HERE/'NOTES-before-centre-v31-visual.md'
assert not archive.exists()
archive.write_bytes(original)
lines=original.decode('utf-8-sig').splitlines()
lines[0]='# Active: REDIRECT4 — v31 REJECTED GAME; capture/deep stop PASS; NEXT substantive v32'
for i,line in enumerate(lines):
    if line.startswith('2. v30 remains REJECTED GAME,'):
        lines[i]='2. v31 visual phase CLOSED,REJECTED:all4 fresh HIGH entry/deep frames GAME,inspected ONCE;never re-view/rerender. Capture/deep stop PASS (below),no live promotion. Exact next substantive v32:abandon sparse global radial-fin topology for locally nested curled/branching petal volumes,overlapping depth,resolved hierarchy and readable narrow black openings;not recolouring/widening ribbons or tiny decorative holes. Validate changed field/bounds,then fresh HIGH entry/deep pairs. Preserve native timer-observed capture and all limits. v30 overshoot cause remains unproven.'
notes='\n'.join(lines)+'\n\n'+'''## Closed v31 visual attempt — REJECTED; no replay
- render_centre_v31.py ONCE exit0:all4 HIGH1200x800 entry/deep temporal frames captured,zero errors,settled,veil0,zero missingEvidence/uncited. Entry[0,1.7,8],deep[0,1.7,−6.02048000183107],yaw/pitch0,paused,no transition. Times3.1475/6.3141/6.8308/9.8974,frames4/8/10/14,settles47.6406/47.0131/42.8501/44.2981s<90s. Same-pose pairs3.1666/3.0666anim seconds,wall92.9307/87.6591s including controls/rendering. Not smoothness/temporalAA/hardware-GPU proof.
- diagnostic-centre-v31-entry.png/-entry-motion.png/-deep.png/-deep-motion.png each inspected exactly ONCE after exit0. ALL GAME:very sparse flat rainbow ribbon spokes/pinwheel,huge empty black wedges,tiny central star,broad smooth colour ramps,needle-like side strips/hard cuts,weak depth/enclosure/jewel-chrome cues,little resolved nested flower hierarchy. Numerical6/18/54 levels do not read as recursive geometry. Visible bending/rotation/colour change does not establish convincing unfolding. Reject,no promotion,no source/coverage credit merely for black background.
- Changed real-input deep stop PASS4.4033088023s,z−6.02048000183107,50ms read-only timer polling,nativeW release then nativeSpace pause,no injected state. Successful THIS fixture run,not original45s exit/full acceptance/general reliability or proven cause of preserved v30 overshoot. Keep changed timer-observed fixture for successor;no unchanged replay.
- close_centre_v31_visual.py ONCE verifies4 receipts/PNGs/numerical/source/protected hashes,records review,json/integrity,latest=inspected labelled ISOLATED v31 deep-motion. README/status current;NOTES once,BOM retained,archive NOTES-before-centre-v31-visual.md. Live v25/trip18/HUD,defaults/manual/source ledgers and numerical evidence unchanged. No fidelity/unchanged desktop acceptance rerun. Exact next substantive v32 local nested curled-petal volumes with depth/resolved hierarchy,not globally sparse radial ribbons or recolouring;all19/source/coverage/route/full unfinished.
'''
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
protected={n:h for n,h in gate['protected'].items() if n!='latest.png'}
assert all(digest(n)==h for n,h in protected.items())
assert digest('latest.png')==receipts[-1]['capture_sha256']
ast.parse((HERE/Path(__file__).name).read_text())
files=[Path(__file__).name,'render_centre_v31.py','render-centre-v31.log','centre-v31-integrity.json',
    PREFIX+'.html',PREFIX+'-receipts.json',PREFIX+'-review.json',PREFIX+'-review.md']
files += [n for r in receipts for n in [r['file'],str(Path(r['file']).with_suffix('.json'))]]
OUT.write_text(json.dumps({'integrity_passed':True,'capture_gate_passed':True,'visual_grade':'GAME',
    'rejected':True,'promotion':False,'protected':protected,'files':{n:digest(n) for n in files},
    'display':{'latest.png':digest('latest.png'),'source':receipts[-1]['file'],'diagnostic_only':True},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md',archive.name]}},indent=2)+'\n')
print('v31 visual closure:4 GAME,rejected;capture/deep stop PASS;latest labelled diagnostic;live/defaults/ledgers unchanged.')
