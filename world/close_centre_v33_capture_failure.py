"""One-shot closure of the actual90s HIGH entry-settle failure; no replay."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
PREFIX='diagnostic-centre-v33'
OUT=HERE/(PREFIX+'-integrity.json')
assert not OUT.exists()
def digest(n):return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
s=read(PREFIX+'-receipts.json')
gate=read('centre-v33-integrity.json')
assert gate['integrity_passed'] and gate['numeric_passed']
assert not s['passed'] and s['protected_unchanged'] and not s['errors']
assert s['receipts']==[] and not list(HERE.glob(PREFIX+'*.png'))
assert s['protected_before']==s['protected_after']==gate['protected']
for hashes in [gate['protected'],gate['files'],s['source_hashes']]:
    assert all(digest(n)==h for n,h in hashes.items())
failure=s['failure'];d=failure['diagnostics']
assert failure['operation']=='entry settle' and 'Timeout 90000ms exceeded' in failure['exception']
assert d['stage']=='chrysanthemum' and d['detail']=='high' and d['paused']
assert d['renderPending'] and not d['transition']
assert d['position']==[0,1.7,8] and d['yaw']==d['pitch']==0
assert not d['missingEvidence'] and d['uncitedMeshes']==0
assert digest('latest.png')==digest('diagnostic-centre-v32-deep-motion.png')
next_work=('Build an isolated v33r2 conservative reach optimization preserving the v33 scalar '
    'zero set and materials. Exploit nonnegative squared-shell/angular/axial costs: '
    'derive smoother lower-bound leaves by omitting nonnegative costs, then MAX '
    'their certified positive reaches with the existing full-leaf reach. Keep '
    'union MIN/intersection MAX,clearance,2048/1536 budgets,14bisections,.00015 '
    'residual,directional-depth gate and no minimum step. Independently validate '
    'the changed marcher and measure saved-ray cost before a fresh1200x800 HIGH '
    'attempt with unchanged90s waits. No unchanged v33 replay.')
reason=(f'First HIGH entry-settle wait timed out after {failure["operation_wall_seconds"]:.6f}s '
    'under the unchanged90000ms limit. No screenshot was reached; zero NEW PNGs. '
    'Failure diagnostics:paused HIGH chrysanthemum,entry[0,1.7,8],yaw/pitch0, '
    f'frame{d["frames"]},time/rendered{d["animTime"]},renderPending=true, '
    'no transition,missingEvidence or uncited meshes. Zero recorded browser errors.')
review={'capture_gate_passed':False,'visual_grade':'UNREVIEWED','promotion':False,
    'diagnostic_only':True,'failure':failure,'new_images':0,'inspections':0,
    'reason':reason,'next_work':next_work,
    'limits':'Actual SwiftShader settling failure,not a hardware-GPU benchmark or established profiling diagnosis. No image/temporal judgement,source/coverage credit,physical-exit or full acceptance claim.'}
md='# v33 capture attempt — FAIL; visually UNREVIEWED\n\n'+reason+'\n\n'
md+='''Would someone who has had this experience recognise this, or does it read as a game?

Not graded: no completed image or temporal pair. Do not infer appearance from
numerical checks. Entry motion,deep walk,deep pair were not reached.

render_centre_v33.py ran ONCE,exit1. The failure receipt and log are preserved.
The larger sparse-ray cost documented in the numerical phase is consistent
with expensive settling,but this is not a profiling proof of the exact cause.
No timeout,resolution,root tolerance or control guard was relaxed.

Numerical checks remain passed,not full-resolution acceptance. Live v25/trip18/
HUD,default captures,source/manual ledgers and prior evidence are unchanged.
latest.png remains the inspected,labelled ISOLATED REJECTED GAME v32 deep-motion
diagnostic; it does not depict v33. No old PNG was re-viewed.

## Next

'''+next_work+'\n\nAll19 realism targets,remaining16 source gates,coverage,route and full acceptance remain open.\n'
notes_path=HERE/'NOTES.md';original=notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive=HERE/'NOTES-before-centre-v33-capture.md'
assert not archive.exists()
readme_path=HERE/'README.md';readme=readme_path.read_text()
start=readme.index('Isolated **v33 closed tapered/curled petal cells** now pass')
end=readme.index('\nOld full defaults',start)
replacement='''Isolated **v33 closed tapered/curled petal cells** pass numerical checks but
**FAIL the first HIGH capture's90s settling gate**. No PNG was saved; appearance
is **UNREVIEWED**,no promotion. Paused entry remained renderPending=true with
zero recorded browser errors. Sparse-ray mean steps rose67.64→586.19.
See [v33 capture failure](diagnostic-centre-v33-review.md) and
[numerical review](centre-v33-numerical-review.md).

Next:isolated v33r2 conservative lower-bound reach optimization preserving
the petal zero set;independent validation before another HIGH attempt.
Original1200x800/90s/root limits stay unchanged. No v33 replay,new image or
source/coverage credit;live/defaults/ledgers and latest v32 diagnostic unchanged.
'''
assert (HERE/'status.txt').read_text().startswith('Isolated v33 closed tapered/curled parent+child petal cells NUMERICAL PASS:')
lines=original.decode('utf-8-sig').splitlines()
lines[0]='# Active: REDIRECT4 — v33 HIGH CAPTURE FAIL90s / UNREVIEWED; NEXT isolated reach optimization'
idx=next(i for i,line in enumerate(lines) if line.startswith('2. v33 closed petal-cell numerical phase COMPLETE;'))
lines[idx]='2. v33 capture phase CLOSED:entry HIGH settle timeout90s,zero PNGs,visually UNREVIEWED. No replay. Exact next:isolated v33r2 nonnegative-cost lower-bound reach optimization preserving scalar zero set;independent numerical validation before unchanged1200x800 HIGH/90s capture.'
notes='\n'.join(lines)+'\n\n## Closed v33 HIGH capture attempt — FAIL90s; no replay\n'
notes+='- render_centre_v33.py ONCE exit1. '+reason+' Entry motion/deep controls never reached;no visual/temporal grade.\n'
notes+='- close_centre_v33_capture_failure.py ONCE binds log,receipt,numerical/source/protected hashes and unreviewed failure report. README/status updated;NOTES once,BOM preserved,archive NOTES-before-centre-v33-capture.md. No new PNG/inspection;latest still labelled inspected REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults,ledgers/evidence unchanged;no fidelity/unchanged acceptance rerun.\n'
notes+='- High numerical cost is consistent with timeout,not exact cause/profiling or hardware-GPU proof. Numerical PASS retained,full-resolution gate FAIL. Next:'+next_work+' All19/source/coverage/route/full unfinished;no completion marker.\n'
ast.parse((HERE/Path(__file__).name).read_text())
(HERE/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n')
(HERE/(PREFIX+'-review.md')).write_text(md)
readme_path.write_text(readme[:start]+replacement+readme[end:])
(HERE/'status.txt').write_text('Isolated v33 HIGH CAPTURE FAIL:first entry settle timeout90.0071s at unchanged90000ms,renderPending=true,zero recorded browser errors;zero PNGs,visually UNREVIEWED,no promotion. Numerical PASS retained,not full-resolution acceptance. Next isolated v33r2 nonnegative-cost lower-bound reach optimization preserving petal zero set;independently validate before original1200x800 HIGH/90s retry with changed marcher. No unchanged v33 replay. latest.png remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
archive.write_bytes(original)
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
assert all(digest(n)==h for n,h in gate['protected'].items())
files=[Path(__file__).name,'render_centre_v33.py','render-centre-v33.log',
    'centre-v33-integrity.json',PREFIX+'.html',PREFIX+'-receipts.json',
    PREFIX+'-review.json',PREFIX+'-review.md']
OUT.write_text(json.dumps({'integrity_passed':True,'capture_gate_passed':False,
    'visual_grade':'UNREVIEWED','promoted':False,'new_images':0,
    'protected':gate['protected'],'files':{n:digest(n) for n in files},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md',archive.name]},
    'next':next_work},indent=2)+'\n')
print('v33 capture failure closure PASS:90s timeout preserved,zero PNGs,UNREVIEWED;live/defaults/ledgers/latest unchanged.')
