# Corpus pipeline — repaired v0.4 pilot

## Status

**The repaired pilot and aggregation are complete; full extraction remains unauthorized.**
There are 200 accepted v0.4 records with 431 scenes. Pilot20 passed its numerical
gate, but the reading audit found errors; neither rendered nor blind fidelity is
certified. The old sampler and fidelity checker require distribution format 2.0.0
and cannot consume the current 3.1.0 aggregate. No world integration was installed.

**Report2 complete — turn 3/3, 2026-09-06.** [CORPUS2.md](CORPUS2.md) supersedes the
original repair/acceptance rules and lifetime caps in [CORPUS.md](CORPUS.md).
[phases2.json](phases2.json), [NOTES.md](NOTES.md) and `status.txt` track delivery.
The CORPUS2 delivery is closed: repair, both pilots, aggregation and this report
are delivered. The completion marker in NOTES.md marks that scoped delivery,
not approval for full extraction or success of the remaining fidelity objectives.

## What changed

- **Smaller provider schema:** v0.4 uses 1,570 compact UTF-8 bytes, 22 declared
  properties and no enums. Free-text descriptors replace constrained vocabulary
  choices; the prompt includes three converted few-shots. Local enrichment adds
  version, normalized descriptors, flags and quote anchors to stored records.
- **Structural acceptance:** parsing, boolean trip classification and at least
  one quote per scene determine acceptance. Semantic doubts become retained flags;
  reading audits report errors without deleting or downgrading records.
- **Local evidence anchoring:** provider quotes are strings without offsets.
  Whitespace/case-normalized matching assigns source offsets and an anchor score;
  scores below 0.85 are weak, not rejected. Excluded-topic tokens are redacted
  inside quotes while retaining records. The audit still found a redaction miss.
- **Conservative normalization:** aliases map through the local vocabulary;
  unmapped descriptors remain `other:<text>`. Blank descriptors stay missing.
- **Changed evidence contract:** dwell, episode boundaries, abruptness and order
  confidence are not collected. Scene-array neighbors are adjacencies, not
  confirmed same-episode transitions; every link has `sampling_eligible: false`.
- **Aggregation rebuilt:** latest structurally accepted v0.4 attempt per ID wins;
  conflicting same-attempt ties fail. Six legacy rows remain untouched and excluded.
  Format 3.1.0 stores sparse bins, shared vocabulary domains, denominators,
  supporting report IDs and pointers into selected records. Flags and weak quotes
  remain available; joint profiles preserve observed co-occurrence.

Sources join by `id`, never row order. Canonical evidence text is
`(title or "") + "\n\n" + (selftext or "")`; offsets are Python Unicode code points.
There are 14,309 tagged baseline IDs, 14,297 raw joins and twelve missing joins.
The original first 200 IDs all join; this is a nonrandom pilot, not a prevalence sample.

## Gate results and current evidence

| Measure | Pilot20 | Additional pilot200 | Combined v0.4 |
| --- | --- | --- | --- |
| Accepted / selected reports | 20/20 | 180/180 | 200/200 |
| Trip-classified with scene and anchored quote | **16/20: PASS**, threshold 14/20 | 128/180 | 144/200 |
| Scenes | 39 | 392 | 431 |
| Anchored / retained quotes | 121/121 | 1,109/1,110 | 1,230/1,231 |
| Reports with flags | 17/20 | 135/180 | 152/200 |
| Billed cost, including retries | $0.208577375 | $1.867267375 | $2.075844750 |
| Incremental phase cap | $1 | $3 | Both respected |

Across both phases, 201 v0.4 generation attempts yielded 200 accepted records and
one provider error. All used JSON-schema transport; there were no structural
rejections or text-JSON fallbacks. The pilot200 error reported only “Invalid
request data,” not a diagnosed grammar failure, and no billed usage. Its targeted
retry succeeded without changing the prompt/schema and cost $0.027693250, already
included above. The compact grammar therefore worked in generation, not only in
the earlier token-count check; this does not establish semantic accuracy.

