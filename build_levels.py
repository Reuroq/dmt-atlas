#!/usr/bin/env python3
"""build_levels.py — /geometry/levels.html, the crosswalk nobody has published.

THE GAP
    PsychonautWiki defines an eight-level geometry ladder (1 Visual noise ...
    8A/8B) and explicitly names DMT among the substances that fork to 8B. It
    is the vocabulary everyone borrows: forums, blogs and Reddit all say
    "level 8B geometry" and none of them say what you would actually be
    LOOKING AT. The ladder is described in the abstract, on purpose — it spans
    every psychedelic.

    The Atlas has the other half: 24 named, cited phenomena people actually
    report — the Chrysanthemum, the Carrier Wave, living language, alien
    glyphs. Nothing anywhere maps one onto the other.

WHAT IS WHOSE
    The level names and the 8A/8B fork are PsychonautWiki's, CC BY-SA,
    attributed and linked. The phenomena, phases and citations are the
    Atlas's. THE MAPPING BETWEEN THEM IS OURS — an interpretation, labelled as
    one on the page, not a claim PsychonautWiki makes.

    Verified against their raw wikitext, not a search summary: the level names
    below are exact, and the 8A/8B sections are NOT empty (they transclude
    ~3,200 characters each from separate main articles) — an earlier read of
    the stripped wikitext suggested otherwise and would have been wrong.

    python build_levels.py
"""
import os
import json
import html
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(ROOT, "data", "atlas.json")
OUT = os.path.join(ROOT, "geometry", "levels.html")

NAV = ('<nav class="site-nav"><a href="/entities/">Entities</a><a href="/realms/">Realms</a>'
       '<a href="/geometry/" class="active">Geometry</a><a href="/motifs/">Motifs</a>'
       '<a href="/crossings/">Crossings</a><a href="/journey.html">Journey</a>'
       '<a href="/themes.html">Themes</a><a href="/research/">Research</a>'
       '<a href="/evidence.html">Evidence</a><a href="/library.html">Library</a>'
       '<a href="/questions.html">Questions</a><a href="/identify.html">Identify</a>'
       '<a href="/ask/">Ask</a><a class="cta" href="/explore.html">✦ Explore</a></nav>')

# level number, exact PsychonautWiki label, what it means in plain words,
# Atlas phenomena that match, the journey phase they sit in
LEVELS = [
    ("1", "Visual noise",
     "The grain that is there when you close your eyes stone sober — visual snow, "
     "eigengrau, stray light under the lids. The bottom of the ladder is not a drug "
     "effect at all.",
     ["TV Static & the Signal-Noise Transition"], "Onset"),
    ("2", "Motion and color",
     "The static starts moving and takes on colour. Surfaces begin to breathe.",
     ["Breathing & Liquid Surfaces", "Impossible Colors"], "Onset"),
    ("3", "Partially defined geometry",
     "Shapes resolve out of the noise but stay unfinished — filigree over surfaces, "
     "the four universal form-constants that recur across every hallucinogen.",
     ["Static Pattern Overlay & filigree", "Klüver Form Constants (the geometric spine)"],
     "Onset"),
    ("4", "Fully defined geometry",
     "The pattern closes into complete, symmetrical, self-similar structure. On DMT "
     "this is the door everyone describes by name.",
     ["The Chrysanthemum", "Mandalas & symmetry fields", "Fractal lattices & jeweled tilings",
      "Ultra-Detail & Infinite Resolution"], "The Chrysanthemum"),
    ("5", "3-Dimensional geometry",
     "The pattern gains volume — objects rather than wallpaper, with depth, texture "
     "and impossible solid geometry.",
     ["Hyper-dimensional objects", "Dimensional Layering & Space-Folding",
      "Tactile Geometry (Felt Textures)"], "The Rush → Breakthrough"),
    ("6", "Partially overriding visual perception",
     "Geometry starts replacing the room rather than decorating it. Faces surface out "
     "of the pattern; the rush and the aperture belong here.",
     ["Embedded Faces & the Pareidolia Cascade", "Zooming / Rushing Tunnel Flight",
      "The Aperture / Iris Opening"], "The Rush → Through the Membrane"),
    ("7", "Fully overriding visual perception",
     "The external world is gone. The body boundary goes with it, and vision stops "
     "being a forward-facing window.",
     ["Body Dissolution & Merging with the Geometry", "Omnidirectional 360° Vision",
      "Hyperbolic Space & Negative Curvature"], "Breakthrough → Arrival"),
]

FORK = {
    "8A": ("Perceived exposure to semantic concept network",
           "Physically stimulating psychedelics with less hallucinatory content — "
           "PsychonautWiki names LSD, 2C-B and 4-HO-MET.", []),
    "8B": ("Perceived exposure to inner mechanics of consciousness",
           "Sedating psychedelics with heavy hallucinatory content. PsychonautWiki "
           "names <b>DMT</b> here, with psilocybin, LSA and 2C-T-7 — so a DMT reader "
           "following this ladder lands on 8B specifically.",
           ["Living language / visible sound", "Alien Glyphs & Unreadable Writing Systems",
            "Energy Conduits & Living Circuitry", "Time Geometry — Moments as Objects & Loops"]),
}


def esc(s):
    return html.escape(str(s), quote=True)


