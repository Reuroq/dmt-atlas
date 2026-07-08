"""Vision self-verify for the multi-page redesign — every page type at 1440 + 390,
console errors collected. Serve first:  python -m http.server 8791  (repo root)."""
import asyncio
import os
import sys

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "shots_v2")
os.makedirs(OUT, exist_ok=True)
BASE = "http://127.0.0.1:8791"

PAGES = [
    ("home", "/index.html"),
    ("entities_idx", "/entities/index.html"),
    ("entity", "/entities/self-transforming-machine-elves.html"),
    ("realms_idx", "/realms/index.html"),
    ("realm", "/realms/the-waiting-room.html"),
    ("journey", "/journey.html"),
    ("themes", "/themes.html"),
    ("evidence", "/evidence.html"),
    ("library", "/library.html"),
    ("motifs_idx", "/motifs/index.html"),
    ("motif", "/motifs/the-download-compressed-information-transfer.html"),
    ("entity_new", "/entities/the-surgeons-hyperspace-medical-team.html"),
    ("explore", "/explore.html"),
]
VIEWPORTS = [("d", 1440, 900), ("m", 390, 844)]

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


async def main():
    errs_all = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for tag, w, h in VIEWPORTS:
            pg = await b.new_page(viewport={"width": w, "height": h})
            errs = []
            pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
            for name, path in PAGES:
                await pg.goto(BASE + path, wait_until="load")
                await pg.wait_for_timeout(1800 if name in ("home", "explore") else 900)
                await pg.screenshot(path=os.path.join(OUT, f"{tag}_{name}.png"))
                if name in ("home", "entity"):   # full-page for the long ones
                    await pg.screenshot(path=os.path.join(OUT, f"{tag}_{name}_full.png"), full_page=True)
            errs_all[tag] = errs
            await pg.close()
        await b.close()
    for tag, errs in errs_all.items():
        print(f"[{tag}] {len(errs)} console errors")
        for e in errs[:12]:
            print("   ", e[:200])
    print(f"shots -> {OUT}")


asyncio.run(main())
