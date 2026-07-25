#!/usr/bin/env python3
"""Normalize + dedup + filter DMT/ayahuasca theses from raw harvests -> theses.json."""
import json, re, os
from collections import Counter, defaultdict

BASE_DIR = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas"
RAW_DIR = os.path.join(BASE_DIR, "data/research/raw")
OUT = os.path.join(BASE_DIR, "data/research/theses.json")

def load(name):
    p = os.path.join(RAW_DIR, name)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def strip_html(s):
    if not s: return s
    # 1) decode entities first (OpenAlex encodes markup as &lt;i&gt; or mangled &gt;i&lt;)
    s = (s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
          .replace('&nbsp;', ' ').replace('&quot;', '"').replace('&#39;', "'"))
    # 2) strip mangled reversed tags  >i<  >/i<
    s = re.sub(r'>\s*/?\s*(i|b|em|sub|sup|strong|it|sc)\s*<', ' ', s)
    # 3) strip normal tags  <i> </i>
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def reconstruct_abstract(inv):
    if not inv: return None
    pos = []
    for word, idxs in inv.items():
        for i in idxs: pos.append((i, word))
    if not pos: return None
    pos.sort()
    return " ".join(w for _, w in pos)

# ---- topic relevance -------------------------------------------------
TOPIC_POS = ["dimethyltryptamine", "n,n-dmt", "n, n-dmt", "ayahuasca", "yage", "yagé",
             "yaje", "5-meo-dmt", "5-methoxy", "banisteriopsis", "harmine", "harmaline",
             "harmala", "psychotria viridis", "hoasca", "daime", "santo daime", "uniao do vegetal",
             "psychedelic", "hallucinogen", "psilocyb", "entheogen", "bufotenin",
             "tryptamine", "dmt", "serotonergic psychedelic"]
# DMT acronym collisions to drop when NO psychedelic term present
DMT_COLLISION = ["dialectical", "distributed multithreading", "diffusion",
                 "dry matter", "disease-modifying", "docetaxel", "music therapy",
                 "material", "concrete", "polymer", "dimethyl terephthalate",
                 "data management", "digital media", "dead man", "dmt algorithm",
                 "trans-splicing", "dynamic mechanical", "adaptive optics"]

STRONG_RE = re.compile(
    r"\b(dimethyltryptamine|ayahuasca|yagé|yajé|banisteriopsis|harmine|"
    r"harmaline|harmala|psychotria viridis|santo daime|hoasca|uni[aã]o do vegetal|"
    r"entheogen\w*|psychedelic\w*|hallucinogen\w*|psilocyb\w*|bufoten\w*|"
    r"5-methoxy-n|5-?meo-?dmt)\b", re.I)
# unaccented yage/yaje are collision-prone (OCR 'wage', split 'voyage') -> need context
YAGE_UNACCENTED = re.compile(r"\byage\b|\byaje\b", re.I)
YAGE_CONTEXT = ["ayahuasca", "banisteriopsis", "caapi", "dmt", "dimethyltryptamine",
                "amazon", "shaman", "vine", "psychoact", "hallucino", "entheog",
                "psychedelic", "indigenous", "curandero", "vegetalismo", "cosmolog"]

def is_relevant(text):
    """Return (relevant, uncertain). Word-boundary matching avoids 'voyage'->'yage' etc."""
    t = (text or "").lower()
    if STRONG_RE.search(t):
        return True, False
    if YAGE_UNACCENTED.search(t):
        if any(k in t for k in YAGE_CONTEXT):
            return True, False
        return False, False  # bare 'yage' with no psychedelic context = typo, drop
    # only 'dmt' acronym present
    if re.search(r'\bdmt\b', t):
        if any(c in t for c in DMT_COLLISION):
            return False, False
        # dmt with tryptamine/serotonin context -> relevant but flag uncertain if thin
        if "tryptamine" in t or "seroton" in t or "psychoactive" in t:
            return True, False
        return True, True  # bare DMT, ambiguous
    if "tryptamine" in t and ("psychoact" in t or "seroton" in t or "hallucino" in t):
        return True, True
    return False, False

