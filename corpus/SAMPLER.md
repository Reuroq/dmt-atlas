# Scene sampler

`sampler.js` is a dependency-free ES module for browsers and Node. It performs no
fetches, file writes, extraction, or rendering. Input is aggregate format `2.0.0`.

```js
import { sample } from './sampler.js';
const result = sample(distributions, 'the-waiting-room', Math.random);
if (result.status === 'sampled') renderMeasuredScene(result);
else showNoEvidence(result.reason);
```

The two application callbacks above are integration placeholders, not supplied APIs.
Node 20.19+ supports this `.js` ES module without a package change; older Node
may require `--experimental-default-type=module`.

## Draw and evidence contract

- Select one unqualified scene joint profile with probability `n / eligible_n`.
  Sampling is with replacement, weighted by scene observations, **not unique
  reports**. All descriptors, being entries and dwell fields come from that same
  bundle; there are no independent field draws, numeric interpolations or defaults.
- Context-flagged realm profiles are excluded. Individually flagged list elements
  are removed; flagged scalar/object fields become null. Other fields survive.
  A flagged being identity becomes null, not a guessed identity; its independently
  supported form/behaviour survives. Null or empty means not coded, not absence.
- `parameters` contains place, nine descriptor lists, beings, and dwell. `evidence`
  maps JSON pointers relative to `parameters` to `{n, report_ids, observations}`.
  Every non-null scalar (including list elements and count/dwell bounds) has support.
  Observations point into retained records and preserve original list indexes even
  when suppression compacts an output list. Evidence is the selected bundle's
  supporting subset, **not** all reports mentioning that value.
- `selection` identifies the distribution profile, weight, eligible denominator,
  suppressed source-relative fields and any additional context exclusions.
  Missing values and empty containers have no positive-value evidence; selection
  observations still identify their source bundle. Outputs are detached from input.
- Dwell description/basis/bounds remain a bundle. Never convert subjective or
  unspecified duration to elapsed seconds, or sample uniformly between bounds.
- Predecessor order and the raw transition are omitted from scene `parameters`.
  Qualified links are returned separately in `outgoing`, as described below.

## Qualified outgoing links

The same RNG draw also selects one observation uniformly within the chosen scene
profile (`selection.sampled_observation`). Its actual outgoing edge is looked up
by report ID and transition pointer. No second independent transition draw is
made: this preserves scene/link correlations, differences among identical scene
profiles, and observations with no eligible outgoing link.

`outgoing.status` is `sampled` or `no_evidence`. The latter is **not** evidence of
an experience ending; do not retry until a link appears. For sampled links,
`outgoing.parameters` contains `to`, destination `order_confidence`, `trigger`
and `abruptness`. `outgoing.evidence` uses pointers relative to those parameters,
with n=1 and the selected report ID. Destination fields point to the destination
record scene; trigger/abruptness point to the source transition. This is a smaller
support subset than the scene bundle's evidence. `selection.edge_pointer`
identifies the aggregate edge; both record endpoint pointers remain available.

Eligibility requires aggregate `sampling_eligible: true`, unflagged endpoints,
order and episode assignments, known endpoints, and high/medium destination
order confidence. A destination must be the consecutive scene in the same record;
same-episode qualification relies on the aggregate's validated metadata (episode
indices are not retained in joint profiles). Field flags still suppress individual
trigger/abruptness values. Contradictory scene/transition bundles, duplicate links,
missing transition profiles and nonconsecutive pointers throw data errors.

Outgoing event rates use eligible links divided by **all eligible source scenes**,
not the aggregate's all-adjacencies denominator. Compare per-scene link counts to
`edge.n / realm.unqualified.scenes.n` for canonical unqualified inputs. Do not
normalize over only the scenes with links or promise that destination parameters
come from this same episode: a subsequent independent `sample(d, to, rng)` draws
a new scene bundle. Replaying complete observed trajectories is not implemented.

