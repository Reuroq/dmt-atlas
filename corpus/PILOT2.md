# v0.4 pilot20 and pilot200

## Pilot200 — final phase disposition, turn 3/3, 2026-09-06

**COMPLETE: 180/180 additional reports accepted, within the $3 phase cap.**
The original 200-report pilot now has 200 accepted v0.4 records. All required
pilot200 measurements are reported below; turn 2 verified the saved cohort,
scene-level anchor coverage, and usage accounting. Turns 2 and 3 made no API
requests. No further extraction or repair is needed to complete this phase.

| Final measure | Pilot200 only (n = 180) | Combined v0.4 (n = 200) |
| --- | --- | --- |
| Trip-classified records | 128/180 | 144/200 |
| Scenes | 392 | 431 |
| Anchored / retained quotes | 1,109/1,110 | 1,230/1,231 |
| Records with any flag | 135/180 (75%) | 152/200 (76%) |
| Measured cost including retry | $1.867267375 | $2.075844750 |
| Cost per selected report | $0.01037370764 | $0.01037922375 |

Combined cost projects to **$148.39** for an equivalent 14,297-report pass, or
**$146.32** for the remaining 14,097 after reusing the pilot. These usage-based
extrapolations exclude legacy spend and retain the limitations stated below.
Pilot200 headroom is $1.132732625; lifetime spend including legacy is
$4.358262625, with no outstanding reservations or unresolved failed cohort IDs.

Completion is not fidelity certification. Pilot20 passed its numerical gate
16/20, but its unchanged ten-record reading audit reports missed stages,
unsupported affect, classification and redaction errors, and temporal concerns.
The additional 180 records have not received a reading audit. The weak quote
and all six historical v0.3 records remain retained; no record was downgraded.

Aggregate2 may proceed only when assigned by the driver, using latest accepted
v0.4 records by ID and normalized descriptors. It and report2 were not started
here. **Full extraction still requires the owner's written authorization.**

## Pilot20 — final phase disposition, turn 3/3, 2026-09-06

**PASS: 16/20 qualifying records against a threshold of 14/20.** The required
ten-record reading audit is complete, and turn 2 verified the saved cohort and
usage accounting. All pilot20 deliverables are complete; no rerun is needed
under the brief's failed-gate repair rule. Turns 2 and 3 submitted no API requests.
Final phase cost is **$0.208577375**, or **$0.01042886875 per selected report**.

This is a numerical-gate pass, not fidelity certification. The audit below retains
the missed stages, unsupported affect, classification error, redaction miss, and
temporal/qualification concerns. No audited record was edited or downgraded.
The tested prompt and schema remain unchanged, preserving the pilot20 baseline.

Pilot200 is eligible only when separately assigned: the remaining 180 IDs from
the original 200, with a $3 incremental cap and $10 cumulative ceiling. No later
phase was started during pilot20. Full extraction remains unauthorized.

## Run and limits

