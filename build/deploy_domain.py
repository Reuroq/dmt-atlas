"""Register dmtatlas.com (Name.com), attach to the Render service, wire DNS, poll TLS."""
import json, time, base64, urllib.request, urllib.error
from pathlib import Path

ENV = Path(r"C:\Users\dwayn\OneDrive\Desktop\workshield-product\.env.deploy")
creds = {}
for line in ENV.read_text(encoding="latin-1").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()

RKEY = creds["RENDER_API_KEY"]
NC_USER, NC_TOKEN = creds["NAMECOM_USERNAME"], creds["NAMECOM_API_TOKEN"]
SERVICE_ID = "srv-d8t78lok1i2s738c1m40"
DOMAIN = "dmtatlas.com"
ONRENDER = "dmt-atlas.onrender.com"
RENDER_APEX_IP = "216.24.57.1"   # Render anycast A record for apex domains
NC = "https://api.name.com"

def req(url, method="GET", headers=None, data=None):
    h = headers or {}; body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e:
        return 0, {"error": str(e)}

def rh(): return {"Authorization": f"Bearer {RKEY}", "Accept": "application/json"}
def nh():
    tok = base64.b64encode(f"{NC_USER}:{NC_TOKEN}".encode()).decode()
    return {"Authorization": f"Basic {tok}", "Accept": "application/json"}

# 1) register (idempotent — if already owned, Name.com returns an error we tolerate)
print("== register", DOMAIN)
s, o = req(f"{NC}/v4/domains", "POST", nh(),
           {"domain": {"domainName": DOMAIN}, "purchasePrice": 12.99,
            "purchaseType": "registration", "years": 1})
if s in (200, 201):
    d = o.get("domain", o)
    print(f"  REGISTERED expires={d.get('expireDate')} ns={d.get('nameservers')}")
else:
    print(f"  register http={s} -> {json.dumps(o)[:240]} (continuing — may already be owned)")

# 2) attach custom domains to Render
for name in (DOMAIN, f"www.{DOMAIN}"):
    s, o = req(f"https://api.render.com/v1/services/{SERVICE_ID}/custom-domains", "POST", rh(), {"name": name})
    print(f"== render add-domain {name}: http={s} {o.get('name','') if isinstance(o,dict) else ''} {o.get('message','') if isinstance(o,dict) else ''}")

# 3) DNS at Name.com — clear conflicting apex A / www, then add ours
s, recs = req(f"{NC}/v4/domains/{DOMAIN}/records", headers=nh())
for r in (recs.get("records") or []):
    host = r.get("host", ""); typ = r.get("type")
    if (host == "" and typ in ("A", "ALIAS", "ANAME")) or (host == "www" and typ in ("A", "CNAME", "ALIAS")):
        ds, _ = req(f"{NC}/v4/domains/{DOMAIN}/records/{r['id']}", "DELETE", nh())
        print(f"  deleted conflicting {typ} host='{host}' -> {ds}")

def add(host, typ, answer):
    s, o = req(f"{NC}/v4/domains/{DOMAIN}/records", "POST", nh(),
               {"host": host, "type": typ, "answer": answer, "ttl": 300})
    print(f"  add {typ} host='{host}' -> {answer}: http={s} {o.get('message','') if isinstance(o,dict) else ''}")

add("", "A", RENDER_APEX_IP)
add("www", "CNAME", ONRENDER + ".")

# 4) poll Render custom-domain verification / cert
print("== waiting for verification + TLS (can take a few minutes)...")
for _ in range(40):
    s, dl = req(f"https://api.render.com/v1/services/{SERVICE_ID}/custom-domains?limit=10", headers=rh())
    rows = dl if isinstance(dl, list) else []
    states = []
    for it in rows:
        cd = it.get("customDomain", it)
        states.append(f"{cd.get('name')}={cd.get('verificationStatus')}")
    print("  ", " | ".join(states))
    if states and all("verified" in s.lower() for s in states):
        print("ALL VERIFIED"); break
    time.sleep(10)
print("done — DNS may still be propagating; TLS issues automatically once verified.")