All 431 scenes have at least one anchored quote; the single weak quote is retained.
The aggregate contains 144 trip-classified and 56 non-report records, 167 being
entries and 287 adjacencies. Place coverage is **7 canonical-mapped, 308 unmapped
and 116 unspecified scenes** out of 431. These mapping strata describe lexical
coverage, not correctness. Flags are diagnostics, not measured error rates.

The fixed ten-record pilot20 reading audit reports overlapping record-level rates:
wrong place **0/10**, missed scene/stage **2/10**, invented detail **1/10**,
classification error **1/10**, redaction miss **1/10**, and temporal/qualification
concerns **5/10**. No audited record was changed or downgraded. The additional 180
records have **not** been reading-audited. High anchor scores establish text
matching, not correct interpretation or complete scene coverage.

See [PILOT2.md](PILOT2.md) for methods, usage, score bins and audit details, and
[DISTRIBUTIONS.md](DISTRIBUTIONS.md) for counts, denominators and coverage.
[PILOT.md](PILOT.md) and [NOTES-run1.md](NOTES-run1.md) describe the historical
failed v0.3 run, not the current evidence.

### Delivery status versus validation

| Workstream | Delivered result | What it does not establish |
| --- | --- | --- |
| Repair | Compact provider schema, local normalization/anchoring and structural acceptance; successful pilot generation. | Complete scene coverage or correct interpretation. |
| Pilot20 | Numerical gate PASS 16/20; required ten-record reading audit reported. | A fidelity pass; the audit still contains errors. |
| Pilot200 | All 180 additional records accepted within its $3 cap. | Reading-audited quality for those 180; 128/180 is descriptive, not another specified pass threshold. |
| Aggregate2 | 200 selected records; format 3.1.0 counts, coverage, profiles and provenance. | Population prevalence, qualified traversal or compatibility with old consumers. |
| Report2 | Complete: final runbook, gate/audit results, measured costs and exact proposed full-pass invocation with its implementation blockers. | Full-pass implementation, spending approval or a completed full extraction. |
| Sampling, rendering and fidelity | Earlier artifacts remain available for migration and evaluation. | A working v0.4 world integration or rendered/blind fidelity certification. |

## Artifacts

| Piece | Files and current contract |
| --- | --- |
| Coding and examples | [schema.json](schema.json), [SCHEMA.md](SCHEMA.md), [vocab.json](vocab.json), [prompt.md](prompt.md), [examples/](examples/). Provider shape differs from enriched stored records; examples are not aggregate inputs. |
| Extraction and normalization | [extract.py](extract.py), [normalise.py](normalise.py), [records/](records/), `extract-state.json`, `requests.jsonl`. Resumable, budgeted pilot extraction; billed failures remain in accounting. |
| Aggregation | [aggregate.py](aggregate.py), [distributions.json](distributions.json), [DISTRIBUTIONS.md](DISTRIBUTIONS.md). Offline v0.4 selection and format 3.1.0 evidence. |
| Legacy sampling | [sampler.js](sampler.js), [SAMPLER.md](SAMPLER.md), [test_sampler.mjs](test_sampler.mjs). Format 2.0.0 consumers; migration required. |
| Integration and fidelity | [INTEGRATION.md](INTEGRATION.md), [fidelity_dist.py](fidelity_dist.py), [BLIND_TEST.md](BLIND_TEST.md). Existing plans/protocol; checker requires format 2.0.0. No renderer, graded-frame dataset or completed blind experiment. |
| Refresh | [refresh.py](refresh.py), [REFRESH.md](REFRESH.md), [refresh.service](refresh.service), [refresh.timer](refresh.timer). Corpus-local overlay; unit texts uninstalled and live harvest unverified. |

Read dated sections in context: SCHEMA.md records the repair-stage checks before
generation, PILOT2.md records the subsequent pilot outcomes, and DISTRIBUTIONS.md
defines the current aggregate contract. Old sampling/integration instructions are
design references, not a working recipe for the new distribution format.

## Runbook