Completed 2026-09-06 with the original first 20 tagged report IDs, joined to raw
sources by ID. Command:

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot20 --limit 20 --budget-usd 10
```

The $1 pilot20 cap includes retries; $10 is the cumulative lifetime ceiling,
including $2.282417875 of legacy spend. Full extraction is not authorized.
Conservative reservations split the cohort into three batches of 9, 8, and 3.
All 20 generation requests succeeded with the compact JSON-schema transport;
no grammar errors, structural failures, text-JSON fallback, or retries occurred.
The command exited 0. Six legacy records remain unchanged alongside the 20 new
v0.4 records; legacy records are not included in these metrics.

## Results — numerical gate PASS

| Metric | Result |
| --- | --- |
| Selected / accepted / attempted | 20 / 20 / 20 |
| Qualifying trip records with a scene and anchored quote | **16/20 (80%)**, threshold 14/20 |
| Non-report classifications / trip records without scenes | 4 / 0 |
| Scenes | 39; 1.95 per selected report |
| Scenes per record: 0 / 1 / 2 / 3 / 4 / 5 | 4 / 3 / 8 / 2 / 1 / 2 records |
| Anchored quotes | 121/121; no weak anchors |
| Anchor scores | 120 at 1.0; 1 at 0.990990991 |
| Redacted quotes | 1/121 |
| Records with any flag | 17/20 (85%); mostly unmapped free text |
| Phase cost / cost per selected or accepted report | **$0.208577375 / $0.01042886875** |
| Phase budget remaining / reserved | $0.791422625 / $0 |
| Lifetime spend including legacy / reserved | $2.490995250 / $0 |

Measured provider usage totals: 15,597 uncached input tokens, 78,527 cache-read
input tokens, 4,133 cache-creation input tokens, and 10,963 output tokens.
Mean total input is 4,912.85 tokens/report; mean output is 548.15. Cost uses
the configured batch rates, including cache reads and cache writes; this is
usage-based accounting, not an invoice reconciliation.

Flag-prefix record counts (overlapping, denominator 20): `unmapped` 16 (80%),
`empty_descriptor` 11 (55%), `excluded_text_redacted` 3 (15%), `redacted` 1 (5%).
Flags are not rejection or semantic-error counts.

Inline verification passed: unique fixed-cohort IDs, structural acceptance,
source-offset bounds, exact folded matches for unredacted score-1 quotes,
weak-anchor threshold consistency, ended jobs, zero reservations and phase cap.

## Gate and reading-audit method

Gate: at least 14 of the fixed 20 must have a retained v0.4 trip record with a
scene containing an anchored quote (score >= 0.85). Select the latest accepted
v0.4 attempt per ID; retain historical records and failed-attempt accounting.

Audit selection: the first ten cohort IDs in source-selection order, independent
of scene count or perceived quality. Compare each accepted record with its full
canonical source, including scene order, descriptions, beings, and quotes.

Report record-level rates: wrong place = a setting contradicted by or unsupported
by the source; missed scene = a distinct experienced setting/stage omitted;
invented detail = an unsupported positive descriptor, being, event, or certainty.
A record may contribute to multiple categories. Report classification errors and
redaction misses separately. Empty fields are not inventions; an unspecified
setting is not inherently wrong. Do not turn future plans or generic advice into
experienced scenes. These are descriptive audit findings, never rejection rules.

The gate passes and the ten-record reading audit below is complete. This permits
the separately assigned pilot200 phase under its $3 cap; it does not certify
fidelity. No pilot200 or full-pass requests were submitted this turn. Prompt and
schema were not changed, and no records were deleted or downgraded after review.

## Reading audit — first ten cohort IDs

Source text was read in full, joined by ID; no record is edited by this audit.
These ten records were reviewed without changing or downgrading them.

| ID | Trip / scenes | Source-to-record findings |
| --- | --- | --- |
| hvbtm | true / 2 | Shifting patterned faces and voluntary entry/exit are captured. Scene 1 blends a comparison with previous trips into the current sequence; temporal ambiguity, not a demonstrably fabricated presence. |
| k8f9v | true / 2 | Both experienced stages and altered bedroom visuals are captured; remembered medical/childhood episodes are not promoted to new trip scenes. Practical-use wording survives in quotes and a transition descriptor: redaction/content-filter miss. |
| oau3u | true / 5 | Vent, pixelated ordinary room, return to vent, and green cubic room occur in the right order. Scene 5 assigns retrospective fear of returning to the experienced scene. Sound is filed under motion and visual sharpness under light: descriptor-category concerns. |
| qqe9b | true / 2 | Panic-to-relief, floating and unchanged room are captured. Ordinary companions are included under beings; source-supported, but downstream entity prevalence must distinguish them. |
| qvwdb | true / 5 | Flashback sequence is captured; no actual visit to Hell is invented as a place. Scene 4's affect drops the conditional from the feared visit, although its quote retains it: certainty-loss concern. Bodily heaviness is filed under density. |
| s3i3v | true / 2 | Faces, three gender-described figures, gesture, touch and disappearance are captured. The explicit return of original perception/self-awareness is not recovered as a final scene; the second scene's quote ends at the figures disappearing. |
| sxnbj | true / 1 | Sparse personal experience is retained without invented visuals or setting. Its affect describes retrospective disappointment rather than a clearly reported in-trip feeling; temporal-attribution concern. |
| t43yv | false / 0 | Correctly identifies a future plan, not a reported trip. |
| uodcz | false / 0 | False negative: the specific recent breakthrough and sustained afterglow are personal experience, despite the surrounding advice request. At least one sparse experienced stage is omitted. |
| urywa | true / 1 | Retains the personal experience and exit outdoors, but merges a particular episode with a general fear-to-enjoyment pattern. `affect: peace` promotes the writer's conjecture about being afraid of happiness/peace into an experienced feeling. The outdoor exit is retained as a transition; no distinct outdoor phenomenology is described, so it is not counted as a missed scene. |

### Audit rates (record denominator n = 10)

- Wrong place: **0/10 (0%)**. Unknown settings are not errors.
- Missed scene/stage: **2/10 (20%)** — s3i3v's explicit return to original
  perception/self-awareness; uodcz's specific recent experience/afterglow.
- Invented detail, including unsupported experienced affect: **1/10 (10%)** —
  urywa's `peace`. No wholly fabricated visual setting or entity was identified.
- Classification error: **1/10 (10%)** — uodcz false negative.
- Practical-use content/redaction miss: **1/10 (10%)** — k8f9v. Local token
  matching is not a complete content filter; no leaked wording is reproduced here.
- Additional temporal/qualification concerns: **5/10 (50%)** — hvbtm, oau3u,
  qvwdb, sxnbj, urywa. These source-supported but ambiguously situated details
  are reported separately, not silently counted as wholly invented content.

Categories overlap; these are reading judgments on a fixed convenience sample,
not population estimates. A described return of original perception counts as a
stage; merely mentioning an exit without destination phenomenology does not.
Exact quotes do not resolve classification, temporal attribution, descriptor
placement, or scene coverage. Nothing in this audit changes record acceptance.

## Turn 2 — saved-cohort gate verification

Rechecked locally on 2026-09-06 without API calls. Rows follow the original
first-20 tagged IDs, joined to canonical sources by ID. Each row uses the latest
accepted v0.4 record; historical v0.3 records do not enter the denominator.
Anchored means score >= 0.85 with `weak_anchor: false`. A `0/0` entry means no
quotes, not a successful anchor rate.

| Report ID | Trip classification | Scenes | Anchored / total quotes | Qualifies |
| --- | --- | --- | --- | --- |
| hvbtm | yes | 2 | 6/6 | yes |
| k8f9v | yes | 2 | 6/6 | yes |
| oau3u | yes | 5 | 14/14 | yes |
| qqe9b | yes | 2 | 7/7 | yes |
| qvwdb | yes | 5 | 12/12 | yes |
| s3i3v | yes | 2 | 9/9 | yes |
| sxnbj | yes | 1 | 1/1 | yes |
| t43yv | no | 0 | 0/0 | no |
| uodcz | no | 0 | 0/0 | no |
| urywa | yes | 1 | 4/4 | yes |
| vxswt | yes | 1 | 5/5 | yes |
| wh63q | yes | 4 | 16/16 | yes |
| wm1gg | no | 0 | 0/0 | no |
| xrjhl | yes | 2 | 10/10 | yes |
| xvm2h | yes | 2 | 8/8 | yes |
| yb4yc | yes | 2 | 6/6 | yes |
| yef97 | no | 0 | 0/0 | no |
| zlujh | yes | 3 | 6/6 | yes |
| zy7fe | yes | 2 | 5/5 | yes |
| 103737 | yes | 3 | 6/6 | yes |
| **Total** | **16/20** | **39** | **121/121** | **16/20** |

The gate remains PASS, two qualifying records above the threshold. Classification
here is the saved model output, not an audit correction: uodcz remains a reported
false negative. All 16 trip-classified records have scenes and anchored quotes;
the four non-trip classifications account for every nonqualifying record.
The existing ten-record reading audit remains unchanged and is not extended by
this mechanical check.

Inline checks confirmed pinned cohort membership, one v0.4 attempt per cohort ID,
structural acceptance, source-span bounds, folded equality for unredacted
score-1 quotes, and weak-anchor threshold consistency. All three pilot20 jobs
are ended. Recalculation from provider usage reconciles to **$0.208577375**;
lifetime spend remains **$2.490995250**, with no reservations. There are no
pilot200 jobs. No records, prompt, schema, or extraction code were changed;
this turn adds **$0** spend and does not start a later phase.

## Pilot200 — run and measurement method

Started 2026-09-06 after assignment and the pilot20 numerical gate PASS:

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot200 --limit 180 --budget-usd 10
```

