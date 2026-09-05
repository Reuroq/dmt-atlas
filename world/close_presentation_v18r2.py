"""Close the inconclusive diagnostic without converting its pass into a repair."""
import ast
import hashlib
import json
from pathlib import Path
from fidelity import render_signature

HERE=Path(__file__).resolve().parent
OUT=HERE/'presentation-v18r2-integrity.json'
assert not OUT.exists()
def digest(n):return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
old=json.loads((HERE/'input-pump-v18-integrity.json').read_text())
for n,h in old['files'].items():assert digest(n)==h,n
for n,h in old['preserved'].items():assert digest(n)==h,n
prefix='diagnostic-presentation-v18r2'
receipt=json.loads((HERE/(prefix+'.json')).read_text())
assert receipt['render_signature']==render_signature()==old['render_signature']
assert receipt['capture_sha256']==digest(prefix+'.png')
assert len(receipt['checks'])==6 and not receipt['errors']
d=receipt['capture_diagnostics']
assert d['paused'] and d['reduced'] and d['detail']=='high'
assert not d['transition'] and not d['renderPending'] and not d['missingEvidence'] and d['uncitedMeshes']==0
assert d['renderedAnimTime']==d['animTime'] and d['position']==[0,1.7,8]
traces=sorted(HERE.glob(prefix+'-*-trace.json'))
assert len(traces)==4
for f in traces:
    p=json.loads(f.read_text())
    assert p['changed_pixels']==0 and not p['browser_errors']
    assert all(q['alpha_extrema']==[0,0] for q in p['canvas_copies'])
    assert p['render_signature']==render_signature()
    for k in ['position','animTime','renderedAnimTime','frames','detail']:
        assert p['before'][k]==p['settled'][k]==p['after'][k]
    assert not p['after']['renderPending']
(HERE/'latest.png').write_bytes((HERE/(prefix+'.png')).read_bytes())

readme=HERE/'README.md';s=readme.read_text()
start=s.index('latest.png shows the newly inspected **1000×380 failed-comparison AFTER crop**,')
end=s.index('The four graded temporal frames remain',start)
s=s[:start]+'''A new isolated presentation diagnostic passed all six screenshot/detail/Sources
checks, but its Canvas2D copies were fully transparent: it did not capture the
rendered framebuffer and **does not explain or clear the original failure**.
No runtime repair or visual regrade. See [diagnostic review](presentation-v18r2-review.md).
Next: instrument submission-time framebuffer bytes before browser presentation.

latest.png now shows the inspected1200×800 **isolated presentation diagnostic**,
still GAME (broad smooth colour bands, small clover centre, sparse detail and
smeared highlights). The failed v18 pair remains preserved. Old full defaults
visual-chrysanthemum.png/json remain unchanged and stale.
'''+s[end:];readme.write_text(s)
(HERE/'status.txt').write_text('Live visual v25 / trip v18 unchanged. Navigation repair remains PASS (centre-0.075,exit9.41s/45s,all8 reduced controls). Original HIGH restored-detail pixel equality FAIL remains unresolved. New isolated presentation-v18r2 diagnostic passes all6 screenshot/detail/Sources checks but Canvas2D copies are transparent,so framebuffer comparison is invalid; NOT a repair. Next: submission-time framebuffer/PBO capture before presentation,strict equality unchanged. latest.png=new inspected1200x800 isolated diagnostic,GAME;failed pair and old full defaults preserved. Coverage84.7% FAIL,dark ABSENT,sources50/20,old grades stale. All19 realism,source/coverage/route/full acceptance unfinished.\n')

