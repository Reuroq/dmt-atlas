#!/home/clawd/corpus-venv/bin/python
"""Budgeted pilot extraction. No API traffic at import; see --help.

Records are locally enriched JSONL; historical v0.3 records are retained.
Operational state contains usage and outstanding
reservations, never source text or rejected model output. A lost submission reply
fails closed: attach its known batch id with --resume-batch, never resubmit blindly.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import fcntl
import json
import math
import os
from pathlib import Path
import random
import re
import sys
import time
import uuid

from normalise import decode_record as decode_v04, normalise_record, structural_check

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT.parent / 'data/corpus/reports.jsonl'
RAW = ROOT.parent / 'data/corpus/raw/DMT_posts.jsonl'
MODEL = 'claude-opus-5'
MAX_TOKENS = 4000
CAP = Decimal('10')
STATE = ROOT / 'extract-state.json'
RATES = {'batch': (Decimal('2.50'), Decimal('12.50'), Decimal('0.25')),
         'smoke': (Decimal('5'), Decimal('25'), Decimal('0.50'))}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def read_json(path):
    return json.loads(path.read_text())


def decode_record(text):
    return decode_v04(text)


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def append(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        stream.write(compact(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def append_record(path, record):
    # Small pilot attempt files: rewriting atomically is cheap and prevents a torn
    # final JSONL line from making a recoverable batch unreadable on restart.
    existing = path.read_text() if path.exists() else ''
    atomic(path, existing + compact(record) + '\n')


@contextmanager
def locked():
    with (ROOT / '.extract.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another extractor holds the lock') from None
        yield


def rows(path):
    with path.open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def load_sources():
    ids = [row['id'] for row in rows(REPORTS)]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate report id in reports.jsonl')
    wanted, sources = set(ids), {}
    for row in rows(RAW):
        rid = row.get('id')
        if rid not in wanted:
            continue
        if rid in sources:
            raise ValueError('Duplicate raw source id: ' + rid)
        title, body = row.get('title') or '', row.get('selftext') or ''
        if not isinstance(title, str) or not isinstance(body, str):
            raise ValueError('Non-string source: ' + rid)
        sources[rid] = title + '\n\n' + body
    return ids, sources


def schema_check(value, node, schema, path=''):
    """Validate every keyword used by v0.3.0; unknown keywords fail closed.

    Deliberately not a general JSON Schema engine or a metaschema validator.
    """
    known = {'$schema', '$id', 'title', '$defs', '$ref', 'type', 'properties',
             'required', 'additionalProperties', 'items', 'anyOf', 'enum',
             'minimum', 'minLength', 'minItems', 'pattern'}
    if node.keys() - known:
        raise ValueError('Unsupported schema keyword')
    if '$ref' in node:
        ref = node['$ref']
        if not ref.startswith('#/$defs/'):
            raise ValueError('Unsupported schema reference')
        schema_check(value, schema['$defs'][ref.split('/')[-1]], schema, path)
    if 'anyOf' in node:
        for branch in node['anyOf']:
            try:
                schema_check(value, branch, schema, path)
                break
            except ValueError:
                pass
        else:
            raise ValueError(path + ': no anyOf branch matched')
    types = {'object': lambda x: isinstance(x, dict),
             'array': lambda x: isinstance(x, list),
             'string': lambda x: isinstance(x, str),
             'integer': lambda x: type(x) is int,
             'number': lambda x: type(x) in (int, float) and math.isfinite(x),
             'boolean': lambda x: type(x) is bool, 'null': lambda x: x is None}
    if 'type' in node and not types[node['type']](value):
        raise ValueError(path + ': wrong type')
    if 'enum' in node and value not in node['enum']:
        raise ValueError(path + ': invalid enum')
    if 'minimum' in node and value < node['minimum']:
        raise ValueError(path + ': below minimum')
    for keyword in ('minLength', 'minItems'):
        if keyword in node and len(value) < node[keyword]:
            raise ValueError(path + ': too short')
    if 'pattern' in node and not re.search(node['pattern'], value):
        raise ValueError(path + ': pattern mismatch')
    if isinstance(value, dict) and 'properties' in node:
        if set(node['required']) - value.keys():
            raise ValueError(path + ': missing keys')
        if node['additionalProperties'] is False and value.keys() - node['properties'].keys():
            raise ValueError(path + ': unexpected keys')
        for key, child in value.items():
            schema_check(child, node['properties'][key], schema, path + '/' + key)
    if isinstance(value, list) and 'items' in node:
        for index, child in enumerate(value):
            schema_check(child, node['items'], schema, path + '/' + str(index))


def leaves(value, path=''):
    if isinstance(value, dict):
        # An otherwise unqualified connection is itself a coded assertion.
        if path.endswith('/transition') and value == {'trigger': [], 'abruptness': None}:
            yield path
        for key, child in value.items():
            if key not in ('quotes', 'uncertain_fields', 'report_id', 'schema_version'):
                yield from leaves(child, path + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from leaves(child, path + '/' + str(index))
    elif value is not None and value != '':
        yield path


def validate(record, rid, source, schema):
    schema_check(record, schema, schema)
    if record['report_id'] != rid:
        raise ValueError('report_id mismatch')
    scenes = record['scenes']
    if not record['is_trip_report'] and scenes:
        raise ValueError('Non-report has scenes')
    substantive = set(leaves(record))
    covered = set()
    groups = [('', record['quotes'])] + [('/scenes/' + str(i) + '/', s['quotes'])
                                           for i, s in enumerate(scenes)]
    for prefix, quotes in groups:
        for quote in quotes:
            start, end = quote['start'], quote['end']
            if not 0 <= start < end <= len(source) or source[start:end] != quote['text']:
                raise ValueError('Quote offset/text mismatch')
            for pointer in quote['supports']:
                allowed = pointer.startswith(prefix) if prefix else pointer in ('/reason', '/is_trip_report')
                if not allowed or pointer not in substantive:
                    raise ValueError('Invalid support pointer')
                covered.add(pointer)
    unavailable = all(part.strip() in ('', '[deleted]', '[removed]') for part in source.split('\n\n'))
    required = substantive - ({'/reason', '/is_trip_report'} if unavailable and not record['is_trip_report'] else set())
    if required - covered:
        raise ValueError('Unsupported fields: ' + ','.join(sorted(required - covered)))

    def unique_lists(value, key=''):
        if isinstance(value, dict):
            for k, child in value.items():
                unique_lists(child, k)
        elif isinstance(value, list):
            if key not in ('scenes', 'beings', 'quotes') and len({compact(x) for x in value}) != len(value):
                raise ValueError('Duplicate list values')
            for child in value:
                unique_lists(child)
    unique_lists(record)
    previous = 0
    for i, scene in enumerate(scenes):
        episode = scene['episode_index']
        if episode not in (previous, previous + 1) or (i == 0 and episode != 1):
            raise ValueError('Invalid episode sequence')
        if episode != previous and scene['order_confidence'] is not None:
            raise ValueError('Episode starts with order confidence')
        boundary = i == len(scenes) - 1 or scenes[i + 1]['episode_index'] != episode
        if boundary and scene['transition'] is not None:
            raise ValueError('Transition crosses episode/end boundary')
        for pointer in scene['uncertain_fields']:
            if not pointer.startswith(f'/scenes/{i}/') or pointer not in covered or pointer.endswith('/transition'):
                raise ValueError('Invalid uncertainty pointer')
        for being in scene['beings']:
            count = being['count']
            if count and count['max'] is not None and count['min'] > count['max']:
                raise ValueError('Reversed count bounds')
            comm = being['communication']
            if 'none' in comm and len(comm) != 1:
                raise ValueError('Nonexclusive communication none')
        dwell = scene['dwell']
        if dwell and dwell['seconds_min'] is not None and dwell['seconds_max'] is not None:
            if dwell['seconds_min'] > dwell['seconds_max']:
                raise ValueError('Reversed dwell bounds')
        previous = episode
    check_excluded(record)


# A conservative quarantine guard, not a semantic safety or relevance proof.
# It never edits evidence. Reading audits still catch paraphrases and context.
EXCLUDED = re.compile(
    r'\b(?:dos(?:e|es|ed|ing|age))\b|'
    r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ug|milligrams?|micrograms?)\b|'
    r'\b(?:smok(?:e|ed|ing)|vap(?:e|ed|ing|ori[sz](?:e|ed|er|ing))|'
    r'inject(?:ed|ing|ion)?|snort(?:ed|ing)?|insufflat\w*|'
    r'sublingual(?:ly)?|intravenous(?:ly)?|oral(?:ly)?|'
    r'procure(?:d|ment)?|vendor|dealer|naphtha)\b', re.IGNORECASE)


def check_excluded(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key not in ('report_id', 'schema_version', 'supports', 'uncertain_fields'):
                check_excluded(child)
    elif isinstance(value, list):
        for child in value:
            check_excluded(child)
    elif isinstance(value, str) and EXCLUDED.search(value):
        raise ValueError('Excluded-content guard matched; reading review required')


def usage_cost(usage, mode):
    incoming, outgoing, cached = RATES[mode]
    usage = dict(usage)
    # SDK cache counters are optional; omitted/null counters mean no cache use.
    # Required input/output counters must never be defaulted to zero.
    for key in ('cache_read_input_tokens', 'cache_creation_input_tokens'):
        if usage.get(key) is None:
            usage[key] = 0
    for key in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise ValueError('Missing or invalid usage; reservation retained')
    creation = usage.get('cache_creation') or {}
    if not isinstance(creation, dict):
        raise ValueError('Invalid cache usage; reservation retained')
    long_cache = creation.get('ephemeral_1h_input_tokens', 0)
    if type(long_cache) is not int or not 0 <= long_cache <= usage['cache_creation_input_tokens']:
        raise ValueError('Invalid cache usage; reservation retained')
    # Five-minute ephemeral cache writes cost 1.25x uncached input. Reserve
    # conservatively too; do not treat writes as free or as cache reads.
    return (Decimal(usage.get('input_tokens', 0)) * incoming
            + Decimal(usage.get('output_tokens', 0)) * outgoing
            + Decimal(usage.get('cache_read_input_tokens', 0)) * cached
            + Decimal(usage['cache_creation_input_tokens']) * incoming * Decimal('1.25')
            + Decimal(long_cache) * incoming * Decimal('0.75')) / 1_000_000


def totals(state):
    spent = Decimal(0)
    reserved = Decimal(0)
    for job in state['jobs']:
        for item in job['items'].values():
            if 'outcome' in item:
                spent += Decimal(item['outcome']['cost'])
            else:
                reserved += Decimal(item['reserve'])
    return spent, reserved


def save(state):
    atomic(STATE, compact(state) + '\n')


def check_state(state, sources, done):
    if state.get('version') != 1 or not isinstance(state.get('jobs'), list):
        raise ValueError('Unknown checkpoint format')
    known, accepted, jobs = set(), set(), set()
    for job in state['jobs']:
        if not re.fullmatch(r'(?:batch|smoke)-[a-f0-9]{32}', job['local_id']) or job['local_id'] in jobs:
            raise ValueError('Invalid/duplicate checkpoint job id')
        jobs.add(job['local_id'])
        if job['mode'] not in RATES or not job['items']:
            raise ValueError('Invalid checkpoint job')
        for rid, item in job['items'].items():
            known.add(rid)
            if rid not in sources or item.get('custom_id') != job['local_id'] + '-' + rid:
                raise ValueError('Checkpoint source/custom_id mismatch')
            reserve = Decimal(item['reserve'])
            if not reserve.is_finite() or reserve <= 0:
                raise ValueError('Invalid reservation')
            if 'outcome' in item:
                outcome = item['outcome']
                status = outcome['status']
                if status not in ('accepted', 'invalid', 'errored', 'canceled', 'expired', 'not_submitted'):
                    raise ValueError('Unknown checkpoint outcome')
                cost = Decimal(outcome['cost'])
                if not cost.is_finite() or cost < 0 or (cost > reserve and not state.get('halted')):
                    raise ValueError('Invalid checkpoint cost')
                if status in ('accepted', 'invalid'):
                    if 'usage' not in outcome or usage_cost(outcome['usage'], job['mode']) != cost:
                        raise ValueError('Checkpoint usage/cost mismatch')
                elif cost != 0 or 'usage' in outcome:
                    raise ValueError('Invalid nonbillable checkpoint outcome')
                if outcome['status'] == 'accepted':
                    accepted.add(rid)
            elif job.get('ended'):
                raise ValueError('Ended job has unresolved reservations')
    # A record written just before a crash may still have a pending outcome.
    # Its original request must be replayed to recover accounting, not regenerated.
    if done - known or accepted - done:
        raise ValueError('Records and accounting disagree; reconcile before continuing')
    batch_ids = {rid for j in state['jobs'] if j['mode'] == 'batch' for rid in j['items']}
    smoke_attempts = sum(len(j['items']) for j in state['jobs'] if j['mode'] == 'smoke')
    if len(batch_ids) > 400 or smoke_attempts > 10:
        raise ValueError('Checkpoint exceeds lifetime pilot/smoke cap')


def output_schema():
    """Compact enum-free v0.4 provider schema, not the enriched storage shape."""
    return read_json(ROOT / 'schema.json')


def parameters(rid, source, schema, system, text_json=False):
    config = {'effort': 'low'}
    if not text_json:
        config['format'] = {'type': 'json_schema', 'schema': schema}
    # Thinking is deliberately left at the provider default, per CORPUS2.
    return {'model': MODEL, 'max_tokens': MAX_TOKENS, 'system': system,
            'messages': [{'role': 'user', 'content': compact({'report_id': rid, 'source': source})}],
            'output_config': config}


def build_system(schema):
    prompt = (ROOT / 'prompt.md').read_text()
    if compact(schema) not in prompt:
        raise ValueError('prompt.md provider schema is stale')
    return [{'type': 'text', 'text': prompt, 'cache_control': {'type': 'ephemeral'}}]


def stored_records(sources):
    for path in sorted((ROOT / 'records').glob('*.jsonl')):
        for record in rows(path):
            if record.get('report_id') not in sources:
                raise ValueError('Unknown checkpoint report id')
            # Storage enrichment is not the provider shape. No semantic review here.
            structural_check(record)
            yield record


def accepted_records(sources, schema=None, version=None):
    return {r['report_id'] for r in stored_records(sources)
            if version is None or r.get('schema_version') == version}


def latest_records(sources):
    latest = {}
    for record in stored_records(sources):
        if record.get('schema_version') != '0.4.0':
            continue
        rid = record['report_id']
        rank = record.get('_extraction', {}).get('attempt', 0)
        if rid not in latest or rank > latest[rid].get('_extraction', {}).get('attempt', 0):
            latest[rid] = record
    return latest


def verify_record_jobs(state, sources):
    """Allow historical versions and retries, but reconcile each new accepted attempt."""
    jobs = {j['local_id']: j for j in state['jobs']}
    seen = set()
    for record in stored_records(sources):
        if record.get('schema_version') != '0.4.0':
            continue
        meta = record.get('_extraction', {})
        pair = (meta.get('job'), record['report_id'])
        if pair in seen or pair[0] not in jobs or pair[1] not in jobs[pair[0]]['items']:
            raise ValueError('Unaccounted or duplicate v0.4 record attempt')
        seen.add(pair)
        outcome = jobs[pair[0]]['items'][pair[1]].get('outcome')
        if outcome and outcome['status'] != 'accepted':
            raise ValueError('Stored v0.4 record disagrees with outcome')
    for job in state['jobs']:
        if job.get('schema_version') == '0.4.0':
            if job.get('phase') not in PHASE_CAPS:
                raise ValueError('v0.4 job lacks an authorized phase')
            for rid, item in job['items'].items():
                if item.get('outcome', {}).get('status') == 'accepted' and (job['local_id'], rid) not in seen:
                    raise ValueError('Accepted v0.4 attempt missing its record')


PHASE_CAPS = {'pilot20': Decimal('1'), 'pilot200': Decimal('3')}


def pilot_cohorts(ids):
    original = ids[:200]
    if len(original) != 200 or len(set(original)) != 200:
        raise ValueError('Original 200-report cohort unavailable')
    return {'pilot20': original[:20], 'pilot200': original[20:]}


def pin_cohorts(state, cohorts):
    if state.get('v04_cohorts', cohorts) != cohorts:
        raise ValueError('Pinned pilot selection changed; never rotate cohorts')
    if 'v04_cohorts' not in state:
        if any(j.get('schema_version') == '0.4.0' for j in state['jobs']):
            raise ValueError('Missing cohort checkpoint for existing v0.4 work')
        state['v04_cohorts'] = cohorts
    for job in state['jobs']:
        if job.get('schema_version') == '0.4.0':
            if job.get('phase') not in cohorts or set(job['items']) - set(cohorts[job['phase']]):
                raise ValueError('Checkpoint job is outside its pinned pilot cohort')


def pilot20_gate(records, cohort):
    qualifying = []
    for rid in cohort:
        record = records.get(rid, {})
        if record.get('is_trip_report') is not True:
            continue
        if any(any(isinstance(q, dict) and not q.get('weak_anchor', True)
                   and isinstance(q.get('anchor_score'), (int, float))
                   and q['anchor_score'] >= .85
                   for q in scene.get('quotes', [])) for scene in record.get('scenes', [])):
            qualifying.append(rid)
    return {'passed': len(cohort) == 20 and len(qualifying) >= 14,
            'qualifying': len(qualifying), 'denominator': 20}


def phase_available(state, cap, phase):
    lifetime = available_budget(state, min(cap, CAP))
    spent, reserved = totals({'jobs': [j for j in state['jobs'] if j.get('phase') == phase]})
    remaining = PHASE_CAPS[phase] - spent - reserved
    if remaining < 0:
        raise ValueError('Phase spend plus reservations exceeds cap; generation blocked')
    return min(lifetime, remaining)


def anchor_quotes(record, source):
    """Derive code-point offsets only for uniquely occurring verbatim quote text.

    Never alter text, guess between repeated occurrences, or repair the source.
    Already-correct spans retain their supplied offsets even when text repeats.
    """
    repaired = 0
    groups = [record['quotes']] + [scene['quotes'] for scene in record['scenes']]
    for quotes in groups:
        for quote in quotes:
            start, end, text = quote['start'], quote['end'], quote['text']
            if 0 <= start < end <= len(source) and source[start:end] == text:
                continue
            found = source.find(text)
            if not text or found < 0 or source.find(text, found + 1) >= 0:
                raise ValueError('Quote is not uniquely anchorable verbatim')
            quote['start'], quote['end'] = found, found + len(text)
            repaired += 1
    return repaired


def accept_result(state, job, rid, result, sources, schema, done):
    if rid not in job['items']:
        raise ValueError('Unexpected batch custom_id')
    item = job['items'][rid]
    if 'outcome' in item:
        return
    outcome = {'status': result.type, 'cost': '0'}
    if result.type == 'succeeded':
        message = result.message
        usage = message.usage.model_dump()
        cost = usage_cost(usage, job['mode'])
        outcome.update(usage=usage, cost=str(cost), message_id=message.id,
                       stop_reason=message.stop_reason)
        try:
            blocks = [block.text for block in message.content if block.type == 'text']
            record = decode_record('\n'.join(blocks))
            if isinstance(record, dict) and set(record) == {'record_json'}:
                record = decode_record(record['record_json'])
            record = normalise_record(record, sources[rid], rid)
            if message.stop_reason != 'end_turn':
                record['flags'].append('stop_reason:' + str(message.stop_reason))
            record['_extraction'] = {'job': job['local_id'], 'phase': job.get('phase'),
                                     'attempt': next(i for i, j in enumerate(state['jobs'], 1)
                                                     if j['local_id'] == job['local_id'])}
        except (ValueError, TypeError, KeyError) as error:
            # Only validator messages, not raw API error bodies or rejected text.
            diagnostic = str(error) if isinstance(error, ValueError) else type(error).__name__
            outcome.update(status='invalid', error=diagnostic[:400])
        else:
            path = ROOT / 'records' / (job['local_id'] + '.jsonl')
            # A crash after the durable record write must not append a duplicate.
            already_written = path.exists() and any(r.get('report_id') == rid for r in rows(path))
            if not already_written:
                append_record(path, record)
            done.add(rid)
            outcome['status'] = 'accepted'
    elif result.type == 'errored':
        error_body = result.error.model_dump()
        outcome['request_id'] = error_body.get('request_id')
        outcome['error_type'] = error_body.get('error', {}).get('type')
    elif result.type not in ('canceled', 'expired'):
        raise ValueError('Unknown result type; reservation retained')
    item['outcome'] = outcome
    if Decimal(outcome['cost']) > Decimal(item['reserve']):
        state['halted'] = 'usage exceeded reservation'
        # Continue collecting already-billable results. main refuses any new
        # submission once collection ends, including on later invocations.
    save(state)


def result_ids(job):
    return {item['custom_id']: rid for rid, item in job['items'].items()}


def available_budget(state, cap):
    if state.get('halted'):
        raise ValueError('Usage exceeded reservation; collected results, new submissions halted')
    spent, reserved = totals(state)
    if spent + reserved > cap:
        raise ValueError('Prior spend plus reservations exceeds supplied cumulative cap')
    return cap - spent - reserved


def budget_argument(text):
    try:
        return Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError('budget must be a decimal dollar amount') from None


def submit_once(client, state, job, requests):
    import anthropic
    submit_client = client.with_options(max_retries=0)

    def rejected(error):
        # Definite rejected requests have no remote work to recover. Timeouts,
        # connection failures and 5xx remain ambiguous and keep reservations.
        if error.status_code in (400, 401, 403, 404, 413, 422, 429):
            for item in job['items'].values():
                item['outcome'] = {'status': 'not_submitted', 'cost': '0',
                                   'http_status': error.status_code,
                                   'request_id': error.request_id}
            job['ended'] = True
            save(state)
    try:
        if job['mode'] == 'smoke':
            return submit_client.messages.create(**requests[0]['params'])
        return submit_client.messages.batches.create(requests=requests)
    except anthropic.RateLimitError as error:
        rejected(error)
        raise
    except anthropic.APIStatusError as error:
        rejected(error)
        raise
    except anthropic.APIConnectionError:
        raise


def reconcile_batch(client, state, batch_id):
    unresolved = [j for j in state['jobs'] if j['mode'] == 'batch' and not j.get('batch_id') and not j.get('ended')]
    if len(unresolved) != 1:
        raise ValueError('Expected exactly one unresolved batch submission')
    if any(j.get('batch_id') == batch_id for j in state['jobs']):
        raise ValueError('Remote batch already attached')
    remote = client.messages.batches.retrieve(batch_id)
    if remote.processing_status != 'ended':
        raise ValueError('Remote batch must end before identity can be reconciled; reservation retained')
    identifiers = [result.custom_id for result in client.messages.batches.results(batch_id)]
    expected = result_ids(unresolved[0])
    if len(identifiers) != len(expected) or set(identifiers) != set(expected):
        raise ValueError('Remote batch custom ids do not match reservation')
    unresolved[0]['batch_id'] = batch_id
    save(state)


def retrieve(client, state, job, sources, schema, done, wait=True):
    batch_id = job.get('batch_id')
    if not batch_id:
        raise ValueError('Unresolved submission ' + job['local_id'] + '; reconcile before proceeding')
    while client.messages.batches.retrieve(batch_id).processing_status != 'ended':
        print('Waiting for batch ' + batch_id, flush=True)
        if not wait:
            return False
        time.sleep(30)
    mapping, seen = result_ids(job), set()
    for result in client.messages.batches.results(batch_id):
        if result.custom_id not in mapping or result.custom_id in seen:
            raise ValueError('Unknown/duplicate batch result id; checkpoint retained')
        seen.add(result.custom_id)
        accept_result(state, job, mapping[result.custom_id], result.result, sources, schema, done)
    if seen != set(mapping):
        raise ValueError('Batch result stream incomplete; checkpoint retained')
    if any('outcome' not in item for item in job['items'].values()):
        raise ValueError('Batch result stream incomplete; reservations retained')
    job['ended'] = True
    save(state)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=200)
    parser.add_argument('--phase', choices=tuple(PHASE_CAPS), default='pilot20', help='Pinned cohort and incremental phase cap: pilot20 $1; pilot200 $3 after gate')
    parser.add_argument('--retry-cohort', action='store_true', help='Explicitly rerun the same full pilot20 cohort; retain prior records and charge all retries')
    parser.add_argument('--ids', type=Path, help='One exact report id per line')
    parser.add_argument('--dry-run', action='store_true', help='Count up to 50 phase sources; no generation')
    parser.add_argument('--budget-usd', type=budget_argument, help='Cumulative extraction cap, including prior runs; max $10')
    parser.add_argument('--no-batch', action='store_true', help='Realtime smoke: at most 5 per invocation, 10 lifetime slots')
    parser.add_argument('--check-schema', action='store_true', help='One live token-count request with schema and few-shots; no generation')
    parser.add_argument('--text-json', action='store_true', help='Omit provider grammar; retain schema in prompt (fallback after grammar rejection)')
    parser.add_argument('--resume-batch', help='Attach remote batch id to the single unresolved batch submission')
    parser.add_argument('--retry-failed', action='store_true', help='Retry only failed ids explicitly listed in --ids')
    parser.add_argument('--collect-only', action='store_true', help='Check existing batches once; harvest ended results, never submit generation')
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 200:
        parser.error('--limit must be 1..200; full extraction is not authorized')
    if args.budget_usd is None:
        parser.error('--budget-usd is required for generation or resumption')
    if args.budget_usd is not None and (not args.budget_usd.is_finite() or not 0 < args.budget_usd <= CAP):
        parser.error('--budget-usd must be finite, positive, and at most 10')
    if args.no_batch and args.limit > 5:
        parser.error('--no-batch requires --limit <= 5')
    if args.retry_failed and (not args.ids or args.dry_run):
        parser.error('--retry-failed requires --ids and generation mode')
    if args.resume_batch and args.dry_run:
        parser.error('--resume-batch cannot be combined with --dry-run')
    if args.collect_only and (args.dry_run or args.retry_failed or args.no_batch):
        parser.error('--collect-only cannot be combined with --dry-run, --retry-failed, or --no-batch')
    if args.check_schema and (args.dry_run or args.collect_only or args.retry_failed or args.resume_batch or args.no_batch):
        parser.error('--check-schema cannot be combined with operational modes')
    if args.retry_cohort and (args.phase != 'pilot20' or args.retry_failed or args.dry_run
                              or args.check_schema or args.collect_only or args.resume_batch or args.no_batch):
        parser.error('--retry-cohort is a pilot20 batch-generation mode only')
    schema = read_json(ROOT / 'schema.json')
    ids, sources = load_sources()
    cohorts = pilot_cohorts(ids)
    ids = cohorts[args.phase]
    if args.ids:
        chosen = args.ids.read_text().split()
        if len(set(chosen)) != len(chosen) or set(chosen) - set(ids):
            raise ValueError('Duplicate ids or ids outside the authorized phase cohort')
        ids = chosen
    # Stable selection: limit BEFORE skipping completed ids prevents a resumed
    # --limit 200 from silently advancing to a second 200-report cohort.
    selected = ids[:args.limit]
    if not selected:
        raise ValueError('Empty selection')
    if args.retry_cohort and set(selected) != set(cohorts['pilot20']):
        raise ValueError('--retry-cohort requires exactly the original 20 pilot IDs')
    if set(selected) - sources.keys():
        raise ValueError('Selected ids have no raw source: ' + ','.join(sorted(set(selected) - sources.keys())))
    system = build_system(schema)
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    def log_response(response):
        append(ROOT / 'requests.jsonl', {'time': time.time(), 'status': response.status_code,
               'request_id': response.headers.get('request-id'),
               'operation': response.request.url.path})

    with locked(), anthropic.Anthropic(http_client=anthropic.DefaultHttpxClient(
            event_hooks={'response': [log_response]})) as client:
        if args.check_schema:
            if not selected:
                raise ValueError('No source selected for schema check')
            params = parameters(selected[0], sources[selected[0]], schema, system, args.text_json)
            params.pop('max_tokens')
            counted = client.messages.count_tokens(**params).input_tokens
            print(compact({'schema_check': 'count_tokens_accepted', 'input_tokens': counted,
                           'provider_schema_bytes': len(compact(schema).encode('utf-8')),
                           'transport': 'text_json' if args.text_json else 'json_schema',
                           'generation_submitted': False,
                           'limitation': 'Token counting does not prove generation grammar compilation'}))
            return 0
        if args.dry_run:
            available_ids = [rid for rid in ids if rid in sources]
            sample = random.Random(20260905).sample(available_ids, min(50, len(available_ids)))
            if not sample:
                raise ValueError('No reports to sample')
            counts = []
            for rid in sample:
                params = parameters(rid, sources[rid], schema, system, args.text_json)
                params.pop('max_tokens')
                counts.append(client.messages.count_tokens(**params).input_tokens)
            mean = Decimal(sum(counts)) / len(counts)
            print(compact({'sample_n': len(counts), 'mean_input_tokens': float(mean),
                'tagged_ids': len(ids), 'joined_sources': len(sources),
                'output_tokens': 'unmeasured; scenarios, not measured cost',
                'batch_projections_usd': {str(n): {str(out): float((mean * Decimal('2.5') + out * Decimal('12.5')) * n / 1_000_000)
                    for out in (1000, 2000, 4000)} for n in (len(selected), len(sources))},
                'cache_assumption': 'uncached input; cache writes can add 25% to input cost'}))
            return
        state = read_json(STATE) if STATE.exists() else {'version': 1, 'jobs': []}
        check_state(state, sources, accepted_records(sources))
        verify_record_jobs(state, sources)
        pin_cohorts(state, cohorts)
        done = accepted_records(sources, version='0.4.0')
        initial_jobs = {j['local_id'] for j in state['jobs']}
        recovered_jobs = {j['local_id'] for j in state['jobs'] if not j.get('ended')}
        if args.retry_cohort and any(not j.get('ended') for j in state['jobs']):
            raise ValueError('Collect/reconcile outstanding work before explicitly starting a retry cohort')
        if args.resume_batch:
            reconcile_batch(client, state, args.resume_batch)
        for job in state['jobs']:
            if not job.get('ended'):
                if job['mode'] != 'batch':
                    if all('outcome' in item for item in job['items'].values()):
                        job['ended'] = True
                        save(state)
                        continue
                    raise ValueError('Unresolved realtime request; manual reconciliation required')
                if not retrieve(client, state, job, sources, schema, done, wait=not args.collect_only):
                    return 2
                if not args.collect_only and all(i['outcome']['status'] == 'errored' for i in job['items'].values()):
                    print('Every request in recovered batch errored; inspect before submitting more.', flush=True)
                    return 1
        if args.collect_only:
            spent, reserved = totals(state)
            print(compact({'collection_complete': True, 'accepted': len(set(selected) & done),
                           'selected': len(selected), 'spent_usd': str(spent),
                           'reserved_usd': str(reserved)}))
            return 0
        # Harvesting is read-only and remains possible even after an overrun or
        # a lowered cap. Neither condition can authorize further generation.
        phase_available(state, args.budget_usd, args.phase)
        if args.phase == 'pilot200' and not pilot20_gate(latest_records(sources), cohorts['pilot20'])['passed']:
            raise ValueError('pilot200 blocked: pilot20 has fewer than 14 qualifying records out of 20')
        mode = 'smoke' if args.no_batch else 'batch'
        cohort = {rid for job in state['jobs'] if job['mode'] == mode for rid in job['items']}
        if len(cohort | set(selected)) > (10 if args.no_batch else 400):
            raise ValueError('Lifetime pilot/smoke report cap would be exceeded')
        attempted = {rid for job in state['jobs'] if job.get('schema_version') == '0.4.0' for rid in job['items']}
        if args.retry_failed and (set(selected) - attempted or set(selected) & done):
            raise ValueError('--retry-failed ids must have failed prior attempts and no accepted record')
        pending = list(selected) if args.retry_cohort else [rid for rid in selected if rid not in done and (args.retry_failed or rid not in attempted)]
        smoke_attempts = sum(len(j['items']) for j in state['jobs'] if j['mode'] == 'smoke')
        if args.no_batch and smoke_attempts + len(pending) > 10:
            raise ValueError('Lifetime realtime request cap would be exceeded')
        while pending:
            spent, reserved = totals(state)
            available = phase_available(state, args.budget_usd, args.phase)
            items, requests = {}, []
            local_id = mode + '-' + uuid.uuid4().hex
            for rid in pending[:1] if args.no_batch else pending:
                params = parameters(rid, sources[rid], schema, system, args.text_json)
                count_params = {k: v for k, v in params.items() if k != 'max_tokens'}
                counted = client.messages.count_tokens(**count_params).input_tokens
                # Byte fallback plus protocol margin avoids relying on approximate
                # token counts as a strict upper bound. Entire source is retained.
                input_bound = max(counted, len(compact(count_params).encode('utf-8'))) + 4096
                incoming, outgoing, _ = RATES[mode]
                reserve = (input_bound * incoming * Decimal('1.25') + MAX_TOKENS * outgoing) / 1_000_000
                if reserve > available:
                    break
                items[rid] = {'reserve': str(reserve), 'counted_input': counted,
                              'input_bound': input_bound, 'custom_id': local_id + '-' + rid}
                requests.append(Request(custom_id=items[rid]['custom_id'], params=MessageCreateParamsNonStreaming(**params)))
                available -= reserve
            if not items:
                print(compact({'stopped': 'budget reservation does not fit', 'remaining': len(pending),
                               'spent_usd': str(spent), 'reserved_usd': str(reserved)}))
                return 2
            job = {'local_id': local_id, 'mode': mode, 'items': items, 'ended': False,
                   'phase': args.phase, 'schema_version': '0.4.0',
                   'transport': 'text_json' if args.text_json else 'json_schema'}
            state['jobs'].append(job)
            save(state)  # Durable reservation BEFORE any possibly billable call.
            if args.no_batch:
                from types import SimpleNamespace
                rid = next(iter(items))
                message = submit_once(client, state, job, requests)
                accept_result(state, job, rid, SimpleNamespace(type='succeeded', message=message), sources, schema, done)
                job['ended'] = True
                save(state)
            else:
                batch = submit_once(client, state, job, requests)
                job['batch_id'] = batch.id
                save(state)
                print('Submitted batch ' + batch.id, flush=True)
                retrieve(client, state, job, sources, schema, done)
                if all(i['outcome']['status'] == 'errored' for i in job['items'].values()):
                    print('Every request in batch errored; inspect before submitting more.', flush=True)
                    return 1
            # Failures are not automatically retried within an invocation.
            pending = [rid for rid in pending if rid not in items]
        phase_available(state, args.budget_usd, args.phase)
        spent, reserved = totals(state)
        attempted = {rid for job in state['jobs'] for rid in job['items']}
        failed_attempts = sorted({rid for j in state['jobs']
            if j['local_id'] not in initial_jobs or j['local_id'] in recovered_jobs
            for rid, item in j['items'].items()
            if rid in selected and item.get('outcome', {}).get('status') != 'accepted'})
        print(compact({'accepted': len(set(selected) & done), 'selected': len(selected),
                       'failed_attempt_ids': failed_attempts,
                       'failed_ids': sorted((set(selected) & attempted) - done),
                       'spent_usd': str(spent), 'reserved_usd': str(reserved)}))
        return 0 if set(selected) <= done and not failed_attempts else 1


if __name__ == '__main__':
    import anthropic
    try:
        sys.exit(main())
    except anthropic.RateLimitError as error:
        print('Rate limited; checkpoint retained. Request id: ' + str(error.request_id), file=sys.stderr)
        sys.exit(2)
    except anthropic.APIStatusError as error:
        print(f'API status {error.status_code}; checkpoint retained. Request id: {error.request_id}', file=sys.stderr)
        sys.exit(2)
    except anthropic.APIConnectionError:
        print('API connection failed; unresolved submissions remain reserved.', file=sys.stderr)
        sys.exit(2)
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
