# Pilot — final turn, 2026-09-05

## Decision and retained data

**Pilot fidelity failed; the 200-report target is incomplete. Do not run full extraction.**
Measured cumulative cost is **$2.282417875**, with **$0 outstanding reservations**.
Every remote job has ended; no local extractor is running. Commands used a
cumulative $5 budget, within the $8 lifetime ceiling. All five realtime attempt
slots are exhausted. There were 56 distinct batch-source IDs, all inside the
original first-200 selection; retries did not expand that cohort.

Twenty unique sources received generated outputs and a complete final reading
audit. Six records remain in `records/*.jsonl`, all with empty `scenes`:

- `t43yv`, `wm1gg`, `yef97`: non-reports, asking about future experiences.
- `sxnbj`, `uodcz`, `zy7fe`: specific but minimal past experiences, with no
  recoverable scene detail under the coding rules.

The other fourteen latest records failed validation or reading review. Seven
scene-bearing records that passed automated validation were quarantined after
reading: their JSONL entries were removed and their state outcomes changed to
`invalid`, with field-level `review_errors`; usage and charges were preserved.
An earlier version of `sxnbj` was also quarantined, then successfully retried.
No scene-bearing record survived review. These six records cannot support scene,
realm, entity, transition, or dwell distributions. Empty scenes mean no coded
scene evidence, not measured absence of those phenomena in the population.

## Measured usage and cost

All token counts below are provider-reported usage, including rejected outputs.
Input categories are disjoint. Batch rates are $2.50/M uncached input, $12.50/M
output, and $0.25/M cache reads; five-minute cache creation is 1.25 times input.
Realtime rates are double these. Costs are calculated from usage at those rates,
not reconciled against a provider invoice. No batch cache reads were observed.

| Run | Attempts | Final outcomes after reading review | Cost, USD |
| --- | ---: | --- | ---: |
| First nested-schema batch | 28 | 28 API errors | 0 |
| Second nested-schema batch | 28 | 1 API error, 27 canceled | 0 |
| Realtime shape-only schema | 2 | 2 definite HTTP 400 rejections | 0 |
| First two generated realtime responses | 2 | 2 invalid | 0.132471 |
| First generated batch, default thinking | 20 | 3 accepted, 17 invalid | 1.276217500 |
| Final realtime response, thinking disabled | 1 | 1 invalid | 0.085711250 |
| Final failed-ID batch retry, thinking disabled | 17 | 3 accepted, 14 invalid | 0.788018125 |
| **Total** | **98** | **6 accepted, 34 invalid, 29 API errors, 27 canceled, 2 HTTP rejections** | **2.282417875** |

Canceled/rejected requests reported no generated usage and carry zero measured
cost. There are no ambiguous submissions or unreconciled reservations remaining.
These are request-attempt counts, not 98 distinct source reports.

| Token measure | First generated batch total (20) | Mean/report | Final batch total (17) | Mean/report |
| --- | ---: | ---: | ---: | ---: |
| Uncached input | 15,597 | 779.85 | 14,926 | 878 |
| Cache creation | 179,260 | 8,963 | 158,525 | 9,325 |
| Cache reads | 0 | 0 | 0 | 0 |
| All input categories | 194,857 | 9,742.85 | 173,451 | 10,203 |
| Output | 54,163 | 2,708.15 | 20,425 | 1,201.47 |
| Cost, USD | 1.276217500 | 0.063810875 | 0.788018125 | 0.04635400735 |

Across all forty generated responses, including three realtime attempts, usage
was 32,671 uncached input + 355,854 cache-creation + 8,872 cache-read tokens, and
78,191 output tokens. Lifetime cost per retained record is $0.380403, including
failed attempts; there is no cost per usable scene record because none survived.

### Full-pass projection, not authorization

Applying the final batch's measured mean token mix at batch rates gives
**$662.723243125 for 14,297 one-attempt reports** (about **$9.270801471 for 200**).
The earlier default-thinking batch projects to $912.304079875 for 14,297.
The final estimate excludes retries, human review, and further prompt changes;
it is not a cost estimate for obtaining valid records. The seventeen retries
are a small, failure-selected sample, not a representative random sample.
The latest untested prompt additions will also change input costs. No extrapolation
of the observed six classification-only successes establishes full-pass fidelity.

