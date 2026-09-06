# v34 geometry implementation — isolated, runtime untested

## Design and source limits

The v33r6 entry was GAME: disconnected oval chains, no readable laminae or
nested flower hierarchy. Its numerical/cost PASS and temporal timeout remain
historical evidence, not v34 results. No replay or frame-pump change.

The existing `chrysanthemum-source-batch2.md` conclusions support transforming
3D mandala depth, subordinate fractals, overlapping entrance layers, and
green/purple unfolding forms with black gaps. Individual palettes and mechanical
variants are not universal. No corpus recollection, new witness count, source
grade, coverage score or visual grade is claimed here.

v34 replaces summed square cell costs with intersections of a thin, continuous
curled shell, an angular cut and a broad longitudinal cut. The shell is
`S = cos(R + .92 sin(U)) - .72 cos(U) + HIGH detail`, with distinct mixed radial
and axial phases R/U. Turning phase moves the angular petal openings; curl and
longitudinal phases animate actual surfaces. There is no angular chart seam.
The common radius retains the closing cap beyond z=-27.5.

The child centreline is `S - .30(1-cos(U))*B`, with `.69 <= B <= 1.31`.
Its .062 halfwidth accompanies the parent's .095 halfwidth. B carries smaller
2.3R and HIGH 6.1U folds; HIGH also adds a .045-amplitude 4.3R parent corrugation.
These are field displacement, not colour-only detail. Gaussian footprint
filtering includes derivatives and affects only the finer terms. Parent and
child silhouette cuts preserve open gaps; the unchanged dark backing remains
real intersected geometry.

At cos(U)=1 both shell centrelines coincide. For cos(U)>=.61, their separation
is at most .15327 < .095+.062: shell volumes overlap in a finite attachment
band. Child angular/longitudinal cuts are stricter versions of the parent's,
and its f+.3 clearance is stricter too. Thus permitted child attachment-band
cross-sections overlap the parent. This is a conditional construction proof,
NOT proof that every global connected component reaches an attachment band,
nor proof of recognisable nested petals. Those remain numerical/topology and
visual questions. The wider shell patches could still read as ribbons/sheets;
the new capture must judge that adversarially.

## Smooth-leaf certificate

Let F be the unchanged inner-clearance field, A the axial gate, G the angular
gate, S the parent shell, and C the child shell. The occupied composite is:

```
P = max(F, A, G, S-.095, -S-.095)
Q = max(F+.3, A+.20, G+.28, C-.062, -C-.062)
D = min(P, Q, F+10)
```

The shader's `a`/`b` outputs are now nonsmooth maxima. They are NOT smooth
leaves, and neither their active gradients nor finite-difference Hessians can
certify reaches across a crease. The reach code explicitly uses all eleven
signed/offset smooth leaves above. Intersections take MAX of free reaches,
unions MIN. The cheap path uses only F and the two axial gates, a subset of the
same intersected leaves; full evaluation invokes that identical cheap helper.

For a positive leaf v, directional derivative d and Hessian-norm bound M,
`v(p+s*r) >= v(p) - abs(d)*s - M*s*s/2`. The unchanged positiveReach function
solves this quadratic for .95*v and caps it at .4. Thus a positive leaf stays
positive on its certified segment in the real-arithmetic model. Negative or
zero leaves certify zero. No minimum step or assumed smoothness of max/abs.

The unchanged envelope permits full/cheap evaluation only at rho>=5.365.
rho is 1-Lipschitz, so every <=.4 certificate stays within rho>=4.965.
For this capped norm, gradient<=1 and Hessian<=1/rho off the C1 cap join;
the same Taylor remainder follows from its Lipschitz gradient across that
join. The inverse-radius complex harmonics are smooth at the axis. Their
global gradient/Hessian bounds follow product differentiation and maximizing
`r^a/(1+r^2)^b` at `r^2=a/(2b-a)`.

`field_centre_v34.analytic_bounds()` carries amplitude, gradient and Hessian
bounds through sums, products, trigonometric phases and Gaussian filtering.
For product ab, H<=|a|Hb+|b|Ha+2LaLb; for sine/cosine, H<=Hphase+Lphase^2.
Filter exp(-k^2*pixelScale^2*distance^2/2) has gradient norm at most
k*pixelScale*exp(-1/2) and Hessian norm at most k^2*pixelScale^2.
The complex product bound also bounds each real projection. HIGH bounds
include every fine term and dominate LOW. The builder pads every nonnegative
coefficient with ceil(1.05*x+1) before embedding shader constants.

