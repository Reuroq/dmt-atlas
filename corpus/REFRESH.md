# Weekly refresh

`refresh.py` harvests and keyword-tags new DMT posts. It never calls Claude,
submits extraction jobs, or installs services. Pending IDs do not authorize
extraction, and the pilot limits remain unchanged.

## Commands

Run from `/home/clawd/dmt-atlas/corpus` with
`/home/clawd/corpus-venv/bin/python -B refresh.py` and one mode:

| Mode | Effect |
| --- | --- |
| `--check` | Read baseline counts/newest timestamp; no network or writes |
| `--fetch --max-requests 100` | Fetch, merge, re-tag overlay, update pending queue |
| `--posts FILE` | Same merge/tag/queue workflow with an offline post JSONL file |
| `--retag` | Rebuild tags and restore missing pending entries without fetching |

Exit 0 means the requested mode completed; exit 2 means error, incomplete fetch,
request-budget exhaustion, or another writer holds the lock. Counts are printed
as one JSON object. `--check` inventories the baseline only; it is not a network
or full overlay health check. No live harvest has been verified during development.

## Read-only baseline and corpus-only overlay

| Role | Default path |
| --- | --- |
| Baseline posts (read only) | `../data/corpus/raw/DMT_posts.jsonl` |
| Baseline tagged IDs (read only) | `../data/corpus/reports.jsonl` |
| Tagging vocabulary (read only) | `../data/corpus/vocab.json`, optional `vocab_extra.json` |
| New raw posts | `refresh-data/raw/DMT_posts.jsonl` |
| Regenerated overlay tags | `refresh-data/reports.jsonl` |
| Additive pending queue | `pending_extraction.txt` |
| Shared writer lock | `.refresh.lock` |

The brief's append/re-tag operation is implemented as a corpus-local overlay,
because modifying `../data/` is prohibited. Existing baseline IDs are skipped;
new IDs are retained once. Overlay files are atomically replaced with their merged
contents, not appended in-place. The original baseline is neither copied nor
rewritten. New posts rejected by the keyword tagger remain in the raw overlay.

The script imports `../build/corpus_tag.py` without writing bytecode, reuses its
`load_vocab()` and `hits()`, and applies its default 400-character eligibility and
removed/deleted-text rules. It does **not** invoke its writing `main()` or regenerate
baseline charts/statistics. These tags are keyword candidates, not structured
scene evidence. Tag positions preserve the legacy single-newline join; extraction
evidence must instead use title + **two** newlines + selftext and Unicode offsets.

Pending IDs are a sorted union of previous queue entries and all overlay-tagged
IDs absent from baseline reports. Nothing is automatically dequeued, and removing
an entry manually does not mark it consumed: re-tagging can restore it. Integrating
the overlay into an authorized extractor requires explicit input/queue lifecycle
work; the current extractor does not automatically read these files.

Alternate inputs use `--raw`, `--reports`, and `--vocab-dir`. Alternate outputs use
`--state-dir` and `--pending`; every output must resolve under corpus/. Inputs and
outputs must not collide. All invocations share one corpus-wide lock, including
invocations using different state directories but the same pending queue.

## Fetch boundaries and failures

The watermark is the maximum timestamp across baseline and overlay, not the last
JSONL row. Search includes that whole second and deduplicates IDs, covering tied
timestamps. Search ends before the run's current integral Unix second. Older late
archive arrivals, edits/deletions to already retained posts, and historical gaps
are not reconciled by this incremental operation.

Requests use Arctic Shift `/api/posts/search`, `subreddit=DMT`, ascending order,
selectable fields, and `after=start-1`, `before=end` for a half-open integer window.
An auto page with 100+ rows is split into smaller date windows. A nonempty shorter
auto page is checked with an explicit `limit=100` request; a short fixed-limit page
completes that window. Saturated single-second windows fail closed. Completion
depends on the server honoring the fixed limit and exclusive date filters; these
live API semantics remain unverified. Invalid ranges, changed probe membership,
duplicate API IDs, or malformed responses fail without committing fetched data.

Request starts are at least one second apart. Each request has a 45-second timeout;
up to three attempts handle transport errors and HTTP 429/500/502/503/504. Retries
and completion probes count toward `--max-requests`. `Retry-After` is honored up to
60 seconds; longer delays stop the run for a later retry. Other HTTP failures stop
immediately. No partial fetch is committed when the request cap is reached.

After successful fetching and validation, raw, tags, and queue are replaced in that
order, synchronizing each file and its directory before moving to the next file.
This is recoverable, not a three-file atomic transaction. A crash after the
raw commit can leave derived files stale; run `--retag` to repair them without a
network dependency. Concurrent readers can observe that intermediate state. A crash
can also leave an unused dot-prefixed temporary file; it is not read as input.
`--retag` requires an existing raw overlay. If overlay tags exist but their raw
source is missing, refreshing stops: restore the raw source instead of erasing
derived tags. Duplicate JSON keys and non-finite JSON constants in baseline,
overlay, offline post input, or HTTP responses are errors, not silently accepted.

## Weekly unit texts

`refresh.service` and `refresh.timer` are system-unit texts for owner installation.
The service runs as `clawd`, with the filesystem read-only except corpus/. The timer
runs Sundays at 04:00 UTC plus up to 30 minutes of jitter; `Persistent=true` catches
missed schedules. The service caps a run at two hours and 100 HTTP attempts. Neither
unit performs extraction. They have been syntax-checked, not installed or started.
