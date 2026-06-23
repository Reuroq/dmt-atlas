# The DMT Atlas — build notes

**What this is:** a source-grounded, interactive cartography of the *collective DMT experience* — every recurring entity, realm, geometry, journey-phase, and theme that people consistently report, each entry cited to who reported it (books, peer-reviewed studies, community archives).

**The honesty charter (non-negotiable):**
- This is a map of what people **report and write**, synthesized from real published sources. Every node carries citations.
- It is a cartography of a shared **phenomenology and mythology** — NOT a claim that these are literally real places/beings in an objective dimension.
- It is NOT a guide to obtaining, making, or taking any substance. No synthesis, no extraction, no dosing. (That's also how Strassman, Johns Hopkins, and Erowid treat the subject.)
- Real survey numbers only when a named study supports them. No invented stats, entities, or quotes. Uncertainty is labeled.

## Architecture
Static, self-contained SPA (deployable like the rest of the fleet). One data file drives everything.
- `data/atlas.json` — the cited knowledge base (schema below). Populated by 6 parallel research agents + hand-verified seed.
- `index.html` / `styles.css` / `app.js` — the three-view front end.
- Three lenses over the same DB, switchable by tab:
  1. **Constellation** — force-directed graph; every entity/realm/geometry/theme linked to the *sources that report it*. Cluster structure = the actual shape of the corpus ("who said what"). Node size = citation count / reported frequency.
  2. **Atlas Map** — illustrated terrain; realms positioned as named regions you pan/zoom and click into.
  3. **The Journey** — the breakthrough arc, inhale → return, each phase opening into what's reported there.
- Click any node → **dossier** panel: description, attributes, real quotes with citations, study %s, cross-links, full source list.

## atlas.json schema
```
{
  "meta": { "title","tagline","charter" },
  "sources":   [{ "key","author","work","year","type","note","url?" }],
  "entities":  [{ "name","aka":[],"type","appearance","behavior","communication",
                  "emotional_tone","message_or_purpose","frequency","phase?","sources":[{source_key,detail}] }],
  "realms":    [{ "name","aka":[],"description","what_happens_there","map_x?","map_y?","sources":[...] }],
  "geometries":[{ "name","description","phase?","sources":[...] }],
  "phases":    [{ "order","name","description","sources":[...] }],
  "themes":    [{ "name","description","phase?","sources":[...] }],
  "data_points":[{ "claim","stat_or_value","source_key","detail" }]
}
```
`type` ∈ machine-elf · insectoid · trickster · reptilian · divine-feminine · deity · alien-grey · deceased · guardian · impersonal-intelligence · other

## Status
- [x] Scaffold + schema + three-view engine + dossier (against hand-verified seed)
- [ ] Merge the 6 research agents' corpus → full atlas.json
- [ ] Playwright self-verify loop (the /goal render→inspect→fix method)
- [ ] Polish (cosmic aesthetic, legend, About/charter modal, mobile)
- [ ] Deploy (GA4 id + bot-radar per standing rules) + saturation loop
