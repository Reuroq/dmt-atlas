#!/usr/bin/env python3
"""Harvest DMT / 5-MeO-DMT / ayahuasca clinical trials + preprints into a JSON catalog."""
import json, time, datetime, sys, re
import requests

OUT = "C:/Users/dwayn/AppData/Local/Temp/claude/C--Users-dwayn-testing1-Polymarket/bbda93a3-2e75-4484-a5d6-d05c39a1fe75/scratchpad/dmt-atlas/data/research/trials.json"

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (research-archive; trials-catalog)"})

CTG = "https://clinicaltrials.gov/api/v2/studies"
# Primary molecule terms + full chemical name + known development codenames that
# name the target molecules only by internal code (missed by plain-text queries).
QUERIES = [
    "dimethyltryptamine", "5-MeO-DMT", "ayahuasca",
    "N,N-dimethyltryptamine", "mebufotenin",
    "BPL-003", "GH001", "GH002", "SPL026",
]

# Codename -> molecule family. Used both to KEEP codename-only trials and to tag them.
CODENAMES = {
    "5-MeO-DMT": ["gh001", "gh 001", "gh-001", "gh002", "gh 002", "gh-002",
                   "bpl-003", "bpl003", "bpl 003", "mebufotenin", "mebufotenine"],
    "N,N-DMT": ["spl026", "spl-026", "spl 026", "spl028", "spl-028", "spl 028",
                 "dmt fumarate", "cyb004", "cyb-004"],
}

source_notes = []

def fetch_ctg(term):
    """Fetch all studies for a query term, paginating."""
    studies = []
    token = None
    while True:
        params = {
            "query.term": term,
            "pageSize": 100,
            "format": "json",
        }
        if token:
            params["pageToken"] = token
        for attempt in range(4):
            try:
                r = S.get(CTG, params=params, timeout=40)
                r.raise_for_status()
                break
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        data = r.json()
        batch = data.get("studies", [])
        studies.extend(batch)
        token = data.get("nextPageToken")
        if not token:
            break
        time.sleep(0.3)
    return studies

def g(d, *path, default=None):
    cur = d
    for p in path:
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return default
        if cur is None:
            return default
    return cur

def _strip_psilocybin_names(t):
    # Remove psilocybin/psilocin/bufotenin IUPAC fragments so the embedded
    # "N,N-dimethyltryptamine" substring does not read as a DMT signal.
    return re.sub(r"\d*-?(phosphoryloxy|phosphoroyloxy|phosphoryl|hydroxy|acetoxy)-n,?\s*n-?dimethyltryptamine", " ", t)

def genuine_signal(text):
    """True if the text genuinely references DMT / 5-MeO-DMT / ayahuasca
    (not merely psilocybin's chemical name), or a known target codename."""
    t = text.lower()
    if "ayahuasca" in t or "banisteriopsis" in t or "hoasca" in t:
        return True
    if re.search(r"5-?methoxy|5-?meo-?dmt|mebufotenin", t):
        return True
    for names in CODENAMES.values():
        if any(c in t for c in names):
            return True
    stripped = _strip_psilocybin_names(t)
    if re.search(r"\bdmt\b|\bn,?\s*n-?dimethyltryptamine\b", stripped):
        return True
    if "dimethyltryptamine" in stripped:
        return True
    return False

def molecule_tag(text):
    t = text.lower()
    # codename match first
    code_5meo = any(c in t for c in CODENAMES["5-MeO-DMT"])
    code_nndmt = any(c in t for c in CODENAMES["N,N-DMT"])
    has_aya = "ayahuasca" in t or "banisteriopsis" in t or "hoasca" in t
    has_5meo = code_5meo or bool(re.search(r"5-?me?o-?dmt|5-methoxy|methoxy-n,n|o-methyl-bufotenin|mebufotenin", t))
    stripped = _strip_psilocybin_names(t)
    has_nndmt = code_nndmt or (bool(re.search(r"\bn,?\s*n-?dimethyltryptamine\b|\bdmt\b|dimethyltryptamine", stripped)) and not has_5meo)
    # ayahuasca inherently contains DMT, so an ayahuasca trial is tagged ayahuasca
    if has_aya and not has_5meo:
        return "ayahuasca"
    # genuine multi-molecule study
    if has_5meo and has_nndmt:
        return "combination"
    if has_aya and has_5meo:
        return "combination"
    if has_5meo:
        return "5-MeO-DMT"
    if has_nndmt:
        return "N,N-DMT"
    return "other"

