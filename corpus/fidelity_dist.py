#!/usr/bin/env python3
"""Offline rendered-feature audit; see BLIND_TEST.md for grades and inference limits."""
import argparse
import json
import math
from pathlib import Path
import re
from statistics import NormalDist
import struct
import sys

ROOT = Path(__file__).resolve().parent
DESCRIPTORS = ('light', 'colour', 'motion', 'geometry', 'material', 'density',
               'scale', 'sound_seen', 'affect')
DEFAULT_FIELDS = ('light', 'colour', 'geometry', 'material', 'density', 'scale',
                  'being_presence')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f'Non-finite JSON constant: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=unique, parse_constant=invalid)


def measure(value, label):
    require(isinstance(value, dict), f'{label}: expected evidence object')
    n, ids = value['n'], value['report_ids']
    require(type(n) is int and n >= 0, f'{label}: invalid n')
    require(isinstance(ids, list) and all(isinstance(i, str) and i for i in ids),
            f'{label}: invalid report IDs')
    require(ids == sorted(set(ids)) and len(ids) <= n and bool(ids) == bool(n),
            f'{label}: inconsistent report IDs')
    return n


def targets(distribution, schema, fields):
    require(distribution['format_version'] == '2.0.0', 'Expected aggregate format 2.0.0')
    require(isinstance(distribution['status'], str) and distribution['status'], 'Invalid dataset status')
    require(isinstance(distribution['realms'], dict) and distribution['realms'],
            'Missing realms')
    global_data = distribution['global']
    counts = {k: measure(global_data[k], k) for k in ('retained_records', 'trip_reports', 'scenes')}
    require(counts['trip_reports'] <= counts['retained_records'] and
            set(global_data['trip_reports']['report_ids']) <= set(global_data['retained_records']['report_ids'])
            and set(global_data['scenes']['report_ids']) <= set(global_data['trip_reports']['report_ids']),
            'Inconsistent global source evidence')
    require(all(len(global_data[k]['report_ids']) == counts[k]
                for k in ('retained_records', 'trip_reports')), 'Report counts must count unique reports')
    props = schema['$defs']['scene']['properties']
    vocabulary = {f: props[f]['items']['enum'] for f in fields if f in DESCRIPTORS}
    result = {}
    scene_total, scene_ids = 0, set()
    for realm, strata in distribution['realms'].items():
        require(isinstance(realm, str) and realm, 'Invalid realm key')
        for qualification in ('unqualified', 'flagged'):
            scene_total += measure(strata[qualification]['scenes'], f'{realm}/{qualification}')
            scene_ids.update(strata[qualification]['scenes']['report_ids'])
        if realm == '__unknown__':
            continue
        s = strata['unqualified']
        n = measure(s['scenes'], realm)
        features = {}
        for field in fields:
            if field == 'being_presence':
                h = s['being_presence']['coded_present']
                entries = [('being_presence', h, h['denominator'])]
            else:
                h = s['descriptors'][field]
                require(set(h['values']) == set(vocabulary[field]),
                        f'{realm}/{field}: vocabulary mismatch')
                entries = [(f'{field}/{v}', h['values'][v]['unqualified'], h['denominator'])
                           for v in vocabulary[field]]
            for key, numerator, denominator in entries:
                require(measure(denominator, key) == n and
                        denominator['report_ids'] == s['scenes']['report_ids'],
                        f'{realm}/{key}: denominator differs from scene stratum')
                count = measure(numerator, key)
                require(count <= n and set(numerator['report_ids']) <= set(denominator['report_ids']),
                        f'{realm}/{key}: invalid numerator')
                p = numerator['frequency']
                require((n == 0 and p is None) or (n > 0 and type(p) in (int, float)
                        and math.isfinite(p) and 0 <= p <= 1
                        and math.isclose(p, count / n, rel_tol=0, abs_tol=1e-12)),
                        f'{realm}/{key}: invalid frequency')
                # Counts are authoritative, including exact zero/one boundaries.
                features[key] = {'expected': count / n if n else None,
                                 'source_n': n, 'source_count': count,
                                 'report_ids': numerator['report_ids'],
                                 'denominator_report_ids': denominator['report_ids']}
        result[realm] = features
    require(scene_total == counts['scenes'] and scene_ids == set(global_data['scenes']['report_ids']),
            'Realm strata do not partition global scene evidence')
    return result


def frame_inventory(frames_dir, expected):
    directory = Path(frames_dir)
    require(directory.is_dir(), 'Frames path must be a directory')
    inventory = {}
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() != '.png':
            continue
        match = re.fullmatch(r'(.+)-(0|[1-9][0-9]*)\.png', path.name)
        require(match is not None and match[1] in expected,
                f'Unknown realm or invalid frame name: {path.name}')
        require(path.is_file(), f'Not a frame file: {path.name}')
        with path.open('rb') as stream:
            header = stream.read(24)
        require(len(header) == 24 and header[:8] == b'\x89PNG\r\n\x1a\n'
                and header[8:16] == b'\x00\x00\x00\rIHDR'
                and all(struct.unpack('>II', header[16:24])),
                f'Invalid PNG header: {path.name}')
        inventory[path.name] = match[1]
    return inventory


