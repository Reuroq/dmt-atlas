"""Open-vocabulary discovery: what recurs in the reports that the atlas does NOT name.

    python build/corpus_discover.py [--top 300]

The saturation curve in corpus_tag.py is closed-vocabulary (the atlas's 128 nodes). This pass
asks the opposite question. Over every tagged report it pulls candidate phrases from the
narrative frames people use to introduce a thing or a place —
    "saw (a|an|the|these) X", "met (a|the) X", "there (was|were) (a|these) X",
    "entered (a|the) X", "(in|into) (a|the) X (room|place|realm|space|hall|chamber|world|city|...)"
— counts the DISTINCT reports each phrase appears in, drops phrases already covered by any atlas
term (vocab.json + vocab_extra.json), and writes data/corpus/discovery.json: the top unmatched
phrases with report counts, first-seen dates and example post ids. Those are the map's
candidate blank spots, for a human (or a reading model) to judge, never auto-added.
"""
import argparse
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "data", "corpus")
PLACE = r"(?:room|place|realm|space|hall|chamber|world|city|dimension|void|tunnel|corridor|palace|temple|garden|" \
        r"landscape|plane|field|cave|forest|ocean|kingdom|domain|lobby|theater|theatre|stage|arena|factory|lab|library|" \
        r"hospital|circus|carnival|zone|area|structure|building|vessel|ship|machine|womb|nursery|hive)"
FRAMES = [
    re.compile(r"\b(?:saw|see|seeing|met|meet|encountered|greeted by|surrounded by|visited by)\s+(?:a|an|the|these|this|some|two|three|several|many)\s+([a-z][a-z\-]+(?:\s+[a-z][a-z\-]+){0,2})", re.I),
    re.compile(r"\bthere\s+(?:was|were)\s+(?:a|an|the|these|this|some|two|three|several|many)\s+([a-z][a-z\-]+(?:\s+[a-z][a-z\-]+){0,2})", re.I),
    re.compile(r"\b(?:entered|inside|into|in)\s+(?:a|an|the|this|some)\s+((?:[a-z][a-z\-]+\s+){0,2}" + PLACE + r")\b", re.I),
    re.compile(r"\b(?:looked like|resembled|shaped like)\s+(?:a|an|the)\s+([a-z][a-z\-]+(?:\s+[a-z][a-z\-]+){0,2})", re.I),
]
STOP_HEAD = {"lot", "bit", "few", "couple", "kind", "sort", "way", "time", "moment", "second", "minute", "thing", "things",
             "point", "part", "sense", "feeling", "same", "first", "last", "next", "whole", "little", "big", "huge", "very",
             "really", "very", "other", "another", "new", "different", "strange", "weird", "certain", "sudden", "long"}
BAD_TAIL = {"of", "that", "which", "who", "and", "or", "but", "with", "in", "on", "at", "to", "for", "from", "as", "i",
            "it", "me", "my", "was", "were", "is", "are", "had", "have", "the", "a", "an"}


def covered_terms():
    terms = set()
    for v in json.load(open(os.path.join(C, "vocab.json"), encoding="utf-8")):
        terms.update(t.lower() for t in v["terms"])
    p = os.path.join(C, "vocab_extra.json")
    if os.path.exists(p):
        for k, ops in json.load(open(p, encoding="utf-8")).items():
            if not k.startswith("_"):
                terms.update(t.lower() for t in ops.get("add", []))
    return terms


def clean(phrase):
    w = phrase.lower().split()
    while w and w[-1] in BAD_TAIL:
        w.pop()
    while w and w[0] in STOP_HEAD:
        w.pop(0)
    if not w or len(w[-1]) < 3:
        return None
    return " ".join(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=300)
    ap.add_argument("--min-reports", type=int, default=8)
    a = ap.parse_args()
    ids = {json.loads(l)["id"] for l in open(os.path.join(C, "reports.jsonl"), encoding="utf-8")}
    texts = {}
    for fp in glob.glob(os.path.join(C, "raw", "*_posts.jsonl")):
        for line in open(fp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("id") in ids:
                texts[r["id"]] = ((r.get("title") or "") + "\n" + (r.get("selftext") or ""), r.get("created_utc"))
    cov = covered_terms()
    counts = collections.Counter(); first = {}; examples = collections.defaultdict(list)
    for pid, (text, ts) in texts.items():
        found = set()
        for rx in FRAMES:
            for m in rx.finditer(text):
                ph = clean(m.group(1))
                if ph and ph not in cov and not any(ph.endswith(" " + t) or ph == t for t in ()):
                    found.add(ph)
        for ph in found:
            counts[ph] += 1
            if ph not in first or (ts and ts < first[ph]):
                first[ph] = ts
            if len(examples[ph]) < 5:
                examples[ph].append(pid)
    # collapse: a phrase whose head noun is itself covered by the atlas is not a blank spot
    def head_covered(ph):
        last = ph.split()[-1]
        return any(last == t or last == t.rstrip("s") or (t.endswith(last) and len(t) - len(last) <= 1) for t in cov if " " not in t)
    GENERIC = {"room", "world", "place", "realm", "space", "void", "dimension", "area", "zone", "plane", "side", "where",
               "stuff", "inside", "light", "face", "person", "man", "woman", "girl", "guy", "figure", "patterns", "visuals",
               "outline", "of people", "universe", "real world", "physical world", "material world", "physical realm",
               "good place", "bad place", "right place", "safe place", "dark place", "room around", "state", "reality",
               "experience", "trip", "body", "mind", "head", "eyes", "hand", "hands", "way", "point", "thing", "things"}
    rows = [{"phrase": ph, "reports": n, "first_seen": first.get(ph), "examples": examples[ph], "head_in_atlas": head_covered(ph)}
            for ph, n in counts.most_common() if n >= a.min_reports and ph not in GENERIC][:a.top]
    json.dump({"reports_scanned": len(texts), "candidates": rows}, open(os.path.join(C, "discovery.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"scanned {len(texts):,} reports; {len(rows)} candidate phrases with >= {a.min_reports} reports")
    print("top blank-spot candidates (not covered by any atlas term; * = head noun IS in the atlas):")
    for r in rows[:60]:
        print(f"  {r['reports']:5d}  {'*' if r['head_in_atlas'] else ' '} {r['phrase']}")


if __name__ == "__main__":
    main()
