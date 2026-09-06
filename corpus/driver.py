"""Drive the corpus Astra through CORPUS.md phases — mechanically.

    python3 corpus/driver.py 47321 [max_turns] [--selftest]

Enforces: phase ORDER + BUDGET (turns per phase), ARTIFACT-OR-FAIL (one of the phase's artifact paths must
change on disk each turn; two misses in a row forfeit the phase), a SIZE GUARD (no file over FILE_CAP_MB
except records/*.jsonl, no subdir over DIR_CAP_MB), a disk floor, and a closing turn. Logs to corpus/driver.log.
"""
import hashlib
import importlib
import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402  (tokens per closed phase, from the dashboard's usage.jsonl)

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 47321
MAX_TURNS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 40
BASE = f"http://127.0.0.1:{PORT}"
HERE = Path(__file__).resolve().parent


def _opt(name: str, default: str) -> str:
    """--name VALUE anywhere in argv (a second run uses its own brief, ledger, phase spec and done marker)."""
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


BRIEF = _opt("--brief", "CORPUS.md")
DONE_MARK = _opt("--done", "<<CORPUS_DONE>>")
LOG = HERE / "driver.log"
LEDGER = HERE / _opt("--ledger", "phases.json")
NOTES = HERE / "NOTES.md"
METRICS = HERE / "metrics.jsonl"
METRICS_MD = HERE / "METRICS.md"
DASH_CWD = str(HERE)  # the corpus dashboard runs with --cwd corpus/
POLL_S = 20

BUDGET = 3
MAX_STRIKES = 6
DIR_CAP_MB = 200
FILE_CAP_MB = 25
MIN_FREE_GB = 1.0
KEEP_DIRS = {"records", "__pycache__"}

# (phase, [artifact globs relative to corpus/]) in order
PHASES = [
    ("schema",    ["schema.json", "SCHEMA.md", "vocab.json", "examples/*.json"]),
    ("harness",   ["extract.py"]),
    ("pilot",     ["PILOT.md", "records/*.jsonl", "extract.py", "schema.json"]),
    ("aggregate", ["aggregate.py", "distributions.json", "DISTRIBUTIONS.md"]),
    ("sampler",   ["sampler.js", "SAMPLER.md", "test_sampler.mjs", "INTEGRATION.md"]),
    ("fidelity",  ["fidelity_dist.py", "BLIND_TEST.md"]),
    ("refresh",   ["refresh.py", "refresh.timer", "refresh.service"]),
    ("report",    ["README.md"]),
]
_spec = HERE / _opt("--spec", "")
if _opt("--spec", "") and _spec.exists():  # a later run supplies its own phases: [[name, [globs...]], ...]
    PHASES = [(p, list(g)) for p, g in json.loads(_spec.read_text(encoding="utf-8"))]
ORDER = [p for p, _ in PHASES]
ARTIFACTS = dict(PHASES)

CONTINUE = (
    f"Read corpus/{BRIEF} (the brief), then corpus/{LEDGER.name}, then ONLY the last section of corpus/NOTES.md. "
    "Work on the phase named below and nothing else. The turn is valid only if one of the phase's artifacts changes "
    "on disk; the driver checks. Write only under corpus/. Never submit a Claude API batch without --budget-usd, and "
    "never beyond the pilot sizes and dollar caps the brief states. End the turn by rewriting the last section of "
    "corpus/NOTES.md (under 40 lines) and corpus/status.txt."
)
CLOSING = (
    "Every phase has had its budget. This is the closing turn: update corpus/README.md (what exists, how to run each "
    "piece, the pilot numbers, the exact command and projected cost for the full pass, what the world gains), update "
    f"corpus/status.txt, and write {DONE_MARK} alone on the last line of corpus/NOTES.md."
)
STRIKE_PREFIX = (
    "YOUR PREVIOUS TURN CHANGED NONE OF THIS PHASE'S ARTIFACTS, so it was invalid. First action this turn: produce or "
    "change one of the artifacts named below. A second turn without one forfeits the phase.\n\n"
)


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")
    except Exception as e:
        log(f"post raised {e!r}")
        time.sleep(5)
        try:
            if get("/api/state").get("busy"):
                return 200, {"ok": True}
        except Exception:
            pass
        return 599, {"ok": False}


def wait_idle():
    while True:
        try:
            if not get("/api/state").get("busy"):
                return
        except Exception as e:
            log(f"state error: {e!r}")
        time.sleep(POLL_S)


# ---------- pure helpers ----------
def artifact_state(phase: str, root: Path = HERE) -> dict:
    """{relative path: sha1} for every existing file matching the phase's globs."""
    out = {}
    for pat in ARTIFACTS[phase]:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def load_ledger(path: Path = LEDGER) -> dict:
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as e:
            log(f"ledger unreadable ({e!r}); starting fresh")
            data = {}
    if not isinstance(data, dict):
        data = {}
    for ph in ORDER:
        row = data.get(ph) if isinstance(data.get(ph), dict) else {}
        try:
            used = int(row.get("turns_used", 0))
        except Exception:
            used = 0
        data[ph] = {"turns_used": max(0, used), "status": str(row.get("status", "PENDING") or "PENDING"),
                    "note": str(row.get("note", "") or "")}
    # turns_used is the driver's number; the agent may rewrite phases.json, so the private copy wins.
    priv = path.with_suffix(".driver.json")
    if priv.exists():
        try:
            mine = json.loads(priv.read_text(encoding="utf-8"))
            for ph in ORDER:
                if isinstance(mine.get(ph), int):
                    data[ph]["turns_used"] = max(0, mine[ph])
        except Exception as e:
            log(f"private ledger unreadable ({e!r}); using phases.json counts")
    return data


def save_ledger(data: dict, path: Path = LEDGER) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    path.with_suffix(".driver.json").write_text(
        json.dumps({ph: data[ph]["turns_used"] for ph in ORDER}, indent=1), encoding="utf-8")


def current_phase(ledger: dict):
    for ph in ORDER:
        if ledger[ph]["turns_used"] < BUDGET:
            return ph
    return None


def compose_prompt(ledger: dict, phase: str, strikes: int) -> str:
    row = ledger[phase]
    later = [p for p in ORDER[ORDER.index(phase) + 1:] if ledger[p]["turns_used"] < BUDGET]
    head = (f"CURRENT PHASE: {phase} — turn {row['turns_used'] + 1} of {BUDGET} on this phase. "
            f"Artifacts that must change this turn (any one): {', '.join(ARTIFACTS[phase])}.")
    head += f" Phases after it: {', '.join(later)}." if later else " It is the last phase; the closing turn follows."
    return (STRIKE_PREFIX if strikes > 0 else "") + head + "\n\n" + CONTINUE


def size_guard(root: Path = HERE) -> list:
    removed = []
    for p in sorted(root.iterdir()):
        try:
            if p.is_dir() and p.name not in KEEP_DIRS:
                mb = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6
                if mb > DIR_CAP_MB:
                    shutil.rmtree(p, ignore_errors=True)
                    removed.append(f"dir {p.name} {mb:.0f}MB")
            elif p.is_file():
                mb = p.stat().st_size / 1e6
                if mb > FILE_CAP_MB:
                    p.unlink()
                    removed.append(f"file {p.name} {mb:.0f}MB")
        except Exception as e:
            removed.append(f"error {p.name}: {e!r}")
    return removed


def disk_free_gb(path: Path = HERE) -> float:
    return shutil.disk_usage(str(path)).free / 1e9


def done() -> bool:
    if not NOTES.exists():
        return False
    return any(line.strip() == DONE_MARK
               for line in NOTES.read_text(encoding="utf-8", errors="replace").splitlines())


# ---------- main ----------
def main():
    log(f"corpus driver start, port {PORT}, max {MAX_TURNS} turns, budget {BUDGET}/phase, phases {ORDER}")
    for _ in range(40):
        try:
            st = get("/api/state")
            log(f"dashboard up: model={st.get('model')} effort={st.get('effort')} cwd={st.get('cwd')}")
            break
        except Exception:
            time.sleep(15)
    for cmd in ("/effort high", "/cap 60000"):
        log(f"cmd {cmd} -> {post('/api/cmd', {'line': cmd})}")
    ledger = load_ledger()
    save_ledger(ledger)
    strikes = strikes_total = 0
    last_phase = None
    first = True
    # Count a turn left in flight by a previous driver (restart mid-run) against the current phase.
    try:
        if get("/api/state").get("busy"):
            t0 = metrics.now_iso()
            ph0 = current_phase(load_ledger())
            before0 = artifact_state(ph0) if ph0 else {}
            log("dashboard busy at start: waiting for the in-flight turn and counting it against the current phase")
            wait_idle()
            ledger = load_ledger()
            if ph0:
                changed0 = artifact_state(ph0) != before0
                k0 = ledger[ph0]["turns_used"] + 1
                ledger[ph0]["turns_used"] += 1
                if ledger[ph0]["status"] == "PENDING":
                    ledger[ph0]["status"] = "IN_PROGRESS"
                save_ledger(ledger)
                metrics.append(METRICS, metrics.turn_metric(0, ph0, k0, changed0, t0, metrics.now_iso(), DASH_CWD))
                metrics.render_md(METRICS, ledger, "phase", BUDGET, METRICS_MD, ORDER)
                log(f"in-flight turn counted for {ph0} ({k0}/{BUDGET}, changed={changed0} over a partial window)")
                first = False
    except Exception as e:
        log(f"resume check failed: {e!r}")
    for turn in range(1, MAX_TURNS + 1):
        wait_idle()
        if turn > 1 and done():
            log("NOTES.md says CORPUS_DONE; stopping")
            break
        free = disk_free_gb()
        if free < MIN_FREE_GB:
            log(f"disk free {free:.2f} GB < {MIN_FREE_GB}; stopping")
            break
        ledger = load_ledger()
        phase = current_phase(ledger)
        if phase is None:
            text = CLOSING
            log(f"turn {turn}: CLOSING (" + ", ".join(f"{p}={ledger[p]['status']}" for p in ORDER) + ")")
        else:
            if phase != last_phase:
                strikes, last_phase = 0, phase
            text = compose_prompt(ledger, phase, strikes)
            if first:
                text = (f"Read corpus/{BRIEF} in full first; it is your brief. Read ../BUILD.md for the honesty charter. "
                        "Then:\n\n" + text)
                first = False
            log(f"turn {turn}: phase {phase} ({ledger[phase]['turns_used'] + 1}/{BUDGET}, strikes {strikes})")
        before = artifact_state(phase) if phase else {}
        k_on = (ledger[phase]["turns_used"] + 1) if phase else 0
        try:
            importlib.reload(metrics)  # pick up metric fixes without restarting the run
        except Exception as e:
            log(f"metrics reload failed: {e!r}")
        t0 = metrics.now_iso()
        while True:
            code, r = post("/api/prompt", {"text": text})
            if code == 200 and r.get("ok"):
                log(f"posted turn {turn}")
                break
            log(f"post turn {turn} -> {code} {r}; retry")
            time.sleep(POLL_S)
        time.sleep(30)
        wait_idle()
        t1 = metrics.now_iso()
        ledger = load_ledger()
        changed = False
        if phase is not None:
            after = artifact_state(phase)
            changed = after != before
            if changed:
                strikes = strikes_total = 0
                ledger[phase]["turns_used"] += 1
                if ledger[phase]["status"] == "PENDING":
                    ledger[phase]["status"] = "IN_PROGRESS"
            else:
                strikes += 1
                strikes_total += 1
                log(f"turn {turn}: NO ARTIFACT CHANGE for {phase} (strike {strikes})")
                if strikes >= 2:
                    ledger[phase]["turns_used"] = BUDGET
                    ledger[phase]["status"] = "FORFEIT"
                    ledger[phase]["note"] = (ledger[phase]["note"] + " | FORFEIT: no artifact in two turns").strip(" |")
                    log(f"turn {turn}: {phase} forfeited")
            save_ledger(ledger)
        tok = {}
        try:
            row = metrics.turn_metric(turn, phase or "closing", k_on, changed, t0, t1, DASH_CWD)
            metrics.append(METRICS, row)
            head = metrics.render_md(METRICS, ledger, "phase", BUDGET, METRICS_MD, ORDER)
            tok = {"tokens": row["tokens"], "cached": row["cached"], "out": row["output"] + row["reasoning"],
                   "per_closed_phase": head.get("tokens_per_closed_unit")}
        except Exception as e:
            log(f"metrics failed: {e!r}")
        for item in size_guard():
            log(f"size guard removed {item}")
        try:
            st = get("/api/state")
            log(f"turn {turn} finished: changed={changed} tokens={tok.get('tokens')} cached={tok.get('cached')} "
                f"out={tok.get('out')} per_closed_phase={tok.get('per_closed_phase')} ctx={st.get('ctx')} "
                f"free={disk_free_gb():.1f}GB rate={json.dumps(st.get('rate'))[:100]}")
        except Exception:
            log(f"turn {turn} finished: changed={changed} tokens={tok.get('tokens')}")
        if phase is None:
            log("closing turn done; exit")
            break
        if strikes_total >= MAX_STRIKES:
            log(f"{MAX_STRIKES} turns without an artifact; stopping for a human")
            break
    log("driver exit")


def selftest():
    import tempfile
    global LOG, NOTES
    tmp = Path(tempfile.mkdtemp())
    LOG = tmp / "driver.log"
    fails = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    led = load_ledger(tmp / "phases.json")
    check("first phase is schema", current_phase(led) == "schema")
    for p in ORDER[:-1]:
        led[p]["turns_used"] = BUDGET
    check("last phase is report", current_phase(led) == "report")
    led["report"]["turns_used"] = BUDGET
    check("all spent -> closing", current_phase(led) is None)
    (tmp / "bad.json").write_text("{nope", encoding="utf-8")
    check("invalid ledger -> fresh", current_phase(load_ledger(tmp / "bad.json")) == "schema")
    lp = load_ledger(tmp / "priv.json")
    lp["schema"]["turns_used"] = 2
    save_ledger(lp, tmp / "priv.json")
    (tmp / "priv.json").write_text(json.dumps({"schema": {"turns_used": 7, "status": "DONE", "note": "agent"}}), encoding="utf-8")
    lp2 = load_ledger(tmp / "priv.json")
    check("private turns_used wins, status from shared file", lp2["schema"]["turns_used"] == 2 and lp2["schema"]["status"] == "DONE")
    # artifact detection with globs
    (tmp / "examples").mkdir()
    s0 = artifact_state("schema", tmp)
    check("no artifacts yet", s0 == {})
    (tmp / "schema.json").write_text("{}", encoding="utf-8")
    s1 = artifact_state("schema", tmp)
    check("new artifact detected", s1 != s0 and "schema.json" in s1)
    (tmp / "examples" / "a.json").write_text("{}", encoding="utf-8")
    s2 = artifact_state("schema", tmp)
    check("glob subdir artifact detected", s2 != s1 and any(k.endswith("a.json") for k in s2))
    (tmp / "schema.json").write_text("{\"x\":1}", encoding="utf-8")
    check("modified artifact detected", artifact_state("schema", tmp) != s2)
    check("other phase unaffected", artifact_state("harness", tmp) == {})
    # prompts
    led = load_ledger(tmp / "phases.json")
    t = compose_prompt(led, "schema", 0)
    check("prompt names phase + artifacts", "CURRENT PHASE: schema" in t and "schema.json" in t)
    check("strike prefix", compose_prompt(led, "schema", 1).startswith("YOUR PREVIOUS TURN"))
    # size guard
    big = tmp / "junk"; big.mkdir()
    (big / "b.bin").write_bytes(b"\0" * (DIR_CAP_MB * 1_000_000 + 1))
    rec = tmp / "records"; rec.mkdir()
    (rec / "r.jsonl").write_bytes(b"\0" * (DIR_CAP_MB * 1_000_000 + 1))
    (tmp / "huge.json").write_bytes(b"\0" * (FILE_CAP_MB * 1_000_000 + 1))
    removed = size_guard(tmp)
    check("oversize dir removed", not big.exists())
    check("records kept", rec.exists())
    check("oversize file removed", not (tmp / "huge.json").exists())
    check("disk free positive", disk_free_gb(tmp) > 0)
    NOTES = tmp / "NOTES.md"
    NOTES.write_text(f"soon {DONE_MARK}\n", encoding="utf-8")
    check("marker in sentence not done", not done())
    NOTES.write_text(f"x\n{DONE_MARK}\n", encoding="utf-8")
    check("marker alone is done", done())
    check("brief/ledger/done defaults", BRIEF == "CORPUS.md" and LEDGER.name == "phases.json" and DONE_MARK == "<<CORPUS_DONE>>")
    check("CONTINUE names the brief and ledger", f"corpus/{BRIEF}" in CONTINUE and LEDGER.name in CONTINUE)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest: {len(fails)} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
