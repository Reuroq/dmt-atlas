# Navigation responsiveness repair — trip v18

## Measured failure, retained

`trace_lateral_v17.py` ran once against an isolated, instrumented v17 copy
at the original 1000×700 HIGH viewport. Native controls reached the right
boundary, then held left until the unchanged centre condition. It reproduced
the failure: x−4, outside −3.2≤x≤0. No pose, route or clock injection.

The left press was handled at performance time 9920.4ms. The next RAF arrived
at 17053.6ms: `syncMovement` integrated 7.1332s in collision substeps, moving
x4 directly to x−4. The observer first saw the crossing at 17062.1ms; release
was handled at 17064.9ms. Native press/release timestamps preceded handling
by about 0.2/0.3ms. The render submission at the crossing took 0.5ms in JS.
Thus this run's large overshoot preceded release: it was not a seconds-long
keyup delivery delay. The trace does not isolate every cause of RAF withholding
or establish hardware-GPU performance.

Trace naming caveat: `native-after` is a separate observer registered BEFORE
the application handlers; its name is misleading. Use `native-before` for
the actual pre-sync handler timestamp and `move-before`/`move-after` for
integration. The original trace and script are retained without relabelling.

## Repair

`trip-v18-candidate.js` adds a demand-driven 16ms navigation timer, independent
of RAF/render submissions. Keyboard and touch holds start it. At most one timer
is scheduled; it stops when input is empty or navigation is inactive. It does
no GL work. RAF, timer and input-event flushes share v17's monotonic clock, so
held time is neither double-counted nor capped/discarded. Collision substeps
remain ≤0.05s; physical portals, boundaries, speed, animation/transition clocks,
pause, reduced motion and one GPU frame in flight remain unchanged.

This makes pose updates available between compositor-delayed RAF callbacks;
it does not make a multi-second GPU render visually smooth.

## Focused results and promotion

- Original combined HIGH gate: **PASS**, centre return x−0.0745600006,
  Sources/right boundary/two-axis drag-look pass. Physical exit reaches cited
  Rush in **9.409652426 seconds**, unchanged 45000ms allowance.
- All eight reduced-mobile LOW controls/idle cases: **PASS**. Real keyboard,
  touch walking/look, stage buttons, being interaction, Sources, motion/pause
  and restart; exact idle pose/clock/frame equality and settled GPU receipts.
- Zero browser errors in both runs. JS syntax and Python AST checks pass.

`input-pump-v18-promotion.json` verifies all prior protected/evidence hashes,
binds both passing outputs to the exact candidate SHA256 and records promotion
to identical `trip-v18.js` / `trip.js`. Old v16 and failed v17 remain immutable.
The tests were isolated; their base-live render-signature fields are accompanied
by the actual candidate hash. They are not registered as current full acceptance.

`fidelity.py --check` regenerated current gate outputs and correctly exits 1:
new runtime signature makes old visual/acceptance receipts stale. No descriptor,
source or realism grades were raised. All19 RECOGNISE, source/coverage,
route and full acceptance remain unfinished. The structural v29 GAME rejection
is unchanged; this is a control repair, not a visual rebuild.

## Post-promotion HIGH stillness — FAIL, unresolved

The original live `render_visual.py --check-stillness --check-sources` ran once
with unique prefix `accessibility-input-pump-v18`, unchanged 1200×800 HIGH
and 90000ms waits. Paused pixels, paused-resize pixels and reduced pixels passed;
detail-toggle pose/route preservation also passed by control flow. Restored-detail
reduced pixel equality **FAILED**, before Sources or a full capture was reached.
The log and all four per-comparison traces are preserved; no pass-hunting rerun.

The failed pair has identical before/settled/after pose [0,1.7,8], zero yaw/pitch,
animation/rendered time 6.30579999980927, frames9, HIGH/reduced, unpaused,
no transition and no pending GPU work. Screenshot durations were 0.2030/0.2244s.
9457 of 380000 crop pixels differ, each by at most **one** 8-bit channel value;
crop-relative bounding box [411,277,1000,380]. Exact equality is still required.
The failed run does not serialize its final browser-error list.

Both 1000×380 failed-comparison PNGs were inspected exactly once after process
exit. Both show the same magenta/red outer sweep, cyan/green/yellow nested smooth
lips and small blue/green clover centre. Sparse resolved hierarchy and broad
smeared highlights remain **GAME**. No conspicuous geometric motion is visible
between these stills; this is not a temporal realism regrade. Do not re-view them.

This resembles an earlier retained intermittent restored-detail failure, but
causal equivalence is unproven. No input was held during this comparison. The
passing control repair stays live, with this explicit HIGH acceptance failure.
Next: diagnose canvas readback versus browser presentation around actual detail
toggles using read-only instrumentation. Do not loosen pixel equality, add blind
settling delays, replay unchanged acceptance or claim fixed presentation timing.
latest.png is the inspected failed AFTER crop, labelled diagnostic in status/README;
the old full-size default captures remain unchanged and stale.
