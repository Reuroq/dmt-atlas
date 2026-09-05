"""One-shot record of four actual v15 view_image inspections, not an image grader."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'perforated-cupped-folds-v15'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = ('Glossy magenta/violet outer lips, orange recesses and green/cyan inner folds '
         'surround a small radial flower. A broad black opening at upper left persists '
         'across the pair, with yellow folded material behind its lower edge. Smaller '
         'openings reveal deeper blue/purple layers. Broad panels and contour-like '
         'highlights remain; some silhouettes are still pointed or stippled.')
close = ('Real forward walking enlarges and changes the occlusion of the green/yellow '
         'folds relative to the violet centre. Broad black gaps are clearly visible at '
         'upper right and the outer margins, distinct from thin rough edge marks. '
         'Curled green cups and orange lips have depth, but approach reveals broad '
         'panels and decorative contouring rather than new levels of recursive solids.')
temporal = ('Entry: the upper-left black opening broadens, the right violet lip bends '
            'and changes overlap, and the left orange recess shifts against green. '
            'At the walked-in fixed pose, the upper-right black opening changes shape '
            'as green/yellow rims move, and the right orange cup opens beneath a red lip. '
            'This demonstrates folding and local deformation, not a complete doorway '
            'transformation, sustained whole-field rotation or a full breathing cycle.')
reason = ('CLOSE, not RECOGNISE: rounded perforations add visible black negative space '
          'and expose deeper coloured folds. Thicker rims retain cupped depth during '
          'approach, but broad glossy sheets, a small repeated radial centre, contour-like '
          'detail and rough pointed rims persist. Rich recursive solid structure and '
          'convincing spatial transformation remain missing. No witness validation is claimed.')
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v15', entry),
                            ('realism-chrysanthemum-close-v15', close)]:
    for suffix in ['', '-motion']:
        path = HERE / (prefix + suffix + '.png')
        r = read(path.with_suffix('.json').name)
        d = r['capture_diagnostics']
        assert r['render_signature'] == signature
        assert d['detail'] == 'high' and not d['renderPending']
        assert d['renderedAnimTime'] == d['animTime']
        capture = {'file': path.name, 'sha256': digest(path),
                   'receipt_sha256': digest(path.with_suffix('.json')),
                   'inspection': 'view_image, inspected once: ' + observation}
        captures.append(capture)
        coverage_captures.append({**capture, 'detail': d['detail'],
                                  'animTime': d['animTime'], 'render_signature': signature})
current = {'grade': 'CLOSE', 'reason': reason, 'temporal_observation': temporal,
           'captures': captures}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                          'before': copy.deepcopy(ledger['targets']['chrysanthemum']),
                          'review': copy.deepcopy(current)})
ledger['targets']['chrysanthemum'] = current
observations = {
    'flower / mandala': ('PRESENT', 'Petal-like overlapping layers surround a radial violet/magenta flower centre.'),
    'geometry / patterns': ('PRESENT', 'Curved scalloped rims, cups and openings repeat through visible layers.'),
    'multicoloured': ('PRESENT', 'Magenta, violet, orange, yellow, green, cyan and blue coexist.'),
    'fractals': ('PARTIAL', 'Nested flower layers suggest self-similarity, but real approach still reveals broad panels and contour-like detail, not rich recursively nested solids.'),
    'tunnel / corridor': ('PARTIAL', 'Forward walking changes relative size and occlusion; a small closed radial centre remains instead of a convincingly endless transforming passage.'),
    'spinning / rotating': ('PARTIAL', 'Rim angles shift, without clearly demonstrated sustained whole-field rotation.'),
    'bright / luminous': ('PRESENT', 'Self-lit saturated surfaces and glossy highlights remain bright beside the black openings.'),
    'morphing / transforming': ('PARTIAL', 'Lips and openings deform locally; the overall flower composition remains stable.'),
    'dark / black': ('PRESENT', 'Broad black negative space appears behind the upper-left entry opening and upper-right walked-in opening, persisting as rims move. Thin stippled edge defects are not credited.'),
    'green': ('PRESENT', 'Large green and yellow-green cupped surfaces dominate the closer view.'),
    'purple / pink': ('PRESENT', 'Magenta/violet outer lips and inner flower layers are prominent.'),
    'saturated / vivid': ('PRESENT', 'Strong pink, violet, orange, green and cyan cover substantial visible surfaces.'),
    'beings / presences': ('ABSENT', 'No readable being, face or embodied presence appears in these four frames.'),
    'breathing / undulating': ('PARTIAL', 'Lips flex and change overlap, but these pairs do not demonstrate a sustained whole-field breathing cycle.'),
    'folding / unfolding': ('PRESENT', 'Right-side curled lips and orange/green cups change bend and overlap at both fixed viewpoints.'),
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
(HERE / 'continuum-v15.js').write_bytes((HERE / 'continuum.js').read_bytes())
print('Recorded four inspected v15 frames and all 15 descriptors; realism remains CLOSE.')
