"""Stage 1: create the dmt-atlas web service (FastAPI+bot radar) and wait for it live.
Low-risk — does NOT touch the live static service or the domain yet."""
import json, time, urllib.request, urllib.error
from pathlib import Path
ENV = Path(r"C:\Users\dwayn\OneDrive\Desktop\workshield-product\.env.deploy")
creds = {}
for line in ENV.read_text(encoding="latin-1").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()
RKEY = creds["RENDER_API_KEY"]; OWNER = creds["RENDER_OWNER_ID"]
LURL = creds["LEADS_SUPABASE_URL"]; LKEY = creds["LEADS_SUPABASE_KEY"]

def req(url, method="GET", data=None):
    h = {"Authorization": f"Bearer {RKEY}", "Accept": "application/json"}
    body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

# reuse if exists
s, existing = req("https://api.render.com/v1/services?limit=100")
svc = None
for it in (existing if isinstance(existing, list) else []):
    sv = it.get("service", it)
    if sv.get("name") == "dmt-atlas-web":
        svc = sv; print("reusing", sv["id"]); break

if not svc:
    payload = {
        "type": "web_service", "name": "dmt-atlas-web", "ownerId": OWNER,
        "repo": "https://github.com/Reuroq/dmt-atlas", "branch": "master", "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python", "region": "oregon", "plan": "starter",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
            },
        },
        "envVars": [
            {"key": "LEADS_SUPABASE_URL", "value": LURL},
            {"key": "LEADS_SUPABASE_KEY", "value": LKEY},
            {"key": "PYTHON_VERSION", "value": "3.12.7"},
        ],
    }
    s, o = req("https://api.render.com/v1/services", "POST", payload)
    print("create status", s)
    if s not in (200, 201):
        print(json.dumps(o)[:800]); raise SystemExit(1)
    svc = o.get("service", o)

SID = svc["id"]
url = svc.get("serviceDetails", {}).get("url") or "https://dmt-atlas-web.onrender.com"
print("WEB service id:", SID)
print("onrender url:", url)
print("waiting for build+deploy (installing fastapi/uvicorn ~2-4 min)...")
for _ in range(70):
    s, dl = req(f"https://api.render.com/v1/services/{SID}/deploys?limit=1")
    if isinstance(dl, list) and dl:
        st = dl[0].get("deploy", {}).get("status", "?")
        print("  deploy:", st)
        if st == "live": print("LIVE ->", url); break
        if st in ("build_failed", "update_failed", "canceled", "deactivated"):
            print("FAILED:", st); break
    time.sleep(9)
