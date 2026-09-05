# Through — a reported-pattern journey

Open **index.html** in a WebGL-capable browser. Everything runs locally: no install,
server, API key, CDN or network connection is needed. On the site, visit `/world/`.

## Take the journey

Begin in an ordinary room and pass through geometry, the chrysanthemum, a rush,
the membrane, the Waiting Room and Cathedral, encounters, visible language,
return and afterglow. Workshop, Garden, clinical room and Void are optional paths
that return to the Cathedral. Beings turn toward you and offer changing forms.

- **Begin the journey:** a paced passage of about four minutes by default.
- **WASD / arrows:** walk; walking switches off the paced passage.
- **Drag:** look around. Approach or click a being to engage it.
- **Move onward:** advance without walking. Optional paths appear in the Cathedral.
- **Paced journey:** switch between manual and automatic passage.
- **Pause / Space:** freeze movement, animation and journey time.
- **Sources / E:** open the current scene's evidence; Escape closes it.
- **Reduced motion:** still views with no automatic camera movement or ambient
  animation. Timed passage and manual controls remain available. The initial
  setting respects the system preference.
- **Detail:** high or lower GPU load. Lower retains recursive ornament, using fewer
  shader levels and a smaller render buffer; newly entered scenes also use fewer instances.
- **Start again:** return to the entrance. Mobile has touch walking and drag look.

There is no audio. The complete evidence atlas remains available through Sources
and as the fallback when WebGL is unavailable.

## Evidence and interpretation

This is a procedural synthesis of reported phenomenology, not a witness image,
claim of literal places or prediction of anyone's experience. Route, scale,
palette, architecture, ordinary furnishings and character designs are editorial
choices. Encounters and their order vary; the journey is not frequency-weighted.

Sources links every scene and its beings to selected atlas descriptions,
citations, tagged-report metadata and credited depiction candidates. Adjacent
tag mentions are not verified travel chronology. Archive counts are not
population prevalence. Full report prose exists in the repository's local raw
corpus; the browser evidence bundle carries metadata and links, not full posts.
External links may be unavailable, and depiction candidates may include AI-generated work.
No community images are downloaded or displayed as witness imagery.

The original museum is retained at **evidence.html** as a searchable evidence
layer covering all 172 atlas entries, 103 sources and 14,309 report records.

## Report-to-render fidelity (REDIRECT3)

`FIDELITY.md` is the generated, worst-first ledger for all 15 stages and four
being types. `fidelity.py --collect` resolves all 14,309 tagged reports to raw
text, extracts local node-hit passages and counts descriptor families once per
report. It retains counts, exact-offset samples, source/depiction metadata and
input hashes in `fidelity-corpus.json` and `fidelity-passages.jsonl`.

The Sources drawer shows the same top-15 counts and visual grades for its scene
and beings, plus measured forward/reverse mention counts and route departures.
These lexical matches are not population prevalence or verified chronology.
Spot checks found real-backyard Garden tags and earlier-trip beings near afterglow
tags. A fixed-order passage review must validate at least 40 relevant reports per
target (or exhaust its pool) before the scored table uses confirmed sample counts.
Unvalidated full-corpus counts remain visible but cannot pass the fidelity gate.
Garden's completed passage audit found four distinct visionary settings among
27 tagged candidates; 23 ordinary-setting, metaphor or comparison matches were
excluded. Exact-offset narrative supplements recover descriptions clipped by
first-hit windows. This is a tiny heterogeneous sample, not precise prevalence.
Its retained first HIGH baseline scores **65.9%**. Two inspected correction
iterations add a creek/pool, folding flowers and a clockwork brick terrace from
those reports. Garden retains **84.1%** descriptor coverage, but its captures need
freshness renewal after the Workshop renderer changes;
water realism, density, communication, layered space and recession remain partial.
This combines different reports, not a claim that everyone sees one garden.
Fixed-camera HIGH temporal pairs show petal opening, ripples and clockwork motion;
the actual exit fade is only a partial match for reported dissolution.
Seventeen other source targets, Garden capture renewal, route review and complete
fresh acceptance remain pending; Workshop's current local result is below.
Stable images, hashes, adverse observations and before/after grades are retained
in `fidelity-grades.json`. Capture new pairs with `render_visual.py --stage garden
--temporal-seconds 6 --exit-sequence --capture-name UNIQUE_ITERATION_NAME` through
real controls; existing stable capture prefixes are protected from overwrite.
Fresh desktop acceptance passes, including Workshop station and Garden terrace
collisions and both physical exits. The first attempt timed out at the unchanged
Cathedral side exit; the rerun passed without navigation changes. Earlier HIGH
Garden stillness/detail-toggle/Sources checks are retained but stale. Mobile, paced and fallback
acceptance still need fresh runs after the remaining visual work.
The Waiting → Cathedral order inverts two atlas phases; stage timing remains
editorial, not an empirically measured duration distribution.