Selection is the remaining 180 IDs of the original first 200, joined to raw
sources by ID. The incremental phase cap is $3; `--budget-usd 10` is the cumulative
lifetime ceiling, including legacy and pilot20 spend. Conservative reservations
split the work into sequential batches. The tested prompt and schema are unchanged.

Pilot200 metrics cover these 180 selected IDs; combined v0.4 metrics cover the
original 200, selecting the latest accepted v0.4 record per ID and excluding legacy
v0.3 records. Costs retain all billed attempts, including failures or retries.
Scene and flag rates use accepted records unless explicitly labeled otherwise;
anchor-score distributions use retained scene quotes, including weak anchors.

The full-pass projection will multiply measured combined cost per selected report
by 14,297 joined reports, at the configured batch rates: $2.50/M uncached input,
$12.50/M output, $0.25/M cache reads, and $3.125/M five-minute cache writes.
It is an extrapolation from a fixed, nonrandom pilot, not a quote or a new spending
authorization. Source lengths, cache reuse, output lengths, and failures can differ.
The ten-record pilot20 audit above is not an audit of the additional 180 reports.

## Pilot200 — completed results, turn 1/3, 2026-09-06

All **180/180** selected reports now have accepted v0.4 records. The first command
exited 1 after ten sequential batches (27, 25, 22, 20, 19, 17, 16, 14, 13, 7):
179 accepted and one `invalid_request_error` for `1i8enw`. The provider diagnostic
was only “Invalid request data”; no specific grammar failure was identified.
That failed request reported no usage and carries $0 in the accounting.

