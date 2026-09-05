# CORPUS — turn 14,297 trip reports into a measured distribution the world can sample

You are a second Astra instance. Another Astra is running the realism pass in `world/` right now
(`world/REDIRECT5.md`). **You never write outside `corpus/`.** You read `../data/`, `../world/` and
`../build/` freely. The two of you share nothing else. The owner watches `corpus/status.txt`.

## Why this exists (read once)
The atlas maps the DMT experience from 14,297 tagged Reddit reports (`../data/corpus/reports.jsonl`,
full text in `../data/corpus/raw/DMT_posts.jsonl`, key `selftext` + `title`; mean 370 words, median
235, p90 788). Today the tags are keyword hits: they say a node is *mentioned*, not what the scene
*looked like* or in what order things happened. `world/` renders one hand-built version of each
realm. The goal is a pipeline that (1) reads every report into a structured record, (2) aggregates
records into per-realm / per-being / per-transition distributions, (3) lets the world draw its scene
parameters from those distributions so every visit differs and the ensemble matches the reports,
(4) tests fidelity distributionally, and (5) refreshes weekly from new posts. You build all five as
code. The reading pass itself runs on the Claude API, not through you, and only after a costed pilot.

## Phases — the driver names the current phase and its required artifacts each turn
A turn is valid only if at least one of the phase's artifacts changes on disk. Each phase has a
budget of 3 turns; the driver moves on regardless. Say what is unfinished in `corpus/NOTES.md`.

1. **schema** → `corpus/schema.json` (JSON Schema, `additionalProperties: false`, every field
   `required` or nullable), `corpus/SCHEMA.md` (what each field means, with the coding rules), and
   `corpus/examples/*.json`: **10 records you extract by hand** from 10 reports you read yourself,
   chosen across eras and lengths. The record: `report_id`, `scenes[]` in experienced order, each
   with `place` (atlas realm slug or `other:<free text>`), `order_confidence`, descriptors as short
   controlled vocab lists for `light`, `colour`, `motion`, `geometry`, `material`, `density`,
   `scale`, `sound_seen`; `beings[]` per scene with `form`, `count`, `behaviour`, `communication`,
   `affect`; `transition` into the next scene (`trigger`, `abruptness`); `affect` of the scene;
   `quotes[]` = verbatim spans (`start`,`end` char offsets + text) that support the fields; and a
   top-level `is_trip_report` boolean with `reason` (many tagged posts are questions or art posts).
   Vocab lives in `corpus/vocab.json` — seed it from `../data/corpus/vocab.json`,
   `../data/corpus/vocab_extra.json` and `../data/atlas.json` node names; never invent a realm.
   **No dose, route, or sourcing fields.** The atlas's honesty charter (`../BUILD.md`) applies.
2. **harness** → `corpus/extract.py`. Python 3.12, interpreter `/home/clawd/corpus-venv/bin/python`
   (has `anthropic` 1.4.0). Reads report ids from `../data/corpus/reports.jsonl`, text from the raw
   file, submits **Message Batches** to `claude-opus-5` with structured output, checkpoints every
   result to `corpus/records/<batch>.jsonl` keyed by `report_id`, resumes by skipping done ids.
   Flags: `--limit N`, `--ids FILE`, `--dry-run` (uses `count_tokens` on a 50-report sample and
   prints the projected cost for N and for all 14,297), `--budget-usd X` = **hard stop**: the
   harness computes spend from `usage` on every result at batch rates ($2.50 in / $12.50 out /
   $0.25 cache-read per million tokens) and refuses to submit a batch that could exceed the cap.
   `--no-batch` is allowed for a 5-report smoke run at realtime rates ($5 / $25). Log every
   request id. The API key is `ANTHROPIC_API_KEY` in your environment; never print it.
3. **pilot** → run `extract.py --limit 200 --budget-usd 5` (batch). Then `corpus/PILOT.md`:
   measured tokens in/out per report, measured cost per report, **projected cost for all 14,297 at
   batch rates**, error rate, and your own quality audit: reread 20 source reports against their
   records and list every wrong field. Fix the schema/prompt, re-run only the failed 20 if needed.
   **The full run needs the owner's written go. Do not run it. The driver will not ask you to.**
4. **aggregate** → `corpus/aggregate.py` → `corpus/distributions.json` + `corpus/DISTRIBUTIONS.md`.
   Per realm: frequency of every descriptor value, being presence, being form/behaviour mix, dwell
   evidence; per being: form/behaviour/communication mix; transitions: realm→realm counts with
   trigger mix and abruptness; global: scene-count and order statistics. Every number carries `n`
   and the list of `report_id`s behind it (that is the evidence trail the world shows). It runs on
   the 200 pilot records now and on the full set later without change. Compare its realm
   prevalences against `../data/corpus/summary.json` and explain the differences.
