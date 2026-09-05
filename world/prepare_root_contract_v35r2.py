"""Freeze/check/close the root evidence contract; not full runtime preparation."""
import ast
import hashlib
import json
import os
import sys
from pathlib import Path
import v35r2_preparation as prior_support

HERE=Path(__file__).resolve().parent
PREFIX='centre-v35r2-root-contract'
HISTORY='centre-v35r2-fixture-integrity.json'
SOURCES=['root_reference_contract_v35r2.py','check_root_reference_contract_v35r2.py',
         'prepare_root_contract_v35r2.py','run_root_contract_v35r2_once.py',PREFIX+'-design.md']


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE/name).read_text())


def write(name,data):
    with (HERE/name).open('xb') as stream:
        stream.write(data if isinstance(data,bytes) else data.encode());stream.flush();os.fsync(stream.fileno())


def save(name,value):
    write(name,json.dumps(value,indent=2)+'\n')


def verify(group):
    for name,want in group.items():assert digest(name)==want,name


def prior(display=True):
    prior_support.closed()
    manifest=read(HISTORY)
    for key in ('files','protected')+(('display',) if display else ()):verify(manifest[key])
    assert manifest['static_passed'] and not manifest['numerical_run']
    return manifest


def gate():
    freeze=read(PREFIX+'-freeze.json')
    assert freeze['history_sha256']==digest(HISTORY)
    verify(freeze['sources']);prior()


def receipt(label):
    stem=PREFIX+'-'+label+'-once'
    r,launch=read(stem+'-exit.json'),read(stem+'-launch.json')
    assert r['actual_exit']==0 and r['launcher_error'] is None,label
    assert r['log_sha256']==digest(stem+'.log') and r['launch_sha256']==digest(stem+'-launch.json')
    assert launch['script_sha256']==digest('prepare_root_contract_v35r2.py')
    assert launch['launcher_sha256']==digest('run_root_contract_v35r2_once.py')
    assert launch['history_sha256']==digest(HISTORY)
    if label!='freeze':assert launch['freeze_sha256']==digest(PREFIX+'-freeze.json')


def freeze():
    prior()
    for name in SOURCES:
        if name.endswith('.py'):ast.parse((HERE/name).read_text(),filename=name)
    save(PREFIX+'-freeze.json',{'sources':{n:digest(n) for n in SOURCES},
        'history_sha256':digest(HISTORY),'runtime_fixtures_complete':False,'field_runtime_permitted':False})
    print('Root evidence contract frozen; no runtime fixtures or field execution')


def check():
    gate();receipt('freeze')
    from check_root_reference_contract_v35r2 import check as contract_check
    result=contract_check()
    gate()
    save(PREFIX+'-static.json',result)
    print('Root contract static PASS:28 ray/6 coverage rejection cases;720 synthetic records; no field samples')


