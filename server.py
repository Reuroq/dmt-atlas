"""Serves the static DMT Atlas + the fleet AI-bot radar (server-side LLM-crawler logging)
+ the /ask question board API. Same files as the static deploy; this adds the radar
middleware and two JSON endpoints. uvicorn server:app."""
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import bot_radar

try:
    import ask_api
except Exception:                      # never let the board break the site
    ask_api = None

app = FastAPI(title="The DMT Atlas")

# Meta-ExternalAgent scrapes URL-shaped strings out of raw inline JS, so it invents
# paths from unrendered template literals and then re-fetches them forever. Measured
# 2026-08-08 in bot_hits: 76 fetches of /entities/null, /motifs/null, /geometry/null,
# /realms/null, /crossings/null, /research/null and /null — every one of them
# Meta-ExternalAgent, and it is the site's single biggest real-content crawler (37.8%).
# A 404 means "try again later" and it does. 410 is Gone, which Meta honors; that is
# the fix already shipped across nine fleet repos. Do not go hunting the markup.
_GONE = re.compile(r"^/(?:[a-z0-9-]+/)*(?:null|undefined)/?$", re.I)


@app.middleware("http")
async def radar(request: Request, call_next):
    if _GONE.match(request.url.path):
        resp = PlainTextResponse("410 Gone — this URL never existed.", status_code=410)
    else:
        resp = await call_next(request)
    try:
        bot_radar.log(request, resp.status_code)
    except Exception:
        pass
    return resp

# --- question board ---------------------------------------------------------
# Declared BEFORE the StaticFiles mount: a mount at "/" swallows every route
# registered after it.

@app.post("/api/ask")
async def api_ask(request: Request):
    if ask_api is None:
        return JSONResponse({"ok": False, "message": "Board unavailable."}, status_code=503)
    try:
        data = await request.json()
    except Exception:
        try:
            data = dict(await request.form())
        except Exception:
            data = {}
    status, payload = ask_api.submit(request, data.get("body", ""), data.get("context", ""))
    return JSONResponse(payload, status_code=status)

@app.get("/api/ask/recent")
async def api_ask_recent():
    if ask_api is None:
        return JSONResponse({"questions": []})
    return JSONResponse(ask_api.recent())

# serve the site (index.html at /, all assets/pages relative) from the repo root
app.mount("/", StaticFiles(directory=".", html=True), name="site")
