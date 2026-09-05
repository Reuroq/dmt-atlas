"""One-shot cheaper crossed-fold field; never mutate live assets or old evidence."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = HERE / 'continuum-v28-candidate.js'
assert not out.exists()
source = (HERE / 'continuum-v27r2-candidate.js').read_text()
start = source.index('   // A connected corolla')
end = source.index('   vec3 spectrum', start)
replacement = r'''   // Connected corolla: same envelope/clearance, simpler crossed folds.
   // Every octave displaces geometry. No angular high-frequency side chart.
   vec4 sheetSample(vec3 p){
    vec3 toEye=p-cameraWorld[3].xyz;
    float footprint=length(toEye)*pixelScale;
    vec3 footprintGradient=normalize(toEye)*pixelScale;
    p.y-=1.7;
    float r=length(p.xy),cap=min(p.z+27.5,0.);
    float rho=length(vec2(r,.45*cap)),u=rho-7.;
    vec3 gu=vec3(p.xy,.2025*cap)/max(rho,.00001);
    float a=atan(p.y,p.x)-time*.065;
    vec3 ga=vec3(-p.y,p.x,0.)/max(r*r,.0000001);
    float pole=r*r/(r*r+4.);
    vec3 gp=vec3(8.*p.xy,0.)/pow(r*r+4.,2.);
    float cw=cap*cap/(cap*cap+4.);
    vec3 gcw=vec3(0.,0.,8.*cap/pow(cap*cap+4.,2.));
    float wx=.65*p.x+time*.11,wy=.65*p.y-time*.09;
    float warp=2.6*preciseCos(wx)*preciseCos(wy);
    vec3 gw=-1.69*vec3(preciseSin(wx)*preciseCos(wy),preciseCos(wx)*preciseSin(wy),0.);
    float shear=1.8+.22*preciseSin(time*.61);
    float v=p.z*.72+shear*u-time*.57+cw*warp;
    vec3 gv=vec3(0.,0.,.72)+shear*gu+gcw*warp+cw*gw;
    float petal=8.*a+.32*preciseSin(v*.5+time*.31);
    vec3 gt=8.*ga+.16*preciseCos(v*.5+time*.31)*gv;
    float phase=v+.65*pole*preciseCos(petal);
    vec3 gphase=gv+.65*(gp*preciseCos(petal)-pole*preciseSin(petal)*gt);
    float f=u-1.18*preciseSin(phase);
    vec3 g=gu-1.18*preciseCos(phase)*gphase;
    phase=petal+.6*preciseSin(v);gphase=gt+.6*preciseCos(v)*gv;
    f-=.4*pole*preciseCos(phase);
    g-=.4*(gp*preciseCos(phase)-pole*preciseSin(phase)*gphase);
    float cx=1.7*p.x+time*.07,cy=1.7*p.y-time*.09;
    float crossed=preciseCos(cx)*preciseCos(cy);
    vec3 gcross=-1.7*vec3(preciseSin(cx)*preciseCos(cy),preciseCos(cx)*preciseSin(cy),0.);
    f-=.28*cw*crossed;g-=.28*(gcw*crossed+cw*gcross);
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.30:(octave==1?.15:.07);
     float k=octave==0?1.3:(octave==1?2.9:6.1);
     float frequency=octave==0?6.:(octave==1?13.:28.);
     float q=footprint*frequency,weight=exp(-.5*q*q);
     vec3 gweight=-weight*frequency*frequency*footprint*footprintGradient;
     // Three-dimensional crossed lobes continue from side to cap without a
     // chart blend. Fixed world frequencies avoid nested phase amplification.
     vec3 phase3=k*vec3(p.xy,.7*p.z)+vec3(time*.07,-time*.09,-time*.13);
     vec3 c=preciseCos(phase3);
     vec3 s=vec3(preciseSin(phase3.x),preciseSin(phase3.y),preciseSin(phase3.z));
     float wave=c.x*c.y*c.z;
     vec3 gwave=-k*vec3(s.x*c.y*c.z,c.x*s.y*c.z,.7*c.x*c.y*s.z);
     f-=amplitude*weight*wave;
     g-=amplitude*(gweight*wave+weight*gwave);
    }
    return vec4(g,f);
   }
   float envelope(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,.45*min(p.z+27.5,0.)));
    // Total displacement <=1.18+.4+.28+.30+.15+.07=2.38.
    // Clearance >=4.615 before z=-27.5, beyond physical exit -22.
    return abs(rho-7.)-2.385;
   }
   float raySlope(vec3 p,vec3 rd){
    // Directional bound throughout the next .4 world units. For a product
    // of cosines the unscaled gradient norm <=1 (also in three dimensions).
    float transverse=length(rd.xy);
    float lower=max(0.,length(p.xy-vec2(0.,1.7))-.4*transverse);
    float poleSlope=transverse*(lower>1.15471?8.*lower/pow(4.+lower*lower,2.):.325);
    float angular=transverse*(lower>2.?lower/(4.+lower*lower):.25);
    float capLo=max(0.,-p.z-27.5-.4*abs(rd.z));
    float capHi=max(0.,-p.z-27.5+.4*abs(rd.z));
    float cwHi=capHi*capHi/(capHi*capHi+4.);
    float capSlope=capHi>0.?abs(rd.z)*(capLo>1.15471?8.*capLo/pow(4.+capLo*capLo,2.):.325):0.;
    float radial=capHi>0.?length(vec3(rd.xy,.45*rd.z)):transverse;
    float meridian=.72*abs(rd.z)+(1.8+.22*preciseSin(time*.61))*radial;
    meridian+=2.6*capSlope+cwHi*1.69*transverse;
    float petalSlope=8.*angular+.16*meridian;
    float result=radial+1.18*(meridian+.65*(poleSlope+petalSlope));
    result+=.4*(poleSlope+petalSlope+.6*meridian);
    result+=.28*(capSlope+cwHi*1.7*transverse);
    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;
    float crossedSlope=length(vec3(rd.xy,.7*rd.z));
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.30:(octave==1?.15:.07);
     float frequency=octave==0?6.:(octave==1?13.:28.);
     float k=octave==0?1.3:(octave==1?2.9:6.1);
     result+=amplitude*exp(-.5*pow(footprint*frequency,2.))*k*crossedSlope;
    }
    // Same global Gaussian-filter derivative bound as v27r2.
    return result+3.47*pixelScale;
   }
'''
source = source[:start] + replacement + source[end:]
out.write_text(source)
(HERE/'gpu_probe_v28_candidate.html').write_text((HERE/'gpu_probe_v27r2_candidate.html').read_text().replace('v27r2','v28'))
probe = (HERE/'probe_numeric_candidate_v27r2.py').read_text().replace('v27r2','v28').replace('field_centre_v27','field_centre_v28')
(HERE/'probe_numeric_candidate_v28.py').write_text(probe)
print('Created isolated v28. Live unchanged; numeric and visual gates pending.')