def write_json(path, data):
    output = Path(path).resolve()
    require(output.is_relative_to(ROOT), 'Output must stay under corpus/')
    require(not output.exists(), 'Output already exists; choose a new path')
    serialized = json.dumps(data, indent=2, allow_nan=False) + '\n'
    with output.open('x', encoding='utf-8') as stream:
        stream.write(serialized)


def load_grades(frames_dir, grades_path, expected):
    inventory = frame_inventory(frames_dir, expected)
    data = read_json(grades_path)
    require(isinstance(data, dict) and set(data) == {'format_version', 'frames'}
            and data['format_version'] == '1.0.0' and isinstance(data['frames'], list),
            'Expected grades format 1.0.0 with frames list')
    grouped = {realm: [] for realm in expected}
    seen = set()
    for row in data['frames']:
        require(isinstance(row, dict) and set(row) == {'frame', 'features'},
                'Each grade must contain only frame and features')
        name = row['frame']
        require(isinstance(name, str) and name in inventory and name not in seen,
                'Grade names must match unique inventory frames')
        seen.add(name)
        realm = inventory[name]
        features = row['features']
        require(isinstance(features, dict) and set(features) == set(expected[realm]),
                f'{name}: supply exactly every selected feature key')
        require(all(v is None or type(v) is bool for v in features.values()),
                f'{name}: grades must be true, false, or null')
        grouped[realm].append(features)
    require(seen == set(inventory), 'Every PNG must have exactly one grade')
    return grouped, len(inventory)


def wilson(successes, n, critical):
    p = successes / n
    z2 = critical ** 2
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    radius = critical * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return [max(0.0, center - radius), min(1.0, center + radius)]


def evaluate(expected, grouped, tolerance, alpha, min_frames):
    rows = []
    for realm, features in expected.items():
        frames = grouped[realm]
        for key, target in features.items():
            known = [f[key] for f in frames if f[key] is not None]
            row = {'realm': realm, 'feature': key, **target, 'frames': len(frames),
                   'graded_n': len(known), 'ungradable_n': len(frames) - len(known),
                   'successes': sum(known), 'status': 'unavailable'}
            if target['expected'] is None:
                row['reason'] = 'no_scene_evidence'
            elif not known:
                row['reason'] = 'no_frames' if not frames else 'no_gradable_frames'
            else:
                p, n, x = target['expected'], len(known), sum(known)
                observed = x / n
                row.update(observed=observed, difference=observed - p)
                if p in (0, 1):
                    # The null is degenerate; no finite z exists on disagreement.
                    row.update(z=None, p_value=1.0 if observed == p else 0.0,
                               test='degenerate_binomial_null', z_reliable=False)
                else:
                    z = (observed - p) / math.sqrt(p * (1 - p) / n)
                    row.update(z=z, p_value=math.erfc(abs(z) / math.sqrt(2)),
                               test='one_sample_proportion_z',
                               z_reliable=n * p >= 5 and n * (1 - p) >= 5)
                row['status'] = 'inconclusive'
            rows.append(row)
    tested = [r for r in rows if 'p_value' in r]
    # The registered family includes unavailable features, conceptually assigned p=1.
    # Missing grades must never narrow the remaining intervals or weaken correction.
    m = len(rows)
    if tested:
        # Bonferroni Wilson intervals; Holm correction for the diagnostic z tests.
        critical = -NormalDist().inv_cdf(alpha / (2 * m))
        running = 0.0
        for rank, row in enumerate(sorted(tested, key=lambda r: r['p_value'])):
            running = max(running, min(1.0, (m - rank) * row['p_value']))
            row['p_holm'] = running
            row['ci'] = wilson(row['successes'], row['graded_n'], critical)
            row['statistical_difference'] = (row['z_reliable'] or
                row['test'] == 'degenerate_binomial_null') and running < alpha
            lo, hi = row['ci']
            p = row['expected']
            adequate = row['graded_n'] >= min_frames and row['ungradable_n'] == 0
            if adequate and (hi < p - tolerance or lo > p + tolerance):
                row['status'] = 'fail'
            elif adequate and lo >= max(0, p - tolerance) and hi <= min(1, p + tolerance):
                row['status'] = 'pass'
            else:
                row['reason'] = ('incomplete_grades' if row['ungradable_n'] else
                                 'too_few_frames' if row['graded_n'] < min_frames else
                                 'interval_overlaps_tolerance_boundary')
    return rows


