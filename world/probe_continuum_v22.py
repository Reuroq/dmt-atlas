"""Numerical v22 mirror: derivative/root checks, not visual acceptance."""
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIXEL = 2 * math.tan(math.radians(34)) / 800
sin, cos, sqrt = math.sin, math.cos, math.sqrt

def add(a, b):
    return tuple(x+y for x, y in zip(a, b))

def mul(a, s):
    return tuple(x*s for x in a)

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def sample(p, time, camera, high=True):
    delta = tuple(x-y for x, y in zip(p, camera))
    length = sqrt(dot(delta, delta))
    footprint = length*PIXEL
    gf = mul(delta, PIXEL/max(length, 1e-12))
    x, y, z = p[0], p[1]-1.7, p[2]
    r2 = x*x+y*y
    cap = min(z+27.5, 0)
    rho = sqrt(r2+cap*cap)
    u = rho-7
    gu = mul((x, y, cap), 1/max(rho, .00001))
    a = math.atan2(y, x)-time*.065
    pole = r2/(r2+1)
    gp = mul((2*x, 2*y, 0), 1/(r2+1)**2)
    ga = mul((-y, x, 0), 1/max(r2, .0000001))
    shear = 1.45+.18*sin(time*.61)
    v = z*.84+shear*u-time*.65
    gv = add((0, 0, .84), mul(gu, shear))
    petal = 10*a+.28*sin(v*.5+time*.37)
    gt = add(mul(ga, 10), mul(gv, .14*cos(v*.5+time*.37)))
    phase = v+.72*pole*cos(petal)
    gphase = add(gv, mul(add(mul(gp, cos(petal)), mul(gt, -pole*sin(petal))), .72))
    f = u-1.35*sin(phase)
    g = add(gu, mul(gphase, -1.35*cos(phase)))
    phase = petal+.7*sin(v)
    gphase = add(gt, mul(gv, .7*cos(v)))
    f -= .45*pole*cos(phase)
    g = add(g, mul(add(mul(gp, cos(phase)), mul(gphase, -pole*sin(phase))), -.45))
    phase = 3*v-2*petal+.35*sin(petal+v)
    gphase = add(add(mul(gv, 3), mul(gt, -2)), mul(add(gt, gv), .35*cos(petal+v)))
    f -= .22*pole*sin(phase)
    g = add(g, mul(add(mul(gp, sin(phase)), mul(gphase, pole*cos(phase))), -.22))
    for amp, fv, fa, frequency in [(.085, 8, 4, 32), (.028, 21, -8, 72), (.010, 55, 16, 180)][:3 if high else 2]:
        weight = math.exp(-.5*(footprint*frequency)**2)
        gw = mul(gf, -weight*frequency*frequency*footprint)
        phase = fv*v+fa*petal
        gphase = add(mul(gv, fv), mul(gt, fa))
        f -= amp*pole*weight*sin(phase)
        g = add(g, mul(add(mul(add(mul(gp, weight), mul(gw, pole)), sin(phase)), mul(gphase, pole*weight*cos(phase))), -amp))
    return f, g

def envelope(p):
    return abs(sqrt(p[0]**2+(p[1]-1.7)**2+min(p[2]+27.5, 0)**2)-7)-2.198

def ray_slope(p, rd, time, high):
    transverse = math.hypot(rd[0], rd[1])
    lower = max(0, math.hypot(p[0], p[1]-1.7)-.4*transverse)
    ps = transverse*(2*lower/(1+lower*lower)**2 if lower > .57736 else .65)
    angular = transverse*(lower/(1+lower*lower) if lower > 1 else .5)
    radial = transverse if p[2]-.4*abs(rd[2]) > -27.5 else 1
    meridian = .84*abs(rd[2])+(1.45+.18*sin(time*.61))*radial
    petal = 10*angular+.14*meridian
    result = radial+1.35*(meridian+.72*(ps+petal))
    result += .45*(ps+petal+.7*meridian)
    result += .22*(ps+3*meridian+2*petal+.35*(petal+meridian))
    result += .085*(ps+8*meridian+4*petal)
    result += .028*(ps+21*meridian+8*petal)
    if high:
        result += .010*(ps+55*meridian+16*petal)
    return result+4*PIXEL

