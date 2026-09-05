"""Bounded CPU numerical probe, not a render or visual acceptance test.

Mirrors archived v21 HIGH field in double precision. Checks the slope claim
and whether the step budget can explain torn seams. Never edits runtime.
"""
import json
from pathlib import Path
import math
import random

HERE = Path(__file__).resolve().parent

def sheet(p, time):
    sin, cos = math.sin, math.cos
    x, y, z = p
    y = y - 1.7
    r = math.hypot(x, y)
    u = math.hypot(r, min(z + 27.5, 0)) - 7
    a = math.atan2(y, x) - time * .065
    pole = r*r/(r*r+1)
    v = z*.84+(1.45+.18*sin(time*.61))*u-time*.65
    petal = 10*a+.28*sin(v*.5+time*.37)
    return (u-1.35*sin(v+.72*pole*cos(petal))
            -pole*(.45*cos(petal+.7*sin(v))
                   +.22*sin(3*v-2*petal+.35*sin(petal+v))
                   +.085*sin(8*v+4*petal)
                   +.028*sin(21*v-8*petal)
                   +.010*sin(55*v+16*petal)))

def field(p, time):
    r = math.hypot(p[0], p[1]-1.7)
    bound = abs(math.hypot(r, min(p[2]+27.5, 0))-7)-2.198
    return bound if bound > .3 else (abs(sheet(p, time))-.055)/12

def rays(position, time, steps):
    # Sparse pixel-centre sample of the 1200x800, vertical FOV68 capture.
    tangent = math.tan(math.radians(34))
    out = {'rays':0,'hits':0,'exhausted':0,'escaped':0}
    for yy in range(10,800,20):
        for xx in range(10,1200,20):
            rd = [(xx/1200*2-1)*1.5*tangent, (1-yy/800*2)*tangent,-1]
            length = math.sqrt(sum(v*v for v in rd))
            rd = [v/length for v in rd]
            travel = 0
            outcome = 'exhausted'
            for _ in range(steps):
                p = [position[k]+rd[k]*travel for k in range(3)]
                d = field(p,time)
                if abs(d) < .00035+travel*(2*tangent/800)*.025:
                    outcome = 'hits'
                    break
                travel += max(abs(d)*.9,.0005)
                if travel > 105:
                    outcome = 'escaped'
                    break
            out['rays'] += 1
            out[outcome] += 1
    return out

rng = random.Random(21)
count = 120000
norm = []
for _ in range(count):
    r,a,z,t = rng.uniform(.02,9.2),rng.uniform(-math.pi,math.pi),rng.uniform(-37,10),rng.uniform(0,16)
    p = [r*math.cos(a),1.7+r*math.sin(a),z]
    if abs(sheet(p,t)) >= .1:
        continue
    gradient = []
    for axis in range(3):
        plus,minus = p.copy(),p.copy()
        plus[axis] += .0001
        minus[axis] -= .0001
        gradient.append((sheet(plus,t)-sheet(minus,t))/.0002)
    norm.append(math.sqrt(sum(v*v for v in gradient)))
out = {'method':'Double-precision CPU field mirror; sparse rays, not GPU diagnosis or visual grading',
       'surface_samples':len(norm), 'max_sampled_gradient':max(norm),
       'samples_exceeding_claimed_slope_12':sum(v>12 for v in norm), 'captures':{}}
for name in ['realism-chrysanthemum-v21','realism-chrysanthemum-close-v21']:
    d=json.loads((HERE/(name+'.json')).read_text())['capture_diagnostics']
    out['captures'][name] = {str(n):rays(d['position'],d['animTime'],n) for n in [256,1024]}
(HERE/'continuum-v21-probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