5. **sampler** → `corpus/sampler.js` (plain ES module, no deps, runs in Node and the browser) +
   `corpus/SAMPLER.md` + `corpus/test_sampler.mjs`. `sample(distributions, realm, rng)` returns a
   parameter set for a scene drawn from the measured frequencies (categorical draws; correlated
   fields drawn jointly where the records show correlation) **with the `report_id`s that back each
   drawn value**. The test draws 1,000 scenes per realm and asserts every marginal is within 3
   points of the distribution. **Do not modify `world/`**; write `corpus/INTEGRATION.md` saying
   exactly which `world/trip.js` / `fractal.js` / `beings.js` knobs each sampled field should drive.
6. **fidelity** → `corpus/fidelity_dist.py`: given a directory of rendered frames named
   `<realm>-<k>.png` and a grades file, checks that feature frequencies across the frames match the
   distributions within tolerance (per-feature z-test, report the worst 10), and writes the
   blind-test protocol as `corpus/BLIND_TEST.md` (frame + three reports → which realm; how to run it
   on a reading model; the pass bar). It must run today on the 200-record distributions.
7. **refresh** → `corpus/refresh.py`: pulls posts newer than the newest id/date in the raw file
   from Arctic Shift (`https://arctic-shift.photon-reddit.com/api/posts/search`, params
   `subreddit=DMT`, `after=<unix>`, `limit=auto`, `fields=` selectable; 1 request/second; see
   `../build/harvest_corpus.py` if present for the exact working call), appends them, re-tags with
   `../build/corpus_tag.py`, writes the new report ids to `corpus/pending_extraction.txt`, and
   prints counts. It does **not** call the Claude API. Also write `corpus/refresh.timer` and
   `corpus/refresh.service` unit texts for a weekly run as `clawd` (the owner installs them).
8. **report** → `corpus/README.md`: what exists, how to run each piece, the pilot numbers, the
   exact command and cost for the full pass, and what the world gains once it runs. End with
   `<<CORPUS_DONE>>` alone on the last line of `corpus/NOTES.md`.

## API facts (current as of Sep 2026; your training may be stale — use these)
- Model id `claude-opus-5`. Thinking is on by default; do **not** send `budget_tokens`. Set
  `output_config={"effort": "low"}` for extraction; raise to `medium` only if the pilot audit shows
  misses that more thinking would fix.
- Structured output: `output_config={"effort": ..., "format": {"type": "json_schema", "schema": {...}}}`
  — the first content block is then text containing valid JSON; `json.loads` it. Schema needs
  `additionalProperties: false` and `required` on every object.
- Batches: `from anthropic.types.message_create_params import MessageCreateParamsNonStreaming`,
  `from anthropic.types.messages.batch_create_params import Request`;
  `client.messages.batches.create(requests=[Request(custom_id=..., params=MessageCreateParamsNonStreaming(model=..., max_tokens=..., system=[...], messages=[...], output_config=...))])`;
  poll `client.messages.batches.retrieve(id).processing_status == "ended"`; iterate
  `client.messages.batches.results(id)`; each has `.custom_id` and `.result.type` in
  succeeded/errored/canceled/expired; `.result.message.usage` has `input_tokens`, `output_tokens`,
  `cache_read_input_tokens`, `cache_creation_input_tokens`. Results arrive in any order — key by
  `custom_id`. Up to 100,000 requests per batch; most finish within an hour.
- Cache the system prompt + schema: `system=[{"type":"text","text":..., "cache_control":{"type":"ephemeral"}}]`.
- `client.messages.count_tokens(model=..., system=..., messages=...)` → `.input_tokens`.
- `max_tokens` 4000 for a record. Never truncate a report; long ones go through whole.
- Errors: catch `anthropic.RateLimitError`, then `anthropic.APIStatusError`, then
  `anthropic.APIConnectionError`; the SDK already retries 429/5xx twice.

## Hard lines
- Write only under `corpus/`. No git. No GUI. Headless only. Never print the API key.
- Never submit a batch without `--budget-usd`; never run more than the 200-report pilot plus one
  5-report smoke test. Total pilot spend cap: $8.
- No dose/route/sourcing content anywhere, including the vocab.
- Keep `corpus/status.txt` (one line) and `corpus/NOTES.md` (rewrite the last section each turn,
  under 40 lines) current. Every turn must change one of the current phase's artifacts.
- No new test harnesses beyond the ones named; no receipts-of-receipts; no hash ledgers.
