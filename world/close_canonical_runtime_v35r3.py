"""Saved-only terminal closure; no field sampling, browser or stage replay."""
import json
import os
import canonical_runtime_v35r3 as r

PREFIX = 'centre-v35r3-canonical-runtime'


def inspect():
    history = r.fixture_gate()
    attempted = [s for s in r.STAGES if r.directory(s).exists()]
    r.require(attempted and attempted == list(r.STAGES[:len(attempted)]))
    stages, files, failed = [], {}, None
    for stage in attempted:
        r.require(failed is None, 'No attempt after failed predecessor')
        r.eligibility(stage)
        receipt = r.read(r.artifact(stage, 'exit.json'))
        r.require(receipt['files'] == r.inventory(stage, ('exit.json',)))
        launch = r.read(r.artifact(stage, 'launch.json'))
        r.require(launch['stage'] == stage)
        r.require(launch['manifest_sha256'] == r.digest(r.MANIFEST))
        r.require(launch['script_sha256'] == r.digest(r.SCRIPTS[stage]))
        r.require(launch['launcher_sha256'] == r.digest('run_canonical_v35r3_once.py'))
        r.require(launch['prerequisites'] == r.prerequisite_hashes(stage))
        ready = False
        try:
            r.stage_receipt(stage)
            ready = True
        except (AssertionError, KeyError, ValueError, TypeError, FileNotFoundError):
            failed = stage
        result_path = r.directory(stage)/'result.json'
        result = r.read(r.artifact(stage, 'result.json')) if result_path.exists() else {}
        item = {'stage': stage, 'actual_exit': receipt['actual_exit'],
                'launcher_error': receipt['launcher_error'], 'eligible_result': ready,
                'inventory_files': len(receipt['files'])}
        for key in ('global_roots_passed', 'numeric_passed', 'reference_rays',
                    'non_reference_checks_passed', 'original_fixed_grid_passed',
                    'additive_reference_contract_passed'):
            if key in result:
                item[key] = result[key]
        if 'failures' in result:
            item['failure_count'] = len(result['failures'])
            item['failures'] = result['failures']
        stages.append(item)
        files.update(receipt['files'])
        name = r.artifact(stage, 'exit.json')
        files[name] = r.digest(name)
    r.require(failed is not None or attempted == list(r.STAGES), 'Passing partial graph is not terminal')
    legacy = r.read(r.artifact('numerical', 'legacy-check.json'))
    summary = {'stages': stages, 'failed_stage': failed, 'numeric_passed': failed is None,
        'original_fixed_grid_passed': legacy['passed'],
        'legacy_missing_keys': [[c['width'], c['height'], c['z'], c['time'], c['high'], v['ray']]
            for c in legacy['cases'] for v in c['references'] if v.get('missing_reference')],
        'new_images': 0, 'cost_permitted': False, 'capture_permitted': False,
        'acceptance_passed': False, 'promoted': False,
        'method': 'Saved results, strict receipts and full inventories only. No field or browser execution.'}
    return history, files, summary


