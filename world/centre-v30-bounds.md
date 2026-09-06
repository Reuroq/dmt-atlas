# v30 volumetric petal network — prospective numerical bounds

This replaces both coaxial membranes with split petal volumes and transverse
branches throughout the outer space. Three smooth leaves are `f,a,b`:

`P=max(f, |a|-.19, .10-|b|)`

`B=max(f+.32, |a|-.40, |b|-.055)`

`F=min(P,B,f+9)`.

The wider parent band supports finer cross branches; the narrower band is split
by real openings. Three spatial scales change the actual zero sets. The highest
octave changes b in HIGH, not pigment. LOW keeps the first two geometric scales.
Geometry is an interpretation of the already-audited flower/fractal/layered
entrance/breathing/folding descriptions, not new witness evidence.

## Analytic bounds

A three-direction Cartesian rosette at k has amplitude <=1, gradient <=k and
Hessian <=k². For `Rk*cos(b*z+c*parent+phase)`, conservative bounds are
`L=k+|b|+|c|*Lparent`, `H=L²+|c|*Hparent`. Orthogonal time rotation does not
change spatial bounds. The four (L,H) pairs are bounded by:

| Level | L | H |
| --- | ---: | ---: |
| r0 | .74 | .5476 |
| r1 | 2.71 | 7.8917 |
| r2 | 7.289 | 60.233051 |
| r3 | 17.7312 | 362.58269424 |

Gaussian footprint w at q=k*pixelScale has `Lw<=exp(-.5)*q`, `Hw<=q²`.
Filtered wave bounds are `L+Lw`, `H+2*L*Lw+Hw`; all filter gradients are in
the jets. For b, including .24 times level3, H is less than
`147.253+223*pixelScale+262.24*pixelScale²`, L less than
`11.545+9.851*pixelScale`. Other leaves are smaller. Use conservative shared
`L=13+12*pixelScale`, `M=160+250*pixelScale+600*pixelScale²`.

`rho=length(x,y,.85*min(z+27.5,0))`. Radial modulation <=.35+.12=.47,
so no material exists for rho<5.48. Before cap z=-27.5, clearance is >=5.48,
covering walking x±4 and exit z=-22. Envelope skip uses 5.475. Within a .4
guarded step after the .08 envelope guard, rho>=4.995; radial Hessian <=1/4.995.
Cap is C1/piecewise C2, anisotropic map is a contraction. No radial singularity
is sampled by the material marcher; the bound is not claimed at the axis.

## CSG first-entry reach

For positive smooth v, use `min(.4,2*.95*v/(|d|+sqrt(d²+2*M*.95*v)))`;
nonpositive leaves have zero exclusion reach. Positive `|a|-width` reaches
its boundary before its absolute-value cusp, so its active arm suffices.
In contrast, `.10-|b|=min(.10+b,.10-b)` has a cusp in FREE space:
use the MINIMUM of the two smooth arms' reaches, never smooth curvature at
that cusp. Intersections take MAX of reaches, unions take MIN.
Retain 14 bracket bisections, .00015 residual and directional-depth acceptance,
2048/1536 budgets and no forced minimum step. This is free-side first-entry
marching, not inside-solid exit logic or a universal grazing-root proof.

## Required checks

Independent scalar/finite differences, all actual GPU smooth-leaf gradients,
exact CSG replay, first-sign-crossing .003 scans with .03 tolerance, even/odd
grids and entry/deep/late times, sampled bounds/clearance/filtering. Raw composite
FD mismatches at creases must be retained, not passed off as differentiable.
Numerical success grants no realism, temporal-quality, source or GPU-performance
credit. New full HIGH entry/deep temporal inspection remains mandatory.
