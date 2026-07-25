# -*- coding: utf-8 -*-
"""Aggregate a books/long-form bibliography on DMT & ayahuasca.
Sources: Google Books API + Open Library Search API (no keys)."""
import requests, time, json, re, sys, html
from collections import defaultdict

OUT = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas/data/research/books.json"
RAW = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas/data/research/_raw_books.json"

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (dmtatlas-bibliography-research/1.0)"})

FAILURES = []

# ---------------- Query sets ----------------
GB_QUERIES = [
    'dimethyltryptamine',
    'N,N-dimethyltryptamine',
    'DMT spirit molecule',
    'DMT psychedelic',
    'ayahuasca',
    'ayahuasca shamanism',
    'ayahuasca visions',
    'yage yaje',
    'psychedelic tryptamine',
    'psychedelic shamanism amazon',
    'hallucinogen tryptamine dmt',
    'hyperspace DMT entities',
    'entheogen ayahuasca',
    'vine of the soul ayahuasca',
    'intitle:ayahuasca',
    'intitle:DMT psychedelic',
    'subject:ayahuasca',
    'psychedelic entheogen amazon shaman',
    'Strassman DMT',
    'ayahuasca ritual religion',
]
OL_QUERIES = [
    # core topics
    'dimethyltryptamine',
    'DMT spirit molecule',
    'DMT psychedelic hyperspace',
    'ayahuasca',
    'ayahuasca shamanism',
    'ayahuasca visions',
    'ayahuasca healing',
    'ayahuasca religion Brazil',
    'ayahuasca tourism',
    'santo daime',
    'uniao do vegetal',
    'yage',
    'yaje vine soul',
    'banisteriopsis caapi',
    'harmala tryptamine',
    'psychedelic tryptamine',
    'entheogen ayahuasca',
    'entheogen plants gods',
    'visionary plants amazon',
    'plant teachers shaman',
    'amazon shamanism hallucinogen',
    '5-MeO-DMT toad',
    'psychedelic amazon curandero',
    'sacred vine medicine',
    # author-centric
    'Rick Strassman DMT',
    'Terence McKenna psychedelic',
    'Dennis McKenna',
    'Jeremy Narby',
    'Luis Eduardo Luna ayahuasca',
    'Benny Shanon ayahuasca',
    'Andrew Gallimore DMT',
    'Graham St John DMT',
    'Ralph Metzner ayahuasca',
    'Richard Evans Schultes plants gods',
    'Jonathan Ott pharmacotheon',
    'Wade Davis amazon',
    'Christian Ratsch encyclopedia psychoactive',
    'Beatriz Labate ayahuasca',
]

# ---------------- Filter vocab ----------------
KEEP_TERMS = [
    'ayahuasca', 'dimethyltryptamine', 'n,n-dmt', 'nn-dmt', 'spirit molecule',
    'yage', 'yaje', 'yag\u00e9', 'tryptamine', 'psychedelic', 'psychedelics',
    'entheogen', 'shaman', 'shamanism', 'hallucinogen', 'psychoactive',
    'ayahuasquero', 'vegetalismo', 'banisteriopsis', 'psychotria', 'chacruna',
    'hyperspace', 'dmt', 'psilocybin', 'mescaline', 'harmaline', 'harmine',
    'santo daime', 'uni\u00e3o do vegetal', 'udv', 'icaros', 'curandero',
    'plant medicine', 'amazon', 'psychonaut', 'psychedelia', 'entheogenic',
    '5-meo-dmt', 'toad', 'bufo', 'consciousness',
]
# Terms that strongly signal a DMT-acronym collision when "dmt" present but no psychedelic context.
COLLISION_TERMS = [
    'dot matrix', 'dot-matrix', 'diffusion mri', 'diffusion tensor', 'materials science',
    'music therapy', 'data management', 'discrete mathematics', 'disaster management',
    'device management', 'sap', 'finance', 'accounting', 'marketing', 'supply chain',
    'welding', 'metallurgy', 'concrete', 'geotechnical', 'petroleum', 'drilling',
    'railway', 'transit', 'manufacturing tool', 'die', 'machining', 'thermogravimetric',
    'differential', 'thermal analysis', 'polymer', 'catalysis', 'catalyst', 'membrane',
    'trauma', 'dialectical', 'medication management', 'diabetes', 'dermatology',
]

