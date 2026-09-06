# World integration plan (not installed)

Runtime: the unbundled ES module passes a headless Chrome smoke. Sampling remains
synchronous and uncached; synthetic 10,000-profile/link inputs took about 47 ms p95
per draw in Node here. Use a worker for large distributions if UI latency matters,
and retain one result per visit, never sample in the animation loop. Browser-scale
latency is not measured. See SAMPLER.md for benchmark commands and evidence costs.

No world files were modified. Current distributions contain no scenes, so do not
enable a measured-scene mode yet. An editorial scene may remain available if it is
clearly labeled as interpretation, not presented as a sampled corpus observation.

## Hook points

Load distributions once at application startup and import `sample` from
`../corpus/sampler.js` in a module adapter. Existing world code uses globals;
loading the sampler alone does not wire it into the renderer. Call it once per
visit before `trip.js build(s)`. Keep the result for the whole visit, not per frame.
On `no_evidence`, show that outcome; never silently substitute another realm or
keyword-tag frequencies. On input validation failure, report a data error.

Pass `result.parameters` into a future `build(s, parameters)` adapter. This is a
proposed signature, not a current API. Make constructors conditional on coded
features: the current unconditional motifs/actors would otherwise swamp sampled
marginals. Renderer mappings and numeric settings below are **art direction**,
not measured physical values. Missing fields must remain marked unknown; any
rendering necessities must be recorded separately as editorial choices.

| Sample field | Existing destination / required adapter |
|---|---|
| `place` | `trip.js build(s)` dispatch: waiting-room → `waiting`; domed-cathedral → `cathedral`; workshop-factory-market → `workshop`; garden → `garden`; hospital-operating-theater → `clinical`; void → `void`. Use full schema slugs with `the-` prefixes in the lookup. Other realms have no approved one-to-one renderer: return unsupported, not nearest match. |
| `light` | `trip.js light(color,intensity,...)`, hemisphere/directional lights in `build`, material `emissiveIntensity`; `fractal.js surface` uniform `radiance`. Pulsing/flashing requires an explicitly gated animation; no measured intensity or rate exists. |
| `colour` | `trip.js mat(color,...)`, `patterned(palette,...)`; `fractal.js surface` palette and colour uniforms. Add a token→palette adapter; keep multi-label colours together. Indescribable is not a numerical colour. |
| `motion` | `trip.js motions` callbacks and `animateBeings(t)`; `fractal.js` material `time` updates. Add independent feature gates/rate controls where shader motion is hard-coded. Do not equate “still” with a global frozen clock or invent measured speeds. |
| `geometry` | Gate `F.lattice`, `F.mandala`, `F.vault`, `F.arcade` and realm field constructors in `trip.js`; `fractal.js surface` pattern controls. Tokens without an implemented motif stay unsupported. |
| `material` | `trip.js mat` metalness/roughness/emissive settings and `patterned`; `fractal.js surface` relief/strength. Category→shader presets need authored mappings; numeric presets are not corpus measurements. |
| `density` | `trip.js dust(count,color,spread)` and constructor repetition loops, plus `F.lattice` layout. Scene density is not an entity count or fog density measurement. Add repetition controls; retain performance caps as editorial. |
| `scale` | `trip.js roomShell(w,l,h)`, bounds/entry/exit coordinates; `F.vault` radius/length, `F.lattice` radius/height, `F.arcade` width/height. Keep collision bounds aligned. “Boundless” is not an infinite mesh dimension. |
| `sound_seen` | Gate `trip.js visibleLanguage()` / `F.language(root,materials,motions)` for supported visible-speech/sound motifs. Other cross-modal tokens need new adapters. This is visual evidence, not an audio track specification. |
| scene `affect` | `trip.js updateUI()`/evidence UI: reported affect label only. There is no validated affect→colour, entity or motion knob; do not introduce one as measured. |
| `beings[].entity` | `trip.js being(kind,x,y,z,size,create)` → `GeometricBeings.create` in `beings.js`; explicit supported lookup only: machine elves→elf, jester→jester, divine feminine→mother, mantis→mantis. Use canonical entity slugs. Null/unsupported identity must not default to elf. |
| `beings[].form` | `beings.js create` body/joints construction; extend with form-token gates. Current kind-specific silhouettes are authored, not automatic form mappings. |
| `beings[].count` | Number of `trip.js being(...)` calls only for an exact supported `min === max`; intervals/open bounds remain bounds, not a uniform count draw. Being entries are not inferred individual counts. |
| `beings[].behaviour` | `trip.js animateBeings(t)`, actor `engaged`, and `beings.js` motions/joints: add behaviour-specific gates. Interaction state alone is not evidence of a reported behaviour. |
| `beings[].communication` | Gate supported gestures/visible symbols via actor joints or `visibleLanguage`; telepathy/direct-knowing remain evidence labels with no current literal rendering control. Coded `none` differs from an empty unknown list. |
| `beings[].affect` | Actor evidence panel; no existing calibrated pose/colour mapping. |
| `dwell` | `trip.js stage.duration` drives paced traversal. Only exact, unflagged elapsed bounds could supply seconds; subjective/unspecified or interval bounds stay evidence labels. Existing stage durations remain editorial. |

## Outgoing navigation

Use only `result.outgoing`, never the omitted raw scene transition. On
`outgoing.status === 'sampled'`, `outgoing.parameters.to` can propose the next
stage for `trip.js go(s)`/portal targets after the explicit realm→stage lookup.
Unknown or unimplemented destinations stay unsupported. `onward()` needs a new
adapter to consume this proposal; existing fixed-route choices remain editorial.
High/medium `order_confidence` is an evidence label, not movement speed.

`trigger` may gate an already implemented interaction (e.g. movement or entity
action); unimplemented causes remain labels, not invented interactions. `abruptness`
can select an authored veil envelope in the `transition.time` render-loop branch
(currently fixed .6/1.3 seconds). Exact envelope durations are not corpus measures.
Suppressed trigger/abruptness values are null/empty and cannot drive those controls.
Use `outgoing.evidence` for these fields; it deliberately cites the selected link
observation, not all reports in the scene profile.

`no_evidence` is not a measured end or a reason to reroll. Keep unsupported
navigation explicitly editorial. Calling `sample` anew at the destination gives
a new observed bundle, not a replay of the original report's trajectory; a
report-continuous journey would require a separate record-aware replay adapter.

## Evidence UI

Extend `trip.js openEvidence()` with `dataset_status`, the sampled bundle IDs,
field-level `evidence` and suppressed/unknown fields. Resolve `report_id` against
retained records, then dereference each observation pointer to supporting quotes;
do not derive quotes from keyword tags. Render source text with text nodes (or the
existing escaping helper), not unescaped HTML. Keep interpretations and measured
tokens separately labeled. Suppressed values have no positive-value evidence entry.
No-scene evidence and incomplete pilot fidelity must remain visible.
