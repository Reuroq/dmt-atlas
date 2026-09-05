"""Every scheduled ray: CPU diagnostic grid and ALL strict entering/exiting cells."""
import root_reference_contract_v35r2 as c
from additive_runtime_v35r2 import HERE, MANIFEST, artifact, read, digest, atomic_json, worker, expected_keys
from additive_evidence_v35r2 import joined_inputs, geometry, scalar_record, validate_local, words

SOURCES=('field_centre_v35r2.py','local_additive_v35r2.py','additive_evidence_v35r2.py',
         'root_reference_contract_v35r2.py','centre-v35r2-bound-design.json',MANIFEST)


def build_record(identity, case, legacy, source_hashes=None, raw_hash=None):
    index=identity[-1];gpu=case['hits'][4*index]
    camera,ray=geometry(identity,gpu)
    full=[scalar_record(gpu+(i-80)*.00005,identity,camera,ray) for i in range(161)]
    samples=[[s['depth'],s['full']] for s in full]
    brackets=[]
    for index in range(160):
        left,right=full[index],full[index+1]
        if not c.strict(left['full'],right['full']):
            continue
        bracket={'index':index,'entering':left['full']>0,'steps':[],'full_steps':[]}
        for _ in range(24):
            before=[left,right]
            mid=scalar_record((left['depth']+right['depth'])/2,identity,camera,ray)
            step={'before':[left['depth'],right['depth'],left['full'],right['full']],
                  'mid':mid['depth'],'value':mid['full']}
            if (mid['full']>0)==(left['full']>0):left=mid
            else:right=mid
            step['after']=[left['depth'],right['depth'],left['full'],right['full']]
            bracket['steps'].append(step)
            bracket['full_steps'].append({'before':before,'midpoint':mid,'after':[left,right]})
            if mid['full']==0:
                bracket['unresolved_midpoint_zero']=True
                break
        bracket['final']=[left['depth'],right['depth'],left['full'],right['full']]
        brackets.append(bracket)
    start=4*identity[-1]
    point_words=case['words']['points'][start:start+4]
    gpu_point=words(case['points'][start:start+4],point_words,4)[:3]
    return {'key':list(identity),'gpu_depth':gpu,'legacy':legacy,
            'actual_gpu_point':gpu_point,'actual_gpu_point_words':point_words,
            'camera':camera.tolist(),'ray':ray.tolist(),
            'reconstructed_gpu_depth_point':(camera+gpu*ray).tolist(),
            'local':{'samples':samples,'full_records':full,'brackets':brackets},
            'source_hashes':source_hashes if source_hashes is not None else {n:digest(n) for n in SOURCES},
            'raw_sha256':raw_hash if raw_hash is not None else digest(artifact('numerical','raw.json'))}


def main():
    raw,legacy=joined_inputs()
    source_hashes={n:digest(n) for n in SOURCES}
    raw_hash=digest(artifact('numerical','raw.json'))
    root=HERE/artifact('local','rays');root.mkdir()
    paths=[]
    for index,identity in enumerate(expected_keys()):
        record=build_record(identity,raw[identity[:5]],legacy[identity]['legacy'],source_hashes,raw_hash)
        path=artifact('local',f'rays/{index:03d}.json')
        atomic_json(path,record)  # Oracle values are durable BEFORE any assessment.
        paths.append(path)
        if index%60==59:print('Local profiles saved',index+1,flush=True)
    failures=[]
    for path in paths:
        try:
            validate_local(read(path),replay_oracle=True)
        except (AssertionError,ValueError,KeyError,TypeError,IndexError,OverflowError) as exc:
            failures.append({'path':path,'failure':repr(exc)})
    atomic_json(artifact('local','result.json'),{
        'root_certification_ready':not failures,'numeric_passed':False,'reference_rays':len(paths),
        'profiles':{path:digest(path) for path in paths},'failures':failures,
        'meaning':'Readiness only. No global first-root or numerical PASS.'})


if __name__=='__main__':
    worker('local',main)