All commands assume `/home/clawd/dmt-atlas/corpus`. Write only here; `../data/`
is read-only. Use `/home/clawd/corpus-venv/bin/python` (Anthropic SDK 1.4.0).
Extraction uses `ANTHROPIC_API_KEY` from the environment; never print it.
The configured model is `claude-opus-5`, effort low, thinking default, maximum
4,000 output tokens. The provider grammar has a text-JSON fallback.

### Supported offline operations

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --help
/home/clawd/corpus-venv/bin/python -B aggregate.py
/home/clawd/corpus-venv/bin/python -B refresh.py --check
```

Help is offline. Aggregation rewrites `distributions.json` and `DISTRIBUTIONS.md`
from retained records; it does not call the API or alter extraction records.
Refresh `--check` inventories the baseline without network or writes.

Aggregate histograms store observed bins only: `vocabulary_ref` points into shared
`vocabulary_domains`. An absent canonical bin reconstructs as `n=0`, no report
IDs, and frequency zero for a nonempty denominator or null for an empty one.
Resolve `denominator_ref` where present. Do not infer missing measurements as zero.
The pilot JSON is 2,943,046 bytes. A synthetic 14,297-report check passed with one
unique scene/place/profile per report; it is not a bound for richer real data.

### Pilot extractor operations and guards

These are the historical cohort invocations, **not instructions to restart a pilot**:

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot20 --limit 20 --budget-usd 10
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot200 --limit 180 --budget-usd 10
```

Pilot200 ran only after the pilot20 gate passed; its one billed retry is included
in the costs above. Selection is pinned to the original 200, split 20/180, and
limited before completed v0.4 IDs are skipped. `--ids` cannot expand a cohort.
`--retry-failed` requires explicitly listed failed IDs; `--retry-cohort` explicitly
reruns the original pilot20 and charges every attempt. Neither is needed now.

`--budget-usd` is mandatory and **cumulative**, including legacy charges;
CORPUS2 raises the lifetime ceiling to $10, 400 distinct batch report IDs and ten
realtime slots. The phase caps remain incremental $1/$3, and `--limit` remains
1..200. Realtime mode permits at most five reports per invocation. The ledger
currently has **$4.358262625 spent, $0 reserved, 200 distinct batch report IDs and
five realtime slots**. Spare lifetime capacity does not authorize another cohort.

`--dry-run` and `--check-schema` make live token-count calls; they are not offline
checks. `--collect-only` can retrieve existing batches without submitting generation.
All require a budget argument. Exit codes: 0 complete, 1 selected failures,
2 budget stop/error. No API calls or added spend occurred in this report turn.

Report2 offline verification passed: local documentation links, fenced blocks,
cost arithmetic, extractor help, and pre-API rejection of the proposed full phase,
expanded limit and expanded budget. Aggregation, refresh and extraction were not rerun.

Turn 2 independently reconciled saved v0.4 records with the aggregate's selected
IDs, report/scene/being/adjacency/flag counts, quote coverage and place-mapping
strata. The original 200-ID cohort, 14,297 raw joins, six excluded legacy rows,
pilot20 gate and phase outcome/cost summaries also matched. All adjacency links
remain ineligible. These read-only consistency checks are not a new reading audit.

### Sampling, fidelity and refresh limitations

Do **not** run the old sampler or fidelity checker against format 3.1.0 as an
operational pipeline: both enforce format 2.0.0. They need a consumer migration
for sparse domains, current profile shapes, missing fields and ineligible links;
changing only the version string is not sufficient. The earlier mechanics checks
are historical, not v0.4 fidelity results. After migration, follow the linked
sampling/integration documentation and blind protocol, revising the measured
feature scope to fields v0.4 actually collects. No world files were modified.

Refresh supports `--posts FILE` for offline merge/tag/queue and `--retag` for
repair of existing overlay-derived files. `--fetch --max-requests 100` is a network
operation; see [REFRESH.md](REFRESH.md). Outputs stay in `refresh-data/` and the
additive `pending_extraction.txt`. The extractor does not read this overlay or
automatically dequeue pending IDs; that queue is not extraction authorization.
The timer text specifies Sundays 04:00 UTC plus up to 30 minutes jitter; it is
not installed. Baseline charts remain unchanged, and live boundary behavior,
archival arrivals and retained-post edits/deletions are not verified/reconciled.

