# Isolated presentation trace — inconclusive, no repair

The original live v18 restored-detail failure remains **FAIL**. No runtime,
source decision, coverage/realism grade or acceptance registry changed.

## Instrumentation and retained setup failure

`build_presentation_trace_v18.py` failed a nonunique replacement assertion
after writing its isolated JS/HTML. Its attempted helper launch also failed
because the helper did not exist. Preserve the partial assets, builder,
`presentation-v18-build-failure.json` and `trace-presentation-v18.log`.

The corrected one-shot v18r2 builder anchors that replacement to the second
screenshot duration. It creates isolated trip instrumentation and a copy of
the original renderer with unchanged controls, 1200×800 HIGH, 90000ms waits,
800ms comparison interval and exact equality assertions. It records RAF,
submissions and fence retirement; after each screenshot it copies the canvas
through Canvas2D, recording RGBA hashes, alpha extrema and diagnostics. Those
read operations add 42–143ms and may perturb presentation timing. This is a
diagnostic, not an unchanged acceptance rerun. It never injects navigation,
pose, input or animation time, and does not overwrite default captures.

## Observations

`trace_presentation_v18r2.py` ran once: all six stillness/detail/Sources checks
passed, zero page/console errors. All four screenshot comparisons had zero
changed pixels. Each before/settled/after pose and clock remained fixed,
with settled receipts. Frame counts were6,8,8,10 for the four comparisons.

**Every Canvas2D copy was fully transparent (alpha min=max=0).** The equal
copy hashes are therefore not evidence of stable rendered colour. A copy taken
after presentation cannot recover the intended default framebuffer in this
configuration (`preserveDrawingBuffer` is false). This probe cannot distinguish
shader/MSAA output from browser composition in the original one-bit failure.
The successful screenshot comparisons do not establish a repair or explain
why the earlier run failed. Do not replay this readback method unchanged.

## Fresh image, inspected once

`diagnostic-presentation-v18r2.png` was inspected exactly once after exit0:
1200×800 HIGH, entry[0,1.7,8], paused/reduced, no transition, frame10,
animation/rendered time6.295300000190739, no pending work. **GAME**: broad
smooth magenta/red/lime/cyan bands surround a small clover centre; sparse
resolved hierarchy, soft/smeared highlights, no convincing dark openings.
This single still is not a temporal regrade. No historical image was re-viewed.
latest.png now displays this labelled isolated diagnostic; old full defaults
remain unchanged/stale. The failed v18 pair remains preserved separately.

## Next

Use submission-time framebuffer capture, preferably queued WebGL2
PIXEL_PACK_BUFFER readPixels before the existing fence and getBufferSubData
after retirement, with explicit buffer-binding restoration. Record dimensions,
frame/time, alpha/nonzero data and hashes; tie screenshots to submitted bytes.
This is a proposed diagnostic, not implemented or a proven fix. Avoid changing
preserveDrawingBuffer, disabling AA, adding blind delays or relaxing equality
to hunt a pass. Keep real controls and original adverse evidence.

The live navigation repair remains v18; structural visuals remain v25/GAME.
All19 RECOGNISE plus source/coverage/route/full acceptance remain unfinished.
