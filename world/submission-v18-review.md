# Submission-time PBO diagnostic — valid readback, no repair

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
