#!/usr/bin/env python3
"""Aggregate peer-reviewed DMT / ayahuasca literature from PubMed, Europe PMC, OpenAlex."""
import json, time, re, sys, html
import requests
import xml.etree.ElementTree as ET

EMAIL = "research@dmtatlas.com"
OUTDIR = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas/data/research"
RAWDIR = OUTDIR + "/raw"
import os
os.makedirs(RAWDIR, exist_ok=True)

S = requests.Session()
S.headers.update({"User-Agent": "DMTAtlas-ResearchArchive/1.0 (mailto:%s)" % EMAIL})

def get(url, params=None, tries=5, timeout=60):
    last = None
    for i in range(tries):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            last = "HTTP %s" % r.status_code
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 * (i + 1))
                continue
            # other codes: brief retry
            time.sleep(1 + i)
        except Exception as e:
            last = str(e)
            time.sleep(2 * (i + 1))
    print("  !! GET failed %s params=%s -> %s" % (url, params, last), file=sys.stderr)
    return None

# ---------------- PubMed ----------------
def pubmed():
    print("== PubMed ==")
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    query = ('("N,N-Dimethyltryptamine"[MeSH Terms] OR "dimethyltryptamine"[Title/Abstract] '
             'OR "N,N-DMT"[Title/Abstract] OR "ayahuasca"[Title/Abstract])')
    # esearch with history
    r = get(base + "esearch.fcgi", {
        "db": "pubmed", "term": query, "retmax": 0, "usehistory": "y",
        "retmode": "json", "email": EMAIL})
    if not r:
        return []
    js = r.json()["esearchresult"]
    count = int(js["count"])
    webenv = js["webenv"]; qk = js["querykey"]
    print("  count = %d" % count)
    records = []
    retmax = 200
    for start in range(0, count, retmax):
        rr = get(base + "efetch.fcgi", {
            "db": "pubmed", "WebEnv": webenv, "query_key": qk,
            "retstart": start, "retmax": retmax, "retmode": "xml", "email": EMAIL})
        if not rr:
            continue
        try:
            root = ET.fromstring(rr.content)
        except Exception as e:
            print("  xml parse err at %d: %s" % (start, e), file=sys.stderr)
            time.sleep(0.5); continue
        for art in root.findall(".//PubmedArticle"):
            records.append(parse_pubmed_article(art))
        print("  fetched %d / %d" % (min(start + retmax, count), count))
        time.sleep(0.4)
    with open(RAWDIR + "/pubmed.json", "w", encoding="utf-8") as f:
        json.dump(records, f)
    print("  parsed %d" % len(records))
    return records

def _txt(el):
    if el is None:
        return ""
    return "".join(el.itertext()).strip()

def parse_pubmed_article(art):
    pmid = _txt(art.find(".//PMID"))
    art_el = art.find(".//Article")
    title = _txt(art.find(".//ArticleTitle"))
    # abstract (may have multiple sections)
    abst_parts = []
    for ab in art.findall(".//Abstract/AbstractText"):
        label = ab.get("Label")
        t = _txt(ab)
        if label:
            abst_parts.append("%s: %s" % (label, t))
        else:
            abst_parts.append(t)
    abstract = " ".join(p for p in abst_parts if p).strip()
    journal = _txt(art.find(".//Journal/Title"))
    # year
    year = None
    for path in [".//Article/Journal/JournalIssue/PubDate/Year",
                 ".//Article/Journal/JournalIssue/PubDate/MedlineDate",
                 ".//PubDate/Year", ".//PubDate/MedlineDate"]:
        el = art.find(path)
        if el is not None and el.text:
            m = re.search(r"(\d{4})", el.text)
            if m:
                year = int(m.group(1)); break
    # authors
    authors = []
    for a in art.findall(".//AuthorList/Author"):
        ln = _txt(a.find("LastName"))
        fn = _txt(a.find("ForeName")) or _txt(a.find("Initials"))
        coll = _txt(a.find("CollectiveName"))
        if ln:
            authors.append((ln + ", " + fn).strip().strip(","))
        elif coll:
            authors.append(coll)
    # doi
    doi = None
    for eid in art.findall(".//ArticleIdList/ArticleId"):
        if eid.get("IdType") == "doi":
            doi = _txt(eid); break
    if not doi:
        for eloc in art.findall(".//ELocationID"):
            if eloc.get("EIdType") == "doi":
                doi = _txt(eloc); break
    ptypes = [_txt(p) for p in art.findall(".//PublicationTypeList/PublicationType")]
    ptype = next((p for p in ptypes if p not in ("Journal Article", "English Abstract")), None) or (ptypes[0] if ptypes else "")
    return {
        "title": title, "authors": authors, "year": year, "venue": journal,
        "doi": doi, "pmid": pmid, "source_db": "pubmed", "type": ptype,
        "cited_by_count": None, "abstract": abstract,
        "url": "https://pubmed.ncbi.nlm.nih.gov/%s/" % pmid if pmid else None,
    }

