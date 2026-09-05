"""One-shot record of four actual v20 view_image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'hinged-multiscale-lobes-v20'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'Pink, violet, orange, yellow, lime, green and cyan oval buds repeat in concentric tenfold layers around a blue/purple central flower. Each broad smooth oval has attached smaller rounded lobes and still smaller rims. Compared with the prior documented scrollwork, this is a new lobed structure, but its isolated repeated units resemble glossy ornamental buds. Concentric highlight/contour bands remain conspicuous on the broad blank oval faces, with fine jagged seams around some subsidiary lobes. Black gaps occupy much of the view.'
close = 'Real forward walking reaches z=-8.37376. Large yellow/green and orange buds pass out through the edges; a small cyan/blue/purple rosette remains separated from them by an enormous black annulus. The first deep frame shows edge-on cupped crowns; the second exposes broad oval faces and opens the central flower wider. Subordinate lobes connect to each primary volume, but the primary volumes themselves remain disconnected floating items. There is insufficient geometry through the near-to-axis transition.'
temporal = 'Entry times4.9185/8.0519 at fixed[0,1.7,8]; deep times9.6198/12.6864 at fixed[0,1.7,-8.37376]. Entry upper orange forms rotate toward upper right and stand more upright as the central rosette contracts. Deep left green and right orange crowns turn from edge-on fingers/cups to front-facing oval buds; small marginal lobes change exposure and relative overlap, and the cyan/purple axial flower expands. Rotation, opening/closing silhouettes and limited local articulation are visible. Two short pairs do not show a complete breathing cycle or continuous surfaces turning inside out.'
reason = 'GAME, not RECOGNISE: broad glossy oval buds with small decorative lobes form a sparse inventory of disconnected repeated objects, not a continuous folding fractal corolla. The centre opens and contracts, and smaller lobes articulate, but large blank faces, contour bands, seam artifacts and especially the vast empty near-to-axis annulus dominate. Five geometric scales are not equivalent to continuous visible complexity. The intended density and contour fixes have not succeeded. Rebuild required; this visual judgment is not witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v20', entry),
                            ('realism-chrysanthemum-close-v20', close)]:
    pair = []
    for suffix in ['', '-motion']:
        path = HERE / (prefix + suffix + '.png')
        r = read(path.with_suffix('.json').name)
        d = r['capture_diagnostics']
        assert not r['errors']
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
observations = {'flower / mandala': ('PRESENT', 'Tenfold rings of rounded lobed buds frame a cyan/blue/purple central flower; the deep second frame exposes a wider petal-like axial corolla.'), 'geometry / patterns': ('PRESENT', 'Repeated primary oval volumes carry successively smaller rounded lobes, arranged in concentric radial layers at both viewpoints.'), 'multicoloured': ('PRESENT', 'Violet, magenta, pink, orange, yellow, lime, green, cyan and blue coexist across the four inspected frames.'), 'fractals': ('PARTIAL', 'Smaller joined lobes repeat along primary buds and at the axial flower. Finite nested detail is visible, but broad smooth oval faces and isolated units dominate, not continuous fine-scale recursion.'), 'tunnel / corridor': ('PRESENT', 'Real forward walking passes near volumes out through the frame while the recessed flower grows. This demonstrates spatial recession and corridor movement, not infinite depth.'), 'spinning / rotating': ('PRESENT', 'Upper orange entry forms move toward the upper right; deep foreground crowns rotate and turn their oval faces toward the camera while axial petals change orientation.'), 'bright / luminous': ('PRESENT', 'Lime, cyan and saturated pink/orange volumes remain self-lit and bright against the black field; small edge halos are visible.'), 'morphing / transforming': ('PARTIAL', 'Central flower width and subordinate-lobe overlap change across the pairs, but all forms retain the same oval-bud inventory rather than becoming new spatial structures.'), 'dark / black': ('PRESENT', 'Large black gaps surround each isolated bud; the deep pair has an enormous black annulus between the foreground and axial flower. Numerical contour/seam defects are not credited.'), 'green': ('PRESENT', 'Lime and green near buds and axial rows occupy substantial parts of the entry and deep views.'), 'purple / pink': ('PRESENT', 'Purple and pink near buds fill entry edges; blue/purple axial petals and pink/red foreground volumes remain visible after walking.'), 'saturated / vivid': ('PRESENT', 'Strong magenta, violet, orange, lime and cyan contrast sharply with black, with several simultaneous saturated hues.'), 'beings / presences': ('ABSENT', 'No readable being, face or embodied presence is visible. Bud-like forms are not credited as entities.'), 'breathing / undulating': ('PARTIAL', 'The entry axial flower narrows and the deep axial flower widens; near crowns also change profile. No complete expansion/contraction cycle is captured.'), 'folding / unfolding': ('PARTIAL', 'Small attached marginal lobes change relative overlap and open cupped silhouettes while broad ovals turn into view. Some articulated closing/opening is visible, but the motion reads mainly as buds tilting; no convincing continuous surface folds over or turns inside out.')}

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
assert (HERE / 'continuum-v20.js').read_bytes() == (HERE / 'continuum.js').read_bytes(), 'Archive changed'
print('Recorded four inspected v20 frames and all 15 descriptors; realism is GAME.')
