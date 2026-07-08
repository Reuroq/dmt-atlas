"""generate.py — static multi-page atlas generator (the SPA-death fix + redesign).

Reads data/atlas.json, writes the whole crawlable site:
  index.html                    landing (hero, stats, section cards, charter)
  explore.html                  the interactive 3-lens SPA (constellation/map/journey)
  entities/  realms/  geometry/  motifs/     index + one page per node
  journey.html  themes.html  evidence.html  library.html
  sitemap.xml
Every child page: breadcrumbs, cited sources, cross-links, FAQ JSON-LD.
Charter honesty on every page. NO how-to content anywhere, ever.

    python build/generate.py            (from repo root or anywhere)
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "atlas.json").read_text(encoding="utf-8"))
BASE = "https://dmtatlas.com"
GA = "G-BKTCYLB89C"
TODAY = date.today().isoformat()

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = {s["key"]: s for s in DATA["sources"]}
META = DATA.get("meta", {})

FAVICON = ("data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Ctext x='16' y='24' font-size='24' text-anchor='middle' fill='%23f3c969'%3E%E2%9C%A6%3C/text%3E%3C/svg%3E")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def pct_of(freq: str):
    """First percentage in a frequency string, for the prevalence bar."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", str(freq or ""))
    if not m:
        return None
    v = float(m.group(1))
    return v if 0 < v <= 100 else None


NAV = [
    ("Entities", "/entities/"), ("Realms", "/realms/"), ("Geometry", "/geometry/"),
    ("Motifs", "/motifs/"), ("Journey", "/journey.html"), ("Themes", "/themes.html"),
    ("Evidence", "/evidence.html"), ("Library", "/library.html"),
]


def header(active: str = "") -> str:
    links = "".join(
        f'<a href="{href}"{" class=\"active\"" if label == active else ""}>{label}</a>'
        for label, href in NAV if not (label == "Motifs" and not DATA.get("motifs")))
    return f"""<header class="site-head"><div class="head-inner">
  <a class="brand" href="/"><span class="mark">✦</span><b>The DMT Atlas</b></a>
  <nav class="site-nav">{links}<a class="cta" href="/explore.html">✦ Explore</a></nav>
</div></header>"""


FOOTER = f"""<footer class="site-foot"><div class="foot-inner">
  <div><h4>The Atlas</h4><a href="/entities/">Entities</a><a href="/realms/">Realms</a>
    <a href="/geometry/">Geometry &amp; phenomena</a><a href="/journey.html">The Journey</a>
    <a href="/themes.html">Themes &amp; mechanics</a>{'<a href="/motifs/">Motifs &amp; events</a>' if DATA.get('motifs') else ''}</div>
  <div><h4>Grounding</h4><a href="/evidence.html">The evidence — by the numbers</a>
    <a href="/library.html">The library — every source</a><a href="/explore.html">Interactive explorer</a></div>
  <div><h4>Tools</h4><a href="/identify.html">What did I meet?</a>
    <a href="/questions.html">Questions from hyperspace</a><a href="/grounding.html">After the experience</a></div>
  <div><h4>What this is</h4><p>A cartography of what people <i>report</i> — every entry cited to who
    reported it. Not a claim these are literal places or beings, and never a guide to
    obtaining, making, or taking anything.</p></div>
</div>
<div class="foot-note"><b>If you or someone you know is struggling after an experience:</b>
Fireside Project (62-FIRESIDE), 988 Suicide &amp; Crisis Lifeline, Crisis Text Line (text HOME to 741741).
See <a href="/grounding.html">After the experience</a>. · © The DMT Atlas</div></footer>"""


def page(path: str, title: str, desc: str, body: str, jsonld: list | None = None,
         active: str = "", canonical: str | None = None) -> None:
    canonical = canonical or (BASE + "/" + path.replace("index.html", "").replace("\\", "/"))
    canonical = canonical.rstrip("/") + ("/" if path.endswith("index.html") and "/" in path else "")
    if path == "index.html":
        canonical = BASE + "/"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>'
                 for j in (jsonld or []))
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:type" content="article"/>
<link rel="icon" href="{FAVICON}"/>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA}');</script>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/site.css?v=3"/>
{ld}
</head>
<body>
<div class="cosmos" aria-hidden="true"></div>
{header(active)}
{body}
{FOOTER}
</body>
</html>"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"  wrote {path}")


