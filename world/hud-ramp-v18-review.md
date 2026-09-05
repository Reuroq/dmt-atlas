# HUD alpha-ramp v18 — corrective phase complete

## Change and bounded evidence

The procedural `#hud::before` gradient is replaced by a deterministic 1×4097
RGBA PNG, stretched to the unchanged fixed inset `48% 0 0`. RGB stays #04020a;
alpha endpoints are 0, 112 at 75%, and 176 at 100%. No geometry, movement,
runtime JavaScript, antialiasing, waiting rules or equality thresholds changed.
`fidelity.py` now includes the PNG bytes in render signatures. The asset is
generated arithmetically, not AI imagery or a source depiction.

The changed-only derivative of the completed v18r2 static fixture passed all
18 desktop and 3 narrow-viewport comparisons: native detail/resize controls,
800 ms separation, 90,000 ms guards, strict zero pixel differences and unchanged
submissions within every pair. Browser and GL errors: zero. The unchanged
gradient-absent case was not rerun. The earlier exact signed 9,457-pixel
reproduction and both initial diagnostic failures remain immutable.

Against the prior full static image, pixels above y384 are exactly identical.
Full-image appearance delta is at most 2/255 per channel (mean absolute 0.142534);
the unobstructed overlay region has mean absolute delta 0.267456. Against the
ideal continuous blend, that region's max error is 1.554249 and mean 0.346398.
These are appearance comparisons, NOT relaxed stillness tolerances. Desktop
and 390×844 fixture images were inspected once after exit: text remains readable,
darkening is preserved, no obvious banding. The narrow fixture stretches the
saved scene texture; this is not a live mobile geometry capture.

## Affected original live acceptance

After promotion, the unchanged `render_visual.py --stage chrysanthemum
--check-stillness --check-sources --capture-name accessibility-hud-ramp-v18`
completed at 1200×800 HIGH with all six checks PASS: paused pixel stillness,
paused resize restoration, reduced-motion stillness, detail-toggle route/pose,
restored-detail reduced stillness, and Sources/fidelity/provenance. Four pixel
comparisons remain strict equality. Browser errors: zero. Final entry pose
[0,1.7,8], yaw/pitch 0, paused/reduced, frame10, animation/rendered time
6.14270000019074, no pending frame, no veil or missing/uncited evidence.

The closure hash guard caught `render_visual.py`'s automatic named-capture copy
over the two default files. Both defaults were restored byte-for-byte from the
hash-matching `accessibility-chrysanthemum-v25` originals; the new named image,
receipt and latest display are untouched. Initial closure failure and recovery
receipts are retained. No test was rerun and no renderer change was needed.

The current affected HIGH failure is corrected on this evidence; historical
failure receipts are retained, not rewritten. This is not full acceptance or
a universal browser-mechanism proof. Internal dithering/cache details remain
unproven. No unchanged navigation or full desktop suite was replayed.

## Fresh visual review

`accessibility-hud-ramp-v18.png` was inspected exactly once after renderer exit.
**GAME**: broad smooth saturated sheets around a small clover/button centre,
sparse resolved nested hierarchy, smeared highlights and no convincing black
openings. This single paused image grants no temporal realism grade. Both new
fixture images are also GAME, diagnostic only. Do not re-view these three PNGs.
`latest.png` equals the fresh LIVE image, no longer a static diagnostic.

`fidelity.py --check` regenerated outputs once after the signature change;
expected exit1, overall false. Manual source/grade ledgers and old default
renders are unchanged/stale. Chrysanthemum coverage remains historical84.7%,
dark ABSENT, source decisions50/20. No full acceptance or realism promotion.

## Next

Return to substantive nested-geometry construction from the rejected v29
candidate's selected code and numerical/bounds reviews. Do not promote v29 or
replay its unchanged probes/renders. New field needs independent gradient,
first-root, clearance/bounds and filtering checks, then fresh HIGH entry/deep
temporal inspection. All19 realism, remaining16 source gates, coverage, route
review and full desktop/mobile/paced/fallback acceptance remain unfinished.
