"""One-shot v25 rebuild. v24 filenames were diagnostic ablations, not runtime."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
assert not (HERE/'continuum-v25.js').exists(), 'Immutable archive already exists'
source = (HERE/'continuum.js').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == '5486919206afcc282f4428a3cb344f8123714b2392b6802bac79631860269ca3'
start = source.index('   // One connected, closed corolla:')
end = source.index('   vec3 spectrum', start)
source = source[:start] + '''   // A connected corolla with a deep ellipsoidal end beyond the walk exit.
   // Cartesian cap folds survive at the axis: no angular pole fan is used
   // as the centre's only geometry. All octaves displace the actual sheet.
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
    float x=.85*p.x,y=.85*p.y;
    float xx=1.7*p.x+time*.19,yy=1.7*p.y-time*.17;
    float warp=2.6*cos(x)*cos(y)+.75*sin(xx)*cos(yy);
    vec3 gw=vec3(-2.21*sin(x)*cos(y)+1.275*cos(xx)*cos(yy),
                 -2.21*cos(x)*sin(y)-1.275*sin(xx)*sin(yy),0.);
    float shear=1.8+.22*sin(time*.61);
    float v=p.z*.72+shear*u-time*.57+cw*warp;
    vec3 gv=vec3(0.,0.,.72)+shear*gu+gcw*warp+cw*gw;
    float petal=8.*a+.32*sin(v*.5+time*.31);
    vec3 gt=8.*ga+.16*cos(v*.5+time*.31)*gv;
    float phase=v+.65*pole*cos(petal);
    vec3 gphase=gv+.65*(gp*cos(petal)-pole*sin(petal)*gt);
    float f=u-1.18*sin(phase);
    vec3 g=gu-1.18*cos(phase)*gphase;
    phase=petal+.6*sin(v);gphase=gt+.6*cos(v)*gv;
    f-=.4*pole*cos(phase);
    g-=.4*(gp*cos(phase)-pole*sin(phase)*gphase);
    // Nested crossed lobes, continuous and nonzero at the cap axis.
    float cx=1.7*p.x+.4*sin(v),cy=1.7*p.y-.4*cos(v);
    vec3 gx=vec3(1.7,0.,0.)+.4*cos(v)*gv;
    vec3 gy=vec3(0.,1.7,0.)+.4*sin(v)*gv;
    f-=.28*cw*cos(cx)*cos(cy);
    g-=.28*(gcw*cos(cx)*cos(cy)-cw*(sin(cx)*cos(cy)*gx+cos(cx)*sin(cy)*gy));
    float plane=sin(.8*p.x)+cos(.8*p.y);
    vec3 gplane=vec3(.8*cos(.8*p.x),-.8*sin(.8*p.y),0.);
    float chart=pole*sin(petal)+cw*plane;
    vec3 gchart=gp*sin(petal)+pole*cos(petal)*gt+gcw*plane+cw*gplane;
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.18:(octave==1?.08:.035);
     float fv=octave==0?2.7:(octave==1?5.7:12.1);
     float fc=octave==0?2.:(octave==1?-4.:7.);
     float frequency=octave==0?30.:(octave==1?64.:130.);
     float q=footprint*frequency,weight=exp(-.5*q*q);
     vec3 gweight=-weight*frequency*frequency*footprint*footprintGradient;
     phase=fv*v+fc*chart;gphase=fv*gv+fc*gchart;
     f-=amplitude*weight*sin(phase);
     g-=amplitude*(gweight*sin(phase)+weight*cos(phase)*gphase);
    }
    return vec4(g,f);
   }
   float envelope(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,.45*min(p.z+27.5,0.)));
    // |displacement| <=2.155. Clearance >=4.84 for z>=-27.5.
    // Scaled z is a contraction, so this remains a safe world-space bound.
    return abs(rho-7.)-2.16;
   }
   float raySlope(vec3 p,vec3 rd){
    // Directional derivative bound throughout the next .4 world units.
    float transverse=length(rd.xy),crosswise=abs(rd.x)+abs(rd.y);
    float lower=max(0.,length(p.xy-vec2(0.,1.7))-.4*transverse);
    float poleSlope=transverse*(lower>1.15471?8.*lower/pow(4.+lower*lower,2.):.325);
    float angular=transverse*(lower>2.?lower/(4.+lower*lower):.25);
    bool cap=p.z-.4*abs(rd.z)<-27.5;
    float radial=cap?length(vec3(rd.xy,.45*rd.z)):transverse;
    float capSlope=cap?.325*abs(rd.z):0.;
    float meridian=.72*abs(rd.z)+(1.8+.22*sin(time*.61))*radial;
    if(cap)meridian+=3.35*capSlope+3.485*crosswise;
    float petalSlope=8.*angular+.16*meridian;
    float result=radial+1.18*(meridian+.65*(poleSlope+petalSlope));
    result+=.4*(poleSlope+petalSlope+.6*meridian);
    if(cap)result+=.28*(capSlope+1.7*crosswise+.8*meridian);
    float chartSlope=poleSlope+petalSlope;
    if(cap)chartSlope+=2.*capSlope+.8*crosswise;
    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;
    result+=.18*exp(-.5*pow(footprint*30.,2.))*(2.7*meridian+2.*chartSlope);
    result+=.08*exp(-.5*pow(footprint*64.,2.))*(5.7*meridian+4.*chartSlope);
    if(high>.5)result+=.035*exp(-.5*pow(footprint*130.,2.))*(12.1*meridian+7.*chartSlope);
    // Max filter derivative: sum(amplitude*frequency)*exp(-.5)<9.2.
    return result+9.2*pixelScale;
   }
''' + source[end:]
source = source.replace('if(abs(value)<.00015){hit=true;break;}', '''// Resolve within .08 pixel, capped at .0015 world units. This
     // avoids chasing subpixel grazing rims to floating-point exhaustion.
     // It is a local surface-distance estimate, not an exact-root proof.
     float tolerance=min(.0015,max(.00015,distanceAlong*pixelScale*.08));
     if(abs(value)<.00015 || abs(value)/max(1.,length(sampleValue.xyz))<tolerance){hit=true;break;}''')
start = source.index('     // Darken actual nearby re-entrant folds')
end = source.index('     float haze=', start)
source = source[:start] + '''     // Normalized local field clearance estimates smooth near-field AO.
     // Bounded ambient attenuation only; never square it across material.
     float side=sign(dot(sheetSample(p).xyz,normal)),occlusion=0.;
     for(int j=0;j<3;j++){
      float reach=.12*pow(2.4,float(j));
      vec4 nearby=sheetSample(p+normal*reach);
      float clearance=side*nearby.w/max(1.,length(nearby.xyz));
      occlusion+=pow(.5,float(j))*clamp(1.-clearance/reach,0.,1.);
     }
     float openness=1.-.24*occlusion/1.75;
     vec3 key=normalize(vec3(.6,.9,.7));
     float visibility=1.;
     for(int j=0;j<4;j++){
      float reach=.24*pow(1.9,float(j));
      vec4 blocker=sheetSample(p+normal*.07+key*reach);
      float clearance=side*blocker.w/max(1.,length(blocker.xyz));
      visibility=min(visibility,mix(.18,1.,smoothstep(-reach*.25,reach*.2,clearance)));
     }
     float light=max(0.,dot(normal,key));
     // Emission and broad environment reflection are independent of key
     // visibility. Only diffuse/specular light from that key is shadowed.
     color=pigment*(.19+(.16+.12*facing)*openness+.68*light*visibility);
     color+=reflected*(.25+.55*fresnel)*mix(.85,1.,openness);
     color+=mix(pigment,vec3(1.),.4)*pow(max(0.,dot(reflect(rd,normal),key)),9.)*.42*visibility;
''' + source[end:]
(HERE/'continuum.js').write_text(source)
(HERE/'continuum-v25.js').write_text(source)
print('v25', hashlib.sha256(source.encode()).hexdigest())