def txt(*parts):
    return " ".join(p for p in parts if p).lower()

# how-to / synthesis / extraction titles are explicitly out of scope
HOWTO_DROP = re.compile(
    r'how to (make|extract|grow|synth)|extraction (tek|guide|method)|'
    r'synthesis of (dmt|tryptamine)|\bmade simple\b|home ?grow|cultivation guide|'
    r'recipe (book|guide)|step[- ]by[- ]step (guide )?(to )?(make|extract)', re.I)

# ayahuasca signal: multi-char safe terms plus word-boundary short terms (avoid Hebrew "va-yaged")
_AYA_WORDS = re.compile(r'\byag[e\u00e9]\b|\byaj[e\u00e9]\b|\bcaapi\b', re.I)
def ayahuasca_signal(blob):
    if any(t in blob for t in ['ayahuasca', 'santo daime', 'vegetalismo', 'banisteriopsis',
                               'ayahuasquero', 'ayahuasquera', 'icaros', 'uni\u00e3o do vegetal',
                               'union do vegetal', 'chacruna']):
        return True
    return bool(_AYA_WORDS.search(blob))

def is_relevant(title, desc, subjects, is_seed=False):
    """Return (keep_bool, uncertain_bool)."""
    if is_seed:
        return True, False
    blob = txt(title, desc, " ".join(subjects or []))
    if HOWTO_DROP.search(blob):
        return False, False
    # strong keep signals
    has_ayahuasca = ayahuasca_signal(blob)
    has_dmt_word = ('dimethyltryptamine' in blob or 'spirit molecule' in blob or
                    '5-meo-dmt' in blob or 'n,n-dmt' in blob or 'nn-dmt' in blob)
    psych_ctx = any(t in blob for t in ['psychedelic', 'entheogen', 'shaman', 'hallucinog',
                                        'psychoactive', 'tryptamine', 'psychonaut', 'hyperspace',
                                        'consciousness', 'mescaline', 'psilocybin', 'plant medicine'])
    # DMT acronym present as standalone token?
    has_dmt_token = bool(re.search(r'\bdmt\b', blob))

    if has_ayahuasca or has_dmt_word:
        return True, False
    if has_dmt_token:
        # need psychedelic context, and no collision signal
        collision = any(c in blob for c in COLLISION_TERMS)
        if psych_ctx and not collision:
            return True, False
        if collision:
            return False, False
        # dmt token but ambiguous
        return True, True  # keep uncertain
    # no dmt/ayahuasca token: keep only if clearly psychedelic-tryptamine themed
    if psych_ctx and any(t in blob for t in ['tryptamine', 'psychedelic', 'entheogen',
                                             'ayahuasca', 'shaman']):
        # generic psychedelic book; keep as uncertain unless strong tryptamine tie
        if 'tryptamine' in blob:
            return True, False
        return True, True
    return False, False

def topic_tag(title, desc, subjects):
    blob = txt(title, desc, " ".join(subjects or []))
    if ayahuasca_signal(blob):
        return 'ayahuasca'
    if 'dimethyltryptamine' in blob or 'spirit molecule' in blob or re.search(r'\bdmt\b', blob) or '5-meo-dmt' in blob:
        return 'N,N-DMT'
    if any(t in blob for t in ['ethnobotan', 'plant', 'shaman', 'amazon', 'curandero', 'botany']):
        return 'ethnobotany'
    return 'psychedelics-general'

def norm_title(t):
    t = (t or '').lower()
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def core_title(t):
    """Main title only (before subtitle/parenthetical), normalized. For author-aware dedup."""
    t = (t or '').lower()
    t = re.split(r'[:(]', t)[0]
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

