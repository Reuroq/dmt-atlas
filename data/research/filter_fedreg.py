import json

raw = json.load(open("fedreg_raw.json", encoding="utf-8"))

# collect all docs, dedupe by document_number
seen = {}
for term, blk in raw.items():
    for d in blk.get("docs", []) or []:
        dn = d.get("document_number")
        if dn and dn not in seen:
            seen[dn] = d

def agency_names(d):
    ags = d.get("agencies") or []
    return ", ".join(a.get("name","") for a in ags if isinstance(a, dict))

# Keywords indicating direct relevance to DMT/ayahuasca scheduling or programs
kw = ["dimethyltryptamine", "ayahuasca", "hoasca", "n,n-dmt", " dmt", "5-meo", "banisteriopsis", "psychotrop"]

print(f"total unique docs: {len(seen)}")
print("="*80)
rel = []
for dn, d in seen.items():
    blob = ((d.get("title") or "") + " " + (d.get("abstract") or "")).lower()
    if any(k in blob for k in kw):
        rel.append(d)

# sort by date
rel.sort(key=lambda d: d.get("publication_date") or "")
print(f"keyword-relevant docs: {len(rel)}")
print("="*80)
for d in rel:
    print(f"{d.get('publication_date')} | {d.get('type')} | {agency_names(d)}")
    print(f"   TITLE: {d.get('title')}")
    print(f"   DOC#: {d.get('document_number')}  CITE: {d.get('citation')}")
    ab = (d.get('abstract') or '')[:400]
    if ab: print(f"   ABS: {ab}")
    print(f"   URL: {d.get('html_url')}")
    print("-"*60)
