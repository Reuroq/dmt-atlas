# v33 — closed tapered, curled petal cells

Synthesised interpretation of already-audited flower/fractal/folding/entrance
reports. No new source decisions, promotion or visual claim.

## Topology

Use the v32 regularized harmonics h_m=((x+iy)/sqrt(x²+y²+2.25))^m after
the actual-clock .075t rotation; rho=length(x,y,.85min(z+27.5,0)). Let

- R=1.35rho+.12z+.15Re(h6)−.12t; T=.9z−.25rho+.2Im(h6)−.19t.
- C=R+.9sin(T); P=.7sin(T)+.22cos(R)+.2t.
- D=3C+.35cos(T)−.21t; U=3T+.4cos(R); V=3P+.3sin(U).
- s=G4(cos(C)−.6cos(T)).
- q=G12(cos(D)−.55cos(U))+HIGH*.11G36(cos(3D+.25Re(h36))).
- A12=|h6|²−G4(Re(h12 exp(iP))); A36=|h18|²−G12(Re(h36 exp(iV))).
- f=6.2−rho+.4Re(h6).
- a=4s²+.55(1−G4(cos(T)))+.65A12−.16+1.6/(x²+y²+2.25).
- b=3q²+.45(1−G12(cos(U)))+1.1A36−.105+1.1/(x²+y²+2.25).
- F=min(max(f,a),max(f+.3,b),f+10).

Gk(v)=v exp(−.5 k² pixel² |p−camera|²), including its full Cartesian jet.
All angular and axial costs are nonnegative. A parent requires cos(T)>=.709
before further costs, closing each cell in depth. At unfiltered large radius,
the angular cost closes cells around twelve separate angular maxima, not an
annulus. Child cells have threefold radial/depth subdivision and36 angular
maxima and are a separate volumetric union, not surface pigment or tiny ripples.
Curl bends each shell and twists its azimuth as depth varies. Squared-shell,
angular and axial costs taper to closed rims; space between cells is actual free
volume. HIGH adds further shell folding; LOW retains both cell families.
Filtering suppresses oscillations, leaving positive axial costs, not distant
solid sheets. These are construction properties, NOT a realism judgement.

## Bounds and safeguards

f>=5.8−rho. Retain the conservative5.445 envelope, .08 guard, .4 maximum
reach, hence rho>=4.965 throughout each material reach. H_rho<=1/4.965.
The cap seam remains C1,piecewise C2. Corridor x±4,entry8,exit−22 unchanged.
Because every cost is nonnegative, a>=1.6/(r²+2.25)−.16 and
b>=1.1/(r²+2.25)−.105; both exclude the bright axis for r<=2.78.

For h_m use the v32 global complex L_m,H_m formula (implemented independently
in analytic_bounds). For bounded products, L_uv<=A_u L_v+A_v L_u and
H_uv<=A_u H_v+A_v H_u+2L_u L_v. Trig has A=1,L=L_v,H=H_v+L_v².
Complex rotations exp(iP) obey the same norm bounds. Norm squares |h|² use
the complex inner-product bounds; no assumption of constant harmonic amplitude.
Gaussian derivatives: L<=L_v+A_v k exp(−.5)pixel;
H<=H_v+2L_v k exp(−.5)pixel+A_v k²pixel². Products retain all cross terms.
Rational6.3/(r²+2.25) has global L<2.5,H<8; scale for both cores.

Independent calculus gives H polynomials (constant,pixel,pixel²):
f=(3.153084,0,0),a=(387.545719,521.660371,467.426735),
b=(4320.035336,6235.209566,4989.570996).
Shader upper bounds:(4,1,1),(388,522,468),(4321,6236,4990).
Global L<=185+148pixel (calculus maximum184.401618+147.567454pixel).

Positive reach=min(.4,2*.95v/(|d|+sqrt(d²+2H*.95v))). No absolute-band
cusps remain. Intersection reach is MAX,union MIN. Original2048/1536 budgets,
14bisections,.00015 residual,directional-depth tolerance and no forced minimum
step remain unchanged. Larger child bounds may cost more; measure, don't assume.

Required before visuals: independent scalar/FD/reach/clearance/filter samples,
actual GPU jets,exact CSG replay,even/odd grids,HIGH/LOW,entry/deep/late clocks,
fixed-grid and separate interval first-root checks. Ordinary float64 intervals
and samples are not universal convergence,temporal-AA or hardware-GPU proof.
