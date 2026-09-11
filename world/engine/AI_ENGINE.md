# The room engine — built for an AI to drive, not a person

This is a scene engine with no editor, no viewport, no inspector and no tutorial. Nothing in
it is discoverable by clicking. It assumes its only operator is a model that can read a schema,
write JSON, run a command, and read numbers back.

That inverts most of the usual design choices, so the reasoning is written down here.

## What a human engine optimises for, and why none of it applies

A human-facing engine spends most of its complexity on *discovery* — menus, gizmos, live
previews, undo, docs — because a person cannot hold the whole system in their head and needs
to find the next affordance by looking. A model has the opposite problem: it can hold a large
formal spec perfectly but cannot see, cannot drag, and cannot tell whether the thing it built
looks right without being handed a measurement.

So every affordance here is text, and every result comes back as a number.

## The six properties this engine is built to have

**1. The room is data, not code.** A room is one JSON file. Models write and diff structured
text far more reliably than they write imperative graphics code, and a diff of a room spec is
readable in a way that a diff of a shader is not. `rooms/*.json` is the source of truth;
`compile.js` is the only thing that turns it into a scene.

**2. The grammar is bounded, and derived from reality.** A room composes named primitives that
already exist and are already shipped — `vault`, `arcade`, `panel`, `cabinet`, `lattice`,
`growth`, `mandala`, `language`, `timeLayers`. A model choosing from nine composable pieces
with typed options produces working scenes; a model handed a blank canvas and a shader compiler
produces plausible-looking code that does not run. `validate.py` reads the real signatures out
of `fractal.js` at validation time, so the grammar cannot drift from the engine it describes.

**3. Citation is a type, not a convention.** Every element carries `cites` (an atlas node key
that must resolve) and `because` (why that source implies this shape). A spec with an
uncited element is rejected before anything renders. The site's charter forbids inventing
content; here that is enforced by the validator rather than trusted to whoever is authoring.
This is the guard that matters most, because inventing a plausible room is exactly the failure
a language model is best at and least able to notice.

**4. Failure is cheap and early.** `validate.py` needs no browser and no GPU. A misspelled
primitive, an out-of-range option, a dangling citation or a missing field fails in
milliseconds, before a headless Chromium ever starts. The expensive step never runs on a spec
that was never going to work.

**5. The scene reports its own state.** `journeyDiagnostics()` already returns the full
machine-readable state of a running scene — stage, evidence keys, drawables, citation
integrity, actor positions. The engine adds nothing to this because it does not need to: the
model reads the scene the way a debugger would, not the way a player would.

**6. The loop closes without a person in it.** `build_room.py` runs spec → validate → render →
measure → compare against the spec's own declared expectations, and returns a verdict. A model
can iterate on a room until the numbers land where it said they should, with no human looking
at a picture in between.

## What this engine deliberately does not do

It does not generate novel shaders. Rooms that genuinely need new raymarched geometry still get
a hand-written `*Field` function, and that is correct: the expensive, hard-to-verify work stays
rare and explicit instead of being something the model attempts on every room.

It does not try to judge whether a room looks good. That judgement failed every time it was
measured — a model asked for a global verdict returned a constant, and a five-axis score
carried no signal once its backend was pinned. The engine measures what pixels can support
(variety, edge density, depth, material) and reports the numbers. Reading them is a separate
job from producing them.

It does not hide randomness. Every element takes a seed. The same spec produces the same room.

## Files

| File | Role |
|---|---|
| `schema.json` | the room spec contract |
| `primitives.json` | the grammar, regenerated from `fractal.js` |
| `validate.py` | static checks: grammar, ranges, citations, completeness |
| `compile.js` | the only spec-to-scene path, runs in the page |
| `build_room.py` | the closed loop: validate, render, measure, verdict |
| `rooms/*.json` | one file per room |
