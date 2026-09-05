"""One-shot promotion of the visually inspected, strictly stable HUD-only correction."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
out = HERE/'hud-ramp-v18-promotion.json'
assert not out.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
r = json.loads((HERE/'diagnostic-hud-ramp-v18.json').read_text())
a = json.loads((HERE/'hud-ramp-v18-appearance.json').read_text())
assert len(r['cases']) == 1 and len(r['cases'][0]['comparisons']) == 21
assert all(c['changed_pixels'] == 0 for c in r['cases'][0]['comparisons'])
assert not r['browser_errors'] and all(r['protected_unchanged'].values())
assert all(digest(n) == h for n,h in r['baseline'].items())
assert all(digest(n) == h for n,h in r['artifact_hashes'].items())
assert a['above_overlay']['changed_pixels'] == 0 and a['full_frame']['max_channel_delta'] <= 2
assert a['unobstructed_overlay']['mean_absolute_channel_delta'] < .5
before = {n:digest(n) for n in [*r['baseline'], 'fidelity.py']}
css = (HERE/'trip.css').read_text()
old = 'background:linear-gradient(transparent,#04020a70 75%,#04020ab0)'
new = 'background:url("hud-alpha-ramp-v18.png") center / 100% 100% no-repeat'
assert css.count(old) == 1
fidelity = (HERE/'fidelity.py').read_text()
anchor = "'beings.js', 'trip.css', 'fidelity-ui.js'"
assert fidelity.count(anchor) == 1
for n in ['trip.css','fidelity.py']:
    archive = HERE/('hud-ramp-v18-before-'+n)
    assert not archive.exists()
    archive.write_bytes((HERE/n).read_bytes())
(HERE/'trip.css').write_text(css.replace(old,new))
# Bind the new runtime asset into render receipts; no grading rules changed.
(HERE/'fidelity.py').write_text(fidelity.replace(anchor,"'beings.js', 'trip.css', 'hud-alpha-ramp-v18.png', 'fidelity-ui.js'"))
after = {n:digest(n) for n in before}
assert all(after[n] == before[n] for n in before if n not in ['trip.css','fidelity.py'])
from fidelity import render_signature
out.write_text(json.dumps({
    'runtime_change':'Only #hud::before background; all JS runtime and geometry unchanged',
    'metadata_change':'Include HUD PNG bytes in render_signature',
    'before':before,'after':after,'asset_sha256':digest('hud-alpha-ramp-v18.png'),
    'render_signature':render_signature(),
    'proof_sha256':{n:digest(n) for n in ['diagnostic-hud-ramp-v18.json','hud-ramp-v18-appearance.json']},
    'visual_review':'Desktop/mobile fixture inspected once; readable, no obvious banding. Geometry remains GAME. Mobile scene stretch is fixture-only.',
    'live_acceptance':'Pending affected original HIGH checks; historical failure preserved',
},indent=2)+'\n')
print('Promoted HUD-only correction and bound PNG asset into render signature.')
