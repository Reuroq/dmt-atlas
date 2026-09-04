"""Tag harvested reports with the atlas vocabulary; mine transitions and the saturation curve.

    python build/corpus_tag.py                # all raw post files under data/corpus/raw
    python build/corpus_tag.py --min-chars 400 --require-report

Outputs (data/corpus/):
  reports.jsonl      one line per qualifying report: id, sub, date, score, ordered node hits
  transitions.json   counts of consecutive (from -> to) node pairs inside reports, per kind
  saturation.json    cumulative distinct nodes vs reports read (chronological), first-seen dates
  saturation.png     the curve (needs matplotlib)
  summary.json       totals, per-node report counts, image-post index (url + permalink, no download)

A hit is a case-insensitive whole-word match of a vocabulary term (from data/corpus/vocab.json,
built from atlas.json names + aka). Terms shorter than MIN_TERM or in STOP are ignored because
they fire on ordinary prose ("She", "the Source", "Onset").
"""
import argparse
import collections
import glob
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "data", "corpus")
MIN_TERM = 5
STOP = {"she", "the source", "onset", "inhalation", "the return", "the rush", "the peak", "the temple", "the vault",
        "the lobby", "the reception", "the nursery", "the other side", "the dmt world", "hyperspace", "the void",
        "the download", "the lesson", "the show", "the machine", "the operators", "the council", "the choir",
        "the mimic", "the logos", "the voice", "the goddess", "supreme being", "the surgeons", "the scanners",
        "the harlequin", "the ringmaster", "the jester", "guides", "spirits", "helpers", "the dome", "the grid",
        "the room", "the hallway", "the corridor", "the tunnel", "the membrane", "breakthrough"}
REPORT_HINTS = re.compile(r"trip report|experience report|my (first|last|recent) (dmt )?(trip|experience|breakthrough)|"
                          r"i (smoked|vaped|took|did|hit) (\d+ ?mg|some|the) (of )?(dmt|spice|deems)|breakthrough", re.I)


def load_vocab():
    vocab = json.load(open(os.path.join(C, "vocab.json"), encoding="utf-8"))
    extra_path = os.path.join(C, "vocab_extra.json")
    extra = json.load(open(extra_path, encoding="utf-8")) if os.path.exists(extra_path) else {}
    pats = []
    for v in vocab:
        terms = [t for t in v["terms"] if len(t) >= MIN_TERM and t.lower() not in STOP]
        def norm(s):  # "The Waiting Room" -> "waiting room"
            s = s.lower().strip()
            return s[4:] if s.startswith("the ") else s
        for key, ops in extra.items():  # vernacular layer: key matches the START of a node name (or kind|name)
            if key.startswith("_"):
                continue
            k_kind, _, k_name = key.partition("|") if "|" in key else ("", "", key)
            if norm(v["name"]).startswith(norm(k_name)) and (not k_kind or k_kind == v["kind"]):
                rm = {t.lower() for t in ops.get("remove", [])}
                terms = [t for t in terms if t.lower() not in rm]
                terms += [t for t in ops.get("add", []) if len(t) >= 3]
        terms = sorted(set(terms), key=len, reverse=True)
        if not terms:
            continue
        alt = "|".join(sorted((re.escape(t) for t in terms), key=len, reverse=True))
        pats.append((v["kind"], v["name"], re.compile(r"(?<![A-Za-z])(?:" + alt + r")(?![A-Za-z])", re.I)))
    return pats


NEG = re.compile(r"(?:\bno\b|\bnon[- ]?|\bnot\b|n't\b|\bnever\b|\bwithout\b|\balmost\b|\bnearly\b|\bclose to\b|\bsub[- ]?|\bfail(?:ed)? to\b|\bcouldn't\b|\bwasn't\b)\s*(?:\w+\s+){0,2}$", re.I)


