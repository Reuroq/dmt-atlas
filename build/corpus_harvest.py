"""Harvest a subreddit's posts (and optionally comments) from the Arctic Shift archive API.

    python build/corpus_harvest.py posts DMT
    python build/corpus_harvest.py posts replications
    python build/corpus_harvest.py comments DMT --after 2015-01-01

Writes line-delimited JSON to data/corpus/raw/<sub>_<kind>.jsonl, resumable: on restart it
continues from the newest created_utc already on disk. Polite: one request at a time,
~0.7 s apart, exponential backoff on 422/429/5xx. No Reddit login, no scraping of reddit.com.
Field set is trimmed to what the atlas needs (text, title, flair, score, url, ids, dates).
Archive: https://github.com/ArthurHeitmann/arctic_shift (removal requests via its form).
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "dmtatlas-research/1.0 (+https://dmtatlas.com; non-commercial research index)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "corpus", "raw")
FIELDS = {  # only the API's selectable fields; permalink = /r/<sub>/comments/<id>/
    "posts": "id,created_utc,author,title,selftext,link_flair_text,score,num_comments,url,over_18,post_hint",
    "comments": "id,link_id,parent_id,created_utc,author,body,score",
}


def get(url: str, tries: int = 8):
    delay = 2.0
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:160]
            if e.code in (422, 429, 500, 502, 503, 504):
                print(f"  http {e.code} ({body}); backoff {delay:.0f}s", flush=True)
                time.sleep(delay); delay = min(delay * 2, 120)
                continue
            raise
        except Exception as e:  # network blip
            print(f"  {e!r}; backoff {delay:.0f}s", flush=True)
            time.sleep(delay); delay = min(delay * 2, 120)
    raise SystemExit("gave up after repeated failures")


def last_ts(path: str):
    if not os.path.exists(path):
        return None
    last = None
    with open(path, "rb") as f:
        try:
            f.seek(-8192, os.SEEK_END)
        except OSError:
            f.seek(0)
        for line in f.read().decode("utf-8", "replace").splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    last = json.loads(line).get("created_utc", last)
                except ValueError:
                    pass
    return last


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("posts", "comments"))
    ap.add_argument("subreddit")
    ap.add_argument("--after", help="ISO date to start from (default: resume from file, else subreddit start)")
    ap.add_argument("--before", help="ISO date to stop at")
    ap.add_argument("--pause", type=float, default=0.7)
    ap.add_argument("--max-pages", type=int, default=0)
    a = ap.parse_args()

    os.makedirs(RAW, exist_ok=True)
    out = os.path.join(RAW, f"{a.subreddit}_{a.kind}.jsonl")
    after = a.after
    resume = last_ts(out)
    if resume and not a.after:
        after = str(int(resume) + 1)  # epoch seconds accepted as Date
        print(f"resuming after {time.strftime('%Y-%m-%d', time.gmtime(int(resume)))}")
    n = pages = 0
    t0 = time.time()
    with open(out, "a", encoding="utf-8") as f:
        while True:
            q = {"subreddit": a.subreddit, "limit": "auto", "sort": "asc", "fields": FIELDS[a.kind]}
            if after: q["after"] = after
            if a.before: q["before"] = a.before
            url = f"{BASE}/{a.kind}/search?" + urllib.parse.urlencode(q)
            d = get(url)
            rows = d.get("data") or []
            if not rows:
                break
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            n += len(rows); pages += 1
            newest = rows[-1]["created_utc"]
            after = str(int(newest) + 1)
            if pages % 10 == 0 or pages == 1:
                print(f"{a.subreddit}/{a.kind}: {n:,} rows, {pages} pages, at {time.strftime('%Y-%m-%d', time.gmtime(newest))}, "
                      f"{(time.time()-t0)/60:.1f} min", flush=True)
            if a.max_pages and pages >= a.max_pages:
                break
            time.sleep(a.pause)
    print(f"done: {n:,} new rows -> {out}")


if __name__ == "__main__":
    main()
