"""ask_api.py — the Atlas question board: submission, charter gate, moderation.

WHY THIS IS PRE-MODERATED, NOT AN OPEN FORUM
    BUILD.md's charter is not decoration: "NOT a guide to obtaining, making, or
    taking any substance. No synthesis, no extraction, no dosing." An open board
    on this subject does not stay inside that line by hoping. We measured the
    base rate on the largest DMT forum in existence: of 71,580 thread titles,
    14,616 — 20.4% — are extraction, synthesis, sourcing or cultivation. One
    post in five would be content this site has promised not to host.

    So: nothing is public until a human approves it. Submissions are screened
    at the door by the same charter filter demand_mine.py uses, and the rest
    queue as `pending`. A rejected submission is still recorded (without being
    published) because it is still demand data — which is the whole point of
    having the board.

Endpoints (mounted by server.py):
    POST /api/ask        submit a question   -> {ok, status, message}
    GET  /api/ask/recent published questions -> {questions:[...]}
"""
import os
import re
import json
import time
import threading
import urllib.request

from demand_mine import EXCLUDE, THEMES

_URL = os.environ.get("LEADS_SUPABASE_URL", "").rstrip("/")
_KEY = os.environ.get("LEADS_SUPABASE_KEY", "")
TABLE = "atlas_questions"

MAX_LEN = 1200
MIN_LEN = 12

# Beyond the charter filter: things a public board must refuse outright.
HARD_BLOCK = re.compile(
    r"\b(where can i (buy|get|score)|dm me|telegram|wickr|signal me|"
    r"selling|for sale|vendor list|darknet|dread|market link|"
    r"kill myself|suicide|end it all|want to die)\b", re.I)

CRISIS_NOTE = (
    "If you are in crisis, please reach a human now — call or text 988 in the US "
    "(Suicide & Crisis Lifeline), or Fireside Project's psychedelic peer-support "
    "line at 62-FIRESIDE. This board cannot help in an emergency."
)

CHARTER_NOTE = (
    "This board maps what people experience and report — it can't host questions "
    "about obtaining, making, extracting, or dosing anything. That's the Atlas's "
    "charter, not a judgement. Ask about what you saw, what it meant, or what the "
    "research says, and it belongs here."
)

_rate = {}
_rate_lock = threading.Lock()


def _client_ip(request):
    return (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "") or "")


def _rate_ok(ip, limit=5, window=3600):
    """Content-level abuse still gets through IP limits (an IP-rotating bot is
    invisible to this), so treat it as a courtesy throttle, not a defence."""
    now = time.time()
    with _rate_lock:
        hits = [t for t in _rate.get(ip, []) if now - t < window]
        if len(hits) >= limit:
            return False
        hits.append(now)
        _rate[ip] = hits
        if len(_rate) > 5000:
            for k in [k for k, v in _rate.items() if not any(now - t < window for t in v)]:
                _rate.pop(k, None)
    return True


def classify(text):
    for name, pat, target in THEMES:
        if re.search(pat, text, re.I):
            return name, target
    return "unsorted", ""


def _post_row(row):
    if not (_URL and _KEY):
        return
    try:
        req = urllib.request.Request(
            _URL + "/rest/v1/" + TABLE, data=json.dumps(row).encode(), method="POST",
            headers={"apikey": _KEY, "Authorization": "Bearer " + _KEY,
                     "Content-Type": "application/json", "Prefer": "return=minimal"})
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass


def _get_published(limit=60):
    if not (_URL and _KEY):
        return []
    try:
        url = ("%s/rest/v1/%s?status=eq.published&order=ts.desc&limit=%d"
               "&select=id,ts,body,theme" % (_URL, TABLE, limit))
        req = urllib.request.Request(
            url, headers={"apikey": _KEY, "Authorization": "Bearer " + _KEY})
        return json.loads(urllib.request.urlopen(req, timeout=8).read())
    except Exception:
        return []


def submit(request, body, context=""):
    """Returns (http_status, payload). Never raises."""
    text = re.sub(r"\s+", " ", (body or "")).strip()[:MAX_LEN]
    ctx = re.sub(r"\s+", " ", (context or "")).strip()[:MAX_LEN]
    ip = _client_ip(request)
    ua = (request.headers.get("user-agent", "") or "")[:400]

    if len(text) < MIN_LEN:
        return 400, {"ok": False, "message": "Say a little more — what did you want to ask?"}

    blob = text + " " + ctx
    if re.search(r"\b(kill myself|suicide|end it all|want to die)\b", blob, re.I):
        _post_row({"body": text, "context": ctx, "theme": "crisis", "status": "rejected",
                   "reject_reason": "crisis", "ip": ip, "ua": ua})
        return 200, {"ok": False, "status": "crisis", "message": CRISIS_NOTE}

    if HARD_BLOCK.search(blob) or EXCLUDE.search(blob):
        # Recorded, not published: still demand data, just not servable demand.
        _post_row({"body": text, "context": ctx, "theme": "charter",
                   "status": "rejected", "reject_reason": "charter", "ip": ip, "ua": ua})
        return 200, {"ok": False, "status": "off-charter", "message": CHARTER_NOTE}

    if not _rate_ok(ip):
        return 429, {"ok": False, "message": "That's a few in a row — try again in a bit."}

    theme, _ = classify(blob)
    _post_row({"body": text, "context": ctx, "theme": theme,
               "status": "pending", "ip": ip, "ua": ua})
    return 200, {"ok": True, "status": "pending", "theme": theme,
                 "message": "Received. Every question is read by a person before it "
                            "appears, so it won't show up immediately."}


def recent():
    return {"questions": _get_published()}