notes=HERE/'NOTES.md';s=notes.read_text(encoding='utf-8-sig')
s=s.replace('# Active: REDIRECT4 — live visual v25 / trip v18; navigation repaired, HIGH stillness FAIL','# Active: REDIRECT4 — live v25 / trip v18; HIGH failure unresolved, presentation probe inconclusive',1)
marker='## Exact next bounded work\n'
at=s.index(marker)
new='''## Completed isolated presentation diagnostic — inconclusive (do not replay)
- build_presentation_trace_v18.py failed nonunique replacement after JS/HTML output; attempted missing helper launch also failed. Preserve partial diagnostic-presentation-v18.js/html,initial builder,presentation-v18-build-failure.json and trace-presentation-v18.log. Corrected v18r2 builder uses unique second_seconds anchor; no runtime correction.
- trace_presentation_v18r2.py ran ONCE with original real controls,1200×800 HIGH,90s waits,800ms comparison interval and strict equality. Adds read-only RAF/submission/fence traces and Canvas2D copies AFTER screenshots,42–143ms overhead; may perturb timing. All6 screenshot/detail/Sources checks PASS,zero errors;four pixel comparisons identical,frame counts6/8/8/10. No repeated unchanged acceptance and no failure cleared.
- Every Canvas2D copy alpha[0,0],fully transparent: equal hashes are NOT framebuffer-colour evidence. Default preserveDrawingBuffer=false; this after-presentation copy cannot distinguish shader/MSAA output from browser composition. Reject method for that purpose;do not rerun unchanged or call it repaired. Original9457 one-bit pixel failure remains active and preserved.
- diagnostic-presentation-v18r2.png inspected exactly ONCE after exit0;do not re-view.1200×800 HIGH entry[0,1.7,8],paused/reduced,frame10,time/rendered6.295300000190739,settled,zero transition/veil/errors/missing evidence/uncited. GAME:broad smooth saturated bands,small clover centre,sparse hierarchy,smeared highlights,no convincing black openings. Single still,not temporal grade. latest.png now equals this labelled isolated diagnostic,not prior failed crop. Old full defaults and failed pair unchanged.
- presentation-v18r2-review.md/integrity.json bind all new sources/trace/receipt/image hashes plus initial build failure and preserved runtime/ledgers/defaults. Live trip-v18.js/continuum-v25.js unchanged;no fidelity/acceptance rerun or promotion. NOTES once this phase,BOM preserved.

'''
s=s[:at]+new+s[at:]
oldline='1. Diagnose failed HIGH stillness with NEW read-only instrumentation around real detail toggles: distinguish raw canvas/GL output from browser-composited screenshot/presentation and record render submission/fence/RAF receipts. Preserve failed pixel pair and strict equality. Do not add blind delays, retry unchanged helper, alter navigation or infer root cause from one-bit differences. Current helper frozen() is at render_visual.py94–127; compositor target/render code at fractal.js450/481; trip renderer antialias:true, default preserveDrawingBuffer, one GPU fence. No new corpus work needed.'
newline='1. Instrument SUBMISSION-TIME framebuffer capture around real detail toggles. Proposed WebGL2 PIXEL_PACK_BUFFER readPixels queued before existing fence,then getBufferSubData after retirement;restore buffer binding explicitly. Capture dimensions/frame/time,nonzero/alpha validity and byte hashes;tie browser screenshots to submitted bytes. This is not implemented or a proven fix. Do not repeat transparent after-presentation Canvas2D copies,change preserveDrawingBuffer/AA,add blind delays or loosen strict equality to hunt a pass. Preserve original failure and all probe evidence. Targeted helper frozen() render_visual.py94–127,compositor fractal.js450/481,trip frame/renderFence;no corpus work.'
assert s.count(oldline)==1;s=s.replace(oldline,newline)
notes.write_text(s,encoding='utf-8-sig')
files=['build_presentation_trace_v18.py','presentation-v18-build-failure.json','diagnostic-presentation-v18.js','diagnostic-presentation-v18.html','trace-presentation-v18.log','build_presentation_trace_v18r2.py','build-presentation-trace-v18r2.log','trace_presentation_v18r2.py','diagnostic-presentation-v18r2.js','diagnostic-presentation-v18r2.html','trace-presentation-v18r2.log',prefix+'.png',prefix+'.json','presentation-v18r2-review.md','README.md','status.txt','NOTES.md','latest.png',Path(__file__).name]+[f.name for f in traces]
for n in files:
    if n.endswith('.py'):ast.parse((HERE/n).read_text())
out={'integrity_passed':True,'diagnostic_screenshot_checks_passed':True,'valid_framebuffer_readback':False,'original_high_failure_resolved':False,'runtime_changed':False,'overall_passed':False,'render_signature':render_signature(),'files':{n:digest(n) for n in files},'preserved':old['preserved'],'inspected_once':prefix+'.png','latest_matches':digest('latest.png')==digest(prefix+'.png')}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['files','preserved']}))
