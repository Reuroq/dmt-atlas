"""One-shot evidence review/display update after the completed, inspected probe."""
from pathlib import Path
import hashlib
import json
import ast
from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
baseline=json.loads((HERE/'submission-v18-baseline.json').read_text())
assert all(sha(HERE/name)==digest for name,digest in baseline.items())
assert not (HERE/'submission-v18-review.md').exists()
receipt=json.loads((HERE/'diagnostic-submission-v18.json').read_text())
assert len(receipt['checks'])==6 and not receipt['errors']
traces=[]
for path in sorted(HERE.glob('diagnostic-submission-v18-*-trace.json')):
    data=json.loads(path.read_text())
    assert data['changed_pixels']==0 and not data['browser_errors']
    for snapshot in data['submission_snapshots']:
        r=snapshot['latest']; b=snapshot['submitted_bytes']
        assert r['alphaMin']==r['alphaMax']==255 and r['nonzeroRGB']==960000
        assert r['queueError']==r['retrieveError']==0
        assert r['queueBindingRestored'] and r['retrieveBindingRestored']
        assert sha(HERE/b['file'])==b['sha256']
        assert r['frame']==snapshot['diagnostics']['frames'] and r['time']==snapshot['diagnostics']['renderedAnimTime']
    traces.append(data)
assert len(traces)==4
raw_hashes={s['submitted_bytes']['sha256'] for d in traces for s in d['submission_snapshots']}
assert len(raw_hashes)==1
for name in ['build_submission_probe_v18.py','trace_submission_v18.py',Path(__file__).name]:
    ast.parse((HERE/name).read_text())
