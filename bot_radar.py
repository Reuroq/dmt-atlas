"""bot_radar.py - fleet AI-bot fetch logger (FastAPI/Starlette). GA4 can't see crawlers;
we log them server-side. Best-effort, non-blocking, swallows all errors. Writes to the
fleet-leads Supabase bot_hits table via LEADS_SUPABASE_URL/KEY."""
import os, json, threading, urllib.request
_URL = os.environ.get("LEADS_SUPABASE_URL", "").rstrip("/")
_KEY = os.environ.get("LEADS_SUPABASE_KEY", "")
_BOTS = [("GPTBot","GPTBot"),("OAI-SearchBot","OAI-SearchBot"),("ChatGPT-User","ChatGPT-User"),
    ("ClaudeBot","ClaudeBot"),("Claude-User","Claude-User"),("Claude-Web","Claude-Web"),
    ("anthropic-ai","anthropic-ai"),("PerplexityBot","PerplexityBot"),("Perplexity-User","Perplexity-User"),
    ("Google-Extended","Google-Extended"),("CCBot","CCBot"),("Bytespider","Bytespider"),
    ("Amazonbot","Amazonbot"),("Meta-ExternalAgent","Meta-ExternalAgent"),("Applebot-Extended","Applebot-Extended"),
    ("DuckAssistBot","DuckAssistBot"),("cohere-ai","cohere-ai"),("YouBot","YouBot"),("Diffbot","Diffbot")]
def _match(ua):
    u = ua.lower()
    for n,l in _BOTS:
        if n.lower() in u: return l
    return None
def _post(row):
    if not (_URL and _KEY): return
    try:
        req = urllib.request.Request(_URL+"/rest/v1/bot_hits", data=json.dumps(row).encode(), method="POST",
            headers={"apikey":_KEY,"Authorization":"Bearer "+_KEY,"Content-Type":"application/json","Prefer":"return=minimal"})
        urllib.request.urlopen(req, timeout=6)
    except Exception: pass
def log(request, status, site=None):
    """FastAPI/Starlette Request. Fire-and-forget; only logs known AI bots."""
    try:
        ua = request.headers.get("user-agent","") or ""
        bot = _match(ua)
        if not bot: return
        host = (request.url.hostname or "").lower()
        site = site or (host[4:] if host.startswith("www.") else host) or "unknown"
        ip = (request.headers.get("x-forwarded-for","").split(",")[0].strip() or (request.client.host if request.client else ""))
        row = {"site":site,"bot":bot,"path":request.url.path[:300],"status":int(status),"ua":ua[:400],"ip":ip[:64]}
        threading.Thread(target=_post, args=(row,), daemon=True).start()
    except Exception: pass
