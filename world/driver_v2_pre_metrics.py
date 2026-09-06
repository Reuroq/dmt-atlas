"""Drive Astra through the DMT world realism targets under REDIRECT5 — mechanically.

    python3 world/driver.py 47320 [max_turns] [--selftest]

What this driver enforces (the brief alone did not hold on Sep 5):
  * ORDER + BUDGET  — targets.json is the ledger; the driver owns `turns_used`, Astra owns `grade`/`note`.
                      Every PENDING target first in journey order, chrysanthemum last, BUDGET turns each.
  * RENDER OR FAIL  — latest.png must change every turn (sha1). One miss = warning prefix on the next
                      prompt; two consecutive misses forfeit the target (turns_used = BUDGET, note says so).
                      MAX_STRIKES misses in a row overall = stop (something is broken, a human should look).
  * SIZE GUARD      — after every turn delete any world/ subdirectory over DIR_CAP_MB (except vendor) and
                      any top-level file over FILE_CAP_MB (except data.js); stop if disk free < MIN_FREE_GB.
  * CLOSING TURN    — when no target has budget left, post one closing turn (coverage + acceptance +
                      WORLD_DONE), then exit.
Logs to world/driver.log. No gates on the model's judgment beyond these.
"""
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 47320
MAX_TURNS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 80
BASE = f"http://127.0.0.1:{PORT}"
HERE = Path(__file__).resolve().parent
LOG = HERE / "driver.log"
LEDGER = HERE / "targets.json"
LATEST = HERE / "latest.png"
NOTES = HERE / "NOTES.md"
POLL_S = 20

BUDGET = 4
MAX_STRIKES = 6
DIR_CAP_MB = 50
FILE_CAP_MB = 20
MIN_FREE_GB = 1.0
KEEP_DIRS = {"vendor", "__pycache__"}
KEEP_FILES = {"data.js", "fidelity-passages.jsonl"}  # the coverage test's passage corpus is 21 MB and legitimate

# Journey order; chrysanthemum (the target the Sep 5 run burned 60 turns on) goes last.
ORDER = ["onset", "geometry", "rush", "membrane", "waiting", "cathedral", "contact", "download",
         "return", "afterglow", "workshop", "garden", "clinical", "void",
         "elf", "jester", "mother", "mantis", "chrysanthemum"]

CONTINUE = (
    "Read world/REDIRECT5.md (the method, it replaces how you worked before), then world/targets.json, then ONLY "
    "the last section of world/NOTES.md. Work on the target named below and nothing else: render it at HIGH "
    "detail from a real journey pose (two frames, same camera, >=2 animation seconds apart), write the newest "
    "frame to world/latest.png, look at both frames, grade RECOGNISE/CLOSE/GAME with specific visual reasons, "
    "record grade+note in world/targets.json and the REALISM table, and if the grade is not RECOGNISE make ONE "
    "substantive visual change and re-render. No new harnesses, probes, fixtures, manifests or numerical checks. "
    "End the turn by rewriting the last section of world/NOTES.md (under 40 lines) and world/status.txt."
)
CLOSING = (
    "Every target now has a grade in world/targets.json. This is the closing turn. Run world/fidelity.py "
    "(coverage) and world/verify.py (acceptance) once each; fix only what they break; put the per-target grades "
    "and reasons into README.md and the Sources drawer table; update world/status.txt and world/latest.png with "
    "a final render. Then write <<WORLD_DONE>> alone on the last line of world/NOTES.md."
)
STRIKE_PREFIX = (
    "YOUR PREVIOUS TURN PRODUCED NO NEW RENDER: world/latest.png did not change, so the turn was invalid. "
    "First action this turn, before anything else: render the current target and overwrite world/latest.png. "
    "A second turn without a new render forfeits this target.\n\n"
)


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------- dashboard API ----------
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


