# Corpus record schema — v0.4.0

## Status and scope

`CORPUS2.md` replaces the v0.3 acceptance contract. `schema.json` is now the
compact provider schema, not a schema for locally enriched stored records.
`prompt.md` contains 376 instruction words, that schema, and three converted
few-shots. `extract.py --check-schema --limit 1 --budget-usd 10` checks one live
token-count request without generating a record. Counting does not demonstrate
that a generation request can compile the grammar.

On 2026-09-06 the exact command above returned `count_tokens_accepted`, 4,849
input tokens, with `json_schema` transport. No generation was submitted. The
offline schema/few-shot/anchor checks passed. `node test_sampler.mjs` failed at
line 125 because its enum-derived realm is now undefined; its fixtures and the
aggregate's v0.3 assumptions still require migration in aggregate2.

Repair turn 3: v0.4 acceptance, mixed-version checkpoint accounting, and
phase-budget guards are integrated. The old validator remains for downstream
migration but is not called by v0.4 acceptance. No generation was submitted
during repair; pilot evidence and generation-grammar compatibility are unmeasured.

## Provider shape

The compact schema is 1,570 UTF-8 bytes, with 22 declared properties, no enums,
and three nested object levels: record, scene, being. Array wrappers add
structural levels; the object-depth measure excludes them. Every object's
properties are required and `additionalProperties` is false. Local acceptance
is intentionally less restrictive than constrained decoding.

| Object | Fields |
| --- | --- |
| Record | `report_id` string, `is_trip_report` boolean, `reason` string, `scenes` array |
| Scene | `place` string; `order` integer starting at 1; `light`, `colour`, `motion`, `geometry`, `material`, `density`, `scale`, `transition_trigger`, `affect` string arrays; `beings` array; `quotes` string array |
| Being | `form`, `behaviour`, `communication`, `affect` string arrays; `count_text` string |

Unknown descriptions use empty arrays/strings. Scene order is experienced order;
transition triggers describe movement into the next scene. A scene need not have
a named setting. Count wording and uncertainty stay in free text. There are no
model-generated offsets, support pointers, dwell bounds, episode indices, or
uncertainty pointers. The normaliser stamps the storage version locally.

## Prompt and examples

The converted examples are `examples/5av2zn.json` (three changing scenes),
`examples/wbm413.json` (one scene with geometric beings), and
`examples/yef97.json` (a future plan, not an experienced trip). The prompt pairs
these with explicitly labelled source excerpts. Every few-shot quote is an
unchanged substring of its excerpt and the joined canonical source. The other
seven examples remain historical v0.3 examples, not current provider templates.
Examples are illustrative hand coding, never prevalence or pilot data.

`parameters` sends low effort with default thinking, a 4,000-token output limit,
and the compact schema directly. `--text-json` omits the provider format while
retaining the schema in the prompt, for fallback after grammar rejection.
`normalise.decode_record` accepts fenced JSON or the first balanced JSON object.
The extractor acceptance path now uses that decoder and `normalise_record`.
Parseable output with a nonstandard stop reason is retained with a flag, not
rejected solely because it hit the output cap. Structurally invalid output is
still charged using provider usage before its failure is checkpointed.

## Local acceptance and enrichment

`normalise.structural_check` requires a JSON object with boolean
`is_trip_report`, a scene array when supplied, and at least one quote per scene.
Missing/null scenes become an empty array with a flag. Other field defects,
contradictory classifications and unmapped descriptors become flags, not grounds
for quarantine. Reading audits report error rates without deleting or downgrading
records. An empty record is not evidence that experiences lack scenes.

`normalise_record` copies provider input, stamps `schema_version: "0.4.0"`, and
can repair report IDs from the authoritative source join with a flag. Original
free-text descriptor fields remain; scene/being `normalised` mappings use existing
vocab values, catalog aliases and explicit synonyms. Unmapped strings become
`other:<word>`; ambiguous aliases are not assigned arbitrarily. Vocab is not
extended. Enrichment is a one-time operation on provider input.

## Quotes and source evidence

