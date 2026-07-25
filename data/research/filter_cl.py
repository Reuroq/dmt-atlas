import json
raw = json.load(open("courtlistener_raw.json", encoding="utf-8"))

seen = {}
for q, blk in raw.items():
    for r in blk.get("results", []) or []:
        url = r.get("absolute_url")
        key = url or r.get("caseName")
        if key and key not in seen:
            seen[key] = r

# Filter to likely-relevant by case name keywords
kw = ["o centro", "vegetal", "udv", "santo daime", "holy light", "hoasca", "ayahuasca",
      "quaintance", "mukasey", "holder", "ashcroft", "gonzales", "sequoyah", "oklevueha"]
print(f"unique CL results: {len(seen)}")
print("="*80)
for key, r in seen.items():
    name = (r.get("caseName") or "").lower()
    if any(k in name for k in kw):
        print(f"{r.get('dateFiled')} | {r.get('court_citation_string') or r.get('court')}")
        print(f"   {r.get('caseName')}")
        cites = r.get('citation')
        print(f"   docket: {r.get('docketNumber')}  cite: {cites}")
        print(f"   URL: https://www.courtlistener.com{r.get('absolute_url')}")
        print("-"*60)
