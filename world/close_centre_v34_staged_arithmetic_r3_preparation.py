"""Saved-only static closure; update current display exactly once. No browser."""
import hashlib
import json
import os
import probe_centre_v34_staged_arithmetic_r3 as p


def write(name, data):
    with (p.HERE / name).open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def main():
    p.gate(prepared=False)
    stem=p.PREFIX+'-static-once'
    receipt, launch=p.read(stem+'-exit.json'),p.read(stem+'-launch.json')
    assert receipt['launcher_error'] is None and type(receipt['actual_exit']) is int
    assert receipt['log_sha256']==p.digest(stem+'.log') and receipt['launch_sha256']==p.digest(stem+'-launch.json')
    assert launch['script_sha256']==p.digest(launch['script'])
    assert launch['launcher_sha256']==p.digest('run_centre_v34_staged_arithmetic_r3_once.py')
    assert launch['freeze_sha256']==p.digest(p.PREFIX+'-freeze.json')
    assert p.read(p.PREFIX+'-close-once-launch.json')['child_pid_parent']==os.getppid()
    assert not any(p.HERE.glob(p.PREFIX+'-event-*'))
    assert not (p.HERE/(p.PREFIX+'-runtime-once-launch.json')).exists()
    passed=receipt['actual_exit']==0
    node_results=[]
    for path in sorted(p.HERE.glob(p.PREFIX+'-node-*-exit.json')):
        name=path.name[:-len('-exit.json')]
        r,l=p.read(path.name),p.read(name+'-launch.json')
        assert l['command_sha256']==hashlib.sha256(json.dumps(l['command'],separators=(',',':')).encode()).hexdigest()
        assert r['launch_sha256']==p.digest(name+'-launch.json')
        assert r['source_sha256']==l['source_sha256']==p.digest(l['source'])
        assert r['stdout_sha256']==p.digest(name+'-stdout.log') and r['stderr_sha256']==p.digest(name+'-stderr.log')
        node_results.append({'stage':name[len(p.PREFIX+'-node-'):], 'actual_exit':r['actual_exit'],
                             'timed_out':r['timed_out'],'launcher_error':r['launcher_error']})
    if passed:
        p.receipt('static')
        check=p.read(p.PREFIX+'-static.json'); extra=p.read(p.PREFIX+'-successor-checks.json')
        assert check['passed'] and not check['runtime_run'] and check['integer_oracle_components']==1024 and len(check['plan'])==126
        assert extra['passed'] and len(extra['resource_cases'])==23 and extra['transport_components']==1024
        assert len(node_results)==35 and all(r['actual_exit']==0 and not r['timed_out'] and r['launcher_error'] is None for r in node_results)
    else:
        assert not (p.HERE/(p.PREFIX+'-static.json')).exists()
    grade='PASS' if passed else 'FAIL'
    manifest=p.PREFIX+('-preparation-integrity.json' if passed else '-preparation-failure-integrity.json')
    assert not (p.HERE/manifest).exists()
    p.save(p.PREFIX+'-close-started.json',{'static_passed':passed,'static_actual_exit':receipt['actual_exit'],'saved_only':True})
    next_work=(
        'Verify centre-v34-staged-arithmetic-r3-preparation-integrity.json files/protected/display and static/close '
        'actual-exit0 receipts including the closure manifest hash. In a separate bounded phase run '
        'python3 -B world/run_centre_v34_staged_arithmetic_r3_once.py runtime ONCE foreground; wait for actual exit '
        'before reading results. Close saved full readbacks, strict source/request/CPU uint32 bits, all 126 stages '
        'or the exact stop, resource identities/disposal attempts/errors, browser lifecycle and chained events '
        'before interpreting the unchanged both-leaf literal/uniform support criterion. No field/roots/cost/capture '
        'or acceptance until subsequent justified gates; do not replay r2 or any historical test.'
        if passed else
        'Verify centre-v34-staged-arithmetic-r3-preparation-failure-integrity.json and static/close receipt hashes. '
        'Inspect only saved failure evidence. Never edit/replay frozen r3; prepare a distinct correction. '
        'Browser arithmetic blocked until a genuinely passing static closure.')
    summary=(f'Distinct staged arithmetic r3 preparation CLOSED static {grade}, actual exit{receipt["actual_exit"]}; runtime NOT RUN. '
        + ('Uint32 ingress uses original texture bits through Uint32Array/Float32Array; exact source/request/CPU checks reject '
           'zero-sign, type and bit mutations. Immediate identity registration covers renderer/target/texture/geometry/material; '
           'no implicit Mesh default material. Cleanup attempts every registered identity once, renderer last, continuing '
           'after disposal exceptions and dirty/throwing GL drains. 23 actual-HTML mock cases and 35 durable Node stages pass. '
           'Original shader/126-stage plan, rational 1024-component oracle and both-leaf exact support criterion preserved. '
           'Full result precedes assessment; resource identity loss is fatal. Mock evidence is not GPU arithmetic or cleanup proof. '
           if passed else 'Frozen static failure preserved; no preparation pass or runtime permission. ')
        + 'Frozen r2 and original exact-jet/716-of-720 failures remain. No candidate promotion, roots/cost/capture/acceptance. '
        'latest unchanged inspected REJECTED GAME v33r6; all19 unfinished.')
    review_name=p.PREFIX+'-preparation-review.md'
    p.save(p.PREFIX+'-preparation-review.json',{'summary':summary,'next_work':next_work,'node_results':node_results,
           'static_passed':passed,'runtime_run':False,'synthetic_uniform_candidate_supported':False,'capture_permitted':False,'new_images':0})
    write(review_name,('# Arithmetic r3 preparation — '+grade+'; browser NOT RUN\n\n'+summary+'\n\n'
         'All changes are recorded in the source-delta manifest against frozen r2; no historical sources or receipts edited. '
         'Source freeze includes the current transport closure/receipt, original input/shader dependencies and new scripts. '
         'Node source, command, stdout/stderr and actual-exit hashes are verified saved-only. '
         'The historical missing-API reproduction was not replayed. Cleanup can still report fatal GL state even when all '
         'disposals were attempted; errors are not excused as a clean runtime.\n\n## Next bounded phase\n\n'+next_work+'\n').encode())
    history=p.read(p.HISTORY)
    notes=(p.HERE/'NOTES.md').read_bytes(); assert notes.startswith(b'\xef\xbb\xbf')
    head,old_next=notes.decode('utf-8-sig').split('## Exact next bounded work\n')
    assert 'centre-v34-transport-runtime-integrity.json' in old_next
    head='# Active: REDIRECT4 — staged arithmetic r3 preparation CLOSED static '+grade+'; runtime NOT RUN\n'+head.split('\n',1)[1]
    head+='## Distinct staged arithmetic r3 preparation CLOSED — static '+grade+'\n- '+summary+'\n'
    head+='- Verified transport1008 evidence/16protected/4display and closure receipt hashes. Prior display archived; NOTES once/BOM retained.\n\n'
    readme=(p.HERE/'README.md').read_text()
    anchors=[line for line in readme.splitlines() if line.startswith('Distinct [transport-only runtime]')]
    assert len(anchors)==1
    assert 'transport runtime CLOSED actual exit0' in (p.HERE/'status.txt').read_text()
    replacement=('Distinct [staged arithmetic r3 preparation]('+review_name+') is **CLOSED static '+grade+'; runtime NOT RUN**. '
                 'Strict uint32 transport and identity-based exception-continuing cleanup prepared. '
                 'Original shader/oracle/support criterion retained; no GPU arithmetic, visual or acceptance claim.')
    updates={'NOTES.md':b'\xef\xbb\xbf'+(head+'## Exact next bounded work\n'+next_work+'\n').encode(),
             'README.md':readme.replace(anchors[0],replacement,1).encode(),'status.txt':(summary+' '+next_work+'\n').encode()}
    archives={}
    for name in updates:
        archive=name+'-before-'+p.PREFIX+'-preparation'
        write(archive,(p.HERE/name).read_bytes()); archives[archive]=p.digest(archive)
    for name,data in updates.items():
        with (p.HERE/name).open('wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
    files=dict(history['files']); files[p.HISTORY]=p.digest(p.HISTORY)
    files.update(p.read(p.PREFIX+'-freeze.json')['sources']); files.update(archives)
    for path in p.HERE.glob(p.PREFIX+'-*'):
        if path.name in (p.PREFIX+'-close-once.log',p.PREFIX+'-close-once-exit.json'): continue
        files[path.name]=p.digest(path.name)
    p.verify(files);p.verify(history['protected'])
    assert p.digest('latest.png')==history['display']['latest.png']
    display={n:p.digest(n) for n in history['display']}
    p.save(manifest,{'files':files,'protected':history['protected'],'display':display,'prior_display':history['display'],
           'archived_display':archives,'static_passed':passed,'static_actual_exit':receipt['actual_exit'],
           'runtime_run':False,'numeric_passed':False,'synthetic_uniform_candidate_supported':False,
           'capture_permitted':False,'new_images':0})
    for key in ('files','protected','display'):p.verify(p.read(manifest)[key])
    print('R3 static preparation closure:',grade,len(files),'evidence hashes; runtime NOT RUN',flush=True)


if __name__=='__main__': main()
