"""Record the actual once-only Linux image inspections; never infer grades from GLSL."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def receipt(name, inspection):
    path = HERE / (name + '.png')
    return {'file': path.name, 'sha256': digest(path),
            'receipt_sha256': digest(path.with_suffix('.json')),
            'inspection': 'view_image, inspected once: ' + inspection}

reason = ('CLOSE, not RECOGNISE: continuous saturated magenta/violet, orange, green and cyan '
          'folds have curled lips, cupped recesses and overlapping depth. Smaller folds now '
          'change the silhouette and highlights. Broad outer surfaces still dominate, however; '
          'fine detail often reads as decorative contouring, the centre is a repeated small '
          'rosette, and thin dark edge defects remain. This is not yet dense, convincingly '
          'recursive unfolding geometry. No witness validation is claimed.')
temporal = ('Entry pair: the right violet lip changes its arc and overlap, the upper green '
            'fold shifts toward yellow, and the orange left recess changes curvature. Walked-in '
            'pair: the right orange cup opens and the overlying violet lip changes thickness '
            'while inner green/cyan folds bend. Actual geometry and colour evolve, not just '
            'texture. Motion is modest, with no demonstrated complete doorway transformation '
            'or clearly sustained whole-field rotation.')
entry_inspection = ('Filled flower-like centre, pointed overlapping green/cyan inner folds, '
                    'glossy orange recesses and broad pink/violet outer sheets. Cupped lips '
                    'are readable; contour-like fine detail and dark edge defects persist.')
walk_inspection = ('Real forward-walk viewpoint: nearer rims expand relative to the centre '
                   'and expose cupped orange/green recesses and layered occlusion. Much of '
                   'the outer area remains a broad sheet; approach does not reveal an '
                   'unbounded hierarchy of new solid forms.')

ledger = read('realism-grades.json')
iterations = {h.get('iteration') for h in ledger.get('history', [])}
assert 'cupped-folds-v14' not in iterations, 'Manual review already recorded'
single_reviews = [
    (10, 'GAME', 'Rainbow pointed bands fill the view, but fine folds read mainly as '
     'surface scribbles on broad, weakly modelled sheets. No convincing recursive depth.'),
    (11, 'CLOSE', reason),
    (12, 'CLOSE', reason),
]
for version, grade, observation in single_reviews:
    review = {'grade': grade, 'reason': observation,
              'temporal_observation': 'Not assessed: the second screenshot timed out after 90 seconds. '
              'One inspected still cannot satisfy the temporal gate.',
              'captures': [receipt(f'realism-chrysanthemum-v{version}', observation)]}
    ledger['history'].append({'target': 'chrysanthemum',
                              'iteration': f'cupped-folds-v{version}-incomplete-pair', 'review': review})
v13 = {'grade': 'CLOSE', 'reason': reason,
       'temporal_observation': 'Same-camera pair: right violet lip flattens and extends, orange '
       'left recess changes its curvature, and the upper green area shifts toward yellow. '
       'Folding is visible but modest; the small central rosette and broad outer areas remain.',
       'captures': [receipt('realism-chrysanthemum-v13' + suffix, entry_inspection)
                    for suffix in ('', '-motion')]}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': 'cupped-folds-v13', 'review': v13})
captures = [receipt('realism-chrysanthemum-v14' + suffix, entry_inspection + ' ' + temporal)
            for suffix in ('', '-motion')]
captures += [receipt('realism-chrysanthemum-walk-v14' + suffix, walk_inspection + ' ' + temporal)
             for suffix in ('', '-motion')]
current = {'grade': 'CLOSE', 'reason': reason, 'temporal_observation': temporal, 'captures': captures}
ledger['targets']['chrysanthemum'] = current
ledger['history'].append({'target': 'chrysanthemum', 'iteration': 'cupped-folds-v14',
                          'review': copy.deepcopy(current)})
write('realism-grades.json', ledger)

observations = {
    'flower / mandala': ('PRESENT', 'Overlapping petal-like rings surround a filled radial flower centre.'),
    'geometry / patterns': ('PRESENT', 'Curving scalloped rims and subordinate cupped forms fill the field.'),
    'multicoloured': ('PRESENT', 'Magenta, violet, orange, yellow-green and cyan/blue coexist and shift.'),
    'fractals': ('PARTIAL', 'Nested rosettes and smaller cups suggest self-similarity, but approach '
                'still reveals broad sheets and decorative contours rather than rich recursive solid forms.'),
    'tunnel / corridor': ('PARTIAL', 'Layered recession and enlargement under real forward walking '
                         'establish depth; a small closed rosette still dominates the destination '
                         'instead of a convincingly endless transforming corridor.'),
    'spinning / rotating': ('PARTIAL', 'Rim angles and overlaps shift, but sustained rotation of '
                           'the whole pattern is not clearly demonstrated by these pairs.'),
    'bright / luminous': ('PRESENT', 'Bright continuous pink/orange/green surfaces and luminous '
                         'highlights remain readable through the recesses.'),
    'morphing / transforming': ('PARTIAL', 'Cups change their curvature and opening, but the '
                               'same flower-sheet topology persists; no major form or doorway transformation.'),
    'dark / black': ('ABSENT', 'Saturated surfaces fill the view. There is no intentional readable '
                     'black negative space; thin dark edge artifacts are not credited as this descriptor.'),
    'green': ('PRESENT', 'Several broad inner folds are distinctly green or yellow-green.'),
    'purple / pink': ('PRESENT', 'Pink and violet outer sheets and inner rims are prominent.'),
    'saturated / vivid': ('PRESENT', 'Strong magenta, violet, orange and green remain saturated '
                         'across large areas rather than a pale white wash.'),
    'beings / presences': ('ABSENT', 'No readable being, face or embodied presence in these views.'),
    'breathing / undulating': ('PARTIAL', 'Cupped lips flex between frames; a sustained cyclic '
                               'whole-field breathing sequence is not demonstrated.'),
    'folding / unfolding': ('PRESENT', 'Right-side curled lips and left orange recesses visibly '
                            'change bend and overlap in both stationary and walked-in temporal pairs.'),
}
temporal_names = {'spinning / rotating', 'morphing / transforming',
                  'breathing / undulating', 'folding / unfolding'}
coverage_captures = []
for capture in captures:
    r = read(Path(capture['file']).with_suffix('.json').name)
    d = r['capture_diagnostics']
    assert not d['renderPending'] and d['renderedAnimTime'] == d['animTime']
    assert r['render_signature'] == render_signature()
    coverage_captures.append({**capture, 'detail': d['detail'],
                             'animTime': d['animTime'], 'render_signature': r['render_signature']})
grades = read('fidelity-grades.json')
before = copy.deepcopy(grades['targets'].get('chrysanthemum'))
coverage_review = {'close_up': False, 'captures': coverage_captures,
                  'descriptors': {name: {'grade': grade, 'observation': observation,
                                  **({'temporal_observation': temporal} if name in temporal_names else {})}
                                  for name, (grade, observation) in observations.items()}}
grades['targets']['chrysanthemum'] = coverage_review
grades['history'].append({'target': 'chrysanthemum', 'iteration': 'cupped-folds-v14',
                         'before': before, 'after': copy.deepcopy(coverage_review),
                         'remaining': 'Black negative space absent; limited recursion, corridor '
                         'recession and transformation; no beings. Realism remains CLOSE.'})
write('fidelity-grades.json', grades)
(HERE / 'continuum-v14.js').write_bytes((HERE / 'continuum.js').read_bytes())
(HERE / 'trip-v14.js').write_bytes((HERE / 'trip.js').read_bytes())
print('Recorded inspected v10-v14 history and v14 top-15 coverage; no automatic passing grades.')