# ---- degree classification -------------------------------------------
def classify_degree(text, oa_type):
    t = (text or "").lower()
    if re.search(r'\b(m\.?sc|master of science|msci)\b', t): return "MSc"
    if re.search(r'master of arts|\bm\.?a\.? thesis|\bm\.a\.\b', t): return "MA"
    if re.search(r"master'?s (thesis|degree|dissertation)|degree of master|magister|mestrado|m\.?phil", t): return "MSc"
    if re.search(r'ph\.?\s?d|doctor of philosophy|doctoral|degree of doctor|doutorado|dphil', t): return "PhD"
    if oa_type == "dissertation":
        return "PhD"  # OpenAlex 'dissertation' skews doctoral
    return "other"

# ---- discipline classification ---------------------------------------
DISC_RULES = [
    ("pharmacology", ["pharmacolog", "pharmaceut", "pharmacokinet", "drug metabolism",
                       "medicinal chemistry", "toxicolog", "receptor binding"]),
    ("neuroscience", ["neuroscience", "neural", "brain", "eeg", "neuroimag", "fmri",
                      "electrophysiolog", "neuropharmacolog", "cortic", "connectivity",
                      "neuroplasticity", "5-ht2a", "serotonin receptor"]),
    ("chemistry", ["synthesis", "chemistr", "analytic", "chromatograph", "mass spectrom",
                   "alkaloid", "phytochemi", "biosynthesis"]),
    ("psychology", ["psycholog", "psychiatr", "mental health", "depression", "ptsd",
                    "well-being", "wellbeing", "consciousness", "psychotherap", "cognit",
                    "personality", "mystical experience", "phenomenolog"]),
    ("anthropology", ["anthropolog", "ethnograph", "shaman", "indigenous", "amazon",
                      "ritual", "cultural", "ethnobotan", "vegetalismo", "curandero"]),
    ("religious studies", ["religio", "spiritual", "theolog", "sacred", "mysticism",
                           "santo daime", "entheog", "ceremony", "pilgrimage"]),
    ("botany/ecology", ["botan", "plant", "ecolog", "taxonom", "species"]),
    ("medicine/public health", ["clinical trial", "therapeutic", "treatment", "addiction",
                                 "substance use", "public health", "epidemiolog", "harm reduction"]),
    ("law/policy", ["legal", "policy", "regulat", "prohibition", "drug law", "criminal"]),
]

def classify_discipline(text, oa_topics):
    t = (text or "").lower()
    # first try OpenAlex topic field names
    fields = " ".join(oa_topics).lower()
    combined = t + " " + fields
    scores = {}
    for disc, kws in DISC_RULES:
        s = sum(combined.count(k) for k in kws)
        if s: scores[disc] = s
    if scores:
        return max(scores, key=scores.get)
    return "other/unspecified"

def norm_title(s):
    s = (s or "").lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# ---- thesis-likeness gate (word-boundary; avoids 'synthesis' matching 'thesis') ----
THESIS_RE = re.compile(
    r"\b(thesis|theses|dissertation|dissertations|doctoral|dphil|ph\.?\s?d|"
    r"mestrado|doutorado|magister|inaugural-?dissertation|"
    r"partial fulfil?ment|degree of doctor|degree of master|master'?s thesis)\b"
    r"|tesis doctoral|teses e disserta", re.I)

def is_thesis(rec):
    """True if the record is genuinely a thesis/dissertation, not a mis-typed article."""
    if rec.get("_oa_type") == "dissertation":
        return True
    if rec.get("_doctype") in ("thesis", "dissertation"):
        return True
    blob = " ".join([rec.get("title") or "", rec.get("institution") or "", rec.get("abstract") or ""])
    return bool(THESIS_RE.search(blob))