def slug(name):
    s = name.lower().replace("&", " ").replace("'", "").replace("’", "")
    s = s.replace("°", "").replace("(", " ").replace(")", " ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def geo_index():
    """Atlas geometry name -> href, verified on disk."""
    with open(ATLAS, encoding="utf-8") as f:
        d = json.load(f)
    out, missing = {}, []
    for g in d["geometries"]:
        p = os.path.join(ROOT, "geometry", slug(g["name"]) + ".html")
        if os.path.exists(p):
            out[g["name"]] = ("/geometry/%s.html" % slug(g["name"]),
                              (g.get("description") or "")[:130])
        else:
            missing.append((g["name"], slug(g["name"])))
    if missing:
        print("  !! %d geometry pages not found: %s" % (len(missing), missing[:3]))
    return out


def row(num, label, meaning, members, phase, idx, fork=False):
    li = []
    for m in members:
        if m in idx:
            href, desc = idx[m]
            li.append('<li><a href="%s">%s</a><span>%s</span></li>' % (esc(href), esc(m), esc(desc)))
        else:
            print("  !! level %s: %r not in atlas geometries" % (num, m))
    cls = "lvl fork" if fork else "lvl"
    return (
        '  <article class="%s" id="level-%s">\n'
        '    <div class="lvl-num">%s</div>\n'
        '    <div class="lvl-body">\n'
        '      <h3>%s</h3>\n'
        '      <p class="lvl-mean">%s</p>\n'
        '      %s\n'
        '      <ul class="lvl-list">%s</ul>\n'
        "    </div>\n  </article>"
        % (cls, num, num, esc(label), meaning,
           ('<p class="lvl-phase">Atlas phase · <b>%s</b></p>' % esc(phase)) if phase else "",
           "".join(li) or '<li class="none">No Atlas phenomenon is specific to this level.</li>'))


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
<title>Geometry levels 1–8B, translated: what you are actually looking at — The DMT Atlas</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://dmtatlas.com/geometry/levels.html"/>
<meta property="og:title" content="Geometry levels 1–8B, translated"/>
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
  <p class="crumbs"><a href="/">Atlas</a> ✦ <a href="/geometry/">Geometry</a> ✦ The levels, translated</p>
  <p class="kicker">✦ THE LEVEL LADDER ✦</p>
  <h1 class="page-title">Levels 1&ndash;8B, translated</h1>
  <p class="lede">Every forum thread borrows the same eight-level vocabulary &mdash;
  &ldquo;that was level 8B geometry&rdquo; &mdash; and none of them say what you would
  actually be looking at. The ladder is deliberately abstract because it has to cover
  every psychedelic. This page maps it onto the specific, named, cited phenomena people
  report on DMT.</p>
  <p class="note">The eight levels and the 8A/8B fork are
  <a href="https://psychonautwiki.org/wiki/Geometry" rel="noopener">PsychonautWiki&rsquo;s</a>
  (CC BY-SA). The phenomena and citations are the Atlas&rsquo;s.
  <b>The mapping between them is ours</b> &mdash; a reading, not a claim PsychonautWiki makes.</p>

  <div class="ladder">
{levels}
  </div>

  <section class="prev-section">
    <h2>Level 8 forks &mdash; and DMT goes one way</h2>
    <p class="sub">At the top the ladder splits into two states of equal intensity. Which
    one you get is substance-dependent, and PsychonautWiki puts DMT firmly on one side.</p>
    <div class="ladder">
{fork}
    </div>
  </section>

  <section class="prev-section">
    <h2>Why the two systems do not line up neatly</h2>
    <p class="sub">A level measures <b>intensity</b>; an Atlas phase measures <b>sequence</b>.
    They are different axes, which is why the mapping above is many-to-many rather than a
    straight list. The Chrysanthemum is level 4 by intensity but arrives second in the
    journey; living language is level 8B by intensity and arrives late. A phenomenon can
    also skip levels entirely &mdash; on a high dose people report going from level 2 to a
    breakthrough in seconds, which is exactly why dose-ladder descriptions written for
    slower psychedelics read oddly to DMT users.</p>
    <div class="cta-row" style="margin-top:18px">
      <a class="btn primary" href="/geometry/">All 24 phenomena</a>
      <a class="btn ghost" href="/journey.html">The journey, in order</a>
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
    idx = geo_index()
    rows = [row(n, l, m, mem, ph, idx) for n, l, m, mem, ph in LEVELS]
    forks = [row(k, "%s — %s" % (k, v[0]), v[1], v[2], "", idx, fork=True)
             for k, v in FORK.items()]
    page = PAGE.format(
        desc=esc("The PsychonautWiki geometry levels 1-8B mapped onto the specific named "
                 "phenomena people report on DMT — what level 4, level 7 and level 8B "
                 "actually look like, each linked to its cited Atlas entry."),
        nav=NAV, levels="\n".join(rows), fork="\n".join(forks),
        crumbs=json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                           "itemListElement": [
                               {"@type": "ListItem", "position": 1, "name": "Atlas",
                                "item": "https://dmtatlas.com/"},
                               {"@type": "ListItem", "position": 2, "name": "Geometry",
                                "item": "https://dmtatlas.com/geometry/"},
                               {"@type": "ListItem", "position": 3, "name": "The levels",
                                "item": "https://dmtatlas.com/geometry/levels.html"}]},
                          ensure_ascii=False))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return len(rows) + len(forks)


if __name__ == "__main__":
    print("geometry/levels.html — %d levels mapped" % build())