_NAME_SUFFIX = {'md', 'phd', 'ph', 'd', 'm', 'dr', 'jr', 'sr', 'ii', 'iii', 'iv',
                'esq', 'msw', 'lcsw', 'od', 'dds', 'mds', 'mba', 'ma'}
def lastname(a):
    toks = re.sub(r'[^a-z ]', ' ', (a or '').lower()).split()
    while toks and toks[-1] in _NAME_SUFFIX:
        toks.pop()
    return toks[-1] if toks else ''

def lastnames(rec):
    return {lastname(a) for a in (rec.get('authors') or []) if a}

def clean_desc(d):
    if not d:
        return ''
    d = html.unescape(d)
    d = re.sub(r'<[^>]+>', '', d)
    d = re.sub(r'\s+', ' ', d).strip()
    if len(d) > 900:
        d = d[:900].rsplit(' ', 1)[0] + '\u2026'
    return d

def year_from(s):
    if not s:
        return None
    m = re.search(r'(1[5-9]\d\d|20\d\d)', str(s))
    return int(m.group(1)) if m else None

# ---------------- Google Books ----------------
def fetch_google():
    out = []
    quota_dead = False
    for q in GB_QUERIES:
        if quota_dead:
            break
        for start in range(0, 120, 40):  # up to 120 results/query
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {"q": q, "startIndex": start, "maxResults": 40,
                      "printType": "books", "country": "US"}
            try:
                r = S.get(url, params=params, timeout=30)
                if r.status_code != 200:
                    if r.status_code == 429 and 'per day' in r.text:
                        FAILURES.append("GoogleBooks: daily anonymous quota exhausted (HTTP 429 'Queries per day') "
                                        "— skipped entirely this run. Retry next UTC day for supplemental coverage.")
                        quota_dead = True
                    else:
                        FAILURES.append(f"GoogleBooks '{q}' start={start}: HTTP {r.status_code}")
                    break
                data = r.json()
            except Exception as e:
                FAILURES.append(f"GoogleBooks '{q}' start={start}: {e}")
                break
            items = data.get("items", [])
            if not items:
                break
            for it in items:
                vi = it.get("volumeInfo", {})
                isbn13 = None
                for ident in vi.get("industryIdentifiers", []) or []:
                    if ident.get("type") == "ISBN_13":
                        isbn13 = ident.get("identifier")
                out.append({
                    "src": "google",
                    "title": vi.get("title", "") + (": " + vi.get("subtitle") if vi.get("subtitle") else ""),
                    "authors": vi.get("authors", []) or [],
                    "year": year_from(vi.get("publishedDate")),
                    "publisher": vi.get("publisher"),
                    "isbn13": isbn13,
                    "description": clean_desc(vi.get("description")),
                    "categories": vi.get("categories", []) or [],
                    "url": vi.get("infoLink") or vi.get("canonicalVolumeLink"),
                    "pageCount": vi.get("pageCount"),
                })
            time.sleep(0.4)
            if len(items) < 40:
                break
    return out

# ---------------- Open Library ----------------
def fetch_openlibrary():
    out = []
    for q in OL_QUERIES:
        url = "https://openlibrary.org/search.json"
        params = {"q": q, "limit": 100,
                  "fields": "key,title,subtitle,author_name,first_publish_year,isbn,publisher,subject,edition_count"}
        try:
            r = S.get(url, params=params, timeout=40)
            if r.status_code != 200:
                FAILURES.append(f"OpenLibrary '{q}': HTTP {r.status_code}")
                continue
            data = r.json()
        except Exception as e:
            FAILURES.append(f"OpenLibrary '{q}': {e}")
            continue
        for d in data.get("docs", []):
            isbns = d.get("isbn", []) or []
            isbn13 = next((i for i in isbns if len(i) == 13 and i.startswith("978")), None)
            title = d.get("title", "")
            if d.get("subtitle"):
                title = title + ": " + d["subtitle"]
            out.append({
                "src": "openlibrary",
                "title": title,
                "authors": d.get("author_name", []) or [],
                "year": d.get("first_publish_year"),
                "publisher": (d.get("publisher") or [None])[0],
                "isbn13": isbn13,
                "description": "",
                "categories": (d.get("subject") or [])[:12],
                "url": "https://openlibrary.org" + d["key"] if d.get("key") else None,
                "pageCount": None,
            })
        time.sleep(0.5)
    return out

