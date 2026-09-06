# v29 perforated membrane field — new bounds, not inherited validation

Two finite-thickness membranes are separated by 2.6 radial-field units;
a closed backing is another 3.4 units beyond the outer one. Actual aperture
constraints remove material. They are not colour masks or march misses.
All three use phase-nested sixfold Cartesian rosettes, without a polar chart.
The finer rosettes displace surfaces and the parent's field modulates the
child's phase. Gaussian footprint filtering includes its analytic gradient.

## Smooth leaf bounds

For `Rk=(cos(k*x)+cos(k*(x/2+sqrt(3)*y/2))+cos(k*(-x/2+sqrt(3)*y/2)))/3`,
absolute value <=1, gradient norm <=k, Hessian operator norm <=k².
The time rotation is orthogonal. For a nested term
`r=Rk*cos(b*z+c*parent+phase)`, triangle/product rules give

`L = k+abs(b)+abs(c)*Lparent`

`H = L²+abs(c)*Hparent`.

This yields `(L,H)` at most `(0.86,0.7396)`, `(3.262,11.529)`,
`(9.0882,95.28)`, `(22.17938,577.70)` for the four rosettes.
For `w=exp(-q²*|p-camera|²/2)`, `Lw<=exp(-1/2)*q`, `Hw<=q²`.
The filtered product has bounds `Lr+Lw`, `Hr+2*Lr*Lw+Hw`.
There is no distance singularity at the camera in the Gaussian derivative.

Total displacement amplitude <=.86+.55+.32+.14+.06=1.93. Inner shell half
thickness .14 gives `rho>=4.93`; the skip envelope conservatively uses 4.925.
The cap starts at z=-27.5, after physical exit -22. Hence all walking-space
transverse clearance is >=4.93. For any marched segment of length <=.4
beginning within the envelope's .08 guard, `rho>=4.445`; radial Hessian
norm <=1/4.445. The anisotropic cap is C1, piecewise C2, and a contraction;
the integrated Hessian bound covers its seam.

The displacement's unfiltered Hessian bound is <55.2. With radial and filter
terms, the base field Hessian is <56+67*pixelScale+66*pixelScale².
The aperture B bound is <95.54+122*pixelScale+121*pixelScale²; A is smaller.
All smooth leaves therefore use `M=100+160*pixelScale+400*pixelScale²`.
All leaf gradient norms are <=`12+12*pixelScale`, also a global Lipschitz
bound for their abs/max/min composition in the guarded region. HIGH's
last geometric octave is omitted in LOW, so these bounds still apply.

## CSG first-entry advancement (not a CSG Hessian claim)

The union field is `min(max(abs(f)-.14,A),max(abs(f-2.6)-.18,B),6-f)`.
For a positive smooth leaf v with directional slope d, a safe forward
distance solves `abs(d)*s+M*s²/2=.95*v`, capped at .4. For a nonpositive
leaf its positive reach is zero. For a shell leaf, the abs cusp cannot be
reached without first crossing the positive shell boundary, so the same
formula safely excludes entry into that shell. CSG itself has nonsmooth
branch switches and does NOT receive a smooth Hessian bound.

To enter an intersection both constraints must be nonpositive: the maximum
of their individually safe reaches excludes entry. To enter a union any
component can suffice: take the minimum of the component reaches. This
is valid from the free side used by camera rays. It is not an inside-solid
exit marcher. Cameras remain in the guaranteed free corridor. Sign brackets
retain 14 bisections; both residual and directional-depth near-root tests
are retained. No minimum step or Newton hit acceptance is added.

## Required evidence / limits

New independent float64 scalar, finite-difference gradient/bound samples,
actual float32 GPU rays and dense first-sign-crossing references are required.
Thin surfaces and CSG creases require branch-aware interpretation of finite
differences: do not silently discard discrepancies. A .003 reference scan
can miss a grazing interval thinner than its spacing; it is not a proof.
Record failures without overwriting. Numerical success does not establish
realism, true continuous temporal quality, hardware performance or exit timing.
Only fresh 1200x800 HIGH entry/deep temporal renders can inform the next
visual review. The live runtime, ledgers and prior failures remain unchanged.
