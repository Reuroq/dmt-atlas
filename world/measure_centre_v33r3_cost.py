"""One-shot saved-ray comparison. No GPU replay and no acceptance inference."""
from pathlib import Path
import hashlib
import json
import numpy as np
HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v33r3-cost-review.json'
assert not OUT.exists()
def read(name):return json.loads((HERE/name).read_text())
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
for name,key in [('centre-v33r3-bounds-check.json','source_hashes'),
                 ('numeric-candidate-v33r3-check.json','files'),
                 ('centre-v33r3-first-root-check.json','source_hashes')]:
    receipt=read(name)
    assert receipt['passed'] and all(digest(n)==h for n,h in receipt[key].items())
old=read('numeric-candidate-v33r2-raw.json');new=read('numeric-candidate-v33r3-raw.json')
keys=['width','height','z','time','high']
def key(c):return tuple(c[k] for k in keys)
lookup={key(c):c for c in new}
matched=[lookup[key(c)] for c in old]
assert len(old)==len(matched)==24 and len(new)==32
def stats(cases):
    steps=np.concatenate([np.array(c['hits']).reshape(-1,4)[:,2] for c in cases])
    out={'rays':len(steps),'mean_steps':float(steps.mean()),'p95_steps':float(np.percentile(steps,95)),
         'max_steps':float(steps.max()),
         'median_three_readbacks_seconds':float(np.median([c['gpu_three_readbacks_seconds'] for c in cases]))}
    if 'counts' in cases[0]:
        counts=np.concatenate([np.array(c['counts']).reshape(-1,4) for c in cases])
        out.update({f'mean_{k}':float(counts[:,i].mean()) for i,k in enumerate(
            ['cheap_calls','full_trace_calls','certified_skips','refinement_calls'])})
        out['mean_envelope_skips']=float((steps-counts[:,0]).mean())
        out['mean_full_field_evaluations_in_probe']=float((counts[:,1]+counts[:,3]+1).mean())
    return out
depth=max(float(np.max(abs(np.array(a['hits']).reshape(-1,4)[:,0]-np.array(b['hits']).reshape(-1,4)[:,0]))) for a,b in zip(old,matched))
out={'matched_v33r2':stats(old),'matched_v33r3':stats(matched),'all_v33r3':stats(new),
    'max_matched_depth_delta':depth,
    'source_hashes':{n:digest(n) for n in ['numeric-candidate-v33r2-raw.json',
        'numeric-candidate-v33r3-raw.json','centre-v33r3-bounds-check.json',
        'numeric-candidate-v33r3-check.json','centre-v33r3-first-root-check.json',Path(__file__).name]},
    'limitations':'Saved sparse SwiftShader rays only. Old timing surrounds page.evaluate; new timing is inside JS around the first three readbacks, excluding RPC and the separate fourth counter readback. Shader instrumentation/compilation and timing boundary differ, so wall-time comparison is indicative, not a controlled benchmark. Main-loop full trace counts omit shaded-frame work. No old replay, no full-resolution or realism acceptance.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='source_hashes'}))
