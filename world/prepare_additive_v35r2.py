"""Static build/freeze/check/close only. Never starts a numerical stage."""
import ast
import json
import sys
import additive_runtime_v35r2 as r

SOURCES=['additive_runtime_v35r2.py','additive_evidence_v35r2.py','build_additive_v35r2.py',
    'run_additive_v35r2_once.py','local_additive_v35r2.py','combine_additive_v35r2.py',
    'numeric_additive_v35r2.py','bounds_additive_v35r2.py','global_additive_v35r2.py',
    'gpu_probe_additive_v35r2_candidate.html','gpu_probe_additive_v35r2_leaves.html',
    'check_additive_v35r2.py','prepare_additive_v35r2.py','run_additive_static_v35r2_once.py',
    r.PREFIX+'-derivation.json',r.PREFIX+'-design.md']


def prior(display=True):
    history=r.read(r.HISTORY)
    for group in ('files','protected')+(('display',) if display else ()):
        r.verify(history[group])
    r.require(history['static_passed'] is True and history['field_runtime_permitted'] is False)
    stem='centre-v35r2-root-contract-close-once'
    receipt,launch=r.read(stem+'-exit.json'),r.read(stem+'-launch.json')
    r.require(type(receipt['actual_exit']) is int and receipt['actual_exit']==0 and receipt['launcher_error'] is None)
    r.require(receipt['manifest_sha256']==r.digest(r.HISTORY))
    r.require(receipt['launch_sha256']==r.digest(stem+'-launch.json') and receipt['log_sha256']==r.digest(stem+'.log'))
    r.require(launch['script_sha256']==r.digest('prepare_root_contract_v35r2.py'))
    r.require(launch['launcher_sha256']==r.digest('run_root_contract_v35r2_once.py'))
    return history


def receipt(label):
    stem=r.PREFIX+'-'+label+'-once'
    result,launch=r.read(stem+'-exit.json'),r.read(stem+'-launch.json')
    r.require(type(result['actual_exit']) is int and result['actual_exit']==0 and result['launcher_error'] is None)
    r.require(result['log_sha256']==r.digest(stem+'.log') and result['launch_sha256']==r.digest(stem+'-launch.json'))
    r.require(launch['script_sha256']==r.digest('prepare_additive_v35r2.py'))
    r.require(launch['launcher_sha256']==r.digest('run_additive_static_v35r2_once.py'))
    r.require(launch['history_sha256']==r.digest(r.HISTORY))
    r.require(launch['builder_sha256']==r.digest('build_additive_v35r2.py'))
    if label in ('check','close'):
        r.require(launch['freeze_sha256']==r.digest(r.PREFIX+'-freeze.json'))


def gate():
    prior();frozen=r.read(r.PREFIX+'-freeze.json')
    r.require(frozen['history_sha256']==r.digest(r.HISTORY))
    r.verify(frozen['sources'])


def build():
    prior()
    from build_additive_v35r2 import build as derive
    derive()


def freeze():
    prior();receipt('build')
    for name in SOURCES:
        if name.endswith('.py'):ast.parse((r.HERE/name).read_text(),filename=name)
    r.atomic_json(r.PREFIX+'-freeze.json',{'sources':{n:r.digest(n) for n in SOURCES},
        'history_sha256':r.digest(r.HISTORY),'field_runtime_permitted':False})
    print('Integration source suite frozen; no field runtime')


def check():
    gate();receipt('build');receipt('freeze')
    from check_additive_v35r2 import check as run_checks
    result=run_checks()
    gate()
    r.atomic_json(r.PREFIX+'-static.json',result)
    print('Full integration static PASS; no field/browser execution')


