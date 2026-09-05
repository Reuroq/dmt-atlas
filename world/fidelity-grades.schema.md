# Manual fidelity review receipts

`fidelity.py` measures lexical evidence; it does not see or auto-grade renders.
Keep reviews in `fidelity-grades.json`. Never fill PRESENT from code inspection.

## Validate passages before grading visuals

Run `python world/fidelity.py --queue`. For each target, read its windows in the
listed order (60 at a time, all 27 candidates for Garden). Add records to
`fidelity-passage-review.json` → `targets` → target → `sub/id`:

```json
{"decision":"include", "reason":"First-person description of this stage, not ordinary surroundings or a different phase", "descriptors":["fractals", "multicoloured"]}
```

Or `{"decision":"exclude", "reason":"Describes the real backyard before the experience"}`.
Only confirm descriptors explicitly describing the target in that passage.
Use `descriptors: []` for a relevant setting with no supported dictionary
descriptor. It counts toward the sample, but contributes no descriptor votes;
absence of a lexical match is not a reason to exclude a relevant report.
Do not count opening one's ordinary eyes as entity eyes, the word 'machine elf'
as observed circuitry, love for a spouse as a being's gesture, or earlier-trip
beings as afterglow visuals. A report may be included with only some lexical
matches confirmed. Reject hypothetical/advice/general-comparison text as such.
Review in fixed queue order until 40 relevant reports, or exhaust the candidate
pool. Re-run `--queue` for the next batch. Keep the initial corpus hash unchanged.
The scored top-15 then uses confirmed sample counts, while the original full
corpus lexical counts remain in `fidelity-corpus.json`. No source-validation
gate can be satisfied by simply copying all lexical matches.

If a title anchor or clipped window omits the actual scene, add a justified
exact-offset window around a later mention in that same tagged report to
`fidelity-extra-passages.jsonl` (same fields as original passages, plus `reason`).
Verify its text against raw `[start:end]` and its node anchor; bind its SHA256 in
the review ledger as `extra_passages_sha256`. These windows supplement reviewed
sample evidence, not the frozen original full-corpus lexical counts. Garden's
four supplements were verified against raw text; its 27 candidates are exhausted.

## Inspect and grade fresh renders

Each `targets.<stage-or-being>` object:

```json
{
  "close_up": false,
  "captures": [{
    "file": "visual-garden.png",
    "sha256": "SHA256 of actual image bytes",
    "detail": "high",
    "render_signature": "from fidelity-results.json at capture time",
    "animTime": 12.3,
    "inspection": "pixelvision label plus concise frame description"
  }],
  "descriptors": {
    "moving / animated": {
      "grade": "PARTIAL",
      "observation": "Describe specific visible evidence and remaining mismatch.",
      "temporal_observation": "For PRESENT temporal descriptors, compare at least two distinct animation times."
    }
  }
}
```

Allowed grades: PRESENT, PARTIAL, ABSENT, UNREVIEWED. All top 15 require review.
Copy captures to stable iteration filenames under `world/` before they can be
overwritten. Every being must have `close_up: true` backed by an inspected close-up.
Frames must come from real controls at HIGH detail; read-only diagnostics may
record metadata, never inject pose/time/navigation. Use pixelvision sequentially.

`history` is a list of iteration notes with target, before/after grade snapshots,
specific changes, capture paths/hashes and any remaining gaps. Never overwrite
an adverse observation just because code was changed; re-render and re-inspect.

`route_review` needs `grade: "PASS"`, a detailed `rationale` addressing measured
forward/reverse counts, atlas-order inversion and editorial timing, and
`audit_sha256`: SHA256 of Python `json.dumps(route_audit, sort_keys=True).encode()`.
Do not turn prose-order counts into experience duration or a compulsory itinerary.

`acceptance` has desktop/mobile/paced/fallback records. Each requires `passed: true`,
the current `render_signature`, and `sha256` of the corresponding fresh
`verification-SECTION.json`, after actually running and inspecting that check.
Hashing an old passing file does not make it fresh acceptance.
