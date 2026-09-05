# V23 diagnostic isolation — live runtime remains v22

Four uniquely named HIGH diagnostic plates were rendered to completion and
inspected exactly once. Do not re-view or overwrite them. These are diagnostic
ablations, not fresh realism grades or qualifying temporal pairs.

## Evidence and observations

| Plate | Observed pose / clock | Findings |
| --- | --- | --- |
| diagnostic-chrysanthemum-v23-entry.png | [0,1.7,8], 3.5568 | Thin coloured contour loops cover the material view but not the neutral-lit or normal view. Neutral Newton/no-Newton views share the same folds and simple axial fan. Linear depth has broad layers rather than the material's fine loops. Root-difference panel is predominantly green with sparse yellow/coloured flecks; isolated magenta rim pixels occur in geometry channels. |
| diagnostic-chrysanthemum-v23-deep.png | [0,1.7,-6.61344], 8.1569 | Same distinction at larger axial scale: contour lines vanish under neutral lighting; smeared corrugations and stretched fan remain. Root differences remain sparse rather than following the extensive material loops. |
| diagnostic-chrysanthemum-v23-material-entry.png | [0,1.7,8], 3.3318 | Removing environment reflection removes the extensive thin contour loops. Removing recess darkening or the separate specular highlight does not. Environment radiance alone reproduces dense orange/blue outlined loops over the same forms. Pigment plus neutral lighting lacks those loops but remains soft and sculpturally simple. |
| diagnostic-chrysanthemum-v23-material-deep.png | [0,1.7,-6.55968], 7.9483 | Confirms the material attribution in the larger flower: no-environment view loses the outlines, no-recess/no-highlight retain them, and environment-only strongly exaggerates them. Rounded lip layering persists, but axial structure is still a flat radial fan; smeared broad wrinkles persist independently of reflection. |

## Interpretation

The dominant widespread contour pattern comes from the current oscillatory
`radiance(reflect(rd,normal))` lookup. Its angular sine bands and narrow
power-18 cyan component turn smoothly varying reflected directions into many
thin bands. This is not evidence of extra geometry, dark space or infinite detail.
Recess darkening and the independent power-10 highlight are not the principal
cause of those widespread lines in these samples.

Newton is not exonerated: the root panel compares the unchanged Newton-enabled
1024-step solver with a 4096-step solver that disables Newton but preserves the
envelope, directional bound and .00015 residual tolerance. Green means both hit
within .002 world units; yellow means Newton's hit is farther, violet nearer,
red reference miss, cyan Newton miss, magenta both miss. A difference alone cannot
distinguish different roots from tolerance error near tangency. Both can share a
floating-point or bound defect. No first-hit proof or universal convergence claim
is made. Sparse differences cannot explain the extensive material loops here.

## Scope and integrity

- Six synchronized 600×400 panels per 1800×800 plate; each panel uses the same
  camera, animation clock, ray projection and matching 400-pixel footprint.
  This is below the 1200×800 production-review resolution.
- HIGH, paused, settled clocks; real UI navigation and real walking to deeper
  poses. No injected position, orientation, navigation shortcut or animation time.
- Normal postprocessing and UI remain; compare forms, not exact panel RGB values.
  Panels have different screen-space vignette/UI exposure. Environment-only is
  unscaled radiance with ordinary haze/postprocessing, not the production strength.
- Four receipts bind images and diagnostic shader/page dependencies by SHA256.
  No browser errors, missing evidence or uncited meshes were reported.
- Diagnostic pages are separate files. index.html, continuum.js, trip.js,
  fractal.js and every prior capture remain unchanged. latest.png remains the
  previously reviewed live v22 deep-motion frame. No acceptance replay or regrade.

## Next implementation

1. Replace the high-frequency angular environment lookup with a smooth,
   roughness-aware broad-lobe jewel/chrome response; do not simply substitute
   matte lighting. Inspect fresh full-resolution evidence to verify the fix.
2. Rebuild the axial fan and smeared corrugations as richer rounded folding
   structure, retaining connected geometry, clearance and the exit beyond z=-22.
   Substantial intentional dark recesses remain missing and need actual form/light.
3. Resolve remaining root ambiguity without trusting the .24 Newton radius as a
   first-hit guarantee; keep any adverse results immutable.
4. Capture new full-resolution HIGH entry/deep temporal pairs, regrade all15,
   then run changed-runtime focused acceptance. Source50/20 stays unchanged.

Live v22 remains GAME / coverage84.7% FAIL. Other18 realism targets, sixteen
source gates, route review and full acceptance are still unfinished.
