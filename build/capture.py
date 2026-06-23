"""Vision self-verify loop — render every view at desktop (1440) AND mobile (390)."""
import asyncio, os
from playwright.async_api import async_playwright

OUT = r"C:\Users\dwayn\OneDrive\Desktop\HyperspaceAtlas\build\shots"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8791/index.html"

VIEWPORTS = [("d", 1440, 900), ("m", 390, 844)]

async def dossier_open(pg):
    return await pg.eval_on_selector("#dossier", "el => !el.classList.contains('closed')")

async def shoot(pg, tag, name):
    await pg.screenshot(path=os.path.join(OUT, f"{tag}_{name}.png"))

async def run_viewport(b, tag, w, h):
    pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    errs = []
    pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
    await pg.goto(URL, wait_until="load")
    await pg.wait_for_timeout(2600)            # fonts + bg image + sim settle
    await shoot(pg, tag, "0_intro")

    await pg.click("#enterBtn")
    await pg.wait_for_timeout(1600)
    await shoot(pg, tag, "1_constellation")

    # dossier
    if tag == "d":
        opened = False
        for (x, y) in [(720, 470), (680, 430), (770, 500), (640, 510), (800, 440), (700, 380)]:
            await pg.mouse.click(x, y)
            await pg.wait_for_timeout(450)
            if await dossier_open(pg):
                opened = True; break
        await shoot(pg, tag, "2_dossier")
        if opened:
            await pg.keyboard.press("Escape")
            await pg.wait_for_timeout(400)
    else:
        # mobile: open dossier via a journey chip (reliable), shows the bottom sheet
        await pg.click("button[data-view='journey']")
        await pg.wait_for_timeout(700)
        await pg.click(".chip")
        await pg.wait_for_timeout(600)
        await shoot(pg, tag, "2_dossier")
        await pg.keyboard.press("Escape")
        await pg.wait_for_timeout(400)
        await pg.click("button[data-view='constellation']")
        await pg.wait_for_timeout(500)

    # map
    await pg.click("button[data-view='map']")
    await pg.wait_for_timeout(1300)
    await shoot(pg, tag, "3_map")

    # journey
    await pg.click("button[data-view='journey']")
    await pg.wait_for_timeout(800)
    await shoot(pg, tag, "4_journey")

    # about (desktop only; identical modal on mobile)
    await pg.click("button[data-view='constellation']")
    await pg.wait_for_timeout(400)
    if tag == "d":
        await pg.click("#aboutBtn")
        await pg.wait_for_timeout(400)
        await shoot(pg, tag, "5_about")

    print(f"[{tag} {w}x{h}] errors:", errs if errs else "none")
    await pg.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, w, h in VIEWPORTS:
            await run_viewport(b, tag, w, h)
        await b.close()

asyncio.run(main())