Join `../data/corpus/reports.jsonl` to raw posts by `id`, never row order.
Canonical text is `(title or "") + "\n\n" + (selftext or "")`. Local quote objects
contain `text`, half-open `start`/`end`, `anchor_score`, `weak_anchor`, `redacted`,
and `ambiguous_anchor`. Offsets are original Python Unicode code-point positions.

Matching casefolds and collapses whitespace. Exact repeated matches select the
earliest occurrence and flag ambiguity. Fuzzy matching chooses the highest
difflib ratio among near-length word windows and matching-block-aligned windows;
it is a heuristic, not exhaustive substring optimisation or semantic support.
Scores at least 0.85 are anchored; lower scores remain with `weak_anchor: true`.
Unavailable offsets are null. Weak evidence is retained, never silently removed.

Anchoring precedes excluded-topic token redaction to `[redacted]`. Stored quote
text may therefore differ from its referenced span. No unredacted copy is added.
Other free-text values are also redacted. The matcher is heuristic, not a complete
semantic content detector; the reading audit must report misses.

## Limits, retries and operation

Authorized lifetime ceilings are $10 cumulative, 400 distinct batch IDs, and
10 realtime slots; previous spend counts. Phase limits are additionally $1 for
pilot20 (all retries included) and $3 for the remaining 180 original pilot IDs,
only after the 20-record gate passes. The full pass remains unauthorized.

The six retained v0.3 records and historical usage are unchanged. Default v0.4
selection is the first 20 of the original first 200 tagged IDs; pilot200 is the
other 180. IDs are joined to source text and checked before any submission.
The cohorts are pinned in state when new work is reserved. `--ids` can only
select within the requested phase. Full extraction remains blocked.

New jobs carry `schema_version`, `phase`, and transport metadata. Each stored
v0.4 record carries `_extraction` with its job, phase, and global attempt number.
Earlier records remain on disk; `latest_records` selects the latest accepted
v0.4 attempt per ID for the pilot gate. Aggregate2 must likewise deduplicate
attempts by ID, preferring v0.4 over legacy, rather than count retries as reports.
A failed retry does not delete an older accepted record; its CLI exit is still 1.

The lifetime ceiling and each phase's spend-plus-reservations are enforced
together. All phase retries count, even invalid outputs, and ambiguous submissions
retain reservations until reconciled. A record written just before a crash is
not duplicated when its result is replayed for usage accounting. Prior legacy
spend continues to count toward both `--budget-usd` and the $10 lifetime ceiling.
The $1 and $3 phase allowances count new jobs tagged with their respective phase.

Operator commands for the subsequent pilot phases (not run during repair):

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot20 --limit 20 --budget-usd 10
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot20 --limit 20 --retry-cohort --budget-usd 10
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot200 --limit 180 --budget-usd 10
```

The cumulative CLI ceiling does not expand the $1/$3 phase allowances. Default
resumption skips accepted v0.4 IDs and does not automatically retry failures.
`--retry-failed --ids FILE` retries explicitly selected failed v0.4 IDs;
`--retry-cohort` explicitly reruns the same full 20, retaining accepted history.
Collect/reconcile any outstanding work before starting a cohort retry. For a
provider grammar rejection, add `--text-json` to an explicit retry; no silent
resubmission occurs. `--collect-only` never submits generation and remains usable
for recovering already-reserved work. Every mode requires `--budget-usd`.

Pilot200 is blocked unless at least 14 of the fixed 20 have a retained v0.4 trip
record with a scene containing an anchored quote. The 10-record reading audit
and its error-rate report remain required pilot20 work; the numerical gate does
not substitute for that audit or certify semantic fidelity.

Offline fake-provider checks passed for legacy upgrades, charged invalid output,
weak-quote retention, nonstandard stop reasons, explicit text/cohort retries,
idempotent resume and crash replay, pinned cohorts, phase/lifetime caps and the
pilot200 gate. Real state remains $2.282417875 spent, $0 reserved, six records.
Aggregate/sampler code still assumes v0.3 enums; its test fails at line 125.
Migration belongs to aggregate2. No synthetic check is a corpus fidelity result.
