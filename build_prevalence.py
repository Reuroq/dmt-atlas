#!/usr/bin/env python3
"""build_prevalence.py — /prevalence.html, the page that ranks the beings AND
explains why every source gives a different number.

WHY THIS PAGE
    Erowid holds 1,176 DMT reports and offers no way to ask "how common is the
    mantis?" Our own /entities/ index carries 28 percentages but is sorted
    ALPHABETICALLY, so the field has never been shown in order of prevalence.

WHY IT IS NOT JUST A RANKED TABLE
    The percentages in atlas.json are NOT commensurable and ranking them
    together would fabricate a finding. Measured while building this:
      * "Light beings & angels — 75%" is the share of encounters rated
        BENEVOLENT (Davis 2020). It is a tone statistic, not a frequency.
      * "The Ringmaster — 47%" sits in a sentence that begins "Not a survey
        category"; the 47% is Michael's presenter/focuser ROLE code.
      * "The Teacher — 43%" is the same 'guide' descriptor already counted
        against the generic Other. Ranking both double-counts one number.
    Only ONE source is a partition over entity types: Lawrence 2022. That is
    the only set this page ranks. Everything else is shown beside it, labelled
    with what it actually measures.

    python build_prevalence.py
"""
import os
import re
import json
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(ROOT, "data", "atlas.json")
OUT = os.path.join(ROOT, "prevalence.html")

NAV = ('<nav class="site-nav"><a href="/entities/">Entities</a><a href="/realms/">Realms</a>'
       '<a href="/geometry/">Geometry</a><a href="/motifs/">Motifs</a><a href="/crossings/">Crossings</a>'
       '<a href="/journey.html">Journey</a><a href="/world/">Walk Through</a><a href="/themes.html">Themes</a><a href="/research/">Research</a>'
       '<a href="/evidence.html" class="active">Evidence</a><a href="/library.html">Library</a>'
       '<a href="/questions.html">Questions</a><a href="/identify.html">Identify</a>'
       '<a href="/ask/">Ask</a><a class="cta" href="/explore.html">✦ Explore</a></nav>')


def esc(s):
    return html.escape(str(s), quote=True)


