"""One-shot numerical implementation integrity; no visual or runtime promotion."""
import json
import math
import py_compile
import subprocess
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-candidate-v27r2-integrity.json'
assert not OUT.exists()
def read(name): return json.loads((HERE/name).read_text())

failed = read('numeric-candidate-v27-check.json')
passed = read('numeric-candidate-v27r2-check.json')
previous = read('redirect4-v25-check.json')
assert not failed['passed'] and passed['passed'] and not passed['errors']
assert sum(c['misses'] for c in failed['cases']) == 3
assert passed['limits'] == failed['limits'] == {'gradient': .005, 'bound_ratio': 1.001, 'scalar': .001, 'root': .03}
assert passed['rays'] == 38160 and passed['reference_rays'] == 360
assert sum(r['axis'] for c in passed['cases'] for r in c['references']) == 16
for result in [failed, passed, read('numeric-candidate-v26-check.json')]:
    for name, sha in result['files'].items():
        assert digest(HERE/name) == sha, name

source = (HERE/'continuum-v27r2-candidate.js').read_text()
extra = '''    // cw is monotone in |cap|. These extrema cover the entire .4 step,
    // including a step that crosses the start of the cap.
    float capLo=max(0.,-p.z-27.5-.4*abs(rd.z));
    float capHi=max(0.,-p.z-27.5+.4*abs(rd.z));
    float cwLo=capLo*capLo/(capLo*capLo+4.);
    float cwHi=capHi*capHi/(capHi*capHi+4.);
'''
assert source.count(extra) == 1
restored = source.replace(extra, '').replace(
    'if(cap)waveSlope=(1.-cwLo)*waveSlope+cwHi*(k*crosswise+.6*meridian)+2.*capSlope;',
    'if(cap)waveSlope=max(waveSlope,k*crosswise+.6*meridian)+2.*capSlope;')
assert restored == (HERE/'continuum-v27-candidate.js').read_text()
assert 'for(int i=0;i<2048;i++)' in source and 'if(i>=1536&&high<.5)break;' in source
assert 'min(p.z+27.5,0.)' in source
amplitude_sum = 1.18+.4+.28+.30+.15+.07
assert amplitude_sum < 2.385 and 7-2.385 >= 4
assert (.30*6+.15*13+.07*28)*math.exp(-.5) < 3.47

assert (HERE/'continuum.js').read_bytes() == (HERE/'continuum-v25.js').read_bytes()
assert (HERE/'trip.js').read_bytes() == (HERE/'trip-v16.js').read_bytes()
assert render_signature() == previous['render_signature']
for name in ['continuum.js','trip.js','fidelity-grades.json','realism-grades.json','fidelity-results.json','fidelity-data.js']:
    assert digest(HERE/name) == previous['sha256'][name]
for name in ['latest.png','visual-chrysanthemum.png']:
    assert digest(HERE/name) == previous['sha256']['accessibility-chrysanthemum-v25.png']
assert digest(HERE/'visual-chrysanthemum.json') == previous['sha256']['accessibility-chrysanthemum-v25.json']
assert not read('continuum-v25-gpu-check.json')['passed']

files = ['field_centre_v27.py', 'check_centre_candidate_v27r2.py', 'probe-numeric-candidate-v27.log',
         'numeric-candidate-v26-integrity.json', 'verification-continuum-v25.json']
for version in ['v27','v27r2']:
    files += [f'build_centre_candidate_{version}.py', f'continuum-{version}-candidate.js',
              f'gpu_probe_{version}_candidate.html', f'probe_numeric_candidate_{version}.py',
              f'build-centre-candidate-{version}.log', f'numeric-candidate-{version}-raw.json',
              f'numeric-candidate-{version}-check.json']
    subprocess.run(['node','--check',str(HERE/f'continuum-{version}-candidate.js')],check=True)
files += ['probe-numeric-candidate-v27-r2.log','probe-numeric-candidate-v27r2.log']
for name in files:
    if name.endswith('.py'):
        py_compile.compile(str(HERE/name),doraise=True)
pixel = 2*math.tan(math.radians(34))/800
out = {
    'integrity_passed': True, 'candidate_numerical_passed': True,
    'live_unchanged': True, 'display_unchanged': True, 'ledgers_unchanged': True,
    'overall_passed': False, 'render_signature': render_signature(),
    'geometry': 'v27 adds three crossed Cartesian cap octave bands blended with angular side folds, amplitudes .30/.15/.07, frequencies 1.3/2.9/6.1. Gaussian scale 6/13/28 replaces 30/64/130. Axis pigment smoothly removes angular colour convergence. v27r2 changes only interval bounds, not this geometry or shading.',
    'clearance': {'displacement_max': amplitude_sum, 'envelope_padding': 2.385,
                  'minimum_before_cap': 7-2.385, 'cap_start_z': -27.5, 'walk_exit_z': -22},
    'bound_derivation': 'For the next .4 world units, |cap| is bounded by capLo/capHi; cw=s^2/(s^2+4) is monotone. The blend derivative is bounded by (1-cwLo)*sideSlope+cwHi*crossedSlope+2*capSlope. CrossedSlope <= k*(|rd.x|+|rd.y|)+.6*meridian. Gaussian spatial derivative sum <3.47*pixelScale. Existing base-field bounds retained.',
    'filter_weights_at_distance_50_height_800': {
        'old': [math.exp(-.5*(50*pixel*f)**2) for f in [30,64,130]],
        'new': [math.exp(-.5*(50*pixel*f)**2) for f in [6,13,28]]},
    'sample_maxima': {k:max(c[k] for c in passed['cases']) for k in
                      ['misses','max_iterations','max_gradient_error','max_bound_ratio','max_field_cpu_gpu_difference']},
    'max_first_root_difference': passed['max_reference_difference'],
    'limitations': 'No fresh image, temporal grade, aliasing assessment, full-resolution performance or real-control acceptance. Filters are approximate, not local Nyquist proof. 38,160 sampled rays and 360 sign-crossing references are not universal convergence/tangency proof. Live v25 still GAME with failed coverage/numerics/45s exit. Preserve v27 failed budget and initial missing-numpy launch.',
    'sha256': {name:digest(HERE/name) for name in files}
}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['integrity_passed','candidate_numerical_passed','live_unchanged','overall_passed','sample_maxima','filter_weights_at_distance_50_height_800']}))