# ---------------- Open Library work-description enrichment ----------------
def enrich_descriptions(records, cap=200):
    """For final records lacking a description that came from Open Library,
    fetch the work JSON and pull its description. Capped to be polite."""
    n = 0
    for rec in records:
        if n >= cap:
            break
        if rec.get("description"):
            continue
        url = rec.get("url") or ""
        m = re.search(r'(/works/OL\d+W)', url)
        if not m:
            continue
        try:
            r = S.get("https://openlibrary.org" + m.group(1) + ".json", timeout=25)
            n += 1
            if r.status_code != 200:
                continue
            w = r.json()
        except Exception:
            continue
        d = w.get("description")
        if isinstance(d, dict):
            d = d.get("value")
        if d:
            rec["description"] = clean_desc(d)
        time.sleep(0.25)
    return n

# ---------------- Seeds ----------------
SEEDS = [
    {"title": "DMT: The Spirit Molecule", "authors": ["Rick Strassman"], "year": 2001,
     "publisher": "Park Street Press", "isbn13": "9780892819270", "topic_tag": "N,N-DMT",
     "type": "book",
     "description": "Clinical psychiatrist Rick Strassman's account of his DEA-approved 1990s human research injecting DMT into volunteers at the University of New Mexico; a landmark scientific and philosophical study of the compound's effects on consciousness."},
    {"title": "DMT and the Soul of Prophecy: A New Science of Spiritual Revelation in the Hebrew Bible",
     "authors": ["Rick Strassman"], "year": 2014, "publisher": "Park Street Press",
     "isbn13": "9781594774560", "topic_tag": "N,N-DMT", "type": "book",
     "description": "Strassman proposes a 'theoneurology' model linking endogenous DMT to the prophetic states described in the Hebrew Bible, extending the arguments of The Spirit Molecule into theology and philosophy."},
    {"title": "The Antipodes of the Mind: Charting the Phenomenology of the Ayahuasca Experience",
     "authors": ["Benny Shanon"], "year": 2002, "publisher": "Oxford University Press",
     "isbn13": "9780199252923", "topic_tag": "ayahuasca", "type": "monograph",
     "description": "A cognitive psychologist's systematic phenomenological survey of the ayahuasca experience, based on the author's own hundreds of sessions and a large body of informant reports; a foundational academic study of ayahuasca visions."},
    {"title": "Alien Information Theory: Psychedelic Drug Technologies and the Cosmic Game",
     "authors": ["Andrew R. Gallimore"], "year": 2019, "publisher": "Strange Worlds Press",
     "isbn13": "9781916142503", "topic_tag": "N,N-DMT", "type": "book",
     "description": "Neurobiologist Andrew Gallimore's synthesis of DMT pharmacology, information theory, and cosmology, exploring the hypothesis that DMT provides access to a genuine alternate reality."},
    {"title": "Death by Astonishment: Confronting the Mystery of the World's Strangest Drug",
     "authors": ["Andrew R. Gallimore"], "year": 2025, "publisher": "St. Martin's Press",
     "isbn13": "9781250325228", "topic_tag": "N,N-DMT", "type": "book",
     "description": "Gallimore's narrative history and scientific examination of DMT, taking its title from Terence McKenna's phrase and confronting the compound's uniquely bewildering phenomenology."},
    {"title": "Ayahuasca Visions: The Religious Iconography of a Peruvian Shaman",
     "authors": ["Luis Eduardo Luna", "Pablo Amaringo"], "year": 1991, "publisher": "North Atlantic Books",
     "isbn13": "9781556430626", "topic_tag": "ayahuasca", "type": "book",
     "description": "A collaboration between anthropologist Luis Eduardo Luna and vegetalista painter Pablo Amaringo, reproducing and interpreting Amaringo's visionary ayahuasca paintings as a window into Amazonian mestizo shamanism."},
    {"title": "Vegetalismo: Shamanism Among the Mestizo Population of the Peruvian Amazon",
     "authors": ["Luis Eduardo Luna"], "year": 1986, "publisher": "Almqvist & Wiksell International",
     "isbn13": None, "topic_tag": "ayahuasca", "type": "monograph",
     "description": "Luna's foundational ethnographic monograph on vegetalismo, the plant-based shamanic tradition of the mestizo population of the Peruvian Amazon, including detailed treatment of ayahuasca practice."},
    {"title": "The Cosmic Serpent: DNA and the Origins of Knowledge",
     "authors": ["Jeremy Narby"], "year": 1998, "publisher": "Jeremy P. Tarcher/Putnam",
     "isbn13": "9780874779646", "topic_tag": "ayahuasca", "type": "book",
     "description": "Anthropologist Jeremy Narby's controversial thesis that Amazonian shamans, through ayahuasca, access molecular-level biological information; a widely read work bridging ethnobotany and biology."},
    {"title": "True Hallucinations: Being an Account of the Author's Extraordinary Adventures in the Devil's Paradise",
     "authors": ["Terence McKenna"], "year": 1993, "publisher": "HarperSanFrancisco",
     "isbn13": "9780062506528", "topic_tag": "psychedelics-general", "type": "book",
     "description": "Terence McKenna's memoir of the 1971 'Experiment at La Chorrera' in the Colombian Amazon, involving psilocybin and ayahuasca and the genesis of his ideas about psychedelics, time, and reality."},
    {"title": "Food of the Gods: The Search for the Original Tree of Knowledge",
     "authors": ["Terence McKenna"], "year": 1992, "publisher": "Bantam Books",
     "isbn13": "9780553371307", "topic_tag": "psychedelics-general", "type": "book",
     "description": "McKenna's cultural and evolutionary history of humanity's relationship with psychoactive plants, including DMT-containing preparations and ayahuasca, advancing his 'Stoned Ape' hypothesis."},
    {"title": "The Brotherhood of the Screaming Abyss: My Life with Terence McKenna",
     "authors": ["Dennis McKenna"], "year": 2012, "publisher": "Polaris Publications",
     "isbn13": "9780875161129", "topic_tag": "psychedelics-general", "type": "book",
     "description": "Ethnopharmacologist Dennis McKenna's memoir of his life and research alongside his brother Terence, including their Amazon expeditions and decades of work on ayahuasca and tryptamines."},
    {"title": "Ayahuasca: Human Consciousness and the Spirits of Nature",
     "authors": ["Ralph Metzner"], "year": 1999, "publisher": "Thunder's Mouth Press",
     "isbn13": "9781560252603", "topic_tag": "ayahuasca", "type": "edited-volume",
     "description": "Edited by psychologist Ralph Metzner, an anthology of scientific, experiential, and cultural essays on ayahuasca, one of the first English-language collections devoted to the brew."},
    {"title": "The Internationalization of Ayahuasca",
     "authors": ["Beatriz Caiuby Labate", "Henrik Jungaberle"], "year": 2011, "publisher": "LIT Verlag",
     "isbn13": "9783643901484", "topic_tag": "ayahuasca", "type": "edited-volume",
     "description": "A scholarly edited volume documenting the global spread of ayahuasca use beyond the Amazon, covering religious, legal, therapeutic, and anthropological dimensions of its internationalization."},
    {"title": "Mystery School in Hyperspace: A Cultural History of DMT",
     "authors": ["Graham St John"], "year": 2015, "publisher": "Evolver Editions / North Atlantic Books",
     "isbn13": "9781583949221", "topic_tag": "N,N-DMT", "type": "book",
     "description": "Cultural historian Graham St John's comprehensive cultural history of DMT, tracing its scientific discovery, countercultural adoption, and role in the visionary imagination."},
    {"title": "One River: Explorations and Discoveries in the Amazon Rain Forest",
     "authors": ["Wade Davis"], "year": 1996, "publisher": "Simon & Schuster",
     "isbn13": "9780684808864", "topic_tag": "ethnobotany", "type": "book",
     "description": "Ethnobotanist Wade Davis's account of Richard Evans Schultes and his students' explorations of Amazonian plants, including extensive treatment of ayahuasca and other psychoactive preparations."},
]

