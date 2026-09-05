# Third instruction from the owner: test it against what people actually see

His words: "make sure it tests it to match what all those other people see and experience."

Your own acceptance so far tests that the build works. It does not test that it is faithful. Add a
fidelity test whose ground truth is the reports, not your judgement, and do not write the done
marker until it passes.

## The ground truth you have
- `data/corpus/reports.jsonl`: 14,309 tagged reports with ordered node sequences (ids point into
  `data/corpus/raw/*_posts.jsonl`, which holds the full text of every post).
- `data/corpus/summary.json`: how many reports mention each node (prevalence).
- `data/atlas.json`: the cited descriptions per entity/realm/geometry/motif, with sources.
- `data/corpus/depictions.json`: 10,906 people-made depictions with titles (links only; you cannot
  fetch them, but their titles and the atlas descriptions tell you what people paint).

## The test (`world/fidelity.py` + `world/FIDELITY.md`)
1. For each stage of the route and each being, gather the report passages that mention its nodes
   (at least 40 passages per stage where the corpus has them; use the raw text around the node hit).
   From those passages, tally the recurring descriptors people use: colours, light, motion, density,
   forms, materials, scale, sound-as-seen, how beings look and behave. Print the top 15 per stage
   with counts. That table is what "people see" for that stage.
2. Render each stage at HIGH detail (and the beings up close) and grade every top descriptor as
   PRESENT / PARTIAL / ABSENT by looking at the render. Be adversarial: a jewelled lattice that is
   static fails "constantly moving"; a single colour fails "impossibly many colours".
3. Score each stage: prevalence-weighted coverage of its top descriptors. Print the table, worst
   stage first. Fix the worst gaps, re-render, re-grade. Repeat until no stage's top-10 descriptors
   contain an ABSENT and coverage is at a level you state and justify in FIDELITY.md.
4. Also grade the ORDER and the TIMING: the route must follow the measured transitions in
   `data/corpus/transitions.json` and the phase order that reports narrate; say where it departs and why.
5. Put the per-stage "what reports say / what you see" table into the Sources drawer so a visitor
   can check the same thing, and summarise it in README.md and NOTES.md.

Same hard lines as `world/BRIEF.md`. `<<WORLD_DONE>>` alone on the last line of NOTES.md only when
the fidelity test passes on every stage and the previous acceptance still passes.
