"""Saved-only joins and local CPU oracle replay. Never reruns GPU or global search."""
import root_reference_contract_v35r2 as contract
from additive_runtime_v35r2 import (HERE, MANIFEST, artifact, read, digest, atomic_json,
    worker, stage_receipt, expected_keys, bijection, require, verify)
from additive_evidence_v35r2 import (numeric_assessment, joined_inputs, validate_local,
    geometry, words, global_valid)
from local_additive_v35r2 import SOURCES


def main():
    numerical=stage_receipt('numerical')
    assessment=numeric_assessment(read(artifact('numerical','legacy-check.json')),read(artifact('numerical','raw.json')))
    require(assessment['non_reference_checks_passed'] is True)
    require(all(assessment[k]==numerical[k] for k in assessment))
    local=stage_receipt('local');independent=stage_receipt('global')
    verify(local['profiles'])
    profiles=bijection(expected_keys(),[read(n) for n in local['profiles']],lambda r:r['key'])
    roots=bijection(expected_keys(),independent['records'],lambda r:r['key'])
    raw,legacy=joined_inputs()
    source_hashes={n:digest(n) for n in SOURCES}
    raw_hash=digest(artifact('numerical','raw.json'))
    records=[];failures=[]
    for identity in expected_keys():
        record=profiles[identity]
        try:
            require(record['source_hashes']==source_hashes)
            require(record['raw_sha256']==raw_hash)
            case=raw[identity[:5]];start=4*identity[-1];gpu=case['hits'][start]
            require(record['gpu_depth']==gpu and record['legacy']==legacy[identity]['legacy'])
            require(record['actual_gpu_point_words']==case['words']['points'][start:start+4])
            require(record['actual_gpu_point']==words(case['points'][start:start+4],record['actual_gpu_point_words'],4)[:3])
            camera,ray=geometry(identity,gpu)
            require(record['reconstructed_gpu_depth_point']==(camera+gpu*ray).tolist())
            validate_local(record,replay_oracle=True)
            root=roots[identity]['independent']
            require(global_valid(root,gpu))
            require(root['original_reference']==record['legacy'] and root['gpu_depth']==gpu)
            record=dict(record,independent=root)
            require(contract.validate_ray(record))
        except (AssertionError,ValueError,KeyError,TypeError,IndexError,OverflowError) as exc:
            failures.append({'key':list(identity),'failure':repr(exc)})
        records.append(record)
    atomic_json(artifact('combination','joined.json'),records)
    combined=contract.combine(expected_keys(),read(artifact('combination','joined.json')))
    passed=not failures and combined['additive_reference_contract_passed']
    atomic_json(artifact('combination','result.json'),{
        'numeric_passed':bool(passed),'non_reference_checks_passed':True,
        'original_fixed_grid_passed':assessment['original_fixed_grid_passed'],
        'additive_reference_contract_passed':combined['additive_reference_contract_passed'],
        'contract':combined,'failures':failures,'reference_rays':len(records),
        'joined_sha256':digest(artifact('combination','joined.json')),
        'cost_permitted':False,'capture_permitted':False,'acceptance_passed':False,
        'limits':'Sampled numerical evidence only. Ordinary float64 with frozen 1e-12 pad, not directed rounding. Matched cost/capture integration and all19 visual/source/coverage/route/full acceptance gates remain separate.'})


if __name__=='__main__':
    worker('combination',main)
