# Isolated v28r3 visual sequence — GAME, not promoted

Executed `render_centre_v28r3.py` once. It exited successfully before inspection.
Viewed each of the four new PNGs exactly once with `view_image`; no historical
PNG was re-viewed. These are visibly labelled synthesised candidate diagnostics,
not witness images or live acceptance captures.

## Visual judgement

Would someone who has had this experience recognise this, or does it read as a
game? **GAME at entry and deep, including both temporal pairs.** This is a
project review against the stated bar, not an actual witness endorsement.

| Capture | Observed form and adverse evidence |
| --- | --- |
| entry | Saturated magenta surround, orange/green outer lobes, cyan/violet inner rings and a small green-blue clover centre. Large smooth areas dominate; there are few nested scales. Rounded wet-plastic folds, not intricate jewelled geometry. |
| entry-motion | At the identical pose, outer lobes and centre clearly change shape and colour. The centre still reads as a simple flower enclosed by concentric bands; large nearly empty pink/purple surfaces remain. Some narrow edges are uneven and streaked. |
| deep | Walking enlarges the cap and adjacent folds. The green/cyan surround remains broad and smooth. The central star-like convergence and soft multicolour lobes are more apparent, without a corresponding increase in resolved detail. |
| deep-motion | At the identical deep pose, the central lobes rearrange and the outer green/orange contour changes substantially. The same soft, rounded material and sparse hierarchy persist; the axial convergence remains conspicuous. |

Colour variety and strong local highlights are present. No obvious low-poly mesh
edges are visible, but that alone is not realism. Broad gradients and smeared
transitions read as wax/liquid plastic, not convincing glass, chrome, or densely
layered jewels. Fine contour marks remain in places; the images do not establish
whether those arise from shading, filtering, or geometry. No substantial black
openings are visible in any frame. More random high-frequency surface noise
would not by itself repair the missing hierarchy, depth, or dark-space structure.

The separated frames establish visible deformation at fixed poses. They do not
establish smooth flow, continuous folding, temporal antialiasing, or perceptual
motion quality between samples. No RECOGNISE or coverage pass is awarded.

## Technical sequence and limitations

- Four 1200x800 HIGH captures pass: paused, settled, matching animation clocks,
  no transition, no missing evidence/uncited meshes, no console/page errors,
  and zero veil opacity. Source and capture hashes are retained in receipts.
- Entry position [0,1.7,8], times 3.5598 and 6.6766 (delta 3.1168 seconds).
  Deep position [0,1.7,-6.71936], times 11.3431 and 14.4430 (delta 3.0999).
  Yaw and pitch are zero and unchanged within both pairs.
- Settle waits: 26.654, 30.844, 29.234, 27.304 seconds, all below the unchanged
  90-second limit. Unlike the previous attempt, this sequence completed.
- Temporal operations including real controls, settling, and screenshots took
  56.165 and 53.730 wall seconds, each with four completed frames. These are
  end-to-end SwiftShader measurements, not isolated shader timings or a
  hardware-GPU benchmark. Interactivity on a decent GPU is not established.
- Real walking to the deep capture plus pause took 45.722 wall seconds. This
  was NOT the original 45-second physical-exit test: the target was only z=-6,
  not exit z=-22. It is adverse latency evidence, not a new exit result or
  proof that the dt cap causes the live failure.
- No pose, route, or clock injection, retries, resolution reduction, extended
  timeouts, repeated numerical samples, or unchanged desktop acceptance runs.

## Decision and next bounded work

Reject promotion. Preserve v28/r2 numerical failures, checker errors, v27r2
visual timeout, and this complete GAME sequence. The v28r3 stepping improvement
is a useful isolated numerical baseline, not a visual success.

Next create a substantive isolated revision addressing the few large smooth
concentric folds, sparse nested centre, waxy low-contrast shading, and missing
dark recess/opening structure. Begin with targeted inspection of the current
material and field; do not repeat corpus exploration or these renders. Separate
geometric hierarchy from material effects so colouring cannot be counted as
geometric detail. Preserve clearance, provenance, real controls, shader LOW,
and strict first-root gates; changed geometry requires new bounds/reference
validation, not inherited numerical claims. Obtain fresh entry/deep temporal
evidence after the changed candidate passes its relevant checks.

Repair the original 45-second walking exit, without extending it, before any
promotion or full acceptance. Its dropped-wall-time hypothesis remains untested.
Do not rerun the unchanged failing exit merely to confirm the same failure.

Live continuum v25/trip v16, coverage/realism/source ledgers and default
visual-chrysanthemum.png/json remain unchanged. `latest.png` is updated to the
newest inspected, labelled v28r3 deep-motion diagnostic, not a promoted runtime.
Live coverage remains 84.7% FAIL (top-ten dark ABSENT), source decisions 50/20,
and original 45-second exit FAIL. Other 18 realism targets, 16 source audits,
route review and full acceptance remain unfinished. No WORLD_DONE.
