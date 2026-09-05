"""Build the matching double-precision mirror without changing old evidence."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'probe_continuum_v22.py').read_text()
def replace(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)
replace('Numerical v22 mirror', 'Numerical v23 mirror')
replace('pole = r2/(r2+1)', 'pole = r2/(r2+4)')
replace('gp = mul((2*x, 2*y, 0), 1/(r2+1)**2)', 'gp = mul((8*x, 8*y, 0), 1/(r2+4)**2)')
replace('''    v = z*.84+shear*u-time*.65
    gv = add((0, 0, .84), mul(gu, shear))''', '''    cap_weight = cap*cap/(cap*cap+4)
    dome = math.exp(-.1*r2)
    gdome = mul((-.2*x*cap_weight, -.2*y*cap_weight, 8*cap/(cap*cap+4)**2), 5*dome)
    v = z*.84+shear*u-time*.65+5*cap_weight*dome
    gv = add(add((0, 0, .84), mul(gu, shear)), gdome)''')
replace('phase = 3*v-2*petal+.35*sin(petal+v)', 'phase = 2*v-petal+.6*sin(petal+v)')
replace('gphase = add(add(mul(gv, 3), mul(gt, -2)), mul(add(gt, gv), .35*cos(petal+v)))', 'gphase = add(add(mul(gv, 2), mul(gt, -1)), mul(add(gt, gv), .6*cos(petal+v)))')
replace('f -= .22*pole*sin(phase)', 'f -= .32*pole*sin(phase)')
replace('mul(gphase, pole*cos(phase))), -.22)', 'mul(gphase, pole*cos(phase))), -.32)')
replace('[(.085, 8, 4, 32), (.028, 21, -8, 72), (.010, 55, 16, 180)]', '[(.14, 2.8, 1, 14), (.06, 6.5, 2, 32), (.022, 14, -4, 64)]')
replace(')-7)-2.198', ')-7)-2.35')
replace('def ray_slope(p, rd, time, high):', 'def ray_slope(p, rd, time, high, camera):')
replace('2*lower/(1+lower*lower)**2 if lower > .57736 else .65', '8*lower/(4+lower*lower)**2 if lower > 1.15471 else .325')
replace('lower/(1+lower*lower) if lower > 1 else .5', 'lower/(4+lower*lower) if lower > 2 else .25')
replace('    petal = 10*angular+.14*meridian', '''    if p[2]-.4*abs(rd[2]) < -27.5:
        dr = .2*lower*math.exp(-.1*lower*lower) if lower > 2.23607 else .27126
        meridian += 5*(dr*transverse+.325*math.exp(-.1*lower*lower)*abs(rd[2]))
    petal = 10*angular+.14*meridian''')
replace('''    result += .22*(ps+3*meridian+2*petal+.35*(petal+meridian))
    result += .085*(ps+8*meridian+4*petal)
    result += .028*(ps+21*meridian+8*petal)
    if high:
        result += .010*(ps+55*meridian+16*petal)''', '''    result += .32*(ps+2*meridian+petal+.6*(petal+meridian))
    footprint = max(0, sqrt(sum((x-y)**2 for x,y in zip(p,camera)))-.4)*PIXEL
    result += .14*math.exp(-.5*(footprint*14)**2)*(ps+2.8*meridian+petal)
    result += .06*math.exp(-.5*(footprint*32)**2)*(ps+6.5*meridian+2*petal)
    if high:
        result += .022*math.exp(-.5*(footprint*64)**2)*(ps+14*meridian+4*petal)''')
replace('range(1024 if high else 768)', 'range(2048 if high else 1536)')
start=s.index('        if abs(value) < .065:')
end=s.index('        previous, previous_value', start)
s=s[:start]+s[end:]
replace('max(min(.4, abs(value)*.95/ray_slope(p, rd, time, high)), .000001)', 'min(.4, abs(value)*.95/ray_slope(p, rd, time, high, camera))')
replace('random.Random(22)', 'random.Random(23)')
replace("'slope_bound': 28+4*PIXEL", "'newton': False, 'slope_bound': 60+4*PIXEL")
replace("continuum-v22-probe.json", "continuum-v23-probe.json")
assert not (HERE/'probe_continuum_v23.py').exists()
(HERE/'probe_continuum_v23.py').write_text(s)
print('Created v23 CPU mirror')
