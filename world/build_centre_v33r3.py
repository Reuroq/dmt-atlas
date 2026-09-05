"""One-shot two-tier marcher build. No live edits or numerical acceptance."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
def save(name,source):
    assert not (HERE/name).exists(),name
    (HERE/name).write_text(source)
def change(source,old,new):
    assert source.count(old)==1,old[:100]
    return source.replace(old,new)
def digest(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

old=(HERE/'continuum-v33r2-candidate.js').read_text()
# Copy only the common axial construction, preserving operation order. Do not
# construct h12/h18/h36, shells, curl, angular phases or full a/b on this path.
prefix=old[old.index('    vec3 q=p-'):old.index('    vec4 r6=')]
cheap='''   void cheapParts(vec3 p,out vec4 f,out vec4 axA,out vec4 axB){
'''+prefix+'''    vec4 r6=jm(r3,r3)-jm(i3,i3),i6=2.*jm(r3,i3);
    vec4 radial=offset(1.35*radius+.12*z+.15*r6,-time*.12);
    vec4 local=offset(.9*z-.25*radius+.2*i6,-time*.19);
    vec4 childLocal=3.*local+.4*jc(radial);
    f=offset(-radius,6.2)+.4*r6;
    axA=offset(-.55*filtered(jc(local),4.,p)+1.6*jm(inv,inv),.38999);
    axB=offset(-.45*filtered(jc(childLocal),12.,p)+1.1*jm(inv,inv),.34499);
   }
   float cheapReach(vec3 p,vec3 rd){
    vec4 f,axA,axB;cheapParts(p,f,axA,axB);
    float s=pixelScale,m=leafCurvature().x;
    float parent=max(positiveReach(f,rd,m),positiveReach(axA,rd,6.+6.*s+10.*s*s));
    float child=max(positiveReach(offset(f,.3),rd,m),positiveReach(axB,rd,18.+36.*s+66.*s*s));
    return min(min(parent,child),positiveReach(offset(f,10.),rd,m));
   }

'''
skip='''     // This threshold selects a useful certificate; it never floors a step.
     float fastStep=cheapReach(p,rd);
     if(fastStep>.08){
      distanceAlong+=fastStep;havePrevious=false;
      if(distanceAlong>105.)break;
      continue;
     }
'''
source=change(old,'   vec4 traceSample(',cheap+'   vec4 traceSample(')
source=change(source,'     float safeStep;sampleValue=traceSample(p,rd,safeStep);',skip+'     float safeStep;sampleValue=traceSample(p,rd,safeStep);')
assert source.replace(cheap,'').replace(skip,'')==old
save('continuum-v33r3-candidate.js',source)

field=(HERE/'field_centre_v33r2.py').read_text()+'''

def cheap_parts(p,t,camera,pixel=PIXEL):
    """Independent scalar f/axial certificates; no full-field construction."""
    p=np.asarray(p,dtype=float)
    x,y,z=p[...,0],p[...,1]-1.7,p[...,2]
    den=x*x+y*y+2.25
    h6=((x+1j*y)*np.exp(.075j*t)/np.sqrt(den))**6
    rho=np.sqrt(x*x+y*y+.7225*np.minimum(z+27.5,0)**2)
    R=1.35*rho+.12*z+.15*h6.real-.12*t
    T=.9*z-.25*rho+.2*h6.imag-.19*t
    U=3*T+.4*np.cos(R)
    footprint2=pixel**2*np.sum((p-camera)**2,axis=-1)
    return np.stack([6.2-rho+.4*h6.real,
        .38999-.55*np.cos(T)*np.exp(-8*footprint2)+1.6/den,
        .34499-.45*np.cos(U)*np.exp(-72*footprint2)+1.1/den],axis=-1)
'''
save('field_centre_v33r3.py',field)

probe=(HERE/'gpu_probe_v33r2_candidate.html').read_text().replace('v33r2','v33r3')
probe=change(probe,"float iterations=0.;');", "float iterations=0.,cheapCalls=0.,fullCalls=0.,certifiedSkips=0.,refineCalls=0.;');")
anchor="fragment=fragment.slice(0,fragment.indexOf('    vec3 color;'))"
instrument='''fragment=fragment.replace('float fastStep=cheapReach(p,rd);','cheapCalls+=1.;float fastStep=cheapReach(p,rd);');
fragment=fragment.replace('distanceAlong+=fastStep;havePrevious=false;','certifiedSkips+=1.;distanceAlong+=fastStep;havePrevious=false;');
fragment=fragment.replace('float safeStep;sampleValue=traceSample(p,rd,safeStep);','fullCalls+=1.;float safeStep;sampleValue=traceSample(p,rd,safeStep);');
fragment=fragment.replace('float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;','refineCalls+=1.;float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;');
'''
probe=change(probe,anchor,instrument+anchor)
probe=change(probe,':vec4(p,length(p-ro)*pixelScale);',':probeMode<2.5?vec4(p,length(p-ro)*pixelScale):vec4(cheapCalls,fullCalls,certifiedSkips,refineCalls);')
# Return the original three-readback measurement before requesting counters.
probe=change(probe,' for(let mode=0;mode<3;mode++){',' const start=performance.now();\n for(let mode=0;mode<4;mode++){')
probe=change(probe,"output[['hits','gradientSlope','points'][mode]]=Array.from(pixels);", "output[['hits','gradientSlope','points','counts'][mode]]=Array.from(pixels);\n  if(mode===2)output.gpu_three_readbacks_seconds=(performance.now()-start)/1000;")
save('gpu_probe_v33r3_candidate.html',probe)

probe=(HERE/'gpu_probe_v33r2_leaves.html').read_text().replace('v33r2','v33r3')
probe=change(probe,' gl_FragColor=probeMode<.5?', ' vec4 cheapF,cheapA,cheapB;cheapParts(p,cheapF,cheapA,cheapB);\n gl_FragColor=probeMode<.5?')
probe=change(probe,':offset(-1.128*shellB,-.211042);',':probeMode<11.5?offset(-1.128*shellB,-.211042):probeMode<12.5?cheapF:probeMode<13.5?cheapA:cheapB;')
probe=change(probe,'mode<12','mode<15')
probe=change(probe,"'shellBn'][mode]","'shellBn','cheapF','cheapA','cheapB'][mode]")
save('gpu_probe_v33r3_leaves.html',probe)
prior=json.loads((HERE/'centre-v33r2-build.json').read_text())
save('centre-v33r3-build.json',json.dumps({
    'candidate':'continuum-v33r3-candidate.js','sha256':digest('continuum-v33r3-candidate.js'),
    'parent':'continuum-v33r2-candidate.js','parent_sha256':digest('continuum-v33r2-candidate.js'),
    'lower_H_upper':prior['lower_H_upper'],'analytic':prior['analytic'],
    'cheap_threshold':.08,'exact_parent_after_removing_insertions':True,
    'state':'IMPLEMENTED, numerically and visually UNVALIDATED; no live changes'},indent=2)+'\n')
print('Built isolated v33r3 shader, scalar reference and instrumented GPU fixtures; no probes run.')
