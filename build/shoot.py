"""Render the three views headless so I can visually self-verify."""
import asyncio, os
from playwright.async_api import async_playwright

OUT = r"C:\Users\dwayn\OneDrive\Desktop\HyperspaceAtlas\build\shots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8791/index.html"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        errs = []
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_timeout(2500)  # let the force sim settle
        await pg.screenshot(path=os.path.join(OUT, "1_constellation.png"))

        # open a dossier by clicking near the biggest source hub (center-ish)
        await pg.mouse.click(720, 450)
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=os.path.join(OUT, "2_constellation_click.png"))

        # Atlas Map
        await pg.click("button[data-view='map']")
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=os.path.join(OUT, "3_map.png"))

        # The Journey
        await pg.click("button[data-view='journey']")
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=os.path.join(OUT, "4_journey.png"))

        # About modal
        await pg.click("button[data-view='constellation']")
        await pg.wait_for_timeout(400)
        await pg.click("#aboutBtn")
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=os.path.join(OUT, "5_about.png"))

        await b.close()
        print("ERRORS:", errs if errs else "none")

asyncio.run(main())