The attachment and derivative calculus are prospective real-arithmetic
arguments. Polynomial trigonometry approximates sine/cosine; paired jets do
not differentiate the polynomial bit-for-bit. Existing reduction/polynomials
are unchanged. Ordinary float64 bound calculations with coefficient padding
are not a directed-rounding or GPUfloat32 proof. Fresh sampled/GLSL/root gates
are mandatory, including phase-boundary cases and cap joins. No inherited
v33r6 numerical pass applies to this new scalar field.

## Cost intent and preservation checks

The full field no longer builds h18/h36, squared shell costs, inverse-core
petal costs, or the old independent high-frequency child shell. Shared paired
local sine/cosine and paired angular rotation avoid duplicate range reduction.
There are eleven full smooth-leaf reaches, versus the old thirteen full/lower
reaches. CommonJets now retains seven vec4s rather than five; register pressure
or code shape may offset arithmetic savings. No speedup claim before a NEW
matched cost experiment. Changed geometry can change hits and iteration counts;
parent/candidate hit equality is not a valid geometry-equivalence assumption.

One reversible section replacement recovers v33r6 byte-for-byte. The builder
checks untouched shader prefix and material/marcher suffix, exact compose,
envelope and positiveReach bodies, JS syntax, Python AST, explicit leaf wiring,
bound coefficient domination, and the conditional shell-overlap inequality.
These checks do not compile GLSL. The renderer is a version-only copy of the
original, not run; it creates its diagnostic HTML only after passing gates.
Live continuum/trip, controls, defaults, source/manual ledgers and historical
PNGs remain unchanged. HIGH2048/LOW1536, 14 bisections, .00015 residual and the
directional gate, .08 cheap selector, .4 certificate cap, original1200x800
HIGH/90000ms capture, centre tolerance and original45s exit are unchanged.

## Next bounded phase

Prepare NEW v34 numerical and cost fixtures before running them ONCE. Do not
blindly version-copy v33r6 leaf/interval/cost logic: its three-smooth-leaf
assumption and exact parent/candidate hits apply to a different task.

- Bounds/clearance: retain 72,000 sampled leaf/reach and 12,000 clearance
  checks, add explicit five-base/eleven-expanded smooth-leaf handling, cap
  joins and attachment-band checks. Check root bands are actually represented
  in clipped petals; report disconnected components if found. No visual credit.
- GPU and independent first roots: retain 48 cases/75,996 rays and 720 fixed
  plus 720 interval references, both grids/modes/entry/deep and all prior
  timings including2.4077/3.5242/4.895. Preserve original error/miss/unresolved
  gates; expand CSG intervals monotonically from smooth leaves. Record selected
  one-sided gradients at creases, not a claimed unique normal. Preserve
  fail-closed shader callback and durable start/failure/actual-exit receipts.
- Cost: prepare a matched v34 shared/unshared experiment using IDENTICAL v34
  geometry and reach/march decisions. Only the reference full trace recomputes
  commonParts(p) through fieldPartsReach instead of consuming retained common
  jets; do not bypass the cheap certificate. Exact hit/root/count comparisons,
  fewer common-prefix evaluations, and both total/median wall ratios<=1 remain
  the gates. Preserve12 balanced pairs, timing boundaries and durable per-arm
  lifecycle; no prewarm. This tests sharing on the NEW field, not v34 versus
  v33r6 performance or the whole geometry-rebuild speedup. The original capture
  still gates full-resolution performance. Do not rerun old experiments.
- Only new numerical+cost PASS permits a passing `centre-v34-integrity.json`
  and the original `render_centre_v34.py` ONCE. Current implementation receipt
  is NOT that gate. Save actual exit before inspecting each new PNG once.

latest.png remains the inspected REJECTED GAME v33r6 entry, explicitly labelled
in README/status. No new image exists in this implementation phase. All19
realism, remaining16 source gates, coverage, route/full acceptance unfinished.
