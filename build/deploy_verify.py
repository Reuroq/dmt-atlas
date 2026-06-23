"""Accurately poll Render custom-domain verification for dmtatlas.com; nudge verify; check DNS."""
import json, time, base64, socket, urllib.request, urllib.error
from pathlib import Path
ENV = Path(r"C:\Users\dwayn\OneDrive\Desktop\workshield-product\.env.deploy")
creds = {}
for line in ENV.read_text(encoding="latin-1").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()
RKEY = creds["RENDER_API_KEY"]
SID = "srv-d8t78lok1i2s738c1m40"
def req(url, method="GET", data=None):
    h = {"Authorization": f"Bearer {RKEY}", "Accept": "application/json"}
    body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def domains():
    s, dl = req(f"https://api.render.com/v1/services/{SID}/custom-domains?limit=20")
    return [it.get("customDomain", it) for it in (dl if isinstance(dl, list) else [])]

# ensure www attached to OUR service
have = {d.get("name") for d in domains()}
if "www.dmtatlas.com" not in have:
    s, o = req(f"https://api.render.com/v1/services/{SID}/custom-domains", "POST", {"name": "www.dmtatlas.com"})
    print("re-add www:", s, o.get("message", "") if isinstance(o, dict) else "")

for _ in range(30):
    ds = domains()
    # nudge verify on any not-yet-verified
    for d in ds:
        if d.get("verificationStatus") != "verified":
            req(f"https://api.render.com/v1/services/{SID}/custom-domains/{d['id']}/verify", "POST")
    ds = domains()
    print("  " + " | ".join(f"{d.get('name')}={d.get('verificationStatus')}" for d in ds))
    if ds and all(d.get("verificationStatus") == "verified" for d in ds):
        print("ALL VERIFIED"); break
    time.sleep(12)

# DNS resolution sanity
try:
    print("apex A resolves ->", socket.gethostbyname("dmtatlas.com"))
except Exception as e:
    print("apex not resolving yet:", e)
