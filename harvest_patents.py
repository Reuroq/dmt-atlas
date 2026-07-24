#!/usr/bin/env python3
"""Harvest DMT / 5-MeO-DMT / ayahuasca psychedelic-therapeutic PATENTS via the
Google Patents public XHR endpoint. Bibliographic metadata only (title, snippet,
assignee, inventors, dates, family) - NO synthesis/manufacturing detail captured.
Self-throttling with backoff; saves raw harvest incrementally so a mid-run block
never loses progress."""
import json, time, os, urllib.parse
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "data", "research", "raw", "patents_raw.json")
LOG = os.path.join(BASE, "harvest_patents.log")
os.makedirs(os.path.dirname(RAW), exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "application/json",
                  "Referer": "https://patents.google.com/"})

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch(query, page):
    inner = urllib.parse.quote(query, safe='')
    extra = f"%26num%3D100%26page%3D{page}"
    url = f"https://patents.google.com/xhr/query?url=q%3D{inner}{extra}&exp="
    backoffs = [15, 30, 60, 120, 180]
    for i in range(6):
        try:
            r = S.get(url, timeout=45)
            if r.status_code == 200:
                return r.json()
            raise RuntimeError(f"HTTP {r.status_code}")
        except Exception as e:
            if i == 5:
                log(f"  FAIL page {page}: {e}")
                return None
            w = backoffs[min(i, len(backoffs) - 1)]
            log(f"  retry {i+1} page {page} ({str(e)[:40]}) wait {w}s")
            time.sleep(w)
    return None

# Full-word "dimethyltryptamine" / "5-methoxy" / "ayahuasca" queries avoid the
# DMT-acronym false positives (Derjaguin-Muller-Toporov, dot-matrix, etc.).
QUERIES = [
    ("TI=(dimethyltryptamine)", "auto"),
    ("AB=(dimethyltryptamine) (therapy OR treatment OR disorder OR depression OR psychedelic OR anxiety OR PTSD OR addiction OR pharmaceutical OR formulation OR dosing)", "auto"),
    ("CL=(dimethyltryptamine) (A61K OR A61P)", "auto"),
    ('AB=("5-methoxy-N,N-dimethyltryptamine")', "5-MeO-DMT"),
    ('TI=("5-methoxy") (dimethyltryptamine OR tryptamine)', "5-MeO-DMT"),
    ('CL=("5-meo-dmt")', "5-MeO-DMT"),
    ("AB=(ayahuasca)", "ayahuasca"),
    ("CL=(ayahuasca) (A61K OR A61P OR treatment OR disorder)", "ayahuasca"),
    ("TI=(ayahuasca)", "ayahuasca"),
    ('assignee:"Small Pharma" (dimethyltryptamine OR tryptamine OR psychedelic)', "auto"),
    ('assignee:"Cybin" (dimethyltryptamine OR tryptamine OR psychedelic)', "auto"),
    ('assignee:"Entheon" (dimethyltryptamine OR tryptamine OR psychedelic)', "auto"),
    ('assignee:"Algernon" (dimethyltryptamine OR DMT OR tryptamine)', "auto"),
    ('assignee:"Mydecine" (tryptamine OR psychedelic OR DMT)', "auto"),
    ('assignee:"GH Research" (dimethyltryptamine OR DMT OR tryptamine)', "auto"),
    ('assignee:"Beckley" (dimethyltryptamine OR DMT OR tryptamine OR psychedelic)', "auto"),
    ('assignee:"Eleusis" (dimethyltryptamine OR DMT OR tryptamine)', "auto"),
    ('assignee:"Biomind" (dimethyltryptamine OR DMT OR ayahuasca)', "auto"),
    ("(dimethyltryptamine) (psilocybin) (treatment OR disorder OR depression)", "auto"),
]

def main():
    store = {}
    if os.path.exists(RAW):
        try:
            store = json.load(open(RAW, encoding="utf-8"))
            log(f"resume: {len(store)} existing records")
        except Exception:
            store = {}
    for qi, (q, hint) in enumerate(QUERIES):
        log(f"QUERY {qi+1}/{len(QUERIES)}: {q[:72]}")
        first = fetch(q, 0)
        if not first:
            log("  no response, skip query")
            continue
        res = first.get("results", {}) or {}
        total = res.get("total_num_results", 0)
        pages = min(res.get("total_num_pages", 1) or 1, 10)
        log(f"  total={total} retrievable_pages={pages}")
        added_q = 0
        for p in range(pages):
            data = first if p == 0 else fetch(q, p)
            if not data:
                continue
            clusters = data.get("results", {}).get("cluster", []) or []
            got = 0
            for cl in clusters:
                for item in cl.get("result", []) or []:
                    pid = item.get("id")
                    pat = item.get("patent")
                    if not pid or not pat:
                        continue
                    got += 1
                    if pid not in store:
                        pat["_query_hint"] = hint
                        pat["_id"] = pid
                        pat["_found_via"] = q[:60]
                        store[pid] = pat
                        added_q += 1
            if got == 0:
                break
            time.sleep(5)
        log(f"  query added {added_q} new (store now {len(store)})")
        json.dump(store, open(RAW, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(5)
    log(f"DONE total unique raw records: {len(store)}")

if __name__ == "__main__":
    main()
