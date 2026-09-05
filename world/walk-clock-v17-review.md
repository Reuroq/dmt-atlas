# Isolated walking-clock diagnosis and repair candidate

**Not promoted. Exit-only PASS; original combined focused gate FAIL.**

## Diagnosis

`trace_exit_clock_v16.py` ran once, preserving live v25/trip v16. This
was a six-second real forward hold, not a retry of the failed exit gate.
The 45 held-input callbacks account for only 0.8167 seconds and move z8 to
z5.38656. The next callback has a 5.7664-second RAF gap, capped to one second,
but the key has already been released. Thus the gap's movement is lost even
before considering the cap. This establishes an event/frame accounting defect;
it does not isolate the relative contribution of each defect in the old exit run.
The original v25 45-second failure at z−18.29216 remains unchanged.

## Candidate

`trip-v17-candidate.js` introduces a separate monotonic movement clock using
`performance.now()`, flushed before input changes, pause, Sources and drag-look.
Fresh presses cannot inherit the preceding idle gap; delayed releases account
for the old held state. Begin/restart/transition/visibility boundaries reset it.
Movement invalidates a frozen render immediately. Collision steps remain at
most 0.05 seconds, with existing boundaries and physical portal checks.
Animation, paced elapsed time and transition clocks retain their existing cap;
this is deliberately a navigation repair, not a route-timing regrade.

## Unchanged combined gate: FAIL

`verification-walk-clock-v17.json` retains the original 1000×700 HIGH setup,
Sources checks, boundary/look assertions and 45000ms exit limit. Sources and
right boundary passed. Returning left reached x−4 and failed the unchanged
−3.2≤x≤0 assertion, before look or exit was tested. The assertion originally
allowed one capped movement frame of key-release latency. The new wall-time
accounting exposes greater lateral overshoot under software-renderer stalls.
No tolerance was widened. Precise input/render timing of this case is still
unmeasured; do not claim a fully explained or fixed responsiveness regression.

## Isolated original exit: PASS

`verification-exit-only-v17.json`: real controls to Chrysanthemum, same
1000×700 HIGH viewport, straight forward hold until the physical exit starts
transition, original 45000ms limit, no navigation/pose/clock injection. Passed
in **13.24224 wall seconds**, then reached Rush with cited geometry and zero
browser errors. Native key-event observations are saved, read-only. This
does not clear the combined-gate failure or establish hardware GPU performance.

## Reduced controls: PASS

`verification-idle-walk-v17.json` passes all eight unchanged v16 focused cases:
keyboard walk, real touch walk, two-axis touch look, button transitions through
Waiting, fixed-pose being interaction, Sources, animation resume/pause, restart.
Idle checks retain exact pose/clock/frame equality and settled GPU receipts.
Zero browser errors. Not full desktop/mobile/route acceptance or a rerun of
the separate six HIGH pixel-stillness checks.

## Preservation and next action

Live assets, source/coverage/realism ledgers and default captures are unchanged.
No PNG was produced or inspected; latest.png remains the previously inspected,
labelled isolated v29 deep-motion diagnostic. All historical failures remain.
Before promotion, instrument native input delivery versus RAF/performance time
and render submission around lateral centre crossing; address responsiveness
without suppressing held time, widening tolerances or extending the 45s exit.
Then rerun only substantively changed focused checks. Visual rebuilding, all
19 RECOGNISE targets and source/coverage/route/full acceptance remain unfinished.
