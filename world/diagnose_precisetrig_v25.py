"""One-shot fixed-point intermediate-channel/atan ablation; runtime untouched."""
import json
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from verify import ARGS
from fidelity import digest
from probe_continuum_v25 import field

HERE=Path(__file__).resolve().parent
OUT=HERE/'diagnostic-precisetrig-v25.json'
assert not OUT.exists()
cases=json.loads((HERE/'continuum-v25-numerical-findings.json').read_text())['cases']
errors=[];results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=ARGS);page=browser.new_page()
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.goto((HERE/'diagnostic_precisetrig_v25.html').as_uri())
    for case in cases:
        point=np.asarray(case['worst_position'],dtype=np.float32).astype(float);z,t=case['z'],case['time']
        actual=page.evaluate('a=>probe(...a)',[point.tolist(),z,t,1,0])
        ablated=page.evaluate('a=>probe(...a)',[point.tolist(),z,t,1,1])
        x,y,zz=point[0],point[1]-1.7,point[2];r=np.hypot(x,y);cap=min(zz+27.5,0.)
        rho=np.hypot(r,.45*cap);a=np.arctan2(y,x)-t*.065;pole=r*r/(r*r+4);cw=cap*cap/(cap*cap+4)
        warp=2.6*np.cos(.85*x)*np.cos(.85*y)+.75*np.sin(1.7*x+t*.19)*np.cos(1.7*y-t*.17)
        v=zz*.72+(1.8+.22*np.sin(t*.61))*(rho-7)-t*.57+cw*warp
        petal=8*a+.32*np.sin(v*.5+t*.31)
        cpu=float(field(point,t,np.array([0,1.7,z]),1))
        result={'z':z,'time':t,'ray':case['worst_ray'],'point_float32':point.tolist(),
                'gpu_channels':actual,'cpu_channels':[[r,rho,a,pole],[cw,warp,v,petal]],
                'cpu_field':cpu,'gpu_field_error':abs(cpu-actual[0][3]),
                'cpu_angle_override_gpu_field':ablated[0][3],
                'cpu_angle_override_error':abs(cpu-ablated[0][3]),
                'angle_error':actual[1][2]-a,'petal_error':actual[2][3]-petal}
        results.append(result)
        print(json.dumps({k:v for k,v in result.items() if k not in ['point_float32','gpu_channels','cpu_channels']}),flush=True)
    browser.close()
out={'method':'Four saved worst-position float32 points, archived GLSL with only sin/cos replaced by range-reduced degree13/12 polynomials, then optional CPU atan override. Live runtime unchanged. No navigation/time/visual acceptance claims.',
     'errors':errors,'cases':results,'sha256':{name:digest(HERE/name) for name in ['continuum.js','continuum-v25.js','trip.js','diagnostic_precisetrig_v25.html','diagnose_precisetrig_v25.py','continuum-v25-numerical-findings.json']}}
OUT.write_text(json.dumps(out,indent=2)+'\n')
assert not errors
