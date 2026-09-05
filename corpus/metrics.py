"""Tokens per accepted artifact — the metric that matters for an autonomous run.

The single_gpt dashboard appends one row per prompt-turn to usage.jsonl (ts, cwd, input, cached, output,
reasoning, tokens, cost, ctx_last, iterations). `cached` is a SUBSET of `input`. A driver turn = one prompt-turn
(plus occasional zero-token rows). This module attributes those rows to driver turns by time window + cwd, appends
one line per turn to metrics.jsonl, and regenerates METRICS.md with the per-unit table and the headline curve:
tokens per closed unit (target or phase) and tokens per productive turn.

    python3 metrics.py --selftest
    python3 metrics.py --backfill DRIVER_LOG CWD METRICS_JSONL LEDGER_JSON UNIT_WORD DATE   (one-time, from a driver.log)
"""
import json
import re
import statistics
import sys
import time
from pathlib import Path

USAGE = Path("/home/clawd/single_gpt/usage.jsonl")
CODEX_SESSIONS = Path("/home/clawd/.codex/sessions")
ISO = "%Y-%m-%dT%H:%M:%S"


def now_iso() -> str:
    return time.strftime(ISO)


def _iso_epoch(s: str) -> float:
    return time.mktime(time.strptime(s[:19], ISO))


