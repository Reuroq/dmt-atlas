#!/usr/bin/env python3
"""Incremental Arctic Shift harvest; never extracts or modifies ../data/.

--check inventories inputs without network or writes. --posts FILE exercises the
same merge/tag/queue path offline. --retag repairs derived files without fetching.
--fetch enables network. Weekly units are texts
for owner installation, not installed by this script.

The baseline is read-only. New raw posts and their re-generated keyword tags live
in refresh-data/. pending_extraction.txt is an additive queue, NOT authorization to
extract it. The extractor does not automatically consume these overlay files.
Tagging reuses corpus_tag.py's load_vocab/hits and default eligibility rules;
legacy tag positions use its single-newline text, NOT canonical evidence offsets.

Arctic Shift auto pages at 100+ rows trigger date-window bisection. Nonempty short
auto pages require a limit=100 completion probe; only a short fixed-limit page
establishes completeness. A saturated single second fails closed without skipping
ties. No new data is committed on fetch/validation failure.
Raw is committed before derived tags/queue; rerunning repairs interrupted writes.
"""
import argparse
from email.utils import parsedate_to_datetime
import fcntl
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT.parent / 'data' / 'corpus'
ENDPOINT = 'https://arctic-shift.photon-reddit.com/api/posts/search'
FIELDS = 'id,created_utc,author,title,selftext,link_flair_text,score,num_comments,url,over_18,post_hint'
SATURATED = 100


def require(condition, message):
    if not condition:
        raise ValueError(message)


def output_path(path):
    resolved = Path(path).resolve()
    require(resolved.is_relative_to(ROOT) and resolved != ROOT,
            'All outputs must stay under corpus/')
    require(not Path(path).is_symlink(), 'Output symlinks are not allowed')
    return resolved


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON object key')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Non-finite JSON constant')