def close():
    gate()
    for label in ('build','freeze','check'):receipt(label)
    history=prior();result=r.read(r.PREFIX+'-static.json')
    r.require(result['static_passed'] is True and result['numeric_passed'] is False)
    r.require(result['field_samples']==result['browser_runs']==0)
    r.require(not any(r.directory(stage).exists() for stage in r.STAGES))
    archives={}
    for name in ('NOTES.md','README.md','status.txt'):
        archive=name+'-before-'+r.PREFIX
        with (r.HERE/archive).open('xb') as stream:stream.write((r.HERE/name).read_bytes())
        archives[archive]=r.digest(archive)
    next_work=('Verify centre-v35r2-additive-integrity.json and close-once actual-exit0 receipt hashes. '
        'The distinct bounds/numerical/local/global/combination integration is statically CLOSED, with no '
        'field stage attempted. Begin only the new foreground run_additive_v35r2_once.py bounds stage, '
        'then inspect its durable actual exit/result before numerical. No old launcher, historical replay, '
        'tolerance change, forged legacy PASS or nearest-root selection. A failed/partial stage blocks '
        'all successors and cannot replay. Cost/capture successor integration remains unprepared and '
        'blocked even after a future combination PASS. All19/source/coverage/route/full acceptance remain unfinished.')
    notes=(r.HERE/'NOTES.md').read_text(encoding='utf-8-sig')
    r.require(notes.count('## Exact next bounded work')==1)
    notes=notes[:notes.index('## Exact next bounded work')]
    notes=notes.replace(notes.splitlines()[0],'# Active: REDIRECT4 — additive integration CLOSED static PASS',1)
    notes+='''## Additive numerical integration CLOSED — static PASS, no field runtime
- Verified root-contract1856 evidence/16protected/4display and close-once hashes including manifest. Added distinct bounds/numerical/local/global/combination runners, Uint32 readback wrappers and exclusive foreground launchers. Candidate, original .003 scans/predicates/search sources, all historical failures and latest remain unchanged.
- Full derivation reversal plus original scan/24step and whole independent domain/exclusion/left-first AST equivalence. All original non-root conjuncts preserved; legacy cheap/full<.00001 remains separate from new exact binary32 cheap/full and saved expanded/CSG/aperture/gradient replay. All48cases/75996rays/720keys are independently enumerated and bijectively joined.
- New local runner retains all161 full/five-base/11leaf samples, all entering/exiting cells and24 full endpoint/midpoint transitions per ray; actual GPU point words separate from CPU-ray reconstruction. Sampled/midpoint zeros unresolved. Durable profiles precede assessment; saved CPU oracle replay mandatory. Global algorithm gets no local hints. Combination preserves missing legacy references and strict global/local correspondence, never nearest-root substitution.
- Frozen static source/transport/complete720join/all-conjunct negatives and actual foreground synthetic success/failure/partial/signal/late-exit/tamper/replay fixtures passed. Synthetic gate overrides are labelled; no field module imported, browser run or historical probe replayed. Runtime requires manifest plus actual-exit0 closure and every prerequisite inventory/exit; partial attempts cannot replay.
- This is integration preparation only, not numerical or global-root proof. New launchers unexecuted. Cost/capture successor integration NOT PREPARED; no source/coverage/route/realism/full acceptance credit or promotion. latest unchanged inspected REJECTED GAME v33r6; all19 unfinished. NOTES updated once/BOM retained, prior displays archived.

## Exact next bounded work
'''+next_work+'\n'
    (r.HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    (r.HERE/'status.txt').write_text('Additive numerical integration CLOSED static PASS; no field/browser runtime. Distinct bounds/numerical/local/global/combination runners retain original scans/predicates/search and add strict word/720key/local/global contracts. Next: verify closure then new bounds stage only. Cost/capture integration blocked; no promotion. latest unchanged inspected REJECTED GAME v33r6. All19/source/coverage/route/full acceptance unfinished.\n')
    readme=(r.HERE/'README.md').read_text()
    (r.HERE/'README.md').write_text(readme+'\n[Additive numerical integration](centre-v35r2-additive-design.md) is **CLOSED static PASS; no field runtime**. New exclusive stages preserve original scan failures and unchanged independent search, adding bit-exact transport and complete 720-ray evidence joins. No numerical, cost, capture or realism credit; all19 remain unfinished.\n')
    prior(display=False);r.verify(r.read(r.PREFIX+'-freeze.json')['sources'])
    r.require(r.digest('latest.png')==history['display']['latest.png'])
    files=dict(history['files']);files[r.HISTORY]=r.digest(r.HISTORY)
    files.update(r.read(r.PREFIX+'-freeze.json')['sources']);files.update(archives)
    for label in ('build','freeze','check'):
        for suffix in ('-launch.json','-exit.json','.log'):
            name=r.PREFIX+'-'+label+'-once'+suffix;files[name]=r.digest(name)
    for suffix in ('-launch.json','-exit.json','.log'):
        name='centre-v35r2-root-contract-close-once'+suffix;files[name]=r.digest(name)
    for path in sorted((r.HERE/(r.PREFIX+'-static-fixtures')).rglob('*')):
        if path.is_file():
            name=str(path.relative_to(r.HERE));files[name]=r.digest(name)
    for name in (r.PREFIX+'-freeze.json',r.PREFIX+'-static.json',r.PREFIX+'-close-once-launch.json'):
        files[name]=r.digest(name)
    r.atomic_json(r.MANIFEST,{'files':files,'protected':history['protected'],
        'display':{n:r.digest(n) for n in history['display']},'archived_display':archives,
        'static_passed':True,'runtime_fixtures_complete':True,'field_runtime_permitted':True,
        'numerical_run':False,'numeric_passed':False,'capture_permitted':False,'cost_permitted':False,
        'new_images':0,'next':next_work})
    print('Saved-only integration CLOSED; numerical field stages not attempted')


if __name__=='__main__':
    {'build':build,'freeze':freeze,'check':check,'close':close}[sys.argv[1]]()
