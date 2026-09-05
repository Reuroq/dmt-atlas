"""One-shot diagnosis receipts; experimental four-point agreement is not a runtime pass."""
import json
import py_compile
from pathlib import Path
from fidelity import digest,render_signature

HERE=Path(__file__).resolve().parent
OUT=HERE/'numeric-diagnosis-v25-check.json'
assert not OUT.exists()
def read(name):return json.loads((HERE/name).read_text())
baseline=read('diagnostic-numeric-v25.json')
failed=read('diagnostic-precisetrig-v25.json')
candidate=read('diagnostic-precisetrig-v25-r2.json')
previous=read('redirect4-v25-check.json')
assert not baseline['errors'] and not candidate['errors']
assert failed['errors'] and any('no matching overloaded function' in e for e in failed['errors'])
assert len(baseline['cases'])==len(candidate['cases'])==4
for b,c in zip(baseline['cases'],candidate['cases']):
    assert [b[k] for k in ['z','time','ray','point_float32']]==[c[k] for k in ['z','time','ray','point_float32']]
    assert abs(b['gpu_field_error']-b['cpu_angle_override_error'])<.000003
    assert c['gpu_field_error']<.00001 and c['gpu_field_error']<b['gpu_field_error']*.02
assert max(c['gpu_field_error'] for c in baseline['cases'])>.001
assert (HERE/'continuum.js').read_bytes()==(HERE/'continuum-v25.js').read_bytes()
assert (HERE/'trip.js').read_bytes()==(HERE/'trip-v16.js').read_bytes()
assert render_signature()==previous['render_signature']
for name in ['continuum.js','trip.js','fidelity-grades.json','realism-grades.json','fidelity-results.json','fidelity-data.js']:
    assert digest(HERE/name)==previous['sha256'][name]
for name in ['latest.png','visual-chrysanthemum.png']:
    assert digest(HERE/name)==previous['sha256']['accessibility-chrysanthemum-v25.png']
assert digest(HERE/'visual-chrysanthemum.json')==previous['sha256']['accessibility-chrysanthemum-v25.json']
files=['diagnostic_numeric_v25.html','diagnose_numeric_v25.py','diagnostic-numeric-v25.json','diagnostic-numeric-v25.log',
       'diagnostic_precisetrig_v25.html','diagnose_precisetrig_v25.py','diagnostic-precisetrig-v25.json','diagnostic-precisetrig-v25.log',
       'diagnostic_precisetrig_v25_r2.html','diagnose_precisetrig_v25_r2.py','diagnostic-precisetrig-v25-r2.json','diagnostic-precisetrig-v25-r2.log',
       'continuum-v25-numerical-findings.json','continuum-v25-gpu-check.json','check_numeric_diagnosis_v25.py']
for name in files:
    if name.endswith('.py'):py_compile.compile(str(HERE/name),doraise=True)
for item in [baseline,failed,candidate]:
    for name,sha in item['sha256'].items():assert digest(HERE/name)==sha
out={'integrity_passed':True,'runtime_unchanged':True,'render_signature':render_signature(),
     'baseline_max_fixed_point_field_error':max(c['gpu_field_error'] for c in baseline['cases']),
     'cpu_angle_override_max_field_error':max(c['cpu_angle_override_error'] for c in baseline['cases']),
     'polynomial_experiment_max_fixed_point_field_error':max(c['gpu_field_error'] for c in candidate['cases']),
     'conclusion':'At four saved worst points, replacing only atan does not remove discrepancy; replacing sin/cos with range-reduced degree13/12 polynomials reduces it below the original .001 scalar agreement limit. Built-in trigonometric evaluation contributes to the measured discrepancy. No new ray/root/gradient/visual/performance acceptance; runtime still v25 and numerical gate still FAIL.',
     'failed_initial_experiment':'Shader compile error: missing vec3 preciseCos overload in unreachable spectrum function. Returned pixels are invalid evidence; original HTML/Python/log/JSON retained.',
     'overall_passed':False,'sha256':{name:digest(HERE/name) for name in files}}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sha256','conclusion','failed_initial_experiment']}))
