"""One-shot record of four actual v22 image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'analytic-filtered-corolla-v22'
ledger, grades = read('realism-grades.json'), read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'A dense connected rainbow corolla fills the view: magenta, red and orange near walls encircle green/yellow, cyan/blue and violet scalloped lips ending in a red/yellow/green radial flower. Broad folds are smoother and the conspicuous torn black seams are much less apparent than in v21. Nevertheless the walls retain thin contour-like loops and fine interference lines; some lips look melted or streaked. The axial flower remains a simple regular pinwheel with stretched blades, not a richly folding centre.'
close = 'Actual forward walking reaches z=-7.67968. Green/cyan foreground fills all image edges around blue/purple and magenta lips, and a much larger red/pink/yellow/green axial flower. The continuous depth connection persists and broad lips are smoother, but the centre looks like a flat stretched radial fan. Thin outlined loops cover smooth wall areas; rims carry fine irregular speckling and some dark sharp slits. These unresolved marks cannot be credited as fractal structure or intentional black space.'
temporal = 'Entry times4.8321/8.0651 at fixed[0,1.7,8]; deep times9.3622/12.5788 at fixed[0,1.7,-7.67968]. At entry the upper green/yellow lip rolls toward the upper right while its left side becomes orange, the cyan throat changes scallop exposure, and the axial flower turns and shifts from green/yellow toward pink/red. Deep green/cyan near lips roll diagonally across the upper and left edges; the large centre contracts, loses its broad green sector and turns into a pink/yellow star. The inner opening changes shape and relative overlap. These are visible undulation and rotation, but the short pairs do not establish a full breathing cycle, inside-out transformation or convincing continuous fold-over. Changing contour lines are not credited as motion evidence.'
reason = 'GAME, not RECOGNISE: solver/root and analytic-normal changes improve broad surface smoothness and reduce obvious torn black seams, but pervasive contour-like lines, smeared corrugations and a flat-looking stretched axial pinwheel still read as a procedural effect. The tube is dense and continuous, not yet an intricate self-transforming fractal corolla. There is no substantial convincing intentional dark space; fine dark creases and slits are ambiguous and receive no descriptor credit. Numerical convergence on a sparse CPU grid does not certify every GPU pixel. Rebuild the axial structure and diagnose remaining shading/contour artifacts without hiding misses. This is visual judgment, not witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v22', entry),
                            ('realism-chrysanthemum-close-v22', close)]:
    pair = []
    for suffix in ['', '-motion']:
        path = HERE / (prefix + suffix + '.png')
        r = read(path.with_suffix('.json').name)
        d = r['capture_diagnostics']
        assert not r['errors'] and r['render_signature'] == signature
        assert r['capture_sha256'] == digest(path)
        assert d['detail'] == 'high' and d['paused'] and not d['renderPending']
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
current = {'grade': 'GAME', 'reason': reason, 'temporal_observation': temporal,
           'captures': captures}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                          'before': copy.deepcopy(ledger['targets']['chrysanthemum']),
                          'review': copy.deepcopy(current)})
ledger['targets']['chrysanthemum'] = current
observations = {'flower / mandala': ('PRESENT', 'Connected concentric scalloped lips frame a strongly radial multicoloured pinwheel flower, substantially enlarged after real walking.'), 'geometry / patterns': ('PRESENT', 'Repeated scallops and corrugations connect across the tunnel and around the axial flower; fine contour artifacts are excluded from this credit.'), 'multicoloured': ('PRESENT', 'Magenta, red, orange, yellow, lime, green, cyan, blue and violet occur simultaneously in both viewpoints.'), 'fractals': ('PARTIAL', 'Large lips contain smaller corrugations, but no clean deep recursive hierarchy appears; outlined loops and fine interference cannot count as fractal geometry.'), 'tunnel / corridor': ('PRESENT', 'Connected near walls recede through successively smaller overlapping lips to an axial flower that becomes much larger after actual forward walking.'), 'spinning / rotating': ('PRESENT', 'Axial coloured sectors change orientation and scallops shift around the central axis in both fixed-pose temporal pairs.'), 'bright / luminous': ('PRESENT', 'Strong self-lit lime, cyan, pink and yellow bands stay bright inside the continuous corolla.'), 'morphing / transforming': ('PARTIAL', 'Scallop outlines, exposure and overlap change while the axial flower contracts and recolours; the basic concentric tunnel and radial fan remain.'), 'dark / black': ('ABSENT', 'No substantial convincing intentional dark region is established. Shaded surfaces are mostly green, blue, maroon or purple; fine dark creases and sharp slits remain ambiguous and receive no credit.'), 'green': ('PRESENT', 'Broad lime/green lips surround the entry throat and occupy the foreground after walking.'), 'purple / pink': ('PRESENT', 'Violet/magenta near walls and inner lips persist, with a large saturated pink central fan in the deep motion frame.'), 'saturated / vivid': ('PRESENT', 'Strong simultaneous pink, lime, yellow, cyan and violet dominate the connected surfaces.'), 'beings / presences': ('ABSENT', 'No readable face, hand, body or embodied presence appears; the radial fan is not an entity.'), 'breathing / undulating': ('PARTIAL', 'The near lips visibly roll and broaden while the deep centre contracts, but no complete expansion/contraction cycle is shown.'), 'folding / unfolding': ('PARTIAL', 'Continuous lips change outlines and relative exposure as they roll through the view. This supports partial folding, not a convincing fold-over or an inside-out transformation; the central fan stays flat-looking.')}
motion = {'spinning / rotating', 'morphing / transforming', 'breathing / undulating', 'folding / unfolding'}
review = {'close_up': False, 'captures': coverage_captures,
          'descriptors': {name: {'grade': grade, 'observation': observation,
                          **({'temporal_observation': temporal} if name in motion else {})}
                          for name, (grade, observation) in observations.items()}}
grades['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                         'before': copy.deepcopy(grades['targets']['chrysanthemum']),
                         'after': copy.deepcopy(review), 'remaining': reason})
grades['targets']['chrysanthemum'] = review
assert (HERE / 'continuum-v22.js').read_bytes() == (HERE / 'continuum.js').read_bytes(), 'Archive changed'
write('realism-grades.json', ledger)
write('fidelity-grades.json', grades)
print('Recorded four inspected v22 frames and all 15 descriptors; realism GAME, dark/black ABSENT; coverage remains failed.')
