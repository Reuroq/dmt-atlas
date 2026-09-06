# v34 offline fixtures — prepared, numerical run blocked

This is a bounded fixture-preparation subphase, not a numerical pass. Candidate,
oracle, shader bound design and original renderer are unchanged from the closed
implementation. No shader compilation, field sampling, browser or image work.

`check_centre_v34_bounds.py` prepares the original 6,000 points × 3 footprints ×
2 cameras × 2 detail modes = 72,000 base leaf/reach samples. The five base fields
expand into eleven signed/offset leaves before reaches are composed. It checks
finite-difference gradient/curvature ratios, four samples per certified segment,
cheap≤full reaches, free cheap segments and independent CSG scalar replay.
Finite-difference slopes do not replace the later actual GLSL-jet audit.

The 12,000 clearance samples retain x±4, z8..−22 and the inner rho5.449 ring.
Additional cap-join samples deliberately straddle z−27.5 at rho5.365. Gaussian
attenuation/derivative checks retain the 1e−7 error gate using the new4/6/9
frequencies and zero/base/2×/4× footprints.

Attachment checks parameterize actual local=2πk planes before the cap, bisect
the parent-shell roots in radius, then require a child-permitted root in every
time/camera/mode group. Both parent AND child must occupy each root and small
3D offsets around it. They retain up to six root positions per group and total
counts. This establishes only sampled local overlap; it cannot establish that
every disconnected component joins a parent. Global topology remains unproved.

`csg_interval_v34.enclosure` expands BOTH endpoints into eleven smooth leaves
before taking minima/maxima and subtracting/adding M·width²/8+1e−12. Negative
shell signs therefore reverse correctly. Only then does monotone CSG compose
the lower/upper bounds. Four synthetic contracts cover an interior crossing
hidden by positive composite endpoints, a negative-shell controlling branch,
an occupied child under a positive parent, and a quadratic shell excursion.
These contracts do not evaluate the v34 field. Ordinary float64 enclosure is
not a directed-rounding proof; the future first-root audit must fail unresolved
intervals/tangencies and retain original gates.

The one-shot bounds runner requires a FUTURE complete
`centre-v34-fixture-integrity.json`, with fixtures_complete=true. The current
`centre-v34-offline-fixtures.json` is deliberately insufficient. No bounds
started/check/failure receipt exists. After complete fixture preparation, run
ONCE with a unique log and saved actual exit; preserve partial attempts.

## Next

Prepare the GPU five-base/eleven-expanded-leaf jet fixture and48-case runner,
720 fixed +720 independent interval first roots, and the12-pair matched v34
shared/unshared cost fixture with durable lifecycle. Use the implementation
review for exact unchanged gates and baseline limits. Incorporate this helper
into interval auditing; do not apply old a/b Hessians. Close full fixture
implementation before running bounds, then GPU, first-root and cost gates in
dependency order. Only all PASS permits original1200x800 HIGH/90s capture.

No historical gate replay, prewarm, promotion, altered frame pump or relaxed
limits. latest.png remains the inspected REJECTED GAME v33r6 entry. All19
realism/source/coverage/route/full acceptance remain unfinished.
