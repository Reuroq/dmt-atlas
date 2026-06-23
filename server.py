"""Serves the static DMT Atlas + the fleet AI-bot radar (server-side LLM-crawler logging).
Same files as the static deploy; this just adds the radar middleware. uvicorn server:app."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import bot_radar

app = FastAPI(title="The DMT Atlas")

@app.middleware("http")
async def radar(request: Request, call_next):
    resp = await call_next(request)
    try:
        bot_radar.log(request, resp.status_code)
    except Exception:
        pass
    return resp

# serve the site (index.html at /, all assets/pages relative) from the repo root
app.mount("/", StaticFiles(directory=".", html=True), name="site")
