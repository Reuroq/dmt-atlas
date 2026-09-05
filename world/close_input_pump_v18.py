"""Bind control success and HIGH failure; update display and concise handoff once."""
import ast
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops
from fidelity import render_signature

HERE=Path(__file__).resolve().parent
OUT=HERE/'input-pump-v18-integrity.json'
assert not OUT.exists(), 'Preserve closed phase'
def digest(n):
    return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
promotion=json.loads((HERE/'input-pump-v18-promotion.json').read_text())
for n,h in promotion['files'].items():assert digest(n)==h,n
assert render_signature()==promotion['render_signature']
assert digest('trip.js')==digest('trip-v18.js')==digest('trip-v18-candidate.js')
for n,h in promotion['previous_protected'].items():
    if n not in ['trip.js','fidelity-data.js']:assert digest(n)==h,n
prefix='accessibility-input-pump-v18'
tracefiles=sorted(HERE.glob(prefix+'-*-trace.json'))
assert len(tracefiles)==4
for f in tracefiles:
    t=json.loads(f.read_text())
    assert t['render_signature']==render_signature()
    for state in ['before','settled','after']:
        d=t[state]
        assert not d['renderPending'] and d['animTime']==d['renderedAnimTime']
        for k in ['position','animTime','renderedAnimTime','frames','detail','paused','reduced']:
            assert d[k]==t['before'][k]
    assert t['changed_pixels']==(9457 if 'restored-detail' in f.name else 0)
stem=prefix+'-restored-detail-reduced-pixel-stillness-'
a=Image.open(HERE/(stem+'before.png')).convert('RGB')
b=Image.open(HERE/(stem+'after.png')).convert('RGB')
diff=ImageChops.difference(a,b)
assert a.size==b.size==(1000,380)
assert max(max(p) for p in diff.getdata())==1
assert diff.getbbox()==(411,277,1000,380)
assert not (HERE/(prefix+'.png')).exists(), 'Full capture was not reached'
assert 'AssertionError: restored-detail reduced pixel stillness: canvas changed' in (HERE/('render-'+prefix+'.log')).read_text()
assert not json.loads((HERE/'fidelity-results.json').read_text())['passed']
(HERE/'latest.png').write_bytes((HERE/(stem+'after.png')).read_bytes())

readme=HERE/'README.md'
s=readme.read_text()
start=s.index('The isolated v17 movement-clock candidate now passes')
end=s.index('The four graded temporal frames remain',start)
s=s[:start]+'''The tested navigation repair is now live as **trip v18** (visual renderer v25).
A demand-driven held-input timer avoids multi-second RAF pose jumps without
discarding held time. The unchanged combined HIGH control gate passes: centre
return x−0.075, physical exit9.41s under45s, Sources/boundary/drag-look pass.
All eight reduced-mobile control/idle cases pass. Historical v16/v17 failures remain.
See [repair and adverse-result review](input-pump-v18-review.md).

The fresh post-promotion HIGH stillness run **FAILED** restored-detail reduced
pixel equality:9457 crop pixels changed by at most one channel value, despite
identical pose/clock/frame and settled receipts. Prior three pixel comparisons
passed; Sources/full capture were not reached. Cause unresolved; no tolerance
relaxed or unchanged rerun. Next: instrument canvas versus presentation timing.
All old visual/full-acceptance receipts are now stale; overall remains false.

latest.png shows the newly inspected **1000×380 failed-comparison AFTER crop**,
not a full-size capture or passing visual result. It remains GAME (smooth broad
colour folds, sparse hierarchy, smeared highlights). The original failed pair,
all traces and log are preserved. visual-chrysanthemum.png/json retain the old,
now-stale full-size accessibility-v25 entry; they were not overwritten.
'''+s[end:]
readme.write_text(s)
(HERE/'status.txt').write_text('Live visual v25 / trip v18: navigation repair promoted after original combined HIGH controls PASS (centre x-0.075, exit9.41s/45s) and all8 reduced-mobile controls/idle PASS. Post-promotion HIGH restored-detail pixel stillness FAIL:9457 crop pixels differ by max1 channel despite identical pose/clock/frames and settled receipts; cause unresolved, Sources/full capture not reached. Next: instrument canvas readback versus browser presentation; no loosened equality or unchanged rerun. latest.png is inspected failed AFTER crop1000x380, GAME, not full capture. Prior full defaults/grades remain stale; live coverage84.7% FAIL,dark ABSENT,sources50/20. Structural successor,other18 realism targets,sixteen source gates,route/full acceptance unfinished. Historical failures preserved.\n')