def normalize(study):
    ps = study.get("protocolSection", {})
    idm = ps.get("identificationModule", {})
    nct = idm.get("nctId")
    brief_title = idm.get("briefTitle", "")
    official = idm.get("officialTitle", "")
    title = brief_title or official
    status = g(ps, "statusModule", "overallStatus", default="")
    start_date = g(ps, "statusModule", "startDateStruct", "date", default="")
    comp_date = (g(ps, "statusModule", "completionDateStruct", "date", default="")
                 or g(ps, "statusModule", "primaryCompletionDateStruct", "date", default=""))
    design = ps.get("designModule", {})
    phases = g(design, "phaseList", "phases", default=[]) or design.get("phases", [])
    if isinstance(phases, list):
        phase = ", ".join(phases) if phases else "N/A"
    else:
        phase = str(phases)
    if phase in ("NA", "", "None"):
        phase = "N/A"
    study_type = design.get("studyType", "")
    enrollment = g(design, "enrollmentInfo", "count", default=None)
    conds = g(ps, "conditionsModule", "conditions", default=[]) or []
    # interventions
    interventions = []
    for iv in g(ps, "armsInterventionsModule", "interventions", default=[]) or []:
        name = iv.get("name", "")
        itype = iv.get("type", "")
        if name:
            interventions.append(f"{itype}: {name}" if itype else name)
    # sponsor / collaborators
    sponsor = g(ps, "sponsorCollaboratorsModule", "leadSponsor", "name", default="")
    collaborators = [c.get("name", "") for c in (g(ps, "sponsorCollaboratorsModule", "collaborators", default=[]) or [])]
    # locations -> countries
    countries = set()
    for loc in g(ps, "contactsLocationsModule", "locations", default=[]) or []:
        c = loc.get("country")
        if c:
            countries.add(c)
    # results
    has_results = study.get("hasResults", False)
    summary = g(ps, "descriptionModule", "briefSummary", default="") or ""
    # molecule tag - prioritise title + interventions + conditions (what the trial
    # actually administers); fall back to the summary only if those are inconclusive,
    # so a passing background mention (e.g. "5-MeO-DMT rat autoradiography") can't flip the tag.
    primary = " ".join([brief_title, official, " ".join(interventions), " ".join(conds)])
    mol = molecule_tag(primary)
    if mol == "other":
        mol = molecule_tag(primary + " " + summary)
    return {
        "nct_id": nct,
        "title": title,
        "status": status,
        "phase": phase,
        "study_type": study_type,
        "conditions": conds,
        "interventions": interventions,
        "sponsor": sponsor,
        "collaborators": [c for c in collaborators if c],
        "enrollment": enrollment,
        "start_date": start_date,
        "completion_date": comp_date,
        "countries": sorted(countries),
        "has_results": bool(has_results),
        "molecule_tag": mol,
        "summary": summary,
        "url": f"https://clinicaltrials.gov/study/{nct}" if nct else "",
    }

# ---- 1. ClinicalTrials.gov ----
raw = {}
for q in QUERIES:
    try:
        st = fetch_ctg(q)
        print(f"CTG '{q}': {len(st)} studies", file=sys.stderr)
        for s in st:
            nct = g(s, "protocolSection", "identificationModule", "nctId")
            if nct and nct not in raw:
                raw[nct] = s
    except Exception as e:
        source_notes.append(f"ClinicalTrials.gov query '{q}' FAILED: {e}")
        print(f"CTG '{q}' FAILED: {e}", file=sys.stderr)

trials = [normalize(s) for s in raw.values()]

# Drop false positives: records that matched a query only because psilocybin/
# psilocin's IUPAC name embeds "N,N-dimethyltryptamine", with no real target molecule.
def is_relevant(t):
    blob = t["title"] + " " + " ".join(t["interventions"]) + " " + " ".join(t["conditions"]) + " " + t["summary"]
    return genuine_signal(blob)

