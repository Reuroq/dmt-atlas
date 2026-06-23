"""Pull each research agent's final JSON out of its task .output transcript,
without loading the (huge) transcripts into the assistant's context."""
import json, re, os, sys

TASKS = r"C:\Users\dwayn\AppData\Local\Temp\claude\c--Users-dwayn-testing1-Polymarket\60c8664f-c4e8-47f6-90ae-a24233468b5b\tasks"
OUT = r"C:\Users\dwayn\OneDrive\Desktop\HyperspaceAtlas\data\raw"
os.makedirs(OUT, exist_ok=True)

JOBS = {
    "mckenna":      "af87108e8dc5273be.output",
    "clinical":     "a7cb2226b0e0c4715.output",
    "crosscultural":"af965c9c5be467fbf.output",
    "community":    "a105d24a11939621d.output",
    "entities":     "ae7201f55cfddd3ac.output",
    "realms":       "ab9acb951d2dae01c.output",
}

def collect_strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_strings(v, out)

def extract_json_from_text(text):
    # prefer a ```json fenced block
    m = re.findall(r"```json\s*(.*?)```", text, re.DOTALL)
    cands = list(m)
    # also try the largest brace-balanced object containing "sources"
    if not cands:
        cands = [text]
    best = None
    for c in cands:
        c = c.strip()
        # trim to first { ... last }
        i, j = c.find("{"), c.rfind("}")
        if i == -1 or j == -1:
            continue
        frag = c[i:j+1]
        try:
            obj = json.loads(frag)
            if isinstance(obj, dict) and ("sources" in obj or "entities" in obj):
                if best is None or len(frag) > best[1]:
                    best = (obj, len(frag))
        except Exception:
            continue
    return best[0] if best else None

summary = {}
for name, fn in JOBS.items():
    path = os.path.join(TASKS, fn)
    if not os.path.exists(path):
        summary[name] = "MISSING FILE"
        continue
    texts = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except Exception:
                texts.append(line)  # not JSONL? keep raw
                continue
            collect_strings(evt, texts)
    # pick the longest text that yields a valid atlas json
    texts.sort(key=len, reverse=True)
    obj = None
    for t in texts[:12]:
        obj = extract_json_from_text(t)
        if obj:
            break
    if not obj:
        summary[name] = "NO JSON FOUND"
        continue
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    summary[name] = {k: len(obj.get(k, [])) for k in
                     ["entities","realms","geometries","phases","themes","data_points","sources"]}

for k, v in summary.items():
    print(f"{k:14s} {v}")