notes=HERE/'NOTES.md'
archive=HERE/'NOTES-before-input-pump-v18.md'
assert not archive.exists()
archive.write_bytes(notes.read_bytes())
notes.write_text('''# Active: REDIRECT4 — live visual v25 / trip v18; navigation repaired, HIGH stillness FAIL

## Rules / authority
- Read REDIRECT4/3/2, continue all19 RECOGNISE plus every source/coverage/route/full acceptance gate. No completion marker yet. Every GAME/CLOSE requires rebuilding; numerical and descriptor passes are not realism.
- Linux /home/clawd/dmt-atlas; all writes world/; no git, agents, background services, web searches, GUI or downloads. Targeted bounded rg before selected ranges; no corpus/atlas re-exploration. NOTES once per phase, preserve BOM. Detailed prior notes archived verbatim in NOTES-before-input-pump-v18.md; search selected entries only.
- Headless Chromium/SwiftShader: PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. Existing numpy/PIL environment if needed: PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages. Direct file:// works with bundled Three0.160.1/data. No screen.cmd here; view_image each NEW completed image exactly once. Never re-view historical PNGs or replay completed one-shot builders/reviews. Wait for renderer exit before inspecting PNG/JSON.
- Real keyboard/touch/drag/buttons only. journeyDiagnostics() read-only: no injected pose, input, route or clocks. Preserve strict pixel equality, centre tolerance−3.2..0, original45s exit, full-resolution1200×800 HIGH and90s settled waits. No unchanged desktop acceptance reruns.

## Current navigation phase (closed; preserve evidence)
- diagnostic-lateral-v17.json reproduces x−4 failure: native left press handled9920.4ms, next RAF17053.6ms integrates7.1332s and jumps x4→−4. Centre observer17062.1, release17064.9; native delivery about.2/.3ms. Crossing render submission.5ms JS. Failure precedes release; not seconds-long keyup latency. Instrument trace `native-after` name is misleading: that listener runs BEFORE app handlers; use `native-before` and move-before/after. Do not rerun unchanged trace.
- build_input_pump_v18.py creates trip-v18-candidate.js from isolated v17 monotonic movement repair. Demand-driven16ms navigation timer while eligible input held; at most one pending timer, no GL calls. Shared performance.now clock with RAF and event flushes retains all held time without duplication. Collision substeps≤.05, speed/bounds/portals unchanged; animation/paced/transition cap1 unchanged. No smooth GPU rendering claim.
- verification-input-pump-v18.json/log PASS original1000×700 HIGH combined gate: Sources/right boundary/drag-look, centre x−.0745600006, real physical exit9.409652426s under unchanged45000ms to cited Rush; zero errors. verification-idle-pump-v18.json/log PASS all8 unchanged reduced-mobile LOW keyboard/touch/look/stages/being/Sources/motion/pause/restart cases, exact idle pose/clock/frames and settled receipts,zero errors. No full acceptance claim. Isolated tests bind candidate hash, not their base-live signature alone.
- promote_input_pump_v18.py ran ONCE: verified prior protected/evidence hashes and promoted identical trip-v18-candidate.js→trip-v18.js/trip.js. input-pump-v18-promotion.json binds tests/hash and new signature. JS syntax/Python AST pass. Live continuum.js remains v25; trip-v16.js and failed candidate v17 immutable. Existing render invalidation, one GPU frame in flight and inactive-state semantics retained.
- fidelity.py --check regenerated outputs, expected exit1 overall false. Old visual/acceptance receipts stale after trip signature change; grade ledgers/source decisions unchanged. Do not re-run just to get another fail. No current full acceptance registered.

## Fresh post-promotion HIGH failure — exact next priority
- render_visual.py --stage chrysanthemum --check-stillness --check-sources --capture-name accessibility-input-pump-v18 ran ONCE at1200×800 HIGH. Failed restored-detail reduced pixel equality; preserve render-accessibility-input-pump-v18.log. Paused pixel, paused-resize pixel, reduced pixel PASS; detail-toggle pose/route assertion PASS by control flow. Sources/full capture NOT reached. No full browser-error list serialized on assertion failure.
- Four accessibility-input-pump-v18-*-trace.json saved. Failed before/settled/after identical entry[0,1.7,8],yaw/pitch0,time/rendered6.30579999980927,frames9,HIGH/reduced,unpaused,no transition/pending. Screenshot.2030/.2244s.9457/380000 crop pixels change,max channel delta1,bbox[411,277,1000,380]. Other three comparisons zero differences. Strict equality remains FAIL; no evidence timer caused it, no proven cause yet.
- BOTH accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-before.png and -after.png inspected exactly ONCE after process exit.1000×380 unobstructed crops: broad magenta/red sweep,green/yellow/cyan smooth nested lips,small blue/green clover centre,sparse hierarchy/smeared highlights, GAME. No obvious geometric change; not temporal regrade. DO NOT re-view. latest.png now equals inspected failed AFTER crop and is labelled diagnostic in README/status. Old full visual-chrysanthemum.png/json unchanged/stale. No completed new full PNG.
- input-pump-v18-review.md and input-pump-v18-integrity.json bind control successes, promotion, HIGH failure, traces, images, display equality and preserved ledgers/defaults. Old intermittent restored-detail failures retained (v23 original failure etc); resemblance is not causal equivalence. Keep passing navigation repair live with explicit HIGH FAIL while diagnosing.

## Exact next bounded work
1. Diagnose failed HIGH stillness with NEW read-only instrumentation around real detail toggles: distinguish raw canvas/GL output from browser-composited screenshot/presentation and record render submission/fence/RAF receipts. Preserve failed pixel pair and strict equality. Do not add blind delays, retry unchanged helper, alter navigation or infer root cause from one-bit differences. Current helper frozen() is at render_visual.py94–127; compositor target/render code at fractal.js450/481; trip renderer antialias:true, default preserveDrawingBuffer, one GPU fence. No new corpus work needed.
2. After causal correction, only affected focused checks, fresh inspected capture and honest display/gate update. Do not redo passing unchanged navigation/desktop gates without change-specific reason. Then return to substantive structural visual successor; no promotion of rejected v29.
3. Other18 realism targets,sixteen source gates,route review/full desktop/mobile/paced/fallback acceptance remain. Only all19 RECOGNISE plus all gates permits completion marker.

## Visual successor / numerical constraints
- Live continuum.js==continuum-v25.js; Chrysanthemum GAME,coverage84.7% FAIL(top10 dark ABSENT),sources50includes/20exclusions. Current grades stale after control repair. v29 isolated field has actual openings but four full-resolution entry/deep temporal captures all GAME; never re-view/rerender unchanged. diagnostic-centre-v29-review.md/receipts/integrity bind evidence. Reject broad coaxial perforated sheets,button-like centre,sparse resolved hierarchy,underlit areas,smeared highlights; changed pixels are not convincing breathing/fold-over. Structural rebuild must resolve nested geometry,not count noise/colour as geometry.
- Start future geometry work from targeted continuum-v29-candidate.js, build_centre_candidate_v29.py, centre-v29-numerical-review.md and centre-v29-bounds.md (selected sections). Earlier v27r2 timed out on temporal capture; v28/r2 root/budget failures preserved; v28r3/v29 numerical successes sampled,not universal proof. Prior composite-FD v29 FAIL retained; subsequent branch-aware leaf checks PASS. Never replay one-shot probes without substantive changed field.
- Maintain x walking bounds±4,entry z8,physical exit−22,closing geometry beyond−27.5,clearance≥4. Existing shaders HIGH2048/LOW1536,14 root bisections,residual.00015; independent gradient/field/first-root validation for NEW field,bounds and filtering. Sampled numerical results do not grant visual/provenance/performance credit.
- v29 full1200×800 HIGH entry/deep pairs settled34.13–44.52s under90s; each pair same actual pose and≥3s animation separation. Do not claim hardware-GPU benchmark. Old60.99s deep walk is not45s exit; movement repaired separately now. Unchanged v29 pictures still rejected.

## Stable route / evidence
- WORLD_DATA172 entries,103 sources,14309 reports. Main route onset→geometry→chrysanthemum→rush→membrane→waiting→cathedral→contact→download→return→afterglow; Workshop/Garden/Clinical/Void return to Cathedral. Route221s editorial; Waiting→Cathedral41 vs reverse64,Contact→Download12 vs reverse129 are prose adjacency,not measured durations. Route audit pending.
- Preserve real movement/collisions/exits,being interactions,Sources,paused/reduced idle,restart,paced mode,shader-based LOW. Onset/afterglow and spacious dark Void are source-specific density exceptions.
- Chrysanthemum source audit COMPLETE:70 fixed-order candidates of480,50include/20exclude; chrysanthemum-source-batch2.md/json. No recollection/re-audit. Top15 flower20,patterns17,multicolour14,fractals8,tunnel8,spinning6,luminous5,transforming5,dark4,green4,purple-pink4,vivid4,beings3,breathing3,folding3;weight108. Counts not independent witnesses/prevalence. Retain dark green l3xvln,layered entrance5ngny9 and justified extension dny4gl.
- Garden27 exhausted4/23 and Workshop76 exhausted28/48,historical84.1/85.4%,images stale. Other16 source gates incomplete. Frozen corpus/passages/queue/lexicon/ledger unchanged;15 supplements(4Garden/11Workshop). Read only selected VISUAL_RESEARCH.json entries; do not dump citations/atlas/summary.
''',encoding='utf-8-sig')

names=promotion['files'].keys()
files=list(names)+['trip.js','trip-v18.js','input-pump-v18-promotion.json','input-pump-v18-review.md','render_visual.py','render-'+prefix+'.log','fidelity-input-pump-v18.log','fidelity-results.json','fidelity-data.js','README.md','status.txt','NOTES.md','NOTES-before-input-pump-v18.md','latest.png',stem+'before.png',stem+'after.png',Path(__file__).name]+[f.name for f in tracefiles]
for n in files:
    if n.endswith('.py'):ast.parse((HERE/n).read_text())
out={'integrity_passed':True,'navigation_promoted':True,'combined_high_controls_passed':True,'reduced_controls_passed':True,'post_promotion_high_stillness_passed':False,'overall_passed':False,'render_signature':render_signature(),'files':{n:digest(n) for n in files},'preserved':{n:digest(n) for n in promotion['previous_protected'] if n not in ['trip.js','fidelity-data.js','latest.png']},'inspected_once':[stem+'before.png',stem+'after.png'],'latest_is_failed_after_crop':digest('latest.png')==digest(stem+'after.png')}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['files','preserved','inspected_once']}))
