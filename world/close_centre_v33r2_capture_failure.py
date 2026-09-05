"""Close the single failed HIGH capture without changing any acceptance limit."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
PREFIX='diagnostic-centre-v33r2'
OUT=HERE/(PREFIX+'-integrity.json')
assert not OUT.exists()
def digest(n):return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
s=read(PREFIX+'-receipts.json');gate=read('centre-v33r2-integrity.json')
assert gate['integrity_passed'] and gate['numeric_passed']
assert not s['passed'] and s['protected_unchanged'] and not s['errors']
assert not s['receipts'] and not list(HERE.glob(PREFIX+'*.png'))
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
next_work=('Build an isolated v33r3 two-tier conservative marcher preserving the v33 zero set/materials. '
    'First evaluate cheap f/axial-only lower-leaf certificates, omitting shell/angular construction; '
    'skip full field evaluation only when all union components certify a useful positive free segment, '
    'with the same intersection MAX/union MIN and .4 reach cap. Reset sign-bracket history only on '
    'certified-free skips, as for the existing envelope. Otherwise use the unchanged v33r2 full path '
    'and acceptance. Preserve clearance,2048/1536 budgets,14bisections,residual/directional tolerances '
    'and no minimum step. Independently validate the changed marcher,including actual failed clock '
    '4.895 alongside existing grids/clocks,and measure cheap/full evaluation counts and saved-ray '
    'cost before any new original1200x800 HIGH/90s attempt. This plan is unvalidated,not a proven '
    'performance diagnosis or fix. Do not replay unchanged v33/v33r2 captures.')
reason=(f'First HIGH entry settle timed out after {failure["operation_wall_seconds"]:.6f}s '
    'under unchanged90000ms. Zero PNGs; no visual/temporal review. Paused HIGH entry[0,1.7,8], '
    f'yaw/pitch0,frame{d["frames"]},time/rendered{d["animTime"]},renderPending=true, '
    'no transition,missingEvidence or uncited meshes;zero recorded browser errors.')
review={'capture_gate_passed':False,'visual_grade':'UNREVIEWED','promotion':False,
    'diagnostic_only':True,'failure':failure,'new_images':0,'inspections':0,
    'reason':reason,'next_work':next_work,
    'limits':'SwiftShader settling failure,not a hardware-GPU benchmark or exact profiling diagnosis. No source/coverage,temporal,physical-exit or full acceptance credit.'}
md='# v33r2 HIGH capture — FAIL90s; visually UNREVIEWED\n\n'+reason+'\n\n'
md+='''Would someone who has had this experience recognise this, or does it read as a game?

Not graded: no completed image or temporal pair. Entry motion,deep walk and
deep pair were not reached. render_centre_v33r2.py ran ONCE,exit1;failure receipt
and log preserved. No resolution,timeout,root tolerance or control guard changed.

The numerical checks remain passed. Saved sparse-ray improvement586.19→166.92
mean steps and.969→.416s median readback did not establish full-resolution
settling. The fresh original gate still fails. This is not an exact attribution
to shader compilation,per-pixel cost,ray tails,or a hardware-GPU performance test.

Live v25/trip18/HUD,defaults,source/manual ledgers and numerical evidence stay
unchanged. latest.png remains the inspected labelled REJECTED GAME v32 deep-motion
diagnostic;it does not depict v33 or v33r2. No old image was re-viewed.

## Next

'''+next_work+'\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain open.\n'
notes_path=HERE/'NOTES.md';original=notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive=HERE/'NOTES-before-centre-v33r2-capture.md';assert not archive.exists()
readme_path=HERE/'README.md';readme=readme_path.read_text()
start=readme.index('Isolated **v33r2 reach-only optimization now passes numerical validation**:')
end=readme.index('\n\nOld full defaults',start)
replacement='''Isolated **v33r2 reach-only optimization passes numerical checks but also
FAILS the original HIGH90s entry settling gate** (90.0097s). Zero PNGs and
recorded browser errors;visually **UNREVIEWED**,no promotion. The sparse-ray
cost reduction did not establish full-resolution acceptance. See
[v33r2 numerical review](centre-v33r2-numerical-review.md) and
[v33r2 capture failure](diagnostic-centre-v33r2-review.md).
Next:isolated v33r3 cheap certified-free fast path before expensive full-field
evaluation,with independent validation/cost measurement before another original
HIGH/90s attempt. No unchanged v33/v33r2 replay;zero-set,root/control limits,
live/defaults/ledgers and latest v32 diagnostic remain unchanged.'''
assert (HERE/'status.txt').read_text().startswith('Isolated v33r2 REACH NUMERICAL PASS:')
lines=original.decode('utf-8-sig').splitlines()
lines[0]='# Active: REDIRECT4 — v33r2 HIGH CAPTURE FAIL90s / UNREVIEWED; NEXT isolated two-tier marcher'
idx=next(i for i,line in enumerate(lines) if line.startswith('2. v33r2 isolated reach-only numerical phase COMPLETE;'))
lines[idx]='2. v33r2 HIGH capture phase CLOSED:entry settle timeout90.0097s,zero PNGs,visually UNREVIEWED. No replay. Exact next:isolated v33r3 cheap axial-only certified-free fast path,independently validate/measure before original1200x800 HIGH/90s capture.'
notes='\n'.join(lines)+'\n\n## Closed v33r2 HIGH capture attempt — FAIL90s; no replay\n'
notes+='- render_centre_v33r2.py ONCE exit1. '+reason+' Entry motion/deep controls never reached;no visual/temporal grade.\n'
notes+='- Numerical PASS and lower sparse-ray cost retained,but full-resolution gate FAIL. No exact profiling diagnosis or hardware-GPU claim. close_centre_v33r2_capture_failure.py ONCE binds log,receipt,numerical/source/protected hashes and failure review. README/status updated;NOTES once,BOM preserved,archive NOTES-before-centre-v33r2-capture.md. No new PNG;latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers/evidence unchanged;no fidelity/unchanged acceptance rerun.\n'
notes+='- Exact next:'+next_work+' All19/source/coverage/route/full unfinished;no completion marker.\n'
for suffix in ['-review.md','-review.json']:assert not (HERE/(PREFIX+suffix)).exists()
(HERE/(PREFIX+'-review.md')).write_text(md)
(HERE/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n')
readme_path.write_text(readme[:start]+replacement+readme[end:])
(HERE/'status.txt').write_text('Isolated v33r2 HIGH CAPTURE FAIL:entry settle timeout90.0097s under unchanged90000ms,renderPending=true,zero recorded browser errors;zero PNGs,visually UNREVIEWED,no promotion. Numerical PASS/sparse-ray speedup retained,not full-resolution acceptance. Next isolated v33r3 cheap axial-only certified-free fast path before full-field evaluation;independently validate/measure including failed clock4.895 before original1200x800 HIGH/90s attempt. No unchanged v33/v33r2 replay. latest.png remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
archive.write_bytes(original)
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
assert all(digest(n)==h for n,h in gate['protected'].items())
files=[Path(__file__).name,'render_centre_v33r2.py','render-centre-v33r2.log',
    PREFIX+'.html',PREFIX+'-receipts.json',PREFIX+'-review.md',PREFIX+'-review.json',
    'centre-v33r2-integrity.json']
OUT.write_text(json.dumps({'integrity_passed':True,'capture_gate_passed':False,
    'visual_grade':'UNREVIEWED','promotion':False,'new_images':0,
    'protected':gate['protected'],'files':{n:digest(n) for n in files},
    'numerical_files':gate['files'],'display':{n:digest(n) for n in ['README.md','status.txt','NOTES.md','latest.png']},
    'next':next_work},indent=2)+'\n')
print('v33r2 capture failure closure PASS;zero PNGs,visually UNREVIEWED,no live changes;next isolated two-tier marcher.')
