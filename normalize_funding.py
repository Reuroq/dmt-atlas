#!/usr/bin/env python3
"""Normalize + dedup DMT/ayahuasca grant records into funding.json.

Dedup policy (DOCUMENTED in source_notes):
  NIH awards recur yearly (one appl_id per fiscal-year action). We first dedup
  raw rows by appl_id, then COLLAPSE to the core project (core_project_num),
  SUMMING award_amount across all fiscal years to get total lifetime funding,
  and recording the fiscal-year span. total_funding_usd = sum over collapsed
  core projects, so no year is double-counted.
"""
import json, os, glob, re, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "data", "research", "funding.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (research-archive dmtatlas.com aggregator)"}

# ---- signal vocab -----------------------------------------------------------
STRONG = ["dimethyltryptamine", "n,n-dmt", "n, n-dmt", "ayahuasca", "banisteriopsis",
          "psychotria viridis", "5-meo-dmt", "5-methoxy-n", "santo daime", "entheogen",
          "yage", "yagé", "hoasca"]
MODERATE = ["psychedelic", "hallucinog", "psilocybin", "psilocin", "mescaline",
            "ibogaine", "tabernanthalog", "5-ht2a", "serotonergic psychedelic",
            "lysergic", "tryptamine hallucinogen", "classic hallucinogen"]
# core projects whose ABSTRACT mentions ayahuasca alkaloids only as background but
# whose actual research purpose is non-psychedelic (reviewed manually):
UNCERTAIN_OVERRIDE = {
    "R01DK128242",   # diabetes / DYRK1A inhibitor harmine (beta-cell regeneration)
    "R61NS138810",   # essential tremor (harmaline as tremorgenic model)
    "R56DA003385",   # broad drugs-of-abuse behavioral analysis
    "ZIADA000522",   # broad stimulant-use-disorder intramural program
}

def signals(blob):
    b = blob.lower()
    s = [k for k in STRONG if k in b]
    m = [k for k in MODERATE if k in b]
    return s, m

def num(x):
    try:
        return int(round(float(x)))
    except Exception:
        return 0

# ---------------------------------------------------------------------------
# NIH
# ---------------------------------------------------------------------------
def load_nih():
    seen_appl = {}
    for path in glob.glob(os.path.join(RAW, "nih_*.json")):
        for r in json.load(open(path, encoding="utf-8")):
            appl = r.get("appl_id")
            if appl is None:
                continue
            seen_appl[appl] = r  # dedup identical appl across queries
    # group by core project
    projects = {}
    for r in seen_appl.values():
        core = r.get("core_project_num") or r.get("project_num")
        projects.setdefault(core, []).append(r)

    records = []
    dropped = 0
    for core, rows in projects.items():
        rows.sort(key=lambda x: (x.get("fiscal_year") or 0))
        latest = rows[-1]
        blob = " ".join(str(x.get("project_title", "")) + " " +
                        str(x.get("abstract_text", "")) + " " +
                        str(x.get("terms", "")) for x in rows)
        s, m = signals(blob)
        if not s and not m:
            dropped += 1
            continue
        total = sum(num(x.get("award_amount")) for x in rows)
        years = sorted({x.get("fiscal_year") for x in rows if x.get("fiscal_year")})
        # PIs union
        pis = {}
        for x in rows:
            for p in (x.get("principal_investigators") or []):
                fn = (p.get("full_name") or "").strip()
                if fn:
                    pis[fn.lower()] = re.sub(r"\s+", " ", fn.title())
        org = (latest.get("organization") or {}).get("org_name") or latest.get("org_name")
        ic = latest.get("agency_ic_admin") or {}
        ic_abbr = ic.get("abbreviation")
        funder = f"NIH/{ic_abbr}" if ic_abbr else "NIH"
        uncertain = (not s and bool(m)) or (core in UNCERTAIN_OVERRIDE)
        records.append({
            "project_title": latest.get("project_title"),
            "pi_names": sorted(pis.values()),
            "institution": org,
            "funder": funder,
            "award_id": core,
            "fiscal_year": (years[0] if years else None),
            "fiscal_year_range": (f"{years[0]}-{years[-1]}" if len(years) > 1 else (str(years[0]) if years else None)),
            "n_fiscal_years": len(years),
            "amount_usd": total,
            "abstract": (latest.get("abstract_text") or "").strip() or None,
            "url": latest.get("project_detail_url"),
            "source": "NIH RePORTER",
            "country": "US",
            "uncertain_topic": uncertain,
        })
    return records, dropped, len(seen_appl)

