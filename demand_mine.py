#!/usr/bin/env python3
"""demand_mine.py — what people actually ask, mined from public community forums.

WHY THIS EXISTS
    Search Console cannot answer "what do people want that we don't have" for
    this site: the full 480-day history is 36 impressions / 6 queries, and all
    six are navigational. GSC only reports queries you already rank for. The
    AI-404 log was empty of real content demand too. So the demand signal has
    to come from where the questions are actually being asked.

HOW IT STAYS POLITE
    XenForo thread URLs carry the slugified thread title, and the forum
    publishes a gzipped sitemap. That means ~72,000 thread titles arrive in
    THREE http requests instead of 72,000 page fetches. We never fetch a
    thread body. Anything the source disallows in robots.txt is never touched.

WHAT IS DELIBERATELY EXCLUDED
    * Reddit — robots.txt is `Disallow: /` for every user-agent. Not touched.
    * Erowid — robots.txt sets `Content-Signal: ai-train=no, use=reference`
      and Disallow:/ for the training crawlers. We link to Erowid; we do not
      ingest it into a derived corpus. Respecting that is also the argument we
      make about our own AI-openness, so we do not get to break it.
    * Extraction / synthesis / sourcing / cultivation threads. BUILD.md's
      charter is explicit: "NOT a guide to obtaining, making, or taking any
      substance. No synthesis, no extraction, no dosing." A demand report that
      surfaced tek requests would be a content brief the site must not act on.
      These are COUNTED AND REPORTED, never silently dropped.

    python demand_mine.py            # fetch + analyse
    python demand_mine.py --offline  # reuse the cached sitemaps
"""
import os
import re
import sys
import gzip
import json
import time
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "data", "demand")
OUT_JSON = os.path.join(CACHE, "demand_report.json")
OUT_MD = os.path.join(ROOT, "DEMAND_REPORT.md")

UA = "Mozilla/5.0 (compatible; DMTAtlasResearch/1.0; +https://dmtatlas.com/)"

SOURCES = [
    # (name, sitemap index url, allowed-path marker)
    ("dmt-nexus", "https://forum.dmt-nexus.me/sitemap.xml", "/threads/"),
]

# ---------------------------------------------------------------------------
# Charter filter — territory the Atlas will not serve
# ---------------------------------------------------------------------------
# Bare keywords over-fire badly here. Measured on the first pass: `machine`
# (added for extraction rigs) excluded 16 of 16 "machine elves" threads — the
# site's single most iconic entity — and `source` killed 40 threads using it in
# the spiritual sense ("the source", "source of consciousness"). Terms that are
# only sometimes chemistry must carry their context with them.
EXCLUDE = re.compile(
    r"\b("
    r"tek|teks|extract|extraction|extracting|reextract|"
    r"synth|synthesis|synthesise|synthesize|reflux|reductive|amination|"
    r"naphtha|xylene|heptane|limonene|dcm|lye|naoh|hcl|sulfuric|acetone|"
    r"acid[- ]?base|stb|straight[- ]?to[- ]?base|fasa|fasi|fasw|mhrb|acrb|root ?bark|"
    r"yield|yields|crystall?i[sz]\w*|recrystall?i[sz]\w*|precipitat\w*|freebase|salting|"
    r"vendor|vendors|sourcing|for sale|price check|"
    r"grow(ing|log)?|cultivat\w*|germinat\w*|seedling|propagat\w*|"
    r"solvent|evaporat\w*|filtration|decarb|ph[- ]?meter|"
    r"cactus|cacti|trichocereus|pachanoi|peruvianus|bridgesii|acacia|mimosa|caapi|chacruna|"
    r"carbonate|bicarb|naphta|freeze[- ]?precip\w*|"
    r"bufo|alvarius|"
    r"san[- ]?pedro|syrian[- ]?rue|jurema|phalaris|desmanthus|anadenanthera|"
    r"dosage|dosing|potency|purity|"
    r"vaporiz\w*|vaporis\w*|gvg|e[- ]?mesh"
    r")\b"
    # context-bound: only chemistry/commerce when the neighbouring word says so
    r"|\b(where|how) to (buy|get|find|obtain|make|produce)\b"
    r"|\b(milk\w*|harvest\w*)\b.{0,20}\b(toad|bufo|venom)\b"
    r"|\b(toad|bufo|venom)\b.{0,20}\b(milk\w*|harvest\w*)\b"
    r"|\b(pull|pulls|pulled|pulling)\b.{0,14}\b(freebase|goo|jar|solvent|naphtha)\b"
    r"|\b(sodium|calcium|magnesium|ammonia)\b.{0,20}\b(carbonate|hydroxide|chloride|solution)\b"
    r"|\b\d+\s?(mg|g|grams?|ml)\b",
    re.I)