One targeted retry, using the unchanged prompt/schema and JSON-schema transport,
succeeded and exited 0:

```sh
/home/clawd/corpus-venv/bin/python -B extract.py --phase pilot200 --limit 1 --ids /dev/stdin --retry-failed --budget-usd 10 <<'IDS'
1i8enw
IDS
```

The retry cost **$0.027693250**, included in all phase and combined costs below.
No text-JSON fallback or structural rejection occurred. All successful generations
ended with `end_turn`. All jobs are ended; lifetime and phase reservations are $0.
Six historical v0.3 records remain unchanged and are excluded from these metrics.

| Metric | Pilot200 only (n = 180) | Combined v0.4 (n = 200) |
| --- | --- | --- |
| Selected / accepted records | 180 / 180 | 200 / 200 |
| Generation attempts / batches | 181 / 11 | 201 / 14 |
| API-error attempts / all attempts | 1/181 (0.55%) | 1/201 (0.50%) |
| Unresolved failed IDs / structural rejections | 0 / 0 | 0 / 0 |
| Trip-classified records with scenes and anchored quotes | 128/180 (71.11%) | 144/200 (72%) |
| Non-trip classifications / trip records without scenes | 52 / 0 | 56 / 0 |
| Scenes / mean per accepted record | 392 / 2.1778 | 431 / 2.155 |
| Anchored / retained quotes | 1,109/1,110 (99.91%) | 1,230/1,231 (99.92%) |
| Redacted quotes / retained quotes | 17/1,110 | 18/1,231 |
| Records with any flag | 135/180 (75%) | 152/200 (76%) |
| Measured cost, including retry | **$1.867267375** | **$2.075844750** |
| Cost per selected or accepted report | **$0.01037370764** | **$0.01037922375** |

The pilot20 gate remains 16/20 against its threshold of 14/20. The combined
144/200 figure describes saved classifications; it is not a new fidelity gate.
Pilot200 phase headroom is **$1.132732625** under its $3 cap. Lifetime spend is
**$4.358262625**, including **$2.282417875** of legacy spend. Usage-based accounting
is not an invoice reconciliation.

### Scene counts

| Scenes per record | Pilot200 records (n = 180) | Combined records (n = 200) |
| --- | --- | --- |
| 0 | 52 | 56 |
| 1 | 33 | 36 |
| 2 | 23 | 31 |
| 3 | 29 | 31 |
| 4 | 22 | 23 |
| 5 | 6 | 8 |
| 6 | 7 | 7 |
| 7 | 6 | 6 |
| 8–10 | 0 | 0 |
| 11 | 1 | 1 |
| 12 | 0 | 0 |
| 13 | 1 | 1 |

### Anchor-score distribution

| Score interval | Pilot200 quotes (n = 1,110) | Combined quotes (n = 1,231) |
| --- | --- | --- |
| Exactly 1.0 | 1,107 | 1,227 |
| 0.95 <= score < 1.0 | 2 | 3 |
| 0.85 <= score < 0.95 | 0 | 0 |
| 0 <= score < 0.85 (weak, retained) | 1 | 1 |

Minimum score is **0.763888889**. The weak quote and its record were retained,
as required; every trip-classified record still has at least one anchored quote.
One quote has an ambiguous-anchor flag. High anchor scores establish text matching,
not correct classification, temporal attribution, scene coverage, or redaction.

