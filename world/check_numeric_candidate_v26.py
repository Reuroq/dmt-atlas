"""One-shot candidate evidence integrity; no runtime or visual promotion."""
import json
import py_compile
import re
import subprocess
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent
OUT = HERE/'numeric-candidate-v26-integrity.json'
assert not OUT.exists()
def read(name): return json.loads((HERE/name).read_text())
result = read('numeric-candidate-v26-check.json')
previous = read('redirect4-v25-check.json')
diagnosis = read('numeric-diagnosis-v25-check.json')
assert result['passed'] and not result['errors']
assert result['limits'] == {'gradient':.005,'bound_ratio':1.001,'scalar':.001,'root':.03}
assert result['rays']==38160 and result['reference_rays']==360
assert len(result['cases'])==24
assert sum(r['axis'] for s in result['cases'] for r in s['references'])==16
assert {s['time'] for s in result['cases']}=={4,8,221,900}
for name,sha in result['files'].items(): assert digest(HERE/name)==sha
for name,sha in diagnosis['sha256'].items(): assert digest(HERE/name)==sha
assert not read('continuum-v25-gpu-check.json')['passed']
source = (HERE/'continuum-v25.js').read_text()
helper = (HERE/'diagnostic_precisetrig_v25_r2.html').read_text().split('const precise=`',1)[1].split('`;',1)[0]
expected = re.sub(r'\bsin\(', 'preciseSin(', source)
expected = re.sub(r'\bcos\(', 'preciseCos(', expected).replace('   mat2 rot(',helper+'   mat2 rot(')
assert (HERE/'continuum-v26-candidate.js').read_text()==expected
assert (HERE/'continuum.js').read_bytes()==(HERE/'continuum-v25.js').read_bytes()
assert (HERE/'trip.js').read_bytes()==(HERE/'trip-v16.js').read_bytes()
assert render_signature()==previous['render_signature']
for name in ['continuum.js','trip.js','fidelity-grades.json','realism-grades.json','fidelity-results.json','fidelity-data.js']:
    assert digest(HERE/name)==previous['sha256'][name]
for name in ['latest.png','visual-chrysanthemum.png']:
    assert digest(HERE/name)==previous['sha256']['accessibility-chrysanthemum-v25.png']
assert digest(HERE/'visual-chrysanthemum.json')==previous['sha256']['accessibility-chrysanthemum-v25.json']
subprocess.run(['node','--check',str(HERE/'continuum-v26-candidate.js')],check=True)
files = ['build_numeric_candidate_v26.py','continuum-v26-candidate.js','gpu_probe_v26_candidate.html',
         'probe_numeric_candidate_v26.py','check_numeric_candidate_v26.py','build-numeric-candidate-v26.log',
         'probe-numeric-candidate-v26.log','numeric-candidate-v26-raw.json','numeric-candidate-v26-check.json',
         'numeric-diagnosis-v25-check.json']
for name in files:
    if name.endswith('.py'): py_compile.compile(str(HERE/name),doraise=True)
out = {'integrity_passed':True,'candidate_numerical_passed':True,'runtime_unchanged':True,
       'render_signature':render_signature(),'display_unchanged':True,'ledgers_unchanged':True,
       'limits':'Same scalar .001, gradient .005, bound ratio 1.001 and first-root .03 limits as v25. No tolerance relaxation.',
       'limitations':'24 sampled states, not universal convergence or accuracy at arbitrary animation times. Three low-resolution GPU readbacks per case took 7.31s total including first compilation; not full-resolution runtime performance evidence. Exact-axis samples do not prove all cap/rim rays. Candidate has no fresh journey captures and is not deployed.',
       'overall_passed':False,'sha256':{name:digest(HERE/name) for name in files}}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sha256','limits','limitations']}))