# ---------------------------------------------------------------------------
# UKRI GtR (enrich with fund + org + PI)
# ---------------------------------------------------------------------------
def gtr_get(url):
    h = dict(UA); h["Accept"] = "application/json"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=h, timeout=45)
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep(1.5)
    return {}

def load_gtr():
    seen = {}
    for path in glob.glob(os.path.join(RAW, "gtr_*.json")):
        for r in json.load(open(path, encoding="utf-8")):
            seen[r.get("id")] = r
    records = []
    for pid, r in seen.items():
        blob = str(r.get("title", "")) + " " + str(r.get("abstractText", "")) + " " + str(r.get("techAbstractText", ""))
        s, m = signals(blob)
        links = r.get("links", {}).get("link", [])
        # fund
        amount = 0; currency = None; start = None; end = None
        fund_hrefs = [l.get("href") for l in links if l.get("rel") == "FUND"]
        if fund_hrefs:
            fd = gtr_get(fund_hrefs[0])
            val = fd.get("valuePounds")
            if isinstance(val, dict):
                amount = num(val.get("amount")); currency = val.get("currencyCode") or "GBP"
            elif val is not None:
                amount = num(val); currency = "GBP"
            start = fd.get("start"); end = fd.get("end")
        # PI persons (top-level firstName/surname on the person resource)
        pis = []
        for l in links:
            if l.get("rel") in ("PI_PER", "STUDENT_PER"):
                per = gtr_get(l.get("href"))
                nm = " ".join(x for x in [per.get("firstName"), per.get("surname")] if x)
                if nm:
                    pis.append(nm)
        # lead org (top-level name on the organisation resource)
        org = None
        for l in links:
            if l.get("rel") == "LEAD_ORG":
                od = gtr_get(l.get("href"))
                org = od.get("name")
                break
        # GBP->USD approx for aggregate (documented). Use 1.27.
        amount_usd = round(amount * 1.27) if currency == "GBP" else amount
        fy = None
        if isinstance(start, (int, float)) and start > 0:
            fy = time.gmtime(start / 1000).tm_year
        elif start:
            mm = re.search(r"(\d{4})", str(start)); fy = int(mm.group(1)) if mm else None
        records.append({
            "project_title": r.get("title"),
            "pi_names": pis,
            "institution": org,
            "funder": r.get("leadFunder"),
            "award_id": pid,
            "fiscal_year": fy,
            "fiscal_year_range": str(fy) if fy else None,
            "n_fiscal_years": 1,
            "amount_usd": amount_usd,
            "amount_original": (f"GBP {amount}" if currency == "GBP" and amount else None),
            "abstract": (r.get("abstractText") or "").strip() or None,
            "url": f"https://gtr.ukri.org/projects?ref={r.get('identifiers',{}).get('identifier',[{}])[0].get('value','')}",
            "source": "UKRI Gateway to Research",
            "country": "UK",
            "uncertain_topic": (not s and not m),
        })
    return records

