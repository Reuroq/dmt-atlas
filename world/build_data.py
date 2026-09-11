"""Rebuild the browser evidence bundle; reads research, writes only world/."""
import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


atlas = read('data/atlas.json')
summary = read('data/corpus/summary.json')
transitions = read('data/corpus/transitions.json')
saturation = read('data/corpus/saturation.json')
discovery = read('data/corpus/discovery.json')
depictions = read('data/corpus/depictions.json')
reports = [json.loads(line) for line in (ROOT / 'data/corpus/reports.jsonl').read_text(encoding='utf-8').splitlines()]
nodes = []
for kind, field in [('realm', 'realms'), ('geometry', 'geometries'), ('entity', 'entities'), ('motif', 'motifs'), ('phase', 'phases'), ('theme', 'themes')]:
    for node in atlas[field]:
        nodes.append(dict(node, kind=kind, key=kind + '|' + node['name']))
node_map = {n['key']: n for n in nodes}
counts = {n['kind'] + '|' + n['name']: n['reports'] for n in summary['per_node']}
report_index = collections.defaultdict(list)
compact_reports = {}
for report in reports:
    keys = ['|'.join(node) for node in report['seq']]
    compact_reports[report['id']] = {'sub': report['sub'], 'date': report['created_utc'], 'seq': keys}
    for key in set(keys):
        report_index[key].append(report['id'])
for node in nodes:
    key = node['key']
    node['report_count'] = counts.get(key)
    node['report_ids'] = report_index.get(key, [])
    node['depiction_ids'] = depictions['per_node'].get(key, [])
# A compact credited index, not downloaded community imagery.
used_depictions = {i for n in nodes for i in n['depiction_ids']}
art = {i: {k: depictions['items'][i].get(k) for k in ['title', 'author', 'permalink', 'kind', 'score']} for i in sorted(used_depictions)}
bundle = {
    'meta': atlas['meta'], 'nodes': nodes, 'sources': atlas['sources'],
    'n_reports': summary['reports'],
    'transitions': transitions['transitions'], 'cooccurrence': transitions['cooccurrence'],
    'saturation': saturation, 'discovery': discovery,
    'depiction_total': depictions['candidates'],
    # Retain only relevant, non-procedural phenomenological study context.
    'study_context': [x for x in atlas['data_points'] if x['source_key'] in ['davis2020', 'lawrence2022', 'lyke2019'] and not any(w in json.dumps(x).lower() for w in ['dose', 'mg', 'synthesis'])],
}
(HERE / 'data.js').write_text('window.WORLD_DATA=' + json.dumps(bundle, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
# reports + depictions are read ONLY by dossier(), i.e. only once a reader opens the
# evidence drawer, and they were 69% of the bundle every visitor downloaded up front.
# They ship separately and trip.js fetches this on idle, so first render does not wait.
trail = {'reports': compact_reports, 'depictions': art}
(HERE / 'data-reports.js').write_text('window.WORLD_REPORTS=' + json.dumps(trail, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
files = ['data/atlas.json', 'data/corpus/summary.json', 'data/corpus/transitions.json', 'data/corpus/saturation.json', 'data/corpus/discovery.json', 'data/corpus/depictions.json', 'data/corpus/reports.jsonl', 'BUILD.md']
manifest = {'inputs': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}, 'nodes': len(nodes), 'reports': len(reports), 'credited_depictions': len(art)}
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'Built {len(nodes)} cited nodes, {len(reports)} report records, {len(art)} credited depiction links.')
