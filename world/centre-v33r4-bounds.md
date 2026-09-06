# v33r4 — common-prefix reuse only

The scalar oracle and every analytic bound are unchanged from v33r3. See
[parent derivation](centre-v33r3-bounds.md) and its v33r2 references. v33r4
factors the identical Cartesian/radius/inverse/cube expressions into commonParts.
Five jets (z, radius, inv, r6, i6) are constructed once at p after the envelope
test and passed to both cheap and full evaluations. Full-only r18/r36, shells,
angular costs and materials stay outside the cheap path. Standalone field/cheap
wrappers compute their own common prefix for independent calls and refinement.

Seven reversible edits recover the parent byte-for-byte; scalar and material
expressions, filter, MAX/MIN composition, padded lower leaves, .08 branch,
.4 reach cap, budgets, brackets and controls are unchanged. This structural
claim is not GLSL compilation, floating-point equivalence or performance proof.

Prepared validation retains independent scalar/FD/reach/clearance/fixed-grid
and first-root interval tests, with HIGH/LOW entry/deep and both grids at
2.4077, 3.5242 and 4.895. 48 GPU cases/75996 rays,
720 fixed-grid and 720 interval references. No universal convergence or
directed-rounding GPU proof. No numerical, cost or visual gate has run yet.