### Flag rates

Counts are records with at least one flag of the named prefix; categories overlap.
They are not rejection counts or semantic-error rates.

| Flag prefix | Pilot200 (n = 180) | Combined (n = 200) |
| --- | --- | --- |
| `unmapped` | 128 (71.11%) | 144 (72%) |
| `empty_descriptor` | 75 (41.67%) | 86 (43%) |
| `excluded_text_redacted` | 31 (17.22%) | 34 (17%) |
| `redacted` | 15 (8.33%) | 16 (8%) |
| `ambiguous_anchor` | 1 (0.56%) | 1 (0.5%) |
| `weak_anchor` | 1 (0.56%) | 1 (0.5%) |

### Provider usage and full-pass projection

| Token counter | Pilot200 (180 accepted) | Combined (200 accepted) |
| --- | --- | --- |
| Uncached input | 141,445 | 157,042 |
| Cache-read input | 739,807 | 818,334 |
| Cache-creation input | 4,133 | 8,266 |
| Output | 105,263 | 116,226 |
| Mean total input per selected report | 4,918.8056 | 4,918.21 |
| Mean output per selected report | 584.7944 | 581.13 |

No one-hour cache-write tokens were reported. Recalculating each billed attempt
from these usage counters and configured batch rates reconciles to stored costs.

- Equivalent full pass over **14,297 joined reports**:
  $2.075844750 / 200 × 14,297 = **$148.39176195375 (about $148.39)**.
- Incremental remainder after reusing these 200 accepted records:
  $2.075844750 / 200 × 14,097 = **$146.31591720375 (about $146.32)**.
- These projections exclude legacy spend and assume the pilot's observed usage,
  cache behavior, and retry profile. The 12 tagged IDs lacking raw joins are not
  included. The full pass has not been submitted and remains unauthorized.

Inline verification passed for fixed-cohort membership, unique accepted v0.4 IDs,
record/job linkage, structural acceptance, quote-offset bounds, folded equality
for unredacted score-1 quotes, weak-anchor threshold flags, per-attempt usage/cost
reconciliation, ended jobs, zero reservations, and phase/lifetime caps. Prompt,
schema, and extraction code were not changed. No record was removed or downgraded
after review. Aggregate2 and report2 were not started.

## Pilot200 — saved-cohort verification, turn 2/3, 2026-09-06

Offline verification passed without API requests or extraction reruns. The pinned
pilot200 selection still equals the original first 200 IDs minus the first 20;
all 180 join to canonical source text by ID. There are exactly 200 accepted v0.4
records across the two cohorts, with no duplicate v0.4 IDs. Six historical v0.3
records remain retained and excluded from these measurements.

| Rechecked measure | Pilot200 (n = 180) | Combined v0.4 (n = 200) |
| --- | --- | --- |
| Accepted records | 180/180 | 200/200 |
| Trip classifications | 128/180 | 144/200 |
| Scenes with at least one anchored quote / all scenes | **392/392** | **431/431** |
| Anchored / retained quotes | 1,109/1,110 | 1,230/1,231 |
| Records with flags | 135/180 | 152/200 |
| Billed cost, including retries | $1.867267375 | $2.075844750 |

The scene-level check confirms that the retained weak quote does not leave any
scene without another anchored quote. This is text-match coverage, not a reading
audit or a finding that all experienced stages were extracted. The original
pilot20 numerical gate remains 16/20; its ten-record reading audit is unchanged.

Recomputed scene histograms, anchor-score bins, flag-prefix counts, redacted-quote
counts, and provider token totals match the tables above. Structural checks,
record/job linkage, Unicode source-span bounds, folded equality for unredacted
score-1 quotes, and weak-anchor threshold consistency passed. Every billed
attempt's usage reconciles to its stored cost; the one unbilled error remains in
attempt accounting, with no unresolved failed cohort ID.

All 23 lifetime jobs are ended, reservations are $0, and lifetime counters are
200 distinct batch IDs and five realtime slots, within the brief's 400/10 limits.
Lifetime spend remains $4.358262625 against $10; pilot200 headroom remains
$1.132732625 against its $3 phase cap. Combined cost per report remains
$0.01037922375, projecting $148.39176195375 for 14,297 joined reports or
$146.31591720375 for the 14,097-report remainder, excluding legacy spend.

This turn adds **$0** spend. Records, prompt, schema, and extraction code are
unchanged. No downstream phase was started; full extraction remains unauthorized.
