"""One-shot evidence integrity check; failed numerical/physical/visual gates stay failed."""
import json
import py_compile
import subprocess
from pathlib import Path
from fidelity import digest,render_signature

HERE=Path(__file__).resolve().parent
OUT=HERE/'redirect4-v25-check.json'
assert not OUT.exists()
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8-sig'))
def run(args,log):
    result=subprocess.run(args,cwd=HERE.parent,capture_output=True,text=True)
    (HERE/log).write_text(result.stdout+result.stderr)
    return result.returncode
assert (HERE/'continuum.js').read_bytes()==(HERE/'continuum-v25.js').read_bytes()
assert (HERE/'trip.js').read_bytes()==(HERE/'trip-v16.js').read_bytes()
assert run(['node','--check','world/continuum.js'],'syntax-v25.log')==0
assert run(['python3','world/check_realism.py'],'realism-gate-v25.log')==0
for name in ['build_continuum_v25.py','probe_continuum_v25.py','review_chrysanthemum_v25.py','verify_continuum_v25.py','check_review_v25.py']:
    py_compile.compile(str(HERE/name),doraise=True)
images,receipts=set(),set()
def verify(value):
    if isinstance(value,dict):
        if value.get('file','').endswith('.png') and value.get('sha256'):
            p=HERE/value['file'];assert digest(p)==value['sha256'];images.add(p.name)
            if value.get('receipt_sha256'):
                assert digest(p.with_suffix('.json'))==value['receipt_sha256'];receipts.add(p.with_suffix('.json').name)
        for child in value.values():verify(child)
    elif isinstance(value,list):
        for child in value:verify(child)
for name in ['fidelity-grades.json','realism-grades.json']:verify(read(name))
signature=render_signature();bundle=read('fidelity-results.json')
assert bundle['render_signature']==signature and not bundle['passed']
target=next(t for t in bundle['targets'] if t['id']=='chrysanthemum')
assert not target['passed'] and target['coverage']==.84722
assert target['blockers']==['Top ten contains ABSENT or UNREVIEWED']
assert target['passage_audit']['included_reports']==50 and target['passage_audit']['excluded_reports']==20
assert 'overall: False' in (HERE/'fidelity-v25-review.log').read_text()
assert read('realism-grades.json')['targets']['chrysanthemum']['grade']=='GAME'
names=['realism-chrysanthemum-v25','realism-chrysanthemum-v25-motion','realism-chrysanthemum-close-v25','realism-chrysanthemum-close-v25-motion','accessibility-chrysanthemum-v25']
for name in names:
    r=read(name+'.json');d=r['capture_diagnostics']
    assert r['render_signature']==signature and r['capture_sha256']==digest(HERE/(name+'.png'))
    assert not r['errors'] and d['detail']=='high' and d['paused'] and not d['renderPending']
    assert d['animTime']==d['renderedAnimTime'] and not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes']==0
access=read('accessibility-chrysanthemum-v25.json')
assert len(access['checks'])==6
traces=sorted(HERE.glob('accessibility-chrysanthemum-v25-*-trace.json'))
assert len(traces)==4
gpu=read('continuum-v25-gpu-check.json');physical=read('verification-continuum-v25.json')
assert not gpu['passed'] and not physical['passed'] and physical['exit_walk_timeout_ms']==45000
assert sum(c['misses'] for c in gpu['cases'])==0
assert max(c['max_field_cpu_gpu_difference'] for c in gpu['cases'])>.001
assert len(physical['checks'])==3 and physical['failure_diagnostics']['stage']=='chrysanthemum'
assert digest(HERE/'latest.png')==digest(HERE/'accessibility-chrysanthemum-v25.png')
assert digest(HERE/'visual-chrysanthemum.png')==digest(HERE/'accessibility-chrysanthemum-v25.png')
assert digest(HERE/'visual-chrysanthemum.json')==digest(HERE/'accessibility-chrysanthemum-v25.json')
files=['continuum.js','continuum-v25.js','trip.js','trip-v16.js','fidelity-grades.json','realism-grades.json',
       'fidelity-results.json','fidelity-data.js','build_continuum_v25.py','build-continuum-v25.log',
       'probe_continuum_v25.py','gpu_probe_v25.html','continuum-v25-gpu-check.json','continuum-v25-gpu-raw.json',
       'continuum-v25-numerical-findings.json','probe-continuum-v25-initial-failure.log','probe-continuum-v25-r2.log',
       'review_chrysanthemum_v25.py','review-chrysanthemum-v25.log','fidelity-v25-review.log',
       'verify_continuum_v25.py','verification-continuum-v25.json','verification-continuum-v25.log',
       'render-chrysanthemum-v25.log','render-chrysanthemum-close-v25.log','render-accessibility-chrysanthemum-v25.log',
       'render_visual.py','syntax-v25.log','realism-gate-v25.log','check_review_v25.py']
files += [name+suffix for name in names for suffix in ['.png','.json']]+[p.name for p in traces]
out={'render_signature':signature,'integrity_passed':True,'node_syntax':'PASS','python_compilation':'PASS',
     'realism_gate_regression':'PASS','verified_ledger_pngs':len(images),'verified_ledger_receipts':len(receipts),
     'realism':'GAME','coverage':target['coverage'],'coverage_passed':False,'coverage_blockers':target['blockers'],
     'sources_included':50,'sources_excluded':20,'focused_stillness_sources_checks':access['checks'],
     'gpu_numerical_check_passed':False,'gpu_field_error_limit':.001,
     'gpu_max_field_difference':max(c['max_field_cpu_gpu_difference'] for c in gpu['cases']),
     'physical_exit_passed':False,'physical_exit_timeout_ms':45000,'physical_failure_position':physical['failure_diagnostics']['position'],
     'display':'accessibility-chrysanthemum-v25.png','overall_passed':False,
     'sha256':{name:digest(HERE/name) for name in files}}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sha256','focused_stillness_sources_checks']}))
