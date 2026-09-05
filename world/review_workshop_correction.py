"""Record the two manually inspected Workshop correction-v1 frames; no auto-grading."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ITERATION = 'fidelity-workshop-correction-v1'
ledger = json.loads((HERE / 'fidelity-grades.json').read_text(encoding='utf-8'))
assert not any(h.get('iteration') == ITERATION for h in ledger['history']), 'Already recorded'
before = copy.deepcopy(ledger['targets']['workshop'])
observations = [
    'Inspected numbered JPEG once: gold toothed gears, press frames and red packages on left-hand benches; a contrasting white-on-black production wing at right. Repeated tall frames and small bays recede behind the purple central portal. Five filament humanoids remain visible. White equipment merges into its bright backdrop, and miniature carriers are not clearly resolved.',
    'Inspected numbered JPEG once at the same camera: left gear spokes change orientation, red packages shift along the bench, and press crosshead heights differ. Workers change arm/head ornaments and surface contours drift. Deep frame rows remain visible; right equipment remains low-contrast. No clear hand-to-hand exchange or teaching is demonstrated.'
]
captures = []
for suffix, label, observation in zip(['', '-motion'], ['fidelity_workshop_correction_v1', 'fidelity_workshop_correction_v1_pair'], observations):
    receipt = json.loads((HERE / f'{ITERATION}{suffix}.json').read_text())
    d = receipt['capture_diagnostics']
    filename = f'{ITERATION}{suffix}.png'
    digest = hashlib.sha256((HERE / filename).read_bytes()).hexdigest()
    assert digest == receipt['capture_sha256']
    assert not receipt['errors'] and not d['missingEvidence'] and d['uncitedMeshes'] == 0
    assert d['detail'] == 'high' and d['paused']
    captures.append(dict(file=filename, sha256=digest, detail='high', render_signature=receipt['render_signature'], animTime=d['animTime'], inspection=f'{label}: {observation}'))

rows = [
    ('beings / presences', 'PRESENT', 'Five distinct filament-bodied presences occupy the aisle. Tiny white carriers are not clearly resolved; unseen-presence variants cannot be depicted literally.'),
    ('circuitry / machinery', 'PRESENT', 'Left-hand benches have unmistakable toothed intermeshing wheels, upright press frames, crossheads and red packages. The pair shows shifted gear spokes and packages. White machinery on the right loses separation against its backdrop; machinery detail is uneven.'),
    ('room / architecture', 'PRESENT', 'Floor, high ceiling, repeating structural frames, production wings and the central purple exit establish factory architecture. Market stalls and folding corridors are not represented.'),
    ('geometry / patterns', 'PRESENT', 'Teal/gold contour fields cover the aisle and left shell, alongside angular gold frames, toothed circles and pink overhead zigzag filaments. The white wing intentionally contrasts with this patterned setting.'),
    ('humanoid / bodies', 'PRESENT', 'Five filament presences have heads, torsos, paired legs and articulated arms. The boxed-body worker variant is too small and low-contrast here to establish its body structure.'),
    ('small / miniature', 'PARTIAL', 'Squat workers stand beside much taller presses, providing a stronger scale cue than the baseline. Product-sized white carriers are not clearly resolved; the scene does not convincingly establish extreme miniature scale.'),
    ('vast / infinite', 'PARTIAL', 'Repeated gold and white frame rows and diminishing production bays extend behind the central exit, making the room substantially deeper. A finite patterned far wall remains, and the camera does not establish limitless or gigantic factory scale.'),
    ('communicating / teaching', 'PARTIAL', 'Workers hold their arms near suspended geometric objects. Changes between frames do not show a legible exchange or lesson; packages moving on a bench are not evidence of communication.'),
    ('intricate / detailed', 'PRESENT', 'Dense body filaments and closely spaced wall/floor contours remain visible; gear teeth, spokes and striped packages add local mechanical detail. The white wing is comparatively simplified, and unlimited detail is not demonstrated.'),
    ('layered / multidimensional', 'PARTIAL', 'Overlapping workers, machines, the central portal and receding frame rows establish multiple depth layers. These are still ordinary perspective, not convincing impossible dimensions or folding entity corridors.'),
    ('moving / animated', 'PRESENT', 'The paired frames show gear-spoke rotation, shifted red packages and press crosshead positions, as well as articulated beings and drifting surface contours. This establishes mechanical and figure animation, not a complete observed manufacturing process.'),
    ('fractals', 'PARTIAL', 'Nested contour fields, branching body filaments and repeated structures suggest fractal detail. Gear teeth and perspective repetition alone do not establish self-similar fractal manufacturing at multiple scales.'),
    ('jester / clown form', 'PARTIAL', 'Pink bobbled head surrounds retain playful silhouettes, but no unmistakable clown face, patterned clown body or multiplying limbs is established.'),
    ('multicoloured', 'PRESENT', 'Teal, green, gold, red and magenta/purple remain distinct across machinery, patterns and beings. The contrasting monochrome wing preserves a different validated variant rather than making every surface rainbow.'),
    ('white', 'PRESENT', 'An entire bright white production wing with black roof/belt contrast occupies the right side, rather than isolated white highlights. White presses and packages merge into the backdrop; this covers the setting palette, not full fidelity to the minimalist carrier narrative.')
]
descriptors = {name: dict(grade=grade, observation=observation) for name, grade, observation in rows}
descriptors['moving / animated']['temporal_observation'] = f"At animTime {captures[0]['animTime']:.4f} versus {captures[1]['animTime']:.4f}, unchanged camera: left gear spokes rotate, red bench packages shift, press crosshead heights differ, workers' arm/head-surround poses change and aisle contours drift. These frames do not establish object teaching, completed manufacture or impossible transformation."
after = dict(close_up=False, captures=captures, descriptors=descriptors)
ledger['targets']['workshop'] = after
history = dict(target='workshop', iteration=ITERATION, changes='Replaced Workshop-only leafy props with gears, piston presses, transporting packages and boxed carriers; deeper lateral production wings and contrasting white-on-black factory. Preserved central portal distance and added station collision bounds. Garden growth unchanged.', before=before, after=copy.deepcopy(after), remaining='Miniature and vast scale, communication, multidimensional layering, fractals and clown form remain PARTIAL. White-wing machinery needs better separation. Renderer edits stale previous Garden capture and acceptance signatures.', verification=dict(syntax=['trip.js PASS', 'fractal.js PASS'], capture_errors=[], uncitedMeshes=0))
ledger['history'].append(history)
(HERE / 'fidelity-grades.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
(HERE / 'workshop-correction-v1-review.json').write_text(json.dumps(dict(iteration=ITERATION, observations=observations, captures=captures, descriptors=descriptors), indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('Workshop correction-v1 manual observations and immutable before/after history recorded.')
