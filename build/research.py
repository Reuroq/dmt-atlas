"""research.py — the /research/ section generator (the peer-reviewed + patents + trials layer).

Reads the four corpora in data/research/ (built by the harvest agents) and emits a crawlable,
citation-dense research wing for the Atlas:
  /research/                 hub — the landscape at a glance (stats table + timeline highlights)
  /research/history.html     cited milestone timeline (1931 → present) + myths-vs-evidence
  /research/studies.html     filterable index of the peer-reviewed literature (DOI/PubMed links)
  /research/trials.html      registered clinical trials (NCT links) + preprints
  /research/patents.html     full DMT/5-MeO-DMT patent landscape (complements /who-owns-dmt.html)

Reuses generate.py's page()/helpers so the shell, nav, footer, and schema match the rest of the site.
Every page carries outbound links to the primary record (the WinNet 'external links' win) and honest
epistemic framing. NO how-to content — bibliographic metadata and abstracts only.

    python build/research.py        (run AFTER build/generate.py, or call build_research() from it)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import generate as G  # page(), esc, slug, crumbs, faq_ld, crumb_ld, faq_block, BASE, TODAY

RES = G.ROOT / "data" / "research"
esc, slug, BASE, TODAY = G.esc, G.slug, G.BASE, G.TODAY


# The DMT / tryptamine-psychedelic family. The literature aggregation deliberately cast a wide
# net (OpenAlex relevance pulls in adjacent 5-HT2A / psilocybin work); for an honest "DMT research"
# headline we keep only records that actually name the DMT family in title/abstract/venue.
FAMILY = re.compile(
    r"dimethyltryptamine|dimethyl-tryptamine|\bn,?\s*n-?dmt\b|\bdmt\b|ayahuasca|banisteriopsis|"
    r"caapi|hoasca|yag[eé]|5-meo-dmt|5-methoxy-n,n|bufotenin|indolethylamine|\binmt\b", re.I)


def _dmt_family(r) -> bool:
    blob = " ".join(str(r.get(k) or "") for k in ("title", "abstract", "venue"))
    return bool(FAMILY.search(blob))


def _pretty(s: str) -> str:
    """Registry ALL-CAPS enums → readable (PHASE1, PHASE2 → Phase 1, Phase 2; ACTIVE_NOT_RECRUITING → Active, not recruiting)."""
    s = str(s or "").strip()
    if not s:
        return ""
    s = s.replace("PHASE1", "Phase 1").replace("PHASE2", "Phase 2").replace("PHASE3", "Phase 3")
    s = s.replace("EARLY_Phase 1", "Early Phase 1").replace("EARLY Phase 1", "Early Phase 1")
    if s.isupper() or "_" in s:
        s = s.replace("_", " ").capitalize()
    return s


def load(name: str):
    p = RES / name
    if not p.exists():
        print(f"  (research: missing {name} — skipping its page)")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  (research: {name} unreadable: {e})")
        return None


def _year(v):
    m = re.search(r"(1[89]\d\d|20\d\d)", str(v or ""))
    return int(m.group(1)) if m else None


def _decades(records, yearkey="year"):
    out = {}
    for r in records:
        y = _year(r.get(yearkey))
        if y:
            d = (y // 10) * 10
            out[d] = out.get(d, 0) + 1
    return dict(sorted(out.items()))


FILTER_JS = """<script>
(function(){var q=document.getElementById('rfilter');if(!q)return;
var rows=[].slice.call(document.querySelectorAll('tbody tr'));
var count=document.getElementById('rcount');
function apply(){var v=q.value.toLowerCase().trim();var n=0;
rows.forEach(function(tr){var hit=!v||tr.textContent.toLowerCase().indexOf(v)>-1;
tr.style.display=hit?'':'none';if(hit)n++;});
if(count)count.textContent=n;}
q.addEventListener('input',apply);})();
</script>"""

FILTER_BOX = ('<div style="margin:18px 0"><input id="rfilter" type="search" '
              'placeholder="Filter by title, author, year, keyword…" '
              'style="width:100%;max-width:520px;padding:11px 14px;border-radius:10px;'
              'border:1px solid rgba(243,201,105,.28);background:rgba(255,255,255,.04);'
              'color:inherit;font-size:15px"/> '
              '<span class="src">Showing <b id="rcount">{n}</b> of {n}</span></div>')


def dataset_ld(name, desc, url, n):
    return {"@context": "https://schema.org", "@type": "Dataset", "name": name,
            "description": desc, "url": url, "creator": {"@type": "Organization", "name": "The DMT Atlas"},
            "keywords": ["DMT", "N,N-dimethyltryptamine", "psychedelic research"],
            "measurementTechnique": "bibliographic aggregation", "size": f"{n} records"}


# ══════════════════════════════════════════ history / timeline
def history_page(hist):
    if not hist:
        return None
    mils = sorted(hist.get("milestones", []), key=lambda m: _year(m.get("year")) or 9999)
    STATUS_CLS = {"established": "epi-study", "historical": "phase", "contested": "epi-contested",
                  "unproven": "epi-anecdote"}
    blocks = ""
    for m in mils:
        cit = m.get("citation") or {}
        url = cit.get("doi_or_url") or ""
        who = f"{cit.get('author','')} — <i>{esc(cit.get('work',''))}</i> ({cit.get('year','')})".strip(" —")
        citelink = (f'<a href="{esc(url)}" rel="noopener" target="_blank">{who} ↗</a>'
                    if url else who) if (cit.get("author") or cit.get("work")) else ""
        st = m.get("proven_status", "")
        badge = f'<span class="badge {STATUS_CLS.get(st,"epi-folk")}">{esc(st)}</span>' if st else ""
        who_line = " · ".join(x for x in (esc(m.get("who", "")), esc(m.get("institution", ""))) if x)
        blocks += f"""<section class="phase-block" id="y{esc(m.get('year',''))}-{slug(m.get('title',''))}">
