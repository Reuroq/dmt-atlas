"""Vision-verify the tool/content pages at desktop + mobile."""
import asyncio, os
from playwright.async_api import async_playwright
OUT = r"C:\Users\dwayn\OneDrive\Desktop\HyperspaceAtlas\build\shots"
BASE = "http://127.0.0.1:8791/"
VPS = [("d", 1440, 1000), ("m", 390, 844)]

async def run(b, tag, w, h):
    pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))

    # IDENTIFY — intro then a driven result (insect/clinical/operated -> mantis)
    await pg.goto(BASE + "identify.html", wait_until="load"); await pg.wait_for_timeout(1500)
    await pg.screenshot(path=f"{OUT}/p_{tag}_identify.png")
    await pg.click('.opt[data-q="look"][data-v="insect"]')
    await pg.click('.opt[data-q="feel"][data-v="clinical"]')
    await pg.click('.opt[data-q="did"][data-v="operated"]')
    await pg.wait_for_timeout(200)
    await pg.click("#reveal"); await pg.wait_for_timeout(900)
    await pg.screenshot(path=f"{OUT}/p_{tag}_identify_result.png", full_page=(tag == "m"))

    # QUESTIONS
    await pg.goto(BASE + "questions.html", wait_until="load"); await pg.wait_for_timeout(1200)
    await pg.screenshot(path=f"{OUT}/p_{tag}_questions.png")

    # GROUNDING (crisis resources above the fold)
    await pg.goto(BASE + "grounding.html", wait_until="load"); await pg.wait_for_timeout(1200)
    await pg.screenshot(path=f"{OUT}/p_{tag}_grounding.png")

    print(f"[{tag} {w}x{h}] errors:", errs if errs else "none")
    await pg.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tag, w, h in VPS:
            await run(b, tag, w, h)
        await b.close()
asyncio.run(main())