before = len(trials)
dropped_ncts = [t["nct_id"] for t in trials if not is_relevant(t)]
trials = [t for t in trials if is_relevant(t)]
dropped = before - len(trials)
if dropped:
    source_notes.append(f"Dropped {dropped} CTG false-positives (matched a search term via psilocybin/psilocin chemical naming, no actual DMT/5-MeO-DMT/ayahuasca): {', '.join(dropped_ncts)}.")

# sort by start_date ascending (empty dates last)
def sort_key(t):
    d = t.get("start_date") or ""
    # normalize YYYY-MM or YYYY-MM-DD
    return (d == "", d)
trials.sort(key=sort_key)

# ---- 2. WHO ICTRP ----
ictrp_ok = False
try:
    # ICTRP public search portal - try the trialsearch endpoint
    r = S.get("https://trialsearch.who.int/api/Trial", params={"searchText": "ayahuasca"}, timeout=25)
    if r.status_code == 200 and r.text.strip().startswith(("{", "[")):
        ictrp_ok = True
        source_notes.append("WHO ICTRP: endpoint returned data (parsing attempted).")
    else:
        source_notes.append(f"WHO ICTRP: no usable JSON endpoint (HTTP {r.status_code}); skipped. Portal requires interactive session/export.")
except Exception as e:
    source_notes.append(f"WHO ICTRP: unreachable without key/session ({type(e).__name__}); skipped.")

# ---- 3. Europe PMC preprints ----
preprints = []
try:
    epmc = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    query = '(dimethyltryptamine OR ayahuasca OR "5-MeO-DMT") AND SRC:PPR'
    cursor = "*"
    seen_pp = set()
    while True:
        params = {"query": query, "format": "json", "pageSize": 100, "cursorMark": cursor, "resultType": "core"}
        r = S.get(epmc, params=params, timeout=40)
        r.raise_for_status()
        data = r.json()
        results = g(data, "resultList", "result", default=[]) or []
        if not results:
            break
        for res in results:
            doi = res.get("doi", "")
            pid = res.get("id", "") or doi
            if pid in seen_pp:
                continue
            seen_pp.add(pid)
            authct = res.get("authorString", "")
            year = res.get("pubYear", "")
            server = res.get("publisher", "") or g(res, "bookOrReportDetails", "publisher", default="") or "preprint server"
            url = ""
            for u in g(res, "fullTextUrlList", "fullTextUrl", default=[]) or []:
                if u.get("url"):
                    url = u["url"]; break
            if not url and doi:
                url = f"https://doi.org/{doi}"
            preprints.append({
                "title": res.get("title", ""),
                "authors": authct,
                "year": year,
                "server": server,
                "doi": doi,
                "url": url,
            })
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.3)
    print(f"Europe PMC preprints: {len(preprints)}", file=sys.stderr)
    source_notes.append(f"Europe PMC preprints (SRC:PPR): {len(preprints)} records.")
except Exception as e:
    source_notes.append(f"Europe PMC preprints FAILED: {e}")

# ---- counts ----
from collections import Counter
def top_counter(vals, n=None):
    c = Counter(vals)
    items = c.most_common(n)
    return {k: v for k, v in items}

counts = {
    "total_trials": len(trials),
    "by_status": top_counter([t["status"] for t in trials]),
    "by_phase": top_counter([t["phase"] for t in trials]),
    "by_molecule_tag": top_counter([t["molecule_tag"] for t in trials]),
    "by_sponsor_top15": top_counter([t["sponsor"] for t in trials if t["sponsor"]], 15),
    "total_preprints": len(preprints),
}

out = {
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "source_notes": " | ".join(source_notes),
    "counts": counts,
    "trials": trials,
    "preprints": preprints,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\nWROTE {OUT}", file=sys.stderr)
print(f"Trials: {len(trials)} | Preprints: {len(preprints)}", file=sys.stderr)
print("Status:", counts["by_status"], file=sys.stderr)
print("Phase:", counts["by_phase"], file=sys.stderr)
print("Molecule:", counts["by_molecule_tag"], file=sys.stderr)