<h2>{esc(m.get('year',''))} — {esc(m.get('title',''))}</h2>
{f'<div class="badges" style="margin:0 0 8px">{badge}</div>' if badge else ''}
{f'<p class="aka">{who_line}</p>' if who_line else ''}
<p>{esc(m.get('what_happened',''))}</p>
{f'<p><b>Why it matters:</b> {esc(m.get("significance",""))}</p>' if m.get('significance') else ''}
{f'<p class="src">Source: {citelink}</p>' if citelink else ''}</section>"""

    myths = hist.get("myths_vs_evidence", [])
    myth_rows = ""
    for mv in myths:
        claim = esc(mv.get("claim") or mv.get("myth") or mv.get("popular_form") or "")
        status = esc(mv.get("status") or mv.get("verdict") or "")
        note = esc(mv.get("reality") or mv.get("note") or mv.get("evidence") or mv.get("detail") or "")
        myth_rows += f'<tr><td>{claim}</td><td class="stat">{status}</td><td>{note}</td></tr>'
    myth_block = ""
    if myth_rows:
        myth_block = (f'<div class="section"><h2><span class="h-mark">✦</span>Popular claims vs. the evidence</h2>'
                      f'<p>Widely-repeated statements about DMT, each with its real evidentiary status. '
                      f'Where a claim is unproven, it is labeled unproven — not dismissed and not endorsed.</p>'
                      f'<div class="tablewrap"><table class="evidence"><thead><tr><th>Claim</th>'
                      f'<th>Status</th><th>What the evidence actually shows</th></tr></thead>'
                      f'<tbody>{myth_rows}</tbody></table></div></div>')

    researchers = hist.get("key_researchers", [])
    r_chips = "".join(f'<div class="rail-box"><h4>{esc(r.get("name",""))}</h4>'
                      f'<div class="kv">{esc(r.get("era",""))} · {esc(r.get("institution",""))}<br/>'
                      f'{esc(r.get("contribution",""))}</div></div>' for r in researchers[:12])

    body = f"""<main class="wrap">
{G.crumbs(("Research", "/research/"), ("History", ""))}
<p class="kicker">RESEARCH · THE DMT ATLAS</p>
<h1 class="page-title">A History of DMT Science</h1>
<p class="lede">From the first synthesis in 1931 to today's clinical renaissance — the landmark studies, the
researchers, and the discoveries that built what is actually known about N,N-dimethyltryptamine. Every
milestone names its source; every unproven claim is labeled as such.</p>
<div class="dossier-grid">
<article class="dossier-main">{blocks}{myth_block}</article>
<aside class="rail"><div class="rail-box"><h4>Jump to</h4><div class="chiprow">
<a class="chip" href="/research/">Research hub</a><a class="chip" href="/research/studies.html">All studies</a>
<a class="chip" href="/research/trials.html">Clinical trials</a><a class="chip" href="/research/patents.html">Patents</a>
</div></div>{r_chips}</aside>
</div></main>"""
    faqs = [
        ("When was DMT discovered?",
         "N,N-dimethyltryptamine was first chemically synthesized in 1931 by the chemist Richard Manske. "
         "Its psychoactivity in humans was not documented until Stephen Szára's self-experiments in 1956."),
        ("Does the human brain make DMT?",
         "Trace endogenous DMT has been detected in mammalian tissue, and the synthesizing enzyme (INMT) is "
         "present in the body. But the popular claim that the pineal gland releases a flood of DMT at birth or "
         "death is not demonstrated in humans and remains unproven."),
        ("Is DMT being researched today?",
         "Yes — after decades of prohibition-era dormancy, DMT is in active clinical trials for depression and "
         "other conditions at Imperial College London, Johns Hopkins, and several biotech companies. See the "
         "clinical-trials and studies pages for the full record."),
    ]
    ld = [G.crumb_ld([("Atlas", "/"), ("Research", "/research/"), ("History", "/research/history.html")]),
          G.faq_ld(faqs),
          {"@context": "https://schema.org", "@type": "Article",
           "headline": "A History of DMT Science", "about": "N,N-dimethyltryptamine research",
           "url": BASE + "/research/history.html", "author": {"@type": "Organization", "name": "The DMT Atlas"}}]
    # append FAQ visibly too
    G.page("research/history.html", "A History of DMT Science — 1931 to Today · The DMT Atlas",
           "The landmark studies and discoveries of DMT science, from Manske's 1931 synthesis and Szára's 1956 "
           "human trials through Strassman's UNM studies and today's clinical renaissance — cited, with unproven "
           "claims labeled.", body + "", jsonld=ld, active="Research")
    return len(mils)


# ══════════════════════════════════════════ studies (peer-reviewed literature)
def studies_page(lit):
    if not lit:
        return None
    # honest DMT/ayahuasca-family core (the aggregation cast wider into adjacent psychedelic work)
    recs = [r for r in lit.get("records", []) if _dmt_family(r)]
    ranked = sorted(recs, key=lambda r: -(r.get("cited_by_count") or 0))
    dec = _decades(recs)
    dec_row = " · ".join(f"{d}s: <b>{n}</b>" for d, n in dec.items())
    earliest = min((_year(r.get("year")) for r in recs if _year(r.get("year"))), default=None)

    rows = ""
    for r in ranked:
        doi = r.get("doi") or ""
        pmid = r.get("pmid") or ""
        url = r.get("url") or (f"https://doi.org/{doi}" if doi else
                               (f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""))
        title = esc(r.get("title", "(untitled)"))
        tcell = f'<a href="{esc(url)}" rel="noopener" target="_blank">{title} ↗</a>' if url else title
        authors = esc(", ".join((r.get("authors") or [])[:3]) + (" et al." if len(r.get("authors") or []) > 3 else ""))
        cb = r.get("cited_by_count")
        rows += (f'<tr><td>{tcell}</td><td>{authors}</td><td class="stat">{esc(r.get("year",""))}</td>'
                 f'<td>{esc(r.get("venue",""))}</td><td class="stat">{cb if cb is not None else ""}</td></tr>')

    n = len(recs)
    body = f"""<main class="wrap">
{G.crumbs(("Research", "/research/"), ("Studies", ""))}
<p class="kicker">RESEARCH · THE DMT ATLAS</p>
<h1 class="page-title">The DMT Research Literature</h1>
<p class="lede">Every peer-reviewed paper we could find on DMT and ayahuasca — <b>{n:,}</b> studies
{f'going back to {earliest}' if earliest else ''}, aggregated from PubMed, Europe PMC, and OpenAlex,
deduplicated, and sorted by citation impact. Each links to the primary record. This is a bibliographic
index, not medical advice.</p>
<p class="src">By decade — {dec_row}</p>
{FILTER_BOX.format(n=n)}
<div class="tablewrap"><table class="evidence">
<thead><tr><th>Title</th><th>Authors</th><th>Year</th><th>Venue</th><th>Cited by</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="src" style="margin-top:16px">Sources: NIH PubMed / NCBI E-utilities, Europe PMC, OpenAlex —
public bibliographic APIs. Citation counts via OpenAlex. Verify each record at its linked source.</p>
</main>{FILTER_JS}"""
    faqs = [
        ("How many scientific studies are there on DMT?",
         f"This index catalogs {n} peer-reviewed papers on DMT and ayahuasca{f' dating back to {earliest}' if earliest else ''}, "
         "aggregated from PubMed, Europe PMC, and OpenAlex. The count grows as new research is published."),
        ("What is the most-cited DMT study?",
         "The table is sorted by citation count, so the most-cited papers appear first — historically these include "
         "Rick Strassman's 1990s human-dosing studies and the modern Imperial College and Johns Hopkins survey work."),
    ]
    ld = [G.crumb_ld([("Atlas", "/"), ("Research", "/research/"), ("Studies", "/research/studies.html")]),
          G.faq_ld(faqs),
          dataset_ld("The DMT research literature index",
                     "Deduplicated bibliographic index of peer-reviewed DMT and ayahuasca research.",
                     BASE + "/research/studies.html", n)]
    G.page("research/studies.html", f"DMT Research: {n:,} Peer-Reviewed Studies, Indexed · The DMT Atlas",
           f"A searchable index of {n:,} peer-reviewed DMT and ayahuasca studies from PubMed, Europe PMC and OpenAlex, "
           "sorted by citation impact and linked to the primary record.", body, jsonld=ld, active="Research")
    return n


# ══════════════════════════════════════════ trials
def trials_page(tr):
    if not tr:
        return None
    trials = tr.get("trials", [])
    ranked = sorted(trials, key=lambda t: _year(t.get("start_date")) or 0, reverse=True)
    rows = ""
    for t in ranked:
        nct = t.get("nct_id", "")
        url = t.get("url") or (f"https://clinicaltrials.gov/study/{nct}" if nct else "")
        title = esc(t.get("title", "(untitled)"))
        tcell = f'<a href="{esc(url)}" rel="noopener" target="_blank">{title} ↗</a>' if url else title
        conds = esc(", ".join((t.get("conditions") or [])[:3]))
        rows += (f'<tr><td>{tcell}</td><td>{esc(_pretty(t.get("phase","")))}</td><td>{esc(_pretty(t.get("status","")))}</td>'
                 f'<td>{conds}</td><td>{esc(t.get("sponsor",""))}</td>'
                 f'<td class="stat">{esc((t.get("start_date") or "")[:7])}</td></tr>')
    preprints = tr.get("preprints", [])
    pp = ""
    for p in preprints[:80]:
        url = p.get("url") or (f'https://doi.org/{p.get("doi")}' if p.get("doi") else "")
        t = esc(p.get("title", ""))
        pp += (f'<div class="src-item"><h3>{f"<a href=\"{esc(url)}\" rel=\"noopener\" target=\"_blank\">{t} ↗</a>" if url else t}</h3>'
               f'<div class="who">{esc(", ".join((p.get("authors") or [])[:3]))} · {esc(p.get("server",""))} · {esc(p.get("year",""))}</div></div>')
    pp_block = (f'<div class="section"><h2><span class="h-mark">✦</span>Preprints</h2>'
                f'<p>Recent non-peer-reviewed preprints (bioRxiv/medRxiv/PsyArXiv). Treat as provisional.</p>{pp}</div>'
                if pp else "")
    n = len(trials)
    body = f"""<main class="wrap">
{G.crumbs(("Research", "/research/"), ("Clinical trials", ""))}
<p class="kicker">RESEARCH · THE DMT ATLAS</p>
<h1 class="page-title">DMT Clinical Trials</h1>
<p class="lede">Every registered clinical trial of DMT, 5-MeO-DMT, and ayahuasca we could find — <b>{n}</b>
studies from ClinicalTrials.gov and other registries, newest first. Status, phase, condition, and sponsor
for each, linked to the official registry entry.</p>
{FILTER_BOX.format(n=n)}
<div class="tablewrap"><table class="evidence">
<thead><tr><th>Trial</th><th>Phase</th><th>Status</th><th>Condition</th><th>Sponsor</th><th>Start</th></tr></thead>
<tbody>{rows}</tbody></table></div>
{pp_block}
<p class="src" style="margin-top:16px">Source: ClinicalTrials.gov API v2 and public trial registries. Registry
records are informational; a listed trial is not an endorsement or an offer of treatment.</p>
</main>{FILTER_JS}"""
    faqs = [
        ("Is DMT in clinical trials?",
         f"Yes. This page indexes {n} registered trials of DMT, 5-MeO-DMT, and ayahuasca — most investigating "
         "depression and other mental-health conditions, at institutions including Imperial College London and "
         "several biotech sponsors."),
        ("Can I join a DMT study?",
         "Trial eligibility, locations, and recruitment status are listed on each trial's official ClinicalTrials.gov "
         "page (linked here). The DMT Atlas is an information archive and cannot enroll anyone or provide access to any substance."),
    ]
    ld = [G.crumb_ld([("Atlas", "/"), ("Research", "/research/"), ("Clinical trials", "/research/trials.html")]),
          G.faq_ld(faqs),
          dataset_ld("DMT clinical trials index", "Registered clinical trials of DMT, 5-MeO-DMT and ayahuasca.",
                     BASE + "/research/trials.html", n)]
    G.page("research/trials.html", f"DMT Clinical Trials — {n} Registered Studies · The DMT Atlas",
           f"A searchable index of {n} registered DMT, 5-MeO-DMT and ayahuasca clinical trials — phase, status, "
           "condition and sponsor, linked to ClinicalTrials.gov.", body, jsonld=ld, active="Research")
    return n


# ══════════════════════════════════════════ patents (full landscape; complements /who-owns-dmt.html)
def patents_page(pat):
    if not pat:
        return None
    recs = pat.get("records", [])
    def pdate(r):
        return _year(r.get("filing_date") or r.get("publication_date")) or 0
    ranked = sorted(recs, key=pdate, reverse=True)
    rows = ""
    for r in ranked:
        url = r.get("url") or ""
        num = esc(r.get("patent_number", ""))
        numcell = f'<a href="{esc(url)}" rel="nofollow noopener" target="_blank">{num} ↗</a>' if url else num
        rows += (f'<tr><td>{esc(r.get("assignee",""))}</td><td>{numcell}</td>'
                 f'<td>{esc(r.get("title",""))}</td><td>{esc(r.get("molecule_tag",""))}</td>'
                 f'<td>{esc(r.get("status",""))}</td>'
                 f'<td class="stat">{esc((r.get("filing_date") or r.get("publication_date") or "")[:7])}</td></tr>')
    n = len(recs)
    body = f"""<main class="wrap">
{G.crumbs(("Research", "/research/"), ("Patents", ""))}
<p class="kicker">RESEARCH · THE DMT ATLAS</p>
<h1 class="page-title">The DMT Patent Landscape</h1>
<p class="lede">You cannot patent DMT itself — the molecule is public domain. But <b>{n}</b> patents and
applications try to own the periphery: formulations, salts, deuterated analogs, dose regimens, devices, and
uses. This is the full record; for what it all <em>means</em>, start with
<a href="/who-owns-dmt.html">Who Owns the Molecule?</a></p>
{FILTER_BOX.format(n=n)}
<div class="tablewrap"><table class="evidence">
<thead><tr><th>Assignee</th><th>Patent / application</th><th>Title</th><th>Molecule</th><th>Status</th><th>Filed</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="src" style="margin-top:16px">Sources: PatentsView (USPTO) and Google Patents public records. Bibliographic
metadata only — claim types and status, never enabling chemistry. Verify each at the linked primary record.</p>
</main>{FILTER_JS}"""
    faqs = [
        ("How many DMT patents are there?",
         f"This index catalogs {n} DMT-related patents and applications. Note that none claim the molecule itself "
         "(which is public domain) — they claim formulations, salts, analogs, doses, devices, or uses."),
        ("Who holds the most DMT patents?",
         "The largest DMT-specific portfolio belongs to Cybin (which absorbed Small Pharma). See "
         "Who Owns the Molecule? for the key players and the prior-art fights."),
    ]
    ld = [G.crumb_ld([("Atlas", "/"), ("Research", "/research/"), ("Patents", "/research/patents.html")]),
          G.faq_ld(faqs),
          dataset_ld("DMT patent landscape index", "DMT and 5-MeO-DMT related patents and applications.",
                     BASE + "/research/patents.html", n)]
    G.page("research/patents.html", f"The DMT Patent Landscape — {n} Filings, Indexed · The DMT Atlas",
           f"A searchable index of {n} DMT and 5-MeO-DMT patents and applications — assignee, claim, molecule and "
           "status, linked to the public record. IP literacy, no chemistry.", body, jsonld=ld, active="Research")
    return n


# ══════════════════════════════════════════ hub
def research_hub(counts, earliest):
    tiles = [
        ("Peer-reviewed studies", "/research/studies.html", counts.get("studies"),
         "Every DMT & ayahuasca paper, deduplicated and citation-ranked, linked to PubMed / DOI."),
        ("Clinical trials", "/research/trials.html", counts.get("trials"),
         "Registered DMT, 5-MeO-DMT & ayahuasca trials — phase, status, sponsor, linked to the registry."),
        ("Patent landscape", "/research/patents.html", counts.get("patents"),
         "Who is trying to own the periphery of a public-domain molecule — the full filing record."),
        ("History of the science", "/research/history.html", counts.get("history"),
         "1931 to today — the landmark discoveries, cited, with the popular myths labeled."),
    ]
    cards = "".join(
        f'<a class="card" style="--card-accent:var(--c-source)" href="{href}"><h3>{esc(t)}</h3><p>{esc(d)}</p>'
        f'<div class="meta">{f"<span class=\"count-pill\">{c} entries</span>" if c else ""}</div></a>'
        for t, href, c, d in tiles)
    statrow = "".join(f'<div class="stat-pill"><b>{v}</b><span>{k}</span></div>'
                      for k, v in (("studies", counts.get("studies")), ("trials", counts.get("trials")),
                                   ("patents", counts.get("patents")),
                                   ("earliest paper", earliest)) if v)
    body = f"""<main class="wrap">
{G.crumbs(("Research", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">The Research Layer</h1>
<p class="lede">Beneath the map of what people <em>report</em> sits the record of what has been <em>studied</em>.
This is the full scientific and legal footprint of DMT — every peer-reviewed paper, every registered clinical
trial, every patent, and the cited history that connects them — aggregated from public research databases and
linked to the primary source so you can verify rather than trust.</p>
<div class="stats-strip" style="margin:20px 0 8px">{statrow}</div>
<div class="grid">{cards}</div>
<div class="section" style="margin-top:30px"><h2><span class="h-mark">✦</span>How this was built</h2>
<p>The studies index aggregates <a href="https://pubmed.ncbi.nlm.nih.gov/" rel="noopener" target="_blank">PubMed</a>,
<a href="https://europepmc.org/" rel="noopener" target="_blank">Europe PMC</a>, and
<a href="https://openalex.org/" rel="noopener" target="_blank">OpenAlex</a>; trials come from
<a href="https://clinicaltrials.gov/" rel="noopener" target="_blank">ClinicalTrials.gov</a>; patents from
<a href="https://patentsview.org/" rel="noopener" target="_blank">PatentsView</a> and
<a href="https://patents.google.com/" rel="noopener" target="_blank">Google Patents</a>. Records are
deduplicated and topic-filtered. It is a bibliographic archive — abstracts and metadata only, never a guide to
obtaining, making, or taking anything.</p></div>
</main>"""
    ld = [G.crumb_ld([("Atlas", "/"), ("Research", "/research/")]),
          {"@context": "https://schema.org", "@type": "CollectionPage",
           "name": "The DMT Atlas — Research Layer", "url": BASE + "/research/",
           "description": "The full scientific and legal record of DMT: studies, clinical trials, patents, and history."}]
    G.page("research/index.html", "DMT Research — Studies, Trials, Patents & History · The DMT Atlas",
           "The complete scientific and legal record of DMT: every peer-reviewed study, registered clinical trial, "
           "and patent, plus the cited history — aggregated from public databases and linked to the primary source.",
           body, jsonld=ld, active="Research")


def build_research():
    lit = load("literature.json")
    tr = load("trials.json")
    pat = load("patents.json")
    hist = load("history.json")
    counts, earliest = {}, None
    if lit:
        core = [r for r in lit.get("records", []) if _dmt_family(r)]
        earliest = min((_year(r.get("year")) for r in core if _year(r.get("year"))), default=None)
        counts["studies"] = studies_page(lit)
    if tr:
        counts["trials"] = trials_page(tr)
    if pat:
        counts["patents"] = patents_page(pat)
    if hist:
        counts["history"] = history_page(hist)
    research_hub(counts, earliest)
    urls = ["/research/"]
    if lit:
        urls.append("/research/studies.html")
    if tr:
        urls.append("/research/trials.html")
    if pat:
        urls.append("/research/patents.html")
    if hist:
        urls.append("/research/history.html")
    print(f"  research: {counts}")
    return [BASE + u for u in urls]


if __name__ == "__main__":
    build_research()
