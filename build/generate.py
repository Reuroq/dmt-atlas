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
    ("Motifs", "/motifs/"), ("Crossings", "/crossings/"), ("Journey", "/journey.html"),
    ("Themes", "/themes.html"), ("Evidence", "/evidence.html"), ("Library", "/library.html"),
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
<meta property="og:image" content="https://dmtatlas.com/assets/og.png"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:image" content="https://dmtatlas.com/assets/og.png"/>
<link rel="icon" href="/favicon.ico" sizes="48x48"/>
<link rel="apple-touch-icon" href="/apple-touch-icon.png"/>
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


# ══════════════════════════════════════════ crossings (cross-tradition hubs)
# Each crossing links a reported DMT figure to the same figure in the older
# record (myth, folklore, the cognitive science of perception), cited and
# ontologically neutral. Section bodies are trusted HTML authored here.

CROSSINGS = [
    {
        "slug": "the-mantis-older-than-religion",
        "title": "The Mantis Older Than Religion",
        "subtitle": "|Kaggen, trance cosmology, and the insectoid beings of DMT",
        "blurb": "A mantis-headed intelligence sits at the centre of two altered-state worlds ten thousand years and a hemisphere apart. What the convergence does — and does not — show.",
        "desc": "The praying-mantis being reported on DMT meets |Kaggen, the Mantis trickster-creator of the |Xam San — bridged by the entoptic model of the world's oldest art. Cited, and careful about what convergence proves.",
        "lede": "One of the more disquieting regularities in the DMT literature is the <a href=\"/entities/mantis-insectoid-beings.html\">praying-mantis being</a> — a towering, triangular-headed, clinical intelligence. Ten thousand years and a hemisphere away, the oldest continuously recorded religion on earth put a mantis at the centre of creation. This page maps that convergence, names the bridge that connects the two, and is deliberate about the difference between a pattern and a proof.",
        "related_entities": ["Mantis & insectoid beings", "The Surgeons — hyperspace medical team"],
        "related_realms": ["The Hive"],
        "sections": [
            ("The being people meet",
             "<p>Across the largest report sets, insectoid and specifically mantis-like beings recur as a distinct class: investigative, telepathic, emotionally cool, often encountered in a clinical or technological setting. Michael and colleagues coded grey- or mantis-like forms in roughly 6% of encounters; the insectoid category appears throughout the Johns Hopkins and Lawrence corpora. What marks the mantis is less its frequency than its <em>consistency</em> — strangers converge on the same triangular head, the same appraising stance. The Atlas documents that convergence as phenomenology; it makes no claim about what, if anything, is on the other side.</p>"),
            ("The oldest trickster",
             "<p>Among the |Xam San (Bushmen) of southern Africa, <strong>|Kaggen</strong> — the Mantis — is the trickster-creator: shape-shifter, maker and unmaker, dying and reviving. He is recorded first-hand in the nineteenth-century Bleek-Lloyd archive, one of the deepest primary records of any hunter-gatherer cosmology. An honest caveat belongs here up front: |Kaggen is a <em>mythic narrative figure</em> — he has a wife and family, he acts in stories — not a being someone reports meeting in trance. The link to DMT does not run through the myth directly. It runs through what the San did with altered states, and through what those states did to the oldest human art.</p>"),
            ("The bridge — entoptic imagery and the first art",
             "<p>This is the load-bearing connection. In the neuropsychological model of rock art (Lewis-Williams &amp; Dowson's <em>The Signs of All Times</em>, 1988; Lewis-Williams's <em>The Mind in the Cave</em>, 2002), the geometric and figurative content of humanity's earliest images derives substantially from altered states of consciousness — the same class of visionary experience the San entered in the trance dance, now argued to underlie Upper Palaeolithic cave art. The model is influential and genuinely contested. But it supplies the one thing the DMT literature lacks: a mechanism for why altered states might generate <em>shared content</em> that then settles into a culture's sacred imagery. If trance reliably produces certain figures, those figures can become gods — and a mantis is one of them, in two places, without contact between them.</p>"),
        ],
        "faqs": [
            ("Did the San take DMT?",
             "There is no evidence the |Xam used DMT or any tryptamine. The connection is not a shared drug. It is a shared class of experience — altered states — plus the entoptic model that ties San trance cosmology to their rock art. Treat the parallel as convergence, not lineage."),
            ("Is the mantis a real being, then?",
             "The Atlas does not adjudicate that. Convergence across cultures is compatible with several readings: a shared neurobiology of the visual and agency systems; an archetype in the Jungian sense; or, for those who hold it, genuine contact. The page maps the pattern and labels the uncertainty; it does not resolve it."),
            ("Why a mantis specifically?",
             "Open question. Hypotheses range from the mantis's uncanny, front-facing, quasi-human gaze and alien articulation, to the general human tendency to read predatory insect forms as intelligences. None is established. The honest answer is that the recurrence is documented and the cause is not."),
        ],
        "sources": [
            {"source_key": "michael2021", "detail": "Coded grey- or mantis-like forms in roughly 6% of DMT entity encounters."},
            {"source_key": "davis2020", "detail": "Large survey establishing insectoid/'alien' beings as a recurring encounter class."},
            {"source_key": "bleeklloyd", "detail": "Primary |Xam San testimony recording |Kaggen, the Mantis trickster-creator."},
            {"source_key": "lewiswilliams_dowson", "detail": "The entoptic model: altered-state percepts recur cross-culturally in rock art."},
            {"source_key": "lewiswilliams", "detail": "Argues the oldest human art derives substantially from altered states of consciousness."},
        ],
        "honesty": "A mantis at the centre of two trance worlds is a real and striking convergence. It is not, by itself, evidence that the mantis is a being that exists independently of the mind that meets it. Cultural diffusion is ruled out by distance; a shared human neurobiology of vision and agency, and the entoptic bridge, remain the most parsimonious frames — with genuine contact held open, not endorsed.",
    },
    {
        "slug": "why-the-walls-have-faces",
        "title": "Why the Walls Have Faces",
        "subtitle": "Pareidolia, agent detection, and the machinery that may have built the gods",
        "blurb": "On DMT the walls fill with faces and the space feels watched. A 1993 theory of religion says that exact reflex is where gods came from.",
        "desc": "The faces-in-the-walls and the felt sense of being watched on DMT, mapped onto face pareidolia, hyperactive agency detection, and Guthrie's theory that religion begins in over-detecting faces. Cited and neutral.",
        "lede": "Two of the most common things people report on DMT are <a href=\"/entities/embedded-faces-faces-in-the-walls.html\">faces embedded in every surface</a> and the sense of being <a href=\"/entities/the-scanners-entry-examiners.html\">watched and appraised</a> by a populated space. Neither is exotic. They are the ceiling of a bias you use every waking second — and one influential theory says that same bias is where religion itself began.",
        "related_entities": ["Embedded faces — faces in the walls", "The Scanners — entry examiners"],
        "related_realms": [],
        "sections": [
            ("The over-detecting brain",
             "<p>Human vision runs a fast, coarse, permanently-on face detector: three dots in a triangle, a pattern of shadow and socket, the front of a car — and you see a face before you can stop yourself. The system is tuned to <em>miss nothing</em>, so it fires on noise. Agency works the same way. Barrett's <strong>Hyperactive Agency Detection Device</strong> describes an evolved, hair-trigger tendency to infer an <em>agent</em> behind ambiguous events — because mistaking the wind for a stalker is cheap, and mistaking a stalker for the wind is fatal. Both systems are biased, by design, toward false positives.</p>"),
            ("Faces in the clouds",
             "<p>In <em>Faces in the Clouds</em> (1993), Stewart Guthrie argues that religion originates in exactly this over-detection, scaled up: systematic anthropomorphism — reading faces, minds, and intentions into a world that has none — yields a cosmos that is watched, animate, and addressed. On this account the gods are not added to perception; they fall out of its default settings. DMT is interesting here because it does not <em>introduce</em> the reflex. It saturates it. The walls-made-of-faces, the felt tribunal, the sense that the space is attending to you — this is the standing bias driven to its maximum, which is why the percept feels less like imagination than like something switched on.</p>"),
            ("What changes when you know this",
             "<p>Naming the mechanism does two useful things and one thing it cannot do. It explains the <em>form</em>: why faces and watchers, specifically, rather than arbitrary shapes. And it reframes the fear — the sense of being judged is, at minimum, your most ancient perceptual safeguard at full volume, which is worth knowing at 3 a.m. What it cannot do is settle the ontology. That a percept has a mechanism does not prove there is nothing there; it proves the brain is shaped to find someone. Guthrie's is one theory among several, and the Atlas presents it as a lens, not a verdict.</p>"),
        ],
        "faqs": [
            ("Why do I see faces in the walls on DMT?",
             "Your visual system carries an always-on, over-sensitive face detector — the same one that finds faces in clouds and outlets. DMT appears to drive that detector far past its normal threshold, so nearly every surface resolves into faces. It is a saturation of an ordinary bias, not a new faculty."),
            ("Is something really watching me?",
             "The felt sense of being watched is produced by an evolved agency-detection bias tuned toward false positives. That accounts for the feeling regardless of whether an agent is present. The Atlas does not claim to know whether anything is there; it explains why the sense of a watcher is so reliably generated."),
            ("What is pareidolia?",
             "Pareidolia is the perception of meaningful patterns — most often faces — in random or ambiguous stimuli. It is universal and non-pathological. On DMT it is one of the most consistently reported features of the visual field."),
        ],
        "sources": [
            {"source_key": "guthrie", "detail": "Religion as systematic anthropomorphism: over-detecting faces and agents in a mindless world."},
            {"source_key": "barrett_hadd", "detail": "The Hyperactive Agency Detection Device — a hair-trigger tendency to infer agents."},
            {"source_key": "davis2020", "detail": "Documents 'presence'/being-watched and face phenomena among recurring encounter features."},
            {"source_key": "strassman", "detail": "Clinical reports of populated, attending spaces and the sense of being expected."},
        ],
        "honesty": "That a percept has a known mechanism explains its form and its reliability, not its ultimate status. Guthrie's anthropomorphism theory and Barrett's HADD are well-developed but not the last word in the cognitive science of religion. This page offers them as an explanatory lens for a common and frightening experience — not as proof that nothing is there.",
    },
    {
        "slug": "the-false-familiar",
        "title": "The False Familiar",
        "subtitle": "The Mimic, the doppelgänger, and why a loved one's face is the most frightening mask",
        "blurb": "The dread of the Mimic isn't monstrous — it's the specific horror of a near-perfect familiar that is subtly wrong. Freud, Mori, and a thousand years of folklore already named it.",
        "desc": "The DMT 'Mimic' — a being wearing a familiar face — mapped onto Freud's uncanny, Mori's uncanny valley, and the doppelgänger and changeling of folklore. One cognitive signature, four instances. Cited and neutral.",
        "lede": "Some DMT beings frighten because they are monstrous. The <a href=\"/entities/the-mimic-wearer-of-familiar-faces.html\">Mimic</a> frightens for the opposite reason: it wears a face you know — a friend, a parent, your own — and something about it is fractionally, unplaceably wrong. That precise dread has a name in three separate literatures that rarely cite one another.",
        "related_entities": ["The Mimic — wearer of familiar faces", "Deceased loved ones & ancestors"],
        "related_motifs": [],
        "sections": [
            ("The recognition test",
             "<p>Recognising a person runs as a fast, largely automatic pass: a face resolves, a familiarity signal fires, and you feel — before any reasoning — that you know who this is. The Mimic's horror is mechanical. It <em>passes</em> that first pass: the face reads as familiar. Then a finer check fails — the eyes are wrong, the warmth is missing, the timing is off. What is left is a category error the body registers as dread: <em>this is someone I know, and it is not.</em> The threat is not ugliness; it is the collapse of recognition itself.</p>"),
            ("Freud to Mori",
             "<p>Freud named this in 1919. The <em>unheimlich</em> — literally 'un-home-like' — is the familiar turned strange, and his central case is the <strong>double</strong>: the doppelgänger, the face that is yours and not yours. Half a century later the roboticist Masahiro Mori drew the <strong>uncanny valley</strong>: as a figure approaches human likeness our warmth rises, then plunges into revulsion at <em>almost</em>-human, before recovering at fully human. Mori named the valley after Freud's <em>unheimlich</em> directly. Two fields, one curve — and the Mimic sits at its lowest point.</p>"),
            ("The face that shouldn't be here",
             "<p>Folklore ritualised the false familiar long before either. The <strong>doppelgänger / fetch</strong>: to see your own double, or a living relative's, was an omen of death. The <strong>changeling</strong>: the child returned that looks right and is not, the substitute that fails the finer test. The <strong>revenant</strong> that comes home wearing a dead relative's face. Across the tale-type indexes these are one recurring structure — the token that passes recognition then fails it. The Mimic is a fourth instance of a very old cognitive alarm, met this time as an entity.</p>"),
        ],
        "faqs": [
            ("Why did the DMT being look like someone I know?",
             "The 'wearing a familiar face' encounter is a recurring report. It engages the recognition system — the being reads as known, then registers as subtly wrong. The Atlas documents the pattern; it makes no claim about what the being is."),
            ("Why is the Mimic so frightening if it looks familiar?",
             "Because familiarity is exactly the trap. Monstrous things trip an obvious threat response; the false familiar passes the first recognition check and fails a finer one, producing a category-error dread — 'someone I know, and not' — which is the uncanny in its purest form."),
            ("What is the uncanny valley?",
             "A 1970 observation by roboticist Masahiro Mori: as something looks more human, our affinity rises, then drops sharply into revulsion at near-but-not-quite human likeness. Mori named it after Freud's concept of the uncanny."),
        ],
        "sources": [
            {"source_key": "freud_uncanny", "detail": "The uncanny as the familiar made strange; the double/doppelganger as its central case."},
            {"source_key": "mori_uncanny", "detail": "Revulsion peaks at almost-but-not-quite human likeness; named after Freud's unheimlich."},
            {"source_key": "uther_atu", "detail": "Changeling and doppelganger tale-types: the substitute that looks right and is not."},
            {"source_key": "davis2020", "detail": "Deceased/familiar figures appear among recurring encounter types."},
        ],
        "honesty": "The false familiar is a cognitive signature shared by a percept (uncanny valley), a psychoanalytic idea (the double), and a folklore motif (changeling/revenant). Naming that shared structure explains why the Mimic is frightening; it says nothing about whether the Mimic is anything more than a face the mind assembled.",
    },
    {
        "slug": "why-you-cant-bring-it-back",
        "title": "Why You Can't Bring It Back",
        "subtitle": "State-dependent memory and the gift that turns to leaves",
        "blurb": "The revelation feels un-losable in the space and evaporates on return — then waits for you next time. That asymmetry is a documented property of memory, and folklore wrote it down as law.",
        "desc": "The re-entry amnesia of DMT ('losing the message') mapped onto state-dependent memory and the folklore of the fairy-gift that turns worthless at the threshold. Cited; the ineffability question is deliberately kept separate.",
        "lede": "A near-universal complaint: inside the space the insight is total and obviously un-losable, and within seconds of return it is gone — yet on the next journey it is waiting again. The Atlas calls this <a href=\"/motifs/losing-the-message-the-amnesia-on-return.html\">Losing the Message</a>, and it behaves far more like a specific property of memory than like ordinary forgetting.",
        "related_entities": [],
        "related_motifs": ["Losing the Message — the amnesia on return", "The Download — compressed information transfer"],
        "sections": [
            ("Encoded in a state you can't get back to",
             "<p>Memory is cued by the state it was formed in. In the classic experiments, material learned in one physiological state is recalled best in that same state (Overton, 1964); divers who learn a word list underwater recall it better underwater than on land (Godden &amp; Baddeley, 1975). This is <strong>state-dependent memory</strong>, and it predicts the DMT pattern exactly. The insight is encoded in a state ordinary waking consciousness cannot reach — so it is not merely forgotten, it is <em>inaccessible from here</em>. The tell is the return of the same content on re-dosing: recovery-on-re-entry is the signature of a retrieval-cue failure, not of erasure.</p>"),
            ("Not the same as ineffability",
             "<p>One honest distinction has to be drawn, because the two are constantly conflated. <em>Ineffability</em> is 'I remember it vividly but cannot put it into words' — a translation problem. <em>Re-entry amnesia</em> is 'I cannot retrieve it at all' — an access problem. They are different phenomena with different mechanisms, and this page is about the second. Chaining them together produces a tidy story and a wrong one; the Atlas keeps them apart.</p>"),
            ("The gift that turns to leaves",
             "<p>Folklore encoded the same asymmetry as narrative law. Fairy gold that becomes dead leaves or coal once carried across the threshold; the Sibyl's prophecies written on leaves and scattered by the wind; the dream-revelation gone on waking. The recurring rule is that value and knowledge are real <em>inside their own world</em> and do not survive the crossing back. It is the pre-scientific observation of exactly what state-dependent memory describes — the boundary, not the mind, is where the gift is lost.</p>"),
        ],
        "faqs": [
            ("Why can't I remember my DMT insights?",
             "The likely mechanism is state-dependent memory: material encoded in the DMT state is cued by that state and is hard to retrieve from ordinary consciousness. That fits the reports better than simple forgetting — especially the way the same content returns on the next experience."),
            ("Why does the same realization come back each time?",
             "Return-on-re-entry is the giveaway. If the memory were erased it would not come back; that it reappears when you re-enter the state points to a retrieval-cue effect — the state is the key that unlocks the content."),
            ("Is the message real, or is it nonsense?",
             "The Atlas takes no position on the content's worth. The memory framing explains why it is hard to carry back; it does not rule on whether the insight was profound or noise. Both happen, and integration work is where people sort them out."),
        ],
        "sources": [
            {"source_key": "overton1964", "detail": "State-dependent learning: material encoded in a state is best retrieved in that state."},
            {"source_key": "goddenbaddeley1975", "detail": "Context-dependent memory (the divers study): retrieval is cued by the encoding context."},
            {"source_key": "uther_atu", "detail": "Fairy-gift-reversal motifs: value that turns worthless once carried across the threshold."},
            {"source_key": "mckenna", "detail": "'It melts away like a dream' — the folk-observation of the return-trip amnesia."},
        ],
        "honesty": "State-dependent memory is a real and well-evidenced phenomenon, and it fits the re-entry amnesia reports closely. That is an explanation of the pattern, not a measurement of any specific person's experience, and it says nothing about the value of what was 'lost'. The folklore parallel is illustrative, not evidentiary.",
    },
    {
        "slug": "the-implant",
        "title": "The Implant",
        "subtitle": "Quartz, abduction, and the Download — when beings put something inside you",
        "blurb": "A distinct motif hides inside the DMT surgery reports: not being probed, but being given an implant that permanently changes you. Aboriginal initiation and abduction lore share the exact grammar.",
        "desc": "The DMT 'Download' / 'Gift' / insertion motif — beings implanting something transformative — mapped onto Aboriginal mabain quartz-insertion initiation and abduction-implant lore. Cited; kept distinct from the dismemberment and examination motifs.",
        "lede": "The Atlas already maps the examination-table overlap between DMT surgery and alien abduction. Buried inside the <a href=\"/motifs/the-download-compressed-information-transfer.html\">Download</a> and <a href=\"/motifs/the-gift-an-object-handed-over.html\">Gift</a> motifs is a different, less-noticed act: not being inspected, but being <em>implanted</em> — an external intelligence installs something inside you that leaves you permanently altered.",
        "related_entities": ["The Surgeons — hyperspace medical team"],
        "related_motifs": ["The Gift — an object handed over", "The Download — compressed information transfer", "The Insertion — implant, probe, procedure"],
        "sections": [
            ("The oldest version: quartz in the body",
             "<p>Across Aboriginal Australia the most consistent act of initiation is not instruction but <em>installation</em>. In Elkin's ethnography, beings of the Dreamtime insert <strong>quartz crystals — mabain / maban</strong> — into the candidate's body, and it is this insertion that converts him 'from physical to psychic levels.' The transformative object is placed <em>inside</em>; the initiate is remade by what he now carries. This is a distinct grammar from the trials and dismemberment that surround it — it is implantation.</p>"),
            ("The modern version: implants",
             "<p>The twentieth-century abduction narrative independently fixates on the same act. Alongside the examination table, its most persistent motif is the <strong>implant</strong> — an object the visitors leave in the body, the procedure that installs rather than merely inspects (catalogued, controversially, by Mack). Whatever one makes of the accounts as events, as <em>folklore</em> they repeat the initiatory structure precisely: beings open the body and leave something transformative behind.</p>"),
            ("The DMT version: the Download",
             "<p>The DMT <a href=\"/motifs/the-download-compressed-information-transfer.html\">Download</a> and <a href=\"/motifs/the-gift-an-object-handed-over.html\">Gift</a> are the same grammar abstracted one step — from object to information. Something is <em>placed into you</em>: a compressed transmission, a bestowed knowing, occasionally a felt object, and you return marked or upgraded. It is worth separating this cleanly from the two neighbouring motifs the Atlas already tracks: it is not the reassembly of <em>dismemberment</em>, and not the inspection of the <em>examination</em> — it is installation. The object-to-information seam is where the parallel is loosest, and it is stated, not smuggled.</p>"),
        ],
        "faqs": [
            ("Why do DMT beings insert something into me?",
             "The 'something placed inside that transforms you' motif is old and cross-cultural — from quartz-insertion in Aboriginal initiation to abduction implants — and on DMT it tends to arrive as information (the 'Download') rather than an object. The Atlas maps the shared structure and takes no view on whether anything is literally installed."),
            ("How is this different from the abduction examination?",
             "The examination inspects; the implant installs. The Atlas already covers the exam-table overlap separately. This crossing is specifically about the second act — the being leaving something transformative behind — which is a distinct motif with its own long lineage."),
            ("Did the beings give me something real?",
             "The Atlas doesn't adjudicate that. What it can say is that the 'implantation-as-transformation' motif recurs across initiation myth, abduction lore, and DMT reports as a narrative structure — which explains its familiarity without settling its status."),
        ],
        "sources": [
            {"source_key": "elkin", "detail": "Aboriginal initiation: beings insert quartz (mabain) into the initiate to remake him 'from physical to psychic levels'."},
            {"source_key": "mack", "detail": "The abduction implant motif: an object installed in the body, distinct from mere examination."},
            {"source_key": "eliade", "detail": "Initiatory insertion/substitution motifs across shamanic traditions."},
            {"source_key": "strassman", "detail": "Clinical DMT reports of information 'downloads' and being remade by hyperspace technicians."},
        ],
        "honesty": "Implantation-as-transformation is a shared narrative structure across three bodies of lore, with one honest seam: the older versions install an object, the DMT version usually installs information. The parallel is about the grammar of the motif, not a claim that the same literal event occurs. Elkin, Eliade, and Mack are all, in their different ways, contested sources.",
    },
]