# ---------- pure helpers (covered by --selftest) ----------
def sha1_of(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha1(path.read_bytes()).hexdigest()


def load_ledger(path: Path = LEDGER) -> dict:
    """targets.json = {target: {turns_used, grade, note}}. Missing/invalid -> fresh ledger, all PENDING."""
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as e:
            log(f"ledger unreadable ({e!r}); starting fresh")
            data = {}
    if not isinstance(data, dict):
        data = {}
    for t in ORDER:
        row = data.get(t) if isinstance(data.get(t), dict) else {}
        try:
            used = int(row.get("turns_used", 0))
        except Exception:
            used = 0
        data[t] = {"turns_used": max(0, used), "grade": str(row.get("grade", "PENDING") or "PENDING"),
                   "note": str(row.get("note", "") or "")}
    return data


def save_ledger(data: dict, path: Path = LEDGER) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def current_target(ledger: dict):
    """First target in ORDER with budget left, else None (=> closing turn)."""
    for t in ORDER:
        if ledger[t]["turns_used"] < BUDGET:
            return t
    return None


def pending_after(ledger: dict, target: str) -> list:
    seen = False
    out = []
    for t in ORDER:
        if t == target:
            seen = True
            continue
        if seen and ledger[t]["turns_used"] < BUDGET:
            out.append(t)
    return out


def compose_prompt(ledger: dict, target: str, strikes_on_target: int) -> str:
    row = ledger[target]
    head = (f"CURRENT TARGET: {target} — turn {row['turns_used'] + 1} of {BUDGET} on this target "
            f"(grade so far: {row['grade']}).")
    rest = pending_after(ledger, target)
    head += f" After it: {', '.join(rest)}." if rest else " It is the last target; the closing turn follows."
    prefix = STRIKE_PREFIX if strikes_on_target > 0 else ""
    return f"{prefix}{head}\n\n{CONTINUE}"


def size_guard(root: Path = HERE) -> list:
    """Delete oversize subdirs/files under world/. Returns a list of what was removed."""
    removed = []
    for p in sorted(root.iterdir()):
        try:
            if p.is_dir() and p.name not in KEEP_DIRS:
                mb = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6
                if mb > DIR_CAP_MB:
                    shutil.rmtree(p, ignore_errors=True)
                    removed.append(f"dir {p.name} {mb:.0f}MB")
            elif p.is_file() and p.name not in KEEP_FILES:
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
    """Finished only when the marker stands alone on its own line."""
    if not NOTES.exists():
        return False
    return any(line.strip() == "<<WORLD_DONE>>"
               for line in NOTES.read_text(encoding="utf-8", errors="replace").splitlines())


# ---------- main loop ----------
def main():
    log(f"driver v2 start, port {PORT}, max {MAX_TURNS} turns, budget {BUDGET}/target, order {ORDER}")
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
    strikes_total = 0
    strikes_on_target = 0
    last_target = None

    for turn in range(1, MAX_TURNS + 1):
        wait_idle()
        if turn > 1 and done():
            log("NOTES.md says WORLD_DONE; stopping")
            break
        free = disk_free_gb()
        if free < MIN_FREE_GB:
            log(f"disk free {free:.2f} GB < {MIN_FREE_GB} GB; stopping")
            break

        ledger = load_ledger()  # Astra may have written grade/note; turns_used stays ours
        target = current_target(ledger)
        if target is None:
            text = CLOSING
            log(f"turn {turn}: CLOSING (all targets graded: "
                + ", ".join(f"{t}={ledger[t]['grade']}" for t in ORDER) + ")")
        else:
            if target != last_target:
                strikes_on_target = 0
                last_target = target
            text = compose_prompt(ledger, target, strikes_on_target)
            log(f"turn {turn}: target {target} ({ledger[target]['turns_used'] + 1}/{BUDGET}, "
                f"grade {ledger[target]['grade']}, strikes {strikes_on_target})")

        before = sha1_of(LATEST)
        while True:
            code, r = post("/api/prompt", {"text": text})
            if code == 200 and r.get("ok"):
                log(f"posted turn {turn}")
                break
            log(f"post turn {turn} -> {code} {r}; retry")
            time.sleep(POLL_S)
        time.sleep(30)
        wait_idle()

        # --- after the turn: render check, ledger, size guard ---
        rendered = sha1_of(LATEST) != before
        ledger = load_ledger()
        if target is not None:
            if rendered:
                strikes_on_target = 0
                strikes_total = 0
                ledger[target]["turns_used"] += 1
            else:
                strikes_on_target += 1
                strikes_total += 1
                log(f"turn {turn}: NO NEW RENDER for {target} (strike {strikes_on_target})")
                if strikes_on_target >= 2:
                    ledger[target]["turns_used"] = BUDGET
                    ledger[target]["note"] = (ledger[target]["note"] + " | FORFEIT: no render in two consecutive turns").strip(" |")
                    log(f"turn {turn}: {target} forfeited")
            save_ledger(ledger)
        removed = size_guard()
        for item in removed:
            log(f"size guard removed {item}")
        try:
            st = get("/api/state")
            log(f"turn {turn} finished: rendered={rendered} ctx={st.get('ctx')} free={disk_free_gb():.1f}GB "
                f"rate={json.dumps(st.get('rate'))[:100]}")
        except Exception:
            log(f"turn {turn} finished: rendered={rendered}")
        if target is None:
            log("closing turn done; exit")
            break
        if strikes_total >= MAX_STRIKES:
            log(f"{MAX_STRIKES} turns in a row without a render; stopping for a human")
            break
    log("driver exit")


# ---------- selftest ----------
def selftest():
    import tempfile
    global HERE, LOG
    tmp = Path(tempfile.mkdtemp())
    LOG = tmp / "driver.log"
    fails = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # ledger: fresh, order, budget, closing
    led = load_ledger(tmp / "targets.json")
    check("fresh ledger has all targets PENDING", all(led[t]["grade"] == "PENDING" for t in ORDER))
    check("first target is onset", current_target(led) == "onset")
    led["onset"]["turns_used"] = BUDGET
    check("after onset budget -> geometry", current_target(led) == "geometry")
    check("chrysanthemum is last in order", ORDER[-1] == "chrysanthemum")
    for t in ORDER:
        led[t]["turns_used"] = BUDGET
    check("all spent -> closing (None)", current_target(led) is None)
    # ledger: Astra-written garbage does not break it
    (tmp / "bad.json").write_text("{not json", encoding="utf-8")
    check("invalid ledger -> fresh", current_target(load_ledger(tmp / "bad.json")) == "onset")
    (tmp / "partial.json").write_text(json.dumps({"rush": {"turns_used": "3", "grade": "CLOSE"}}), encoding="utf-8")
    p = load_ledger(tmp / "partial.json")
    check("partial ledger keeps rush 3/CLOSE, others PENDING", p["rush"]["turns_used"] == 3 and p["rush"]["grade"] == "CLOSE" and p["onset"]["grade"] == "PENDING")
    # prompt composition
    led = load_ledger(tmp / "targets.json")
    txt = compose_prompt(led, "onset", 0)
    check("prompt names target and budget", "CURRENT TARGET: onset — turn 1 of 4" in txt)
    check("prompt lists pending after", "After it: geometry, rush" in txt)
    check("no strike prefix at 0 strikes", not txt.startswith("YOUR PREVIOUS TURN"))
    check("strike prefix at 1 strike", compose_prompt(led, "onset", 1).startswith("YOUR PREVIOUS TURN"))
    for t in ORDER[:-1]:
        led[t]["turns_used"] = BUDGET
    check("last target says closing follows", "closing turn follows" in compose_prompt(led, "chrysanthemum", 0))
    # render detection
    png = tmp / "latest.png"
    png.write_bytes(b"a" * 10)
    h1 = sha1_of(png)
    png.write_bytes(b"b" * 10)
    check("sha1 changes when latest.png changes", sha1_of(png) != h1)
    check("missing file hashes to empty", sha1_of(tmp / "nope.png") == "")
    # size guard: an oversize dir goes, vendor stays, oversize file goes, data.js stays
    big = tmp / "centre-x"
    big.mkdir()
    (big / "blob.bin").write_bytes(b"\0" * (DIR_CAP_MB * 1_000_000 + 1))
    vend = tmp / "vendor"
    vend.mkdir()
    (vend / "blob.bin").write_bytes(b"\0" * (DIR_CAP_MB * 1_000_000 + 1))
    (tmp / "numeric-raw.json").write_bytes(b"\0" * (FILE_CAP_MB * 1_000_000 + 1))
    (tmp / "data.js").write_bytes(b"\0" * (FILE_CAP_MB * 1_000_000 + 1))
    (tmp / "small.json").write_bytes(b"\0" * 1000)
    removed = size_guard(tmp)
    check("oversize dir removed", not big.exists() and any(r.startswith("dir centre-x") for r in removed))
    check("vendor kept", vend.exists())
    check("oversize file removed", not (tmp / "numeric-raw.json").exists())
    check("data.js kept", (tmp / "data.js").exists())
    check("small file kept", (tmp / "small.json").exists())
    check("disk_free_gb positive", disk_free_gb(tmp) > 0)
    # done marker: alone on a line only
    global NOTES
    NOTES = tmp / "NOTES.md"
    NOTES.write_text("I will write <<WORLD_DONE>> later\n", encoding="utf-8")
    check("marker in a sentence is not done", not done())
    NOTES.write_text("all good\n<<WORLD_DONE>>\n", encoding="utf-8")
    check("marker alone is done", done())
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest: {len(fails)} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
