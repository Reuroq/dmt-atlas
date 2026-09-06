# v33r3 numerical closure — PASS; visuals UNREVIEWED

The unchanged one-shot bounds, GPU, independent first-root and saved-cost scripts
completed. 72,000 leaf/reach samples, 12,000 clearance samples, Gaussian filter
checks, 32 GLSL cases / 50,772 rays and 480 fixed-grid plus 480 interval roots pass.
Both grids include the prior failed clock4.895, HIGH/LOW and entry/deep.
Zero GPU misses, browser errors or unresolved intervals. Cheap/full count
invariants pass; composite finite-difference discrepancies at creases are retained.

The implementation receipt binds exact parent recovery after removing the two
insertions. Full scalar, materials, normals, cameras, filtering and budgets remain
unchanged. This closure checks all implementation, numerical and protected hashes,
Python AST and candidate JS syntax. Live v25/trip18/HUD, defaults and ledgers stay
unchanged. No renderer or acceptance rerun occurred in this phase.

## Numerical metrics

```json
{
  "leaf_samples": 72000,
  "cheap_gradient_ratio": 0.5909294909471751,
  "cheap_curvature_ratio": 0.25403856510314404,
  "cheap_minimum_advanced_field": 0.0171400780328117,
  "gpu_rays": 50772,
  "max_leaf_scalar_error": 0.0005786689624480701,
  "max_leaf_gradient_error": 0.0024201492853705986,
  "max_cheap_scalar_error": 4.900856256812025e-05,
  "max_cheap_gradient_error": 0.000124345840910145,
  "max_cheap_full_jet_error": 0.0,
  "composite_fd_discrepancies": 0,
  "fixed_root_error": 0.0006198227703571035,
  "interval_root_error": 0.0006197967529288917
}
```

## Saved-ray cost

```json
{
  "matched_v33r2": {
    "rays": 38160,
    "mean_steps": 166.9232180293501,
    "p95_steps": 252.04999999999563,
    "max_steps": 476.0,
    "median_three_readbacks_seconds": 0.41566840512678027
  },
  "matched_v33r3": {
    "rays": 38160,
    "mean_steps": 170.71027253668763,
    "p95_steps": 258.0,
    "max_steps": 480.0,
    "median_three_readbacks_seconds": 0.4875499997138977,
    "mean_cheap_calls": 163.2559748427673,
    "mean_full_trace_calls": 105.4585429769392,
    "mean_certified_skips": 57.797431865828095,
    "mean_refinement_calls": 0.0033018867924528303,
    "mean_envelope_skips": 7.454297693920336,
    "mean_full_field_evaluations_in_probe": 106.46184486373166
  },
  "all_v33r3": {
    "rays": 50772,
    "mean_steps": 171.22209091625305,
    "p95_steps": 258.0,
    "max_steps": 480.0,
    "median_three_readbacks_seconds": 0.4729500002861023,
    "mean_cheap_calls": 163.76802174426848,
    "mean_full_trace_calls": 105.73985661388167,
    "mean_certified_skips": 58.028165130386824,
    "mean_refinement_calls": 0.0024816828173008744,
    "mean_envelope_skips": 7.454069171984559,
    "mean_full_field_evaluations_in_probe": 106.74233829669897
  },
  "max_matched_depth_delta": 0.0006561279296875,
  "limitations": "Saved sparse SwiftShader rays only. Old timing surrounds page.evaluate; new timing is inside JS around the first three readbacks, excluding RPC and the separate fourth counter readback. Shader instrumentation/compilation and timing boundary differ, so wall-time comparison is indicative, not a controlled benchmark. Main-loop full trace counts omit shaded-frame work. No old replay, no full-resolution or realism acceptance."
}
```

Matched mean iterations increased166.92→170.71; v33r3 averages105.46 full trace
calls and57.80 certified skips. Median three-readback time increased.416→.488s.
These timings do not demonstrate a speedup, even though the fast path avoids
full evaluation on many iterations. Full-resolution settling remains unproven.

Ordinary float64 sampled/interval evidence is not a formal GPU roundoff proof,
universal convergence or temporal-antialiasing acceptance. Timing boundaries and
instrumentation differ from v33r2; timing is indicative, not a controlled benchmark.
Trace counters omit shaded-frame work. Only a fresh original full-resolution
capture can test the existing90s gate; no runtime or realism pass is inferred.

## Next

Run prepared render_centre_v33r3.py ONCE, original1200x800 HIGH/90s, real entry/deep controls and fixed-pose>=3s pairs. Wait for process exit before viewing each NEW PNG exactly once. Preserve failures without relaxing limits or replaying unchanged work. No visual grade or promotion before inspection.

Latest remains the already inspected, labelled REJECTED GAME v32 deep-motion
diagnostic. Prior v33/v33r2 HIGH90s failures remain intact. All19 realism,
remaining source/coverage/route/full acceptance work is unfinished.
