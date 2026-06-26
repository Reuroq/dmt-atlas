"""Bake a static, crawlable text-index of the atlas into index.html so the homepage isn't a
~100-word SPA shell to Google. Reproducible + idempotent (re-run after atlas.json changes).
Run: python inject_atlas_text.py"""
import json, re, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "data", "atlas.json"), encoding="utf-8"))


def clean(s):
    return html.escape(re.sub("�", "-", str(s or "")).strip())[:220]


P = ['<style>.atlas-text{max-width:780px;margin:48px auto 24px;padding:0 22px;color:#cfd6e6;'
     'font:16px/1.65 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}.atlas-text h2{color:#fff;'
     'margin:1.7em 0 .45em;font-size:1.32rem;letter-spacing:-.01em}.atlas-text ul,.atlas-text ol{padding-left:1.2em}'
     '.atlas-text li{margin:.4em 0}.atlas-text b{color:#e8edf7}.atlas-text .muted{color:#8a93a8;font-size:.9rem;margin-top:1.4em}</style>',
     '<section class="atlas-text" id="atlas-text">',
     '<h2>The DMT experience, mapped</h2>',
     f'<p>An evidence-grounded cartography of what people report from the DMT (N,N-Dimethyltryptamine) '
     f'breakthrough state, drawn from {len(d["sources"])} written sources: the entities encountered, the realms '
     f'reached, the stages of the journey, and the recurring themes. This is a map of what is <em>reported</em> '
     f'across the literature — not a metaphysical claim and not a how-to.</p>']

P.append(f'<h2>Entities reported in the DMT space ({len(d["entities"])})</h2><ul>')
for e in d["entities"]:
    desc = e.get("appearance") or e.get("behavior") or e.get("message_or_purpose") or ""
    P.append(f'<li><b>{clean(e["name"])}</b> — {clean(desc)}</li>')
P.append("</ul>")

P.append(f'<h2>Realms &amp; spaces ({len(d["realms"])})</h2><ul>')
for r in d["realms"]:
    P.append(f'<li><b>{clean(r["name"])}</b> — {clean(r.get("description"))}</li>')
P.append("</ul>")

phases = sorted(d["phases"], key=lambda p: int(re.sub(r"\D", "", str(p.get("order", "0"))) or 0))
P.append(f'<h2>The breakthrough journey ({len(phases)} stages)</h2><ol>')
for p in phases:
    P.append(f'<li><b>{clean(p["name"])}</b> — {clean(p.get("description"))}</li>')
P.append("</ol>")

P.append(f'<h2>Recurring themes ({len(d["themes"])})</h2><ul>')
for t in d["themes"]:
    P.append(f'<li><b>{clean(t["name"])}</b> — {clean(t.get("description"))}</li>')
P.append("</ul>")
P.append('<p class="muted">Every entry traces to the written sources catalogued in the interactive map above; '
         'convergence across independent reports is striking but is not proof of anything external. Educational only.</p>')
P.append("</section>")

block = "<!-- ATLAS-TEXT-START -->\n" + "\n".join(P) + "\n<!-- ATLAS-TEXT-END -->"
ip = os.path.join(HERE, "index.html")
src = open(ip, encoding="utf-8").read()
if "ATLAS-TEXT-START" in src:
    src = re.sub(r"<!-- ATLAS-TEXT-START -->.*?<!-- ATLAS-TEXT-END -->", block, src, flags=re.S)
else:
    src = src.replace("</body>", block + "\n</body>")
open(ip, "w", encoding="utf-8").write(src)
words = len(re.sub("<[^>]+>", " ", "\n".join(P)).split())
print(f"injected ~{words} crawlable words into index.html ({len(d['entities'])} entities, {len(d['realms'])} realms, {len(phases)} phases, {len(d['themes'])} themes)")
