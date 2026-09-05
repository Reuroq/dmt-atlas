"""One-shot record of four actual v19 view_image inspections; no automatic grading."""
import copy
import json
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

iteration = 'connected-rounded-arc-sweeps-v19'
ledger = read('realism-grades.json')
grades = read('fidelity-grades.json')
assert not any(h.get('iteration') == iteration for h in ledger['history']), 'Already reviewed'
assert not any(h.get('iteration') == iteration for h in grades['history']), 'Already reviewed'
signature = render_signature()
entry = 'Pink, magenta, orange and violet large rounded scroll hoops surround yellow, green and cyan layers. Smaller curled branches visibly join the hoop interiors. Broad paddle faces are gone and the tips are rounder, but smooth repeated circular bands resemble ornamental ironwork or glossy plastic. Fine contour bands remain on the surfaces. Large black spaces separate the outer rings from a small central green/cyan/blue rosette.'
close = 'Real forward walking reaches z=-8.37280. Foreground orange, pink and lime hoops enlarge and leave the frame while a green/cyan/yellow scroll rosette grows at the axis. Small curled branches share roots with larger circular bands. A broad empty black annulus isolates the central medallion. Repeated hoop proportions, largely blank rounded bands, contour artifacts and a tiny star at the very centre retain a manufactured ornamental appearance.'
temporal = 'Entry times5.7325/8.7824 at fixed[0,1.7,8]; deep times9.5800/12.6300 at fixed[0,1.7,-8.3728]. The central upper green/cyan lobe turns toward the upper right; large left green foreground hoops descend in the deep pair. Smaller curls change exposure and overlap while the same repeated scroll inventory persists. Rotation and modest curl-profile variation are visible; no full breathing cycle, genuine fold-over or transformation into new structures is demonstrated.'
reason = 'GAME, not RECOGNISE: the broad graph paddles and applied surface motifs are replaced by visibly joined rounded branches, but those branches form repetitive circular scrollwork resembling glossy plastic or ornamental ironwork. Large black gaps dominate, especially the empty annulus isolating the central medallion after forward walking. Smooth broad bands have fine contour artifacts, sparse subordinate curls and no continuous fine-scale complexity. The axial rosette is richer than v19 but still terminates in a tiny repeated star. Rounded geometry and clear rotation do not establish immersive realism; rebuild required, no witness certification.'
captures, coverage_captures = [], []
for prefix, observation in [('realism-chrysanthemum-v19', entry),
                            ('realism-chrysanthemum-close-v19', close)]:
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
observations = {'flower / mandala': ('PRESENT', 'Radially repeated rounded lobes and nested scroll layers form a clear mandala around the small axial star, especially in the approached rosette.'), 'geometry / patterns': ('PRESENT', 'Large circular scrolls, shared-root smaller curls and repeated lobed axial rosettes are clearly visible at both viewpoints.'), 'multicoloured': ('PRESENT', 'Pink, magenta, violet, orange, yellow, lime, green, cyan and blue coexist across the four inspected frames.'), 'fractals': ('PARTIAL', 'Smaller curls visibly branch from larger scrolls and recur at several sizes in the axis. Finite, sparse branching and largely smooth bands do not provide continuous recursive detail.'), 'tunnel / corridor': ('PRESENT', 'Actual forward walking enlarges and passes near hoops while the recessed axial rosette grows and changes occlusion. This demonstrates traversable spatial recession, not infinite depth.'), 'spinning / rotating': ('PRESENT', 'The upper green/cyan central lobe turns toward the upper right and large left foreground green hoops descend in the fixed-pose deep pair; the entry rings also rotate.'), 'bright / luminous': ('PRESENT', 'Lime and cyan rosette edges and saturated pink/orange near scrolls remain luminous against broad black spaces.'), 'morphing / transforming': ('PARTIAL', 'Subordinate curl profiles and overlap vary, but the scene retains its repetitive hoop-and-scroll inventory rather than transforming into new spatial structures.'), 'dark / black': ('PRESENT', 'Broad black gaps exist between all scroll layers, with a particularly large empty black annulus around the isolated deep central rosette. Fine contour artifacts are not credited.'), 'green': ('PRESENT', 'Bright lime and green large approached hoops and axial curled branches occupy substantial parts of the view.'), 'purple / pink': ('PRESENT', 'Near hoops and attached curls are magenta, pink and violet at entry; pink/red large bands remain at the approached right edge.'), 'saturated / vivid': ('PRESENT', 'Strong pink, magenta, orange, lime and cyan coexist with deeply saturated violet; the bright forms contrast sharply with black.'), 'beings / presences': ('ABSENT', 'No readable face, being or embodied presence appears; the repeated scrolls are not credited as faces.'), 'breathing / undulating': ('PARTIAL', 'Lobe profiles and overlaps vary modestly, but dominant rotation and the short pairs do not demonstrate a whole-field breathing cycle.'), 'folding / unfolding': ('ABSENT', 'The rounded scroll inventory rotates and exposes smaller curls, but no surface visibly folds over or unfolds in either pair. A curled shape alone does not establish folding motion.')}

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
assert (HERE / 'continuum-v19.js').read_bytes() == (HERE / 'continuum.js').read_bytes(), 'Archive changed'
print('Recorded four inspected v19 frames and all 15 descriptors; realism is GAME.')