def hits(text, pats):
    """First non-negated match per node; a hit within a few words of 'no/not/never/without/almost/sub-' is dropped."""
    found = []
    for kind, name, rx in pats:
        for m in rx.finditer(text):
            if NEG.search(text[max(0, m.start() - 28):m.start()]):
                continue
            found.append((m.start(), kind, name))
            break
    found.sort()
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-chars", type=int, default=400)
    ap.add_argument("--require-report", action="store_true", help="keep only posts that read like a report")
    ap.add_argument("--files", nargs="*")
    a = ap.parse_args()
    pats = load_vocab()
    files = a.files or sorted(glob.glob(os.path.join(C, "raw", "*_posts.jsonl")))
    rows = []
    images = []
    for fp in files:
        sub = os.path.basename(fp).split("_")[0]
        for line in open(fp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            url = str(r.get("url") or "")
            is_img = (r.get("post_hint") in ("image", "hosted:video", "rich:video") or "reddit.com/gallery/" in url
                      or url.split("?")[0].lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4"))
                      or "i.redd.it" in url or "v.redd.it" in url or "imgur.com" in url)
            if is_img:
                images.append({"id": r.get("id"), "sub": sub, "title": r.get("title"), "url": url,
                               "permalink": f"https://www.reddit.com/r/{sub}/comments/{r.get('id')}/",
                               "kind": r.get("post_hint") or "link", "score": r.get("score"),
                               "created_utc": r.get("created_utc"), "author": r.get("author")})
            text = (r.get("title") or "") + "\n" + (r.get("selftext") or "")
            if r.get("selftext") in ("[removed]", "[deleted]", None) or len(text) < a.min_chars:
                continue
            if a.require_report and not REPORT_HINTS.search(text):
                continue
            h = hits(text, pats)
            if not h:
                continue
            rows.append({"id": r.get("id"), "sub": sub, "created_utc": r.get("created_utc"), "score": r.get("score"),
                         "flair": r.get("link_flair_text"), "chars": len(text),
                         "seq": [[k, n] for _, k, n in h], "pos": [p for p, _, _ in h]})
    rows.sort(key=lambda x: x["created_utc"] or 0)
    os.makedirs(C, exist_ok=True)
    with open(os.path.join(C, "reports.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # transitions: consecutive distinct nodes within a report, by kind pair
    trans = collections.Counter()
    per_node = collections.Counter()
    co = collections.Counter()
    for r in rows:
        seq = [tuple(x) for x in r["seq"]]
        pos = r.get("pos") or list(range(len(seq)))
        for n in set(seq):
            per_node[n] += 1
        for (x, px), (y, py) in zip(zip(seq, pos), zip(seq[1:], pos[1:])):
            if x != y and py > px:  # two nodes firing on the same word are one observation, not a transition
                trans[(x, y)] += 1
        for i, x in enumerate(seq):
            for y in seq[i + 1:]:
                if x != y:
                    co[tuple(sorted((x, y)))] += 1
    # saturation: cumulative distinct nodes vs reports, chronological
    seen = {}
    curve = []
    for i, r in enumerate(rows, 1):
        for k, n in r["seq"]:
            if (k, n) not in seen:
                seen[(k, n)] = {"first_report_index": i, "first_seen": r["created_utc"], "id": r["id"]}
        if i % 25 == 0 or i == len(rows):
            curve.append([i, len(seen)])
    json.dump({"n_reports": len(rows), "n_nodes_total": len(pats),
               "transitions": [{"from": list(x), "to": list(y), "n": n} for (x, y), n in trans.most_common()],
               "cooccurrence": [{"a": list(x), "b": list(y), "n": n} for (x, y), n in co.most_common(400)]},
              open(os.path.join(C, "transitions.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"n_reports": len(rows), "vocab_nodes": len(pats), "nodes_seen": len(seen), "curve": curve,
               "first_seen": {f"{k}|{n}": v for (k, n), v in seen.items()},
               "never_seen": [f"{k}|{n}" for k, n, _ in pats if (k, n) not in seen]},
              open(os.path.join(C, "saturation.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"reports": len(rows), "images": len(images), "files": [os.path.basename(f) for f in files],
               "per_node": [{"kind": k, "name": n, "reports": c} for (k, n), c in per_node.most_common()],
               "image_posts": sorted(images, key=lambda x: -(x.get("score") or 0))[:5000]},
              open(os.path.join(C, "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"reports tagged: {len(rows):,}  image posts indexed: {len(images):,}  nodes seen: {len(seen)}/{len(pats)}")
    print("top nodes:", ", ".join(f"{n} ({c})" for (k, n), c in per_node.most_common(12)))
    print("top transitions:", "; ".join(f"{x[1]}->{y[1]} {n}" for (x, y), n in trans.most_common(8)))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs, ys = zip(*curve) if curve else ([], [])
        plt.figure(figsize=(9, 5)); plt.plot(xs, ys, lw=2)
        plt.axhline(len(pats), ls="--", c="grey"); plt.xlabel("reports read (chronological)"); plt.ylabel("distinct atlas nodes seen")
        plt.title(f"DMT Atlas saturation: {len(seen)}/{len(pats)} nodes after {len(rows):,} reports")
        plt.grid(alpha=.3); plt.tight_layout(); plt.savefig(os.path.join(C, "saturation.png"), dpi=130)
        print("saturation.png written")
    except Exception as e:
        print("no chart:", e)


if __name__ == "__main__":
    main()