def decode_json(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def rows(path):
    with Path(path).open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            require(bool(line.strip()), f'{path}:{number}: empty JSONL row')
            row = decode_json(line)
            require(isinstance(row, dict), f'{path}:{number}: expected object')
            yield row


def post_id(row):
    value = row.get('id')
    require(isinstance(value, str) and re.fullmatch('[0-9a-z]+', value),
            'Invalid Reddit post ID')
    return value


def timestamp(row):
    value = row.get('created_utc')
    require(type(value) in (int, float) and math.isfinite(value)
            and value >= 0 and int(value) == value, 'Invalid post timestamp')
    return int(value)


def validate_post(row):
    post_id(row)
    timestamp(row)
    for key in ('title', 'selftext'):
        require(row.get(key) is None or isinstance(row[key], str),
                f'Invalid post {key}')
    require(str(row.get('subreddit', 'DMT')).lower() == 'dmt',
            'Non-DMT post in response')


def inventory(raw, reports):
    ids, newest = set(), None
    for row in rows(raw):
        ident, date = post_id(row), timestamp(row)
        ids.add(ident)
        newest = date if newest is None else max(newest, date)
    require(newest is not None, 'Baseline raw file is empty; historical harvest refused')
    tagged = {post_id(row) for row in rows(reports)}
    return ids, newest, tagged


class ArcticClient:
    def __init__(self, max_requests):
        self.max_requests = max_requests
        self.requests = 0
        self.last_request = None

    def get(self, start, end, limit='auto'):
        query = urllib.parse.urlencode(dict(subreddit='DMT', after=start - 1,
                                           before=end, limit=limit, sort='asc', fields=FIELDS))
        request = urllib.request.Request(ENDPOINT + '?' + query,
                                         headers={'User-Agent': 'dmtatlas-refresh/1.0'})
        for attempt in range(3):
            require(self.requests < self.max_requests, 'Request cap reached; nothing committed')
            if self.last_request is not None:
                time.sleep(max(0, 1 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            self.requests += 1
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = decode_json(response.read())
                break
            except (urllib.error.URLError, TimeoutError) as error:
                delay = 2 ** attempt
                if isinstance(error, urllib.error.HTTPError):
                    try:
                        require(error.code in (429, 500, 502, 503, 504),
                                f'Non-retryable HTTP status {error.code}')
                        retry_after = error.headers.get('Retry-After') if error.headers else None
                        if retry_after:
                            if retry_after.isdigit():
                                delay = max(delay, int(retry_after))
                            else:
                                delay = max(delay, parsedate_to_datetime(retry_after).timestamp() - time.time())
                    finally:
                        error.close()
                require(attempt < 2 and self.requests < self.max_requests,
                        'HTTP retries/request budget exhausted; nothing committed')
                require(delay <= 60, 'Retry-After exceeds 60 seconds; retry a later run')
                time.sleep(delay)
        require(isinstance(data, dict) and isinstance(data.get('data'), list),
                'Malformed Arctic Shift response')
        batch = data['data']
        seen = set()
        for row in batch:
            require(isinstance(row, dict), 'Invalid response post')
            validate_post(row)
            ident = post_id(row)
            require(ident not in seen, 'Duplicate ID within API page')
            seen.add(ident)
            require(start <= timestamp(row) < end, 'API returned post outside requested window')
        return batch


def fetch_windows(client, start, end):
    """Half-open integral windows; overlap the baseline's newest second by ID."""
    if start >= end:
        return []
    windows, found = [(start, end)], {}
    while windows:
        low, high = windows.pop()
        batch = client.get(low, high)
        if 0 < len(batch) < SATURATED:
            probe = client.get(low, high, limit=SATURATED)
            require({post_id(row) for row in batch} <= {post_id(row) for row in probe},
                    'Archive changed between auto page and completion probe; retry later')
            batch = probe
        if len(batch) >= SATURATED:
            require(high - low > 1, 'Saturated single-second window; refusing to skip posts')
            middle = (low + high) // 2
            windows.extend([(middle, high), (low, middle)])
            continue
        for row in batch:
            ident = post_id(row)
            require(ident not in found, 'Duplicate ID across date windows')
            found[ident] = row
    return list(found.values())


def tag_posts(posts, vocab_dir):
    # Import without pycache writes in ../build/. Do not invoke its writing main().
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location('refresh_legacy_tagger',
                                                    ROOT.parent / 'build' / 'corpus_tag.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    module.C = str(vocab_dir)
    patterns = module.load_vocab()
    tagged = []
    for row in posts:
        text = (row.get('title') or '') + '\n' + (row.get('selftext') or '')
        if row.get('selftext') in ('[removed]', '[deleted]', None) or len(text) < 400:
            continue
        hits = module.hits(text, patterns)
        if not hits:
            continue
        tagged.append(dict(id=row['id'], sub='DMT', created_utc=row['created_utc'],
                           score=row.get('score'), flair=row.get('link_flair_text'),
                           chars=len(text), seq=[[kind, name] for _, kind, name in hits],
                           pos=[position for position, _, _ in hits]))
    return tagged


def atomic_write(path, text):
    path = output_path(path)
    handle, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(handle, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        # Persist the rename before committing the next derived file.
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def jsonl(data):
    return ''.join(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n' for row in data)


def run(args):
    baseline_ids, newest, baseline_reports = inventory(args.raw, args.reports)
    state = output_path(args.state_dir)
    raw = output_path(state / 'raw' / 'DMT_posts.jsonl')
    tags = output_path(state / 'reports.jsonl')
    pending = output_path(args.pending)
    # A single corpus-wide lock also protects queues shared by different state dirs.
    lock = output_path(ROOT / '.refresh.lock')
    outputs = {raw, tags, pending, lock}
    inputs = {Path(p).resolve() for p in (args.raw, args.reports,
              Path(args.vocab_dir) / 'vocab.json', Path(args.vocab_dir) / 'vocab_extra.json')}
    if args.posts:
        inputs.add(Path(args.posts).resolve())
    require(len(outputs) == 4 and not outputs & inputs, 'Input/output path collision')
    require(all(not path.exists() or path.is_file() for path in outputs),
            'Output paths must be regular files, not directories or special files')
    require(all(not child.is_relative_to(parent) for child in outputs for parent in outputs
                if child != parent), 'Output file paths may not contain one another')
    if args.check:
        return dict(mode='check', baseline_posts=len(baseline_ids),
                    baseline_reports=len(baseline_reports), newest_utc=newest)
    raw.parent.mkdir(parents=True, exist_ok=True)
    pending.parent.mkdir(parents=True, exist_ok=True)
    with lock.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(raw.exists() or not tags.exists(),
                'Overlay tags exist without raw source; restore raw before refreshing')
        require(not args.retag or raw.is_file(), '--retag requires an existing raw overlay')
        overlay = {}
        if raw.exists():
            for row in rows(raw):
                validate_post(row)
                ident = post_id(row)
                require(ident not in overlay, 'Duplicate overlay ID')
                if ident not in baseline_ids:
                    overlay[ident] = row
        cursor = max([newest] + [timestamp(row) for row in overlay.values()])
        client = ArcticClient(args.max_requests)
        end = int(time.time())
        require(cursor < end, 'Newest stored timestamp is current/future; retry later or repair input')
        incoming = (fetch_windows(client, cursor, end) if args.fetch else
                    [] if args.retag else list(rows(args.posts)))
        added = 0
        incoming_ids = {}
        for row in incoming:
            validate_post(row)
            ident = post_id(row)
            require(timestamp(row) < end, 'Incoming post has current/future timestamp')
            require(ident not in incoming_ids or incoming_ids[ident] == row,
                    'Conflicting duplicate incoming ID')
            incoming_ids[ident] = row
            if ident in overlay:
                require(timestamp(row) == timestamp(overlay[ident]),
                        'Incoming ID timestamp conflicts with retained overlay')
            if ident not in baseline_ids and ident not in overlay and timestamp(row) >= cursor:
                overlay[ident] = row
                added += 1
        ordered = sorted(overlay.values(), key=lambda row: (timestamp(row), int(row['id'], 36)))
        tagged = tag_posts(ordered, args.vocab_dir)
        queued = set()
        if pending.exists():
            for ident in pending.read_text(encoding='utf-8').splitlines():
                post_id({'id': ident})
                queued.add(ident)
        before = len(queued)
        queued.update(row['id'] for row in tagged if row['id'] not in baseline_reports)
        # Serialize everything before the first commit. Raw-first enables repair.
        raw_text, tag_text = jsonl(ordered), jsonl(tagged)
        queue_text = ''.join(ident + '\n' for ident in sorted(queued))
        atomic_write(raw, raw_text)
        atomic_write(tags, tag_text)
        atomic_write(pending, queue_text)
        return dict(mode='fetch' if args.fetch else 'retag' if args.retag else 'offline', requests=client.requests,
                    fetched_posts=len(incoming), new_posts=added, overlay_posts=len(ordered),
                    tagged_reports=len(tagged), new_pending=len(queued) - before,
                    pending_total=len(queued), newest_utc=max([newest] + [timestamp(r) for r in ordered]))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--fetch', action='store_true')
    mode.add_argument('--retag', action='store_true', help='Repair overlay tags/queue without network')
    mode.add_argument('--posts', type=Path, help='Offline API-post JSONL input')
    parser.add_argument('--raw', type=Path, default=BASELINE / 'raw' / 'DMT_posts.jsonl')
    parser.add_argument('--reports', type=Path, default=BASELINE / 'reports.jsonl')
    parser.add_argument('--vocab-dir', type=Path, default=BASELINE)
    parser.add_argument('--state-dir', type=Path, default=ROOT / 'refresh-data')
    parser.add_argument('--pending', type=Path, default=ROOT / 'pending_extraction.txt')
    parser.add_argument('--max-requests', type=int, default=100)
    args = parser.parse_args()
    try:
        require(args.max_requests > 0, '--max-requests must be positive')
        print(json.dumps(run(args), sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        # Do not echo remote response bodies or raw report text.
        print(f'refresh failed ({type(error).__name__}): {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