def close():
    gate();receipt('freeze');receipt('check');history=prior()
    result=read(PREFIX+'-static.json')
    assert result['static_passed'] and not result['numeric_passed']
    assert result['field_samples']==result['browser_runs']==0
    for pattern in ('numeric-candidate-v35r2-*.json','diagnostic-centre-v35r2*',
                    'run-centre-v35r2-*-once-launch.json'):
        assert not list(HERE.glob(pattern)),pattern
    next_work=('Verify centre-v35r2-root-contract-integrity.json files/protected/display and close-once '
        'actual-exit0 receipt hashes. Root contract design/core is static PASS, NOT complete runtime '
        'fixtures. Implement DISTINCT versioned numerical/local/global/combination runners and '
        'foreground launchers per centre-v35r2-root-contract-design.md; no candidate edit. '
        'Preserve old .003 scans/verdicts, all720 identities, every non-root predicate, add explicit '
        'exact cheap/full comparison (legacy code is <.00001), and retain unchanged global '
        'left-first algorithm/tolerances. Prove AST/source equivalence, strict stage eligibility, '
        'bijective joins, durable-before-assessment, transport and failure/partial/replay contracts. '
        'Freeze and statically close the full integration before ANY field runtime. No historical '
        'replay, promotion, tolerance relaxation or cost/capture/acceptance bypass.')
    status=('Root-certificate contract design/core CLOSED static PASS:28 ray/6 coverage rejection '
        'cases,720 synthetic records; no field/browser runtime. Original .003 scan failure remains '
        'separate from proposed local-bracket plus independent global evidence. AST anchors bind '
        'all non-root predicates and global recursion. Legacy cheap/full gate is <.00001; successor '
        'must also require exact equality. Full runtime integration NOT PREPARED. Next implement '
        'distinct runners/launchers and close their static gates before field runtime. latest.png '
        'unchanged inspected REJECTED GAME v33r6 entry; live/defaults/ledgers unchanged. '
        'All19/source/coverage/route/full acceptance unfinished; no promotion or realism pass.')
    archives={}
    for name in ('NOTES.md','README.md','status.txt'):
        archive=name+'-before-'+PREFIX;write(archive,(HERE/name).read_bytes());archives[archive]=digest(archive)
    notes=(HERE/'NOTES.md').read_text(encoding='utf-8-sig')
    assert notes.count('## Exact next bounded work')==1
    notes=notes[:notes.index('## Exact next bounded work')]
    notes=notes.replace(notes.splitlines()[0],'# Active: REDIRECT4 — root contract design/core CLOSED static PASS',1)
    notes+='''## Additive root-contract design/core CLOSED — static PASS, integration NOT PREPARED
- Verified v35r2 preparation1836 evidence/16protected/4display and actual-exit0 closure receipts. Frozen centre-v35r2-root-contract-design.md explicitly separates legacy .003 scan verdict, all non-root gates, all720 local profiles/brackets, unchanged independent global first-root algorithm and final evidence combination. No nearest-root substitution or forged legacy PASS; local correspondence alone is not earliest-root proof.
- New oracle-free root_reference_contract_v35r2.py validates complete161point local grids/all entering+exiting brackets/24step histories, global strict <=1e-7 positive-negative bracket/unresolved/difference gates, original found-reference requirements and bijective720 identities. Numerical PASS is always false: external field/provenance/exact-jet/global/runtime gates remain mandatory. Local sampled zeros are unresolved, never permission for later-root selection.
- Frozen foreground static actual exit0:28ray/6coverage adversarial rejection cases,720synthetic records and narrow crossing pair missed by coarse endpoints PASS. AST-only anchors reconstruct every original non-root conjunct exactly, enumerate48cases/75996rays/720keys and bind unchanged global recursion. No field module imported, historical scan replayed, browser or candidate samples run.
- Audit correction: frozen original cheap/full predicate is <.00001, despite earlier notes shorthand claiming exact. New integration must preserve that verdict AND require separate exact binary32 cheap/full equality; no widening or retroactive gate credit. Full numerical/local/global/combination runners, launchers and their static integration are NOT prepared. Candidate and every historical failure unchanged.
- Contract integrity binds historical/source/static/receipt/protected/current display; NOTES once/BOM retained, prior display archived. No root proof,cost,capture,acceptance,new image/inspection or promotion. latest unchanged inspected REJECTED GAME v33r6;all19 unfinished.

## Exact next bounded work
'''+next_work+'\n'
    (HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    (HERE/'status.txt').write_text(status+'\n')
    readme=(HERE/'README.md').read_text()
    readme+='\n[Additive root-contract design/core](centre-v35r2-root-contract-design.md) is **CLOSED static PASS; runtime integration NOT PREPARED**. Local brackets and all720 identity checks cannot replace independent global first-root evidence. Original scan failures remain separate. Static source audit also requires an explicit exact cheap/full gate in the successor; legacy predicate is <.00001. No new render, numerical acceptance or promotion.\n'
    (HERE/'README.md').write_text(readme)
    prior(display=False);verify(read(PREFIX+'-freeze.json')['sources'])
    assert digest('latest.png')==history['display']['latest.png']
    files=dict(history['files']);files[HISTORY]=digest(HISTORY)
    for label in ('freeze','check'):
        for suffix in ('-launch.json','-exit.json','.log'):
            name=PREFIX+'-'+label+'-once'+suffix;files[name]=digest(name)
    for suffix in ('-launch.json','-exit.json','.log'):
        name='centre-v35r2-close-once'+suffix;files[name]=digest(name)
    files.update(read(PREFIX+'-freeze.json')['sources']);files.update(archives)
    for name in (PREFIX+'-freeze.json',PREFIX+'-static.json',PREFIX+'-close-once-launch.json'):files[name]=digest(name)
    save(PREFIX+'-integrity.json',{'files':files,'protected':history['protected'],
        'display':{n:digest(n) for n in history['display']},'archived_display':archives,
        'static_passed':True,'runtime_fixtures_complete':False,'field_runtime_permitted':False,
        'numeric_passed':False,'first_root_certified':False,'capture_permitted':False,'new_images':0,'next':next_work})
    print('Saved-only root contract design/core CLOSED; full integration remains unprepared')


if __name__=='__main__':
    {'freeze':freeze,'check':check,'close':close}[sys.argv[1]]()
