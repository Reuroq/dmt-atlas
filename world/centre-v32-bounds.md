# v32 — local nested curled-petal volume, prospective bounds

Synthesised geometry interpretation of the already-audited flower, fractal,
layered entrance, folding and dark-opening reports. No new source decisions.
Materials unchanged from v31; no visual grade before fresh HIGH inspection.

## Topology

Let h_m=((x+iy)/sqrt(x²+y²+2.25))^m, m=6,18,54, after actual clock rotation.
rho=length(x,y,.85 min(z+27.5,0)). Define local coordinates

- R=1.05rho+.22z+.65 Re(h6)−.13t
- T=.65z−.4rho+.6 Im(h6)−.18t
- C=R+1.1cos(T), D=3C+.65cos(3T)+.4 Re(h18)−.17t
- E=3D+.35 Re(h54), S=T+.5cos(C), Q=3T+.6C+.4 Im(h18)

G_k multiplies its argument by exp(−.5 k² pixel² |p−camera|²), with full jets.

f=6.2−rho+.65 Re(h6)+.1cos(T).
a=G4(cos(C)−.85cos(T)−.3 Re(h6))+.18G12(cos(D))
  +6.3/(x²+y²+2.25)+HIGH*.035G36(cos(E)).
b=G4(cos(S))+.26G12(cos(Q)).

P=max(f,|a|−.10,.035−|b|), B=max(f+.38,|a|−.25,|b|−.014),
F=min(P,B,f+10). The local curl turns back in depth and radius; angular terms
break coaxial sheets, parent C bends child D and D bends E. Local level sets
can terminate/reconnect where the primary offset exceeds the cosine range.
Narrow split cuts and a connecting family replace globally sparse radial fins.
These are construction properties, not proof of readable flower hierarchy.
The axial core is 2.8; |oscillatory a|<=2.15+.18+.035=2.365,
so a>=.435>.25 there: bright axial endplate excluded, backing remains actual.

## Prospective derivative and reach bounds

Use S(a,b)=sup(q>=0) q^a/(1+q²)^b, maximizer q²=a/(2b−a).
For regularized complex h_m with R0=1.5:

L_m=m/R0 [S(m−1,m/2)+S(m+1,m/2+1)].
H_m=[m(m−1)S(m−2,m/2)+(2m²+m)S(m,m/2+1)
     +m(m+2)S(m+2,m/2+2)]/R0².

These global complex bounds also bound each real/imaginary part. Addition
uses absolute-coefficient triangle bounds. For cos(v), L=L_v,H=H_v+L_v².
Core rational term conservatively has L<2.5,H<8 globally.
f>=5.45−rho. Envelope5.445, guard.08, max reach.4 ensure rho>=4.965
through every material step. There H_rho<=1/4.965; cap seam C1, piecewise C2.
Walking x±4,entry8,physical exit−22 and cap onset−27.5 remain untouched.

For scalar amplitude A, Gaussian product H<=H_v+2L_v k exp(−.5)p+A k²p².
Unfiltered primary amplitude bound2.15 is included (not assumed to be1).
Independent analytic_bounds() gives per-leaf H polynomials approximately
f:(5.934,0,0), a:(301.672,186.578,105.68), b:(85.567,64.044,53.44).
Shader bounds: f:7+p+p², a:305+190p+110p², b:87+65p+54p².
Global L<=16+8p; a is the largest with constants15.800+7.291p.

Positive smooth reach remains min(.4,2*.95v/(|d|+sqrt(d²+2H*.95v))).
Ordinary absolute bands use their positive active arm; excluded b band uses
MIN of two smooth-arm reaches across its free-side cusp. Intersections use
MAX, unions MIN. No forced minimum step; original2048/1536 iterations,
14bisections,.00015 residual and directional-depth gate unchanged.

Required: independent scalar/FD/reach, GPU jets and exact CSG replay, even/odd
grids,HIGH/LOW,entry/deep/late clocks,fixed-grid plus independent interval
first roots. Samples/ordinary float64 intervals do not prove universal
convergence or temporal filtering. Full HIGH temporal inspection remains.
