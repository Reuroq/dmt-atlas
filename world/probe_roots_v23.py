"""Independent fixed-step sign brackets vs production bound; not global proof."""
import hashlib
import json
import math
import random
from probe_continuum_v23 import HERE, add, mul, dot, sample, ray, ray_slope

output=HERE/'continuum-v23-root-check.json'
assert not output.exists(), 'Keep evidence immutable'
rng=random.Random(2301)
max_ratio=0
for _ in range(1200):
    r,a,z,t=rng.uniform(.001,9.4),rng.uniform(-math.pi,math.pi),rng.uniform(-37,10),rng.uniform(0,18)
    p=(r*math.cos(a),1.7+r*math.sin(a),z)
    rd=tuple(rng.uniform(-1,1) for _ in range(3))
    rd=mul(rd,1/math.sqrt(dot(rd,rd)))
    camera=(0,1.7,rng.choice([8,-8]))
    bound=ray_slope(p,rd,t,True,camera)
    for h in [0,.1,.2,.3,.4]:
        _,g=sample(add(p,mul(rd,h)),t,camera)
        max_ratio=max(max_ratio,abs(dot(g,rd))/bound)

# Dense fixed steps use neither envelope nor derivative bound nor Newton.
# Sampling cannot exclude a crossing and return wholly inside one .003 interval.
rays=[]
for z,t in [(8,5),(8,8),(-8,10),(-8,13)]:
    camera=(0,1.7,z)
    for x,y in [(0,0),(.03,.01),(.2,-.11),(-.43,.31),(.8,.6),(-.9,-.5)]:
        rd=(x,y,-1)
        rd=mul(rd,1/math.sqrt(dot(rd,rd)))
        actual,iterations,residual=ray(camera,rd,t,True)
        assert actual is not None
        previous=sample(camera,t,camera)[0]
        first=None
        step=.003
        for i in range(1,math.ceil((actual+.2)/step)+1):
            along=i*step
            current=sample(add(camera,mul(rd,along)),t,camera)[0]
            if current*previous<0:
                lo,hi=(i-1)*step,along
                lv=previous
                for _ in range(18):
                    mid=(lo+hi)/2
                    value=sample(add(camera,mul(rd,mid)),t,camera)[0]
                    if value*lv>0: lo,lv=mid,value
                    else: hi=mid
                first=(lo+hi)/2
                break
            previous=current
        rays.append(dict(z=z,time=t,direction=rd,actual=actual,reference=first,
                         delta=None if first is None else actual-first,iterations=iterations,residual=residual))
    print(f'Checked fixed-step roots z{z} t{t}',flush=True)
passed=max_ratio<=1 and all(r['reference'] is not None and abs(r['delta'])<.005 for r in rays)
out=dict(method='CPU double precision, 6000 segment derivatives and 24 fixed-step .003 ray scans; finite sampling, not first-hit proof or GPU acceptance',
         newton=False,max_derivative_bound_ratio=max_ratio,passed=passed,rays=rays,
         dependencies={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['continuum.js','continuum-v23.js','probe_continuum_v23.py','probe_roots_v23.py']})
output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(passed=passed,max_ratio=max_ratio,max_abs_root_delta=max(abs(r['delta']) for r in rays if r['delta'] is not None))))
assert passed
