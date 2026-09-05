# Manual realism review ledger

`realism-grades.json` is the manual source; `realism.py`, called by `fidelity.py`,
generates `REALISM.md`, `realism-results.json` and the browser Sources judgments.
Do not infer a grade from code, counts, screenshots not inspected, or old receipts.

Each of the 15 stages and 4 beings has a `targets[id]` entry:

- `grade`: RECOGNISE / CLOSE / GAME, or null until inspected. Null displays PENDING.
- `reason`: concrete reasons answering REDIRECT4's recognition-versus-game question.
- `temporal_observation`: changes actually visible between the inspected frames.
- `captures`: each contains `file`, image `sha256`, sibling JSON `receipt_sha256`,
  and `inspection` (pixelvision label and actual observations).
- Beings additionally need `close_up: true` and each capture needs a
  `close_up_observation` describing legible face, hands and geometry integration.
- Preserve earlier iterations and adverse observations under `history`.

Gate validation requires all 19 RECOGNISE, nonempty reasons, unaltered PNG/JSON
receipts, the current renderer signature, HIGH actual diagnostics, paused and
settled captures, no console errors or uncited geometry, and at least two distinct
images at the same camera/stage separated by >=2 animation seconds. Being receipts
must show the relevant actor in an allowed stage. Timestamps come from the bound
capture diagnostics, not reviewer-entered numbers. A close-up flag is necessary,
not a substitute for manual inspection. Earlier grades stay visible when stale,
but cannot pass. `check_realism.py` checks the gate using isolated receipt fixtures.

The overall `fidelity.py --check` requires realism **and** the unchanged source,
descriptor coverage, measured route rationale and full functional acceptance.
No subjective-experience equivalence or witness endorsement is implied.
