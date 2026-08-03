#!/usr/bin/env python3
"""nav_merge.py — join the orphaned tool pages to the atlas.

THE PROBLEM (measured 2026-08-02):
    The site had TWO navigations that could not reach each other.
      * atlas template  `nav.site-nav`  — 12 links, on 143 pages
      * tool island     `nav.page-nav`  —  4 links, on questions/identify/grounding,
                                           pointing only at each other
    Those three orphans are the site's BEST performers on both datasets:
      /questions.html  = 15 of ~45 GSC impressions
      /identify.html   = position 3.5, the best rank on the site
      both + /grounding = the top pages live AI agents fetch after the homepage
    So the pages search and AI actually land on were dead ends, and the 146-page
    corpus behind them was unreachable from the landing point.

THE FIX (idempotent — safe to re-run):
    1. port the site-head/site-nav CSS into styles.css (tool pages load a
       different stylesheet than the atlas and had no site-nav rules at all)
    2. give the 3 tool pages the full atlas header, keeping their tool sub-nav
    3. add Questions + Identify to site-nav on every page, so the atlas links
       back and the loop is closed both ways

    python nav_merge.py [--dry]
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DRY = "--dry" in sys.argv

TOOLS = {
    "questions.html":  ("Questions", "Questions from hyperspace"),
    "identify.html":   ("Identify",  "What did I meet?"),
    "grounding.html":  ("After",     "After the experience"),
}

# The canonical nav. `active` is applied per page from ACTIVE_BY_PATH.
NAV_ITEMS = [
    ("/entities/",        "Entities"),
    ("/realms/",          "Realms"),
    ("/geometry/",        "Geometry"),
    ("/motifs/",          "Motifs"),
    ("/crossings/",       "Crossings"),
    ("/journey.html",     "Journey"),
    ("/themes.html",      "Themes"),
    ("/research/",        "Research"),
    ("/evidence.html",    "Evidence"),
    ("/library.html",     "Library"),
    ("/questions.html",   "Questions"),   # NEW - was unreachable from the atlas
    ("/identify.html",    "Identify"),    # NEW - best-ranking page on the site
    ("/ask/",             "Ask"),         # NEW - the question board
]
# Dropped from the global nav to make room, NOT orphaned: /who-owns-dmt.html is
# linked in-body from 143 pages plus the homepage "Most asked" block.
CTA = ('<a class="cta" href="/explore.html">✦ Explore</a>')

SITE_NAV_RE = re.compile(r'<nav class="site-nav">.*?</nav>', re.S)
PAGE_HEAD_RE = re.compile(r'<header class="page-head">.*?</header>', re.S)

CSS_MARKER = "/* --- atlas header (ported by nav_merge.py) --- */"
CSS_BLOCK = CSS_MARKER + """
.site-head{
  position:sticky;top:0;z-index:50;
  background:linear-gradient(180deg,#070514f5 0%,#070514e8 70%,#07051400 100%);
  border-bottom:1px solid #17122e;backdrop-filter:blur(8px);
}
.head-inner{max-width:1180px;margin:0 auto;padding:12px 20px;display:flex;
  align-items:center;gap:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:11px;color:var(--ink);text-decoration:none}
.brand:hover{text-decoration:none}
.brand .mark{color:var(--gold);font-size:19px;filter:drop-shadow(0 0 10px #f3c96977)}
.brand b{font-family:"Fraunces",serif;font-size:18px;font-weight:600;white-space:nowrap}
nav.site-nav{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto;align-items:center}
nav.site-nav a{color:var(--muted);font-size:13px;padding:7px 11px;border-radius:9px;
  transition:.15s;white-space:nowrap;text-decoration:none}
nav.site-nav a:hover{color:var(--ink);background:#151038;text-decoration:none}
nav.site-nav a.active{color:var(--ink);background:#1a1442;box-shadow:0 0 0 1px #2c2456 inset}
nav.site-nav a.cta{color:#0c0716;background:linear-gradient(135deg,var(--gold),#e0b04f);
  font-weight:600;margin-left:6px;box-shadow:0 0 22px -8px #f3c96988}
nav.site-nav a.cta:hover{background:linear-gradient(135deg,#ffd97e,var(--gold))}
/* #cosmos is position:fixed z-index:0 pointer-events:none — anything left at
   z-index:auto paints UNDER it while still being clickable (hit-testable but
   invisible). .tool escapes with z-index:5; the sub-nav must do the same. */
.tool-subnav{position:relative;z-index:5;display:flex;justify-content:center;padding:16px 20px 0}
@media(max-width:760px){nav.site-nav{gap:0}nav.site-nav a{font-size:12px;padding:6px 8px}}
"""


def build_nav(active_href=""):
    parts = []
    for href, label in NAV_ITEMS:
        cls = ' class="active"' if href == active_href else ""
        parts.append('<a href="%s"%s>%s</a>' % (href, cls, label))
    return '<nav class="site-nav">' + "".join(parts) + CTA + "</nav>"


def active_for(path):
    """Which nav item should be lit for this file."""
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    for href, _ in NAV_ITEMS:
        seg = href.strip("/")
        if href.endswith("/") and rel.startswith(seg + "/"):
            return href
        if rel == seg:
            return href
    return ""


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    if DRY:
        return
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def step1_css():
    p = os.path.join(ROOT, "styles.css")
    css = read(p)
    if CSS_MARKER in css:
        return "styles.css already has the atlas header CSS"
    write(p, css.rstrip() + "\n\n" + CSS_BLOCK)
    return "styles.css += atlas header CSS"


def step2_tool_pages():
    out = []
    for fname, (label, _) in TOOLS.items():
        p = os.path.join(ROOT, fname)
        if not os.path.exists(p):
            continue
        html = read(p)
        if 'class="site-nav"' in html:
            out.append("%s already joined" % fname)
            continue
        sub = (
            '<div class="tool-subnav"><nav class="page-nav">'
            '<a href="/explore.html">Explore</a>'
            '<a href="/questions.html"%s>Questions</a>'
            '<a href="/identify.html"%s>Identify</a>'
            '<a href="/grounding.html"%s>After</a>'
            "</nav></div>"
        ) % tuple(' class="on"' if fname == f else ""
                  for f in ("questions.html", "identify.html", "grounding.html"))
        header = (
            '<header class="site-head"><div class="head-inner">\n'
            '  <a class="brand" href="/"><span class="mark">✦</span>'
            "<b>The DMT Atlas</b></a>\n  "
            + build_nav("/" + fname)
            + "\n</div></header>\n"
            + sub
        )
        new, n = PAGE_HEAD_RE.subn(header, html, count=1)
        if not n:
            out.append("%s  !! page-head not found - SKIPPED" % fname)
            continue
        write(p, new)
        out.append("%s joined to the atlas (+%d nav links)" % (fname, len(NAV_ITEMS)))
    return out


def step3_all_pages():
    changed = 0
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if os.sep + ".git" in p or os.sep + "build" in p:
            continue
        html = read(p)
        if 'class="site-nav"' not in html:
            continue
        new = SITE_NAV_RE.sub(lambda m: build_nav(active_for(p)), html, count=1)
        if new != html:
            write(p, new)
            changed += 1
    return "site-nav rewritten on %d pages" % changed


if __name__ == "__main__":
    print("nav_merge%s" % ("  [DRY RUN]" if DRY else ""))
    print(" 1.", step1_css())
    for line in step2_tool_pages():
        print(" 2.", line)
    print(" 3.", step3_all_pages())