Unknown/missing realms and empty eligible sets return `status: 'no_evidence'`,
`parameters: null`, empty evidence/IDs, and a reason. They consume no RNG draws.
Malformed versions/counts/profile evidence throw; invalid RNG outputs throw.
Scene observations must be unique within the requested realm's unqualified stratum,
including across profiles. Duplicate support would bias weights and is rejected.
Selected transition profiles also require consistent counts, IDs and unique pointers.
Runtime checks are structural and scoped to the requested stratum/selected link,
not a full schema, vocabulary or source-text audit of the entire distribution.
Use validated aggregate output; these checks cannot establish that evidence is true.
Pass an RNG returning finite numbers in `[0,1)` for reproducibility. No cache is
used, so replacing distributions does not reuse stale profiles.

## Current evidence and verification

Current retained data contains zero scenes: every canonical realm returns
`no_evidence`. The pilot failed fidelity and was incomplete. Sampler mechanics do
not establish semantic fidelity or representative prevalence.

Run `node test_sampler.mjs`. The test calls each realm 1,000 times, asserting
marginal deviations at most 0.03 where measured scenes exist. Today
those marginal checks are explicitly **unavailable**, not a fidelity pass.
The marginal suite checks all scene descriptor values, being presence and all four
being descriptor families, entity and count bounds (including null), dwell presence,
basis/description/bounds, and qualified edge/trigger/abruptness per-scene event rates.
Being descriptor rates use being entries as denominator; dwell scalar rates use
observed dwell bundles. Multi-label arrays are occurrences, not categorical shares.

The test also runs `aggregate.aggregate` offline in a foreground Python subprocess
on in-memory synthetic records covering all 31 canonical realms, then applies the
same marginal suite. It verifies every returned evidence scalar against those
synthetic source records and checks episode/order eligibility. No retained examples
or synthetic files are loaded/written as evidence. Enum values come from schema.json.
The test uses `/home/clawd/corpus-venv/bin/python`; the sampler itself requires no Python.

Marginal checks use 1,000 stratified uniforms in permuted order, with fixed seeded
jitter, to avoid an IID multiple-comparison lottery across thousands of bins.
This tests the categorical mapping, not IID randomness or semantic fidelity.
A separate fixed-seed IID 1,000-draw test checks .75 weighting and correlation.
Arbitrary IID runs can exceed .03 by chance. Current synthetic aggregate results:
8,215 marginals checked, 10,292 qualified links verified; production has zero
measurable marginals. Regression checks also reject duplicate scene support within
and across profiles, noncanonical scene pointers and inconsistent link counts,
and verify that an in-place distribution update takes effect on the next draw.

## Runtime and scale

`node test_sampler.mjs --browser --benchmark` additionally runs a real headless
Chrome module smoke and synthetic scale measurements. Chrome defaults to
`/usr/bin/google-chrome`; override with `SAMPLER_BROWSER`. This optional smoke uses
local file access and `--no-sandbox` only for its generated local fixture; these are
not deployment settings. Temporary browser files live under corpus and are removed.
The default suite does not require Chrome. No browser server or extraction is started.
The smoke imports the unbundled module with no Node globals and checks scenes,
links/missing links, evidence, no-evidence RNG behavior, invalid RNG and detached output.

Measured on Node 20.19.0 in this workspace (100 timed draws after five warmups;
synthetic inputs, milliseconds per call, no hardware-dependent timing assertions):

| Input in one realm | Median | p95 |
| --- | ---: | ---: |
| 100 distinct scene profiles + 100 links | 0.34 | 0.48 |
| 1,000 distinct scene profiles + 1,000 links | 2.70 | 3.92 |
| 10,000 distinct scene profiles + 10,000 links | 35.01 | 46.59 |
| One profile with 10,000 support observations (25 timed draws) | 12.65 | 19.50 |

Each draw validates all unqualified profiles/observations in the requested realm,
scans matching-source edge observations and the selected edge's joint profiles,
and validates the selected transition profile. Evidence/output copying scales with
the selected scene profile's support count times its non-null scalar count.
These costs are not constant-time; large evidence bundles can dominate allocation.
Sample once per visit, not per frame; use a worker for large inputs when UI latency
matters. Preserve returned support IDs/pointers rather than silently truncating them.
No index/cache is provided: input mutation remains observable without invalidation
rules. Full-corpus latency and browser scale are unmeasured; these synthetic timings
are not a performance guarantee or a corpus fidelity result.