def codex_rows(cwd: str, t0: str, t1: str, root: Path = CODEX_SESSIONS) -> list:
    """Ground truth: Codex's own rollout logs. Every `token_count` event carries `last_token_usage` for one API
    request (input incl. cached, output, reasoning) with a UTC timestamp. Sum the events inside [t0, t1] from
    sessions whose cwd matches. The dashboard's usage.jsonl logs zeros on rollover turns; this does not."""
    out = []
    if not root.exists():
        return out
    t0e = _iso_epoch(t0) - 120  # a session file may predate the window by a little; mtime must be >= t0
    for f in root.rglob("rollout-*.jsonl"):
        try:
            if f.stat().st_mtime < t0e:
                continue
            with f.open(encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
                try:
                    meta = json.loads(first)
                except Exception:
                    continue
                if (meta.get("payload") or {}).get("cwd") != cwd:
                    continue
                for line in fh:
                    if '"token_count"' not in line:
                        continue
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    ts = str(e.get("timestamp", ""))[:19]
                    if not (t0 <= ts <= t1):
                        continue
                    info = ((e.get("payload") or {}).get("info") or {})
                    u = info.get("last_token_usage") or {}
                    if not u:
                        continue
                    out.append({"ts": ts, "cwd": cwd, "input": u.get("input_tokens", 0), "cached": u.get("cached_input_tokens", 0),
                                "output": u.get("output_tokens", 0), "reasoning": u.get("reasoning_output_tokens", 0),
                                "cost": 0.0, "iterations": 1, "session": f.name})
        except Exception:
            continue
    return out


def usage_rows(cwd: str, t0: str, t1: str, usage: Path = USAGE) -> list:
    """Rows for this cwd whose ts falls in [t0, t1]. ISO strings compare lexically."""
    out = []
    if not usage.exists():
        return out
    for line in usage.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("cwd") == cwd and t0 <= str(r.get("ts", "")) <= t1:
            out.append(r)
    return out


def summarize(rows: list) -> dict:
    s = {"requests": len(rows), "iterations": 0, "input": 0, "cached": 0, "output": 0, "reasoning": 0, "cost": 0.0}
    for r in rows:
        s["iterations"] += int(r.get("iterations") or 0)
        for k in ("input", "cached", "output", "reasoning"):
            s[k] += int(r.get(k) or 0)
        s["cost"] += float(r.get("cost") or 0)
    s["tokens"] = s["input"] + s["output"] + s["reasoning"]  # cached is inside input
    s["cost"] = round(s["cost"], 4)
    return s


def append(metrics_path: Path, row: dict) -> None:
    with metrics_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load(metrics_path: Path) -> list:
    if not metrics_path.exists():
        return []
    out = []
    for line in metrics_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def render_md(metrics_path: Path, ledger: dict, unit_word: str, budget: int, out_md: Path, order: list) -> dict:
    """Per-unit table + headline. ledger[unit] has turns_used and grade (world) or status (corpus)."""
    rows = load(metrics_path)
    per = {}
    for r in rows:
        u = r.get("unit") or "?"
        p = per.setdefault(u, {"turns": 0, "productive": 0, "tokens": 0, "cached": 0, "input": 0, "output": 0,
                               "reasoning": 0, "requests": 0, "cost": 0.0})
        p["turns"] += 1
        p["productive"] += 1 if r.get("productive") else 0
        for k in ("tokens", "cached", "input", "output", "reasoning", "requests"):
            p[k] += int(r.get(k) or 0)
        p["cost"] += float(r.get("cost") or 0)
    total_tokens = sum(p["tokens"] for p in per.values())
    closed = [u for u in order if ledger.get(u, {}).get("turns_used", 0) >= budget]
    closed_tokens = sum(per.get(u, {}).get("tokens", 0) for u in closed)
    prod_turn_tokens = [r.get("tokens", 0) for r in rows if r.get("productive")]
    head = {
        "turns": len(rows),
        "productive_turns": sum(1 for r in rows if r.get("productive")),
        "total_tokens": total_tokens,
        "units_closed": len(closed),
        "tokens_per_closed_unit": int(closed_tokens / len(closed)) if closed else None,
        "median_tokens_per_productive_turn": int(statistics.median(prod_turn_tokens)) if prod_turn_tokens else None,
        "cached_share": round(sum(p["cached"] for p in per.values()) / max(1, sum(p["input"] for p in per.values())), 3),
    }
    srcs = {r.get("source", "usage") for r in rows}
    lines = [f"# Tokens per {unit_word} — measured from Codex's own session logs", "",
             f"Updated {now_iso()} UTC. Source: one `token_count` event per API request in ~/.codex/sessions "
             f"(rows from: {', '.join(sorted(srcs)) or 'none'}; 'usage' = the dashboard's usage.jsonl fallback, which "
             f"under-reports). Tokens = input + output + reasoning; cached is a share of input.", "",
             f"- Turns: **{head['turns']}** ({head['productive_turns']} productive)",
             f"- Total tokens: **{head['total_tokens']:,}**",
             f"- {unit_word.capitalize()}s closed: **{head['units_closed']}** of {len(order)}",
             f"- Tokens per closed {unit_word}: **{head['tokens_per_closed_unit']:,}**" if head['tokens_per_closed_unit'] else f"- Tokens per closed {unit_word}: n/a",
             f"- Median tokens per productive turn: **{head['median_tokens_per_productive_turn']:,}**" if head['median_tokens_per_productive_turn'] else "- Median tokens per productive turn: n/a",
             f"- Cached share of input: **{head['cached_share']:.0%}**", "",
             f"| {unit_word} | turns | productive | tokens | cached | output+reasoning | outcome |",
             "|---|---|---|---|---|---|---|"]
    for u in order:
        p = per.get(u)
        led = ledger.get(u, {})
        outcome = led.get("grade") or led.get("status") or "PENDING"
        if p:
            lines.append(f"| {u} | {p['turns']} | {p['productive']} | {p['tokens']:,} | "
                         f"{(p['cached'] / p['input']) if p['input'] else 0:.0%} | {p['output'] + p['reasoning']:,} | {outcome} |")
        else:
            lines.append(f"| {u} | 0 | 0 | 0 | | | {outcome} |")
    lines += ["", "## Curve — cumulative tokens per closed unit, in closing order", "",
              "| closed | unit | tokens this unit | cumulative tokens | tokens per closed unit so far |", "|---|---|---|---|---|"]
    cum = 0
    for i, u in enumerate(closed, 1):
        t = per.get(u, {}).get("tokens", 0)
        cum += t
        lines.append(f"| {i} | {u} | {t:,} | {cum:,} | {int(cum / i):,} |")
    lines += ["", "## Per turn", "", "| ts | turn | unit | k | productive | requests | tokens | cached | output+reasoning |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows[-80:]:
        lines.append(f"| {r.get('t1', '')[11:16]} | {r.get('turn')} | {r.get('unit')} | {r.get('k')} | {'yes' if r.get('productive') else 'NO'} | "
                     f"{r.get('requests')} | {int(r.get('tokens') or 0):,} | {int(r.get('cached') or 0):,} | {int(r.get('output') or 0) + int(r.get('reasoning') or 0):,} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return head


def turn_metric(turn: int, unit: str, k: int, productive: bool, t0: str, t1: str, cwd: str,
                usage: Path = USAGE, codex: Path = CODEX_SESSIONS) -> dict:
    rows = codex_rows(cwd, t0, t1, codex)
    source = "codex"
    if not rows:
        rows = usage_rows(cwd, t0, t1, usage)
        source = "usage"
    s = summarize(rows)
    return {"t0": t0, "t1": t1, "turn": turn, "unit": unit, "k": k, "productive": bool(productive), "source": source, **s}


def backfill(driver_log: Path, cwd: str, metrics_path: Path, unit_word: str, date: str,
             usage: Path = USAGE, codex: Path = CODEX_SESSIONS) -> int:
    """Reconstruct metrics rows from a driver.log written before metrics existed. Every driver run in the log
    (each ' start, port' line) is a segment whose turn numbers restart; rows are keyed by their posted timestamp,
    so re-running is idempotent. Runs without unit lines (the pre-REDIRECT5 driver) contribute nothing."""
    text = driver_log.read_text(encoding="utf-8", errors="replace").splitlines()
    posted = {}
    unit_of = {}
    rows = 0
    pat_unit = re.compile(rf"^(\d\d:\d\d:\d\d) turn (\d+): {unit_word} (\S+) \((\d+)/\d+")
    pat_post = re.compile(r"^(\d\d:\d\d:\d\d) posted turn (\d+)")
    pat_fin = re.compile(r"^(\d\d:\d\d:\d\d) turn (\d+) finished: (rendered|changed)=(\w+)")
    existing = {r.get("t0") for r in load(metrics_path)}
    for l in text:
        if " start, port" in l:
            posted, unit_of = {}, {}
            continue
        m = pat_unit.match(l)
        if m:
            unit_of[int(m.group(2))] = (m.group(3), int(m.group(4)))
            continue
        m = pat_post.match(l)
        if m:
            posted[int(m.group(2))] = f"{date}T{m.group(1)}"
            continue
        m = pat_fin.match(l)
        if m:
            n = int(m.group(2))
            if n not in posted or n not in unit_of or posted[n] in existing:
                continue
            t1 = f"{date}T{m.group(1)}"
            u, k = unit_of[n]
            append(metrics_path, turn_metric(n, u, k, m.group(4) == "True", posted[n], t1, cwd, usage, codex))
            existing.add(posted[n])
            rows += 1
    return rows


def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    usage = tmp / "usage.jsonl"
    fails = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    rows = [
        {"ts": "2026-09-05T20:00:10", "cwd": "/a", "input": 1000, "cached": 800, "output": 50, "reasoning": 20, "cost": 0.01, "iterations": 3},
        {"ts": "2026-09-05T20:03:00", "cwd": "/a", "input": 0, "cached": 0, "output": 0, "reasoning": 0, "cost": 0, "iterations": 1},
        {"ts": "2026-09-05T20:03:30", "cwd": "/b", "input": 5000, "cached": 0, "output": 5, "reasoning": 0, "cost": 0.05, "iterations": 1},
        {"ts": "2026-09-05T20:09:00", "cwd": "/a", "input": 2000, "cached": 1000, "output": 100, "reasoning": 40, "cost": 0.02, "iterations": 5},
    ]
    usage.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    got = usage_rows("/a", "2026-09-05T20:00:00", "2026-09-05T20:05:00", usage)
    check("window+cwd filter", len(got) == 2)
    s = summarize(got)
    check("tokens = input+output+reasoning", s["tokens"] == 1070 and s["cached"] == 800 and s["requests"] == 2)
    nocodex = tmp / "no_codex"
    m = tmp / "metrics.jsonl"
    append(m, turn_metric(1, "onset", 1, True, "2026-09-05T20:00:00", "2026-09-05T20:05:00", "/a", usage, nocodex))
    append(m, turn_metric(2, "onset", 2, False, "2026-09-05T20:05:01", "2026-09-05T20:10:00", "/a", usage, nocodex))
    check("falls back to usage when no codex logs", load(m)[0]["source"] == "usage")
    # codex rollout logs are the preferred source: one token_count event per API request, cwd in session_meta
    croot = tmp / "codex" / "2026" / "09" / "05"
    croot.mkdir(parents=True)

    def ev(ts, inp, cached, out, reas):
        return json.dumps({"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {}, "last_token_usage": {"input_tokens": inp, "cached_input_tokens": cached,
                                                          "output_tokens": out, "reasoning_output_tokens": reas}}}})
    (croot / "rollout-a.jsonl").write_text("\n".join([
        json.dumps({"timestamp": "2026-09-05T19:59:00.000Z", "type": "session_meta", "payload": {"cwd": "/a"}}),
        json.dumps({"timestamp": "2026-09-05T20:00:05.000Z", "type": "event_msg", "payload": {"type": "agent_message"}}),
        ev("2026-09-05T20:00:10.100Z", 1000, 900, 10, 5),
        ev("2026-09-05T20:03:00.500Z", 2000, 1900, 20, 0),
        ev("2026-09-05T20:07:00.000Z", 5000, 0, 1, 0),
    ]) + "\n", encoding="utf-8")
    (croot / "rollout-b.jsonl").write_text("\n".join([
        json.dumps({"timestamp": "2026-09-05T19:59:00.000Z", "type": "session_meta", "payload": {"cwd": "/other"}}),
        ev("2026-09-05T20:01:00.000Z", 99999, 0, 0, 0),
    ]) + "\n", encoding="utf-8")
    import os
    for f in croot.glob("*.jsonl"):  # the mtime prefilter must see these files as written after the window opened
        os.utime(f, (_iso_epoch("2026-09-05T20:10:00"), _iso_epoch("2026-09-05T20:10:00")))
    cr = codex_rows("/a", "2026-09-05T20:00:00", "2026-09-05T20:05:00", tmp / "codex")
    check("codex rows: window + cwd", len(cr) == 2 and sum(r["input"] for r in cr) == 3000)
    tmc = turn_metric(3, "geometry", 1, True, "2026-09-05T20:00:00", "2026-09-05T20:05:00", "/a", usage, tmp / "codex")
    check("codex preferred over usage", tmc["source"] == "codex" and tmc["tokens"] == 3035 and tmc["cached"] == 2800)
    led = {"onset": {"turns_used": 2, "grade": "GAME"}, "geometry": {"turns_used": 0, "grade": "PENDING"}}
    head = render_md(m, led, "target", 2, tmp / "M.md", ["onset", "geometry"])
    check("headline totals", head["turns"] == 2 and head["productive_turns"] == 1 and head["total_tokens"] == 1070 + 2140)
    check("tokens per closed unit", head["tokens_per_closed_unit"] == 3210 and head["units_closed"] == 1)
    md = (tmp / "M.md").read_text(encoding="utf-8")
    check("md has table rows", "| onset | 2 | 1 |" in md and "| geometry | 0 |" in md and "| 1 | onset |" in md)
    # backfill from a driver.log
    log = tmp / "driver.log"
    log.write_text("\n".join([
        "19:00:00 driver v2 start, port 1",
        "20:00:00 turn 1: target onset (1/4, grade PENDING, strikes 0)",
        "20:00:00 posted turn 1",
        "20:05:00 turn 1 finished: rendered=True ctx=1",
        "20:05:01 turn 2: target onset (2/4, grade GAME, strikes 0)",
        "20:05:01 posted turn 2",
        "20:10:00 turn 2 finished: rendered=False ctx=1",
    ]) + "\n", encoding="utf-8")
    m2 = tmp / "m2.jsonl"
    n = backfill(log, "/a", m2, "target", "2026-09-05", usage)
    bf = load(m2)
    check("backfill wrote 2 rows", n == 2 and len(bf) == 2)
    check("backfill tokens match", bf[0]["tokens"] == 1070 and bf[1]["tokens"] == 2140 and bf[1]["productive"] is False)
    check("backfill idempotent", backfill(log, "/a", m2, "target", "2026-09-05", usage) == 0)
    print(f"selftest: {len(fails)} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--backfill" in sys.argv:
        a = sys.argv[sys.argv.index("--backfill") + 1:]
        n = backfill(Path(a[0]), a[1], Path(a[2]), a[4], a[5])
        print(f"backfilled {n} rows into {a[2]}")
    else:
        print(__doc__)