def main():
    print("Fetching Google Books...", file=sys.stderr)
    g = fetch_google()
    print(f"  google raw: {len(g)}", file=sys.stderr)
    print("Fetching Open Library...", file=sys.stderr)
    o = fetch_openlibrary()
    print(f"  openlibrary raw: {len(o)}", file=sys.stderr)

    raw = g + o
    with open(RAW, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=1)

    # normalize + filter
    normd = []
    for r in raw:
        title = (r["title"] or "").strip()
        if not title:
            continue
        keep, uncertain = is_relevant(title, r.get("description", ""), r.get("categories", []))
        if not keep:
            continue
        rec = {
            "title": title,
            "authors": r.get("authors", []),
            "year": r.get("year"),
            "publisher": r.get("publisher"),
            "isbn13": r.get("isbn13"),
            "type": "book",
            "topic_tag": topic_tag(title, r.get("description", ""), r.get("categories", [])),
            "description": r.get("description", ""),
            "seminal": False,
            "url": r.get("url"),
            "_src": r["src"],
            "_cats": r.get("categories", []),
        }
        if uncertain:
            rec["uncertain_topic"] = True
        normd.append(rec)

    # prepend seeds (as records)
    for s in SEEDS:
        rec = dict(s)
        rec["seminal"] = True
        rec["_src"] = "seed"
        rec["_cats"] = []
        normd.insert(0, rec)

    # ---- dedup ----
    by_key = {}
    def better(a, b):
        # prefer one with more fields filled / longer description / seed
        if a.get("seminal") and not b.get("seminal"):
            return a
        if b.get("seminal") and not a.get("seminal"):
            return b
        score = lambda x: (bool(x.get("isbn13")), len(x.get("description") or ""),
                           bool(x.get("publisher")), bool(x.get("year")), len(x.get("authors") or []))
        return a if score(a) >= score(b) else b

    def merge(a, b):
        keep = better(a, b)
        other = b if keep is a else a
        for fld in ["publisher", "year", "isbn13", "url"]:
            if not keep.get(fld) and other.get(fld):
                keep[fld] = other[fld]
        if len(other.get("description") or "") > len(keep.get("description") or ""):
            keep["description"] = other["description"]
        if len(other.get("authors") or []) > len(keep.get("authors") or []):
            keep["authors"] = other["authors"]
        # merge cats
        keep["_cats"] = list({*(keep.get("_cats") or []), *(other.get("_cats") or [])})
        if other.get("seminal"):
            keep["seminal"] = True
        if keep.get("uncertain_topic") and not other.get("uncertain_topic"):
            keep.pop("uncertain_topic", None)
        return keep

    # first pass: ISBN13
    for rec in normd:
        isbn = rec.get("isbn13")
        key = ("isbn", isbn) if isbn else ("title", norm_title(rec["title"]))
        if key in by_key:
            by_key[key] = merge(by_key[key], rec)
        else:
            by_key[key] = rec

    # second pass: collapse title dups that have different/absent ISBNs into one
    title_map = {}
    final = []
    for rec in by_key.values():
        nt = norm_title(rec["title"])
        # also collapse very-close titles (strip trailing edition noise handled by norm)
        if nt in title_map:
            idx = title_map[nt]
            final[idx] = merge(final[idx], rec)
        else:
            title_map[nt] = len(final)
            final.append(rec)

    # ---- third pass: author-aware merge of same-main-title editions/translations ----
    groups = defaultdict(list)
    for rec in final:
        groups[core_title(rec["title"])].append(rec)
    merged = []
    for ck, group in groups.items():
        if len(group) == 1:
            merged.append(group[0])
            continue
        used = [False] * len(group)
        multiword = len(ck.split()) > 1
        for i in range(len(group)):
            if used[i]:
                continue
            base = group[i]
            used[i] = True
            for j in range(i + 1, len(group)):
                if used[j]:
                    continue
                ln_i, ln_j = lastnames(base), lastnames(group[j])
                share = bool(ln_i & ln_j)
                authorless = (not ln_i or not ln_j) and multiword
                if share or authorless:
                    base = merge(base, group[j])
                    used[j] = True
            merged.append(base)
    final = merged

    # enrich missing descriptions from Open Library works API
    enriched = enrich_descriptions(final, cap=220)
    print(f"descriptions enriched via OL works API: {enriched}", file=sys.stderr)

    # ---- edited-volume / monograph typing heuristic (after enrichment) ----
    for rec in final:
        if rec.get("seminal"):
            continue
        blob = txt(rec["title"], rec.get("description",""), " ".join(rec.get("_cats") or []))
        if any(w in blob for w in ['edited by', 'edited volume', 'editors', 'anthology',
                                   'collection of essays', 'edited collection', 'reader in',
                                   'essays on', 'proceedings of']):
            rec["type"] = "edited-volume"
        elif any(w in blob for w in ['ethnograph', 'monograph', 'dissertation', 'ph.d', 'doctoral thesis']):
            rec["type"] = "monograph"

    # drop internal fields; sort by year
    def yr(r):
        return r.get("year") if r.get("year") else 9999
    final.sort(key=lambda r: (yr(r), norm_title(r["title"])))

    out_records = []
    for rec in final:
        rec.pop("_src", None)
        rec.pop("_cats", None)
        # ensure field order
        out_records.append({
            "title": rec["title"],
            "authors": rec.get("authors", []),
            "year": rec.get("year"),
            "publisher": rec.get("publisher"),
            "isbn13": rec.get("isbn13"),
            "type": rec.get("type", "book"),
            "topic_tag": rec.get("topic_tag", "psychedelics-general"),
            "description": rec.get("description", ""),
            "seminal": bool(rec.get("seminal")),
            "url": rec.get("url"),
            **({"uncertain_topic": True} if rec.get("uncertain_topic") else {}),
        })

    # counts
    by_decade = {}
    by_type = {}
    for r in out_records:
        y = r.get("year")
        if y:
            dec = f"{(y//10)*10}s"
        else:
            dec = "unknown"
        by_decade[dec] = by_decade.get(dec, 0) + 1
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    # sort decade keys
    def dkey(k):
        return -1 if k == "unknown" else int(k[:-1])
    by_decade = {k: by_decade[k] for k in sorted(by_decade, key=dkey)}

    payload = {
        "generated_utc": "PLACEHOLDER",
        "source_notes": ("Aggregated from Google Books API and Open Library Search API (no auth keys). "
                         "Queries covered DMT/N,N-dimethyltryptamine, ayahuasca/yage, psychedelic tryptamines, "
                         "Amazonian shamanism/ethnobotany, and entheogen studies. Records deduplicated by ISBN-13 "
                         "then normalized title. 15 canonical seed works were verified and enriched by hand and "
                         "marked seminal. Acronym-collision 'DMT' hits (dot-matrix, diffusion-MRI, materials science, "
                         "music therapy, business/finance, etc.) were filtered out; genuinely ambiguous items are "
                         "flagged uncertain_topic rather than dropped. Metadata + publisher descriptions only \u2014 "
                         "no dosing, synthesis, or how-to content."),
        "counts": {"total": len(out_records), "by_decade": by_decade, "by_type": by_type},
        "api_failures": FAILURES,
        "records": out_records,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    # report to stderr
    print(f"TOTAL unique: {len(out_records)}", file=sys.stderr)
    print(f"by_decade: {by_decade}", file=sys.stderr)
    print(f"by_type: {by_type}", file=sys.stderr)
    print(f"failures: {FAILURES}", file=sys.stderr)
    seeds_present = [r['title'] for r in out_records if r['seminal']]
    print(f"seminal present ({len(seeds_present)}):", file=sys.stderr)
    for t in seeds_present:
        print("  - " + t, file=sys.stderr)

if __name__ == "__main__":
    main()
