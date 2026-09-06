# v33r3 — two-tier certified-free marching

This inserts an axial-only fast path into v33r2. Removing the two insertions
recovers the parent source byte-for-byte. The zero set, full jets, CSG, normals,
materials, camera, filtering and animation clock are unchanged. No live promotion.

## Cheap certificate

`cheapParts` computes only f and the two axial lower leaves from
[v33r2 bounds](centre-v33r2-bounds.md). It omits h12/h18/h36, shell construction,
angular phases and full a/b. Existing padded axial expressions, filter gradients
and curvature polynomials are retained. Within each intersection take MAX of
f/axial reaches; across the parent, child and backing union take MIN. Every
positive reach is capped at .4. The original envelope/guard preserves rho>=4.965.

If this certificate exceeds .08, advance by exactly its certified reach and
clear bracket history. The .08 threshold selects the fast path; it is neither
a minimum step nor a hit tolerance. Retain the 105 distance limit. Otherwise
execute the unchanged v33r2 full path. No cheap value accepts a hit or normal.
The 2048/1536 budgets, 14 bisections, .00015 residual, directional tolerance,
clearance and real journey controls remain unchanged.

This can use shorter steps than v33r2 and adds overhead on full-path iterations.
Performance improvement and budget sufficiency are unproven until measured.

## Prepared checks (not yet run)

- Original derivative, lower-leaf domination, free-reach, clearance and Gaussian
  tests; independent cheap scalar/derivative/reach samples at the original
  pixel scales, adding clock4.895.
- Actual GLSL even/odd entry/deep HIGH/LOW rays at original clocks, plus4.895
  on both grids:32 cases,50,772 rays,480
  fixed-grid and480 independent interval first-root references. No relaxed limits.
- Saved-root cheap jets versus both independent float64 and full-path jets.
- Separate fourth readback records main-loop cheap calls, full trace calls,
  certified skips and refinement calls. Envelope skips=iterations−cheap calls.
  The terminal diagnostic root adds one full sample per ray. These are probe
  counts, not complete shaded-frame costs. Time the first three readbacks
  separately; compare only matching saved v33r2 cases, without replaying them.

Ordinary float64 sampled/interval evidence is not a formal GPU roundoff proof,
universal convergence, temporal antialiasing, performance or realism acceptance.
Only a passing numerical closure permits a fresh original1200×800 HIGH/90s
capture. Historical failures and latest's rejected v32 image remain intact.
