"""One-shot isolated tapered/curling petal cells, preserving live geometry."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
OUT=HERE/'continuum-v33-candidate.js'
assert not OUT.exists()
source=(HERE/'continuum-v32-candidate.js').read_text()
start=source.index('    // Two local coordinates bend')
end=source.index('\n   vec3 spectrum(',start)
source=source[:start]+'''
    // Separate tapered cells in angle, radius AND depth. Positive angular
    // and axial costs close every petal rim; no annular sheet is retained.
    vec4 r12=jm(r6,r6)-jm(i6,i6),i12=2.*jm(r6,i6);
    vec4 r36=jm(r18,r18)-jm(i18,i18),i36=2.*jm(r18,i18);
    vec4 radial=offset(1.35*radius+.12*z+.15*r6,-time*.12);
    vec4 local=offset(.9*z-.25*radius+.2*i6,-time*.19);
    vec4 sinLocal=jc(offset(local,-1.5707963267948966));
    vec4 curl=radial+.9*sinLocal;
    vec4 phase=offset(.7*sinLocal+.22*jc(radial),time*.2);
    vec4 child=offset(3.*curl+.35*jc(local),-time*.21);
    vec4 childLocal=3.*local+.4*jc(radial);
    vec4 childPhase=3.*phase+.3*jc(offset(childLocal,-1.5707963267948966));
    vec4 parentShell=filtered(jc(curl)-.6*jc(local),4.,p);
    vec4 childShell=filtered(jc(child)-.55*jc(childLocal),12.,p);
    if(high>.5)childShell+=.11*filtered(jc(3.*child+.25*r36),36.,p);
    vec4 angular12=jm(r6,r6)+jm(i6,i6)-filtered(turnPair(r12,i12,phase),4.,p);
    vec4 angular36=jm(r18,r18)+jm(i18,i18)-filtered(turnPair(r36,i36,childPhase),12.,p);
    f=offset(-radius,6.2)+.4*r6;
    a=offset(4.*jm(parentShell,parentShell)-.55*filtered(jc(local),4.,p)+.65*angular12+1.6*jm(inv,inv),.39);
    b=offset(3.*jm(childShell,childShell)-.45*filtered(jc(childLocal),12.,p)+1.1*angular36+1.1*jm(inv,inv),.345);
   }

   vec4 jmax(vec4 a,vec4 b){return a.w>b.w?a:b;}
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    vec4 parent=jmax(f,a),child=jmax(offset(f,.3),b),backing=offset(f,10.);
    vec4 result=parent;layer=0.;
    if(child.w<result.w){result=child;layer=1.;}
    if(backing.w<result.w){result=backing;layer=2.;}
    return result;
   }
   vec4 sheetSample(vec3 p){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);return compose(f,a,b,layer);
   }
   float envelope(vec3 p){
    float rho=length(vec3(p.xy-vec2(0.,1.7),.85*min(p.z+27.5,0.)));
    return max(0.,5.445-rho);
   }
   float raySlope(vec3 p,vec3 rd){return 185.+148.*pixelScale;}
   vec3 leafCurvature(){
    float s=pixelScale;
    return vec3(4.,388.,4321.)+vec3(1.,522.,6236.)*s+vec3(1.,468.,4990.)*s*s;
   }
   float positiveReach(vec4 leaf,vec3 rd,float curvature){
    if(leaf.w<=0.)return 0.;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);vec3 m=leafCurvature();
    float parent=max(positiveReach(f,rd,m.x),positiveReach(a,rd,m.y));
    float child=max(positiveReach(offset(f,.3),rd,m.x),positiveReach(b,rd,m.z));
    safeStep=min(min(parent,child),positiveReach(offset(f,10.),rd,m.x));
    return compose(f,a,b,layer);
   }
'''+source[end:]
OUT.write_text(source)
for kind in ['candidate','leaves']:
    target=HERE/f'gpu_probe_v33_{kind}.html'
    assert not target.exists()
    target.write_text((HERE/f'gpu_probe_v32_{kind}.html').read_text().replace('v32','v33'))
(HERE/'centre-v33-build.json').write_text(json.dumps({
    'candidate':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'parent':'continuum-v32-candidate.js','live_modified':False,
    'structure':'Closed tapered curled petal cells:12 angular parent petals and36 child petals, radial/depth3x coordinates; nonnegative angular/axial costs eliminate annular sheets; physical gaps',
    'clearance_lower_bound':5.8,'excluded_bright_axis_radius':2.78,'cap_begins_z':-27.5,
    'unchanged':'materials,2048/1536 budgets,14 bisections,.00015 residual,directional-depth gate,no forced minimum step,actual camera/shared clock',
    'state':'Unvalidated; no realism or promotion'},indent=2)+'\n')
print('Built isolated v33 closed petal cells; live files unchanged.')