def crumbs(*parts) -> str:
    items = ['<a href="/">Atlas</a>']
    for label, href in parts[:-1]:
        items.append(f'<a href="{href}">{esc(label)}</a>')
    items.append(f"<span>{esc(parts[-1][0])}</span>")
    return '<nav class="crumbs">' + '<span class="sep">✦</span>'.join(items) + "</nav>"


def cite_html(sources: list) -> str:
    """'What the sources say' — quotes with attribution links to the library."""
    out = []
    for s in sources or []:
        k = s.get("source_key")
        rec = SRC.get(k)
        who = f"{rec['author']} — <i>{esc(rec['work'])}</i> ({rec['year']})" if rec else esc(k)
        out.append(f"""<blockquote class="q">{esc(s.get('detail', ''))}
<footer>— <a href="/library.html#src-{slug(k or '')}">{who}</a></footer></blockquote>""")
    return "".join(out)


def faq_ld(qas: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}


def crumb_ld(parts: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                 "item": BASE + h} for i, (n, h) in enumerate(parts)]}


def faq_block(qas: list[tuple[str, str]]) -> str:
    if not qas:
        return ""
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qas)
    return f'<div class="faq"><h2 style="font-size:20px;color:var(--gold);margin-bottom:14px">Questions</h2>{items}</div>'


PHASES = sorted(DATA["phases"], key=lambda p: p["order"])
PHASE_BY_NUM = {p["order"]: p for p in PHASES}


def phase_chip(num) -> str:
    p = PHASE_BY_NUM.get(num)
    if not p:
        return ""
    return (f'<a class="chip" href="/journey.html#phase-{slug(p["name"])}">'
            f'Phase {p["order"]}: {esc(p["name"])}</a>')


def related_chips(kind: str, me: dict) -> str:
    """Same-phase cross-links across categories."""
    ph = me.get("phase") or me.get("typical_phase")
    chips = []
    if ph:
        for cat, folder, key in (("entities", "entities", "phase"), ("motifs", "motifs", "typical_phase"),
                                 ("geometries", "geometry", "phase")):
            for n in DATA.get(cat, []):
                if n["name"] != me["name"] and (n.get(key) == ph):
                    chips.append(f'<a class="chip" href="/{folder}/{slug(n["name"])}.html">{esc(n["name"])}</a>')
    return "".join(chips[:10])