Initial dry-run counts used the superseded nested transport: a fixed-seed sample
of fifty joined reports averaged 14,875.94 input tokens. Those counts are not
current envelope-transport estimates. Sources contain 14,309 tagged IDs and
14,297 raw joins; twelve lack raw text, while all first 200 join by ID.

## Error rates and output fit

- Pre-fix batch compatibility: 29/56 grammar-too-large errors (51.79%) and
  27/56 cancellations (48.21%); no generated outputs.
- First generated batch: ten of twenty responses hit `max_tokens` (nine had
  thinking only; one partial text). Five complete thinking-plus-text responses
  were incorrectly rejected by the old first-block parser; one other response
  lacked dwell support pointers. Four initially passed; reading rejected one.
- Final batch: all seventeen ended normally, reported zero thinking tokens,
  and used 196–3,194 output tokens within the unchanged 4,000-token limit.
  Seven failed automatic validation (41.18%); ten initially passed. Reading
  rejected seven more, leaving three accepted and fourteen invalid (82.35%).
- Latest outputs across the twenty audited sources: fourteen failed (70%), six
  retained (30%). All seven scene-bearing final outputs that passed automated
  validation failed the semantic reading audit (100% of that subgroup).
- Across all forty generated responses, 34 were invalid after review (85%).
  Overall retained yield was 6/98 completed request attempts (6.12%). Canceled
  requests and definite API rejections are not in the generated-output denominator.

The final sample fits the output limit, but does not establish fit for longer
reports or a full corpus. Token fit and complete pointer coverage do not establish
semantic fidelity. Thirty-six other unique batch IDs have only pre-fix errors or
cancellations; they were not part of the twenty-output reading audit.

## Twenty-report reading audit — latest complete outputs

Each of these twenty sources was read in full against its latest decoded record:
seventeen final retry outputs and three retained non-reports from the earlier
batch. Evidence uses `(title or "") + "\n\n" + (selftext or "")`, joined by `id`,
with Python Unicode code-point offsets. Paths below are JSON Pointers; abbreviated
paths are relative to the scene or being named. A plausible value with a quote
from the wrong episode still fails. Ambiguous interpretations are identified as
such, not presented as certain source facts. No rejected model payload is saved.

