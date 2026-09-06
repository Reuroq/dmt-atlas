# v33r2 — reach-only lower-leaf acceleration

The v33 field, CSG, gradients used for normals, materials, camera and shared
animation clock are unchanged. Symbols below are defined in centre-v33-bounds.md.
This is not a visual rebuild or a realism claim. No live promotion.

## Lower leaves

Every omitted cost is nonnegative: squared shells; axial 1−G(cos); angular
|h_m|²−G(Re(h_2m exp(iP))), since |h_2m|=|h_m|² and 0<=G<=1; rational cores.
Use the following smooth scalar lower bounds, each with an additional −.00001
pad. The pad is conservative slack, not a formal floating-point error proof.

| Parent lower bound (<=a) | Child lower bound (<=b) |
| --- | --- |
| .39−.55G4(cos(T))+1.6/den | .345−.45G12(cos(U))+1.1/den |
| −.16+.65A12+1.6/den | −.105+1.1A36+1.1/den |
| ±1.6s−.32 | ±1.128q−.211032 |

Shell bounds follow 4s²−.16−(±1.6s−.32)=4(s∓.2)²>=0 and
3q²−.105−(±1.128q−.211032)=3(q∓.188)²>=0. Both signs are independent lower
leaves, not an abs cusp. The positive value of any lower leaf proves its full
leaf positive over the lower leaf's certified reach. MAX all these reaches
with the full-leaf reach in the corresponding intersection; union remains MIN.
Full-leaf values still alone determine hit acceptance and normals.

## Derivative bounds

Independent float64 calculus reuses v33 product/trig/Gaussian/harmonic norm
rules, including camera-distance filter derivative cross terms. For each lower
leaf its Hessian bound is rounded upward coefficient-by-coefficient, with one
extra unit. Order: axial parent/child, angular parent/child, shell parent ±,
shell child ±. Coefficients are (constant,pixel,pixel²):

- Axial: (6,6,10), (18,36,66).
- Angular: (37,15,12), (256,174,160).
- Shell: (29,33,42) for both parent signs; (280,381,414) for both child signs.

Full-leaf H and L remain v33's. The 5.445 envelope, .08 guard, .4 maximum
reach retain rho>=4.965, including cap geometry. Clearance, 2048/1536 budgets,
14 bisections, .00015 residual, original directional depth tolerance, and
no forced minimum step are unchanged. MAX cannot shorten the certified full
reach in exact arithmetic. Reduced ray steps do not imply lower GPU wall cost.

## Required checks

Independent full/lower leaf FD, domination and reach samples; original clearance
and Gaussian tests; actual GLSL full/lower jets and exact CSG/normal replay;
HIGH/LOW even/odd rays at entry/deep and clocks4/8/221/900; fixed-grid and separate
interval first-root checks. Compare saved v33 rays without replay. Only after
passing, consider the unchanged 1200×800 HIGH / 90s-settle fixture. Numerical
samples/ordinary float64 intervals are not universal convergence, formal GPU
roundoff, temporal antialiasing, performance, or visual acceptance proof.
