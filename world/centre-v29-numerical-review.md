# Isolated v29 — numerical phase closed, visual grade pending

Live continuum v25/trip v16 remain unchanged. No v29 images have been rendered
or graded. `latest.png` remains the last inspected, labelled v28r3 deep-motion
diagnostic. That candidate remains GAME and is not promoted.

## Substantive successor

- Two finite-thickness membranes with actual geometric apertures and radial-field
  separation 2.6; closed, low-radiance backing another 3.4 units farther out.
- Four phase-nested sixfold Cartesian rosettes displace geometry; LOW retains
  the first three. No polar chart singularity or angular pigment convergence.
- Radius/clearance >=4.93 before the cap at z=-27.5, beyond physical exit -22.
- Narrow HDR reflections, metallic/iridescent tint and reduced diffuse/emission
  replace broad wax-like lighting. These are implementation intentions, not
  observed realism or dark-descriptor evidence.
- New analytic smooth-leaf bounds and conservative CSG intersection/union
  first-entry stepping. The old smooth-field curvature is not inherited.
  Original HIGH2048/LOW1536 budgets, residual/directional-depth limits and
  bracket bisections remain. No minimum step, Newton hit or changed route.

## Evidence and retained adverse results

`check-centre-v29-bounds.log` retains an initial missing-numpy import failure;
no samples ran. Existing environment correction uses
`PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages`, not an install.
The completed one-shot bounds run is `check-centre-v29-bounds-r2.log`.
Its 24,000 smooth-leaf samples pass: maximum sampled derivative/bound ratio
0.202365, curvature/bound ratio0.096597. Four substep samples per free-side
point stay outside occupied material. Sampling is not an interval proof.

`probe_numeric_candidate_v29.py` executed once: **original composite-gradient
gate FAIL**, preserved in `numeric-candidate-v29-check.json` and its raw/log.
38,160 HIGH/LOW rays at entry/deep, even/odd grids and times4/8/221/900 all
hit within budgets (max399 iterations). All360 fixed-.003 first-crossing
references pass unchanged .03 tolerance, max difference0.001253116.
Scalar and bound gates pass; no console/page errors.

18 central-difference gradient comparisons exceed .005, maximum0.647419.
The new intersection has CSG creases: a finite-difference stencil spanning
different surfaces is not the analytic normal of either surface. At one
saved point a float64/float32 branch near-tie also selects opposite leaves.
This cannot be resolved by calling the original composite-gradient check a pass.

`check_centre_v29_leaves.py` subsequently audits **every smooth leaf at every
saved actual GPU root**. It does not replay ray marches or reference scans.
Independent float64 scalar/finite differences check all three GPU jets;
composition is independently replayed from the actual GPU leaf values and
compared with the original GPU normals. All pass unchanged tolerances:

| New audit | Maximum error |
| --- | ---: |
| All smooth-leaf scalar values | 0.000121032 (<0.001) |
| All smooth-leaf gradients | 0.000462990 (<0.005) |
| Replayed CSG selection | 0.000000103 |
| Replayed versus original GPU normal | 0 (exact) |

The audit retains all18 original disagreements and branch margins explicitly.
No alternate normal is arbitrarily accepted and no tolerance is enlarged.
The valid gate is smooth-leaf derivatives plus actual CSG branch selection,
not a claim that a crease has a unique differentiable normal. A numerical
pass here is this documented branch-aware method, not a reversal/deletion
of the original composite-FD failure. All earlier failures remain intact.

## Next bounded phase

Run the prepared `render_centre_v29.py` ONCE after its integrity gate, using
the existing numpy environment and `PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright`.
Four fresh1200x800 HIGH entry/deep temporal captures; unchanged90s settling
limits and real controls only. Wait for process completion, then inspect each
new PNG exactly once. Grade apertures/depth, nested density, axial form,
material sharpness, repetition and temporal evidence adversarially. A numerical
pass cannot establish that this construction fixes the rejected visual form.
Update the display only from a completed, inspected, labelled new capture.

Do not repeat completed v28r3/v29 numerical samples or historical image views.
Original45s physical exit remains FAIL; repair/test without extension before
promotion. Other18 realism targets, sixteen source audits and route/full
acceptance remain unfinished. Live coverage84.7% FAIL, top10 dark ABSENT,
source decisions50/20 unchanged. No completion marker.