def ray(camera, rd, time, high):
    travel = previous = previous_value = 0
    have_previous = False
    def point(t):
        return add(camera, mul(rd, t))
    for iteration in range(1024 if high else 768):
        p = point(travel)
        bound = envelope(p)
        if bound > .08:
            travel += bound*.95
            have_previous = False
            continue
        value, gradient = sample(p, time, camera, high)
        if have_previous and value*previous_value < 0:
            lo, hi, lv = previous, travel, previous_value
            for _ in range(14):
                mid = (lo+hi)/2
                mv = sample(point(mid), time, camera, high)[0]
                if mv*lv > 0:
                    lo, lv = mid, mv
                else:
                    hi = mid
            travel = (lo+hi)/2
            return travel, iteration+1, abs(sample(point(travel), time, camera, high)[0])
        if abs(value) < .00015:
            return travel, iteration+1, abs(value)
        if abs(value) < .065:
            trial = travel
            for _ in range(6):
                s, g = sample(point(trial), time, camera, high)
                derivative = dot(g, rd)
                if abs(derivative) < .0001:
                    break
                trial -= max(-.08, min(.08, s/derivative))
                trial = max(travel, min(travel+.24, trial))
            residual = abs(sample(point(trial), time, camera, high)[0])
            if residual < .00015:
                return trial, iteration+1, residual
        previous, previous_value, have_previous = travel, value, True
        travel += max(min(.4, abs(value)*.95/ray_slope(p, rd, time, high)), .000001)
        if travel > 105:
            return None, iteration+1, None
    return None, iteration+1, None

def main():
    rng = random.Random(22)
    error = maximum = 0
    for _ in range(1600):
        r, a, z, t = rng.uniform(.01, 9.2), rng.uniform(-math.pi, math.pi), rng.uniform(-37, 10), rng.uniform(0, 16)
        p, camera = (r*cos(a), 1.7+r*sin(a), z), (0, 1.7, 8)
        _, gradient = sample(p, t, camera)
        maximum = max(maximum, sqrt(dot(gradient, gradient)))
        for axis in range(3):
            plus, minus = list(p), list(p)
            plus[axis] += .000001
            minus[axis] -= .000001
            estimate = (sample(plus, t, camera)[0]-sample(minus, t, camera)[0])/.000002
            error = max(error, abs(estimate-gradient[axis]))
    out = {'method': 'Double precision CPU mirror; sparse rays, not visual acceptance or a complete GPU diagnosis',
           'derivative_samples': 1600, 'max_derivative_error': error,
           'max_sampled_gradient': maximum, 'slope_bound': 28+4*PIXEL, 'rays': {}}
    for high in [True, False]:
        for z, time in [(8, 5), (8, 8), (-8, 10), (-8, 13)]:
            camera = (0, 1.7, z)
            counts = {'rays': 0, 'hits': 0, 'exhausted_or_escaped': 0, 'max_iterations': 0, 'max_residual': 0}
            for yy in range(25, 800, 50):
                for xx in range(25, 1200, 50):
                    rd = ((xx/1200*2-1)*1.5*math.tan(math.radians(34)), (1-yy/800*2)*math.tan(math.radians(34)), -1)
                    rd = mul(rd, 1/sqrt(dot(rd, rd)))
                    travel, iterations, residual = ray(camera, rd, time, high)
                    counts['rays'] += 1
                    counts['hits' if travel is not None else 'exhausted_or_escaped'] += 1
                    counts['max_iterations'] = max(counts['max_iterations'], iterations)
                    counts['max_residual'] = max(counts['max_residual'], residual or 0)
            out['rays'][f'{"HIGH" if high else "LOW"}-z{z}-t{time}'] = counts
            print(json.dumps({list(out['rays'])[-1]: counts}), flush=True)
    (HERE/'continuum-v22-probe.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'rays'}))
    assert error < .0001
    assert maximum < out['slope_bound']
    assert all(c['exhausted_or_escaped'] == 0 for c in out['rays'].values())

if __name__ == '__main__':
    main()
