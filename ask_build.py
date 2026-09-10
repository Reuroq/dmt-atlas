#!/usr/bin/env python3
"""ask_build.py — generates /ask/, the Atlas question board.

The board is SEEDED, not empty. A new forum with no posts is worse than none:
it reads as abandoned, it is thin content, and it answers nothing. So the
opening state is the demand we measured — 71,580 real thread titles from the
largest public DMT forum, clustered by what people are actually asking.

We publish OUR canonical phrasing of each cluster, not the scraped titles.
Republishing other people's thread titles verbatim would be duplicate content
we didn't write; synthesising the recurring question and answering it is the
same thing the Atlas already does with its sources. Cluster sizes are shown
because the number is the evidence that the question is real.

    python ask_build.py
"""
import os
import json
import html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(ROOT, "data", "demand", "demand_report.json")
OUT_DIR = os.path.join(ROOT, "ask")

NAV = ('<nav class="site-nav"><a href="/entities/">Entities</a><a href="/realms/">Realms</a>'
       '<a href="/geometry/">Geometry</a><a href="/motifs/">Motifs</a><a href="/crossings/">Crossings</a>'
       '<a href="/journey.html">Journey</a><a href="/world/">Walk Through</a><a href="/themes.html">Themes</a><a href="/research/">Research</a>'
       '<a href="/evidence.html">Evidence</a>'
       '<a href="/library.html">Library</a><a href="/questions.html">Questions</a>'
       '<a href="/identify.html">Identify</a><a href="/ask/" class="active">Ask</a><a class="cta" href="/explore.html">✦ Explore</a></nav>')