# Terms that must NEVER be excluded (core phenomenology) and terms that must
# ALWAYS be excluded (charter territory). Asserted by --selftest so a future
# tightening of EXCLUDE cannot silently delete the map's own subject matter.
MUST_KEEP = [
    "machine elves", "bad machine elf ate my hamster", "the source",
    "source of consciousness", "pure consciousness", "what did i meet",
    "the mantis showed me something", "is hyperspace real",
    "elves laughing at me", "clones of myself in the void",
    "how much of it do you remember", "space between thoughts",
]
MUST_DROP = [
    "my first a/b tek", "straight to base extraction", "naphtha pulls not working",
    "mhrb vendor recommendations", "how to buy dmt", "san pedro grow log",
    "yield from 100g root bark", "sodium carbonate solution question",
    "milking a bufo alvarius toad", "best vaporizer for dmt",
    "recrystallization help", "syrian rue dosage", "freeze precip question",
]

# Question shapes — a title that is genuinely someone asking something.
QUESTION = re.compile(
    r"(^|\b)(what|why|how|when|where|who|which|is|are|was|were|do|does|did|can|could|"
    r"should|would|has|have|had|anyone|anybody|am i|has anyone|does anyone|"
    r"help|advice|confused|explain|meaning|difference)\b", re.I)

# Demand themes we can actually serve, mapped to the section of the Atlas that
# would answer them. Order matters: first match wins.
THEMES = [
    ("entity-identification", r"\b(entity|entities|being|beings|elf|elves|machine elf|mantis|"
                              r"insectoid|reptilian|jester|clown|grey|greys|alien|goddess|"
                              r"deity|deities|god|guide|guardian|creature|figure|人)\b", "/entities/"),
    ("what-did-i-see",        r"\b(what (did|do) i (see|meet|encounter)|what was (that|it|this)|"
                              r"can anyone identify|identify|recogni[sz]e|has anyone (seen|met))\b", "/identify.html"),
    ("realms-places",         r"\b(realm|realms|hyperspace|waiting room|void|cathedral|palace|"
                              r"library|throne|dimension|dimensions|place|world|worlds|space)\b", "/realms/"),
    ("geometry-visuals",      r"\b(geometry|geometric|fractal|chrysanthemum|pattern|patterns|"
                              r"visual|visuals|colors|colours|lattice|kaleidoscop|carrier wave|"
                              r"language|glyph|symbols?)\b", "/geometry/"),
    ("integration-aftermath", r"\b(integrat|aftermath|afterwards|after (the|my)|shaken|scared|"
                              r"traumat|anxiety|depress|ptsd|process(ing)? (it|this)|"
                              r"months? later|years? later|changed me|cope|coping|healing)\b", "/grounding.html"),
    ("ontology-is-it-real",   r"\b(real|reality|actually there|objective|independent|"
                              r"just my brain|hallucination|imagination|believe|belief|proof|"
                              r"evidence|ontolog|simulation)\b", "/questions.html"),
    ("science-research",      r"\b(study|studies|research|paper|trial|clinical|neuroscien|"
                              r"eeg|fmri|pineal|endogenous|strassman|imperial|johns hopkins)\b", "/research/"),
    ("nde-death",             r"\b(death|dying|die|near-?death|nde|afterlife|deceased|"
                              r"passed away|the other side)\b", "/questions.html"),
    ("themes-meaning",        r"\b(meaning|message|purpose|lesson|download|telepath|"
                              r"communicat|why me|expecting me|cosmic joke|ego death|"
                              r"time|memory|remember|belief|beliefs|changed (me|my))\b", "/themes.html"),
    # The single biggest shape in the corpus, found by reading the bigrams:
    # "need help" 209, "please help" 129, "need advice" 92, "help please" 67...
    # Someone asking for help with no other keyword still IS demand — it was
    # falling through to unthemed and hiding the largest signal in the data.
    ("help-seeking",          r"\b(need help|please help|help needed|help please|need advice|"
                              r"advice needed|advice please|looking for advice|any advice|"
                              r"can someone help|help me|first time|newbie|new to)\b", "/questions.html"),
]


def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return data


def load_sitemap_urls(name, index_url, offline):
    os.makedirs(CACHE, exist_ok=True)
    idx_p = os.path.join(CACHE, "%s-index.xml" % name)
    if offline and os.path.exists(idx_p):
        raw = open(idx_p, "rb").read()
    else:
        raw = fetch(index_url, idx_p)
        time.sleep(2)                       # politeness between requests
    txt = _text(raw)
    subs = re.findall(r"<loc>([^<]+)</loc>", txt)
    urls = []
    for i, s in enumerate(subs):
        p = os.path.join(CACHE, "%s-%d.xml" % (name, i))
        if offline and os.path.exists(p):
            sraw = open(p, "rb").read()
        else:
            sraw = fetch(s, p)
            time.sleep(2)
        urls += re.findall(r"<loc>([^<]+)</loc>", _text(sraw))
    return urls


def _text(raw):
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def slug_to_title(url):
    m = re.search(r"/threads/([^/]+?)\.(\d+)/?$", url)
    if not m:
        return None
    s = m.group(1)
    s = re.sub(r"-+", " ", s).strip()
    return s


