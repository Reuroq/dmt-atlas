# Fifth instruction from the owner: render, grade, improve, move on

The owner reviewed the Sep 5 run. Turns 1–80 on this server produced one accepted change to the
screen (before 11:09 UTC) and about sixty "CLOSED — PASS" documents about a shader's floating-point
arithmetic. `latest.png` did not change after 15:06 UTC. Eighteen of nineteen realism targets were
never inspected. That run is over. This instruction replaces the working method; the bar in
`REDIRECT4.md` (how the target looks) and the coverage test in `REDIRECT3.md` still stand.

## What went wrong, so you do not repeat it
- The CPU-vs-GPU "field agreement" limit was your own invention, not the owner's. It was measured
  against SwiftShader, a software renderer; the viewer runs on an RTX GPU. That discrepancy is out of
  scope forever. Do not measure it, mention it, or build anything for it.
- "Never replay", "preserve every attempt", "distinct version", "static closure", "receipt hashes",
  "root contract", "canonical successor": none of that reaches the screen. All of it is banned below.
- The done condition "every target RECOGNISE" gave you no honest way to stop on a target you could not
  fix, so you stopped rendering instead. That condition is replaced.

## The method — every turn, in this order
1. Read this file, then `world/targets.json`, then ONLY the last section of `world/NOTES.md`.
   The driver's prompt names the current target. Work on that target only.
2. Open the relevant code (`trip.js`, `fractal.js`, `continuum.js`, `beings.js`) with targeted
   searches. Do not open any `centre-*`, `numeric-*`, `probe_*`, `audit_*`, `additive_*`,
   `canonical_*` or `NOTES-before-*` file; they are archived history from the failed method.
3. Render the target at HIGH detail from a real journey pose: two frames, same camera, at least two
   animation seconds apart (the REDIRECT4 temporal receipt). Write the newest frame to
   `world/latest.png`. **A turn in which `latest.png` does not change is invalid** — the driver
   checks its hash and will repeat the instruction; two such turns in a row forfeit the target.
4. Look at both frames and grade the target RECOGNISE / CLOSE / GAME with specific visual reasons,
   against the REDIRECT4 description of the replications. Record it in `world/targets.json`
   (`grade`, `note`) and in the REALISM table.
5. If the grade is not RECOGNISE and this target has budget left: make ONE substantive visual change
   (shader, material, motion, density, form), re-render, re-grade. Bigger moves beat small ones;
   another colour tweak is not a move.
6. Rewrite the last section of `world/NOTES.md` (plain language, under 40 lines): what changed on
   screen, the grade and why, what you would try next on this target. Update `world/status.txt`.

## Budget and order
- Each target gets **4 turns**, then the driver moves to the next one whatever the grade. A target
  that ends GAME after 4 turns is recorded as GAME with a one-paragraph reason. That is a legitimate
  outcome. It is not a failure to be prevented by more verification.
- Order: every PENDING target first, in journey order — onset, geometry, rush, membrane, waiting,
  cathedral, contact, download, return, afterglow, workshop, garden, clinical, void, elf, jester,
  mother, mantis — then chrysanthemum last with 4 fresh turns. The driver enforces the order; do not
  argue with it or work ahead.
- When every target has a non-PENDING grade, the driver posts one closing turn: run `fidelity.py`
  (coverage) and `verify.py` (acceptance) once, fix only what they break, update README.md and the
  Sources drawer table, and write `<<WORLD_DONE>>` alone on the last line of NOTES.md.

## Banned for the rest of this build
- New test harnesses, probes, oracles, fixtures, launchers, manifests, integrity files, receipts of
  receipts, "distinct versions", "static closures", hash ledgers, numerical agreement checks of any
  kind. The only checks are `fidelity.py`, `verify.py` and your eyes on the two frames.
- New directories under `world/`. New files over 5 MB (except `data.js`). More than 2 PNGs per
  target per turn (`realism-<target>-v<N>.png` and `-motion.png`). The disk is nearly full; the
  driver deletes any `world/` subdirectory over 50 MB and any file over 20 MB except `data.js`.
- Rewriting your own rules into "never re-view images" or "read only lines N–M". Look at the frames
  every time; that is the whole job.
- Multi-page NOTES sections, review documents, design documents, protocols. One NOTES section per
  turn, under 40 lines.

## Unchanged
- Hard lines from `BRIEF.md`: write only under `world/`, no git, headless only, no Reddit fetching,
  every element keeps its way back to the evidence, honesty labels stay, generated reference images
  are labelled synthesised.
- Keep the Sources drawer, the coverage test and the previous acceptance working.
- Renders here come from SwiftShader: judge form, colour, motion and density, never frame rate or
  arithmetic.