# ══════════════════════════════════════════ child + index page builders
def node_page(kind: str, folder: str, n: dict, badge: str, extra_sections: str = "",
              extra_rail: str = "", qas: list | None = None):
    name = n["name"]
    aka = f'<p class="aka">Also called: {esc(", ".join(n["aka"]))}</p>' if n.get("aka") else ""
    ph = n.get("phase") or n.get("typical_phase")
    freq = n.get("frequency") or n.get("frequency_note")
    p = pct_of(freq)
    bar = f'<div class="prevalence"><i style="width:{max(p,2):.1f}%"></i></div>' if p else ""
    freq_html = (f'<div class="freq"><b>How often is this reported?</b><br/>{esc(freq)}{bar}</div>'
                 if freq else "")
    epi = n.get("epistemic_status")
    epi_cls = {"community folk-knowledge": "epi-folk", "anecdotal, unverified": "epi-anecdote",
               "supported by study data": "epi-study", "contested": "epi-contested",
               "speculative/contested": "epi-contested"}.get(epi, "epi-folk")
    badges = f'<div class="badges"><span class="badge {badge}">{esc(n.get("type", kind))}</span>'
    if ph:
        badges += f'<span class="badge phase">Phase {ph}</span>'
    if epi:
        badges += f'<span class="badge {epi_cls}">{esc(epi)}</span>'
    if n.get("convergence_strength"):
        badges += f'<span class="badge epi-anecdote">convergence: {esc(n["convergence_strength"])}</span>'
    badges += "</div>"

    sections = ""
    for label, key in (("Appearance", "appearance"), ("Behavior", "behavior"),
                       ("Communication", "communication"), ("Emotional tone", "emotional_tone"),
                       ("Message or purpose", "message_or_purpose"),
                       ("What happens there", "what_happens_there"),
                       ("Description", "description"), ("Interpretations", "interpretations")):
        if n.get(key):
            sections += f'<div class="section"><h2><span class="h-mark">✦</span>{label}</h2><p>{esc(n[key])}</p></div>'
    if n.get("science_note"):
        sections += f'<div class="sci"><b>What the science says:</b> {esc(n["science_note"])}</div>'
    if n.get("skeptical_reading"):
        sections += f'<div class="skeptic"><b>The skeptical reading:</b> {esc(n["skeptical_reading"])}</div>'
    if n.get("also_noted"):
        notes = "".join(f"<p>{esc(t)}</p>" for t in n["also_noted"])
        sections += f'<div class="section"><h2><span class="h-mark">✦</span>Further notes from the corpus</h2>{notes}</div>'
    sections += extra_sections
    cites = cite_html(n.get("sources"))
    if cites:
        sections += f'<div class="section"><h2><span class="h-mark">✦</span>What the sources say</h2>{cites}</div>'

    rel = related_chips(kind, n)
    rail = ""
    if ph:
        rail += f'<div class="rail-box"><h4>Where in the journey</h4><div class="chiprow">{phase_chip(ph)}</div></div>'
    if n.get("typical_entities"):
        ents = "".join(f'<a class="chip" href="/entities/{slug(e)}.html">{esc(e)}</a>'
                       if any(x["name"] == e for x in DATA["entities"]) else f'<span class="chip">{esc(e)}</span>'
                       for e in n["typical_entities"][:10])
        rail += f'<div class="rail-box"><h4>Reported inhabitants</h4><div class="chiprow">{ents}</div></div>'
    if n.get("typical_actors"):
        acts = "".join(f'<a class="chip" href="/entities/{slug(e)}.html">{esc(e)}</a>'
                       if any(x["name"] == e for x in DATA["entities"]) else f'<span class="chip">{esc(e)}</span>'
                       for e in n["typical_actors"][:10])
        rail += f'<div class="rail-box"><h4>Typical actors</h4><div class="chiprow">{acts}</div></div>'
    if rel:
        rail += f'<div class="rail-box"><h4>Reported alongside</h4><div class="chiprow">{rel}</div></div>'
    nsrc = len(n.get("sources") or [])
    rail += (f'<div class="rail-box"><h4>Citations</h4><div class="kv"><b>{nsrc}</b> source'
             f'{"s" if nsrc != 1 else ""} cite this — see <a href="/library.html">the library</a>.</div></div>')
    rail += extra_rail

    qas = qas or []
    desc_txt = (n.get("description") or n.get("appearance") or "")[:250]
    body = f"""<main class="wrap">
{crumbs((kind.title(), f"/{folder}/"), (name, ""))}
<p class="kicker">{kind.upper()} · THE DMT ATLAS</p>
<h1 class="page-title">{esc(name)}</h1>
{aka}{badges}{freq_html}
<div class="dossier-grid">
<article class="dossier-main">{sections}{faq_block(qas)}</article>
<aside class="rail">{rail}</aside>
</div></main>"""
    ld = [crumb_ld([("Atlas", "/"), (kind.title(), f"/{folder}/"), (name, f"/{folder}/{slug(name)}.html")])]
    if qas:
        ld.append(faq_ld(qas))
    page(f"{folder}/{slug(name)}.html", f"{name} — {kind.title()} · The DMT Atlas",
         f"{name}: {desc_txt}", body, jsonld=ld, active=kind.title())