def analyse(titles):
    kept, excluded, non_question = [], [], 0
    for t in titles:
        if EXCLUDE.search(t):
            excluded.append(t)
            continue
        kept.append(t)
    questions = [t for t in kept if QUESTION.search(t)]

    theme_hits = defaultdict(list)
    unthemed = []
    for t in questions:
        for name, pat, target in THEMES:
            if re.search(pat, t, re.I):
                theme_hits[name].append(t)
                break
        else:
            unthemed.append(t)

    # phrase frequency inside the servable question set
    STOP = set("""the a an and or of to in on for with is are was were be been it its
        this that these those i you my your me we our they them he she his her what
        why how when where who which do does did can could should would has have had
        anyone anybody am if not no yes but so about from at as by just get got go
        going any some more most very much like really been being im ive dont cant
        thats whats theres youre theyre s t re ve ll d m""".split())
    words = Counter()
    bigrams = Counter()
    for t in questions:
        toks = [w for w in re.findall(r"[a-z']+", t.lower()) if w not in STOP and len(w) > 2]
        words.update(toks)
        bigrams.update(" ".join(p) for p in zip(toks, toks[1:]))

    return {
        "total_threads": len(titles),
        "servable": len(kept),
        "excluded_by_charter": len(excluded),
        "questions": len(questions),
        "themes": {k: v for k, v in sorted(theme_hits.items(), key=lambda kv: -len(kv[1]))},
        "unthemed_sample": unthemed[:60],
        "top_words": words.most_common(60),
        "top_bigrams": [b for b in bigrams.most_common(80) if b[1] > 8],
        "excluded_sample": excluded[:25],
    }


def write_md(res, atlas):
    T = {name: target for name, _, target in THEMES}
    L = []
    L.append("# What people actually ask — mined demand\n")
    L.append("*Generated by `demand_mine.py`. Titles only, from public sitemaps; "
             "no thread bodies fetched, nothing crawled that robots.txt disallows.*\n")
    L.append("## Corpus\n")
    L.append("| | count |")
    L.append("|---|---|")
    L.append("| Thread titles read | %d |" % res["total_threads"])
    L.append("| Excluded by the charter (extraction/sourcing/cultivation) | %d |"
             % res["excluded_by_charter"])
    L.append("| Servable (phenomenology & experience) | %d |" % res["servable"])
    L.append("| Of those, question-shaped | %d |" % res["questions"])
    L.append("\n> Excluded threads are counted, never silently dropped. "
             "BUILD.md forbids serving that territory, so demand for it is not a content brief.\n")

    L.append("## Demand by theme — and where the Atlas answers it\n")
    L.append("| Theme | Threads | Atlas page | Covered? |")
    L.append("|---|---|---|---|")
    for name, hits in res["themes"].items():
        L.append("| %s | %d | `%s` | %s |" % (
            name.replace("-", " "), len(hits), T.get(name, "—"),
            "yes" if T.get(name) else "**gap**"))

    L.append("\n## The most-asked phrasings\n")
    L.append("These are the exact word pairs people use. They are the phrasing the "
             "pages should match — not our vocabulary, theirs.\n")
    for b, n in res["top_bigrams"][:40]:
        L.append("- `%s` — %d threads" % (b, n))

    L.append("\n## Sample questions with no Atlas home\n")
    L.append("Candidate new coverage — each one is a real thread title.\n")
    for t in res["unthemed_sample"][:40]:
        L.append("- %s" % t)
    return "\n".join(L)


def selftest():
    """Both directions. A filter proven only on what it drops will happily
    drop everything — the first version scored 100% on MUST_DROP while also
    deleting every 'machine elves' thread on the forum."""
    bad = []
    for t in MUST_KEEP:
        if EXCLUDE.search(t):
            bad.append("WRONGLY EXCLUDED: %r  (matched %r)"
                       % (t, EXCLUDE.search(t).group(0)))
    for t in MUST_DROP:
        if not EXCLUDE.search(t):
            bad.append("WRONGLY KEPT:     %r" % t)
    for line in bad:
        print("  " + line)
    print("  selftest: %d/%d keep-cases, %d/%d drop-cases  -> %s"
          % (len(MUST_KEEP) - sum(1 for b in bad if "EXCLUDED" in b), len(MUST_KEEP),
             len(MUST_DROP) - sum(1 for b in bad if "KEPT" in b), len(MUST_DROP),
             "FAIL" if bad else "PASS"))
    return not bad


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    offline = "--offline" in sys.argv
    os.makedirs(CACHE, exist_ok=True)
    all_titles = []
    for name, idx, marker in SOURCES:
        urls = load_sitemap_urls(name, idx, offline)
        titles = [slug_to_title(u) for u in urls if marker in u]
        titles = [t for t in titles if t]
        print("%-12s %6d urls -> %6d thread titles" % (name, len(urls), len(titles)))
        all_titles += titles

    atlas = json.load(open(os.path.join(ROOT, "data", "atlas.json"), encoding="utf-8"))
    res = analyse(all_titles)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(write_md(res, atlas))

    print("\n  total %d | charter-excluded %d | servable %d | questions %d"
          % (res["total_threads"], res["excluded_by_charter"],
             res["servable"], res["questions"]))
    print("  themes:", ", ".join("%s=%d" % (k, len(v)) for k, v in res["themes"].items()))
    print("\n  ->", OUT_MD)
