"""One-shot record of four actual v16 view_image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'nested-hollow-chambers-v16'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = ('Pink/violet outer folds, orange/yellow middle folds and green/cyan inner '
         'folds converge on a small blue/magenta flower. Small oval cavities and '
         'rolled mouths appear within larger lobes, especially at upper centre and '
         'right. Broad black openings remain at upper left and behind the right '
         'layers. Pointed wedge-like panels, stretched cavities, contour-like '
         'highlights and stippled edges dominate over readable nested solids.')
close = ('Real forward walking to z=-8.74656 enlarges green/yellow folds and changes '
         'their overlap with the cyan/violet centre. Small round mouths and recessed '
         'ovals become visible on the upper green and right orange surfaces, but '
         'they are still stretched into broad panels. Black distance persists at '
         'upper right; other holes expose blue/violet folds. The central rosette '
         'remains small and repeated; approach does not reveal convincing recursive '
         'chambers. Rough dark silhouette edges remain.')
temporal = ('Entry: the left orange tongue moves downward, right violet lobes change '
            'overlap and cavity outlines shift; the upper-left black opening changes '
            'shape. At the fixed walked-in pose, the right orange fold curls into a '
            'larger visible oval mouth beneath a pink lip and the left green tongue '
            'changes its bend. These demonstrate local folding/deformation, not '
            'sustained whole-field rotation, a full breathing cycle or transformation '
            'into a new spatial structure.')
reason = ('CLOSE, not RECOGNISE: saturated self-lit folds, layered overlap and broad '
          'black openings remain. Small hollow mouths and recessed cavities now '
          'appear inside some larger lobes, but broad pointed decorative panels '
          'still dominate. Their cavities are visibly stretched, the small repeated '
          'centre persists and contour-like highlights/stippled rims remain. '
          'Approach does not demonstrate convincing recursively nested solids. '
          'This construction needs rebuilding, not another noise/colour adjustment. '
          'No witness validation is claimed.')
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v16', entry),
                            ('realism-chrysanthemum-close-v16', close)]:
    pair = []
    for suffix in ['', '-motion']:
        path = HERE / (prefix + suffix + '.png')
        r = read(path.with_suffix('.json').name)
        d = r['capture_diagnostics']
        assert r['render_signature'] == signature
        assert d['detail'] == 'high' and not d['renderPending']
        assert d['renderedAnimTime'] == d['animTime']
        assert not d['missingEvidence'] and d['uncitedMeshes'] == 0
        pair.append(d)
        capture = {'file': path.name, 'sha256': digest(path),
                   'receipt_sha256': digest(path.with_suffix('.json')),
                   'inspection': 'view_image, inspected once: ' + observation}
        captures.append(capture)
        coverage_captures.append({**capture, 'detail': d['detail'],
                                 'animTime': d['animTime'], 'render_signature': signature})
    assert pair[0]['position'] == pair[1]['position']
    assert pair[1]['animTime'] - pair[0]['animTime'] >= 3
current = {'grade': 'CLOSE', 'reason': reason, 'temporal_observation': temporal,
           'captures': captures}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                          'before': copy.deepcopy(ledger['targets']['chrysanthemum']),
                          'review': copy.deepcopy(current)})
ledger['targets']['chrysanthemum'] = current
observations = {
    'flower / mandala': ('PRESENT', 'Overlapping petal-like lobes surround a radial blue/violet/magenta flower centre.'),
    'geometry / patterns': ('PRESENT', 'Repeated curled lobes, oval mouths, recessed cavities and layered radial patterns are visible.'),
    'multicoloured': ('PRESENT', 'Pink, violet, orange, yellow, green, cyan and blue coexist across both viewpoints.'),
    'fractals': ('PARTIAL', 'Small cavities appear within larger lobes, but walking reveals stretched panel details rather than convincing recursively nested solids.'),
    'tunnel / corridor': ('PARTIAL', 'Real walking changes scale and occlusion between layers; a small repeated rosette still closes the centre instead of an endless transforming corridor.'),
    'spinning / rotating': ('PARTIAL', 'Lobe orientations shift locally; sustained whole-field rotation is not demonstrated.'),
    'bright / luminous': ('PRESENT', 'Saturated self-lit coloured surfaces and bright glossy highlights contrast with dark distance.'),
    'morphing / transforming': ('PARTIAL', 'Mouths and lobes change shape, but the overall pointed flower-panel composition persists.'),
    'dark / black': ('PRESENT', 'Broad black openings persist at upper left in the entry pair and upper right after walking. Thin rough edge artifacts are not credited.'),
    'green': ('PRESENT', 'Large green/yellow-green folds and cavity mouths dominate the approached view.'),
    'purple / pink': ('PRESENT', 'Broad pink/violet outer folds and blue/violet/magenta inner layers remain visible.'),
    'saturated / vivid': ('PRESENT', 'Intense pink, violet, orange, green and cyan occupy substantial areas.'),
    'beings / presences': ('ABSENT', 'No readable being, face or embodied presence appears in any of these four inspected frames.'),
    'breathing / undulating': ('PARTIAL', 'Local tongues and lips flex, but these pairs do not demonstrate a sustained whole-field breathing cycle.'),
    'folding / unfolding': ('PRESENT', 'The right orange fold opens into a larger visible mouth beneath a pink lip during the approached pair; left tongues change their bend and overlap.'),
}
motion = {'spinning / rotating', 'morphing / transforming', 'breathing / undulating', 'folding / unfolding'}
review = {'close_up': False, 'captures': coverage_captures,
          'descriptors': {name: {'grade': grade, 'observation': observation,
                          **({'temporal_observation': temporal} if name in motion else {})}
                          for name, (grade, observation) in observations.items()}}
grades['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                         'before': copy.deepcopy(grades['targets']['chrysanthemum']),
                         'after': copy.deepcopy(review), 'remaining': reason})
grades['targets']['chrysanthemum'] = review
write('realism-grades.json', ledger)
write('fidelity-grades.json', grades)
(HERE / 'continuum-v16.js').write_bytes((HERE / 'continuum.js').read_bytes())
print('Recorded four inspected v16 frames and all 15 descriptors; realism remains CLOSE.')
