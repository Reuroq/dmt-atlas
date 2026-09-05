# Static compositor isolation — original pixel failure reproduced

Live v25 / trip v18 and all grades remain unchanged. Original HIGH strict
equality is still **FAIL**; this diagnostic establishes a correction target,
not acceptance or a runtime repair.

## Method and bounded results

- Immutable opaque 1200×800 bottom-up submission-v18 frame9 uploaded once as
  a nearest-sampled WebGL2 texture. Antialiasing remains enabled; no geometry
  shader, application navigation, clock, PBO readback or recurring render loop.
- Actual index.html HUD markup and trip.css, real detail clicks (HIGH/LOW/HIGH
  pixel ratios) and viewport resize/restoration. Simplified diagnostic handlers
  are not application acceptance. Native dimension and fence guards, 90000ms
  timeout, original 1000×380 crop and strict equality over 800ms remain.
- Six cycles per gradient-present/absent case: baseline, resize-restored and
  detail-restored comparisons. 36 pairs total; zero browser/GL errors.
- Present: 2/18 FAIL, at cycle3 baseline and resize-restored; both 9457 pixels,
  maximum channel delta1, crop bbox[411,277,1000,380]. First has 4853 positive
  and 4859 negative channel deltas; the second reverses the counts.
- Absent: 18/18 exact-equality PASS. Both cases submit25 static frames; every
  pair's before/after diagnostics (including submission list) are identical.
- The saved first static failure has the **exact same signed per-channel
  difference array** as the original live restored-detail failure, not just
  equal counts or bounding boxes. Historical images analyzed numerically only.

This reproduces the original failure signature without running the geometry
shader and with unchanged submissions during each failing interval. Removing
only the gradient background eliminates it in the bounded negative control.
The HUD gradient's browser presentation is therefore the demonstrated defect
site; internal tile dithering/raster-cache details are not established.

## Instrumentation / limitations

Passive CDP LayerTree events recorded153/147 tree updates, including updates
during comparisons. No layerPainted events were emitted. The gradient's final
1200×416 layer draws content with paintCount13 when present, and does not draw
content with paintCount0 when absent. Layer telemetry alone does not identify
the raster algorithm. This is not a claim about all browsers or GPU hardware.

Initial v18 fixture stopped on an asynchronous resize-observer race: it checked
the previous pending=false before native resize delivery. Preserved initial
files/log and static-compositor-v18-initial-failure.json distinguish this harness
failure. v18r2 waits for actual drawing dimensions and fence retirement, with no
blind delay or relaxed comparison. Neither one-shot run may be replayed unchanged.

## New images inspected once after exit0

The full r2 fixture and its first failed crop pair were each inspected once.
No visible geometric difference in the pair. Full image visibly labelled
“Static compositor diagnostic”: saved broad smooth saturated sheets, small
clover/button centre, sparse hierarchy and smeared highlights, still **GAME**.
No new temporal or live realism grade. latest.png now equals that labelled
1200×800 fixture. Original failed pair and default full captures are preserved.

## Next correction phase

Build an isolated replacement for the CSS procedural gradient, preserving
readability, transparent start at48% and the existing dark colour/alpha stops.
A deterministic narrow pre-rasterized alpha-ramp PNG is the first candidate;
stretch it responsively with no geometry/input/AA changes. Test the CHANGED
static candidate using the same detail/resize and strict equality cases, inspect
one new full image and compare its overlay numerically to the original ramp.
Do not remove the HUD gradient or widen tolerance. If the candidate passes,
apply only that HUD correction and run affected original HIGH stillness/detail/
Sources checks. Preserve the original failure and avoid unchanged desktop runs.
Then resume substantive structural visual rebuilding; rejected v29 stays rejected.

All19 RECOGNISE plus source/coverage/route/full acceptance remain unfinished.