def index_page(kind: str, folder: str, nodes: list, badge: str, accent: str,
               title: str, lede: str, active: str):
    cards = ""
    for n in sorted(nodes, key=lambda x: x["name"].lower()):
        d = (n.get("description") or n.get("appearance") or n.get("what_happens_there") or "")
        meta_bits = []
        ph = n.get("phase") or n.get("typical_phase")
        if ph:
            meta_bits.append(f"Phase {ph}")
        f = n.get("frequency") or n.get("frequency_note") or ""
        pv = pct_of(f)
        if pv:
            meta_bits.append(f"~{pv:g}% of reports")
        meta_bits.append(f'{len(n.get("sources") or [])} sources')
        cards += f"""<a class="card" style="--card-accent:{accent}" href="/{folder}/{slug(n['name'])}.html">
<h3>{esc(n['name'])}</h3><p>{esc(d)}</p>
<div class="meta">{'<span>·</span>'.join(f'<span>{esc(m)}</span>' for m in meta_bits)}</div></a>"""
    body = f"""<main class="wrap">
{crumbs((title, ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">{esc(title)}</h1>
<p class="lede">{lede}</p>
<div class="grid">{cards}</div></main>"""
    page(f"{folder}/index.html", f"{title} · The DMT Atlas",
         lede[:250], body, active=active,
         jsonld=[crumb_ld([("Atlas", "/"), (title, f"/{folder}/")])])