# ---- normalize OpenAlex ----------------------------------------------
def norm_openalex(w):
    title = strip_html(w.get("title") or w.get("display_name") or "") or ""
    authors = [a.get("author", {}).get("display_name") for a in w.get("authorships", []) if a.get("author")]
    author = ", ".join([a for a in authors if a]) or None
    year = w.get("publication_year")
    # institution: authorship institution, else primary_location source
    inst = None
    for a in w.get("authorships", []):
        insts = a.get("institutions") or []
        if insts:
            inst = insts[0].get("display_name"); break
    if not inst:
        pl = w.get("primary_location") or {}
        src = pl.get("source") or {}
        inst = src.get("display_name")
    abstract = strip_html(reconstruct_abstract(w.get("abstract_inverted_index")))
    doi = w.get("doi")
    url = doi or (w.get("primary_location") or {}).get("landing_page_url") or w.get("id")
    oa_type = (w.get("type") or "").lower()
    topics = []
    for tp in (w.get("topics") or []):
        topics.append(tp.get("display_name") or "")
        f = tp.get("field") or {}
        topics.append(f.get("display_name") or "")
        sf = tp.get("subfield") or {}
        topics.append(sf.get("display_name") or "")
    for c in (w.get("concepts") or [])[:5]:
        topics.append(c.get("display_name") or "")
    blob = " ".join([title, abstract or "", " ".join(topics), inst or ""])
    return {
        "title": title.strip(),
        "author": author,
        "year": year,
        "institution": inst,
        "degree": classify_degree(blob, oa_type),
        "discipline": classify_discipline(blob, topics),
        "abstract": abstract,
        "doi_or_url": (("https://doi.org/" + doi.replace("https://doi.org/", "")) if doi and not doi.startswith("http") else url),
        "source_db": "openalex",
        "_doi_key": (doi or "").lower().replace("https://doi.org/", "").strip(),
        "_blob": blob,
        "_oa_type": oa_type,
    }

def norm_core(h):
    title = strip_html(h.get("title") or "") or ""
    authors = h.get("authors") or []
    names = []
    for a in authors:
        if isinstance(a, dict): names.append(a.get("name"))
        elif isinstance(a, str): names.append(a)
    author = ", ".join([n for n in names if n]) or None
    year = h.get("yearPublished") or h.get("publishedDate")
    if isinstance(year, str):
        m = re.search(r'(\d{4})', year); year = int(m.group(1)) if m else None
    inst = None
    pubs = h.get("publisher")
    if isinstance(pubs, str): inst = pubs
    doi = h.get("doi")
    url = h.get("downloadUrl") or h.get("sourceFulltextUrls") or None
    if isinstance(url, list): url = url[0] if url else None
    if not url:
        url = (doi if doi else None) or h.get("id")
    abstract = h.get("abstract")
    doctype = (h.get("documentType") or "") + " " + (str(h.get("fieldOfStudy") or ""))
    blob = " ".join([title, abstract or "", doctype, inst or ""])
    return {
        "title": title.strip(),
        "author": author,
        "year": year,
        "institution": inst,
        "degree": classify_degree(blob, ""),
        "discipline": classify_discipline(blob, [str(h.get("fieldOfStudy") or "")]),
        "abstract": abstract,
        "doi_or_url": (("https://doi.org/" + doi) if doi and not str(doi).startswith("http") else (url or "")),
        "source_db": "core",
        "_doi_key": (str(doi or "")).lower().replace("https://doi.org/", "").strip(),
        "_blob": blob,
        "_oa_type": "",
        "_doctype": (h.get("documentType") or "").lower(),
    }

