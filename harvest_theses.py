#!/usr/bin/env python3
"""Harvest DMT / ayahuasca DISSERTATIONS & THESES into a deduplicated JSON catalog.
OpenAlex is the workhorse; CORE + BASE are supplements. Metadata + abstracts only."""
import requests, json, time, re, os

BASE_DIR = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas"
OUT = os.path.join(BASE_DIR, "data/research/theses.json")
RAW_DIR = os.path.join(BASE_DIR, "data/research/raw")
os.makedirs(RAW_DIR, exist_ok=True)

MAILTO = "research@dmtatlas.com"
S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (dmtatlas research archive; mailto:%s)" % MAILTO})

source_notes = []
def log(m): print(m, flush=True)

# ==================================================================
# OpenAlex
# ==================================================================
def reconstruct_abstract(inv):
    if not inv:
        return None
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    if not pos:
        return None
    pos.sort()
    return " ".join(w for _, w in pos)

def oa_paginate(filt, label):
    out = []
    cursor = "*"
    pg = 0
    while cursor:
        params = {"filter": filt, "per-page": 200, "cursor": cursor, "mailto": MAILTO}
        try:
            r = S.get("https://api.openalex.org/works", params=params, timeout=60)
        except Exception as e:
            log("  OA error %s: %s" % (label, e)); break
        if r.status_code != 200:
            log("  OA HTTP %s for %s (%s)" % (r.status_code, label, filt)); return out, r.status_code
        d = r.json()
        batch = d.get("results", [])
        out.extend(batch)
        pg += 1
        meta = d.get("meta", {})
        cursor = meta.get("next_cursor")
        log("  [%s] page %d +%d (count=%s)" % (label, pg, len(batch), meta.get("count")))
        if not batch: break
        time.sleep(0.15)
    return out, 200

def harvest_openalex():
    log("=== OpenAlex ===")
    terms = ["dimethyltryptamine", "ayahuasca", "N,N-dimethyltryptamine",
             "psychedelic tryptamine", "harmine harmaline", "yage", "5-MeO-DMT"]
    works = {}
    thesis_type_ok = None
    # Pass A: type:dissertation
    for t in terms:
        res, code = oa_paginate("type:dissertation,title_and_abstract.search:%s" % t, "diss:%s" % t)
        for w in res: works[w["id"]] = w
    # Pass B: type:thesis (may 400/empty)
    for t in terms:
        res, code = oa_paginate("type:thesis,title_and_abstract.search:%s" % t, "thesis:%s" % t)
        if code != 200:
            thesis_type_ok = False
        else:
            if thesis_type_ok is None: thesis_type_ok = True
            for w in res: works[w["id"]] = w
    # Pass C: broad (no type) topic search -> keep only thesis-like records not already captured
    broad_kept = 0
    for t in terms:
        res, code = oa_paginate("title_and_abstract.search:%s" % t, "broad:%s" % t)
        for w in res:
            if w["id"] in works:
                continue
            typ = (w.get("type") or "").lower()
            title = (w.get("title") or "").lower()
            venue = ""
            hv = w.get("primary_location") or {}
            src = (hv.get("source") or {})
            venue = (src.get("display_name") or "").lower()
            hint = " ".join([title, venue, typ])
            if typ == "dissertation" or any(k in hint for k in [
                "thesis", "dissertation", "doctoral", "ph.d", " phd", "master's thesis",
                "submitted in partial fulfillment", "degree of doctor", "degree of master"]):
                works[w["id"]] = w
                broad_kept += 1
    log("OpenAlex unique candidate works: %d (broad-pass added %d)" % (len(works), broad_kept))
    with open(os.path.join(RAW_DIR, "theses_openalex_raw.json"), "w", encoding="utf-8") as f:
        json.dump(list(works.values()), f)
    tn = "thesis type filter: %s" % ("returned data" if thesis_type_ok else "invalid/empty (OpenAlex has no 'thesis' type)")
    source_notes.append("OpenAlex: OK — %d candidate works (dissertation type + broad thesis-like sweep, 7 terms). %s." % (len(works), tn))
    return list(works.values())

# ==================================================================
# CORE (try without key)
# ==================================================================
def harvest_core():
    log("=== CORE ===")
    out = []
    url = "https://api.core.ac.uk/v3/search/works"
    queries = ["dimethyltryptamine thesis", "ayahuasca dissertation", "ayahuasca thesis", "dimethyltryptamine dissertation"]
    worked = False
    for q in queries:
        try:
            r = S.post(url, json={"q": q, "limit": 50}, timeout=45)
        except Exception as e:
            log("  CORE error: %s" % e)
            source_notes.append("CORE: request error (%s) — skipped." % e); return out
        if r.status_code in (401, 403):
            log("  CORE auth required HTTP %s — skip." % r.status_code)
            source_notes.append("CORE: HTTP %s (API key required, none supplied) — skipped." % r.status_code); return out
        if r.status_code == 429:
            log("  CORE 429 rate limit; waiting 15s"); time.sleep(15)
            try: r = S.post(url, json={"q": q, "limit": 50}, timeout=45)
            except Exception:
                source_notes.append("CORE: rate-limited (429) then error — partial/skipped."); break
        if r.status_code != 200:
            log("  CORE HTTP %s '%s'" % (r.status_code, q)); continue
        worked = True
        d = r.json()
        hits = d.get("results", [])
        log("  CORE '%s' +%d (total=%s)" % (q, len(hits), d.get("totalHits")))
        out.extend(hits)
        time.sleep(2.0)
    if worked:
        source_notes.append("CORE: OK without key — %d raw hits across %d queries." % (len(out), len(queries)))
        with open(os.path.join(RAW_DIR, "theses_core_raw.json"), "w", encoding="utf-8") as f:
            json.dump(out, f)
    return out

# ==================================================================
# BASE (HTML)
# ==================================================================
def harvest_base():
    log("=== BASE ===")
    url = "https://www.base-search.net/Search/Results"
    for q in ["ayahuasca dissertation", "dimethyltryptamine thesis"]:
        try:
            r = S.get(url, params={"lookfor": q, "type": "all"}, timeout=30)
        except Exception as e:
            log("  BASE error: %s" % e)
            source_notes.append("BASE: request error (%s) — skipped." % e); return []
        log("  BASE '%s' HTTP %s len=%d" % (q, r.status_code, len(r.text)))
        if r.status_code != 200:
            source_notes.append("BASE: HTTP %s — skipped." % r.status_code); return []
        with open(os.path.join(RAW_DIR, "theses_base_%s.html" % q.replace(" ", "_")), "w", encoding="utf-8") as f:
            f.write(r.text)
        time.sleep(1.0)
    source_notes.append("BASE: HTTP 200 but results are rendered client-side / no stable structured records in HTML — raw saved, not merged.")
    return []

if __name__ == "__main__":
    oa = harvest_openalex()
    core = harvest_core()
    base = harvest_base()
    with open(os.path.join(RAW_DIR, "theses_source_notes.json"), "w", encoding="utf-8") as f:
        json.dump(source_notes, f, indent=2)
    log("\n".join(source_notes))
    log("HARVEST DONE: OpenAlex=%d CORE=%d BASE=%d" % (len(oa), len(core), len(base)))
