# v31 — swept hierarchical flower, prospective bounds

This is geometry interpreted from the already-audited flower/fractal/layered
entrance/folding reports, not new witness evidence. No source regrading.

`h_m=((x+iy)/sqrt(x²+y²+R²))^m`, R=1.5, m=6/18/54. These smooth Cartesian
functions have no angular seam, tiled cells or singular axis. Complex phase
rotation sweeps six petal fins radially and longitudinally; the parent bends
the 18-fold split/branch structure, with 54-fold geometric detail in HIGH.
Amplitude tends to zero at the axis, smoothly suppressing unresolved harmonics.
Gaussian screen-footprint weights and their derivatives remain explicit.

`P=max(f,|a|-.065,.16-|b|)`, `B=max(f+.45,|a|-.18,|b|-.03)`,
`F=min(P,B,f+12)`. Thin angular fins replace v30's intersecting Cartesian bands.
The smooth core `.675/(x²+y²+2.25)` keeps bright geometry off the exact axis:
there a=.3, so both families are excluded. The axial ray reaches actual dark
backing, not a painted miss. No visual grade until fresh temporal inspection.

## Bounds

For S(a,b)=sup(q>=0) q^a/(1+q²)^b, its maximizer is q²=a/(2b-a).
The complex directional derivative triangle inequality gives

`L_m = m/R [S(m-1,m/2)+S(m+1,m/2+1)]`.

`H_m = [m(m-1)S(m-2,m/2)+(2m²+m)S(m,m/2+1)+m(m+2)S(m+2,m/2+2)]/R²`.

These bound complex magnitudes, therefore any real phase projection. Values
are approximately (L,H)=(1.922,7.380),(3.389,22.966),(5.917,70.006).
For Re(h exp(i phi)), use L=Lh+Lphi and
H=Hh+2Lh Lphi+Lphi²+Hphi. `analytic_bounds()` independently computes the
actual coefficients. Core bounds L<=.3, H<=.8 are conservative.

As before rho=length(x,y,.85 min(z+27.5,0)). Modulation <=.9+.15=1.05;
there is no material inside rho4.9. Envelope skip4.895, .08 guard and .4
maximum reach imply rho>=4.415 throughout any material step. Thus radial
H<=1/4.415. The cap is C1 and piecewise C2; no axis-Hessian claim is needed.
Walking x±4, entry8, exit−22 and cap−27.5 remain unchanged.

Gaussian product H<=Hh+2 Lh exp(-.5) k pixel+(k pixel)². Per-leaf conservative
H polynomials are f:11+2p+2p², a:22+13p+10p², b:140+140p+170p².
Global leaf L<=12+10p. Using individual H in exclusion reaches reduces
unnecessary evaluations on the low-frequency radial and primary-petal leaves.
This is an analytic cost improvement, not a measured GPU-performance claim.

Positive smooth-leaf reach stays min(.4,2*.95v/(|d|+sqrt(d²+2H*.95v))).
Positive ordinary abs bands use their smooth active arm before its cusp;
the excluded b band uses MIN of two smooth-arm reaches. CSG intersections
take MAX, unions MIN. Budgets2048/1536,14bisections,residual.00015 and
directional-depth gate unchanged; no forced minimum step.

## Checks required

Independent scalar/FD bounds and reach samples, actual GPU jets and exact
CSG replay, even/odd grids, HIGH/LOW, entry/deep/late clocks and first roots.
Preserve original fixed .003 reference gate separately from an offline
interval-exclusion audit of every saved reference ray. Neither ordinary float64
interval exclusion nor samples prove universal convergence or temporal filtering.
Fresh1200×800 HIGH entry/deep pairs and all realism/source/acceptance gates remain.
