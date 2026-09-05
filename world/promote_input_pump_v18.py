"""Promote only the tested control repair; no visual or full-acceptance credit."""
import ast
import hashlib
import json
from pathlib import Path
from fidelity import render_signature

HERE=Path(__file__).resolve().parent
OUT=HERE/'input-pump-v18-promotion.json'
assert not OUT.exists() and not (HERE/'trip-v18.js').exists(), 'Preserve history'
def digest(n):
    return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
old=json.loads((HERE/'walk-clock-v17-integrity.json').read_text())
for n,h in old['protected'].items():
    assert digest(n)==h, n
for n,h in old['files'].items():
    assert digest(n)==h, n
focused=json.loads((HERE/'verification-input-pump-v18.json').read_text())
idle=json.loads((HERE/'verification-idle-pump-v18.json').read_text())
candidate=digest('trip-v18-candidate.js')
assert focused['passed'] and not focused['errors']
assert focused['candidate_sha256']==candidate
assert focused['exit_walk_timeout_ms']==45000 and focused['exit_wall_seconds']<45
assert -3.2<=focused['centre_return_x']<=0
assert idle['passed'] and len(idle['checks'])==8 and not idle['errors']
assert idle['trip_sha256']==candidate
names=['trace_lateral_v17.py','diagnostic-lateral-v17.js','diagnostic-lateral-v17.html','diagnostic-lateral-v17.json','trace-lateral-v17.log','build_input_pump_v18.py','trip-v18-candidate.js','input-pump-v18-candidate.html','verify_input_pump_v18.py','verification-input-pump-v18.json','verify-input-pump-v18.log','verify_idle_pump_v18.py','verification-idle-pump-v18.json','verify-idle-pump-v18.log',Path(__file__).name]
for n in names:
    if n.endswith('.py'):ast.parse((HERE/n).read_text())
out={'promoted':True,'full_acceptance_passed':False,'visual_regraded':False,
     'previous_render_signature':render_signature(),'previous_protected':old['protected'],
     'files':{n:digest(n) for n in names},'centre_return_x':focused['centre_return_x'],
     'exit_wall_seconds':focused['exit_wall_seconds'],
     'limits':'Focused isolated runtime tests bind exact candidate hash. Old visual/acceptance receipts become stale; no visual equivalence or hardware-GPU benchmark claim.'}
b=(HERE/'trip-v18-candidate.js').read_bytes()
(HERE/'trip-v18.js').write_bytes(b)
(HERE/'trip.js').write_bytes(b)
out['render_signature']=render_signature()
assert digest('trip.js')==digest('trip-v18.js')==candidate
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['promoted','centre_return_x','exit_wall_seconds','render_signature']}))
