"""Serves the static DMT Atlas + the fleet AI-bot radar (server-side LLM-crawler logging)
+ the /ask question board API. Same files as the static deploy; this adds the radar
middleware and two JSON endpoints. uvicorn server:app."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import bot_radar

try:
    import ask_api
except Exception:                      # never let the board break the site
    ask_api = None

app = FastAPI(title="The DMT Atlas")

@app.middleware("http")
async def radar(request: Request, call_next):
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
