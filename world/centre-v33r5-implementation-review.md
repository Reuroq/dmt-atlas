# v33r5 implementation CLOSED — runtime pending

Only the whole-token GLSL identifier `common` became `sharedJetsState` in the
isolated candidate. Exact reverse substitution recovers v33r4 byte-for-byte;
the prior seven reverse edits still recover v33r3. Expressions, control flow,
materials, scalar oracle and renderer settings are unchanged. JS/AST and
instrumentation-anchor checks PASS. This is not an actual GLSL compilation PASS.

The four derived GPU fixtures have exactly reversible version/token edits and
an identical Three shader-error callback that throws within render before any
readback. Its fake-link failure contract passes; no browser or warmup was run.
The numerical runner persists a started receipt and holds on browser errors;
exceptions receive a separate failure receipt. Historical v33r4 evidence remains
immutable. Bounds are inherited via exact scalar/expression equivalence:
72,000 leaf/reach plus 12,000 clearance samples, zero new bounds runs.

All 48 cases / 75,996 rays / 720 fixed + 720 interval roots remain required.
The new 12-pair balanced cost runner retains its instrumentation, timing
boundaries and strict gates. No timing or speedup claim. No PNG/inspection or
promotion; latest remains labelled REJECTED GAME v32 deep-motion.

## Next

Run probe_numeric_candidate_v33r5.py ONCE with unique log, inspect exit/receipts; only PASS permits audit_centre_v33r5_first_roots.py ONCE, then measure_centre_v33r5_cost.py ONCE. Use PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. No bounds rerun. Preserve48cases/75996rays/720fixed+720interval roots; cost12balanced pairs,identical boundaries,no warmup. Hold on changed hits/counters,worse inferred prefix work or total/median paired wall cost. Close centre-v33r5-integrity.json only on numerical+cost PASS (integrity_passed,numeric_passed,capture_cost_gate_passed,files,protected); only then version-only render_centre_v33r5.py original1200x800 HIGH/90000ms ONCE. No frame-pump change,prewarm,relaxed gates or promotion on failure.