| Report | Disposition | Wrong fields, missing evidence, and coding concerns found |
| --- | --- | --- |
| `hvbtm` | Validator rejection | `/scenes/1/motion/1` is the invalid enum `changing` and lacks its own support pointer. `/scenes/0/transition/abruptness` misses an explicit sudden change. `/quotes/0` does not support the encounter/transformation detail in `/reason`. Enum failure occurred before anchoring; this is not a claim that all quote texts were non-verbatim. |
| `k8f9v` | Reading quarantine | `/scenes/1/place` omits an explicit bed. `/scenes/1/quotes/0/text` includes excluded procedural detail missed by the guard. `/scenes/1/quotes/3/text` supports fear using a childhood non-trip memory rather than the current episode; current fear elsewhere does not repair this citation. The two-episode structure itself is correct. |
| `oau3u` | Reading quarantine | `/scenes/1/material/0=metallic` mistakes a colour description for material. `/scenes/1/motion/0` and `/scenes/3/motion/0=rushing` infer speed from soaring. `/scenes/1/affect/1=awe` and `/scenes/4/affect` (confusion/awe) infer emotions from beauty or strangeness. `/scenes/1/scale` omits an explicitly huge wall. `/scenes/1/uncertain_fields` omits approximate count bounds, though it flags form. `/scenes/3/beings/0/count` omits explicit plurality. `/scenes/0/transition/trigger/0` cites a curtain-like description instead of the separate explicit eye-closing evidence. Pixelated and diamond-shaped imagery exposes vocabulary gaps, not permission to substitute another motif. |
| `qqe9b` | Reading quarantine | `/scenes/0/affect/4=confusion` is inferred from paradoxical familiarity rather than an explicit emotion. `/quotes/0/supports` points to a reason listing panic, visuals, and fading, but its quote only establishes that the experience started. Explicit fear/panic/overwhelm and floating are supported; joy from feeling good is interpretive rather than a definite additional error. |
| `qvwdb` | Reading quarantine | `/scenes/0` turns a generic recurring history into a specific episode; consequently `/scenes/1/episode_index=2` is wrong for the first recoverable specific episode. `/scenes/1/affect/2=awe` is inferred from an epiphany. `/scenes/1/quotes/0/supports` cites only the computer for a place value also naming the bed; the latter needs its own evidence. No causal claim about the experience is established by classifying the account. |
| `s3i3v` | Validator rejection | `/scenes/0/affect/1=disbelief-not-coded` is an invalid enum without support. `/scenes/0/motion/0=floating` transfers being movement to scene movement. `/scenes/0/beings/0/affect/0=joy` infers emotion from smiling; its `/behaviour/0=ignoring` turns tentative disinterest into a definite action without an uncertainty flag. `/scenes/0/beings/1/form/0=humanoid` infers morphology from gendered figures. That group also conflates one figure's gestures with two others' comforting contact, mis-scoping attributes. `/reason` has details not supported by its root quote. |
| `sxnbj` | Retained | No wrong field identified in the latest record: specific minimal experience, true classification, no scenes. Earlier excluded content in `/reason` was corrected. |
| `t43yv` | Retained | No wrong field identified: future advice request, false classification, no scenes. |
| `uodcz` | Retained | No wrong field identified: specific recent minimal experience, true classification, no scenes. Earlier false classification was corrected. |
| `urywa` | Validator rejection | `/quotes/0/text` and `/scenes/0/quotes/0/text` contain an excluded topic label. Classification and the brief overwhelming experience otherwise have source support. |
| `vxswt` | Reading quarantine | `/scenes/0/motion/0=flowing` forces dancing imagery into a different enum. `/scenes/0/affect/0=calm` is inferred from not being scary. Earlier unsupported outdoors setting was corrected to null. |
| `wh63q` | Reading quarantine | `/scenes/1/geometry/0` codes merging with geometry from an out-of-body description. `/scenes/2/beings/0/entity` assigns a named atlas identity to a generic voice; its `/behaviour/0=threatening` infers an action from tone and imperatives. `/scenes/2/motion/0` and `/scenes/3/motion/0=flowing` overinterpret movement/rippling or the room returning in waves. `/scenes/2/light/0=bright` treats potentially colour-only brightness as illumination without resolving ambiguity. `/scenes/2/affect/0=panic` cites intensity/freefall rather than the separately described panic. `/scenes/0/place` has a quote cut off before the setting noun. Clay-like material is a vocabulary gap, not evidence for another material. |
| `wm1gg` | Retained | No wrong field identified: future question, false classification, no scenes. |
| `xrjhl` | Reading quarantine | `/scenes/0/transition` connects separate trips across an explicit comedown; it should be null. `/scenes/1/episode_index` should be 2 and `/scenes/1/order_confidence` null. `/scenes/1/colour/1=indescribable` derives from indescribable visuals, not colour. `/scenes/1/scale/0=vast` infers perceived size from being at the universe's centre. `/scenes/0/motion/1=flowing` forces dancing walls into a different motion category. |
| `xvm2h` | Validator rejection | `/scenes/1/quotes/0/text` alters a source misspelling and is non-verbatim. `/scenes` omits a distinct later intensely uncomfortable experience and conflates separate experiences into one episode. `/scenes/1/place` omits the bed. `/scenes/1/beings/0` does not adequately flag uncertainty in the retrospective presence's form/behaviour or its timing across experiences; flagging only entity identity is insufficient. |
| `yb4yc` | Validator rejection | `/quotes/0/text` invents a paragraph break and is non-verbatim. `/scenes/0/affect/1=confusion` is inferred from fear of losing sanity. `/scenes/1/motion/0=vibrating` maps an audible vibration/frequency to scene or viewpoint motion. `/scenes/0/light/0=bright` adds intensity to a white flash without explicit brightness: an unresolved interpretation, not an independently measured property. |
| `yef97` | Retained | No wrong field identified: future first-experience question, false classification, no scenes. |
| `zlujh` | Validator rejection | `/scenes/0/dwell/description`, `/basis`, `/seconds_min`, and `/seconds_max` lack evidence support pointers. `/scenes/0/affect/0=awe` overinterprets an evaluative adjective. `/scenes/0/light` omits explicit brighter lights. `/scenes/1/dwell` retains elapsed minutes but loses a distinct subjective lifetime description; this is also a single-dwell representation limitation. `/scenes/1/transition/trigger` omits an explicit cognitive cue. `/reason` includes identity loss beyond the root quote's initial-minute evidence. |
| `zy7fe` | Retained | No wrong field identified: specific minimal earlier experience, true classification, no scenes; subsequent symptoms are not invented into scenes. Earlier false classification was corrected. |
| `103737` | Validator rejection | `/reason` has no support pointer. `/quotes/0/text` contains excluded detail missed by the guard. `/scenes/2/motion/0=still` transfers beings standing still to the scene. `/scenes/2/beings/0/form/1=geometric` infers geometry from unspecified patterns; `/scenes/2/affect/0=calm` infers narrator emotion from a comforting presence. `/scenes/2/uncertain_fields` flags only humanoid form, insufficient for the explicitly tentative identification/count of beings and interpreted form. Two-episode ordering is otherwise correct. |

