"""One-shot record of four actual v23 inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent
def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))
def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

iteration = 'rough-jewel-corolla-v23'
ledger, grades = read('realism-grades.json'), read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'Connected red/magenta/violet walls enclose green/yellow, cyan/blue and pink scalloped lips, ending in a small green/yellow/pink radial flower. The fine contour loops seen in v22 are no longer pervasive. Broad highlights are smoother, but many hard-edged near-black oval and lobed blotches cover the walls. Large surface areas are dim; scattered lime, cyan and pink highlights look glossy. The centre remains a simple stretched pinwheel, not a richly folding corolla.'
close = 'Actual forward walking reaches z=-8.31904. Green/cyan foreground surrounds blue/violet inner lips and a large pink/yellow/red axial fan. Smaller corrugations remain, but broad surfaces are smooth or smeared rather than deeply recursive. Black lobed patches are conspicuous and often look flat. In the motion frame the centre becomes an almost featureless coloured radial disc with a sharp central convergence; the axial warp has not established convincing depth folding.'
temporal = 'Entry times6.3165/9.4996 at fixed[0,1.7,8]; deep times9.5688/12.6189 at fixed[0,1.7,-8.31904]. Entry upper green/yellow lip becomes red/yellow and rolls diagonally while the cyan/blue throat changes scallop exposure; the small green flower turns into a pink/yellow fan. Deep green/cyan near walls roll across the upper/left edges, violet lips shift overlap, and the centre broadens and simplifies from a sharply creased fan to a smoother pink/yellow radial disc. This supports rotation and undulation with some changing outlines, not a full breathing cycle, convincing fold-over or inside-out transformation. Moving black blotches are not credited as geometry motion.'
reason = 'GAME, not RECOGNISE: the old pervasive fine reflection contours are reduced, but hard-edged black blotches, large dim/smeared wall areas, shallow detail and a flat-looking axial colour fan still read as a procedural effect. Deep motion makes the centre smoother and less intricate, not richly folded. Glossy highlights do not establish jewel-like density throughout. Black patches exist but do not convincingly read as intentional spatial openings; no root-miss or shading artifact receives geometry credit. Next diagnose occlusion and axial form separately before rebuilding. This is visual judgment, not witness certification; CPU convergence is not GPU first-hit proof.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v23', entry), ('realism-chrysanthemum-close-v23', close)]:
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
        assert not d['transition'] and r['veil_opacity'] == 0
        pair.append(d)
        capture = {'file': path.name, 'sha256': digest(path),
                   'receipt_sha256': digest(path.with_suffix('.json')),
                   'inspection': 'view_image, inspected once: ' + observation}
        captures.append(capture)
        coverage_captures.append({**capture, 'detail': d['detail'], 'animTime': d['animTime'], 'render_signature': signature})
    assert pair[0]['position'] == pair[1]['position']
    assert pair[1]['animTime'] - pair[0]['animTime'] >= 3
current = {'grade': 'GAME', 'reason': reason, 'temporal_observation': temporal, 'captures': captures}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                          'before': copy.deepcopy(ledger['targets']['chrysanthemum']), 'review': copy.deepcopy(current)})
ledger['targets']['chrysanthemum'] = current
observations = {
    'flower / mandala': ('PRESENT', 'Concentric scalloped lips frame a multicoloured radial flower/fan, much larger after walking, although its simple flat appearance fails the separate realism bar.'),
    'geometry / patterns': ('PRESENT', 'Connected repeated scallops, corrugations and radial sectors remain visible. Black blotches are excluded from pattern credit.'),
    'multicoloured': ('PRESENT', 'Simultaneous red, orange, yellow, lime, green, cyan, blue, violet and magenta appear across the connected surfaces.'),
    'fractals': ('PARTIAL', 'Large lips contain smaller corrugations, but lack deep clean recursive structure; the deep motion centre becomes broadly smooth. Blotches are not fractals.'),
    'tunnel / corridor': ('PRESENT', 'Near walls recede through smaller overlapping lips to a radial centre, enlarged by real forward walking.'),
    'spinning / rotating': ('PRESENT', 'Coloured axial sectors change orientation and surrounding scallop exposure shifts around the axis in both fixed-pose pairs.'),
    'bright / luminous': ('PARTIAL', 'Localized lime, cyan, yellow and pink highlights appear bright and glossy, but extensive dim wall areas and black shading interrupt an enveloping luminous field.'),
    'morphing / transforming': ('PARTIAL', 'Lips change outlines and overlap, and the centre broadens and simplifies. The basic concentric tunnel and radial fan persist.'),
    'dark / black': ('PARTIAL', 'Substantial near-black regions contrast with coloured highlights, unlike the tiny ambiguous v22 slits. They often look like flat hard-edged shading patches, not convincing spatial black gaps. Credit is limited to visible darkness, not openings or verified occlusion geometry.'),
    'green': ('PRESENT', 'Green/lime surrounds the entry throat and broad green/cyan surfaces fill the deep foreground.'),
    'purple / pink': ('PRESENT', 'Magenta/violet outer and inner lips surround a large pink axial fan, persisting through both pairs.'),
    'saturated / vivid': ('PRESENT', 'Strong pink, lime, cyan, violet and yellow hues coexist, despite lower brightness across much of the view.'),
    'beings / presences': ('ABSENT', 'No readable face, hand, body or embodied presence appears; the axial fan is not a being.'),
    'breathing / undulating': ('PARTIAL', 'Near lips roll and change width while the centre broadens. The short pairs do not show a complete expansion/contraction cycle.'),
    'folding / unfolding': ('PARTIAL', 'Continuous lips change relative exposure and outlines, but no convincing fold-over or inside-out transformation is shown; the deep axial centre becomes a smooth flat-looking disc.')}
motion = {'spinning / rotating', 'morphing / transforming', 'breathing / undulating', 'folding / unfolding'}
review = {'close_up': False, 'captures': coverage_captures,
          'descriptors': {name: {'grade': grade, 'observation': observation,
                          **({'temporal_observation': temporal} if name in motion else {})}
                          for name, (grade, observation) in observations.items()}}
assert len(observations) == 15
grades['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                         'before': copy.deepcopy(grades['targets']['chrysanthemum']),
                         'after': copy.deepcopy(review), 'remaining': reason})
grades['targets']['chrysanthemum'] = review
assert (HERE / 'continuum-v23.js').read_bytes() == (HERE / 'continuum.js').read_bytes()
write('realism-grades.json', ledger)
write('fidelity-grades.json', grades)
print('Recorded four inspected v23 frames and all15 descriptors: GAME; luminous and dark/black PARTIAL; beings ABSENT.')
