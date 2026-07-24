#!/usr/bin/env python3
"""Normalize + filter + dedup the raw Google-Patents harvest into patents.json.
Bibliographic level only: title / snippet-abstract / assignee / dates / family.
No synthesis or manufacturing procedure is captured."""
import json, os, re, datetime, html
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "data", "research", "raw", "patents_raw.json")
OUT = os.path.join(BASE, "data", "research", "patents.json")

def clean(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)          # strip <b> highlight tags
    s = html.unescape(s)
    s = s.replace("–", "-").replace("‐", "-")
    return re.sub(r"\s+", " ", s).strip()

def jurisdiction(pub):
    m = re.match(r"^([A-Z]{2})", pub or "")
    return m.group(1) if m else "?"

def kind_status(pub):
    """Infer granted vs application from trailing kind code."""
    m = re.search(r"([A-Z]\d?)$", pub or "")
    kc = m.group(1) if m else ""
    if kc in ("B1", "B2", "C1", "C2", "E", "Y", "S"):
        return "granted"
    if kc in ("A1", "A2", "A3", "A9", "A", "A8"):
        return "application/publication"
    return "unknown"

def fam_status(pat, juris):
    try:
        cs = pat["family_metadata"]["aggregated"]["country_status"]
        for c in cs:
            if c.get("country_code") == juris:
                st = c.get("best_patent_stage", {}).get("state")
                if st:
                    return st
    except Exception:
        pass
    return None

# molecule tagging ---------------------------------------------------------
FIVE = ("5-methoxy", "5-meo", "5 meo", "mebufoten", "5‐methoxy", "o-methyl-bufotenin")
def molecule_tag(text, hint):
    t = text.lower()
    if any(k in t for k in FIVE):
        return "5-MeO-DMT"
    if "ayahuasca" in t or "banisteriopsis" in t or "harmine" in t and "dimethyltryptamine" in t:
        return "ayahuasca"
    if "dimethyltryptamine" in t or "n,n-dmt" in t or "n, n-dmt" in t:
        return "N,N-DMT"
    if hint in ("5-MeO-DMT", "ayahuasca"):
        return hint
    if "tryptamine" in t:
        return "tryptamine-general"
    return "other"

# relevance filtering ------------------------------------------------------
DROP_MARKERS = ("derjaguin", "muller-toporov", "muller–toporov", "contact mechanics",
                "dot matrix", "dot-matrix", "dimethyl terephthalate", "dimethyl tin")
COMPOUND_MARKERS = ("dimethyltryptamine", "tryptamine", "ayahuasca", "5-meo", "5-methoxy",
                    "mebufoten", "psilocyb", "n,n-dmt", " dmt ", "-dmt", "dmt.", "dmt,",
                    "banisteriopsis", "harmine", "bufotenin")
THERAPEUTIC = ("therap", "treat", "disorder", "depress", "anxiet", "ptsd", "addict",
               "pharmaceutic", "medic", "dose", "dosing", "administ", "patient",
               "psychedelic", "mental", "neuro", "formulation", "for use", "psychiat",
               "hallucinog", "serotonin", "5-ht", "receptor", "substance use", "clinical",
               "microdos", "psycho", "compound for", "composition")

def is_droppable(text):
    t = text.lower()
    if any(m in t for m in DROP_MARKERS):
        return True
    if not any(m in t for m in COMPOUND_MARKERS):
        return True
    return False

def is_uncertain(text):
    return not any(k in text.lower() for k in THERAPEUTIC)

def decade(y):
    return f"{(y//10)*10}s" if y else "unknown"

def year_of(d):
    if d and re.match(r"\d{4}", d):
        return int(d[:4])
    return None