The audit identifies errors found in a full manual comparison, not a proof of
exhaustiveness or an independently adjudicated gold set. Omissions caused by
vocabulary limitations are distinguished from unsupported substitutions. Generic
recurring memories, ordinary settings, subjective versus elapsed duration, and
being-versus-scene attributes require semantic review beyond pointer checks.

## Compatibility and corrections

1. The count endpoint rejected a schema minimum constraint. Removing it only
   from the provider schema enabled the initial dry-run; the canonical schema
   stayed unchanged. Actual batch compilation still rejected the nested grammar.
   Even a 2,912-byte shape-only provider schema failed in two realtime attempts.
2. A minimal structured envelope, `{record_json: <JSON string>}`, works with
   `claude-opus-5`. The full canonical schema is included in the prompt and
   enforced locally. Provider structured output guarantees the envelope only,
   not the inner record. Canonical `schema.json` remains version 0.3.0.
3. Quote anchoring derives offsets only from unchanged, uniquely occurring
   verbatim text; already-correct repeated spans are retained. Absent, ambiguous,
   or altered text fails. Offset repairs are recorded, never textual corrections.
4. Default thinking exhausted ten first-batch output limits. Explicit
   `thinking: {type: disabled}` retained the 4,000-token cap and low effort and
   eliminated truncation in the final sample. Parsing now selects exactly one
   text block even when preceded by thinking, instead of assuming the first block.
5. Before the final retry, prompt changes covered partial-report classification,
   episode and dwell evidence, no container/null support pointers, no generic
   histories as discrete scenes, colour versus illumination, explicit affect,
   and excluding forbidden topics even from reasons and quotes. The exclusion
   regex was expanded; reading still found context-dependent misses.
6. After the final reading audit, further prompt instructions prohibit invalid
   enum placeholders, inferred emotion/material/scale, cross-trip transitions,
   transferring being motion to scenes, named identities for generic voices,
   and evidence borrowed from unrelated memories. They reinforce uncertainty
   flags. **These last prompt additions have not been generation-tested and do
   not establish that the semantic failures are fixed.** No further retries ran.

All-error batches now stop the normal invocation before another chunk is
submitted. `--collect-only` checks/harvests without generation (exit 2 pending,
0 collection complete, not necessarily 200 records complete). Definite HTTP
rejections release reservations; ambiguous submissions stay reserved until
reconciled. Error outcomes retain worker request IDs and error categories.
Accounting is in `extract-state.json`; HTTP request IDs are in `requests.jsonl`.
The last remote batch was `msgbatch_01NUTRFpGZ5KnbutZUszHkNL` and is fully harvested.
`pilot-retry-ids.txt` describes that historical seventeen-ID retry, not a new
approved retry set. The required initial dry-run and budgeted pilot invocation
were performed; neither successful completion of 200 nor full-pass readiness is
claimed. Full extraction remains unauthorized.

## Verification and remaining work

Inline offline checks passed for all ten hand-coded examples, structured-envelope
round trips, Unicode/ambiguous/non-verbatim anchoring, collection-only behavior,
all-error batch stopping, request-ID retention, thinking-plus-text parsing,
exclusion changes, and disabled-thinking parameters. No persistent test harness
was created. Final retained records validate against source text and canonical
schema; checkpoint outcomes agree with the six JSONL IDs, and usage-derived costs
agree with the ledger. No unresolved reservations remain.

Unfinished: 200 accepted pilot records; reliable scene extraction; independent
semantic validation; robust handling of vocabulary gaps and dual duration scales;
representative cost/fidelity estimates. A revised extractor needs a new reviewed
pilot before any full pass. Later phases must explicitly handle the absence of
scene evidence rather than manufacture distributions. No later-phase work was run.
