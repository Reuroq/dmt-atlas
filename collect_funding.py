#!/usr/bin/env python3
"""Collect DMT / ayahuasca research grant metadata from public funders.

Sources:
  1. NIH RePORTER API v2 (POST) - US federal grants
  2. UKRI Gateway to Research (GET) - UK grants
  3. NSF Awards API (GET) - US NSF grants (supplement)

The bare "N,N-DMT" / "DMT" acronym collides catastrophically at NIH
(218,947 hits) so we NEVER run it alone. We use precise full-word searches
plus AND-combos ("DMT psychedelic", "DMT hallucinogen") and abort any search
whose reported total exceeds COLLISION_CAP.
"""
import json, time, sys, os
import requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (research-archive dmtatlas.com aggregator)"}
COLLISION_CAP = 1500  # any search bigger than this is an acronym collision -> abort

# ---------------------------------------------------------------------------
# 1. NIH RePORTER
# ---------------------------------------------------------------------------
NIH_URL = "https://api.reporter.nih.gov/v2/projects/search"

def nih_search(search_text, label, operator="and"):
    all_rows = []
    offset = 0
    limit = 100
    collided_total = None
    while True:
        body = {
            "criteria": {
                "advanced_text_search": {
                    "operator": operator,
                    "search_field": "projecttitle,abstracttext,terms",
                    "search_text": search_text,
                }
            },
            "limit": limit,
            "offset": offset,
        }
        for attempt in range(4):
            try:
                r = requests.post(NIH_URL, json=body, headers=UA, timeout=60)
                if r.status_code == 429:
                    time.sleep(3 + attempt * 2)
                    continue
                r.raise_for_status()
                break
            except Exception as e:
                print(f"  [NIH {label}] offset {offset} attempt {attempt} err: {e}", file=sys.stderr)
                time.sleep(2 + attempt * 2)
        else:
            print(f"  [NIH {label}] giving up at offset {offset}", file=sys.stderr)
            break
        data = r.json()
        results = data.get("results", [])
        total = data.get("meta", {}).get("total", 0)
        if offset == 0 and total > COLLISION_CAP:
            print(f"  [NIH {label}] COLLISION total={total} > cap {COLLISION_CAP} -> ABORT (kept 0)")
            collided_total = total
            break
        all_rows.extend(results)
        print(f"  [NIH {label}] offset {offset}: got {len(results)} (total {total})")
        offset += limit
        if offset >= total or not results:
            break
        time.sleep(0.5)
    return all_rows, collided_total

# ---------------------------------------------------------------------------
# 2. UKRI Gateway to Research
# ---------------------------------------------------------------------------
GTR_URL = "https://gtr.ukri.org/gtr/api/projects"

def gtr_search(query, label):
    all_rows = []
    page = 1
    while True:
        params = {"q": query, "p": page, "s": 100}
        headers = dict(UA); headers["Accept"] = "application/json"
        for attempt in range(4):
            try:
                r = requests.get(GTR_URL, params=params, headers=headers, timeout=60)
                if r.status_code == 429:
                    time.sleep(3 + attempt * 2); continue
                r.raise_for_status(); break
            except Exception as e:
                print(f"  [GTR {label}] page {page} attempt {attempt} err: {e}", file=sys.stderr)
                time.sleep(2 + attempt * 2)
        else:
            break
        try:
            data = r.json()
        except Exception as e:
            print(f"  [GTR {label}] json err: {e} head: {r.text[:150]}", file=sys.stderr); break
        projects = data.get("project", [])
        total_pages = int(data.get("totalPages", 1) or 1)
        all_rows.extend(projects)
        print(f"  [GTR {label}] page {page}/{total_pages}: got {len(projects)}")
        if page >= total_pages or not projects or page >= 10:
            break
        page += 1; time.sleep(0.5)
    return all_rows

# ---------------------------------------------------------------------------
# 3. NSF Awards API
# ---------------------------------------------------------------------------
NSF_URL = "https://api.nsf.gov/services/v1/awards.json"

def nsf_search(keyword, label):
    all_rows = []
    offset = 1
    fields = ("id,title,awardeeName,fundsObligatedAmt,startDate,piFirstName,"
              "piLastName,abstractText,fundProgramName,agency,date,estimatedTotalAmt")
    while True:
        params = {"keyword": keyword, "printFields": fields, "offset": offset, "rpp": 25}
        for attempt in range(4):
            try:
                r = requests.get(NSF_URL, params=params, headers=UA, timeout=60)
                if r.status_code == 429:
                    time.sleep(3 + attempt * 2); continue
                r.raise_for_status(); break
            except Exception as e:
                print(f"  [NSF {label}] offset {offset} attempt {attempt} err: {e}", file=sys.stderr)
                time.sleep(2 + attempt * 2)
        else:
            break
        try:
            data = r.json()
        except Exception as e:
            print(f"  [NSF {label}] json err: {e} head: {r.text[:150]}", file=sys.stderr); break
        awards = data.get("response", {}).get("award", [])
        all_rows.extend(awards)
        print(f"  [NSF {label}] offset {offset}: got {len(awards)}")
        if len(awards) < 25:
            break
        offset += 25; time.sleep(0.5)
    return all_rows


def main():
    out = {}
    collisions = {}

    print("=== NIH RePORTER ===")
    nih_queries = [
        ("dimethyltryptamine", "dimethyltryptamine"),
        ("ayahuasca", "ayahuasca"),
        ("DMT psychedelic", "DMT+psychedelic"),
        ("DMT hallucinogen", "DMT+hallucinogen"),
        ("DMT tryptamine", "DMT+tryptamine"),
        ("5-MeO-DMT", "5-MeO-DMT"),
        ("banisteriopsis", "banisteriopsis"),
        ("psychotria viridis", "psychotria_viridis"),
        ("harmaline harmine", "harmaline+harmine"),
    ]
    for text, label in nih_queries:
        rows, collided = nih_search(text, label)
        out[f"nih_{label}"] = rows
        if collided is not None:
            collisions[f"nih_{label}"] = collided
        time.sleep(0.3)

    print("=== UKRI GtR ===")
    out["gtr_ayahuasca"] = gtr_search("ayahuasca", "ayahuasca")
    out["gtr_dimethyltryptamine"] = gtr_search("dimethyltryptamine", "dimethyltryptamine")

    print("=== NSF ===")
    try:
        out["nsf_ayahuasca"] = nsf_search("ayahuasca", "ayahuasca")
        out["nsf_dimethyltryptamine"] = nsf_search("dimethyltryptamine", "dimethyltryptamine")
    except Exception as e:
        print(f"NSF failed: {e}", file=sys.stderr)
        out.setdefault("nsf_ayahuasca", []); out.setdefault("nsf_dimethyltryptamine", [])

    for k, v in out.items():
        with open(os.path.join(RAW, f"{k}.json"), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, indent=1)
        print(f"WROTE {k}: {len(v)} rows")
    with open(os.path.join(RAW, "_collisions.json"), "w", encoding="utf-8") as f:
        json.dump(collisions, f, indent=1)
    print("COLLISIONS:", collisions)


if __name__ == "__main__":
    main()
