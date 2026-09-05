"""One-shot record of four actual v25 inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent
def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))
def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

iteration = 'cartesian-deep-corolla-v25'
ledger, grades = read('realism-grades.json'), read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'Bright pink/red/violet walls surround lime/cyan, blue/violet and yellow/green scalloped lips. The large hard black lobes are gone. Highlights are broad and milky; most wall area is smooth, rubbery or smeared. The centre is a small padded four-lobed flower with blue dimples and a sharp axial colour convergence, not a dense recursively folding mandala.'
close = 'Real walking reaches z=-7.03968. Broad green/cyan foreground surrounds violet/pink lips and an enlarged green/yellow/orange flower. Several padded central lobes now have visible relief, but the whole remains shallow-looking and sparse. Motion exposes large triangular outer lips and simplifies the centre into a smooth few-lobed pinwheel. No convincing black spatial gaps are visible.'
temporal = 'Fixed entry[0,1.7,8] at6.1390/9.1889; fixed deep[0,1.7,-7.03968] at9.1686/12.2020. Entry scallops rotate diagonally and the blue/pink inner ring changes overlap; the centre changes its small lobe exposure. Deep foreground lime/cyan lobes widen into large pointed sheets, violet/pink inner lips change relative exposure, and the central padded flower becomes a smoother pinwheel. Supports rotation and undulation with outline changes; not a complete breathing cycle or convincing fold-over/inside-out transformation.'
reason = 'GAME, not RECOGNISE: hard black material blotches are removed and the field is more luminous, but broad rubbery/smeared walls, sparse scalloped rings, milky highlights and a simple axial flower remain. Cartesian central lobes have more relief than the old fan yet do not establish dense recursive 3D folding. Motion makes the centre simpler. No convincing black gaps, readable beings or jewel-like detail throughout. New subpixel ray tolerance is not universal convergence proof, and apparent gaps receive no artifact credit. Next investigate geometry scale/filter suppression and the axial pigment convergence; another colour adjustment alone is insufficient. This is visual judgment, not witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v25', entry), ('realism-chrysanthemum-close-v25', close)]:
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
observations = {'flower / mandala': ('PRESENT', 'Concentric scalloped lips surround a padded multicoloured flower, enlarged by real walking. Its sparse simple form fails the separate realism bar.'), 'geometry / patterns': ('PRESENT', 'Repeated scallops, pointed lips and nested lobes visibly form the connected tunnel.'), 'multicoloured': ('PRESENT', 'Red, orange, yellow, lime, green, cyan, blue, violet and magenta coexist across both fixed-pose pairs.'), 'fractals': ('PARTIAL', 'Smaller lobes and local ripples sit on larger lips, but recursive depth/detail is weak; broad surfaces and the moving centre become smooth.'), 'tunnel / corridor': ('PRESENT', 'Near walls recede through overlapping scalloped lips toward a flower, substantially enlarged by actual forward walking.'), 'spinning / rotating': ('PRESENT', 'Scallop orientation and coloured inner lips turn around the axis in both temporal pairs.'), 'bright / luminous': ('PRESENT', 'An enveloping bright lime, cyan, pink and violet field persists across both pairs, without the former broad black shading. Broad milky highlights do not earn jewel-realism credit.'), 'morphing / transforming': ('PARTIAL', 'Lips change outline and exposure; deep rounded lobes become pointed sheets. The same concentric tunnel and simple flower persist.'), 'dark / black': ('ABSENT', 'Blue/violet creases remain coloured rather than black. No substantial black field or convincing dark spatial openings appear; the removed shading blotches receive no gap credit.'), 'green': ('PRESENT', 'Lime/green rings persist at entry and green/cyan sheets dominate the deep foreground and central flower.'), 'purple / pink': ('PRESENT', 'Violet/blue and pink/magenta lips persist around the throat and flower through both pairs.'), 'saturated / vivid': ('PRESENT', 'Strong simultaneous pink, lime, cyan, violet and yellow dominate, with smoothly blended colour gradients.'), 'beings / presences': ('ABSENT', 'No readable face, hand, body or embodied presence; the central flower is not a being.'), 'breathing / undulating': ('PARTIAL', 'Lips change width and exposure at fixed pose, but the pairs do not show a complete expansion/contraction cycle.'), 'folding / unfolding': ('PARTIAL', 'Connected lips roll and change overlap, with some relief in central lobes, but no convincing fold-over or inside-out transformation. The deep motion centre simplifies.')}
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
assert (HERE / 'continuum-v25.js').read_bytes() == (HERE / 'continuum.js').read_bytes()
write('realism-grades.json', ledger)
write('fidelity-grades.json', grades)
print('Recorded four inspected v25 frames and all15 descriptors: GAME; luminous PRESENT; dark/black and beings ABSENT. Top10 dark blocker retained.')
