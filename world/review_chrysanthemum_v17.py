"""One-shot record of four actual v17 view_image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'local-frame-capsule-vaults-v17'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = ('Eightfold layers of pink/magenta and orange rounded shell mouths surround '
         'yellow/green, cyan and blue inner layers. Thick rims, deep interiors and '
         'paired small hooked vaults are visible. Broad black gaps separate petals. '
         'Large isolated shells, severed lip ends, contour-like highlights and a '
         'small repeated blue centre read as glossy manufactured segments.')
close = ('Real forward walking reaches z=-8.26656. Green/yellow and orange chamber '
         'interiors enlarge; paired subordinate vaults are visibly set into curved '
         'back walls. Axial layers recede into a blue/violet centre with changed '
         'occlusion. Foreground geometry has conspicuous flat cut faces, perforated '
         'annular strips and sharp crescent ends. Black distance remains between '
         'shells. Nested geometry is readable but sparse and mechanically repeated.')
temporal = ('At entry, the large upper magenta mouth moves left while the right '
            'magenta mouth rises and turns; the lower-right shell rotates upward. '
            'At the fixed walked-in pose, the foreground perforated ring changes '
            'into separated crescents and right-hand nested mouths turn into view. '
            'The coordinated angular shift demonstrates rotation. Opening and '
            'overlap change, but the same capsule inventory persists; a full '
            'breathing cycle or convincing spatial self-transformation is not shown.')
reason = ('GAME, not RECOGNISE: rigid-frame rounded interiors and smaller attached '
          'vaults improve readable volume over v16, but the large glossy shell '
          'segments look manufactured. Sharp sliced ends, perforated annular '
          'strips, sparse repeated capsule shapes, contour highlights and the tiny '
          'repeated centre dominate. Walking exposes more clipping instead of '
          'dense continuous recursive structure. Saturated colour and visible '
          'rotation do not overcome the game/CG-sculpture appearance. Rebuild '
          'required; no witness validation is claimed.')
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v17', entry),
                            ('realism-chrysanthemum-close-v17', close)]:
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
observations = {
    'flower / mandala': ('PRESENT', 'Eightfold rounded petals and interleaved smaller radial layers form a flower around the blue/violet centre.'),
    'geometry / patterns': ('PRESENT', 'Radial shell repetition, oval mouths and paired hooked interior vaults are plainly visible.'),
    'multicoloured': ('PRESENT', 'Pink, magenta, orange, yellow, green, cyan and blue coexist in both entry and approached views.'),
    'fractals': ('PARTIAL', 'Smaller paired vaults are visibly nested in larger curved interiors; only a few simple repeated scales read, not continuous recursive intricacy.'),
    'tunnel / corridor': ('PRESENT', 'Successive shells surround an axial corridor; actual forward walking enlarges and occludes near layers while exposing deeper cyan/blue chambers. This does not establish an endless tunnel.'),
    'spinning / rotating': ('PRESENT', 'Tracked upper and right magenta shells shift together around the axis, and approached mouths turn through changing angular positions across the settled temporal pairs.'),
    'bright / luminous': ('PRESENT', 'Bright yellow/green interiors and saturated pink/orange rims remain self-lit against black gaps, with glossy highlights.'),
    'morphing / transforming': ('PARTIAL', 'Mouth exposure and crescent overlap change in time, but the same sparse capsule-shaped inventory persists.'),
    'dark / black': ('PRESENT', 'Large black gaps remain between outer petals and between approached chambers; thin numerical rim defects are not credited.'),
    'green': ('PRESENT', 'Large green and yellow-green chamber interiors fill much of the approached view.'),
    'purple / pink': ('PRESENT', 'Pink/magenta and violet outer shells occupy broad regions, with blue/violet in the centre.'),
    'saturated / vivid': ('PRESENT', 'Intense magenta, orange, lime green and cyan span the layered scene.'),
    'beings / presences': ('ABSENT', 'No readable being, face or embodied presence appears in any of the four inspected frames.'),
    'breathing / undulating': ('PARTIAL', 'The field changes aperture and overlap, but rotation and local tilting cannot establish a whole-field breathing cycle in these pairs.'),
    'folding / unfolding': ('PARTIAL', 'Foreground closed-looking oval strips become exposed crescents and mouths change tilt; convincing continuous folding is weakened by hard clipped ends and rigid repeated shapes.'),
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
(HERE / 'continuum-v17.js').write_bytes((HERE / 'continuum.js').read_bytes())
print('Recorded four inspected v17 frames and all 15 descriptors; realism is GAME.')