def main():
    nih, dropped, n_appl = load_nih()
    gtr = load_gtr()
    collisions = {}
    cpath = os.path.join(RAW, "_collisions.json")
    if os.path.exists(cpath):
        collisions = json.load(open(cpath))

    records = nih + gtr
    records.sort(key=lambda x: (x.get("fiscal_year") or 9999, -(x.get("amount_usd") or 0)))

    # counts
    by_funder = {}
    by_inst = {}
    by_year = {}
    total = 0
    for r in records:
        by_funder[r["funder"]] = by_funder.get(r["funder"], 0) + 1
        inst = r.get("institution") or "(unknown)"
        by_inst[inst] = by_inst.get(inst, 0) + 1
        fy = str(r.get("fiscal_year") or "unknown")
        by_year[fy] = by_year.get(fy, 0) + 1
        total += r.get("amount_usd") or 0

    top_inst = dict(sorted(by_inst.items(), key=lambda kv: -kv[1])[:15])
    by_funder = dict(sorted(by_funder.items(), key=lambda kv: -kv[1]))
    by_year = dict(sorted(by_year.items(), key=lambda kv: kv[0]))

    doc = {
        "generated_utc": "PLACEHOLDER",
        "source_notes": (
            "Public research-grant metadata for DMT (N,N-dimethyltryptamine) and ayahuasca "
            "science, aggregated for dmtatlas.com. Sources: NIH RePORTER API v2 (US federal, "
            "POST full-text search over projecttitle/abstracttext/terms), UKRI Gateway to "
            "Research (UK). Queries used at NIH: 'dimethyltryptamine', 'ayahuasca', and "
            "targeted AND-combos 'DMT psychedelic', 'DMT hallucinogen', 'DMT tryptamine', "
            "plus 'banisteriopsis', 'harmaline harmine'. The bare 'DMT'/'N,N-DMT'/'5-MeO-DMT' "
            "acronym searches were DELIBERATELY NOT used alone: they collide catastrophically "
            "at NIH (N,N-DMT matched 218,947 records; 5-MeO-DMT matched 461,543 -- diffusion "
            "MRI tensor, dendritic, etc.) and were auto-aborted by a 1,500-hit collision cap. "
            "DEDUP/AGGREGATION: NIH awards recur yearly (one appl_id per fiscal-year action); "
            "rows were deduped by appl_id, then COLLAPSED to the core project (core_project_num) "
            "with award_amount SUMMED across all fiscal years = total lifetime funding. "
            "amount_usd therefore reflects cumulative award per project; fiscal_year is the "
            "FIRST funded year and fiscal_year_range spans the project. total_funding_usd is the "
            "sum over collapsed projects (no year double-counted). FILTER: each project must carry "
            "a genuine dimethyltryptamine/ayahuasca/psychedelic/hallucinogen signal in "
            "title+abstract+terms; projects with only a moderate psychedelic-adjacent signal or "
            "where an ayahuasca alkaloid (harmine/harmaline) appears only as background to "
            "non-psychedelic research (diabetes, essential-tremor modeling) are tagged "
            "uncertain_topic=true. GtR amounts converted GBP->USD at 1.27 for the aggregate; "
            "amount_original preserves the GBP figure. NSF Awards API returned zero matches for "
            "'ayahuasca'/'dimethyltryptamine' and is omitted."
        ),
        "counts": {
            "total_grants": len(records),
            "nih_grants": len(nih),
            "ukri_grants": len(gtr),
            "uncertain_topic_flagged": sum(1 for r in records if r.get("uncertain_topic")),
            "by_funder": by_funder,
            "by_institution_top15": top_inst,
            "by_fiscal_year": by_year,
            "nih_unique_appl_ids_before_collapse": n_appl,
            "nih_projects_dropped_no_signal": dropped,
            "acronym_collisions_aborted": collisions,
        },
        "total_funding_usd": total,
        "records": records,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print(f"WROTE {OUT}")
    print(f"records={len(records)} nih={len(nih)} gtr={len(gtr)} total_usd=${total:,}")
    print(f"nih unique appl_ids={n_appl}  dropped_no_signal={dropped}  uncertain={doc['counts']['uncertain_topic_flagged']}")
    print("by_funder:", by_funder)
    print("earliest year:", min((r.get('fiscal_year') for r in records if r.get('fiscal_year')), default=None))
    top5 = sorted(records, key=lambda x: -(x.get('amount_usd') or 0))[:8]
    print("TOP FUNDED:")
    for r in top5:
        print(f"  ${r['amount_usd']:>12,} | {r['award_id']} | {str(r['project_title'])[:55]} | {r['institution']}")

if __name__ == "__main__":
    main()
