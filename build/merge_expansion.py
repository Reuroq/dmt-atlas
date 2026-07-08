"""merge_expansion.py — fold the research agents' expansion JSON into data/atlas.json.

Rules (honesty-gated):
  - atlas.json backed up once to data/atlas_v1_backup.json
  - sources_new: first-wins on key collisions (collisions logged for review)
  - nodes (entities/realms/geometries/themes/motifs): skip if a same-name node exists
    (case-insensitive); every node's source_keys must resolve or the node is dropped+logged
  - data_points: deduped on (claim, source_key)
  - augments: appended to the target node as `also_noted` paragraphs + extra sources
  - red-flag audit (report-only): guidance-style phrasing gets listed for human review

    python build/merge_expansion.py            # merge everything in data/expansion/
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EXP = DATA / "expansion"
ATLAS = DATA / "atlas.json"
BACKUP = DATA / "atlas_v1_backup.json"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATS = ("entities", "realms", "geometries", "themes", "motifs")
RED_FLAGS = re.compile(
    r"\b(how to (?:take|smoke|vape|extract|make|dose)|recommended dose|start with \d|"
    r"extraction (?:tek|guide|method)|recipe|you should (?:take|try|start))\b", re.I)


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    atlas = load(ATLAS)
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(atlas, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"backup -> {BACKUP.name}")
    src_keys = {s["key"] for s in atlas["sources"]}
    names = {c: {n["name"].strip().lower() for n in atlas.get(c, [])} for c in CATS}
    dp_seen = {(d["claim"].strip().lower(), d["source_key"]) for d in atlas["data_points"]}
    atlas.setdefault("motifs", [])

    stats = {"sources": 0, "data_points": 0, "augments": 0, "dropped": [],
             "collisions": [], "flags": []}
    for c in CATS:
        stats[c] = 0

    files = sorted(EXP.glob("*.json"))
    if not files:
        sys.exit("no expansion files found")
    print(f"merging {len(files)} expansion files: {[f.name for f in files]}")

    # pass 1: all new sources first, so cross-file citations resolve
    payloads = {}
    for f in files:
        try:
            payloads[f.name] = load(f)
        except ValueError as e:
            print(f"  !! {f.name}: invalid JSON ({e}) — SKIPPED")
    for fname, p in payloads.items():
        for s in p.get("sources_new") or []:
            k = s.get("key", "").strip()
            if not k or not s.get("work"):
                continue
            if k in src_keys:
                stats["collisions"].append(f"{fname}: source key '{k}' already exists")
                continue
            atlas["sources"].append({kk: s.get(kk, "") for kk in
                                     ("key", "author", "work", "year", "type", "note", "url") if s.get(kk) or kk != "url"})
            src_keys.add(k)
            stats["sources"] += 1

    def sources_ok(node, fname, label):
        srcs = node.get("sources") or []
        bad = [s.get("source_key") for s in srcs if s.get("source_key") not in src_keys]
        if bad:
            stats["dropped"].append(f"{fname}: {label} '{node.get('name', node.get('claim','?'))}' "
                                    f"unresolvable keys {bad}")
            return False
        return True

    # pass 2: nodes + data points + augments
    for fname, p in payloads.items():
        for c in CATS:
            for n in p.get(c) or []:
                nm = (n.get("name") or "").strip()
                if not nm:
                    continue
                if nm.lower() in names[c]:
                    stats["collisions"].append(f"{fname}: {c} '{nm}' already exists — skipped")
                    continue
                if not sources_ok(n, fname, c):
                    continue
                txt = json.dumps(n, ensure_ascii=False)
                if RED_FLAGS.search(txt):
                    stats["flags"].append(f"{fname}: {c} '{nm}' — review wording")
                atlas[c].append(n)
                names[c].add(nm.lower())
                stats[c] += 1
        for d in p.get("data_points") or []:
            key = ((d.get("claim") or "").strip().lower(), d.get("source_key"))
            if not key[0] or key in dp_seen:
                continue
            if d.get("source_key") not in src_keys:
                stats["dropped"].append(f"{fname}: data_point '{d.get('claim','?')[:60]}' bad key")
                continue
            atlas["data_points"].append(d)
            dp_seen.add(key)
            stats["data_points"] += 1
        for a in p.get("augments") or []:
            nm = (a.get("name") or "").strip().lower()
            cat = a.get("category")
            if cat not in CATS:                    # infer category by name lookup
                cat = next((c for c in CATS
                            if any(n["name"].strip().lower() == nm for n in atlas.get(c, []))), None)
            tgt = next((n for n in atlas.get(cat, []) if n["name"].strip().lower() == nm), None) if cat else None
            if not tgt:
                stats["dropped"].append(f"{fname}: augment target '{a.get('name')}' not found")
                continue
            detail = a.get("add_detail") or a.get("note")
            if detail:
                tgt.setdefault("also_noted", []).append(detail)
            existing = {(s.get("source_key"), (s.get("detail") or "")[:40]) for s in tgt.get("sources", [])}
            for s in a.get("add_sources") or a.get("sources") or []:
                if s.get("source_key") in src_keys and \
                        (s.get("source_key"), (s.get("detail") or "")[:40]) not in existing:
                    tgt.setdefault("sources", []).append(s)
            stats["augments"] += 1

    ATLAS.write_text(json.dumps(atlas, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nMERGED:")
    for k in ("sources", "entities", "realms", "geometries", "themes", "motifs", "data_points", "augments"):
        print(f"  +{stats[k]} {k}")
    print(f"totals now: " + ", ".join(f"{k}={len(atlas[k])}" for k in
          ("sources", "entities", "realms", "geometries", "themes", "motifs", "data_points", "phases")))
    if stats["collisions"]:
        print(f"\ncollisions ({len(stats['collisions'])}):")
        for c in stats["collisions"][:20]:
            print("  -", c)
    if stats["dropped"]:
        print(f"\ndropped ({len(stats['dropped'])}):")
        for d in stats["dropped"][:20]:
            print("  -", d)
    if stats["flags"]:
        print(f"\n⚠ REVIEW WORDING ({len(stats['flags'])}):")
        for f in stats["flags"]:
            print("  -", f)


if __name__ == "__main__":
    main()
