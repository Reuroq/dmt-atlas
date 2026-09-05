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
population prevalence. Full report prose is not stored locally; external links
may be unavailable, and depiction candidates may include AI-generated work.
No community images are downloaded or displayed as witness imagery.

The original museum is retained at **evidence.html** as a searchable evidence
layer covering all 172 atlas entries, 103 sources and 14,309 report records.

## Files and verification

- `index.html`, `trip.css`, `trip.js`: active first-person experience.
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
