"""One-shot record of four actual v21 image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'connected-sheared-corolla-v21'
ledger, grades = read('realism-grades.json'), read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'A connected rainbow tunnel fills the view, with broad magenta/orange outer folds, green/yellow intermediate scallops, cyan/blue/purple inner scallops and a red/yellow/green pinwheel-like central flower. The enormous empty annulus and isolated oval buds are gone. Ruffled lips and smaller ripples connect across the image, but the surfaces are covered in scratch-like striations and interference patterns, with torn, jagged black seams around the major lips. The axial flower is a regular converging pinwheel, not an intricate folding centre.'
close = 'Real forward walking reaches z=-8.00000. The connected green/cyan near surface fills all edges around a blue/purple scalloped throat and much larger magenta/orange/yellow axial flower. The near-to-axis transition remains filled. Large wave-shaped lips overlap, but severe fine striations, cellular-looking highlight interference and jagged dark tears dominate the surface. These are rendering defects, not evidence of fractals or intentional openings.'
temporal = 'Entry times5.0273/8.0607 at fixed[0,1.7,8]; deep times9.5423/12.6423 at fixed[0,1.7,-8.00000]. Entry green/yellow lip broadens upward and shifts its scallops, revealing a wider cyan band as the axial flower changes orientation and hue. Deep cyan/green lips roll diagonally toward the top and left; the blue throat changes its outline and the central pinwheel contracts and turns. Continuous wave propagation and changing overlap are visible, but two short pairs do not establish a full breathing cycle or a surface turning inside out. Fine scratch changes are not credited as motion evidence.'
reason = 'GAME, not RECOGNISE: the disconnected motif inventory has genuinely been replaced by a dense, connected ruffled tunnel, but extreme scratch-like aliasing, interference highlights, torn black seams and a simple axial pinwheel read as a defective procedural effect. Density is improved, not realism acceptance. Broad fold outlines change over time, but fine detail is not clean recursive geometry and folding remains only partially convincing. Black defects cannot satisfy the dark/black report descriptor. Rebuild the surface solver, sampling and axial structure; this is visual judgment, not witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v21', entry),
                            ('realism-chrysanthemum-close-v21', close)]:
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
observations = {
    'flower / mandala': ('PRESENT', 'Concentric scalloped corolla lips surround an axial multicoloured pinwheel flower; walking makes this flower substantially larger.'),
    'geometry / patterns': ('PRESENT', 'Continuous scalloped bands repeat around the axis with smaller ripples across the same surfaces, not isolated inventory pieces.'),
    'multicoloured': ('PRESENT', 'Magenta, violet, pink, orange, yellow, lime, green, cyan and blue coexist across the connected tunnel and central flower.'),
    'fractals': ('PARTIAL', 'Larger scalloped lips carry smaller ruffles, but no clean deep recursive hierarchy is resolved; much of the apparent fine detail is scratch-like aliasing and cannot be credited.'),
    'tunnel / corridor': ('PRESENT', 'Connected near walls recede through successively smaller scallops to an axial flower, which enlarges after actual forward walking.'),
    'spinning / rotating': ('PRESENT', 'Scallop positions shift around the axis and the central pinwheel changes orientation in both fixed-pose temporal pairs.'),
    'bright / luminous': ('PRESENT', 'Bright self-lit pink, lime, cyan and yellow remain visible in the folds without an external visible light source.'),
    'morphing / transforming': ('PARTIAL', 'The lips change outlines and relative overlap while waves propagate; the overall concentric tunnel and axial pinwheel structure persists.'),
    'dark / black': ('ABSENT', 'The view is filled by luminous coloured surfaces. Visible black slits are ragged rendering defects, not convincing intentional dark space or openings; they receive no credit.'),
    'green': ('PRESENT', 'Lime/green scallops are substantial at entry and fill the foreground after walking.'),
    'purple / pink': ('PRESENT', 'Magenta and violet cover entry walls, the inner throat and much of the deep central flower.'),
    'saturated / vivid': ('PRESENT', 'Strong simultaneous magenta, orange, yellow, green and cyan gradients dominate both views.'),
    'beings / presences': ('ABSENT', 'No readable being, face, hand or embodied presence is visible; the central pinwheel is not an entity.'),
    'breathing / undulating': ('PARTIAL', 'Near lips roll and broaden while the deep axial flower contracts; no complete expansion/contraction cycle is captured.'),
    'folding / unfolding': ('PARTIAL', 'Continuous scalloped lips change exposure and overlap, especially in the deep pair. They read as rolling waves, but aliasing and brief sampling prevent a convincing continuous fold-over or inside-out transformation.')}
motion = {'spinning / rotating', 'morphing / transforming', 'breathing / undulating', 'folding / unfolding'}
review = {'close_up': False, 'captures': coverage_captures,
          'descriptors': {name: {'grade': grade, 'observation': observation,
                          **({'temporal_observation': temporal} if name in motion else {})}
                          for name, (grade, observation) in observations.items()}}
grades['history'].append({'target': 'chrysanthemum', 'iteration': iteration,
                         'before': copy.deepcopy(grades['targets']['chrysanthemum']),
                         'after': copy.deepcopy(review), 'remaining': reason})
grades['targets']['chrysanthemum'] = review
assert (HERE / 'continuum-v21.js').read_bytes() == (HERE / 'continuum.js').read_bytes(), 'Archive changed'
write('realism-grades.json', ledger)
write('fidelity-grades.json', grades)
print('Recorded four inspected v21 frames and all 15 descriptors; realism GAME, dark/black ABSENT.')
