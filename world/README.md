# Through — a reported-pattern journey

Open **index.html** in a WebGL-capable browser, or visit `/world/`.
Everything runs locally: no install, server, API key, CDN or network is needed.

## Final build — REDIRECT5

All 19 targets completed their four-turn visual-review budgets: **16 GAME,
3 CLOSE (return, void, chrysanthemum), 0 RECOGNISE**. These are final visual judgments, not
claims of witness accuracy or a coverage pass. No further target work is pending.
The table below reproduces the final grades and reasons from `targets.json`;
the same table is available in every scene's Sources drawer.

## Closing checks

- Coverage: `python3 world/fidelity.py` ran once; **overall NOT PASSED**.
  Sixteen targets have 0% reviewed descriptor coverage (unreviewed, not observed
  absence). Garden is 84.1%, chrysanthemum 84.7%, workshop 85.4%; all retain
  blockers. Route review and legacy acceptance freshness gates are unsatisfied.
  See [FIDELITY.md](FIDELITY.md) and [closing-fidelity.log](closing-fidelity.log).
- Acceptance: `python3 world/verify.py` ran once and **FAILED** at a desktop
  screenshot (20-second timeout); subsequent acceptance sections did not run.
  `verify.py` now pauses through real controls, waits for rendering to settle,
  allows 90 seconds for capture, and copies that frame to `latest.png`.
  This fix has not been acceptance-retested, respecting the once-only closing
  instruction. No acceptance pass is claimed. See [closing-verify.log](closing-verify.log).
- Final render: [latest.png](latest.png) is the newer inspected HIGH frame.
  The pair is [first](visual-chrysanthemum.png) /
  [motion](visual-chrysanthemum-motion.png), at animation 6.1138 / 8.1637 seconds,
  identical real entry pose `[0, 1.7, 8]`, yaw/pitch 0. No page errors, missing
  evidence or uncited meshes. Changing curls and darker recesses remain visible;
  rainbow tiers and lacquer-like blades retain the final CLOSE limitations.

## Final per-target grades and reasons

