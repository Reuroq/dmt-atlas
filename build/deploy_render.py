"""Create the Render static site for dmt-atlas and wait for the first deploy."""
import json, time, urllib.request, urllib.error
from pathlib import Path

ENV = Path(r"C:\Users\dwayn\OneDrive\Desktop\workshield-product\.env.deploy")
creds = {}
for line in ENV.read_text(encoding="latin-1").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()
KEY = creds["RENDER_API_KEY"]; OWNER = creds.get("RENDER_OWNER_ID", "")

def req(url, method="GET", data=None):
    h = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
    body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

if not OWNER:
    s, o = req("https://api.render.com/v1/owners?limit=1")
    OWNER = o[0]["owner"]["id"]

# reuse if a dmt-atlas service already exists
s, existing = req("https://api.render.com/v1/services?limit=50")
svc = None
for it in (existing if isinstance(existing, list) else []):
    sv = it.get("service", it)
    if sv.get("name") == "dmt-atlas":
        svc = sv; print("reusing existing service", sv["id"]); break

if not svc:
    payload = {
        "type": "static_site", "name": "dmt-atlas", "ownerId": OWNER,
        "repo": "https://github.com/Reuroq/dmt-atlas", "branch": "master",
        "autoDeploy": "yes",
        "serviceDetails": {"buildCommand": "", "publishPath": "."},
    }
    s, o = req("https://api.render.com/v1/services", "POST", payload)
    print("create status", s)
    if s not in (200, 201):
        print(json.dumps(o)[:600]); raise SystemExit(1)
    svc = o.get("service", o)
SID = svc["id"]
url = svc.get("serviceDetails", {}).get("url") or f"https://dmt-atlas.onrender.com"
print("service id:", SID)
print("url:", url)

# poll latest deploy
print("waiting for deploy...")
for _ in range(60):
    s, dl = req(f"https://api.render.com/v1/services/{SID}/deploys?limit=1")
    if isinstance(dl, list) and dl:
        st = dl[0].get("deploy", {}).get("status", "?")
        print("  deploy status:", st)
        if st == "live":
            print("LIVE ->", url); break
        if st in ("build_failed", "update_failed", "canceled", "deactivated"):
            print("DEPLOY FAILED:", st); break
    time.sleep(8)
