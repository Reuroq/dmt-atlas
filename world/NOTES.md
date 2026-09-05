# Complete: Through — first-person journey

## Scope and constraints
- Active entry is index.html: an immersive DMT-inspired journey, not the superseded museum. BRIEF.md and REDIRECT.md informed the build; research is complete. Do not repeat corpus exploration.
- All project writes remain under world/. No git, agents, background services, web searches, GUI or community-image downloads. Verification is foreground/headless and offline.
- Local Three.js 0.160.1 and data.js support direct file:// opening. Run `node --check world/trip.js` before `python world/verify.py`.

## Delivered
- Ordinary room → geometry → chrysanthemum → rush → membrane → Waiting Room → Cathedral → contact → visible-language/download → return → afterglow.
- First-person keyboard/touch walking, drag look, physical exits and optional Workshop, Garden, clinical room and Void paths with Cathedral returns.
- Articulated elves, jester, maternal presence and mantis; proximity/click engagement and changing offerings. Surrounding architecture, not exhibit plinths.
- Approximately four-minute paced journey; manual walking switches off pacing. Pause, restart, reduced motion, scene-linked Sources and WebGL-unavailable fallback.
- Sources connects scenes and beings to selected descriptions, citations, report metadata and credited depiction candidates. The original museum remains at evidence.html as the complete evidence atlas.
- Interpretation labels explain editorial sequencing/design, variable encounters, adjacent tag mentions rather than verified travel chronology, archive limits and possible AI depiction candidates. No audio or substance instructions.
- README.md now describes the active journey, actual controls, evidence conventions and verification.

## Acceptance completed
- JavaScript syntax passed. verification.json combines successful section runs, with their filenames recorded; no browser/console/shader errors were recorded in acceptance.
- Desktop: full manual route, keyboard/drag, physical central and side exits, bench/column/cabinet collision, world boundary, all optional paths/returns, actor picking/proximity/articulation, geometry disposal, all scene evidence, pause/Sources freeze, restart and reduced-motion pixel equality.
- Mobile: real touch hold/release and drag, touch-only route/branch controls, system reduced motion, Sources, branch return, unobscured layout at 390×844, 360×640 and 844×390.
- Paced: all 11 main stages completed in real time, 237.3 seconds after initial pause/Sources checks. Includes a full reduced-motion stage. No fake timers or injected navigation.
- Fallback: unavailable WebGL displays its fallback and opens the local evidence atlas.
- Fixed findings: added missing Jester evidence in download; corrected the custom vertex shader to apply instanceMatrix so chrysanthemum petals render separately. Added touch-action manipulation for controls.
- The initial mobile test's instantaneous synthetic swipe suppressed Chromium's next tap. Replaced it with a 250 ms multi-step gesture and release interval, and used actual taps throughout mobile navigation; the full mobile check then passed.
- Earlier collision/furniture, Cathedral elf evidence, restart reset and reduced-motion surface fixes are covered by the successful desktop run.

## Visual inspection and artifacts
- Inspected corrected chrysanthemum, contact elves/jester, Garden presence, clinical mantis, small portrait and short-landscape renders. Controls remain legible and unobscured.
- latest.png is the fresh final contact encounter, also saved as journey-final.png. status.txt records completion. journey-*.png contains route and mobile renders.
- Pixelvision previews already inspected/labeled: journey_chrysanthemum_fixed, journey_contact, journey_garden, journey_mantis, journey_mobile_portrait, journey_mobile_landscape. Use `screen.cmd read --name <name>` for later looks; never re-view those JPEGs. Older journey_chrysanthemum and journey_mobile_initial previews are superseded.
- journeyDiagnostics() is read-only and exposes route, movement, actors, provenance and renderer metrics. No test-only navigation API exists.
- verification-desktop.json preserves the completed desktop section of the full run; mobile/paced/fallback files record successful targeted reruns. verification.json is their combined final result, not a claim of one uninterrupted run.
- data.js contains 172 entries, 103 sources and 14,309 report metadata records. JOURNEY_RESEARCH.json preserves selected research; neither needs reloading. smoke-trip.json is an earlier baseline, not final acceptance.
- No outstanding acceptance or polish tasks. Open world/index.html to take the complete trip.

<<WORLD_DONE>>
