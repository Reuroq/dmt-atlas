# Atlas of Reported Worlds

Open **index.html** in a WebGL-capable browser. Everything needed for the museum
is local: no install, build server, API key, CDN connection or external fonts.
When served as part of the existing site, the address is `/world/`.

## Explore

- WASD / arrow keys: move. Shift: faster movement.
- Drag the scene: look. Click a glowing exhibit: evidence.
- E: inspect the exhibit in the crosshair. I: searchable index.
- H: return to the current room's entrance. Escape: close the evidence panel.
- Mobile: directional pad to move, drag to look, tap exhibits.
- Room navigation and the curated route work without walking.
- Pause motion disables ambient rotation and floating; system reduced-motion
  preferences are respected. There is no autoplay audio, flashing or forced flight.

Eight independently walkable spaces interpret the Waiting Room, Domed Cathedral,
Workshop, Garden, Operating Theater, Library, Void and Hyperspace/Observatory.
The index covers all 172 atlas entries, including those outside the corpus's
fixed 128-node vocabulary. Deep links use `#space=garden` or
`#node=realm%7CThe%20Void`.

## Evidence and visual conventions

Architecture is a procedural interpretation, not a witness image or an assertion
of literal places. Scale, palette, layout, decorative lighting and room order
are editorial choices. The eight-space route is a museum itinerary, not an
empirically observed sequence of experiences. Abstract exhibit gems are symbols,
not claimed likenesses of beings.

Each room and exhibit exposes its atlas descriptions and citations, corpus
mention count when available, dated report permalinks with stored tag sequences,
credited depiction links, adjacent-mention connections and co-occurrence pairs.
All report records are local metadata; full report prose is not in this dataset.
Posts can be unavailable. No Reddit scraping or community-image downloading occurs.

The Observatory has 128 points, with a minimum radius plus a square-root scaling
of tagged-report count. Sphere positions use an arbitrary golden-angle layout;
they do not encode similarity, geography or measured distances. Its 80 connecting
lines are the strongest stored co-occurrence pairs, not transitions. The methods
panel explains corpus limits, the fixed-vocabulary saturation curve, and candidate
places from a separate phrase scan. Corpus counts are not population prevalence.

## Files and reproducibility

- `world.js`, `style.css`, `index.html`: renderer and UI.
- `data.js`: generated, local browser evidence bundle.
- `build_data.py`: reads the repository research; writes only under `world/`.
- `manifest.json`: SHA-256 hashes of all research inputs.
- `vendor/three.min.js`: pinned Three.js 0.160.1; adjacent MIT license.
- `verify.py`: foreground headless Playwright checks; no server or GUI.
- `verification.json`: latest acceptance results and render statistics.
- `latest.png`: current entrance screenshot for the build wall.
- Other PNGs: desktop room, evidence-panel and mobile screenshots.

From the repository root:

```powershell
python world/build_data.py
python world/verify.py
```

Verification needs Python Playwright and its Chromium headless runtime, already
present in this development environment. Runtime visitors need only a browser.
The evidence index remains usable if WebGL or the 3D library is unavailable.
No repository files outside `world/` are changed by the build or checks.