def slug(name):
    # The real filenames DROP the ampersand rather than spelling it "and"
    # (alien-grey-forms.html, not alien-and-grey-forms.html). Expanding it
    # silently broke half the cross-links.
    s = name.lower().replace("&", " ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def load():
    with open(ATLAS, encoding="utf-8") as f:
        return json.load(f)


def lawrence_rows(d):
    rows = []
    for p in d["data_points"]:
        c = p.get("claim") or ""
        if p.get("source_key") == "lawrence2022" and "phenotype:" in c:
            v = str(p.get("stat_or_value"))
            m = re.search(r"([\d.]+)\s*%", v)
            n = re.search(r"n\s*=\s*([\d,]+)", v)
            rows.append({
                "label": c.split("phenotype:")[1].strip(),
                "pct": float(m.group(1)) if m else None,
                "n": int(n.group(1).replace(",", "")) if n else None,
            })
    rows.sort(key=lambda r: -(r["pct"] or 0))
    return rows


def entity_index(d):
    """name -> href, so each phenotype row can point at the real pages.
    Reports any entity whose page could not be found, and any BUCKET_MEMBERS
    name that does not exist — a silently dropped cross-link is invisible."""
    out, missing = {}, []
    for e in d["entities"]:
        p = os.path.join(ROOT, "entities", slug(e["name"]) + ".html")
        if os.path.exists(p):
            out[e["name"]] = "/entities/%s.html" % slug(e["name"])
        else:
            missing.append(e["name"])
    if missing:
        print("  !! no page found for %d entities: %s" % (len(missing), missing[:4]))
    names = {e["name"] for e in d["entities"]}
    for bucket, members in BUCKET_MEMBERS.items():
        bad = [m for m in members if m not in names]
        if bad:
            print("  !! BUCKET_MEMBERS[%r] names not in atlas.json: %s" % (bucket, bad))
    return out


# phenotype bucket -> the Atlas entities that live inside it
BUCKET_MEMBERS = {
    "feminine": ["The Divine Feminine", "Fairies, sirens & seductresses",
                 "The Hive Queen — matriarch of the swarm"],
    "deities / divine beings": ["Deities & god-like presences", "Light beings & angels",
                                "Animal-headed figures — Egyptian-styled beings",
                                "Aztec & Mayan-styled beings"],
    "aliens": ["Alien & 'Grey' forms", "Robotic drones & automatons",
               "The Operators — hidden technicians of the experience",
               "The Surgeons — hyperspace medical team"],
    "creature-based (incl. reptilian, insectoid)":
        ["Mantis & insectoid beings", "Reptilian beings", "Octopoid & tentacled beings",
         "The Cosmic Serpent", "Plant spirits & devas"],
    "mythological beings (incl. 'machine elves')":
        ["Self-transforming machine elves", "Child-sprites — hyperspace children",
         "Hooded & cloaked figures", "The Dream Wizards — robed magi of hyperspace"],
    "jesters / clowns": ["The Jester / Trickster / Clown",
                         "The Harlequin — card-dealer of hyperspace",
                         "The Ringmaster — showman of the circus dimension"],
}

# The disagreements worth showing. Each is two real figures for the same word.
CONFLICTS = [
    ("&ldquo;Alien&rdquo;", "39%", "Davis 2020 — share of 2,561 respondents who "
     "<em>chose the word</em> &lsquo;alien&rsquo; from a descriptor list",
     "16.3%", "Lawrence 2022 — share of 3,778 experiences whose entity was "
     "<em>classified</em> as the alien phenotype",
     "Davis let people tick every word that fit, so his figures sum past 100%. "
     "Lawrence sorted each encounter into one bucket. Neither is wrong; they answer "
     "different questions."),
    ("Machine elves", "2.9%", "share of one report set using the literal term",
     "8.4%", "Lawrence 2022 — the whole <em>mythological beings</em> phenotype that "
     "contains them",
     "The famous name is rarer than the category it belongs to. Quoting 8.4% as "
     "&lsquo;machine elves&rsquo; inflates the icon; quoting 2.9% as the whole "
     "mythological class deflates it."),
    ("Entity encounters overall", "45.5%", "Lawrence 2022 — share of inhaled-DMT "
     "reports containing any entity",
     "94%", "Michael 2021 — share of a 36-person naturalistic field study",
     "A self-selected archive of written trip reports and a supervised field study "
     "are not the same population. The 36-person figure is precise and tiny; the "
     "3,778-report figure is broad and self-selected."),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
<title>How often is each being actually reported? — The DMT Atlas</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://dmtatlas.com/prevalence.html"/>
<meta property="og:title" content="How often is each being actually reported?"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:type" content="article"/>
<meta property="og:image" content="https://dmtatlas.com/assets/og.png"/>
<meta name="twitter:card" content="summary_large_image"/>
<link rel="icon" href="/favicon.ico" sizes="48x48"/>
<link rel="apple-touch-icon" href="/apple-touch-icon.png"/>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BKTCYLB89C"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-BKTCYLB89C');</script>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/site.css?v=4"/>
<script type="application/ld+json">{crumbs}</script>
</head>
<body>
<div class="cosmos" aria-hidden="true"></div>
<header class="site-head"><div class="head-inner">
  <a class="brand" href="/"><span class="mark">✦</span><b>The DMT Atlas</b></a>
  {nav}
</div></header>
<main>
<div class="wrap">
  <p class="crumbs"><a href="/">Atlas</a> ✦ <a href="/evidence.html">Evidence</a> ✦ How often each being is reported</p>
  <p class="kicker">✦ PREVALENCE ✦</p>
  <h1 class="page-title">How often is each being actually reported?</h1>
  <p class="lede">Every source gives a different number, and most pages quote whichever one
  suits them. This page ranks the one set of figures that can honestly be ranked, shows the
  others beside it labelled with what they measure, and names the archetypes that no survey
  has ever counted.</p>

  <section class="prev-section">
    <h2>The one rankable set — Lawrence 2022</h2>
    <p class="sub">{corpus}. This is the only source that sorts each encounter into a
    single entity type, so it is the only one whose figures can be put in order.
    The six named phenotypes account for <b>{summed:.1f}%</b>; the remaining
    <b>{rest:.1f}%</b> was not assigned to any of them.</p>
    <table class="prev-table">
      <thead><tr><th>Phenotype</th><th class="num">Share</th><th class="num">n</th><th>In the Atlas</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
    <p class="tiny-note">Bars are drawn to the share column. &lsquo;In the Atlas&rsquo; lists the
    entries this study&rsquo;s bucket contains — a phenotype is a coarse bin, and the Atlas splits
    it further wherever the reports do.</p>
  </section>

  <section class="prev-section">
    <h2>Why you will see different numbers everywhere else</h2>
    <p class="sub">These are not contradictions. They are different denominators, and no
    other page states them side by side.</p>
    <div class="conflict-grid">
{conflicts}
    </div>
  </section>

  <section class="prev-section" id="forum-corpus">
    <h2>The table above is built from forum posts. That matters.</h2>
    <p class="sub">Lawrence 2022 is the only rankable set on this page, and it is a
    content analysis of <b>3,305 r/DMT posts</b>. It measures what people wrote down.
    Whether that is the same thing as what people experienced is a real question, and
    no other page asks it.</p>

    <p>Here is why it is worth asking. We read the titles of <b>71,580 discussion
    threads</b> from the largest public DMT forum and counted how often the community
    actually names each kind of being. If forum writing tracked experience, the two
    columns would agree. They do not:</p>

    <table class="prev-table">
      <thead><tr><th>Phenotype</th><th class="num">Reported</th><th class="num">Named in threads</th><th class="num">Mentions per point</th></tr></thead>
      <tbody>
        <tr><th>jester / clown</th><td class="num">6.5%</td><td class="num">52</td><td class="num"><b>8.0</b></td></tr>
        <tr><th>creature (mantis, reptilian)</th><td class="num">9.2%</td><td class="num">25</td><td class="num">2.7</td></tr>
        <tr><th>mythological (machine elves)</th><td class="num">8.4%</td><td class="num">21</td><td class="num">2.5</td></tr>
        <tr><th>feminine / goddess</th><td class="num">24.2%</td><td class="num">46</td><td class="num">1.9</td></tr>
        <tr><th>deities / divine beings</th><td class="num">17.0%</td><td class="num">29</td><td class="num">1.7</td></tr>
        <tr><th>aliens</th><td class="num">16.3%</td><td class="num">21</td><td class="num"><b>1.3</b></td></tr>
      </tbody>
    </table>

    <p>The rank correlation between the two is <b>+0.09</b> &mdash; effectively none. The
    <em>rarest</em> phenotype is discussed about six times more, per unit of occurrence,
    than one two and a half times more common. Across the forum&rsquo;s entire fifteen-year
    life, entity talk holds flat at roughly <b>1.2%</b> of all threads.</p>

    <p>The likeliest reason is mundane, and visible in the same corpus: the single
    largest thing people post is a <b>request for help</b> &mdash; &ldquo;need help&rdquo;,
    &ldquo;please help&rdquo; and &ldquo;need advice&rdquo; are the most common phrases in
    the whole set. A forum does not collect experience. It collects <em>unresolved</em>
    experience. A benevolent, coherent encounter gives you nothing to ask. A menacing
    trickster you have no word for gives you a thread title.</p>

    <p class="tiny-note"><strong>What we are not claiming.</strong> We tested whether
    scraped corpora report more menace than surveys do, and they do not: the negative or
    menacing share is <b>8%</b> in a supervised field study (Michael 2021, n=36),
    <b>11.4%</b> in the scraped corpus (Lawrence 2022), and <b>&lt;15%</b> in a recruited
    survey (Davis 2020, N=2,561). The scraped figure sits between the other two, so there
    is no clean instrument effect in that direction and we do not assert one. What stands
    is narrower: the ranking above comes from written posts, written posts demonstrably
    over-represent the disturbing and the unnameable, and the size of that distortion is
    unmeasured. Read the percentages as <em>the shape of what gets written down</em>.</p>
  </section>

  <section class="prev-section">
    <h2>The archetypes no survey has ever counted</h2>
    <p class="sub">{uncounted_n} of the Atlas&rsquo;s {total_n} entries have no survey figure at
    all. They are documented in community lexicons, Effect Index&rsquo;s archetype list, or
    clinical narrative — which is weaker evidence, and is said plainly on each page rather
    than dressed in a borrowed percentage.</p>
    <div class="uncounted">
{uncounted}
    </div>
  </section>

  <section class="prev-section">
    <h2>What this means if you are trying to place your own encounter</h2>
    <p>The single most-reported figure is not the famous one. A feminine or maternal presence
    leads at <b>24.2%</b>; the self-transforming machine elves that gave the subject its
    vocabulary are a minority percept. If what you met was ordinary-shaped, wordless, or
    simply <em>present</em>, that is closer to the centre of the distribution than the icon is.</p>
    <div class="cta-row" style="margin-top:18px">
      <a class="btn primary" href="/identify.html">What did <i>you</i> meet?</a>
      <a class="btn ghost" href="/evidence.html">Every number, with its study</a>
    </div>
  </section>
</div>
</main>
<footer class="site-foot"><div class="foot-inner">
  <p>The DMT Atlas — a cartography of the collective experience. Every entry cited.</p>
</div></footer>
</body>
</html>
"""


def build():
    d = load()
    idx = entity_index(d)
    rows = lawrence_rows(d)
    summed = sum(r["pct"] or 0 for r in rows)
    top = max((r["pct"] or 0) for r in rows) if rows else 1

    tr = []
    for r in rows:
        members = BUCKET_MEMBERS.get(r["label"], [])
        links = " · ".join('<a href="%s">%s</a>' % (esc(idx[m]), esc(m.split(" — ")[0]))
                           for m in members if m in idx)
        w = (r["pct"] or 0) / top * 100
        tr.append(
            '        <tr><th scope="row"><span class="bar" style="--w:%.1f%%"></span>%s</th>'
            '<td class="num"><b>%s%%</b></td><td class="num">%s</td><td class="members">%s</td></tr>'
            % (w, esc(r["label"]), r["pct"], "{:,}".format(r["n"]) if r["n"] else "—",
               links or "<span class=\"none\">—</span>"))

    cf = []
    for term, a_v, a_src, b_v, b_src, note in CONFLICTS:
        cf.append(
            '      <article class="conflict">\n'
            '        <h3>%s</h3>\n'
            '        <div class="two"><div><b>%s</b><span>%s</span></div>'
            '<div><b>%s</b><span>%s</span></div></div>\n'
            '        <p>%s</p>\n'
            "      </article>" % (term, a_v, a_src, b_v, b_src, note))

    counted = set()
    for ms in BUCKET_MEMBERS.values():
        counted.update(ms)
    unc = []
    for e in d["entities"]:
        f = e.get("frequency", "")
        if re.search(r"no survey isolates|not a survey category|uncounted", f, re.I):
            href = idx.get(e["name"], "")
            first = re.split(r"(?<=[.;])\s", f)[0][:150]
            unc.append('      <div class="unc"><a href="%s">%s</a><span>%s</span></div>'
                       % (esc(href), esc(e["name"]), esc(first)))

    page = PAGE.format(
        desc=esc("The DMT entity phenotypes ranked by how often they are reported (Lawrence 2022, "
                 "3,778 experiences) — why Davis 2020 and Michael 2021 give different figures for "
                 "the same beings, which archetypes no survey has counted, and what it means that "
                 "the ranking itself is built from forum posts."),
        nav=NAV,
        corpus="Content analysis of 3,778 experiences drawn from 3,305 r/DMT posts (2009–2018)",
        summed=summed, rest=100 - summed,
        rows="\n".join(tr), conflicts="\n".join(cf),
        uncounted="\n".join(unc), uncounted_n=len(unc), total_n=len(d["entities"]),
        crumbs=json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                           "itemListElement": [
                               {"@type": "ListItem", "position": 1, "name": "Atlas",
                                "item": "https://dmtatlas.com/"},
                               {"@type": "ListItem", "position": 2, "name": "Prevalence",
                                "item": "https://dmtatlas.com/prevalence.html"}]},
                          ensure_ascii=False))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return len(rows), len(unc), summed


if __name__ == "__main__":
    n, u, s = build()
    print("prevalence.html — %d ranked phenotypes (%.1f%% of the partition), "
          "%d uncounted archetypes named" % (n, s, u))