old_stem='accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-'
a=Image.open(HERE/(old_stem+'before.png')).convert('RGB')
b=Image.open(HERE/(old_stem+'after.png')).convert('RGB')
delta=ImageChops.difference(a,b)
assert delta.getbbox()==(411,277,1000,380)
assert sum(any(p) for p in delta.getdata())==9457
assert max(max(p) for p in delta.getdata())==1
review='''# Submission-time PBO diagnostic — valid readback, no repair

Original live v18 restored-detail strict pixel equality remains **FAIL**.
Live trip-v18 / continuum-v25, source decisions, grade ledgers and full default
captures are unchanged. This is an isolated diagnostic, not acceptance credit.

## Method

`build_submission_probe_v18.py` built isolated JS/HTML and a renderer copy.
For each Chrysanthemum submission, WebGL2 PIXEL_PACK_BUFFER readPixels is queued
after the final compositor pass and before the existing application fence.
getBufferSubData retrieves it after fence retirement. Both operations explicitly
restore the previous buffer binding; the temporary buffer is deleted. Packing
and default read-framebuffer state are checked. No preserveDrawingBuffer, AA,
shader, navigation, input or clock changes; original real controls, HIGH1200×800,
90000ms settled waits,800ms screenshot interval and exact equality remain.

Lightweight snapshots bracket screenshots. Immutable submitted RGBA bytes are
exported only AFTER both screenshots, saved with SHA256 and associated by
frame/time/dimensions. Exports can affect subsequent test timing; PBO reads can
also force GPU resolves. Instrumentation therefore cannot establish that the
unmodified application is repaired. No transparent after-presentation copy.

## Results — one run, exit0

- All six stillness/detail/Sources checks pass; zero browser errors.
- Four screenshot pairs have zero changed pixels. Associated frames5/7/7/9
  are settled at animation/rendered time4.650899999427792.
- All exported full1200×800 frames have the same SHA256; all960000 pixels
  contain nonzero RGB,alpha min=max255. No GL errors; buffer bindings restored.
  Resize restoration and detail restoration thus reproduce identical submitted
  bytes in THIS run, including the whole framebuffer, not just the crop.
- Each screenshot matches submitted RGB exactly above crop row275. Under the
  HUD gradient,104991 pixels differ,maximum channel delta38,bbox[0,275,1000,380].
  The corresponding screenshot-to-screenshot difference is zero.
- PBO queue calls for referenced frames take2.2–7ms; retrieval1.7–13.1ms.
  Full byte export overhead is recorded separately in each trace.

## Narrowed hypothesis, not a demonstrated cause

trip.css has `#hud::before` fixed from48% screen height (384px at800px), with a
transparent-to-dark CSS gradient. Raw/screenshot differences start at global
y385, consistent with that intended overlay. Numerical analysis of the preserved
original failure (NOT re-viewed) finds all9457 changed pixels within this same
overlay area: crop bbox[411,277,1000,380],global y387–489. All deltas are±1,
approximately balanced positive/negative; many rows remain identical and
changed rows often contain255-pixel runs/counts. These facts motivate a browser
gradient raster/composition hypothesis, but do not prove it. No raw pixels were
captured in the failing run. Do not equate this successful run with its failure.

Next: a bounded static compositor isolation using these saved opaque submission
bytes, with the actual HUD gradient and real detail/resize controls. Compare
gradient-present and gradient-absent diagnostic controls, record raster/layer
changes if useful. This can avoid repeated expensive unchanged shader renders.
Only a reproduced causal effect warrants a correction; retain HUD readability,
strict equality and adverse evidence. Do not blindly remove AA/add delays.

## Fresh full image — inspected once

`diagnostic-submission-v18.png`:1200×800 HIGH,entry[0,1.7,8],paused/reduced,
frame9,time4.650899999427792,no transition/pending work,veil0,no errors or uncited
geometry. **GAME**: broad smooth saturated sheets surround a small clover/button
centre; sparse nested detail, smeared highlights and no convincing black
openings. This is one still, not a temporal regrade. latest.png now shows this
labelled diagnostic. Prior failed pair, earlier diagnostic and default full
captures remain preserved; no historical image re-viewed.

All19 RECOGNISE plus source/coverage/route/full acceptance remain unfinished.
'''
(HERE/'submission-v18-review.md').write_text(review)
readme=HERE/'README.md'
text=readme.read_text()
old='Next: instrument submission-time framebuffer bytes before browser presentation.\n\nlatest.png now shows the inspected1200×800 **isolated presentation diagnostic**,\nstill GAME (broad smooth colour bands, small clover centre, sparse detail and\nsmeared highlights).'
new='The subsequent submission-time PBO diagnostic produced opaque valid pixels,\nidentical full-frame hashes through resize/detail restoration, and six passing\nchecks. It still **does not clear the original failure**. Differences from raw\nRGB begin under the HUD gradient; browser overlay raster/composition is the next\nisolation target. See [submission diagnostic review](submission-v18-review.md).\n\nlatest.png now shows the inspected1200×800 **isolated submission diagnostic**,\nstill GAME (broad smooth colour sheets, small clover centre, sparse detail and\nsmeared highlights).'
assert text.count(old)==1
readme.write_text(text.replace(old,new))
(HERE/'latest.png').write_bytes((HERE/'diagnostic-submission-v18.png').read_bytes())
(HERE/'status.txt').write_text('Live visual v25 / trip v18 unchanged. Navigation repair PASS remains; original HIGH restored-detail equality FAIL unresolved. New isolated submission-v18 PBO diagnostic: valid opaque pixels, identical full-frame hashes across resize/detail restoration, all6 checks PASS,zero errors; NOT a repair. Raw/screenshot differences start under HUD gradient; next static compositor isolation,strict equality unchanged. latest.png=new inspected1200x800 submission diagnostic,GAME. Failed pair/old full defaults preserved. Coverage84.7% FAIL,dark ABSENT,sources50/20,grades stale. All19 realism/source/coverage/route/full acceptance unfinished.\n')
notes=HERE/'NOTES.md'
prior=notes.read_bytes()
(HERE/'NOTES-before-submission-v18.md').write_bytes(prior)
text=prior.decode('utf-8-sig')
text=text.replace('# Active: REDIRECT4 — live v25 / trip v18; HIGH failure unresolved, presentation probe inconclusive','# Active: REDIRECT4 — live v25 / trip v18; HIGH failure unresolved, valid PBO diagnostic')
text=text.replace('latest.png now equals this labelled isolated diagnostic,not prior failed crop.','latest.png then equalled this labelled isolated diagnostic; superseded by submission-v18 below.')
start=text.index('## Exact next bounded work')
end=text.index('## Visual successor / numerical constraints')
text=text[:start]+'''## Completed submission-time diagnostic (do not replay)
- build_submission_probe_v18.py / trace_submission_v18.py ran ONCE,exit0. Isolated PBO readPixels queued after composite before fence; getBufferSubData after retirement; explicit binding restoration,GL state/errors/dimensions/frame/time recorded. Live files unchanged. Byte exports occur after both screenshots; readback/exports can perturb timing.
- All6 original1200×800 HIGH/90s/800ms strict stillness/detail/Sources checks PASS,zero errors. Four pairs0changed; frames5/7/7/9,time4.650899999427792. Full RGBA hashes IDENTICAL across resize/detail restoration,alpha255,960000 nonzeroRGB pixels,no GL errors,bindings restored. Raw .rgba files and SHA256 preserved. Valid readback,NOT a repair or clearing original failure.
- Raw RGB equals screenshots above crop y275;104991 differences beneath HUD gradient,max38. trip.css #hud::before starts screen48%=384px. Original preserved9457 onebit differences all within gradient region(global y387–489),balanced±1,sparse changed rows,often255 counts. Historical images only analyzed numerically,not re-viewed. Overlay raster/composition is a hypothesis,NOT established cause.
- diagnostic-submission-v18.png inspected exactly ONCE after exit0:HIGH1200×800 entry,paused/reduced,frame9,settled,veil0,zero errors/uncited. GAME:broad smooth saturated sheets,small clover/button centre,sparse hierarchy,smeared highlights,no convincing dark openings. Single still,not temporal regrade. latest.png equals this labelled diagnostic;old defaults and failed pair untouched.
- submission-v18-review.md/integrity.json bind sources,traces,raw frames,receipt,image,display and unchanged runtime/ledgers/defaults. No fidelity/acceptance rerun/promotion. NOTES updated once this phase; prior archived in NOTES-before-submission-v18.md.

## Exact next bounded work
1. Test browser overlay raster/composition hypothesis using a bounded STATIC fixture from saved opaque diagnostic-submission-v18-frame-9.rgba (1200×800,bottom-up RGBA). Actual HUD gradient plus real detail/resize controls; gradient-present/absent diagnostic cases,layer/raster observations if useful. Avoid expensive unchanged shader rerenders. Goal is causal reproduction,not a lucky pass. Original HIGH failure remains. Do not replay Canvas2D after-presentation copy or unchanged PBO run,disable AA/add blind delays/loosen equality.
2. After causal correction, only affected focused checks, fresh inspected capture and honest display/gate update. Do not redo passing unchanged navigation/desktop gates without change-specific reason. Then return to substantive structural visual successor; no promotion of rejected v29.
3. Other18 realism targets,sixteen source gates,route review/full desktop/mobile/paced/fallback acceptance remain. Only all19 RECOGNISE plus all gates permits completion marker.

'''+text[end:]
notes.write_text('\ufeff'+text,encoding='utf-8')
assert all(sha(HERE/name)==digest for name,digest in baseline.items())
files=[p for p in HERE.glob('diagnostic-submission-v18*') if p.is_file()]
files += [HERE/name for name in ['build_submission_probe_v18.py','trace_submission_v18.py',Path(__file__).name,'trace-submission-v18.log','submission-v18-baseline.json','submission-v18-review.md','README.md','NOTES.md','NOTES-before-submission-v18.md','status.txt','latest.png']]
integrity={'result':'valid isolated readback; original HIGH failure unresolved','protected_unchanged':baseline,
           'files':{p.name:sha(p) for p in files},'full_rgba_sha256':next(iter(raw_hashes)),
           'display_equals_inspected_capture':sha(HERE/'latest.png')==sha(HERE/'diagnostic-submission-v18.png'),
           'review':'GAME; one new full PNG viewed once; no historical PNG viewed'}
(HERE/'submission-v18-integrity.json').write_text(json.dumps(integrity,indent=2)+'\n')
print('Closed PBO diagnostic; original failure retained, live/ledgers/defaults unchanged, display and notes updated.')
