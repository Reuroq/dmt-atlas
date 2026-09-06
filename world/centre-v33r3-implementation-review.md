# v33r3 implementation — complete; numerical/visual validation pending

Isolated axial-only certificate path added. Segments over .08 advance by the
certified reach (maximum .4) and reset bracket history. Otherwise v33r2's full
path is unchanged. This is a performance hypothesis, not a measured fix.

Static checks PASS: removing two inserted blocks recovers v33r2 byte-for-byte;
independent full scalar reference unchanged; original HIGH fixture differs only
by candidate version; Python AST and JavaScript syntax pass; instrumentation
anchors are unique. This does not establish GLSL compilation or numerical safety.

Prepared bounds/GPU/interval/cost fixtures include clock4.895, cheap jet checks,
free-segment sampling and cheap/full/skip/refinement counters. No numerical or
render fixture has run. The renderer still requires a passing numerical closure.

Live v25/trip18/HUD, defaults, source/manual ledgers and old evidence are unchanged.
latest.png remains the inspected, labelled REJECTED GAME v32 deep-motion image.
No new PNG; v33r3 is visually UNREVIEWED. All19 realism/source/coverage/route/full
acceptance remain open.

## Next

Run check_centre_v33r3_bounds.py, then probe_numeric_candidate_v33r3.py, then audit_centre_v33r3_first_roots.py and measure_centre_v33r3_cost.py ONCE each, saving logs. Original cases plus failed clock4.895:32 GPU cases/50772 rays/480 fixed-grid and480 interval roots; preserve all limits. Inspect failures before any correction; never replay unchanged completed probes. If numerical checks pass, write a numerical closure binding sources/protected hashes and cost (centre-v33r3-integrity.json); only then may prepared render_centre_v33r3.py run ONCE at original1200x800 HIGH/90s. No capture is authorized by this static receipt.