def main():
    history, files, summary = inspect()
    stem = PREFIX+'-close-once'
    launch = r.read(stem+'-launch.json')
    r.require(launch['script_sha256'] == r.digest('close_canonical_runtime_v35r3.py'))
    r.require(launch['launcher_sha256'] == r.digest('run_close_canonical_runtime_v35r3_once.py'))
    r.require(launch['history_sha256'] == r.digest(r.MANIFEST))
    r.atomic_json(PREFIX+'-check.json', summary)
    verdict = 'NUMERICAL PASS' if summary['numeric_passed'] else 'FAIL '+summary['failed_stage']
    next_work = ('Verify centre-v35r3-canonical-runtime-integrity.json and its actual-exit0 close receipt, '
        'including archived canonical display hashes. '
        + ('Prepare a distinct matched-cost/capture integration statically using these successful numerical receipts. '
           'Cost/capture are NOT PREPARED or enabled by numerical PASS. '
           if summary['numeric_passed'] else
           'Inspect only saved failed evidence; preserve attempt and prepare any correction as a distinct successor. ')
        + 'Never replay historical or completed stages. Preserve original fixed-grid FAIL and original global exit1. '
        'No tolerance relaxation, nearest-root substitution, live promotion or acceptance bypass. '
        'All19 realism/source/coverage/route/full acceptance remain unfinished; latest remains inspected REJECTED GAME v33r6.')
    archives, historical_display = {}, {}
    for name, want in history['display'].items():
        target = name
        if name in ('NOTES.md', 'README.md', 'status.txt'):
            target = name+'-before-'+PREFIX
            with (r.HERE/target).open('xb') as stream:
                stream.write((r.HERE/name).read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            archives[target] = r.digest(target)
        r.require(r.digest(target) == want)
        historical_display[name] = target
    notes = (r.HERE/'NOTES.md').read_text(encoding='utf-8-sig')
    r.require(notes.count('## Exact next bounded work') == 1)
    notes = notes[:notes.index('## Exact next bounded work')]
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — canonical runtime CLOSED '+verdict, 1)
    notes += '## Canonical runtime CLOSED — '+verdict+'; no replay\n'
    notes += '- Verified static manifest cea717961d275425e694648a0fab79d6478f56f1f7920c9e7f6e21102259295e (4511 evidence/16protected/4display) and close-once receipts before fresh foreground global.\n'
    for item in summary['stages']:
        notes += '- '+json.dumps(item, separators=(',', ':'))+'\n'
    notes += '- Original fixed-grid verdict remains '+str(summary['original_fixed_grid_passed'])+'; '+str(len(summary['legacy_missing_keys']))+' missing references retained. Historical global exit1 remains false/ineligible; new global computed fresh. No failed saved roots certified.\n'
    notes += '- Saved-only terminal closure binds complete inventories, original history, sources, prerequisites and actual exits. Sampled numerical evidence only; ordinary float64/frozen pad is not directed rounding or universal convergence. No field/camera/marcher/material change, image, inspection, promotion or visual/coverage/acceptance credit. Cost/capture NOT PREPARED. latest unchanged inspected REJECTED GAME v33r6. NOTES once/BOM retained; prior display archived.\n\n## Exact next bounded work\n'+next_work+'\n'
    (r.HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    (r.HERE/'status.txt').write_text('Canonical runtime CLOSED '+verdict+'. '+', '.join(
        x['stage']+' exit'+str(x['actual_exit']) for x in summary['stages'])+
        '. Original global exit1 ineligible; original fixed-grid FAIL retained. Cost/capture not prepared. '
        'latest unchanged inspected REJECTED GAME v33r6; all19/source/coverage/route/full acceptance unfinished; no promotion.\n')
    readme = (r.HERE/'README.md').read_text()
    (r.HERE/'README.md').write_text(readme+'\n[Canonical runtime closure]('+PREFIX+'-check.json): **'+verdict+'**. Fresh global and saved-only combination receipts remain distinct from original global exit1 and fixed-grid FAIL. Numerical evidence does not enable cost/capture or confer visual acceptance. No new image or promotion; all19 gates unfinished.\n')
    for group in ('files', 'protected'):
        r.verify(history[group])
    for name, target in historical_display.items():
        r.require(r.digest(target) == history['display'][name])
    r.verify_history(history['historical_display'])
    files.update(history['files'])
    files[r.MANIFEST] = r.digest(r.MANIFEST)
    files.update(archives)
    for label in ('build', 'freeze', 'check', 'close'):
        for suffix in ('-launch.json', '-exit.json', '.log'):
            name = r.PREFIX+'-'+label+'-once'+suffix
            files[name] = r.digest(name)
    for name in (PREFIX+'-check.json', 'close_canonical_runtime_v35r3.py',
                 'run_close_canonical_runtime_v35r3_once.py', stem+'-launch.json'):
        files[name] = r.digest(name)
    r.atomic_json(PREFIX+'-integrity.json', {'files': files, 'protected': history['protected'],
        'display': {n: r.digest(n) for n in history['display']}, 'historical_display': historical_display,
        'runtime_closed': True, **summary, 'next': next_work})
    print(verdict, 'saved-only terminal closure; no new runtime', flush=True)


if __name__ == '__main__':
    main()
