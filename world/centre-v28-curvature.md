# v28 second-order ray advancement

The v28r3 field, gradient, envelope, HIGH/LOW budgets and tighter v28r2 hit
criterion are unchanged. This is not unbracketed Newton root acceptance.
For unit ray direction and a segment of length at most 0.4, a bound M on
the second directional derivative gives

`|F(p+s*d)-F(p)| <= |gradient(F) dot d|*s + M*s*s/2`.

Choose the positive root where that upper bound equals `0.95*abs(F)`.
Either this step or the old directional-Lipschitz step is safe independently;
their maximum, capped at 0.4, remains safe. No forced minimum step, extra
iteration budget or relaxed numerical gate is introduced.

## Conservative bound for this field only

The field is evaluated only when `abs(rho-7)-2.385 <= 0.08`.
Thus rho >= 4.535 and throughout the next 0.4 segment rho >= 4.135.
The anisotropic cap map contracts lengths. Along a unit ray:
`|u'| <= 1`, `|u''| <= 0.25`.
The cap seam is C1 and has bounded one-sided second derivatives; the
integrated bound also covers segments crossing it.

For `P=r²/(r²+4)`, `C=cap²/(cap²+4)`:
`|P'|,|C'| <= .325`, `|P''|,|C''| <= .5`.
For `W=2.6 cos(.65x+t*.11) cos(.65y-t*.09)`:
`|W'| <= 1.69`, `|W''| <= 1.0985`.
Consequently `V1=5.275`, `V2=4.002` bound the first and second
derivatives of the meridian `v=.72z+shear*u-time*.57+C*W`.

Let a be the transverse polar angle. The weighted angular terms obey
`P*|a'| <= .25`, `P*(a')² <= .25`,
`P*|a''| <= .5`, `|P'*a'| <= .5`.
These bounds cover the continuous extension at the pole: the attenuated
angular functions have Lipschitz gradients even though the unweighted
angle is undefined there.

For `B=P*cos(8a+.32*sin(v/2+t*.31))`:

- `B1 <= 2.325+.16*V1`
- `B2 <= 28.5+.744*V1+.1056*V1²+.16*V2`

For `D=P*cos(8a+.32*sin(v/2+t*.31)+.6*sin(v))`:
`D2 <= 28.5+3.534*V1+1.2576*V1²+.76*V2`.

The two primary displacements contribute at most
`1.18*((V1+.65*B1)²+V2+.65*B2)+.4*D2`.
The separate .28 crossed cap term contributes at most
`.28*(.5+2*.325*1.7+1.7²)`.

For each 3D cosine-product octave, the gradient norm is <= k and the
Hessian norm is <= 2.49*k² (Fourier wave-vector bound for scales 1,1,.7).
The radial Gaussian weight with q=frequency*pixelScale has gradient norm
<= q*exp(-.5), Hessian norm <= q² and value <= 1. Therefore the octave
second-derivative bound is
`amplitude*(2.49*k²+2*exp(-.5)*frequency*pixelScale*k+frequency²*pixelScale²)`.

Summing HIGH's three octaves, the base rho, and all primary/cap terms gives
less than `143 + 25*pixelScale + 92*pixelScale²`.
The shader uses `160 + 25*pixelScale + 92*pixelScale²` with extra margin.
LOW drops a nonnegative contribution, so the same bound applies.

## Limits

The derivation concerns the ideal smooth field and its C1 seams. Float32
arithmetic and near-root stopping still require actual GPU/reference checks.
Sampled checks do not prove universal first-hit correctness or temporal
antialiasing. Neither these bounds nor a numerical pass establishes realism
or full-resolution performance. Earlier failed v28/v28r2 probes stay intact.