CROSSING_BY_NODE: dict[str, list] = {}
for _c in CROSSINGS:
    for _e in _c.get("related_entities", []) + _c.get("related_motifs", []):
        CROSSING_BY_NODE.setdefault(slug(_e), []).append(_c)


def crossing_card(node_name: str, noun: str = "being") -> str:
    """Reciprocal link injected into an entity/motif page that features in a crossing."""
    cs = CROSSING_BY_NODE.get(slug(node_name))
    if not cs:
        return ""
    links = "".join(
        f'<p><a href="/crossings/{c["slug"]}.html"><b>{esc(c["title"])}</b></a> — {esc(c["subtitle"])}</p>'
        for c in cs)
    return ('<div class="section"><h2><span class="h-mark">✦</span>'
            f'Crossings — where this {noun} meets the older record</h2>' + links + '</div>')


def crossing_page(c: dict) -> None:
    secs = ""
    for h2, bodyhtml in c["sections"]:
        secs += f'<div class="section"><h2><span class="h-mark">✦</span>{esc(h2)}</h2>{bodyhtml}</div>'
    cites = cite_html(c.get("sources"))
    if cites:
        secs += f'<div class="section"><h2><span class="h-mark">✦</span>What the sources say</h2>{cites}</div>'
    if c.get("honesty"):
        secs += f'<div class="skeptic"><b>What this does and does not mean:</b> {esc(c["honesty"])}</div>'
    rail = ""
    ent_chips = "".join(f'<a class="chip" href="/entities/{slug(e)}.html">{esc(e)}</a>'
                        for e in c.get("related_entities", []))
    if ent_chips:
        rail += f'<div class="rail-box"><h4>Beings in this crossing</h4><div class="chiprow">{ent_chips}</div></div>'
    realm_chips = "".join(f'<a class="chip" href="/realms/{slug(r)}.html">{esc(r)}</a>'
                          for r in c.get("related_realms", []))
    if realm_chips:
        rail += f'<div class="rail-box"><h4>Realms</h4><div class="chiprow">{realm_chips}</div></div>'
    motif_chips = "".join(f'<a class="chip" href="/motifs/{slug(m)}.html">{esc(m)}</a>'
                          for m in c.get("related_motifs", []))
    if motif_chips:
        rail += f'<div class="rail-box"><h4>Motifs</h4><div class="chiprow">{motif_chips}</div></div>'
    nsrc = len(c.get("sources") or [])
    rail += (f'<div class="rail-box"><h4>Citations</h4><div class="kv"><b>{nsrc}</b> sources'
             f' — see <a href="/library.html">the library</a>.</div></div>')
    body = f"""<main class="wrap">
{crumbs(("Crossings", "/crossings/"), (c["title"], ""))}
<p class="kicker">CROSSINGS · THE DMT ATLAS</p>
<h1 class="page-title">{esc(c["title"])}</h1>
<p class="aka">{esc(c["subtitle"])}</p>
<p class="lede">{c["lede"]}</p>
<div class="dossier-grid">
<article class="dossier-main">{secs}{faq_block(c.get("faqs"))}</article>
<aside class="rail">{rail}</aside>
</div></main>"""
    ld = [crumb_ld([("Atlas", "/"), ("Crossings", "/crossings/"), (c["title"], f"/crossings/{c['slug']}.html")])]
    if c.get("faqs"):
        ld.append(faq_ld(c["faqs"]))
    page(f"crossings/{c['slug']}.html", f"{c['title']} — Crossings · The DMT Atlas",
         c["desc"], body, jsonld=ld, active="Crossings")


