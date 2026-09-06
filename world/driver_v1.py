"""Keep Astra going on the DMT world: one brief, then 'continue' whenever it goes idle, until it says done.

    python world/driver.py 47320 [max_turns]

No gates, no phases. Posts world/BRIEF.md as the first prompt; after each turn ends, if NOTES.md does not
contain <<WORLD_DONE>>, posts a continue prompt. Logs to world/driver.log.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 47320
MAX_TURNS = int(sys.argv[2]) if len(sys.argv) > 2 else 24
BASE = f"http://127.0.0.1:{PORT}"
HERE = Path(__file__).resolve().parent
LOG = HERE / "driver.log"
POLL_S = 20

FIRST = ("Read world\\BRIEF.md in full, then the research files it lists. Then build a 3D rendition of this research "
         "that people can move through in a browser. Everything about how is your decision. Keep world\\status.txt and "
         "world\\latest.png current as you go. When you have taken it as far as you can this turn, write world\\NOTES.md "
         "(what you did, what is next). Say <<WORLD_DONE>> only when you consider the world finished.")
CONTINUE = ("Continue building the DMT journey. Read world\\NOTES.md (your own notes), then world\\REDIRECT4.md (the bar: as "
            "real visually as what people see, the realism gate), REDIRECT3.md (the coverage test) and REDIRECT2.md, then keep "
            "going with your own plan. Keep status.txt and latest.png current; rewrite NOTES.md at the end of the turn. Put "
            "<<WORLD_DONE>> alone on the last line of NOTES.md only when every stage and being is RECOGNISE, the coverage test "
            "passes on every stage, and the acceptance still passes.")


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


def done():
    """Finished only when the marker stands alone on its own line (a sentence mentioning it does not count)."""
    p = HERE / "NOTES.md"
    if not p.exists():
        return False
    return any(line.strip() == "<<WORLD_DONE>>" for line in p.read_text(encoding="utf-8", errors="replace").splitlines())


def main():
    global FIRST
    if len(sys.argv) > 3:  # optional: a file whose text replaces the first prompt (a redirect)
        FIRST = Path(sys.argv[3]).read_text(encoding="utf-8")
    log(f"driver start, port {PORT}, max {MAX_TURNS} turns")
    for _ in range(40):
        try:
            st = get("/api/state"); log(f"dashboard up: model={st.get('model')} effort={st.get('effort')} cwd={st.get('cwd')}")
            break
        except Exception:
            time.sleep(15)
    for cmd in ("/effort high", "/cap 60000"):
        log(f"cmd {cmd} -> {post('/api/cmd', {'line': cmd})}")
    for turn in range(1, MAX_TURNS + 1):
        wait_idle()
        if turn > 1 and done():
            log("NOTES.md says WORLD_DONE; stopping"); break
        text = FIRST if turn == 1 else CONTINUE
        while True:
            code, r = post("/api/prompt", {"text": text})
            if code == 200 and r.get("ok"):
                log(f"posted turn {turn}"); break
            log(f"post turn {turn} -> {code} {r}; retry"); time.sleep(POLL_S)
        time.sleep(30)
        wait_idle()
        try:
            st = get("/api/state"); log(f"turn {turn} finished: ctx={st.get('ctx')} rate={json.dumps(st.get('rate'))[:120]}")
        except Exception:
            log(f"turn {turn} finished")
    log("driver exit")


if __name__ == "__main__":
    main()
