"""One-shot reach-only successor; keep every v33 surface/material expression."""
from pathlib import Path
import hashlib
import importlib.util
import json
import numpy as np

HERE=Path(__file__).resolve().parent
def save(name,source):
    path=HERE/name
    assert not path.exists(),name
    path.write_text(source)
def change(source,old,new):
    assert source.count(old)==1,old[:100]
    return source.replace(old,new)

field=(HERE/'field_centre_v33.py').read_text()
field=change(field,"    return {'leaf_L_constants'",'''    lower=[local.trig().filtered(4).scale(.55)+core.scale(1.6/6.3),
        child_local.trig().filtered(12).scale(.45)+core.scale(1.1/6.3),
        angular12.scale(.65)+core.scale(1.6/6.3),
        angular36.scale(1.1)+core.scale(1.1/6.3),
        parent_shell.scale(1.6),parent_shell.scale(1.6),
        child_shell.scale(1.128),child_shell.scale(1.128)]
    return {'lower_L_polynomials':[v.L.tolist() for v in lower],
        'lower_H_polynomials':[v.H.tolist() for v in lower],
        'leaf_L_constants' ''')
field+='''

def lower_parts(p,t,camera,high,pixel=PIXEL):
    """Independent scalar lower leaves, each <= its original parent/child leaf."""
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(.075*t),np.sin(.075*t)
    x,y=c*px-s*py,s*px+c*py
    den=x*x+y*y+2.25
    h=(x+1j*y)/np.sqrt(den)
    h6,h12,h18,h36=h**6,h**12,h**18,h**36
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    R=1.35*rho+.12*z+.15*h6.real-.12*t
    T=.9*z-.25*rho+.2*h6.imag-.19*t
    C=R+.9*np.sin(T);P=.7*np.sin(T)+.22*np.cos(R)+.2*t
    D=3*C+.35*np.cos(T)-.21*t;U=3*T+.4*np.cos(R)
    V=3*P+.3*np.sin(U)
    footprint2=pixel**2*np.sum((p-camera)**2,axis=-1)
    def G(v,k):return v*np.exp(-.5*k*k*footprint2)
    s=G(np.cos(C)-.6*np.cos(T),4)
    q=G(np.cos(D)-.55*np.cos(U),12)
    if high:q+=.11*G(np.cos(3*D+.25*h36.real),36)
    A=abs(h6)**2-G((h12*np.exp(1j*P)).real,4)
    B=abs(h18)**2-G((h36*np.exp(1j*V)).real,12)
    return np.stack([.39-.55*G(np.cos(T),4)+1.6/den,
        .345-.45*G(np.cos(U),12)+1.1/den,
        -.16+.65*A+1.6/den,-.105+1.1*B+1.1/den,
        1.6*s-.32,-1.6*s-.32,1.128*q-.211032,-1.128*q-.211032],axis=-1)-.00001
'''
save('field_centre_v33r2.py',field)
spec=importlib.util.spec_from_file_location('v33r2_field',HERE/'field_centre_v33r2.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
analytic=module.analytic_bounds()
H=(np.ceil(analytic['lower_H_polynomials'])+1).astype(int)
def poly(row):
    return f'{row[0]}.+{row[1]}.*s+{row[2]}.*s*s'

source=(HERE/'continuum-v33-candidate.js').read_text()
source=change(source,'void fieldParts(vec3 p,out vec4 f,out vec4 a,out vec4 b){',
    'void fieldPartsReach(vec3 p,out vec4 f,out vec4 a,out vec4 b,out vec4 axA,out vec4 axB,out vec4 angA,out vec4 angB,out vec4 shellA,out vec4 shellB){')
anchor='    b=offset(3.*jm(childShell,childShell)-.45*filtered(jc(childLocal),12.,p)+1.1*angular36+1.1*jm(inv,inv),.345);'
source=change(source,anchor,anchor+'''
    // Omitted costs are nonnegative. These jets only certify free space.
    axA=offset(-.55*filtered(jc(local),4.,p)+1.6*jm(inv,inv),.38999);
    axB=offset(-.45*filtered(jc(childLocal),12.,p)+1.1*jm(inv,inv),.34499);
    angA=offset(.65*angular12+1.6*jm(inv,inv),-.16001);
    angB=offset(1.1*angular36+1.1*jm(inv,inv),-.10501);
    shellA=parentShell;shellB=childShell;''')
source=change(source,'   vec4 jmax(vec4 a,vec4 b)', '''   void fieldParts(vec3 p,out vec4 f,out vec4 a,out vec4 b){
    vec4 axA,axB,angA,angB,shellA,shellB;
    fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);
   }
   vec4 jmax(vec4 a,vec4 b)''')
start=source.index('   vec4 traceSample(')
end=source.index('\n\n   vec3 spectrum(',start)
trace='''   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b,axA,axB,angA,angB,shellA,shellB;float layer;
    fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);
    vec3 m=leafCurvature();float s=pixelScale;
    float parent=max(positiveReach(f,rd,m.x),positiveReach(a,rd,m.y));
    float child=max(positiveReach(offset(f,.3),rd,m.x),positiveReach(b,rd,m.z));
'''
for name,branch,i in [('axA','parent',0),('axB','child',1),('angA','parent',2),('angB','child',3),
    ('offset(1.6*shellA,-.32001)','parent',4),('offset(-1.6*shellA,-.32001)','parent',5),
    ('offset(1.128*shellB,-.211042)','child',6),('offset(-1.128*shellB,-.211042)','child',7)]:
    trace+=f'    {branch}=max({branch},positiveReach({name},rd,{poly(H[i])}));\n'
trace+='''    safeStep=min(min(parent,child),positiveReach(offset(f,10.),rd,m.x));
    return compose(f,a,b,layer);
   }'''
source=source[:start]+trace+source[end:]
save('continuum-v33r2-candidate.js',source)
for kind in ['candidate','leaves']:
    probe=(HERE/f'gpu_probe_v33_{kind}.html').read_text().replace('v33','v33r2')
    if kind=='leaves':
        probe=change(probe,' fieldParts(p,f,a,b);\n gl_FragColor=probeMode<.5?f:probeMode<1.5?a:probeMode<2.5?b:compose(f,a,b,layer);', ''' vec4 axA,axB,angA,angB,shellA,shellB;
 fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);
 gl_FragColor=probeMode<.5?f:probeMode<1.5?a:probeMode<2.5?b:probeMode<3.5?compose(f,a,b,layer):
 probeMode<4.5?axA:probeMode<5.5?axB:probeMode<6.5?angA:probeMode<7.5?angB:
 probeMode<8.5?offset(1.6*shellA,-.32001):probeMode<9.5?offset(-1.6*shellA,-.32001):
 probeMode<10.5?offset(1.128*shellB,-.211042):offset(-1.128*shellB,-.211042);''')
        probe=change(probe,'mode<4','mode<12')
        probe=change(probe,"['base','apertureA','apertureB','composed']", "['base','apertureA','apertureB','composed','axA','axB','angA','angB','shellAp','shellAn','shellBp','shellBn']")
    save(f'gpu_probe_v33r2_{kind}.html',probe)
save('centre-v33r2-build.json',json.dumps({'candidate':'continuum-v33r2-candidate.js',
    'sha256':hashlib.sha256(source.encode()).hexdigest(),'parent':'continuum-v33-candidate.js',
    'lower_H_upper':H.tolist(),'analytic':analytic,'state':'Unvalidated reach-only successor; no live changes'},indent=2)+'\n')
print(json.dumps({'lower_H_upper':H.tolist(),'lower_H_analytic':analytic['lower_H_polynomials']}))