def run(args):
    require(math.isfinite(args.tolerance) and 0 < args.tolerance < 1, 'Tolerance must be in (0,1)')
    require(math.isfinite(args.alpha) and 0 < args.alpha < 1, 'Alpha must be in (0,1)')
    require(args.min_frames > 0, 'Minimum frames must be positive')
    fields = args.fields.split(',')
    require(len(fields) == len(set(fields)) and fields and
            set(fields) <= set(DESCRIPTORS + ('being_presence',)), 'Invalid or duplicate fields')
    if args.grade_template is not None:
        require(bool(args.frames) and args.grades is None and args.output is None,
                '--grade-template requires --frames and forbids --grades/--output')
    else:
        require(bool(args.frames) == bool(args.grades), 'Supply --frames and --grades together')
    d = read_json(args.distributions)
    expected = targets(d, read_json(args.schema), fields)
    if args.realms is not None:
        realms = args.realms.split(',')
        require(len(realms) == len(set(realms)) and set(realms) <= set(expected),
                'Invalid or duplicate realms')
        expected = {r: expected[r] for r in realms}
    available_features = set(next(iter(expected.values()), {}))
    selected_features = available_features
    if args.features is not None:
        requested = args.features.split(',')
        require(len(requested) == len(set(requested)) and set(requested) <= available_features,
                'Invalid or duplicate features (keys must belong to selected --fields)')
        selected_features = set(requested)
        expected = {realm: {key: target for key, target in features.items() if key in selected_features}
                    for realm, features in expected.items()}
    if args.grade_template is not None:
        inventory = frame_inventory(args.frames, expected)
        require(bool(inventory), 'Cannot prepare a grade template for an empty frame directory')
        write_json(args.grade_template, {'format_version': '1.0.0', 'frames': [
            {'frame': name, 'features': {key: None for key in expected[realm]}}
            for name, realm in inventory.items()]})
        print(json.dumps({'status': 'grade_template_written', 'evaluated': False,
                          'frames': len(inventory), 'features_per_frame': len(selected_features),
                          'dataset_status': d['status']}, indent=2))
        return 2  # Prepared input is never a fidelity pass.
    grouped, frame_n = (load_grades(args.frames, args.grades, expected) if args.frames
                        else ({r: [] for r in expected}, 0))
    rows = evaluate(expected, grouped, args.tolerance, args.alpha, args.min_frames)
    counts = {s: sum(r['status'] == s for r in rows)
              for s in ('pass', 'fail', 'inconclusive', 'unavailable')}
    source_available = any(r['source_n'] for r in rows)
    status = ('no_evidence' if not source_available else 'not_evaluated' if not args.frames
              else 'fail' if counts['fail'] else 'inconclusive' if
              counts['inconclusive'] or counts['unavailable'] else 'pass')
    tested = [r for r in rows if 'p_value' in r]
    worst = sorted(tested, key=lambda r: (r['p_value'], -abs(r['difference']),
                                          r['realm'], r['feature']))[:10]
    compact_keys = ('realm', 'feature', 'status', 'expected', 'observed', 'difference',
                    'source_n', 'graded_n', 'ungradable_n', 'z', 'z_reliable', 'test',
                    'p_value', 'p_holm', 'ci', 'reason')
    summary = {'status': status, 'dataset_status': d['status'],
               'source_counts': {k: d['global'][k]['n'] for k in
                                 ('retained_records', 'trip_reports', 'scenes')},
               'scope': 'fixed_empirical_coded_scene_targets_not_population_fidelity',
               'fields': fields, 'realms': list(expected), 'frames': frame_n,
               'selected_features': sorted(selected_features),
               'excluded_features': sorted(available_features - selected_features),
               'tolerance': args.tolerance, 'alpha': args.alpha,
               'min_frames': args.min_frames, 'counts': counts,
               'family_size': len(rows),
               'unavailable_reasons': {reason: sum(r.get('reason') == reason for r in rows)
                                       for reason in sorted({r['reason'] for r in rows
                                                              if r['status'] == 'unavailable'})},
               'tested_features': len(tested),
               'worst_10': [{k: r[k] for k in compact_keys if k in r} for r in worst]}
    if args.output:
        write_json(args.output, {**summary, 'features': rows})
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0 if status == 'pass' else 1 if status == 'fail' else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distributions', default=ROOT / 'distributions.json')
    parser.add_argument('--schema', default=ROOT / 'schema.json')
    parser.add_argument('--frames', help='Directory of <realm>-<k>.png; omit with grades for evidence inventory')
    parser.add_argument('--grades', help='Blind grades JSON, format 1.0.0')
    parser.add_argument('--grade-template', help='Write a new all-null grades JSON for --frames; no evaluation')
    parser.add_argument('--fields', default=','.join(DEFAULT_FIELDS))
    parser.add_argument('--features', help='Comma-separated preregistered feature keys within --fields; default all')
    parser.add_argument('--realms', help='Comma-separated preregistered realm subset; default all known realms')
    parser.add_argument('--tolerance', type=float, default=.03)
    parser.add_argument('--alpha', type=float, default=.05)
    parser.add_argument('--min-frames', type=int, default=1000)
    parser.add_argument('--output', help='New JSON result file under corpus/, includes all feature evidence')
    args = parser.parse_args()
    try:
        return run(args)
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
