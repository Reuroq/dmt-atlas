# Build a 3D rendition of this research

You are working in the DMT Atlas repository (dmtatlas.com): a source-grounded map of the collective
DMT experience. Today the research is text, numbers and an index of pictures. The owner wants it to
become a 3D world people can move through in a browser. That is the whole instruction. How it looks,
how it is structured, what you build first, which tools you use, how far you go — all yours.

## The research (read it, then decide)
- `data/atlas.json` — 40 entities, 31 realms, 24 geometries, 22 motifs, 11 journey phases, 44 themes,
  106 data points, 103 cited sources. Each entry has descriptions, aliases and the sources that report it.
- `data/corpus/transitions.json` — measured transitions between nodes inside 14,309 real trip reports
  (which realm leads to which, which beings appear together), and co-occurrence counts.
- `data/corpus/summary.json` — how many reports mention each node (prevalence).
- `data/corpus/saturation.json` — the discovery curve: all 128 nodes attested by report 6,025 of 14,309.
- `data/corpus/discovery.json` — recurring places the reports name that the atlas does not yet
  (living room, dark room, forest, hospital, garden, white room, cartoon world, lab, cave …).
- `data/corpus/depictions.json` — 10,906 people-made depictions (images, videos, galleries) with
  permalink, author and score; `assets/img/depictions/` holds three CC-licensed images with ATTRIBUTION.json.
- `data/corpus/reports.jsonl` — the tagged reports (ids, dates, ordered node sequences).
- `BUILD.md` — the honesty charter: this is a map of what people report, cited; not a claim of literal
  places; no sourcing/dosing content.

## The few hard lines
- Write only under `world/`. Do not modify anything else in the repository. Do not run `git`.
- Tools on this machine: Blender 4.2 at `C:\tmp\blender\blender-4.2.22-windows-x64\blender.exe`
  (headless, `--background --python`, absolute output paths), Python 3.12 with numpy/PIL/cv2/scipy/
  pygltflib, three.js from a CDN in the browser. Your built-in image generation is enabled; generated
  imagery must be labelled as synthesised from the cited descriptions, never presented as a witness image.
- No Reddit scraping, no downloading community images: depictions are shown by link/embed with credit.
- Never open a GUI window, browser or dialog. Headless only.
- Every element that reaches the screen keeps a way back to its evidence (which reports/sources/depictions
  it came from). That is the one thing this world has that no other attempt has had.
- Keep `world/status.txt` (one line, what you are doing) and `world/latest.png` (the newest render or
  screenshot) current; the owner watches them on a TV. When the world is walkable in a browser,
  `world/index.html` should open it.
- When you have taken the work as far as you can this turn, write what you did and what is next in
  `world/NOTES.md`; you will be told to continue. Say `<<WORLD_DONE>>` only when you consider it finished.
