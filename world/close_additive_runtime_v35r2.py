"""Saved-only terminal closure. Does not retry, sample a field or launch a browser."""
import json
from pathlib import Path
import additive_runtime_v35r2 as r

PREFIX='centre-v35r2-additive-runtime'


def main():
    history=r.fixture_gate()
    attempted=[s for s in r.STAGES if r.directory(s).exists()]
    r.require(attempted and attempted==list(r.STAGES[:len(attempted)]))
    stages=[];files={};failed=None
    for stage in attempted:
        r.require(failed is None, 'No attempt after a failed predecessor')
        receipt=r.read(r.artifact(stage,'exit.json'))
        r.require(receipt['files']==r.inventory(stage,('exit.json',)))
        launch=r.read(r.artifact(stage,'launch.json'))
        r.require(launch['manifest_sha256']==r.digest(r.MANIFEST))
        r.require(launch['script_sha256']==r.digest(r.SCRIPTS[stage]))
        r.require(launch['launcher_sha256']==r.digest('run_additive_v35r2_once.py'))
        r.require(launch['prerequisites']==r.prerequisite_hashes(stage))
        r.eligibility(stage)
        ready=False
        try:
            r.stage_receipt(stage);ready=True
        except (AssertionError,KeyError,ValueError,TypeError,FileNotFoundError):
            failed=stage
        result_name=r.artifact(stage,'result.json')
        result=r.read(result_name) if (r.HERE/result_name).exists() else None
        failure_name=r.artifact(stage,'failure.json')
        item={'stage':stage,'actual_exit':receipt['actual_exit'],'launcher_error':receipt['launcher_error'],
              'eligible_result':ready,'result_exists':result is not None,
              'failure':r.read(failure_name) if (r.HERE/failure_name).exists() else None}
        if result is not None:
            for key in ('passed','non_reference_checks_passed','original_fixed_grid_passed',
                        'root_certification_ready','global_roots_passed','numeric_passed',
                        'base_leaf_reach_samples','clearance_samples','reference_rays','rays','cases'):
                if key in result and not isinstance(result[key],(dict,list)):item[key]=result[key]
            if 'exact_transport' in result:
                item['exact_transport_failures']={k:sum(c[k] is not True for c in result['exact_transport'])
                    for k in ('transport_passed','exact_cheap_full_passed','exact_csg_replay_passed')}
        stages.append(item)
        files.update(receipt['files'])
        name=r.artifact(stage,'exit.json');files[name]=r.digest(name)
    r.require(failed is not None or attempted==list(r.STAGES), 'Do not close a passing partial graph')
    numeric_passed=failed is None
    summary={'stages':stages,'failed_stage':failed,'numeric_passed':numeric_passed,
        'new_images':0,'cost_permitted':False,'capture_permitted':False,'promoted':False,
        'method':'Saved inventories/results and actual exits only. No field, GPU, global search or historical replay.'}
    diagnosis_name='centre-v35r2-additive-global-saved-diagnosis.json'
    if failed=='global' and (r.HERE/diagnosis_name).exists():
        diagnosis=r.read(diagnosis_name);r.verify(diagnosis['source_hashes'])
        r.require(diagnosis['saved_only'] is True and diagnosis['field_samples']==0)
        r.require(diagnosis['numeric_passed'] is False and diagnosis['original_global_actual_exit']==1)
        summary['global_postprocessing_diagnosis']=diagnosis
        files[diagnosis_name]=r.digest(diagnosis_name)
    numerical=r.artifact('numerical','legacy-check.json')
    if (r.HERE/numerical).exists():
        legacy=r.read(numerical)
        summary['original_fixed_grid_passed']=legacy['passed']
        summary['legacy_missing_keys']=[[c['width'],c['height'],c['z'],c['time'],c['high'],v['ray']]
            for c in legacy['cases'] for v in c['references'] if v.get('missing_reference')]
        summary['legacy_failed_cases']=[{k:c[k] for k in ('width','height','z','time','high','cheap_full_jet_error','non_reference_checks_passed')}
            for c in legacy['cases'] if not c['passed']]
    r.atomic_json(PREFIX+'-check.json',summary)
    verdict='NUMERICAL PASS' if numeric_passed else 'FAIL '+failed
    next_work=('Verify centre-v35r2-additive-runtime-integrity.json and close-once receipt hashes. '
        +('Prepare distinct matched-cost/capture successor integration statically; neither is enabled by this numerical result. '
          if numeric_passed else 'Inspect only saved '+failed+' evidence and failure cause; preserve every attempt, do not replay or edit frozen sources. Prepare any correction as a distinct version and statically close it before new runtime. ')
        +('Global failure is the NumPy/Python scalar serialization boundary, not a saved bracket failure: all720 saved brackets satisfy strict predicates, zero unresolved. Successor must assess canonical data read back AFTER durable saving, preserve the exact finite/type predicates, and add a real NumPy-to-JSON integration regression. Preserve original exit1; design/check successor eligibility explicitly before any field or saved-only certification work. '
          if 'global_postprocessing_diagnosis' in summary else '')
        +'Candidate/live/defaults/ledgers/latest unchanged. No tolerance relaxation, forged legacy PASS, nearest-root substitution, or acceptance bypass. All19/source/coverage/route/full acceptance unfinished.')
    archives={}
    for name in ('NOTES.md','README.md','status.txt'):
        archive=name+'-before-'+PREFIX
        with (r.HERE/archive).open('xb') as stream:stream.write((r.HERE/name).read_bytes())
        archives[archive]=r.digest(archive)
    notes=(r.HERE/'NOTES.md').read_text(encoding='utf-8-sig')
    r.require(notes.count('## Exact next bounded work')==1)
    notes=notes[:notes.index('## Exact next bounded work')]
    notes=notes.replace(notes.splitlines()[0],'# Active: REDIRECT4 — additive runtime CLOSED '+verdict,1)
    notes+='## Additive runtime CLOSED — '+verdict+'; no replay\n'
    notes+='- Verified integration1949 evidence/16protected/4display and actual-exit0 static closure before new foreground stages. Saved-only closure binds every attempted inventory, source, prerequisite and actual exit.\n'
    for item in stages:
        notes+='- '+json.dumps(item,separators=(',',':'))+'\n'
    if 'original_fixed_grid_passed' in summary:
        notes+='- Original fixed-grid verdict retained: '+str(summary['original_fixed_grid_passed'])+'; missing keys='+json.dumps(summary['legacy_missing_keys'],separators=(',',':'))+'. No retroactive PASS or changed scan tolerance.\n'
    if 'global_postprocessing_diagnosis' in summary:
        d=summary['global_postprocessing_diagnosis']
        notes+='- Saved-only diagnosis: all720 global records satisfy strict saved predicates, zero unresolved; max bracket width='+str(d['max_saved_bracket_width'])+', max difference='+str(d['max_saved_difference'])+'. finish_global persisted raw.json but assessed original NumPy scalars; contract.finite excludes numpy.float64. Equal native-float/NumPy-float synthetic pair reproduces accept/reject. Canonical saved JSON passes the record-shape predicate, but actual global exit1 and false result remain immutable; no root/numerical credit. See centre-v35r2-additive-global-saved-diagnosis.json.\n'
    notes+='- Terminal result preserved; '+('all numerical stages completed' if numeric_passed else 'all successors of '+failed+' unattempted and blocked')+'. No historical replay. Cost/capture successor integration remains NOT PREPARED. No new image/inspection, promotion, realism/source/coverage/route/full acceptance credit. latest unchanged inspected REJECTED GAME v33r6; all19 unfinished. NOTES once/BOM retained and prior display archived.\n\n## Exact next bounded work\n'+next_work+'\n'
    (r.HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    status='Additive runtime CLOSED '+verdict+'. '+', '.join(x['stage']+' exit'+str(x['actual_exit']) for x in stages)+'. '
    status+='No replay; '+('numerical evidence only' if numeric_passed else 'downstream stages blocked')+'. Cost/capture not prepared. latest unchanged inspected REJECTED GAME v33r6; all19/source/coverage/route/full acceptance unfinished; no promotion.\n'
    (r.HERE/'status.txt').write_text(status)
    readme=(r.HERE/'README.md').read_text()
    (r.HERE/'README.md').write_text(readme+'\n[Additive runtime closure](centre-v35r2-additive-runtime-check.json): **'+verdict+'**. Actual exits and all raw/partial evidence are preserved; no replay. Original fixed-grid verdict remains separate. No new image or promotion; cost/capture and all19 visual/coverage/route/full acceptance remain unfinished.\n')
    for group in ('files','protected'):r.verify(history[group])
    r.require(r.digest('latest.png')==history['display']['latest.png'])
    files.update(history['files']);files[r.MANIFEST]=r.digest(r.MANIFEST);files.update(archives)
    for suffix in ('-launch.json','-exit.json','.log'):
        name='centre-v35r2-additive-close-once'+suffix;files[name]=r.digest(name)
    for name in (PREFIX+'-check.json','close_additive_runtime_v35r2.py','run_close_additive_runtime_v35r2_once.py',PREFIX+'-close-once-launch.json'):
        files[name]=r.digest(name)
    r.atomic_json(PREFIX+'-integrity.json',{'files':files,'protected':history['protected'],
        'display':{n:r.digest(n) for n in history['display']},'archived_display':archives,
        'runtime_closed':True,'failed_stage':failed,'numeric_passed':numeric_passed,
        'new_images':0,'cost_permitted':False,'capture_permitted':False,'next':next_work})
    print(verdict,'saved-only terminal closure; no new runtime',flush=True)


if __name__=='__main__':
    main()
