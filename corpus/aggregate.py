#!/home/clawd/corpus-venv/bin/python
"""Aggregate retained v0.4 JSONL records offline; never calls the API."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

from extract import ROOT, atomic, load_sources, rows
from normalise import decode_record, key, structural_check, vocabulary_maps

DESCRIPTORS = ('light', 'colour', 'motion', 'geometry', 'material', 'density',
               'scale', 'affect')
BEING_FIELDS = ('form', 'behaviour', 'communication', 'affect')
UNKNOWN = '__unknown__'
VERSION = '0.4.0'


def evidence(items):
    """Items are observational units, not necessarily unique reports."""
    items = list(items)
    return {'n': len(items), 'report_ids': sorted({x['report_id'] for x in items})}


def frequency(items, denominator, *, include_denominator=True, denominator_ref=None):
    result = evidence(items)
    if denominator_ref:
        result['denominator_ref'] = denominator_ref
    elif include_denominator:
        result['denominator'] = evidence(denominator)
    result['frequency'] = result['n'] / len(denominator) if denominator else None
    return result


def histogram(items, field, multiple=False, vocabulary_ref=None):
    """Per-unit occurrence: aliases/repeated labels count at most once per unit."""
    buckets = {}
    observed, missing = [], []
    for item in items:
        value = item['data'].get(field)
        if value is None or value == [] or value == '':
            missing.append(item)
            continue
        observed.append(item)
        for v in dict.fromkeys(value if multiple else [value]):
            buckets.setdefault(str(v), []).append(item)
    return {**({'vocabulary_ref': vocabulary_ref} if vocabulary_ref else {}),
            'denominator': evidence(items), 'observed': evidence(observed),
            'missing': evidence(missing),
            'values': {v: frequency(xs, items, include_denominator=False)
                       for v, xs in sorted(buckets.items())}}


def mapping_coverage(items, field, domain, multiple=False):
    """Disjoint per-unit strata; mixed units retain both kinds of descriptors."""
    domain = set(domain)
    groups = {k: [] for k in ('mapped_only', 'unmapped_only', 'mixed', 'missing')}
    for item in items:
        value = item['data'].get(field)
        values = (value if multiple else [value]) if value is not None else []
        values = [v for v in values if v not in ('', UNKNOWN)]
        mapped = any(v in domain for v in values)
        unmapped = any(v not in domain for v in values)
        kind = 'mixed' if mapped and unmapped else 'mapped_only' if mapped else 'unmapped_only' if unmapped else 'missing'
        groups[kind].append(item)
    return {'denominator': evidence(items),
            'values': {k: frequency(xs, items, include_denominator=False) for k, xs in groups.items()}}


def observation(rid, pointer, data):
    return {'report_id': rid, 'pointer': pointer, 'data': data}


def joint_profiles(items):
    """Normalized co-occurring bundles with pointers into unchanged source records."""
    groups = {}
    for item in items:
        data = {k: v for k, v in item['data'].items() if k != 'quotes'}
        signature = json.dumps(data, sort_keys=True, ensure_ascii=False)
        groups.setdefault(signature, {'value': data, 'items': []})['items'].append(item)
    result = []
    for signature in sorted(groups):
        group = groups[signature]
        xs = group.pop('items')
        group.update(evidence(xs))
        group['observations'] = [{'report_id': x['report_id'], 'pointer': x['pointer']} for x in xs]
        result.append(group)
    return result


def select_records(records):
    """Latest v0.4 extraction attempt wins, independent of file name/order."""
    latest, legacy, superseded = {}, [], []
    for record in records:
        structural_check(record)
        if record.get('schema_version') != VERSION:
            legacy.append(record)
            continue
        rid = record['report_id']
        rank = record.get('_extraction', {}).get('attempt', 0)
        old = latest.get(rid)
        if old is not None:
            old_rank = old.get('_extraction', {}).get('attempt', 0)
            if rank == old_rank and record != old:
                raise ValueError('Conflicting records at the same attempt: ' + rid)
            if rank <= old_rank:
                superseded.append(record)
                continue
            superseded.append(old)
        latest[rid] = record
    selected = [latest[rid] for rid in sorted(latest)]
    return selected, {'selected_v04': evidence(selected), 'legacy_excluded': evidence(legacy),
                      'superseded_v04_rows': evidence(superseded),
                      'policy': 'Only structurally accepted v0.4; highest _extraction.attempt per ID. '
                                'Legacy files and superseded attempts remain on disk.'}


def normalized_scenes(record, maps):
    """Use the local normaliser's vocabulary/aliases without re-anchoring quotes.

    Recompute from raw descriptors, not potentially stale stored normalised fields.
    Empty descriptors are missing; unknown nonempty text remains other:<text>.
    """
    def mapped(value, field):
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)
        if not value.strip():
            return None
        if value.startswith('other:'):
            return value if value[6:].strip() else None
        return maps.get(field, {}).get(key(value), 'other:' + value)

    def labels(obj, field):
        raw = obj.get(field, [])
        if not isinstance(raw, list):
            raw = [] if raw is None else [raw]
        return sorted({v for value in raw if (v := mapped(value, field)) is not None})

    result = []
    for i, scene in enumerate(record.get('scenes') or []):
        data = {field: labels(scene, field) for field in (*DESCRIPTORS, 'transition_trigger')}
        data['place'] = mapped(scene.get('place', ''), 'place') or UNKNOWN
        order = scene.get('order')
        data['order'] = order if type(order) is int else None
        data['quotes'] = scene['quotes']  # Preserve every anchor, including weak ones.
        data['beings'] = []
        beings = scene.get('beings', [])
        for being in beings if isinstance(beings, list) else []:
            # Structural acceptance permits malformed descriptors; do not reject scenes.
            obj = being if isinstance(being, dict) else {}
            data['beings'].append({**{f: labels(obj, f) for f in BEING_FIELDS},
                                   'count_text': obj.get('count_text', '')})
        result.append(observation(record['report_id'], f'/scenes/{i}', data))
    return result


def being_observations(scenes):
    return [observation(s['report_id'], s['pointer'] + f'/beings/{i}', b)
            for s in scenes for i, b in enumerate(s['data']['beings'])]


def being_summary(items, maps):
    return {'observations': evidence(items),
            'fields': {f: histogram(items, f, True, f'#/vocabulary_domains/{f}') for f in BEING_FIELDS},
            'joint_profiles': joint_profiles(items)}


def realm_summary(scenes, trips, maps):
    ids = {s['report_id'] for s in scenes}
    return {'scenes': evidence(scenes),
            'coded_report_prevalence': frequency([{'report_id': rid} for rid in ids], trips,
                                                 denominator_ref='#/global/trip_reports'),
            'descriptors': {f: histogram(scenes, f, True, f'#/vocabulary_domains/{f}') for f in DESCRIPTORS},
            'being_presence': {
                'coded_present': frequency([s for s in scenes if s['data']['beings']], scenes),
                'none_coded_not_absence': frequency([s for s in scenes if not s['data']['beings']], scenes)},
            'beings': being_summary(being_observations(scenes), maps),
            'dwell': {'status': 'not_collected_in_v04'},
            'joint_profiles': joint_profiles(scenes)}


def baseline_comparison(vocab, tagged, summary, trips, realms):
    """Reconstruct IDs; summary.json itself contains only counts."""
    names = {x['name']: x['slug'] for x in vocab['catalog']['realm']}
    buckets = {slug: [] for slug in names.values()}
    for row in tagged:
        for slug in {names[name] for kind, name in row['seq'] if kind == 'realm' and name in names}:
            buckets[slug].append({'report_id': row['id']})
    universe = [{'report_id': row['id']} for row in tagged]
    summary_counts = {x['name']: x['reports'] for x in summary['per_node'] if x['kind'] == 'realm'}
    if summary['reports'] != len(universe):
        raise ValueError('summary.json report total differs from tagged universe')
    result = {}
    selected = {r['report_id'] for r in trips}
    for name, slug in names.items():
        if summary_counts.get(name) != len(buckets[slug]):
            raise ValueError('summary.json realm count differs from reconstructed IDs: ' + slug)
        result[slug] = {'name': name, 'summary_count_verified': True,
                        'keyword_prevalence': frequency(buckets[slug], universe,
                                                        denominator_ref='#/baseline_population'),
                        'keyword_prevalence_in_retained_trip_reports': frequency(
                            [r for r in buckets[slug] if r['report_id'] in selected], trips,
                            denominator_ref='#/global/trip_reports'),
                        'coded_report_prevalence': realms[slug]['coded_report_prevalence'],
                        'interpretation': 'Keyword mentions versus normalized scene places; '
                                          'nonrandom pilot, incomplete lexical mapping, no accuracy inference.'}
    return result


def aggregate(records, schema, vocab, tagged, summary):
    records, selection = select_records(records)
    maps = vocabulary_maps(vocab)
    trips = [r for r in records if r['is_trip_report']]
    trip_ids = {r['report_id'] for r in trips}
    nontrips = [r for r in records if not r['is_trip_report']]
    scenes_by_id = {r['report_id']: normalized_scenes(r, maps) for r in records}
    scenes = [s for r in trips for s in scenes_by_id[r['report_id']]]
    nontrip_scenes = [s for r in nontrips for s in scenes_by_id[r['report_id']]]
    realm_groups = {x['slug']: [] for x in vocab['catalog']['realm']}
    realm_groups[UNKNOWN] = []
    for scene in scenes:
        realm_groups.setdefault(scene['data']['place'], []).append(scene)
    realms = {p: realm_summary(xs, trips, maps) for p, xs in sorted(realm_groups.items())}
    beings = being_observations(scenes)
    form_groups = {v: [] for v in maps['form'].values()}
    form_groups[UNKNOWN] = []
    for being in beings:
        for form in being['data']['form'] or [UNKNOWN]:
            form_groups.setdefault(form, []).append(being)
    edges, adjacency, bad_order = defaultdict(list), [], []
    for report in trips:
        report_scenes = scenes_by_id[report['report_id']]
        if [s['data']['order'] for s in report_scenes] != list(range(1, len(report_scenes) + 1)):
            bad_order.append(report)
        for left, right in zip(report_scenes, report_scenes[1:]):
            item = observation(report['report_id'], left['pointer'],
                               {'trigger': left['data']['transition_trigger']})
            item['destination_pointer'] = right['pointer']
            adjacency.append(item)
            edges[(left['data']['place'], right['data']['place'])].append(item)
    transitions = []
    for (source, target), items in sorted(edges.items()):
        transitions.append({'from': source, 'to': target, 'kind': 'consecutive_scene_adjacency',
                            'sampling_eligible': False, **frequency(items, adjacency,
                                denominator_ref='#/global/scene_adjacencies'),
                            'with_trigger': frequency([x for x in items if x['data']['trigger']], items),
                            'trigger': histogram(items, 'trigger', True, '#/vocabulary_domains/trigger'),
                            'abruptness': {'status': 'not_collected_in_v04'},
                            'observations': [{'report_id': x['report_id'],
                                              'source_pointer': x['pointer'],
                                              'trigger_pointer': x['pointer'] + '/transition_trigger',
                                              'destination_pointer': x['destination_pointer']} for x in items],
                            'joint_profiles': joint_profiles(items)})
    counts = defaultdict(list)
    for report in trips:
        counts[len(report.get('scenes') or [])].append(report)
    flag_items = [observation(r['report_id'], '', {'flags': sorted({str(f).split(':')[0]
                  for f in r.get('flags', [])})}) for r in records]
    quotes = [observation(s['report_id'], s['pointer'] + f'/quotes/{i}', q)
              for s in scenes for i, q in enumerate(s['data']['quotes'])]
    anchored, weak, unknown_anchor = [], [], []
    for q in quotes:
        data = q['data']
        score = data.get('anchor_score') if isinstance(data, dict) else None
        if type(score) not in (int, float):
            unknown_anchor.append(q)
        elif score >= 0.85:
            anchored.append(q)
        else:
            weak.append(q)
    return {'format_version': '3.1.0', 'record_schema_version': VERSION,
            'vocabulary_domains': {f: sorted(set(maps[f].values()))
                                   for f in sorted(set((*DESCRIPTORS, *BEING_FIELDS, 'trigger', 'place')))},
            'status': 'descriptive_only' if scenes else 'no_scene_evidence',
            'selection': selection,
            'semantics': {
                'n': 'Observational units; report_ids are unique supporting IDs, not necessarily n.',
                'frequency': 'n / denominator.n; inline denominator, denominator_ref, or enclosing histogram. Null if empty.',
                'normalisation': 'normalise.vocabulary_maps/key; recomputed from raw fields; synonyms collapse per unit; other:<text> retained; blank is missing.',
                'sparse_histograms': 'values contains observed bins only. vocabulary_ref lists canonical values; absent bins have n=0, report_ids=[], frequency=0 if denominator.n>0 else null. Other text remains explicit.',
                'mapping_coverage': 'Disjoint mapped_only/unmapped_only/mixed/missing observational-unit strata; mapped does not mean semantically verified.',
                'flags': 'All flagged records and weak quotes retained. Flags are diagnostics, not semantic rejection or sampling qualifications.',
                'missing': 'Not coded, never evidence of absence. Removed fields are not_collected_in_v04, not zero.',
                'scope': 'Realm/being/adjacency measures use trip-classified scenes. Non-trip scenes, if any, are counted separately and retained in profiles.',
                'transitions': 'Array-neighbor adjacency only; outgoing trigger is on source scene. Episodes/order confidence/abruptness are not collected. No qualified traversal inferred.',
                'beings': 'Entries, not individuals; form grouping is multi-label, not entity identity. Ordinary companions may be included.',
                'pointers': 'Pointers address selected stored records before normalization; selected_records resolves files and attempts.',
                'compatibility': 'Breaking v3 format; existing v2 sampler/fidelity consumers require migration.',
                'validation': 'Structural acceptance only; anchoring does not establish semantic fidelity.'},
            'global': {
                'retained_records': evidence(records), 'trip_reports': evidence(trips),
                'non_reports': evidence(nontrips), 'scene_bearing_reports': evidence([r for r in trips if r.get('scenes')]),
                'scenes': evidence(scenes), 'non_trip_scenes': evidence(nontrip_scenes),
                'non_trip_scene_profiles': joint_profiles(nontrip_scenes),
                'beings': evidence(beings), 'scene_count_per_trip_report': {
                    str(k): frequency(xs, trips, denominator_ref='#/global/trip_reports') for k, xs in sorted(counts.items())},
                'order': histogram(scenes, 'order'), 'reports_with_nonsequential_order': evidence(bad_order),
                'episodes': {'status': 'not_collected_in_v04'},
                'order_confidence': {'status': 'not_collected_in_v04'},
                'scene_adjacencies': evidence(adjacency),
                'adjacencies_with_trigger': frequency([x for x in adjacency if x['data']['trigger']], adjacency),
                'terminal_scenes_with_trigger': evidence([xs[-1] for xs in scenes_by_id.values()
                    if xs and xs[-1]['report_id'] in trip_ids and xs[-1]['data']['transition_trigger']]),
                'descriptors': {f: histogram(scenes, f, True, f'#/vocabulary_domains/{f}') for f in DESCRIPTORS},
                'mapping_coverage': {
                    'place': mapping_coverage(scenes, 'place', maps['place'].values()),
                    'descriptors': {f: mapping_coverage(scenes, f, maps[f].values(), True) for f in DESCRIPTORS},
                    'beings': {f: mapping_coverage(beings, f, maps[f].values(), True) for f in BEING_FIELDS}},
                'records_with_flags': frequency([r for r in records if r.get('flags')], records),
                'flag_prefixes': histogram(flag_items, 'flags', multiple=True),
                'quotes': {'retained': evidence(quotes), 'anchored': frequency(anchored, quotes),
                           'weak': frequency(weak, quotes), 'unknown_anchor': frequency(unknown_anchor, quotes)}},
            'realms': realms, 'beings': {'all': being_summary(beings, maps),
                'by_form': {form: being_summary(xs, maps) for form, xs in sorted(form_groups.items())}},
            'transitions': transitions,
            'baseline_population': evidence([{'report_id': r['id']} for r in tagged]),
            'baseline_comparison': baseline_comparison(vocab, tagged, summary, trips, realms)}


def read_records(directory, sources, schema):
    records, locations = [], {}
    for path in sorted(directory.glob('*.jsonl')):
        with path.open() as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                record = decode_record(line)
                structural_check(record)
                rid = record['report_id']
                if rid not in sources:
                    raise ValueError('Missing canonical source: ' + rid)
                records.append(record)
                locations[id(record)] = {'file': str(path.relative_to(ROOT)), 'line': number,
                                         'attempt': record.get('_extraction', {}).get('attempt', 0),
                                         'job': record.get('_extraction', {}).get('job'),
                                         'flags': record.get('flags', [])}
    selected, _ = select_records(records)
    return records, {r['report_id']: locations[id(r)] for r in selected}


def documentation(result):
    g = result['global']
    n, t, s = (g[k]['n'] for k in ('retained_records', 'trip_reports', 'scenes'))
    unknown = result['realms'][UNKNOWN]['scenes']['n']
    other = sum(row['scenes']['n'] for place, row in result['realms'].items() if place.startswith('other:'))
    lines = ['# Corpus distributions — v0.4 pilot', '',
             'Generated offline by `aggregate.py`; extraction and stored records are unchanged.', '',
             '## Current evidence', '',
             f'**{n} unique v0.4 records; {t} trip-classified; {s} trip scenes.** '
             f"{result['selection']['legacy_excluded']['n']} legacy rows are excluded and retained on disk. "
             f"{result['selection']['superseded_v04_rows']['n']} older/duplicate v0.4 rows were superseded.", '',
             '| Measure | n / denominator |', '| --- | ---: |',
             f'| Trip-classified reports | {t} / {n} reports |',
             f"| Non-reports | {g['non_reports']['n']} / {n} reports |",
             f"| Scene-bearing trip reports | {g['scene_bearing_reports']['n']} / {t} trip reports |",
             f"| Being entries | {g['beings']['n']} across {s} scenes |",
             f"| Flagged reports (retained) | {g['records_with_flags']['n']} / {n} reports |",
             f"| Anchored quotes | {g['quotes']['anchored']['n']} / {g['quotes']['retained']['n']} quotes |",
             f"| Weak quotes (retained) | {g['quotes']['weak']['n']} / {g['quotes']['retained']['n']} quotes |",
             f"| Unknown anchor scores | {g['quotes']['unknown_anchor']['n']} / {g['quotes']['retained']['n']} quotes |",
             f'| Canonical realm-mapped scenes | {s - unknown - other} / {s} scenes |',
             f'| Unmapped nonempty places (`other:*`) | {other} / {s} scenes |',
             f'| Unspecified places | {unknown} / {s} scenes |',
             f"| Consecutive-scene adjacencies | {g['scene_adjacencies']['n']} across {t} trip reports |",
             f"| Adjacencies with an outgoing trigger | {g['adjacencies_with_trigger']['n']} / {g['scene_adjacencies']['n']} adjacencies |",
             f"| Nonsequential order labels | {g['reports_with_nonsequential_order']['n']} / {t} trip reports |", '',
             'Pilot20 passed its numerical gate **16/20**. Its fixed ten-record audit reported '
             'wrong place 0/10, missed scene/stage 2/10, invented detail 1/10, classification error '
             '1/10, redaction miss 1/10, and temporal/qualification concerns 5/10 (overlapping). '
             'The additional 180 were not reading-audited. These are descriptive counts on a '
             'nonrandom pilot, not population prevalence or fidelity certification. See `PILOT2.md`.', '',
             '## Run and evidence contract', '', '```sh',
             '/home/clawd/corpus-venv/bin/python -B aggregate.py', '```', '',
             '- Format **3.1.0** uses sparse histograms and is deliberately incompatible with the old v2 sampler/fidelity '
             'contract; those consumers are not migrated by this aggregate phase.',
             '- Inputs are `records/*.jsonl`, never examples or rejected outputs. Only structurally '
             'accepted v0.4 records enter the selected cohort, highest `_extraction.attempt` per ID. '
             'Conflicting ties fail explicitly. Legacy and superseded files are not modified.',
             '- Every measure in `distributions.json` has `n` and unique sorted supporting `report_ids`. '
             '`frequency` uses an inline denominator, JSON `denominator_ref`, or enclosing histogram '
             'denominator. Empty denominators yield null. Repeated scenes/beings count separately.',
             '- `selected_records` resolves each ID to its file, line, attempt, job and original flags. '
             'Joint-profile and adjacency observations point into these unchanged records. Profiles '
             'contain normalized co-occurring bundles; their weights are `n`, not independent draws.',
             '- The existing local normaliser\'s vocabulary maps and synonym rules are applied anew '
             'to raw descriptors. Nonempty unmapped words remain `other:<text>`; blank is missing. '
             'Repeated labels/aliases count once per observational unit. `values` stores observed '
             'bins only; `vocabulary_ref` points to a shared canonical domain. An absent canonical '
             'bin has `n: 0`, `report_ids: []`, and frequency 0 for a nonempty denominator or null '
             'for an empty denominator. Nonempty `other:*` bins stay explicit. Multi-label '
             'frequencies may sum above one.',
             '- Flags and weak anchors never remove or downgrade evidence. Original flags remain '
             'available per selected record; prefix rates are diagnostic, not error rates. '
             'Neither mapped nor unflagged means reading-verified.',
             '- Realm denominators are scenes in that normalized place, or all trip reports for '
             'report prevalence. Being denominators are entries, not individual counts; grouping '
             'by form is multi-label and does not infer entity identity. Ordinary companions may '
             'be coded as beings. No being coded is not demonstrated absence.',
             '- Scene-count and order measures use trip-classified records. Any non-trip scenes '
             'are counted separately and retained in `global.non_trip_scene_profiles`.',
             '- Transitions are **array-neighbor adjacencies**, with the outgoing trigger on the '
             'source scene. They are not confirmed same-episode transitions. No reordering occurs. '
             'Episode boundaries, dwell, abruptness and order confidence were removed in v0.4; '
             'they are explicitly not collected, never zero/imputed. All links have '
             '`sampling_eligible: false` because the former qualification cannot be established.', '',
             '## Scenes per trip report', '', '| Scenes | n / trip reports |', '| ---: | ---: |']
    for count, row in g['scene_count_per_trip_report'].items():
        lines.append(f"| {count} | {row['n']} / {t} |")
    lines += ['', '## Normalization coverage', '',
              'Each row partitions observational units into mapped-only, unmapped-only, mixed '
              '(both), and missing. All cells are n; the final column is the shared denominator n. '
              'These are lexical mapping rates, not accuracy rates. Unmapped evidence is retained. '
              'JSON supplies each cell\'s report IDs and frequency.', '',
              '| Unit / field | Mapped only n | Unmapped only n | Mixed n | Missing n | Denominator n |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    coverage = g['mapping_coverage']
    coverage_rows = [('scene / place', coverage['place'])]
    coverage_rows += [(f'scene / {f}', h) for f, h in coverage['descriptors'].items()]
    coverage_rows += [(f'being entry / {f}', h) for f, h in coverage['beings'].items()]
    for name, hist in coverage_rows:
        cells = ' | '.join(str(hist['values'][k]['n']) for k in ('mapped_only', 'unmapped_only', 'mixed', 'missing'))
        lines.append(f"| {name} | {cells} | {hist['denominator']['n']} |")
    lines += ['', '## Descriptor coverage', '',
              'Top values are scene occurrence counts, not shares of descriptor mentions. '
              'Full per-realm values, missing counts and evidence IDs are in JSON.', '',
              '| Field | Observed n / scenes | Most frequent values (n) |', '| --- | ---: | --- |']
    def top(hist, limit=5):
        values = sorted(hist['values'].items(), key=lambda pair: (-pair[1]['n'], pair[0]))
        return '; '.join(f"{escape(v)} ({row['n']})" for v, row in values[:limit] if row['n']) or 'None coded'
    for field, hist in g['descriptors'].items():
        lines.append(f"| {field} | {hist['observed']['n']} / {s} | {top(hist)} |")
    lines += ['', '## Being mix', '', '| Field | Observed n / being entries | Most frequent values (n) |',
              '| --- | ---: | --- |']
    for field, hist in result['beings']['all']['fields'].items():
        lines.append(f"| {field} | {hist['observed']['n']} / {g['beings']['n']} | {top(hist)} |")
    lines += ['', '## Most frequent adjacency pairs', '',
              'Top 12; all pairs and supporting source/destination pointers are in JSON. '
              'Counts include missing triggers, self-links and unknown places.', '',
              '| From → to | n / all adjacencies | With trigger n / pair adjacencies |', '| --- | ---: | ---: |']
    for row in sorted(result['transitions'], key=lambda r: (-r['n'], r['from'], r['to']))[:12]:
        lines.append(f"| {escape(row['from'])} → {escape(row['to'])} | {row['n']} / {g['scene_adjacencies']['n']} | {row['with_trigger']['n']} / {row['n']} |")
    lines += ['', '## Keyword baseline comparison', '',
              'Baseline IDs are reconstructed by ID from `reports.jsonl` tags and counts verified '
              'against `summary.json`. The 14,309 tagged reports include twelve missing raw joins. '
              'Keyword mentions are not experienced scene settings. The first-200 nonrandom pilot '
              'also differs from that population; the matched-trip-cohort column separates part '
              'of this selection difference. Conservative lexical mapping leaves free-text places '
              'unmapped rather than forcing realm identity. These differences cannot establish '
              'extraction accuracy. All columns have numerator/denominator IDs in JSON.', '',
              '| Realm | Keyword n / tagged reports | Keyword n / pilot trip reports | Coded n / pilot trip reports | Scenes n |',
              '| --- | ---: | ---: | ---: | ---: |']
    for slug, row in result['baseline_comparison'].items():
        lines.append(f"| {escape(row['name'])} | {row['keyword_prevalence']['n']} / {result['baseline_population']['n']} | {row['keyword_prevalence_in_retained_trip_reports']['n']} / {t} | {row['coded_report_prevalence']['n']} / {t} | {result['realms'][slug]['scenes']['n']} |")
    lines += ['', '## Noncanonical places', '',
              'Exact normalized labels are retained; descriptive phrases are not semantically merged.', '',
              '| Place | Scenes n / all scenes | Reports n / trip reports |', '| --- | ---: | ---: |']
    for place, row in result['realms'].items():
        if place == UNKNOWN or place.startswith('other:'):
            lines.append(f"| {escape(place)} | {row['scenes']['n']} / {s} | {row['coded_report_prevalence']['n']} / {t} |")
    lines += ['', '## Offline capacity check — 2026-09-06', '',
              'Turn 2 verified that sparse storage preserves every prior nonzero measure, '
              'denominator, profile and provenance pointer. The 103,852 canonical zero bins '
              'are reconstructible from shared domains; 13 coverage rows partition their '
              'observational units exactly. Pilot JSON decreased from 8,697,818 to 2,943,046 bytes.', '',
              'A separate in-memory synthetic check aggregated 14,297 distinct report IDs with '
              'one scene, one unique noncanonical place and one unique profile each. Report, '
              'scene, realm and profile totals passed; aggregation took 2.999 seconds on this '
              'machine. Compact serialization was 61,655,498 bytes, excluding the file/line '
              'registry (synthetic inputs had no files). Process peak RSS was 381,368 KiB, '
              'including prior verification work. No synthetic record or distribution was '
              'written to disk or mixed with pilot evidence.', '',
              'This checks report-count capacity and high place diversity, not full-extraction '
              'fidelity or a size bound. Multiple scenes, beings, longer labels and richer '
              'profiles can increase size and memory. No full extraction was run or authorized.']
    return '\n'.join(lines) + '\n'


def escape(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')


def local_path(value):
    path = Path(value).resolve()
    if not path.is_relative_to(ROOT):
        raise argparse.ArgumentTypeError('Path must stay under corpus/')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records-dir', type=local_path, default=str(ROOT / 'records'))
    parser.add_argument('--output', type=local_path, default=str(ROOT / 'distributions.json'))
    parser.add_argument('--documentation', type=local_path, default=str(ROOT / 'DISTRIBUTIONS.md'))
    args = parser.parse_args()
    if not args.records_dir.is_dir():
        parser.error('records directory does not exist')
    protected = {ROOT / 'schema.json', ROOT / 'vocab.json', ROOT / 'extract-state.json'}
    for path in (args.output, args.documentation):
        if path in protected or path.is_relative_to(args.records_dir) or path.suffix not in ('.json', '.md'):
            parser.error('Unsafe output destination')
    if args.output == args.documentation:
        parser.error('Output destinations must differ')
    schema = json.loads((ROOT / 'schema.json').read_text())
    vocab = json.loads((ROOT / 'vocab.json').read_text())
    _, sources = load_sources()
    records, locations = read_records(args.records_dir, sources, schema)
    tagged = list(rows(ROOT.parent / 'data/corpus/reports.jsonl'))
    if len({r['id'] for r in tagged}) != len(tagged):
        raise ValueError('Duplicate baseline report ID')
    summary = json.loads((ROOT.parent / 'data/corpus/summary.json').read_text())
    result = aggregate(records, schema, vocab, tagged, summary)
    result['selected_records'] = locations
    atomic(args.output, json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')
    atomic(args.documentation, documentation(result))
    print(json.dumps({'status': result['status'], 'retained': result['global']['retained_records']['n'],
                      'scenes': result['global']['scenes']['n']}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print('aggregate: ' + str(exc), file=sys.stderr)
        sys.exit(2)
