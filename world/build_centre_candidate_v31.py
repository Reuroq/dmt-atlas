"""One-shot swept complex-harmonic flower; isolated, no live edits."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
OUT=HERE/'continuum-v31-candidate.js'
assert not OUT.exists()
source=(HERE/'continuum-v30-candidate.js').read_text()
start=source.index('   void fieldParts(')
end=source.index('   vec3 spectrum(',start)
source=source[:start]+'''
   // Complex powers of (x+iy)/sqrt(x*x+y*y+2.25): smooth at the axis,
   // global rotational hierarchy, no atan seam and no Cartesian lattice.
   vec4 jis(vec4 v){float s=inversesqrt(v.w);return vec4(-.5*s*s*s*v.xyz,s);}
   void cubePair(vec4 x,vec4 y,out vec4 a,out vec4 b){
    vec4 xx=jm(x,x),yy=jm(y,y);
    a=jm(x,xx-3.*yy);b=jm(y,3.*xx-yy);
   }
   vec4 turnPair(vec4 a,vec4 b,vec4 phase){
    return jm(a,jc(phase))-jm(b,jc(offset(phase,-1.5707963267948966)));
   }
   void fieldParts(vec3 p,out vec4 f,out vec4 a,out vec4 b){
    vec3 q=p-vec3(0.,1.7,0.);
    float angle=time*.075,c=preciseCos(angle),s=preciseSin(angle);
    vec4 x=vec4(c,-s,0.,c*q.x-s*q.y),y=vec4(s,c,0.,s*q.x+c*q.y);
    vec4 z=vec4(0.,0.,1.,q.z);
    float cap=min(q.z+27.5,0.),rho=length(vec3(q.xy,.85*cap));
    vec4 radius=vec4(vec3(q.xy,.7225*cap)/max(rho,.00001),rho);
    vec4 inv=jis(offset(jm(x,x)+jm(y,y),2.25));
    vec4 u=jm(x,inv),v=jm(y,inv),r3,i3;
    cubePair(u,v,r3,i3);
    vec4 r6=jm(r3,r3)-jm(i3,i3),i6=2.*jm(r3,i3),r18,i18;
    cubePair(r6,i6,r18,i18);
    // Radially swept angular fins: the parent physically bends each child.
    vec4 petal=turnPair(r6,i6,offset(.24*radius+.10*z+.65*r6,-time*.21));
    vec4 branch=turnPair(r18,i18,offset(.38*radius+.19*z+1.1*petal,-time*.33));
    vec4 w=filtered(petal,3.,p);
    f=offset(-radius,5.95)+.9*r6+.15*w;
    // The smooth core excludes the axis from both bright leaf families.
    a=w+.675*jm(inv,inv);
    b=filtered(branch,8.,p);
    if(high>.5){
     vec4 r54,i54;cubePair(r18,i18,r54,i54);
     vec4 fine=turnPair(r54,i54,offset(.7*radius+.32*z+.8*r18,-time*.47));
     b+=.25*filtered(fine,20.,p);
    }
   }
   vec4 ja(vec4 a){return vec4(sign(a.w)*a.xyz,abs(a.w));}
   vec4 jmax(vec4 a,vec4 b){return a.w>b.w?a:b;}
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    vec4 aa=ja(a),bb=ja(b);
    vec4 petals=jmax(f,jmax(offset(aa,-.065),offset(-bb,.16)));
    vec4 branches=jmax(offset(f,.45),jmax(offset(aa,-.18),offset(bb,-.03)));
    vec4 backing=offset(f,12.);
    vec4 result=petals;layer=0.;
    if(branches.w<result.w){result=branches;layer=1.;}
    if(backing.w<result.w){result=backing;layer=2.;}
    return result;
   }
   vec4 sheetSample(vec3 p){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);return compose(f,a,b,layer);
   }
   float envelope(vec3 p){
    float rho=length(vec3(p.xy-vec2(0.,1.7),.85*min(p.z+27.5,0.)));
    return max(0.,4.895-rho);
   }
   float raySlope(vec3 p,vec3 rd){return 12.+10.*pixelScale;}
   vec3 leafCurvature(){
    float s=pixelScale;
    return vec3(11.,22.,140.)+vec3(2.,13.,140.)*s+vec3(2.,10.,170.)*s*s;
   }
   float positiveReach(vec4 leaf,vec3 rd,float curvature){
    if(leaf.w<=0.)return 0.;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   float excludedBandReach(vec4 leaf,float halfWidth,vec3 rd,float curvature){
    return min(positiveReach(offset(leaf,halfWidth),rd,curvature),
               positiveReach(offset(-leaf,halfWidth),rd,curvature));
   }
   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);
    vec4 aa=ja(a),bb=ja(b);vec3 m=leafCurvature();
    float petals=max(positiveReach(f,rd,m.x),max(positiveReach(offset(aa,-.065),rd,m.y),excludedBandReach(b,.16,rd,m.z)));
    float branches=max(positiveReach(offset(f,.45),rd,m.x),max(positiveReach(offset(aa,-.18),rd,m.y),positiveReach(offset(bb,-.03),rd,m.z)));
    safeStep=min(min(petals,branches),positiveReach(offset(f,12.),rd,m.x));
    return compose(f,a,b,layer);
   }
'''+source[end:]
source=source.replace('float hue=.067*p.z+.21*openingA.w+.16*openingB.w+time*.023;',
    'float hue=.032*p.z+.14*length(p.xy-vec2(0.,1.7))+.24*openingB.w+time*.012;')
source=source.replace('mix(180.,35.,roughness)','mix(420.,120.,roughness)')
source=source.replace('color+=pigment*(.14+.34*diffuse*openness);',
    'color+=pigment*(.18+.28*diffuse*openness);')
source=source.replace('color=color*.045','color=color*.009')
OUT.write_text(source)
for kind in ['candidate','leaves']:
    target=HERE/f'gpu_probe_v31_{kind}.html'
    assert not target.exists()
    target.write_text((HERE/f'gpu_probe_v30_{kind}.html').read_text().replace('v30','v31'))
(HERE/'centre-v31-build.json').write_text(json.dumps({
    'candidate':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'parent':'continuum-v30-candidate.js','live_modified':False,
    'structure':'Regularized complex 6/18/54-fold swept petal fins; nested phase bending and true split/branch volumes; excluded bright axis, deeper dark backing',
    'clearance_lower_bound':4.9,'cap_begins_z':-27.5,
    'cost_change':'Per-leaf curvature reaches 11/22/140 instead of shared160; algebraic powers replace Cartesian rose products',
    'unchanged':'2048/1536 budgets,14 bisections,.00015 residual,no forced minimum step,actual camera and shared clock',
    'state':'Unvalidated; no realism or promotion'},indent=2)+'\n')
print('Built isolated v31 swept hierarchical flower; no live changes.')