# ---------------- Europe PMC ----------------
def europepmc():
    print("== Europe PMC ==")
    base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    query = "dimethyltryptamine OR ayahuasca"
    cursor = "*"
    records = []
    page = 0
    while True:
        r = get(base, {"query": query, "format": "json", "pageSize": 1000,
                       "cursorMark": cursor, "resultType": "core"})
        if not r:
            break
        js = r.json()
        results = js.get("resultList", {}).get("result", [])
        for res in results:
            records.append(parse_epmc(res))
        page += 1
        total = js.get("hitCount")
        print("  page %d, got %d (running %d / %s)" % (page, len(results), len(records), total))
        nxt = js.get("nextCursorMark")
        if not nxt or nxt == cursor or not results:
            break
        cursor = nxt
        time.sleep(0.3)
    with open(RAWDIR + "/europepmc.json", "w", encoding="utf-8") as f:
        json.dump(records, f)
    print("  parsed %d" % len(records))
    return records

def parse_epmc(res):
    authors = []
    al = res.get("authorList", {}).get("author", [])
    for a in al:
        nm = a.get("fullName") or a.get("collectiveName") or ""
        if nm:
            authors.append(nm)
    year = None
    for k in ("pubYear", "firstPublicationDate"):
        v = res.get(k)
        if v:
            m = re.search(r"(\d{4})", str(v))
            if m:
                year = int(m.group(1)); break
    doi = res.get("doi")
    pmid = res.get("pmid")
    ptypes = res.get("pubTypeList", {}).get("pubType", [])
    if isinstance(ptypes, str):
        ptypes = [ptypes]
    ptype = next((p for p in ptypes if p not in ("Journal Article", "research-article", "article")), None) or (ptypes[0] if ptypes else "")
    url = None
    if doi:
        url = "https://doi.org/" + doi
    elif pmid:
        url = "https://pubmed.ncbi.nlm.nih.gov/%s/" % pmid
    elif res.get("id"):
        url = "https://europepmc.org/article/%s/%s" % (res.get("source", "MED"), res.get("id"))
    return {
        "title": (res.get("title") or "").strip().rstrip("."),
        "authors": authors, "year": year,
        "venue": res.get("journalInfo", {}).get("journal", {}).get("title") or res.get("bookOrReportDetails", {}).get("publisher") or "",
        "doi": doi, "pmid": pmid, "source_db": "europepmc", "type": ptype,
        "cited_by_count": res.get("citedByCount"),
        "abstract": (res.get("abstractText") or "").strip(),
        "url": url,
    }

# ---------------- OpenAlex ----------------
def openalex():
    print("== OpenAlex ==")
    base = "https://api.openalex.org/works"
    records = []
    cursor = "*"
    page = 0
    while True:
        r = get(base, {"search": "dimethyltryptamine", "per-page": 200,
                       "cursor": cursor, "mailto": EMAIL})
        if not r:
            break
        js = r.json()
        results = js.get("results", [])
        for res in results:
            records.append(parse_openalex(res))
        page += 1
        total = js.get("meta", {}).get("count")
        print("  page %d, got %d (running %d / %s)" % (page, len(results), len(records), total))
        cursor = js.get("meta", {}).get("next_cursor")
        if not cursor or not results:
            break
        time.sleep(0.25)
    with open(RAWDIR + "/openalex.json", "w", encoding="utf-8") as f:
        json.dump(records, f)
    print("  parsed %d" % len(records))
    return records

def invert_abstract(inv):
    if not inv:
        return ""
    positions = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)

def parse_openalex(res):
    authors = []
    for a in res.get("authorships", []):
        nm = a.get("author", {}).get("display_name")
        if nm:
            authors.append(nm)
    doi = res.get("doi")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    pmid = None
    ids = res.get("ids", {})
    if ids.get("pmid"):
        m = re.search(r"(\d+)$", ids["pmid"])
        if m:
            pmid = m.group(1)
    venue = ""
    pl = res.get("primary_location") or {}
    src = pl.get("source") or {}
    if src:
        venue = src.get("display_name") or ""
    return {
        "title": (res.get("title") or "").strip().rstrip("."),
        "authors": authors,
        "year": res.get("publication_year"),
        "venue": venue,
        "doi": doi, "pmid": pmid, "source_db": "openalex",
        "type": res.get("type") or "",
        "cited_by_count": res.get("cited_by_count"),
        "abstract": invert_abstract(res.get("abstract_inverted_index")),
        "url": res.get("doi") or (res.get("primary_location") or {}).get("landing_page_url") or res.get("id"),
    }

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "pubmed"):
        pubmed()
    if which in ("all", "europepmc"):
        europepmc()
    if which in ("all", "openalex"):
        openalex()
    print("DONE fetch")
