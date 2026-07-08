"""Stage 2: move dmtatlas.com from the static service to the web service, repoint www, verify."""
import json, time, base64, urllib.request, urllib.error
from pathlib import Path
ENV = Path(r"C:\Users\dwayn\OneDrive\Desktop\workshield-product\.env.deploy")
c = {}
for line in ENV.read_text(encoding="latin-1").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); c[k.strip()] = v.strip()
RKEY = c["RENDER_API_KEY"]; NCU, NCT = c["NAMECOM_USERNAME"], c["NAMECOM_API_TOKEN"]
STATIC = "srv-d8t78lok1i2s738c1m40"
WEB = "srv-d8t7g6e8bjmc73eckai0"
DOMAIN = "dmtatlas.com"; NEW_ONRENDER = "dmt-atlas-web.onrender.com"
NC = "https://api.name.com"

def req(url, method="GET", headers=None, data=None):
    h = headers or {}; body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, (json.loads(e.read().decode() or "{}"))
def rh(): return {"Authorization": f"Bearer {RKEY}", "Accept": "application/json"}
def nh():
    return {"Authorization": "Basic " + base64.b64encode(f"{NCU}:{NCT}".encode()).decode(), "Accept": "application/json"}

# 1) delete the static service (frees the custom domains)
s, o = req(f"https://api.render.com/v1/services/{STATIC}", "DELETE")
print("delete static service:", s)
time.sleep(3)

# 2) attach domains to the web service
for name in (DOMAIN, f"www.{DOMAIN}"):
    for attempt in range(6):
        s, o = req(f"https://api.render.com/v1/services/{WEB}/custom-domains", "POST", rh(), {"name": name})
        msg = o.get("message", "") if isinstance(o, dict) else ""
        print(f"attach {name}: {s} {msg}")
        if s in (200, 201) or "already" in msg.lower():
            break
        time.sleep(5)

# 3) repoint www CNAME -> new onrender host (apex A 216.24.57.1 stays)
s, recs = req(f"{NC}/v4/domains/{DOMAIN}/records", headers=nh())
for r in (recs.get("records") or []):
    if r.get("host") == "www" and r.get("type") == "CNAME":
        ds, _ = req(f"{NC}/v4/domains/{DOMAIN}/records/{r['id']}", "DELETE", nh())
        print("deleted old www CNAME ->", ds)
s, o = req(f"{NC}/v4/domains/{DOMAIN}/records", "POST", nh(),
           {"host": "www", "type": "CNAME", "answer": NEW_ONRENDER + ".", "ttl": 300})
print("new www CNAME ->", s)

# 4) verify
print("verifying on web service...")
for _ in range(40):
    s, dl = req(f"https://api.render.com/v1/services/{WEB}/custom-domains?limit=20", headers=rh())
    ds = [it.get("customDomain", it) for it in (dl if isinstance(dl, list) else [])]
    for d in ds:
        if d.get("verificationStatus") != "verified":
            req(f"https://api.render.com/v1/services/{WEB}/custom-domains/{d['id']}/verify", "POST", rh())
    ds = [it.get("customDomain", it) for it in (req(f"https://api.render.com/v1/services/{WEB}/custom-domains?limit=20", headers=rh())[1] or [])]
    print("  " + " | ".join(f"{d.get('name')}={d.get('verificationStatus')}" for d in ds))
    if ds and all(d.get("verificationStatus") == "verified" for d in ds):
        print("ALL VERIFIED"); break
    time.sleep(10)
