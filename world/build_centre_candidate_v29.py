"""One-shot perforated, nested membrane successor. Never edits live assets."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE/'continuum-v29-candidate.js'
assert not OUT.exists(), 'Preserve candidate history'
source = (HERE/'continuum-v28r3-candidate.js').read_text()
start = source.index('   // Connected corolla:')
end = source.index('   void main(){', start)
geometry = '''
   // Jets carry analytic Cartesian gradients in xyz, scalar value in w.
   // No angular chart or radial colour fan at the cap's axis.
   vec4 jc(vec4 q){return vec4(-preciseSin(q.w)*q.xyz,preciseCos(q.w));}
   vec4 jm(vec4 a,vec4 b){return vec4(a.xyz*b.w+b.xyz*a.w,a.w*b.w);}
   vec4 offset(vec4 a,float b){return vec4(a.xyz,a.w+b);}
   vec4 rose(vec4 x,vec4 y,float k){
    return (jc(k*x)+jc(k*(.5*x+.866025403784*y))+jc(k*(-.5*x+.866025403784*y)))/3.;
   }
   vec4 filtered(vec4 a,float frequency,vec3 p){
    vec3 delta=p-cameraWorld[3].xyz;
    float q=frequency*pixelScale,w=exp(-.5*q*q*dot(delta,delta));
    return jm(a,vec4(-q*q*w*delta,w));
   }
   void fieldParts(vec3 p,out vec4 f,out vec4 holeA,out vec4 holeB){
    vec3 q=p-vec3(0.,1.7,0.);
    float angle=time*.065,c=preciseCos(angle),s=preciseSin(angle);
    vec4 x=vec4(c,-s,0.,c*q.x-s*q.y),y=vec4(s,c,0.,s*q.x+c*q.y);
    vec4 z=vec4(0.,0.,1.,q.z);
    float cap=min(q.z+27.5,0.),rho=length(vec3(q.xy,.45*cap));
    vec4 radial=vec4(vec3(q.xy,.2025*cap)/max(rho,.00001),rho-7.);
    // Each finer rosette is phase-modulated by its parent, and displaces
    // actual geometry. This is not pigment/noise counted as hierarchy.
    vec4 r0=jm(rose(x,y,.62),jc(offset(.24*z,-time*.30)));
    vec4 r1=jm(rose(x,y,1.65),jc(offset(.58*z+1.2*r0,-time*.36)));
    vec4 r2=jm(rose(x,y,4.4),jc(offset(1.1*z+1.1*r1,-time*.41)));
    vec4 w1=filtered(r1,4.,p),w2=filtered(r2,11.,p);
    f=radial-.86*jc(offset(.68*z+1.1*r0,-time*.48))-.55*r0-.32*w1-.14*w2;
    if(high>.5){
     vec4 r3=jm(rose(x,y,11.7),jc(offset(2.3*z+.9*r2,-time*.47)));
     f-=.06*filtered(r3,27.,p);
    }
    // Positive hole fields remove material, exposing another membrane
    // 2.6 units farther out and a real dark backing 6 units farther out.
    holeA=offset(w1,-.05);
    holeB=offset(w2+.35*r0,-.14);
   }
   vec4 membrane(vec4 f,float centre,float thickness,vec4 hole){
    vec4 a=offset(f,-centre);
    vec4 shell=vec4(sign(a.w)*a.xyz,abs(a.w)-thickness);
    return shell.w>hole.w?shell:hole;
   }
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    vec4 first=membrane(f,0.,.14,a),second=membrane(f,2.6,.18,b);
    vec4 backing=offset(-f,6.);
    vec4 result=first;layer=0.;
    if(second.w<result.w){result=second;layer=1.;}
    if(backing.w<result.w){result=backing;layer=2.;}
    return result;
   }
   vec4 sheetSample(vec3 p){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);return compose(f,a,b,layer);
   }
   float envelope(vec3 p){
    float rho=length(vec3(p.xy-vec2(0.,1.7),.45*min(p.z+27.5,0.)));
    // Displacement <=1.93, inner half-thickness .14: rho>=4.93.
    // Clearance holds before the cap, beyond the physical exit at -22.
    return max(0.,4.925-rho);
   }
   float raySlope(vec3 p,vec3 rd){return 12.+12.*pixelScale;}
   float positiveReach(vec4 leaf,vec3 rd){
    if(leaf.w<=0.)return 0.;
    // New v29 leaf bound; NEVER apply a smooth Hessian bound to CSG max/min.
    // For shells this is valid until |f-centre| reaches thickness, before
    // the abs cusp. See centre-v29-bounds.md for CSG first-entry reasoning.
    float curvature=100.+160.*pixelScale+400.*pixelScale*pixelScale;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   float membraneReach(vec4 f,float centre,float thickness,vec4 hole,vec3 rd){
    vec4 a=offset(f,-centre);
    vec4 shell=vec4(sign(a.w)*a.xyz,abs(a.w)-thickness);
    // Both constraints must be nonpositive to enter this intersection.
    return max(positiveReach(shell,rd),positiveReach(hole,rd));
   }
   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);
    safeStep=min(membraneReach(f,0.,.14,a,rd),membraneReach(f,2.6,.18,b,rd));
    // To enter a union, any component can be the first encountered.
    safeStep=min(safeStep,positiveReach(offset(-f,6.),rd));
    return compose(f,a,b,layer);
   }
   vec3 spectrum(float x){return .5+.5*preciseCos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d,float roughness){
    // Small HDR reflection sources over a genuinely dark environment.
    // Distinct sharp glints and dim fill replace broad wax-like gradients.
    float power=mix(180.,35.,roughness);
    vec3 warm=normalize(vec3(-.7,.5,.4)),cool=normalize(vec3(.6,-.3,.7));
    vec3 rim=normalize(vec3(.1,.8,-.6));
    vec3 light=vec3(.0015,.002,.004);
    light+=vec3(8.,4.2,.8)*pow(max(0.,dot(d,warm)),power);
    light+=vec3(.7,4.8,9.)*pow(max(0.,dot(d,cool)),power*.7);
    light+=vec3(4.,.2,1.4)*pow(max(0.,dot(d,rim)),power*.5);
    light+=vec3(.07,.025,.008)*pow(max(0.,dot(d,warm)),3.);
    light+=vec3(.008,.035,.09)*pow(max(0.,dot(d,cool)),3.);
    return light;
   }
'''
source = source[:start]+geometry+source[end:]
source = source.replace('sampleValue=sheetSample(p);', 'float safeStep;sampleValue=traceSample(p,rd,safeStep);', 1)
start = source.index('     // Both steps bound field change')
end = source.index('     previousAlong=', start)
source = source[:start]+'''     // Conservative first-entry CSG leaf reach; no forced minimum step.
     float stepSize=safeStep;
'''+source[end:]
start = source.index('     float a=atan(')
end = source.index('     vec4 clip=', start)
source = source[:start]+'''     vec4 base,openingA,openingB;float layer;
     fieldParts(p,base,openingA,openingB);compose(base,openingA,openingB,layer);
     float facing=max(0.,dot(normal,-rd));
     float hue=.10*p.z+.16*preciseCos(.42*p.x)*preciseCos(.42*(p.y-1.7))+time*.018;
     vec3 pigment=pow(spectrum(hue),vec3(1.8));
     // Metallic F0 retains saturated colour, with angle-dependent thin-film
     // tint. Layer selection follows actual intersections, never a hole mask.
     vec3 metal=mix(vec3(.55),pigment,.72);
     float fresnel=pow(1.-facing,5.);
     vec3 film=mix(metal,spectrum(hue+.22*(1.-facing)),.25);
     vec3 reflected=radiance(reflect(rd,normal),.10+.10*(1.-facing));
     float openness=1.;
     for(int j=0;j<3;j++){
      float reach=.08*pow(3.,float(j));
      vec4 nearby=sheetSample(p+normal*reach);
      float clearance=nearby.w/max(1.,length(nearby.xyz));
      openness-=.18*pow(.55,float(j))*clamp(1.-clearance/reach,0.,1.);
     }
     vec3 key=normalize(vec3(.6,.9,.7));
     float diffuse=max(0.,dot(normal,key));
     color=reflected*mix(film,vec3(1.),fresnel)*openness;
     color+=pigment*(.026+.11*diffuse*openness);
     // The third surface is a recessed, low-radiance backing, not a miss
     // painted black or evidence that numerical failure makes an opening.
     if(layer>1.5)color=color*.045+vec3(.0005,.0007,.001);
     float haze=1.-exp(-distanceAlong*.002);
     color=mix(color,vec3(.001,.0007,.002),haze);
'''+source[end:]
source = source.replace('// Miss fallback is not evidence of an opening in the closed corolla.', '// A miss remains a numerical failure, not evidence of an aperture.')
source = source.replace('color=vec3(.001,.0005,.003)+vec3(.14,.025,.002)*exp(-45.*length(rd.xy));', 'color=vec3(.001,.0005,.003);')
OUT.write_text(source)
probe_html = (HERE/'gpu_probe_v28r3_candidate.html').read_text().replace('v28r3','v29')
(HERE/'gpu_probe_v29_candidate.html').write_text(probe_html)
probe = (HERE/'probe_numeric_candidate_v28r3.py').read_text().replace('v28r3','v29').replace('field_centre_v28','field_centre_v29')
(HERE/'probe_numeric_candidate_v29.py').write_text(probe)
print('Created isolated v29: nested perforated membranes, Cartesian hierarchy, metallic lighting; NOT validated or promoted.')