Workshop passage validation passes by pool exhaustion: all 76 candidates reviewed,
28 included and 48 excluded. Exclusions include retail markets, film comparisons,
ordinary-room overlays, a mushroom experience, a later dream and one repeated
market narrative. Eleven exact-offset Workshop supplements recover clipped context.
Relevant descriptions without dictionary matches remain with zero descriptor votes.
This heterogeneous sample includes mixed-substance reports and contrasting markets,
colourful manufacturing, minimalist white factories and black-and-white grids;
it does not establish one universal factory or population prevalence. Workshop's
inspected HIGH temporal correction scored **85.4%** (70/82), passing its then-current local gate,
up from the preserved **66.5%** baseline. Toothed gears, presses, moving packages,
receding production frames and a contrasting white-on-black wing correct the worst
gaps. Miniature/vast scale, communication, multidimensional layering, fractals and
clown form remain PARTIAL; white machinery loses contrast against its backdrop.
All fifteen descriptors are graded and no top-ten descriptor is ABSENT. Baseline
captures and adverse grades remain in history. Renderer changes make the earlier
Garden captures stale despite its unchanged 84.1% descriptor score; fresh inspection
and acceptance are required before overall completion.

Visual review is **not yet complete**. Grades require inspected HIGH-detail
captures, being close-ups and temporal comparisons for motion/behaviour. Coverage
weights PRESENT=1, PARTIAL=½, ABSENT=0; each target needs ≥80%, no ABSENT in its
top ten, and all fifteen graded. UNREVIEWED is not a claimed visual absence.
`python world/fidelity.py --check` fails until visual, route and fresh functional
acceptance and REDIRECT4 realism gates pass. See `fidelity-grades.schema.md` for review receipts.

## Visual realism (REDIRECT4)

Coverage alone is not visual realism. [REALISM.md](REALISM.md) records a separate
RECOGNISE / CLOSE / GAME judgment for every stage and being, with visual and
temporal reasons. PENDING means no inspected grade. Every target requires fresh,
hash-bound HIGH frame pairs; beings require close-ups. Anything CLOSE or GAME
must be rebuilt. These are visual judgments, not witness certification.

The rebuild replaces the chrysanthemum's mesh tunnel, mandala shells and
particles with `continuum.js`: actual-camera ray-marched folded sheets.
Overlapping scalloped surfaces curl around the walking path, with deeper folds
beyond the physical exit filling the sightline. Colour evolves across red/gold
and blue/cyan, with reflections and depth haze. The seven layers and eightfold
design are editorial choices, not source-established counts. Pixel-sized hit
and normal footprints limit subpixel noise. HIGH and lower both use shaders; pause
and reduced motion share the existing animation clock. Walking and physical
exits retain their original bounds and route.

The inspected v3/v4 petal-primitive attempts and v5 cut-through fractal were
rejected as **GAME**; their images and adverse judgments remain immutable.
The first deterministic Chrysanthemum source batch is audited: 7 included and
3 excluded among 480 candidates, with no skipped decisions. Source validation
is still incomplete; these are not prevalence estimates or a passing visual
score. See [the bounded evidence and design notes](chrysanthemum-source-batch1.md).

The v6/v7 recursive corolla remains archived as **CLOSE**. V8 folded sheets were
**GAME**: flat cutout bands, radial streaking and a colour seam. Current v9 is
**CLOSE**, not passing: the inspected HIGH pair shows curved overlapping folds,
a filled centre and changing openings; the seam is gone and streaking reduced.
Broad pale surfaces, thin dark edge artifacts and limited nested detail still
fall short of dense recursively unfolding jewelled geometry. All nine adverse
iterations retain their immutable image pairs and judgments. The other 18 realism targets,
including all being redesigns, remain pending. Workshop and Garden descriptor
scores remain in history, but their receipts and the previous full acceptance
are now stale after the renderer change. Overall completion remains blocked.

Fresh v9 focused checks pass: HIGH walking boundary, drag-look, restart and
physical exit to Rush; paused/reduced-motion pixel stillness, detail-toggle
preservation and Sources provenance. These do not replace full acceptance.
The current `latest.png` is the separate HIGH accessibility capture, not the
inspected temporal pair. SwiftShader measured 1.59 fps, not GPU performance.

## Files and verification

- `index.html`, `trip.css`, `trip.js`: active first-person experience.
- `fractal.js`: procedural relief, recursive fronds, pleated room skins, banked passage floors, deeply folded rear architecture, branching fan vaults, open canopy/furniture, connected spatial script, phase-delayed spatial contours, instanced mandala, bloom and granular signal seams. Effects share the pausable animation clock; no history-buffer drift.
- `beings.js`: articulated crystal beings, contour-engraved masks and nested 4D-projection offerings.
- `render_visual.py`: offline foreground visual iteration using real journey controls.
- `evidence.html`, `world.js`, `style.css`: retained evidence atlas.
- `data.js`: bundled evidence; `build_data.py` regenerates it from local research.
- `vendor/three.min.js`: local Three.js 0.160.1 with its adjacent license.
- `verify.py`: foreground, offline headless acceptance using real controls.
- `verification*.json`: acceptance results; `journey-*.png`: saved renders.
- `latest.png`, `status.txt`, `NOTES.md`: current render, status and build notes.

From the repository root:

```powershell
node --check world/trip.js
python world/verify.py
```

Verification needs Python Playwright, Chromium and Pillow. It checks the full
manual route, branches, collisions, interactions, evidence, pause/reduced motion,
mobile controls/layout, real-time paced completion and WebGL fallback. The paced
check takes several minutes. Targeted reruns accept
`--only desktop`, `--only mobile`, `--only paced` or `--only fallback`.
Diagnostics are read-only; checks do not inject navigation or fake journey time.
All generated files stay under `world/`.

The second visual redesign is in progress. Old verification results establish the
journey structure, not acceptance of the new renderer. See `NOTES.md` for remaining work.