def main():
    oa_raw = load("theses_openalex_raw.json")
    core_raw = load("theses_core_raw.json")
    try:
        source_notes = load("theses_source_notes.json")
    except Exception:
        source_notes = []

    recs = []
    NON_THESIS_TYPES = {"dataset", "peer-review", "grant", "paratext", "supplementary-materials"}
    for w in oa_raw:
        if (w.get("type") or "").lower() in NON_THESIS_TYPES:
            continue  # dataset deposits etc. are not theses
        recs.append(norm_openalex(w))
    for h in core_raw:
        # CORE returns many non-thesis works; keep only thesis-like
        dt = (h.get("documentType") or "").lower()
        title = (h.get("title") or "").lower()
        if not (dt in ("thesis", "dissertation") or "thesis" in title or "dissertation" in title):
            continue
        recs.append(norm_core(h))

    # filter: must be a genuine thesis AND topically relevant
    filtered = []
    dropped = 0
    dropped_not_thesis = 0
    for r in recs:
        if not r["title"]:
            dropped += 1; continue
        if not is_thesis(r):
            dropped_not_thesis += 1; continue
        rel, unc = is_relevant(r["_blob"])
        if not rel:
            dropped += 1; continue
        r["uncertain_topic"] = unc
        filtered.append(r)

    # dedup: DOI key first, then normalized title
    seen_doi = {}
    seen_title = {}
    unique = []
    for r in sorted(filtered, key=lambda x: (0 if x["source_db"] == "openalex" else 1)):
        dk = r["_doi_key"]
        tk = norm_title(r["title"])
        if dk and dk in seen_doi:
            # merge source_db
            ex = seen_doi[dk]
            if r["source_db"] not in ex.get("_srcs", []):
                ex.setdefault("_srcs", [ex["source_db"]]).append(r["source_db"])
            continue
        if tk and tk in seen_title:
            ex = seen_title[tk]
            if r["source_db"] not in ex.get("_srcs", []):
                ex.setdefault("_srcs", [ex["source_db"]]).append(r["source_db"])
            continue
        r["_srcs"] = [r["source_db"]]
        unique.append(r)
        if dk: seen_doi[dk] = r
        if tk: seen_title[tk] = r

    # finalize records
    final = []
    for r in unique:
        rec = {
            "title": r["title"],
            "author": r["author"],
            "year": r["year"],
            "institution": r["institution"],
            "degree": r["degree"],
            "discipline": r["discipline"],
            "abstract": r["abstract"],
            "doi_or_url": r["doi_or_url"],
            "source_db": "+".join(sorted(set(r.get("_srcs", [r["source_db"]])))),
        }
        if r.get("uncertain_topic"):
            rec["uncertain_topic"] = True
        final.append(rec)

    final.sort(key=lambda x: (x["year"] is None, x["year"] or 0, x["title"]))

    # counts
    by_decade = Counter()
    by_disc = Counter()
    by_source = Counter()
    by_degree = Counter()
    for r in final:
        y = r["year"]
        dec = ("%ds" % (y // 10 * 10)) if y else "unknown"
        by_decade[dec] += 1
        by_disc[r["discipline"]] += 1
        by_source[r["source_db"]] += 1
        by_degree[r["degree"]] += 1

    def ordered(counter, keyfn=None):
        return dict(sorted(counter.items(), key=keyfn or (lambda kv: (-kv[1], kv[0]))))

    method_note = ("METHOD: OpenAlex is authoritative source (CORE down w/ 504 gateway timeout at harvest time; "
                   "BASE served an anti-bot HTML shell, no structured records). OpenAlex has no 'thesis' work-type "
                   "and stores no degree level, so degree (PhD/MSc/MA) and discipline are HEURISTIC inferences from "
                   "title/abstract/venue/topic text; 'dissertation'-typed records with no 'master' cue default to PhD "
                   "(hence PhD-heavy). Thesis-likeness gated by work-type=='dissertation' or word-boundary thesis/"
                   "dissertation/doctoral markers (drops ~130 chemistry 'synthesis' journal articles). Abstracts "
                   "reconstructed from OpenAlex inverted index.")
    all_notes = (source_notes if isinstance(source_notes, list) else [str(source_notes)]) + [method_note]
    out = {
        "generated_utc": "PLACEHOLDER",
        "source_notes": " | ".join(all_notes),
        "counts": {
            "total": len(final),
            "by_decade": dict(sorted(by_decade.items())),
            "by_discipline": ordered(by_disc),
            "by_degree": ordered(by_degree),
            "by_source": ordered(by_source),
            "uncertain_topic_flagged": sum(1 for r in final if r.get("uncertain_topic")),
            "raw_candidates_before_filter": len(recs),
            "dropped_not_a_thesis": dropped_not_thesis,
            "dropped_irrelevant_or_untitled": dropped,
        },
        "records": final,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("WROTE %d unique theses -> %s" % (len(final), OUT))
    print("by discipline:", dict(by_disc))
    print("by decade:", dict(sorted(by_decade.items())))
    print("by degree:", dict(by_degree))
    print("earliest:", final[0]["year"] if final else None, "-", final[0]["title"][:70] if final else "")

if __name__ == "__main__":
    main()
