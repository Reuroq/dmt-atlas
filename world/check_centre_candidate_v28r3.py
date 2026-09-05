"""One-shot curvature sampling and immutable evidence/runtime integrity check."""
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
from field_centre_v28 import field, PIXEL
from fidelity import render_signature

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-candidate-v28r3-integrity.json'
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

# Independent float64 finite differences, not copied analytic gradients.
rng = np.random.default_rng(2803)
n = 8000
angles = rng.uniform(-np.pi, np.pi, n)
rho = rng.uniform(4.535, 9.465, n)
q = rng.uniform(-1, 0, n)
r = rho*np.sqrt(1-q*q)
p = np.column_stack([r*np.cos(angles), 1.7+r*np.sin(angles), -27.5+rho*q/.45])
# Half side-wall points, plus explicit seam and axis samples.
p[:n//2] = np.column_stack([rho[:n//2]*np.cos(angles[:n//2]),
    1.7+rho[:n//2]*np.sin(angles[:n//2]), rng.uniform(-27.5, 8, n//2)])
seam = p[:512].copy()
seam[:, 2] = -27.5+rng.uniform(-.001, .001, 512)
axis = np.column_stack([np.zeros(512), np.full(512, 1.7), -27.5-rho[:512]/.45])
p = np.concatenate([p, seam, axis])
t = rng.uniform(0, 900, len(p))
d = rng.normal(size=p.shape)
d /= np.linalg.norm(d, axis=1)[:, None]
camera = np.column_stack([np.zeros(len(p)), np.full(len(p), 1.7), rng.choice([8, -6], len(p))])
eps = .001
curvature = 160+25*PIXEL+92*PIXEL**2
sampling = []
for high in [1, 0]:
    f = field(p, t, camera, high)
    slope = (field(p+eps*d, t, camera, high)-field(p-eps*d, t, camera, high))/(2*eps)
    max_second = 0
    max_remainder_ratio = 0
    for step in [0, .1, .2, .4]:
        q = p+step*d
        second = (field(q+eps*d, t, camera, high)-2*field(q, t, camera, high)+field(q-eps*d, t, camera, high))/eps**2
        max_second = max(max_second, float(np.max(np.abs(second))))
        if step:
            remainder = np.abs(field(q, t, camera, high)-f-slope*step)
            max_remainder_ratio = max(max_remainder_ratio, float(np.max(remainder/(.5*curvature*step**2))))
    remaining = .95*np.abs(f)
    quadratic = np.minimum(.4, 2*remaining/(np.abs(slope)+np.sqrt(slope*slope+2*curvature*remaining)))
    after = field(p+quadratic[:, None]*d, t, camera, high)
    crossings = int(np.sum(f*after<0))
    sampling.append({'high': high, 'points': len(p), 'max_second_derivative': max_second,
        'curvature_bound': curvature, 'max_taylor_remainder_ratio': max_remainder_ratio,
        'quadratic_endpoint_sign_crossings': crossings,
        'passed': max_second<curvature and max_remainder_ratio<=1 and crossings==0})

prior = json.loads((HERE/'diagnostic-centre-v27r2-receipts.json').read_text())
protected = prior['protected_after']
unchanged = {name: digest(name)==sha for name, sha in protected.items()}
numeric = json.loads((HERE/'numeric-candidate-v28r3-check.json').read_text())
numeric_hashes = {name: digest(name)==sha for name, sha in numeric['files'].items()}
evidence = json.loads((HERE/'diagnostic-centre-v27r2-integrity.json').read_text())['evidence_hashes']
prior_hashes = {name: digest(name)==sha for name, sha in evidence.items()}
syntax = []
for name in ['continuum-v28-candidate.js','continuum-v28r2-candidate.js','continuum-v28r3-candidate.js']:
    subprocess.run(['node', '--check', str(HERE/name)], check=True, capture_output=True)
    syntax.append(name)
new_files = []
for pattern in ['*v28*.py','*v28*.js','*v28*.html','*v28*.json','*v28*.log','centre-v28-curvature.md']:
    new_files.extend(p.name for p in HERE.glob(pattern) if p.name != 'check-centre-candidate-v28r3-r2.log')
for name in new_files:
    if name.endswith('.py'):
        compile((HERE/name).read_text(), name, 'exec')
comparison = []
for version in ['v27r2','v28','v28r2','v28r3']:
    check = json.loads((HERE/f'numeric-candidate-{version}-check.json').read_text())
    raw = json.loads((HERE/f'numeric-candidate-{version}-raw.json').read_text())
    iterations = [v for c in raw for v in c['hits'][2::4]]
    comparison.append({'version': version, 'passed': check['passed'],
        'misses': sum(c['misses'] for c in check['cases']),
        'max_iterations': max(iterations), 'mean_iterations': float(np.mean(iterations)),
        'gpu_three_readbacks_total_seconds': sum(c['gpu_three_readbacks_seconds'] for c in check['cases']),
        'max_reference_difference': check['max_reference_difference']})
out = {'integrity_passed': numeric['passed'] and all(s['passed'] for s in sampling)
       and all(unchanged.values()) and all(numeric_hashes.values()) and all(prior_hashes.values()),
    'numeric_passed': numeric['passed'], 'curvature_sampling': sampling,
    'protected_unchanged': unchanged, 'numeric_receipt_hashes_valid': numeric_hashes,
    'prior_visual_evidence_hashes_valid': prior_hashes, 'syntax_passed': syntax,
    'sampled_cost_comparison': comparison, 'live_render_signature': render_signature(),
    'source_hashes': {name: digest(name) for name in sorted(set(new_files))},
    'limits': 'Finite samples and ideal-field bound derivation, not universal float32 root proof. Small probe readback times are not full-resolution rendering, temporal quality, frame rate or hardware-GPU benchmarks.',
    'candidate_promoted': False, 'visual_sequence_passed': False, 'overall_passed': False}
OUT.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({k: out[k] for k in ['integrity_passed','curvature_sampling','sampled_cost_comparison']}))
assert out['integrity_passed']
