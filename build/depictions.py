"""Build the depictions index: people-made images of the DMT experience, mapped to atlas nodes.

    python build/depictions.py

Reads data/corpus/raw/*_posts.jsonl (Arctic Shift harvest) and data/corpus/vocab.json.
Keeps image / gallery / video posts that are about DMT and look like depictions (replications,
drawings, paintings, renders), tags each with the atlas nodes its title/body names, and writes
data/corpus/depictions.json: per node, the best-scored candidates with permalink, author,
score, date and the media kind. NOTHING is downloaded: the site embeds the Reddit post
(creator-owned) with credit; only CC/PD files (Commons) are ever copied into assets/.
"""
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "data", "corpus")
DMT = re.compile(r"\b(dmt|deems|dimethyltryptamine|spice|changa|ayahuasca|5-?meo)\b", re.I)
ART = re.compile(r"\b(replication|replicat(ed|ing)|drew|drawing|drawn|paint(ed|ing)?|sketch|illustrat|art(work)?|render|"
                 r"animation|animated|3d|blender|digital|oc\b|my (attempt|take|depiction|version)|what i saw|"
                 r"recreat|visual(s|ization)?)\b", re.I)
NOT = re.compile(r"\b(meme|shitpost|for sale|shop|etsy|print available|commission)\b", re.I)


def load_vocab():
    vocab = json.load(open(os.path.join(C, "vocab.json"), encoding="utf-8"))
    pats = []
    for v in vocab:
        terms = [t for t in v["terms"] if len(t) >= 5]
        if terms:
            alt = "|".join(sorted((re.escape(t) for t in terms), key=len, reverse=True))
            pats.append((v["kind"], v["name"], re.compile(r"(?<![A-Za-z])(?:" + alt + r")(?![A-Za-z])", re.I)))
    return pats


def main():
    pats = load_vocab()
    files = sorted(glob.glob(os.path.join(C, "raw", "*_posts.jsonl")))
    cands = []
    for fp in files:
        sub = os.path.basename(fp).split("_")[0]
        for line in open(fp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            url = str(r.get("url") or "")
            media = (r.get("post_hint") in ("image", "hosted:video", "rich:video") or "reddit.com/gallery/" in url
                     or url.split("?")[0].lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4"))
                     or "i.redd.it" in url or "v.redd.it" in url or "imgur.com" in url or "youtu" in url)
            if not media:
                continue
            text = (r.get("title") or "") + "\n" + (r.get("selftext") or "") + "\n" + (r.get("link_flair_text") or "")
            if NOT.search(text):
                continue
            about_dmt = bool(DMT.search(text)) or sub.lower() == "dmt"
            arty = bool(ART.search(text)) or sub.lower() == "replications"
            if not (about_dmt and arty):
                continue
            nodes = [(k, n) for k, n, rx in pats if rx.search(text)]
            kind = "video" if (r.get("post_hint") in ("hosted:video", "rich:video") or "v.redd.it" in url or "youtu" in url) else \
                   "gallery" if "gallery/" in url else "image"
            cands.append({"id": r.get("id"), "sub": sub, "title": (r.get("title") or "")[:200], "author": r.get("author"),
                          "score": r.get("score") or 0, "created_utc": r.get("created_utc"), "kind": kind, "url": url,
                          "permalink": f"https://www.reddit.com/r/{sub}/comments/{r.get('id')}/",
                          "flair": r.get("link_flair_text"), "nodes": [f"{k}|{n}" for k, n in nodes]})
    cands.sort(key=lambda c: -c["score"])
    by_node = collections.defaultdict(list)
    for c in cands:
        for n in c["nodes"]:
            by_node[n].append(c["id"])
    out = {"candidates": len(cands), "by_sub": collections.Counter(c["sub"] for c in cands),
           "by_kind": collections.Counter(c["kind"] for c in cands),
           "nodes_covered": len(by_node), "per_node": {n: ids[:40] for n, ids in sorted(by_node.items(), key=lambda kv: -len(kv[1]))},
           "items": {c["id"]: c for c in cands}}
    json.dump(out, open(os.path.join(C, "depictions.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"depiction candidates: {len(cands):,}  by sub: {dict(out['by_sub'])}  kinds: {dict(out['by_kind'])}")
    print(f"atlas nodes with at least one depiction: {len(by_node)} / {len(pats)}")
    for n, ids in list(sorted(by_node.items(), key=lambda kv: -len(kv[1])))[:15]:
        print(f"  {len(ids):4d}  {n}")
    print("top candidates:")
    for c in cands[:10]:
        print(f"  {c['score']:6d} r/{c['sub']:<13} {c['kind']:<7} {c['title'][:70]}")


if __name__ == "__main__":
    main()
