#!/usr/bin/env python3
"""ask_moderate.py — review the question board queue.

Nothing on /ask/ is public until it passes through here. The charter filter at
the door only catches what it can pattern-match; a human decides the rest.

    python ask_moderate.py                 list pending
    python ask_moderate.py --all           include rejected + published
    python ask_moderate.py --publish 12    publish question #12
    python ask_moderate.py --reject 12 "reason"
    python ask_moderate.py --demand        what the queue says people want
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from collections import Counter

_URL = os.environ.get("LEADS_SUPABASE_URL", "").rstrip("/")
_KEY = os.environ.get("LEADS_SUPABASE_KEY", "")
ENV_FALLBACK = r"C:/Users/dwayn/OneDrive/Desktop/workshield-product/.env.deploy"
TABLE = "atlas_questions"


def _creds():
    global _URL, _KEY
    if _URL and _KEY:
        return
    try:
        for line in open(ENV_FALLBACK, encoding="latin-1"):
            if line.startswith("LEADS_SUPABASE_URL="):
                _URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")
            elif line.startswith("LEADS_SUPABASE_KEY="):
                _KEY = line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass


def _req(path, method="GET", body=None, prefer=None):
    _creds()
    h = {"apikey": _KEY, "Authorization": "Bearer " + _KEY,
         "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    r = urllib.request.Request(_URL + "/rest/v1/" + path, method=method,
                               data=json.dumps(body).encode() if body else None,
                               headers=h)
    raw = urllib.request.urlopen(r, timeout=20).read()
    return json.loads(raw) if raw else []


def listq(statuses=("pending",)):
    f = "in.(%s)" % ",".join(statuses)
    rows = _req("%s?status=%s&order=ts.desc&limit=200&select=id,ts,status,theme,body,context,reject_reason"
                % (TABLE, urllib.parse.quote(f, safe="")))
    if not rows:
        print("  queue empty")
        return
    for r in rows:
        print("  #%-4s %-10s %-22s %s" % (r["id"], r["status"], r["theme"] or "-",
                                          r["ts"][:16].replace("T", " ")))
        print("        %s" % (r["body"] or "")[:150])
        if r.get("context"):
            print("        ctx: %s" % r["context"][:110])
        if r.get("reject_reason"):
            print("        rejected: %s" % r["reject_reason"])
        print()
    print("  %d shown" % len(rows))


def setstatus(qid, status, reason=""):
    body = {"status": status}
    if reason:
        body["reject_reason"] = reason
    _req("%s?id=eq.%d" % (TABLE, qid), method="PATCH", body=body,
         prefer="return=minimal")
    print("  #%d -> %s" % (qid, status))


def demand():
    """The queue is a demand log even when nothing gets published — including
    the rejections, which say what people want that this site won't serve."""
    rows = _req("%s?select=theme,status&limit=5000" % TABLE)
    if not rows:
        print("  no submissions yet")
        return
    by_theme = Counter(r["theme"] or "unsorted" for r in rows)
    by_status = Counter(r["status"] for r in rows)
    print("  submissions: %d" % len(rows))
    print("  by status:", dict(by_status))
    print("  by theme:")
    for t, n in by_theme.most_common():
        print("    %-24s %d" % (t, n))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--publish" in a:
        setstatus(int(a[a.index("--publish") + 1]), "published")
    elif "--reject" in a:
        i = a.index("--reject")
        setstatus(int(a[i + 1]), "rejected", a[i + 2] if len(a) > i + 2 else "manual")
    elif "--demand" in a:
        demand()
    elif "--all" in a:
        listq(("pending", "published", "rejected"))
    else:
        listq()
