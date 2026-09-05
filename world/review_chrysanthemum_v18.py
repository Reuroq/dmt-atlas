"""One-shot record of four actual v18 view_image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'swept-branching-corollas-v18'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'Pink/magenta and orange swept leaves fill the near view around yellow, green, cyan and blue radial layers. Three pairs of smaller cupped motifs occur inside broad glossy surfaces. Density increases, but the leaves repeat mechanically, wide faces remain smooth, rim bands are jagged and the axial centre is a tiny pinwheel. Black openings are mostly peripheral at entry.'
close = 'Real forward walking reaches z=-7.41312. Large green/yellow and cyan paddle-like panels surround deeper blue layers, with paired smaller cupped forms on their faces. Broad black inter-petal gaps persist. The subordinate forms read as attached decorative motifs, not convincing structural branching. Straight-looking panel sides, broad blank interiors, serrated perimeter bands and glossy repeated shapes dominate.'
temporal = 'At entry, the upper orange/yellow leaf shifts right while the upper-left magenta leaf moves left and becomes violet; right-hand leaves move upward. At the fixed walked-in pose, the green upper-centre panel turns toward the upper right, and the right orange foreground petal rotates upward. Black gaps change width and curled faces change exposure. Rotation is clear, but the repeated paddle-and-motif inventory persists; a complete breathing cycle or substantial spatial self-transformation is not demonstrated.'
reason = 'GAME, not RECOGNISE: density and the extent of readable smaller folds improve, and the old radial/perforation cuts are removed. Nevertheless broad glossy paddle surfaces and repeated applied cup motifs look manufactured. Jagged/segmented edge bands, near-straight panel sides, weak structural connection between scales and a tiny blue pinwheel centre remain prominent in the genuine deep view. The intended connected branching corolla is not convincingly achieved visually. Clear rotation and saturated colour do not overcome the game/CG-sculpture appearance; rebuild required, no witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v18', entry),
                            ('realism-chrysanthemum-close-v18', close)]:
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
current = {'grade': 'GAME', 'reason': reason, 'temporal_observation': temporal,
           'captures': captures}
ledger['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                          'before': copy.deepcopy(ledger['targets']['chrysanthemum']),
                          'review': copy.deepcopy(current)})
ledger['targets']['chrysanthemum'] = current
observations = {'flower / mandala': ('PRESENT', 'Eightfold swept petals and nested radial layers form a flower around the blue pinwheel centre.'), 'geometry / patterns': ('PRESENT', 'Repeated corolla panels, paired small cupped motifs and concentric radial ordering are clearly visible.'), 'multicoloured': ('PRESENT', 'Magenta, pink, orange, yellow, lime green, cyan, blue and violet coexist across the entry and approached views.'), 'fractals': ('PARTIAL', 'Several sizes of subordinate cupped folds occur on larger leaves and deeper layers. They read as sparse applied motifs rather than continuous structural recursion at every scale.'), 'tunnel / corridor': ('PRESENT', 'Real forward walking enlarges near corollas and exposes broader green/cyan panels with changed occlusion around the deeper blue axis. This demonstrates spatial recession, not an endless tunnel.'), 'spinning / rotating': ('PRESENT', 'Tracked upper-centre panels turn toward the upper right and right-hand foreground petals rise around the axis in the fixed-pose temporal pairs.'), 'bright / luminous': ('PRESENT', 'Bright yellow/lime and cyan interiors and saturated magenta/orange foreground leaves remain luminous against the dark openings.'), 'morphing / transforming': ('PARTIAL', 'Curl exposure and gap width change with rotation, but broad panels retain the same inventory of paired motifs rather than transforming into new structures.'), 'dark / black': ('PRESENT', 'Broad black spaces persist between approached petals in both deep frames; entry openings are more peripheral. Jagged numerical edge defects are not credited.'), 'green': ('PRESENT', 'Large lime-green and yellow-green panels dominate the approached corolla.'), 'purple / pink': ('PRESENT', 'Broad near leaves are pink/magenta and violet, with deeper blue/violet around the axis.'), 'saturated / vivid': ('PRESENT', 'Strong pink, magenta, orange, lime and cyan remain highly saturated across the view.'), 'beings / presences': ('ABSENT', 'No readable being, face or embodied presence appears in any of the four inspected frames; paired motifs are not graded as faces.'), 'breathing / undulating': ('PARTIAL', 'Aperture and overlap vary across the pair, but rotation predominates and a whole-field breathing cycle is not demonstrated.'), 'folding / unfolding': ('PARTIAL', 'Curl profiles and subordinate cups change exposure, but no convincing broad fold-over or continuous opening sequence emerges from the repeated paddles.')}

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
(HERE / 'continuum-v18.js').write_bytes((HERE / 'continuum.js').read_bytes())
print('Recorded four inspected v18 frames and all 15 descriptors; realism is GAME.')
