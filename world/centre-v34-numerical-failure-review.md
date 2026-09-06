# v34 numerical phase CLOSED — FAIL; downstream held

The foreground bounds run exited **0**; the foreground GPU run exited **1** at
its final `assert out['passed']`. Both actual exits, launch records and log hashes
are verified. No probe was rerun for this closure. The first closure attempt exited 1 at a
README paragraph-boundary assertion before any documentation/output write. Its
source/log/launch/actual exit are preserved and bound. This r2 closure uses the
unique README line; numerical checks and limits are unchanged.

Bounds retain sampled PASS: 72,000 leaf/reach and 12,000 clearance samples;
12 cap, 12 filter and 28 attachment groups pass. This is not a universal proof.

The GPU completed 48 cases / 75,996 rays, with no recorded browser errors or GPU
misses. All 48 cases fail exact expanded-jet replay. Saved float32 readbacks show
36,599 mismatching childAxial components (maximum 1.1920928955078125e-7) and
40,662 childAngular components (maximum 5.960464477539063e-8). The other nine
expanded leaves match exactly. The equality requirement is unchanged; small
differences are not waived or diagnosed as harmless rounding.

Composite, aperture, saved-gradient and cheap/full jet replay are exact.
Recorded smooth-leaf gradient/scalar, directional-bound, lower-field domination
and count checks pass. These partial results do not turn the failed gate into PASS.

Only 716/720 fixed-grid references were found; their worst depth difference is
0.0011048514545066723 (limit <0.03). Missing references:

| Grid | Camera | Time | Mode | Ray |
| --- | --- | --- | --- | --- |
| 48×32 | entry z=8 | 4.895 | LOW | 839 |
| 48×32 | deep z=-6 | 8 | LOW | 745 |
| 49×33 | deep z=-6 | 8 | HIGH | 807 |
| 49×33 | deep z=-6 | 8 | HIGH | 809 |

The saved missing flags mean the original 0.003-spaced scan found no strict
adjacent-sample sign change from depth zero to GPU depth+1. No new scan was run.
They do not prove absence of a surface, tangency, a marcher error or an oracle bug.
The replay differences and missing-reference causes remain unresolved.

All 100 durable lifecycle events are bound, with 48 started/completed pairs
matching the raw cases and a browser-closed event. This establishes recorded
completion, not numerical success. Independent interval roots, matched cost and
capture did NOT run. No performance, temporal or v34 realism claim is possible.

The failure integrity manifest binds fixture evidence, protected files, numerical
receipts, raw cases, lifecycle, launch/log/actual exits and this saved-evidence
analysis. It is NOT `centre-v34-integrity.json` and never authorizes capture.
Historical fixture/display hashes remain in their immutable manifest; pre-closure
NOTES are archived byte-for-byte with BOM. README/status/NOTES now describe failure.
latest.png remains the once-inspected REJECTED GAME v33r6 entry diagnostic;
there is no new image to inspect or substitute. Live/defaults/source/manual
ledgers remain unchanged; all19/source/coverage/route/full acceptance unfinished.

Next: bounded read-only source/saved-evidence investigation of the two failure
classes, separately. Preserve every v34 artifact and original gate. Do not run
dependent gates or replay failed/completed probes. Establish a justified change
before preparing a new isolated revision and new one-shot experiment.