| Target | Grade | Observed result and limitations |
| --- | --- | --- |
| onset | GAME | Turn 4 final: GAME; four-turn budget exhausted. One onset-only aperture rebuild replaced the gold doorway panel with a recessed lit passage and cut a real window opening with deep lining, sill, glass and dusk light beyond. Both final HIGH frames show readable jamb depth and breathing furniture, but the passage still ends in a bright flat panel and the window view reads mainly as a pale gradient. Plain boxy walls, sharp ceiling seams, primitive plant and weak surface motion remain. Earlier surface work removed distracting foil folds and clarified timber without reaching convincing onset transformation. Keep GAME and move to geometry. |
| geometry | GAME | Turn 4 final: GAME; four-turn budget exhausted. The final geometry-only form change replaced broad porous ribbons with a denser rounded branching network and softened the clipped inner boundary. Both HIGH frames show many overlapping lobes, moving gaps and highlights, and a more open receding centre; earlier work also removed the disconnected floor and flat end panel. The material still reads as metallic plastic, similar small forms repeat, the near surfaces lack convincing recursive intricacy, and distant detail collapses into a speckled dark opening. Density and continuity improved substantially without reaching the replication bar. Keep GAME and move to rush. |
| rush | GAME | Turn 4 final: GAME; four-turn budget exhausted. The final rush-only rebuild replaces the closed embossed relief with porous volumetric branches and deeper backing, breaking up concentric colour bands. Both HIGH frames show overlapping rounded forms, visible cavities, a clearer receding channel and substantial changes in branch silhouettes and openings. Across the rush work, the disconnected floor, wires and tiny doorway were removed and continuous travelling form was established. However, the near surfaces still look like smooth coloured plastic, their fine detail resembles scattered scratches rather than nested structure, similar holes repeat, and the centre falls into largely empty teal haze. Depth and motion improved without reaching the replication bar. Keep GAME and move to membrane. |
| membrane | GAME | Turn 4 final: GAME; four-turn budget exhausted. The final membrane-only form change rounds the iris into rolled lips, widens the nested openings and replaces the central solid form with a concave chamber. A chamber-boundary sign bug exposed by rendering was corrected within that change. Both final HIGH frames show substantial changes in aperture size, overlapping folds and visible deeper layers. Across membrane work the detached floor, tiled vault, wires and flat pinwheel were removed, improving continuity and motion. However, broad pastel folds remain smooth and plastic-like, repeated luminous striations substitute for nested intricacy, radial star-like organisation persists, and the distant chamber reads as a coloured rosette disc rather than convincing space beyond a yielding veil. Keep GAME and move to waiting. |
| waiting | GAME | Turn 4 final: GAME; four-turn budget exhausted. A waiting-only usher replacement removes the detached dotted jester: a continuous mantle, floor tendrils, sculpted face, separated fingers and moving open palms are now readable in both HIGH frames. Its closer placement and teal-gold surface better connect it visually to the room. However, it still reads as a stylised robed statue with goggle-like eyes and surface lines rather than an intricately morphing being; tendrils touch the floor without truly merging into it. The surrounding room breathes substantially but retains broad lacquer/plastic surfaces, oversized looping relief and insufficient nested architectural density. Readability and continuity improved without reaching the replication bar. Keep GAME and move to cathedral. |
| cathedral | GAME | Turn 4 final: GAME; four-turn budget exhausted. The final cathedral-only coffer rebuild blends separate wall/rib-facing projections, broadens nested recess profiles and aligns surface highlights with the moving relief. Both HIGH frames show much less speckling, clearer connected arches and visible changes in recess outlines and highlights. Across the cathedral work, wire architecture became a continuous solid nave with thick piers, arches, dome and recessed passages. However, broad surfaces still resemble embossed plastic, rounded-square panels visibly repeat across the walls and floor, side passages retain stretched horizontal bands, the far opening looks shallow and the unchanged elves remain detached dotted silhouettes. Depth and surface coherence improved without reaching the replication bar. Keep GAME and move to contact. |
| contact | GAME | Turn 4 final: GAME; four-turn budget exhausted. Fresh HIGH baseline pair inspected: horned toy-like figures stood separately on a pastel embossed-plastic floor. One contact-only figure-form rebuild in beings.js replaces their short bodies, legs and horns with elongated silhouettes, narrow sculpted mask faces with seed-dependent orbital proportions, longer articulated fingers and fluted lower bodies spreading into buried floor bases. Both revised frames show changing hand poses, body contours and flowing room relief. The beings look less like small mascots and their bases visibly meet the floor, but they still resemble patterned statues with similar mask faces; broad glowing loops obscure facial anatomy and the bases retain distinct edges against the room. The surrounding embossed-plastic vault, flat bright rectangular throat and particle-mechanism offering remain below the replication bar. Final HIGH frames at 16.9971 / 20.0304 animation seconds, same real entry [0,1.7,9], yaw/pitch 0. Keep GAME and move to download when directed. |
| download | GAME | Turn 4 final: GAME; four-turn budget exhausted. One download-only figure replacement uses the existing continuous ray-marched contact figure factory for all four dotted actors. Both revised HIGH frames show solid elongated bodies, spreading bases, raised readable hands and changing hand/body poses. However, similar patterned mask-statues replace the dots rather than convincing beings; pale waxy glyphs obscure their faces, bases retain distinct edges against the floor, the enclosure reads as pastel embossed plastic, and the offering remains a bead-and-rod mechanism. Earlier changes established solid morphing language and continuous carved surroundings with a receding arched passage, but the forms remain visually separate and lack convincing recursive jewel-like intricacy. Final frames at 19.1484 / 22.1818 animation seconds, same real entry [0,1.7,9], yaw/pitch 0. Keep GAME; return is next when directed. |
| return | CLOSE | Turn 4 final: CLOSE; four-turn budget exhausted. One return-only spatial dissolution change breaks the continuous relief into moving patches, exposes nearby plaster and a calmer wood floor, brings the sofa forward and adds a side window; the etched contour-line overlay is removed. Both HIGH frames show folds reshaping and colour withdrawing across the same room surfaces, so ordinary space now emerges around the viewer rather than only inside a distant box. Not RECOGNISE: residual relief resembles waxy embossed plaster, furnishings and flat luminous windows remain schematic, and the far floor has a dark speckled patch. Frames at 21.0360 / 23.0860 animation seconds, same real entry [0,1.7,8], yaw/pitch 0. Further improvement would need more convincing room lighting/materials and cleaner relief-to-floor integration; no further return work in this budget. |
| afterglow | GAME | Turn 4 final: GAME; four-turn budget exhausted. One afterglow-only practical-prop rebuild replaces solid oval leaves with thin curved veined blades and slender stems, adds a tapered rimmed pot with soil, builds a dimensional fabric lampshade with binding rings, supports, bulb and weighted base, and gives books separate covers, page blocks and spine bands. Both HIGH frames show readable lamp depth and more natural plant silhouettes while the room remains still with slight dust/light changes. The target remains GAME because blank evenly shaded walls, repetitive flooring, simplified padded furniture, dark ribbon-like leaves and the flat luminous passage/window still read as a synthetic interior rather than convincing familiar space. Frames at 23.7999 / 25.9164 animation seconds (2.1165 apart), same real entry [0,1.7,6.5], yaw/pitch 0. Further improvement would require integrated room lighting and richer furnishing/surface construction, not more psychedelic motion; no further afterglow work in this budget. |
| workshop | GAME | Turn 4 baseline: GAME. Both fresh HIGH frames inspected: dense jewelled mosaic and reflective machinery remain visibly separate from thin thread-like makers with unreadable faces/hands and pale floating offerings. One workshop-only continuous-maker rebuild remains to do before final rendering and closure. |
| garden | GAME | Turn 4 final: GAME; four-turn budget exhausted. One garden-only maternal rebuild replaces the dotted figure with a continuous shaded mantle, sculpted face, swept hair/crown, separated fingers and spreading base, using a mother-specific variant of the existing implicit figure factory. Both final HIGH frames show readable open hands, changing arm poses and flowing surface highlights. Across garden work, vegetation became fuller and smoother, leafy boughs replaced the wire roof, and rounded shaded ground replaced contour wallpaper. Still GAME: the mother resembles a glossy masked statue with luminous surface loops and a distinct base edge; oversized foliage looks plastic, branches are tubular, the ground is waxy, and the creek bank remains sharply patterned. Improved form and motion do not meet the replication bar. Frames at 14.9172 / 17.0672 animation seconds, fixed real entry [0,1.7,13], yaw/pitch 0. No further garden work in this budget; clinical is next when directed. |
| clinical | GAME | Turn 4 final: GAME; four-turn budget exhausted. One clinical-only chamber rebuild replaces shallow pale embossing with a deep morphing porous wall/ceiling layer, replaces rectangular empty bays with unequal oval instrument cradles and luminous inset sensors, embeds a lobed optical organ overhead, and calms the floor. Both final HIGH frames show stronger depth, changing wall openings/highlights and moving examiner hands, with the central passage visible. Still GAME: the wall layer resembles oversized cut ribbons with abrupt edges and broad glossy patches rather than continuous fine living geometry; equipment reads as rounded portholes on smooth tubes, floor lighting remains synthetic, and the unchanged striped insect torso, triangular head and blade-like legs remain toy-like and separate from the room. The four turns improved solidity, gesture and density but did not reach the replication bar. Final frames at 17.3686 / 19.4519 animation seconds, fixed real entry [0,1.7,11], yaw/pitch 0. No further clinical work in this budget; await the driver for void. |
| void | CLOSE | Turn 4 final: CLOSE; four-turn budget exhausted. One void-only internal-form/material rebuild replaces faint noise contours with porous nested sheets, shaded bodies, luminous ribs and depth absorption, retaining three separated drifting regions and broad open darkness. Both HIGH frames show fuller folded bodies, clearer central and lower-right layers, and changing openings and overlaps; there is no floor, horizon, ring or enclosing wall. Not RECOGNISE: the forms remain blurred smoke membranes with broad looping edges, little resolved fine nested structure and weak internal occlusion. Frames at 14.0594 / 16.1093 animation seconds, fixed real entry [0,1.7,8], yaw/pitch 0. Keep CLOSE; no further void work in this budget. |
| elf | GAME | Turn 4 final: GAME; four-turn budget exhausted. One elf-only body/material rebuild replaces striped hoops with a fuller branching sheet, nested openings, tapered forked roots and depth-based jewel/metal colour. Both HIGH frames show torso openings and silhouettes changing alongside fingers and knees; faces and hands remain readable. Still GAME: broad smooth teal perforated plates resemble a suit, nested detail is sparse, thin limbs and near-identical gold mask faces remain toy-like, and small roots do not visually merge the beings into the room. Frames at 14.3673 / 16.4007 animation seconds, fixed real contact entry [0,1.7,9], yaw/pitch 0. Keep GAME; no further elf work in this budget. |
| jester | GAME | Turn 4 final: GAME; four-turn budget exhausted. One final jester-only facial-anatomy/relief rebuild adds raised moving brows and cheeks, deeper cheek and nostril recesses, an opening grin with teeth, and multiscale body relief while reducing broad gold stripes. Both HIGH frames show a more legible grin, denser body highlights and changing face, hands, crown and torso openings. Across the four turns, the detached costume gained continuous shaded anatomy, readable fingers, a morphing body and cleaner tapered roots; torn ribbons and black base wedges were removed. Still GAME: the face resembles a metallic carnival mask, fine relief reads as glittery hammered metal rather than resolved nested living geometry, the body remains an ornamental oval suit, and roots visibly meet rather than merge with the room. Final frames at 11.5493 / 13.5827 animation seconds, identical real waiting entry [0,1.7,11], yaw/pitch 0. Keep GAME; no further jester work in this budget. Mother is next when directed. |
| mother | GAME | Turn 4 final: GAME; four-turn budget exhausted. One mother-only form change replaces swollen hair/shoulder lobes with tapered flowing sweeps and nested longitudinal grooves. Both final HIGH frames show narrower ribbed hair, an exposed neck, readable fingers and changing hand/head poses. Still GAME: hair reads as fine metallic curtains rather than integrated living geometry, the face remains a smooth doll-like mask with bulbous cheeks, and the glossy perforated gown has a distinct ground boundary. Final animation 18.8897 / 20.9397, identical real walking pose [0,1.7,5.948479998779286], yaw/pitch 0. No page errors, missing evidence or uncited meshes. Driver-owned turns_used preserved at 3; no further mother work in this budget. |
| mantis | GAME | Turn 4 final: GAME; four-turn budget exhausted. One mantis-only lower-leg/foot rebuild replaces tiny abrupt feet with swept branching tarsal fans that spread from the lower shins and taper beneath the floor. Both final HIGH frames show wider foot fans, changing foot spread and grasping hand poses. The continuity goal is not achieved: the fans read as oversized rubbery toes with distinct floor boundaries, while the narrow stalk thorax, shiny seed-pod abdomen, regular limb ribbing and speckled shins remain game-like. Compound eyes and mandibles are readable, but the figure still stands apart from the room rather than forming continuous jewelled living geometry. Final animation 18.3334 / 20.3833, identical real walking pose [0,1.7,6.9286399993896595], yaw/pitch 0. No page errors, missing evidence or uncited meshes. Driver-owned turns_used preserved at 3; no further mantis work in this budget. |
| chrysanthemum | CLOSE | Turn 4 final: CLOSE; four-turn target budget complete. One chrysanthemum-only fold-aware lighting rebuild in continuum.js strengthens local occlusion, restores broad shading from the actual sheet normal and concentrates etched emission on raised petal lips. Both HIGH frames show darker recesses, clearer overlapping petals and a more legible layered centre while luminous engraving and changing curls remain visible. Not RECOGNISE: repeated rainbow tiers and broad blade-like petals persist; nested detail still reads as surface decoration, some highlights remain lacquer-like, and convincing recursive fold-over/inside-out motion is absent. Final animation 5.3381 / 7.3714, identical real journey entry [0,1.7,8], yaw/pitch 0. No page errors, missing evidence or uncited meshes. Driver-owned turns_used preserved at 3. Any future redesign would need genuinely nested folding geometry, not more surface decoration; no further target work within this budget. |

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

## Files and verification

- `index.html`, `trip.js`, `trip.css`: first-person experience and controls.
- `continuum.js`, `fractal.js`, `beings.js`: procedural environments and beings.
- `data.js`, `fidelity-data.js`, `fidelity-ui.js`: local evidence and Sources tables.
- `targets.json`: final visual grades; `REALISM.md`: visual-review details.
- `FIDELITY.md`, `fidelity-results.json`: separate descriptor coverage findings.
- `verification.json`: closing acceptance results.
- `latest.png`, `status.txt`, `NOTES.md`: closing frame and build state.
- `vendor/three.min.js`: bundled Three.js 0.160.1 and adjacent license.

Existing checks (from the repository root):

```bash
python3 world/fidelity.py
python3 world/verify.py
```

Verification uses Python Playwright, headless Chromium and Pillow, with offline
real-control navigation. It covers the manual route, optional paths, collisions,
interactions, provenance, pause/reduced motion, mobile, paced passage and fallback.
SwiftShader frames support visual inspection, not hardware performance claims.