def crossings_index() -> None:
    cards = ""
    for c in CROSSINGS:
        cards += (f'<a class="card" href="/crossings/{c["slug"]}.html">'
                  f'<h3>{esc(c["title"])}</h3><p>{esc(c["subtitle"])}</p>'
                  f'<div class="meta"><span>{esc(c["blurb"])}</span></div></a>')
    body = f"""<main class="wrap">
{crumbs(("Crossings", ""))}
<p class="kicker">THE DMT ATLAS</p>
<h1 class="page-title">Crossings</h1>
<p class="lede">Where a being, realm, or motif reported on DMT meets the same figure in the older record — myth, folklore, and the cognitive science of perception. Each crossing states the connection, cites it to published sources, and stays careful about the difference between a pattern and a proof.</p>
<div class="grid">{cards}</div></main>"""
    page("crossings/index.html", "Crossings — cross-tradition connections · The DMT Atlas",
         "Where the reported DMT experience meets myth, folklore, and the cognitive science of perception — cited, and careful about what convergence proves.",
         body, active="Crossings", jsonld=[crumb_ld([("Atlas", "/"), ("Crossings", "/crossings/")])])


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
        node_page("entities", "entities", e, "entity", extra_sections=crossing_card(nm), qas=qas)
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
            node_page("motifs", "motifs", m, "motif", extra_sections=crossing_card(m["name"], "motif"), qas=qas)
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

    # ---------- crossings ----------
    for c in CROSSINGS:
        crossing_page(c)
    crossings_index()

    # ---------- sitemap ----------
    urls = [f"{BASE}/", f"{BASE}/explore.html", f"{BASE}/journey.html", f"{BASE}/themes.html",
            f"{BASE}/evidence.html", f"{BASE}/library.html", f"{BASE}/entities/", f"{BASE}/realms/",
            f"{BASE}/geometry/", f"{BASE}/identify.html", f"{BASE}/questions.html", f"{BASE}/grounding.html"]
    if DATA.get("motifs"):
        urls.append(f"{BASE}/motifs/")
    if CROSSINGS:
        urls.append(f"{BASE}/crossings/")
        urls += [f"{BASE}/crossings/{c['slug']}.html" for c in CROSSINGS]
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
