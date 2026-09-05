"""One-shot volumetric petal-network successor. No live assets modified."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
OUT = HERE/'continuum-v30-candidate.js'
assert not OUT.exists(), 'Preserve candidate history'
source = (HERE/'continuum-v29-candidate.js').read_text()
start = source.index('   void fieldParts(')
end = source.index('   vec3 spectrum(', start)
source = source[:start]+'''
   // Three smooth jets; abs/max/min are composed explicitly below.
   // Occupied material is a branching volume, NOT coaxial membranes.
   void fieldParts(vec3 p,out vec4 f,out vec4 a,out vec4 b){
    vec3 q=p-vec3(0.,1.7,0.);
    float angle=time*.075,c=preciseCos(angle),s=preciseSin(angle);
    vec4 x=vec4(c,-s,0.,c*q.x-s*q.y),y=vec4(s,c,0.,s*q.x+c*q.y);
    vec4 z=vec4(0.,0.,1.,q.z);
    float cap=min(q.z+27.5,0.),rho=length(vec3(q.xy,.85*cap));
    vec4 radial=vec4(-vec3(q.xy,.7225*cap)/max(rho,.00001),5.95-rho);
    // Every level controls physical zero sets, with the parent changing
    // the child's phase. Sixfold Cartesian symmetry has no polar-axis seam.
    vec4 r0=jm(rose(x,y,.46),jc(offset(.28*z,-time*.31)));
    vec4 r1=jm(rose(x,y,1.25),jc(offset(.72*z+r0,-time*.43)));
    vec4 r2=jm(rose(x,y,3.4),jc(offset(1.45*z+.9*r1,-time*.57)));
    vec4 w1=filtered(r1,4.,p),w2=filtered(r2,10.,p);
    f=radial+.35*r0+.12*w1;
    a=w1+.24*w2;
    b=w2;
    if(high>.5){
     vec4 r3=jm(rose(x,y,9.1),jc(offset(2.8*z+.8*r2,-time*.71)));
     b+=.24*filtered(r3,26.,p);
    }
   }
   vec4 ja(vec4 a){return vec4(sign(a.w)*a.xyz,abs(a.w));}
   vec4 jmax(vec4 a,vec4 b){return a.w>b.w?a:b;}
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    // Split broad petals by true openings, then grow finer transverse
    // branches across the gaps. Both extend throughout the outer volume.
    vec4 aa=ja(a),bb=ja(b);
    vec4 petals=jmax(f,jmax(offset(aa,-.19),offset(-bb,.10)));
    vec4 branches=jmax(offset(f,.32),jmax(offset(aa,-.40),offset(bb,-.055)));
    vec4 backing=offset(f,9.);
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
    // Total radial modulation <=.47: first material rho>=5.48.
    return max(0.,5.475-rho);
   }
   float raySlope(vec3 p,vec3 rd){return 13.+12.*pixelScale;}
   float positiveReach(vec4 leaf,vec3 rd){
    if(leaf.w<=0.)return 0.;
    // Smooth-leaf bound only, never a Hessian claim for CSG creases.
    float curvature=160.+250.*pixelScale+600.*pixelScale*pixelScale;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   float excludedBandReach(vec4 leaf,float halfWidth,vec3 rd){
    // halfWidth-|leaf| is a MIN of two smooth leaves. Bound each arm:
    // its cusp lies in free space, so treating it as a smooth leaf is invalid.
    return min(positiveReach(offset(leaf,halfWidth),rd),
               positiveReach(offset(-leaf,halfWidth),rd));
   }
   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);
    vec4 aa=ja(a),bb=ja(b);
    // Positive |leaf|-width reaches its zero before its cusp, so the
    // active smooth arm suffices for those ordinary band constraints.
    float petals=max(positiveReach(f,rd),max(positiveReach(offset(aa,-.19),rd),excludedBandReach(b,.10,rd)));
    float branches=max(positiveReach(offset(f,.32),rd),max(positiveReach(offset(aa,-.40),rd),positiveReach(offset(bb,-.055),rd)));
    safeStep=min(min(petals,branches),positiveReach(offset(f,9.),rd));
    return compose(f,a,b,layer);
   }
'''+source[end:]
source=source.replace('float hue=.10*p.z+.16*preciseCos(.42*p.x)*preciseCos(.42*(p.y-1.7))+time*.018;',
    'float hue=.067*p.z+.21*openingA.w+.16*openingB.w+time*.023;')
source=source.replace('color+=pigment*(.026+.11*diffuse*openness);',
    'color+=pigment*(.14+.34*diffuse*openness);')
source=source.replace('// The third surface is a recessed, low-radiance backing, not a miss',
    '// The outer backing is reached through real gaps in the petal volume, not a miss')
OUT.write_text(source)
for name in ['gpu_probe_v29_candidate.html','gpu_probe_v29_leaves.html']:
    target=HERE/name.replace('v29','v30')
    assert not target.exists()
    target.write_text((HERE/name).read_text().replace('v29','v30'))
(HERE/'centre-v30-build.json').write_text(json.dumps({
    'candidate':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'parent':'continuum-v29-candidate.js','live_modified':False,
    'structure':'Volumetric split petals and transverse nested branches, replacing two coaxial sheets',
    'clearance_lower_bound':5.48,'cap_begins_z':-27.5,
    'unchanged':'2048/1536 budgets,14 bisections,.00015 residual,no forced minimum step,actual camera and shared clock',
    'state':'Unvalidated; no visual grade or promotion',
},indent=2)+'\n')
print('Built isolated v30 branching petal volume; no live changes.')