def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    records = []
    for pid, pat in raw.items():
        pub = pat.get("publication_number") or ""
        title = clean(pat.get("title"))
        snippet = clean(pat.get("snippet"))
        text = f"{title} {snippet}"
        if is_droppable(text):
            continue
        juris = jurisdiction(pub)
        inv = pat.get("inventor")
        inventors = [inv.strip()] if inv and inv.strip() else []
        grant = pat.get("grant_date") or ""
        kstat = kind_status(pub)
        if kstat != "granted":
            grant = ""  # don't assert a grant date for applications
        fstat = fam_status(pat, juris)
        status = fstat if fstat else kstat
        rec = {
            "patent_number": pub,
            "title": title,
            "assignee": clean(pat.get("assignee")) or None,
            "inventors": inventors,
            "filing_date": pat.get("filing_date") or None,
            "publication_date": pat.get("publication_date") or None,
            "grant_date": grant or None,
            "priority_date": pat.get("priority_date") or None,
            "jurisdiction": juris,
            "status": status,
            "molecule_tag": molecule_tag(text, pat.get("_query_hint", "auto")),
            "abstract": snippet or None,
            "claims_summary": None,  # full-text claims not fetched (bibliographic only)
            "url": f"https://patents.google.com/patent/{pub}/en" if pub else None,
            "uncertain_topic": is_uncertain(text),
            "_priority": pat.get("priority_date") or "",
        }
        records.append(rec)

    # sort by filing_date asc, fallback priority then publication
    def sortkey(r):
        return (r["filing_date"] or r["priority_date"] or r["publication_date"] or "9999")
    records.sort(key=sortkey)

    # counts ----------------------------------------------------------------
    by_decade = Counter()
    by_assignee = Counter()
    by_molecule = Counter()
    fam = set()
    for r in records:
        y = year_of(r["filing_date"] or r["priority_date"] or r["publication_date"])
        by_decade[decade(y) if y else "unknown"] += 1
        if r["assignee"]:
            by_assignee[r["assignee"]] += 1
        by_molecule[r["molecule_tag"]] += 1
        famkey = (re.sub(r"[^a-z0-9]", "", r["title"].lower())[:60], r["priority_date"] or r["filing_date"])
        fam.add(famkey)

    counts = {
        "total_records": len(records),
        "estimated_unique_families": len(fam),
        "uncertain_topic": sum(1 for r in records if r["uncertain_topic"]),
        "by_decade": dict(sorted(by_decade.items())),
        "by_assignee_top20": dict(by_assignee.most_common(20)),
        "by_molecule_tag": dict(by_molecule.most_common()),
        "by_jurisdiction": dict(Counter(r["jurisdiction"] for r in records).most_common()),
    }

    for r in records:
        r.pop("_priority", None)

    out = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_notes": (
            "Source: Google Patents public XHR (patents.google.com/xhr/query) - the only "
            "free source reachable without a key. PatentsView legacy API (api.patentsview.org) "
            "is RETIRED (301-redirects to the USPTO ODP portal HTML); the new "
            "search.patentsview.org API requires an API key (not available) - both unusable. "
            "The Lens / EPO OPS not attempted (require keys). Google Patents caps retrievable "
            "results at ~1000 per query (10 pages x 100), so coverage combines title-scoped, "
            "abstract-scoped-with-therapeutic-terms, claims-scoped, 5-MeO / ayahuasca, and "
            "modern-assignee queries, then deduplicates by publication number. Abstracts are "
            "SNIPPET-LEVEL text returned by the search API (not the full published abstract); "
            "claims_summary left null - full claim text was intentionally not fetched to keep "
            "this a bibliographic catalog with no synthesis/manufacturing detail. Inventor field "
            "is the lead inventor only (search API returns one). Records are publication-level "
            "and deduped by patent_number; cross-jurisdiction family members are retained as "
            "separate rows (see estimated_unique_families for the collapsed count)."
        ),
        "counts": counts,
        "records": records,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {len(records)} records -> {OUT}")
    print("molecule:", dict(by_molecule))
    print("decades:", dict(sorted(by_decade.items())))
    print("top assignees:", by_assignee.most_common(12))

if __name__ == "__main__":
    main()