## Full-pass cost and exact proposed command

Combined measured cost per selected report is **$0.01037922375**, including the
pilot retry. Mean input is 4,918.21 tokens/report and output 581.13. Combined
usage is 157,042 uncached input, 818,334 cache-read input, 8,266 cache-creation
input and 116,226 output tokens. Configured batch rates per million tokens are
$2.50 input, $12.50 output and $0.25 cache reads; five-minute cache writes use
1.25 times input price. Observed caching and retry behavior are part of this estimate.

| Scope | Calculation | Projected cost |
| --- | --- | --- |
| Equivalent fresh pass over all joined reports | $0.01037922375 × 14,297 | **$148.39** |
| Additional extraction after reusing the 200 pilot records | $0.01037922375 × 14,097 | **$146.32** |
| Projected cumulative ledger after that remainder | $4.358262625 + $146.31591720375 | **$150.67** |

The first two projections exclude legacy spend; the cumulative row includes it.
The pilot is nonrandom; source lengths, output volume, cache hits and retries can
change costs. These are estimates, not a quote or authorization.

**There is no runnable full-pass command in the current CLI.** The exact target
invocation proposed for a future, reviewed full-pass implementation is:

```sh
# PROPOSED ONLY — unsupported today; DO NOT RUN.
/home/clawd/corpus-venv/bin/python -B extract.py --phase full --ids full-joined-ids.txt --limit 14297 --budget-usd 180
```

Here `--phase full` is a **proposed new mode**, not an existing flag value, and
`full-joined-ids.txt` is a **not-yet-created** manifest of the 14,297 baseline IDs
with raw joins, excluding the twelve missing joins. In that future mode the
14,297-ID selection must reuse the 200 accepted v0.4 records and submit only
14,097 pending IDs. `$180` is a proposed cumulative ceiling, about $29.33 above
the projected ending ledger, not approved spending or a guaranteed sufficient cap.

Before this command can become runnable:

1. Obtain the owner's written go for the full joined-baseline scope and an explicit
   cumulative budget. CORPUS2 expressly requires this; no such go has been given.
2. Implement/review a separate full phase and its pinned manifest, selection and
   checkpoint validation. Current phase choices/cohort pinning, 200-limit, $10
   ceiling and 400-ID guard all block it; raising one constant is insufficient.
   Preserve prior charges, accepted records and pilot caps.
3. Retain cumulative spent-plus-reserved checks, bounded resumable batches, request
   logging and explicit retry accounting. Conservative reservations may stop before
   the measured-cost estimate; never raise the approved budget automatically.
4. Verify the expanded selection/accounting offline and finalize the invocation
   against that implementation. Do not rotate pilot cohorts or reset the ledger.

This report changes documentation only; it neither creates full-pass support nor
runs extraction. The owner can review the concrete scope, estimate and proposed
command here; implementation beyond pilot guards remains future work.

## What the world gains, and what remains

The repaired evidence now supplies observed scene/being bundles, measured weights,
coverage gaps and report-level provenance. A migrated sampler and renderer could
vary supported visits from those joint profiles and expose supporting evidence.
A full pass would broaden that evidence; it would not by itself validate reading
accuracy, solve the sparse canonical-place mapping, or establish rendered fidelity.

Future work outside this completed delivery: obtain written full-pass
scope/budget and implement its guarded mode; audit broader reading quality without
removing flagged evidence; migrate the sampler/fidelity consumers; integrate and
evaluate the renderer; then connect and validate refresh ingestion separately.
Consumer migration and further pilot auditing can use the existing 200 records;
they do not depend on approval or completion of the full extraction.
Do not invent dwell times, episode-qualified traversal or missing realm evidence.
Until those integrations and evaluations exist, the world is not certified as a
corpus-sampled experience.
