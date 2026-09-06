# v34 saved-evidence investigation — no numerical rerun

`investigate_centre_v34_saved.py` ran once, actual exit 0. It verified the
closed-failure manifest's 340 files, 16 protected files and 4 display files
before analysing saved readbacks. No field evaluations or browser work ran.
The v34 numerical result remains **FAIL**; no limits changed.

## Expanded jets: narrower hypothesis, not a diagnosis

All 36,599 childAxial and 40,662 childAngular mismatches are in **w only**.
All xyz gradient components are exact. Source construction is respectively
`offset(offset(x,-.62),.20)` and `offset(offset(x,-.90),.28)` for a scalar
predecessor x; replay instead adds the second offset to the saved parent.

For each saved parent/child pair, intersect inverse binary32 rounding cells
under the restricted model A=round(x+c1), B=round(x+round(c1+c2)). Constants
c1/c2 are binary32. All 75,996 pairs for each leaf have strictly overlapping
cells. Thus constant folding of the two binary32 constants is compatible with
every pair. This is **not proof of compiler behaviour**: x is an unknown real
latent value, not the actual saved shader predecessor; neither generated
machine code nor intermediate arithmetic was recorded. Closed cells deliberately
overapproximate tie endpoints. No equality failure is waived.

The alternative using the rounded decimal sum -.42 is refuted for 26,124
axial pairs (23,268 mismatching pairs). Binary32 constant addition yields
-0.42000001668930054, whereas rounded decimal -.42 is -0.41999998688697815.
For angular, both tested constant sums equal -0.6200000047683716.

## Four missing references: termination path established, cause unresolved

All four saved hit flags are 1, with **zero refinement calls**. Instrumentation
increments refinement calls inside the 14-step bisection branch. Consequently
these hits did not take that branch: the source's local residual/directional
test accepted them. That test is not a first-root existence certificate.

| Grid / camera / time / mode / ray | Depth | Saved residual | Active saved leaf |
| --- | ---: | ---: | --- |
| 48×32 / entry / 4.895 / LOW / 839 | 42.23194885253906 | 3.135204315185547e-5 | parentF |
| 48×32 / deep / 8 / LOW / 745 | 31.51067352294922 | 2.6620924472808838e-5 | childPositive |
| 49×33 / deep / 8 / HIGH / 807 | 34.128604888916016 | 8.821487426757812e-6 | childAxial |
| 49×33 / deep / 8 / HIGH / 809 | 34.128604888916016 | 8.821487426757812e-6 | childAxial |

Other parent/child constraints near these hits are still negative, including
parentNegative=-.0009799451 for 839, childAxial=-.0004776716 for 745, and
childPositive=-.0007008538 for 807/809. These point values do not establish
interval widths, a crossing, tangency, or a missed surface.

Saved GPU points differ from float64 CPU-ray reconstructed points by up to
5.153982122863e-6 among these four rays. This records different point arithmetic,
not evidence that it caused the missing references. GPU ray vectors,
termination-time sampleValue, pre-hit histories and failed CPU scan values
were not saved. The final saved residual is a fresh sheetSample at the hit,
not a readback of the termination-time sampleValue. Ratios reconstructed using
CPU rays are labelled accordingly in the JSON.

## Decision

Prepare the two independently bounded experiments in
[the new design](centre-v34-followup-experiment-design.md). The arithmetic
experiment tests a runtime-uniform second offset, without changing its value
or geometry in real arithmetic. This is a falsifiable candidate change, not
a presumed fix. The root diagnostic gathers new local profiles for only the
four unresolved rays; it is not a replay of the failed full-grid scan or the
blocked independent first-root gate.

No new candidate is promoted or declared passing. No v34 probe, bounds test,
interval-root gate, cost, capture, image inspection or desktop acceptance ran.
latest.png and live/defaults/source/manual ledgers remain unchanged. Both
failure causes still require new evidence; all19 acceptance remains unfinished.
