# CORPUS2 — repair the extractor; the pilot failed because of the grammar and your validator, not the model

Read `CORPUS.md` first (still the brief), then this. Everything in `CORPUS.md` stands except where this
file changes it. Your first run closed with `PILOT.md` saying: 98 attempts, 6 accepted records with
**empty scenes**, 34 invalid, 29 API errors, $2.28 spent. The owner read it. Diagnosis:

1. **Grammar too large.** 29 of 56 batch requests failed with grammar-too-large: the 9 KB schema
   (41 properties, 276 enum values, depth 8) exceeds what constrained decoding accepts. You then fell
   back to a shape-only schema and to text JSON. That fallback was right; the schema was not.
2. **Your validator and reading review rejected 85 % of what came back** for reasons like: an affect
   word inferred rather than explicit; a quote that fixed a source misspelling; a quote with a
   "paragraph break"; a dwell field without a support pointer; a `reason` without a support pointer;
   an enum value outside the vocab; a quote that mentions an excluded topic. The six records you
   accepted are the ones that claimed nothing. **A validator that only passes empty records is the
   defect.** This is the same failure as the world run: a gate satisfiable by rejecting more will be
   satisfied by rejecting more.

## The repair (phase `repair`)
- **Schema v0.4, built for constrained decoding:** depth ≤ 4, ≤ 30 properties total, **no enums**
  (descriptor fields are `array of string`, free text; the vocab mapping happens locally after
  extraction in a normaliser that maps synonyms to `vocab.json` and keeps unmapped words as
  `other:<word>`). Keep `report_id`, `is_trip_report`, `reason`, `scenes[]` with `place`, `order`,
  `light`, `colour`, `motion`, `geometry`, `material`, `density`, `scale`, `beings[]` (`form`,
  `count_text`, `behaviour`, `communication`, `affect`), `transition_trigger`, `affect`, and
  **`quotes: array of string` per scene** (verbatim, no offsets). Drop dwell, episode_index, support
  pointers, uncertain-field pointers. Check `count_tokens` accepts it; keep the provider schema under
  3 KB. If the provider still rejects it, use text JSON with the schema in the prompt and parse
  leniently (strip fences, take the first `{`…`}` balanced block).
- **Quotes are anchored locally, never rejected:** for each quote, find the best match in the source
  with normalised whitespace and case; record `anchor_score` (difflib ratio on the best window) and
  the offsets you find. Score ≥ 0.85 = anchored; below = `weak_anchor: true`. **Both are kept.**
- **Validity = structural only:** JSON parses; `is_trip_report` is a boolean; every scene has ≥ 1
  quote; nothing else can invalidate a record. Semantic doubts become flags on the record
  (`flags: [...]`), never quarantine. No reading review may delete or downgrade a record; the reading
  audit (below) reports rates.
- **Excluded topics:** redact dose/route/sourcing tokens inside quotes to `[redacted]`; keep the record.
- Prompt: extraction instructions under 600 words, the schema, three of your `examples/*.json`
  rewritten to v0.4 as few-shot. `output_config={"effort": "low"}`, thinking default. Batch API.
- Raise your own lifetime guards to: **$10 cumulative** (the $2.28 already spent counts), 400 batch
  IDs, 10 realtime slots. The owner set these numbers.

## Gates
- **`pilot20`:** 20 reports, budget cap $1. Pass = ≥ 14 of 20 records are trip reports with ≥ 1 scene
  and ≥ 1 anchored quote. Write `PILOT2.md` with the counts, cost per report, and a 10-record reading
  audit that REPORTS error rates (wrong place, missed scene, invented detail) without changing records.
  If it fails, spend the remaining `repair`-style turns inside this phase fixing the prompt/schema and
  re-run the same 20 (retries count against the cap).
- **`pilot200`:** only if `pilot20` passed: the original 200-report selection minus the 20, cap $3.
  Update `PILOT2.md`: measured cost per report, projected full-pass cost at batch rates, scene
  counts, anchor-score distribution, flag rates. **The full pass still needs the owner's written go.**
- **`aggregate2`:** re-run `aggregate.py` on the valid records (adapt it to v0.4; free-text
  descriptors go through the normaliser first). `DISTRIBUTIONS.md` now shows real numbers with `n`.
- **`report2`:** update `README.md`: what changed, the gate results, the exact full-pass command and
  its projected cost. `<<CORPUS2_DONE>>` alone on the last line of `NOTES.md`.

## Unchanged
Write only under `corpus/`. No git, no GUI, never print the key, no dose/route/sourcing content in
the vocab or the schema. Never exceed the caps above. One `NOTES.md` section per turn, under 40 lines.