# Canonical question per measured cluster. `key` matches demand_report themes.
CLUSTERS = [
    ("what-did-i-see", "I met something. What was it?",
     "The most common reason people go looking after a breakthrough — trying to put a name to "
     "a being that felt specific and intentional. The Atlas mirrors an encounter against the "
     "archetypes others most commonly report, with how often each appears and who documented it.",
     [("Run the encounter identifier", "/identify.html"),
      ("Browse all 40 reported entity types", "/entities/")]),

    ("entity-identification", "Why do strangers describe the same beings?",
     "Machine elves, a mantis, a feminine presence, a jester — people who have never met and never "
     "compared notes report the same recurring figures. That the descriptions converge is the "
     "documented, interesting fact. It does not settle what they are.",
     [("The 40 entity types, with frequencies", "/entities/"),
      ("Are the entities real? — the honest answer", "/questions.html")]),

    ("ontology-is-it-real", "Was any of that real, or was it just my brain?",
     "The question people ask most, and genuinely unresolved. The serious positions — disrupted "
     "top-down control, Jungian archetypes, Strassman's and Gallimore's independently-real "
     "hypotheses, and plain agnosticism — are mapped side by side. The Atlas takes no verdict.",
     [("The range of positions, cited", "/questions.html"),
      ("What the studies actually measured", "/evidence.html")]),

    ("integration-aftermath", "It shook me. What now?",
     "A large share of the questions people ask are not about the trip — they are about the weeks "
     "after it. What is commonly reported afterwards, what tends to settle on its own, and where "
     "real peer support and crisis lines are.",
     [("After the experience", "/grounding.html"),
      ("What people commonly report afterwards", "/themes.html")]),

    ("themes-meaning", "It felt like a message. Did it mean something?",
     "The download, the sense of being expected, the cosmic joke, the conviction that you already "
     "knew this. These recur across thousands of accounts as describable, nameable themes — "
     "which is itself the finding.",
     [("The 44 recurring themes", "/themes.html"),
      ("What repeatedly happens — the motifs", "/motifs/")]),

    ("realms-places", "Where was I?",
     "The waiting room, the domed cathedral, the control room, the library, the void. People "
     "describe arriving somewhere with structure and consistency, and the reported places have "
     "been mapped as named regions.",
     [("The 31 reported realms", "/realms/"),
      ("The journey, inhale to return", "/journey.html")]),

    ("geometry-visuals", "What is the geometry I keep seeing?",
     "The chrysanthemum at the threshold, the carrier wave, living language, faces embedded in "
     "everything. The perceptual signatures are catalogued with what the science says about each.",
     [("Geometry & phenomena", "/geometry/"),
      ("The evidence behind the numbers", "/evidence.html")]),

    ("nde-death", "Is this the same as a near-death experience?",
     "Partly. In a placebo-controlled study DMT scored higher than placebo on 15 of 16 Greyson "
     "NDE-scale items — but the signature NDE elements, the life review and meeting the deceased, "
     "are rare in DMT reports. It models the feeling and the structure; it demonstrates nothing "
     "about an afterlife.",
     [("The NDE comparison, cited", "/questions.html"),
      ("Timmermann and the study data", "/evidence.html")]),

    ("science-research", "Is DMT actually being studied?",
     "Yes, and far more than most people assume. The research layer indexes the peer-reviewed "
     "literature, the registered clinical trials, the patent landscape, and a cited history — "
     "each linked to its primary source.",
     [("2,857 peer-reviewed studies", "/research/studies.html"),
      ("52 registered clinical trials", "/research/trials.html"),
      ("Who is trying to own the molecule", "/who-owns-dmt.html")]),

    ("help-seeking", "I don't know what I'm asking yet.",
     "The single largest shape in the measured corpus is someone simply asking for help — no "
     "keyword, no category, just needing a person. Start with the questions everyone asks; if "
     "yours isn't there, the board below is open.",
     [("The questions everyone asks", "/questions.html"),
      ("After the experience", "/grounding.html")]),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
<title>Ask the Atlas — the questions people actually bring</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://dmtatlas.com/ask/"/>
<meta property="og:title" content="Ask the Atlas — the questions people actually bring"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:type" content="website"/>
<meta property="og:image" content="https://dmtatlas.com/assets/og.png"/>
<meta name="twitter:card" content="summary_large_image"/>
<link rel="icon" href="/favicon.ico" sizes="48x48"/>
<link rel="apple-touch-icon" href="/apple-touch-icon.png"/>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BKTCYLB89C"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-BKTCYLB89C');</script>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/site.css?v=3"/>
<script type="application/ld+json">{faq}</script>
<script type="application/ld+json">{crumbs}</script>
</head>
<body>
<div class="cosmos" aria-hidden="true"></div>
<header class="site-head"><div class="head-inner">
  <a class="brand" href="/"><span class="mark">✦</span><b>The DMT Atlas</b></a>
  {nav}
</div></header>
<main>
<section class="hero" style="padding-top:52px">
  <div class="hero-inner">
    <p class="kicker">✦ ASK THE ATLAS ✦</p>
    <h1>The questions people actually bring</h1>
    <p class="lede">These are not invented categories. They are what {total:,} real discussion
    threads across the largest public DMT community are asking, clustered by what the question
    is really about — and answered from the Atlas, with citations.</p>
    <p class="note">A map of what people <em>report</em>. Nothing here is about obtaining, making,
    or taking anything, and questions asking for that can't be answered on this board.</p>
  </div>
</section>

<section class="home-section section-cards">
  <h2>Where the questions go</h2>
  <p class="sub">Cluster sizes are measured, not estimated — each is the count of matching
  discussion threads in a {total:,}-thread corpus.</p>
  <div class="ask-list">
{clusters}
  </div>
</section>

<section class="home-section section-cards" id="ask">
  <h2>Ask a question</h2>
  <p class="sub">Every question is read by a person before it appears — this is a moderated board,
  not a live forum. That's slower, and it's the only way a board on this subject stays inside the
  Atlas's charter.</p>
  <form class="ask-form" id="askForm">
    <label for="qbody">Your question</label>
    <textarea id="qbody" name="body" rows="4" maxlength="1200"
      placeholder="What did you want to ask? e.g. &quot;I saw something insectoid that seemed to be examining me — is that common?&quot;"></textarea>
    <label for="qctx">Anything that helps place it <span class="opt">(optional)</span></label>
    <textarea id="qctx" name="context" rows="2" maxlength="1200"
      placeholder="What you saw, what it felt like, what you're trying to make sense of."></textarea>
    <button type="submit">Send it</button>
    <p class="ask-status" id="askStatus" role="status"></p>
    <p class="tiny-note">If you're in crisis, please reach a person now — call or text
    <strong>988</strong> in the US, or Fireside Project's psychedelic peer-support line at
    <strong>62-FIRESIDE</strong>. This board can't help in an emergency.</p>
  </form>
</section>
</main>
<footer class="site-foot"><div class="foot-inner">
  <p>The DMT Atlas — a cartography of the collective experience. Every entry cited.</p>
</div></footer>
<script>
document.getElementById('askForm').addEventListener('submit', async function(e){{
  e.preventDefault();
  var s=document.getElementById('askStatus'), b=document.getElementById('qbody').value,
      c=document.getElementById('qctx').value, btn=this.querySelector('button');
  s.className='ask-status'; s.textContent='Sending…'; btn.disabled=true;
  try{{
    var r=await fetch('/api/ask',{{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{body:b,context:c}})}});
    var j=await r.json();
    s.textContent=j.message||'Thanks.';
    s.className='ask-status '+(j.ok?'ok':'warn');
    if(j.ok){{document.getElementById('qbody').value='';document.getElementById('qctx').value='';}}
  }}catch(err){{ s.textContent='Could not send that — try again in a moment.'; s.className='ask-status warn'; }}
  btn.disabled=false;
}});
</script>
</body>
</html>
"""


def esc(s):
    return html.escape(s, quote=True)


def build():
    with open(REPORT, encoding="utf-8") as f:
        rep = json.load(f)
    counts = {k: len(v) for k, v in rep["themes"].items()}
    total = rep["total_threads"]

    blocks, faq = [], []
    for key, q, a, links in CLUSTERS:
        n = counts.get(key, 0)
        link_html = "".join(
            '<a class="ask-link" href="%s">%s</a>' % (esc(h), esc(t)) for t, h in links)
        blocks.append(
            '    <article class="ask-item">\n'
            '      <h3>%s</h3>\n'
            '      <p class="ask-count"><b>%d</b> discussion threads ask a version of this</p>\n'
            '      <p>%s</p>\n'
            '      <div class="ask-links">%s</div>\n'
            "    </article>" % (esc(q), n, esc(a), link_html))
        faq.append({"@type": "Question", "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}})

    desc = ("The questions people actually bring to the DMT experience, clustered from %d real "
            "discussion threads and answered from the Atlas with citations." % total)
    page = PAGE.format(
        desc=esc(desc), nav=NAV, total=total, clusters="\n".join(blocks),
        faq=json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                        "mainEntity": faq}, ensure_ascii=False),
        crumbs=json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                           "itemListElement": [
                               {"@type": "ListItem", "position": 1, "name": "Atlas",
                                "item": "https://dmtatlas.com/"},
                               {"@type": "ListItem", "position": 2, "name": "Ask the Atlas",
                                "item": "https://dmtatlas.com/ask/"}]}, ensure_ascii=False))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return len(CLUSTERS), total


if __name__ == "__main__":
    n, total = build()
    print("ask/index.html — %d clusters seeded from %d measured threads" % (n, total))
