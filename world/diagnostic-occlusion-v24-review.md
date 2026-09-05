# Current v23 occlusion / geometry isolation (trip v16)

Two new HIGH diagnostic plates rendered to completion and were inspected exactly
once using view_image. Never re-view or overwrite them. These are synchronized
ablations, not qualifying realism stills or a fixed-pose temporal pair. Live
continuum.js/trip.js remain v23/v16; “v24” names the diagnostic experiment only.

## Observations

| Plate | Real pose / settled time | Observation |
| --- | --- | --- |
| diagnostic-chrysanthemum-v24-occlusion-entry.png | [0,1.7,8] / 3.2220 | Current material has dark outlined lobes across green/red outer folds. No-key-visibility is much brighter but retains the sharply bounded patches. No-recess removes those hard patches while retaining broad dim bands. Removing both produces smooth, bright but still smeared scalloped walls. Normals retain a small radial fan; depth shows broad stacked layers and a largely uniform central disc. |
| diagnostic-chrysanthemum-v24-occlusion-deep.png | [0,1.7,-6.7200] / 7.8554 | Confirms attribution at larger axial scale: no-key-visibility keeps discrete dark elongated lobes on brighter surfaces; no-recess removes those lobes but leaves substantial dim blue/green regions. Neither-term view is brighter and smooth, not recursively jewelled. Normals show elongated fan sectors, and depth still has a broad shallow central cap. Tiny magenta missed-ray marks occur at some inner fold rims in geometry channels, not across the extensive material blotches. |

Both sets read GAME. Removing darkening does not produce convincing multiscale
structure, jewel density, fold-over or an inside-out flower. No descriptor or
realism grades are changed by these diagnostic observations.

## Attribution and next implementation

- **Hard black blotches: primarily recess darkening.** Four normal-offset
  signed-field samples subtract near-discrete increments from `recess`; squaring
  it and multiplying almost every material term yields sharply different dark
  regions. This is an approximation evaluated on a non-distance implicit field,
  not a calibrated measure of open space. The no-recess ablation removes the
  patches; no-visibility does not. Do not turn these patches into credit for
  holes or black openings.
- **Broad dimness: key visibility and material lighting.** The eight light-ray
  samples also gate environment reflection through `.15+.85*visibility`, although
  reflected light comes from different directions. Decouple directional direct
  light from ambient/reflected/emissive contributions. Replacing this alone
  cannot repair the form.
- **Axial simplicity: geometry.** The fan survives both material ablations and
  the normal channel; depth lacks a densely layered central structure. Code
  inspection additionally shows angular perturbations attenuated by
  `r*r/(r*r+4.)` toward the pole. This suggests why the centre simplifies; the
  plates do not prove a complete causal decomposition of the cap. Rebuild with
  actual multiscale three-dimensional folds, not only angular colour/normal
  detail. Preserve at least four units of clearance and a cap beyond exit -22.
- **Sparse rim misses remain unresolved.** Geometry channels explicitly mark
  non-converged rays magenta. The plates contain isolated rim marks. No claim of
  universal GPU first-hit correctness follows from earlier CPU probes. Preserve
  this evidence and address root robustness in the geometry rebuild.

## Method and limits

Six 600×400 panels per 1800×800 plate share pose, animation time, field, solver,
HIGH setting and ray projection. Top: unchanged v23 material / visibility=1 /
recess=1. Bottom: both=1 / camera-facing analytic normal / linear ray depth÷60.
Only panel projection and the matching pixel footprint are adjusted. UI and
normal postprocessing remain, so do not interpret panel pixels as raw numeric
normal/depth values. Labels/UI partially obscure the lower panels.

Entry→deep uses actual keyboard walking; animation advances, so these are not
matched-pose temporal evidence. Paused receipts require no pending GPU work and
matching animation clocks, with no errors, missing evidence or uncited meshes.

Initial builder failed before outputs because it named nonexistent sources.js;
the initial script and failure JSON are preserved. The corrected builder names
fidelity-data.js. No prior builder, review, CPU test or acceptance was replayed.

`diagnostic-occlusion-v24-check.json` binds both captures/receipts, generator,
renderer, log, initial failure, this review and runtime equality checks.
latest.png shows the inspected deep diagnostic plate, explicitly labelled;
visual-chrysanthemum.png/json retain the current live idle-reduced-v16 entry.
Source counts, stale historical coverage, original45-second exit failure,
intermittent historical pixel failure and all unfinished overall gates remain.