# ══════════════════════════════════════════ build everything
def build():
    counts = {k: len(DATA.get(k, [])) for k in
              ("entities", "realms", "geometries", "motifs", "themes", "phases", "data_points", "sources")}

    # ---------- entities ----------
    for e in DATA["entities"]:
        nm = e["name"]
        qas = [(f"What are {nm} in the DMT experience?",
                (e.get("appearance") or "")[:400] + " This describes what people report — the Atlas documents the phenomenology, not a metaphysical claim."),
               (f"How often are {nm} reported?", e.get("frequency") or "Frequency varies across report sets; see the cited sources.")]
        ph = e.get("phase")
        if ph and PHASE_BY_NUM.get(ph):
            qas.append((f"When in the experience are {nm} encountered?",
                        f"Most reports place them around phase {ph} — {PHASE_BY_NUM[ph]['name']} — of the commonly-reported journey arc."))
        node_page("entities", "entities", e, "entity", qas=qas)
    index_page("entities", "entities", DATA["entities"], "entity", "var(--c-entity)",
               "The Entities", "Every recurring being reported in the DMT literature — who appears, how they behave, "
               "how often, and exactly who reported them. A field guide to the reported inhabitants of hyperspace.",
               "Entities")

    # ---------- realms ----------
    for r in DATA["realms"]:
        nm = r["name"]
        qas = [(f"What is {nm}?", (r.get("description") or "")[:400]),
               (f"What do people report happening in {nm}?",
                (r.get("what_happens_there") or "See the cited sources.")[:400])]
        node_page("realms", "realms", r, "realm", qas=qas)
    index_page("realms", "realms", DATA["realms"], "realm", "var(--c-realm)",
               "The Realms", "The recurring places of the reported DMT space — waiting rooms, cathedrals, control "
               "rooms, voids — mapped from thousands of written accounts, each with its reported architecture and inhabitants.",
               "Realms")

    # ---------- geometry ----------
    for g in DATA["geometries"]:
        nm = g["name"]
        qas = [(f"What is {nm}?", (g.get("description") or "")[:400])]
        if g.get("science_note"):
            qas.append((f"Is there research on {nm}?", g["science_note"][:400]))
        node_page("geometry", "geometry", g, "geometry", qas=qas)
    index_page("geometry", "geometry", DATA["geometries"], "geometry", "var(--c-geometry)",
               "Geometry & Phenomena", "The visual and perceptual signatures of the experience — the chrysanthemum, "
               "lattices, impossible colors, visible language — including what perceptual science says about each.",
               "Geometry")

    # ---------- motifs ----------
    if DATA.get("motifs"):
        for m in DATA["motifs"]:
            nm = m["name"]
            qas = [(f"What is '{nm}' in DMT reports?", (m.get("description") or "")[:400]),
                   (f"Is '{nm}' commonly reported?",
                    m.get("frequency_note") or "It recurs across independent report sets; see the cited sources.")]
            node_page("motifs", "motifs", m, "motif", qas=qas)
        index_page("motifs", "motifs", DATA["motifs"], "motif", "var(--c-motif)",
                   "Motifs & Events", "The recurring narrative beats of the reports — the greeting, the presentation, "
                   "the download, the send-back. What repeatedly happens, told across independent accounts.",
                   "Motifs")

    # ---------- journey ----------
    blocks = ""
    for p in PHASES:
        rel = ""
        for cat, folder, key in (("entities", "entities", "phase"), ("geometries", "geometry", "phase"),
                                 ("motifs", "motifs", "typical_phase"), ("themes", None, "phase")):
            for n in DATA.get(cat, []):
                if n.get(key) == p["order"]:
                    if folder:
                        rel += f'<a class="chip" href="/{folder}/{slug(n["name"])}.html">{esc(n["name"])}</a>'
                    else:
                        rel += f'<a class="chip" href="/themes.html#theme-{slug(n["name"])}">{esc(n["name"])}</a>'
        cites = cite_html(p.get("sources"))
        blocks += f"""<section class="phase-block" data-order="{p['order']}" id="phase-{slug(p['name'])}">
<h2>{esc(p['name'])}</h2><p>{esc(p['description'])}</p>
{f'<div class="chiprow">{rel}</div>' if rel else ''}{cites}</section>"""
    body = f"""<main class="wrap">
{crumbs(("The Journey", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">The Journey — the breakthrough arc</h1>
<p class="lede">The commonly-reported sequence from onset to return, assembled from the literature.
The order is a strong pattern in the reports, not a law — many journeys skip, loop, or reorder stages.</p>
{blocks}</main>"""
    page("journey.html", "The Journey — the 11 reported stages · The DMT Atlas",
         "The commonly-reported DMT journey arc, stage by stage — onset, the chrysanthemum, breakthrough, "
         "entity contact, the return — each stage cited to the sources that describe it.", body, active="Journey",
         jsonld=[crumb_ld([("Atlas", "/"), ("The Journey", "/journey.html")]),
                 faq_ld([("What are the stages of a DMT experience, as reported?",
                          " → ".join(p["name"] for p in PHASES) + ". This arc is a strong pattern in reports, not a law."),
                         ("Does everyone experience all the stages?",
                          "No — the order is commonly reported but many accounts skip, loop, or reorder stages, and sub-breakthrough experiences may only include early stages.")])])

    # ---------- themes ----------
    items = ""
    for t in sorted(DATA["themes"], key=lambda x: x["name"].lower()):
        epi = t.get("epistemic_status")
        epi_cls = {"community folk-knowledge": "epi-folk", "anecdotal, unverified": "epi-anecdote",
                   "supported by study data": "epi-study", "contested": "epi-contested",
                   "speculative/contested": "epi-contested"}.get(epi, "")
        badges = ""
        if epi:
            badges += f'<span class="badge {epi_cls}">{esc(epi)}</span>'
        if t.get("convergence_strength"):
            badges += f'<span class="badge epi-anecdote">convergence: {esc(t["convergence_strength"])}</span>'
        sci = f'<div class="sci"><b>What the science says:</b> {esc(t["science_note"])}</div>' if t.get("science_note") else ""
        skep = f'<div class="skeptic"><b>The skeptical reading:</b> {esc(t["skeptical_reading"])}</div>' if t.get("skeptical_reading") else ""
        items += f"""<section class="phase-block" style="padding-left:22px" id="theme-{slug(t['name'])}">
<h2>{esc(t['name'])}</h2>{f'<div class="badges" style="margin:0 0 10px">{badges}</div>' if badges else ''}
<p>{esc(t['description'])}</p>{sci}{skep}{cite_html(t.get('sources'))}</section>"""
    body = f"""<main class="wrap">
{crumbs(("Themes", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">Themes, parallels &amp; reported mechanics</h1>
<p class="lede">The recurring meanings and regularities of the reports — the felt truths ("more real than real"),
the cross-cultural echoes, and the community's folk-knowledge about how the space behaves. Epistemic status labeled on every entry.</p>
{items}</main>"""
    page("themes.html", "Themes & reported mechanics · The DMT Atlas",
         "The recurring themes of DMT reports — more-real-than-real, the cosmic joke, time dilation, "
         "cross-cultural parallels — each labeled by epistemic status and cited.", body, active="Themes",
         jsonld=[crumb_ld([("Atlas", "/"), ("Themes", "/themes.html")])])

    # ---------- evidence ----------
    rows = ""
    for d in DATA["data_points"]:
        rec = SRC.get(d["source_key"], {})
        who = f"{rec.get('author','?')} ({rec.get('year','?')})"
        rows += f"""<tr><td>{esc(d['claim'])}</td><td class="stat">{esc(d['stat_or_value'])}</td>
<td>{esc(d.get('detail',''))}<br/><span class="src"><a href="/library.html#src-{slug(d['source_key'])}">{esc(who)}</a></span></td></tr>"""
    body = f"""<main class="wrap">
{crumbs(("Evidence", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">By the numbers — the evidence spine</h1>
<p class="lede">Every hard figure in the Atlas, with its study and its caveats: survey percentages, sample sizes,
EEG findings, frequency counts. Real numbers from named studies only — no invented statistics.</p>
<div class="tablewrap"><table class="evidence">
<thead><tr><th>Claim</th><th>Figure</th><th>Context &amp; source</th></tr></thead>
<tbody>{rows}</tbody></table></div></main>"""
    page("evidence.html", "The evidence — every number, cited · The DMT Atlas",
         f"All {counts['data_points']} quantitative findings behind the DMT Atlas: entity-encounter survey "
         "percentages, sample sizes, EEG findings — each cited to its study.", body, active="Evidence",
         jsonld=[crumb_ld([("Atlas", "/"), ("Evidence", "/evidence.html")]),
                 {"@context": "https://schema.org", "@type": "Dataset",
                  "name": "The DMT Atlas evidence spine",
                  "description": "Quantitative findings from the DMT phenomenology literature, cited per claim.",
                  "url": BASE + "/evidence.html", "creator": {"@type": "Organization", "name": "The DMT Atlas"}}])

    # ---------- library ----------
    items = ""
    for s in sorted(DATA["sources"], key=lambda x: (x.get("type", ""), str(x.get("year", "")))):
        url = f' · <a href="{esc(s["url"])}" rel="noopener">source ↗</a>' if s.get("url") else ""
        items += f"""<div class="src-item" id="src-{slug(s['key'])}">
<span class="stype">{esc(s.get('type','') )}</span>
<h3>{esc(s['work'])}</h3><div class="who">{esc(s['author'])} · {esc(s['year'])}{url}</div>
<p>{esc(s.get('note',''))}</p></div>"""
    body = f"""<main class="wrap">
{crumbs(("Library", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">The Library — every source</h1>
<p class="lede">The written corpus behind the Atlas: peer-reviewed studies, books, lectures, and community archives.
Each note says what the source contributes and how much weight it can carry.</p>
{items}</main>"""
    page("library.html", "The Library — all sources · The DMT Atlas",
         f"The {counts['sources']}-source corpus behind the DMT Atlas: peer-reviewed studies, books, "
         "and community archives, each with an honest reliability note.", body, active="Library",
         jsonld=[crumb_ld([("Atlas", "/"), ("Library", "/library.html")])])

    # ---------- landing ----------
    sections = [
        ("The Entities", "/entities/", "var(--c-entity)", counts["entities"],
         "A field guide to every recurring being in the reports — machine elves to the Divine Feminine, with honest frequency data."),
        ("The Realms", "/realms/", "var(--c-realm)", counts["realms"],
         "The waiting room, the cathedral, the control room, the void — the reported places, mapped."),
        ("Geometry & Phenomena", "/geometry/", "var(--c-geometry)", counts["geometries"],
         "The chrysanthemum, living language, impossible colors — the perceptual signatures, with the science."),
        ("The Journey", "/journey.html", "var(--c-phase)", counts["phases"],
         "The breakthrough arc from inhale to return — the commonly-reported stages, in order."),
        ("Themes & Mechanics", "/themes.html", "var(--c-theme)", counts["themes"],
         "More real than real, the cosmic joke, time dilation — the felt truths and folk-laws of the space."),
        ("The Evidence", "/evidence.html", "var(--c-source)", counts["data_points"],
         "Every number behind the Atlas: survey percentages, sample sizes, EEG findings — all cited."),
    ]
    if DATA.get("motifs"):
        sections.insert(3, ("Motifs & Events", "/motifs/", "var(--c-motif)", counts["motifs"],
                            "The greeting, the presentation, the download, the send-back — what repeatedly happens."))
    cards = "".join(f"""<a class="card" style="--card-accent:{acc}" href="{href}">
<h3>{esc(t)}</h3><p>{esc(d)}</p><div class="meta"><span class="count-pill">{c} entries</span></div></a>"""
                    for t, href, acc, c, d in sections)
    stats = "".join(f'<div class="stat-pill"><b>{counts[k]}</b><span>{lbl}</span></div>'
                    for k, lbl in (("entities", "entities"), ("realms", "realms"),
                                   ("geometries", "phenomena"), ("motifs", "motifs"),
                                   ("themes", "themes"), ("data_points", "cited stats"),
                                   ("sources", "sources")) if counts.get(k))
    honesty = META.get("honesty") or []
    charter_lis = "".join(f"<li>{esc(h)}</li>" for h in honesty)
    body = f"""<main>
<section class="hero"><div class="hero-inner">
  <img class="flower" src="/assets/img/chrysanthemum.png" alt="" aria-hidden="true"/>
  <p class="kicker">✦ A CARTOGRAPHY OF THE COLLECTIVE EXPERIENCE ✦</p>
  <h1>The DMT Atlas</h1>
  <p class="lede">The recurring entities, realms, geometry, and journey of the reported DMT experience —
  mapped from {counts['sources']} written sources and every entry cited to who reported it.</p>
  <p class="note">A map of what people <em>report</em> — not a claim that these are literal places or beings,
  and never a guide to obtaining, making, or taking anything.</p>
  <div class="cta-row">
    <a class="btn primary" href="/explore.html">✦ Enter the interactive Atlas</a>
    <a class="btn ghost" href="/identify.html">What did <i>you</i> meet?</a>
  </div>
  <div class="stats-strip">{stats}</div>
</div></section>
<section class="home-section section-cards">
  <h2>The territories</h2>
  <p class="sub">Everything in the Atlas is drawn from published books, peer-reviewed studies, and community
  archives — then cross-linked, so every entity knows its realm, its phase, and its sources.</p>
  <div class="grid">{cards}</div>
</section>
<section class="charter"><div class="charter-card">
  <h2>What this is — and what it isn't</h2>
  <p>{esc(META.get('charter', ''))}</p>
  <ul class="charter-list">{charter_lis}</ul>
</div></section>
</main>
<script>/* legacy deep links (#entity:x, #about) belong to the explorer */
if(location.hash && /^#(entity|realm|geometry|theme|phase|source|about)/.test(location.hash))
  location.replace('/explore.html'+location.hash);</script>"""
    page("index.html", META.get("title", "The DMT Atlas") + " — a cartography of the collective DMT experience",
         f"An interactive, source-grounded map of the collective DMT experience: {counts['entities']} entities, "
         f"{counts['realms']} realms, the journey stages and themes people report — every entry cited to "
         f"{counts['sources']} written sources.", body,
         jsonld=[{"@context": "https://schema.org", "@type": "WebSite", "name": "The DMT Atlas",
                  "url": BASE + "/", "description": "A source-grounded cartography of the reported DMT experience."}])

    # ---------- sitemap ----------
    urls = [f"{BASE}/", f"{BASE}/explore.html", f"{BASE}/journey.html", f"{BASE}/themes.html",
            f"{BASE}/evidence.html", f"{BASE}/library.html", f"{BASE}/entities/", f"{BASE}/realms/",
            f"{BASE}/geometry/", f"{BASE}/identify.html", f"{BASE}/questions.html", f"{BASE}/grounding.html"]
    if DATA.get("motifs"):
        urls.append(f"{BASE}/motifs/")
    for folder, cat in (("entities", "entities"), ("realms", "realms"),
                        ("geometry", "geometries"), ("motifs", "motifs")):
        for n in DATA.get(cat, []):
            urls.append(f"{BASE}/{folder}/{slug(n['name'])}.html")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    print(f"  wrote sitemap.xml ({len(urls)} urls)")
    print(f"\nDONE — {counts}")


if __name__ == "__main__":
    build()
