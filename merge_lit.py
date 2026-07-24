#!/usr/bin/env python3
"""Merge, deduplicate, filter DMT literature from raw source dumps into literature.json."""
import json, re, unicodedata, sys

OUTDIR = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas/data/research"
RAWDIR = OUTDIR + "/raw"

def load(name):
    try:
        with open(RAWDIR + "/" + name, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("  (missing %s)" % name, file=sys.stderr)
        return []

# ---- topic filtering ----
# On-topic if any of these appear in title/abstract/venue.
TOPIC_TERMS = [
    "dimethyltryptamine", "dimethyl-tryptamine", "n,n-dmt", "nn-dmt", "n-n-dmt",
    "ayahuasca", "yage", "yaje", "yag\u00e9", "hoasca", "caapi", "banisteriopsis",
    "psychotria viridis", "chacruna", "tryptamine", "5-meo-dmt", "5-methoxy",
    "bufotenin", "psychedelic", "psychodysleptic", "hallucinogen", "psychotomimetic",
    "psychotropic", "entheogen", "5-ht2a", "5-ht2", "serotonin 2a", "serotonergic",
    "harmine", "harmaline", "harmala", "tetrahydroharmine", "beta-carboline",
    "\u03b2-carboline", "monoamine oxidase inhibit", "maoi", "indolealkylamine",
    "indole alkylamine", "indoleamine", "sigma-1", "sigma 1 receptor",
    "trace amine", "dmt", "n, n-dimethyltryptamine",
]
# Strong off-topic signals (materials science / other DMT expansions).
OFFTOPIC_STRONG = [
    "derjaguin", "dmt contact model", "dmt model", "contact mechanics",
    "adhesion model", "maugis", "dugdale", "jkr", "asperity",
    "discrete multitone", "dial-up", "adsl", "vdsl",
    "dermatophyte", "dermatophytosis",
    "de martini", "dimethyl terephthalate", "dimethyltin", "dimethyltellur",
    "3,4-methylenedioxymethamphetamine",  # avoid MDMA-only collision unless psychedelic term present
]
DMT_ACRONYM = re.compile(r"\bDMT\b")

def norm_txt(s):
    return (s or "").lower()

def is_on_topic(rec):
    blob = " ".join([norm_txt(rec.get("title")), norm_txt(rec.get("abstract")),
                     norm_txt(rec.get("venue"))])
    # explicit topic term hit
    hit_terms = [t for t in TOPIC_TERMS if t != "dmt" and t in blob]
    strong_topic = bool(hit_terms)
    # bare "DMT" acronym in title/abstract
    bare_dmt = bool(DMT_ACRONYM.search((rec.get("title") or "") + " " + (rec.get("abstract") or "")))
    off = any(o in blob for o in OFFTOPIC_STRONG)

    if strong_topic:
        # even with a strong topic term, kill obvious materials-science hybrids
        if off and not any(t in blob for t in ("dimethyltryptamine", "ayahuasca", "psychedelic",
                                               "hallucinogen", "5-meo", "harm", "tryptamine",
                                               "banisteriopsis", "entheogen")):
            return (False, False)
        return (True, False)
    if bare_dmt and not off:
        # keep but flag uncertain (bare acronym, no explicit topic term)
        return (True, True)
    if off:
        return (False, False)
    # no topic evidence at all, no abstract to judge -> uncertain keep if title has DMT-ish
    return (False, False)

# ---- dedup keys ----
def norm_title(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"<[^>]+>", " ", t)          # strip markup
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def richness(rec):
    score = 0
    if rec.get("abstract"): score += 3 + min(len(rec["abstract"]) // 500, 5)
    if rec.get("doi"): score += 2
    if rec.get("pmid"): score += 2
    if rec.get("authors"): score += min(len(rec["authors"]), 5)
    if rec.get("year"): score += 1
    if rec.get("venue"): score += 1
    if rec.get("cited_by_count") is not None: score += 1
    return score

SRC_PRIORITY = {"pubmed": 3, "europepmc": 2, "openalex": 1}

def merge_two(a, b):
    """Merge b into a, keeping richest fields. Returns merged dict."""
    keep = a if (richness(a), SRC_PRIORITY.get(a["source_db"], 0)) >= (richness(b), SRC_PRIORITY.get(b["source_db"], 0)) else b
    other = b if keep is a else a
    m = dict(keep)
    for field in ("doi", "pmid", "abstract", "venue", "year", "type", "url"):
        if not m.get(field) and other.get(field):
            m[field] = other[field]
    # longer abstract wins
    if other.get("abstract") and len(other["abstract"]) > len(m.get("abstract") or ""):
        m["abstract"] = other["abstract"]
    # more authors wins
    if len(other.get("authors") or []) > len(m.get("authors") or []):
        m["authors"] = other["authors"]
    # max citation count
    cvals = [x.get("cited_by_count") for x in (a, b) if x.get("cited_by_count") is not None]
    if cvals:
        m["cited_by_count"] = max(cvals)
    # provenance
    srcs = set()
    for x in (a, b):
        s = x.get("source_dbs") or [x["source_db"]]
        srcs.update(s)
    m["source_dbs"] = sorted(srcs)
    m["source_db"] = keep["source_db"]
    if a.get("uncertain_topic") and b.get("uncertain_topic"):
        m["uncertain_topic"] = True
    elif "uncertain_topic" in m and not (a.get("uncertain_topic") and b.get("uncertain_topic")):
        m["uncertain_topic"] = False
    return m

def main():
    all_recs = []
    counts_raw = {}
    for fn in ("pubmed.json", "europepmc.json", "openalex.json"):
        recs = load(fn)
        counts_raw[fn.split(".")[0]] = len(recs)
        all_recs.extend(recs)
    print("raw totals:", counts_raw, "sum", len(all_recs))

    # filter
    kept = []
    dropped = 0
    for r in all_recs:
        on, uncertain = is_on_topic(r)
        if not on:
            dropped += 1
            continue
        if uncertain:
            r["uncertain_topic"] = True
        kept.append(r)
    print("after topic filter: kept %d, dropped %d" % (len(kept), dropped))

    # dedup by DOI then normalized title
    by_doi = {}
    no_doi = []
    for r in kept:
        doi = (r.get("doi") or "").strip().lower().rstrip(".")
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
        if doi:
            r["_doi_key"] = doi
            if doi in by_doi:
                by_doi[doi] = merge_two(by_doi[doi], r)
            else:
                by_doi[doi] = r
        else:
            no_doi.append(r)

    merged = list(by_doi.values())

    # title dedup: fold no_doi into existing (and each other) by normalized title
    by_title = {}
    for r in merged:
        nt = norm_title(r.get("title"))
        if nt:
            by_title.setdefault(nt, []).append(r)

    final = list(merged)
    title_index = {}
    for r in final:
        nt = norm_title(r.get("title"))
        if nt:
            title_index[nt] = r

    for r in no_doi:
        nt = norm_title(r.get("title"))
        if nt and nt in title_index:
            existing = title_index[nt]
            m = merge_two(existing, r)
            # replace in final
            idx = final.index(existing)
            final[idx] = m
            title_index[nt] = m
        else:
            final.append(r)
            if nt:
                title_index[nt] = r

    # second pass: collapse any remaining exact-normalized-title dupes among final
    collapsed = {}
    order = []
    for r in final:
        nt = norm_title(r.get("title"))
        key = nt if nt else ("__notitle__%d" % id(r))
        if key in collapsed:
            collapsed[key] = merge_two(collapsed[key], r)
        else:
            collapsed[key] = r
            order.append(key)
    final = [collapsed[k] for k in order]

    # clean helper keys
    for r in final:
        r.pop("_doi_key", None)
        r.setdefault("source_dbs", [r["source_db"]])
        if "uncertain_topic" not in r:
            r["uncertain_topic"] = False

    # sort by year asc (None -> end)
    final.sort(key=lambda r: (r.get("year") is None, r.get("year") or 9999, norm_title(r.get("title"))))

    # counts
    by_decade = {}
    by_source = {"pubmed": 0, "europepmc": 0, "openalex": 0}
    uncertain_n = 0
    for r in final:
        y = r.get("year")
        if y:
            dec = "%d0s" % (y // 10)
        else:
            dec = "unknown"
        by_decade[dec] = by_decade.get(dec, 0) + 1
        for s in r.get("source_dbs", []):
            if s in by_source:
                by_source[s] += 1
        if r.get("uncertain_topic"):
            uncertain_n += 1

    by_decade_sorted = dict(sorted(by_decade.items(),
        key=lambda kv: (kv[0] == "unknown", kv[0])))

    out = {
        "generated_utc": "PLACEHOLDER",
        "query_notes": ("PubMed: (\"N,N-Dimethyltryptamine\"[MeSH] OR \"dimethyltryptamine\"[TIAB] "
            "OR \"N,N-DMT\"[TIAB] OR \"ayahuasca\"[TIAB]); Europe PMC: 'dimethyltryptamine OR ayahuasca'; "
            "OpenAlex: search='dimethyltryptamine'. Deduplicated by lowercased DOI then normalized title; "
            "richest record kept on merge. Topic filter keeps records mentioning dimethyltryptamine/ayahuasca/"
            "tryptamine/psychedelic/hallucinogen/5-HT2A/beta-carboline etc.; drops materials-science 'DMT' "
            "(Derjaguin/contact model), DSL, and other acronym collisions. Bare 'DMT' acronym w/o explicit "
            "topic term kept with uncertain_topic=true for review."),
        "counts": {
            "total_unique": len(final),
            "raw_by_source": counts_raw,
            "unique_by_source_membership": by_source,
            "by_decade": by_decade_sorted,
            "uncertain_topic": uncertain_n,
        },
        "records": final,
    }
    with open(OUTDIR + "/literature.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE %d unique records" % len(final))
    print("by decade:", by_decade_sorted)
    print("by source membership:", by_source)
    print("uncertain:", uncertain_n)
    # earliest 5
    dated = [r for r in final if r.get("year")]
    print("\nEarliest 5:")
    for r in dated[:5]:
        print("  %s  %s" % (r["year"], (r["title"] or "")[:100]))

if __name__ == "__main__":
    main()
