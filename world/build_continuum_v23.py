"""Build v23 once from immutable v22; no changes to route or provenance."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE/'continuum-v22.js').read_text()

def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)

replace('float pole=r*r/(r*r+1.);', 'float pole=r*r/(r*r+4.);')
replace('vec3 gp=vec3(2.*p.xy,0.)/pow(r*r+1.,2.);', 'vec3 gp=vec3(8.*p.xy,0.)/pow(r*r+4.,2.);')
replace('    float v=p.z*.84+shear*u-time*.65;\n    vec3 gv=vec3(0.,0.,.84)+shear*gu;', '''    // Smooth axial meridian warp creates rounded nested folds at the cap.
    // It and its first derivative vanish at the tube/cap join, beyond exit.
    float capWeight=cap*cap/(cap*cap+4.),dome=exp(-.10*r*r);
    vec3 gdome=5.*dome*vec3(-.20*p.xy*capWeight,8.*cap/pow(cap*cap+4.,2.));
    float v=p.z*.84+shear*u-time*.65+5.*capWeight*dome;
    vec3 gv=vec3(0.,0.,.84)+shear*gu+gdome;''')
replace('phase=3.*v-2.*petal+.35*sin(petal+v);', 'phase=2.*v-petal+.6*sin(petal+v);')
replace('gphase=3.*gv-2.*gt+.35*cos(petal+v)*(gt+gv);', 'gphase=2.*gv-gt+.6*cos(petal+v)*(gt+gv);')
replace('f-=.22*pole*sin(phase);', 'f-=.32*pole*sin(phase);')
replace('g-=.22*(gp*sin(phase)+pole*cos(phase)*gphase);', 'g-=.32*(gp*sin(phase)+pole*cos(phase)*gphase);')
replace('float amplitude=octave==0?.085:(octave==1?.028:.010);', 'float amplitude=octave==0?.14:(octave==1?.06:.022);')
replace('float fv=octave==0?8.:(octave==1?21.:55.);', 'float fv=octave==0?2.8:(octave==1?6.5:14.);')
replace('float fa=octave==0?4.:(octave==1?-8.:16.);', 'float fa=octave==0?1.:(octave==1?2.:-4.);')
replace('float frequency=octave==0?32.:(octave==1?72.:180.);', 'float frequency=octave==0?14.:(octave==1?32.:64.);')
replace('''    // Total displacement <=2.143 plus .055 thickness: radial clearance
    // >=4.802 before the rounded cap begins, 5.5 units beyond the exit.
    return abs(rho-7.)-2.198;''', '''    // Displacement <=2.342, reserve .008: clearance >=4.65 before cap.
    // All new axial folding starts at -27.5, beyond the physical exit -22.
    return abs(rho-7.)-2.35;''')
replace('lower>.57736?2.*lower/pow(1.+lower*lower,2.):.65', 'lower>1.15471?8.*lower/pow(4.+lower*lower,2.):.325')
replace('lower>1.?lower/(1.+lower*lower):.5', 'lower>2.?lower/(4.+lower*lower):.25')
replace('    float petalSlope=10.*angular+.14*meridian;', '''    if(p.z-.4*abs(rd.z)<-27.5){
     float domeRadial=lower>2.23607?.2*lower*exp(-.1*lower*lower):.27126;
     meridian+=5.*(domeRadial*transverse+.325*exp(-.1*lower*lower)*abs(rd.z));
    }
    float petalSlope=10.*angular+.14*meridian;''')
replace('''    result+=.22*(poleSlope+3.*meridian+2.*petalSlope+.35*(petalSlope+meridian));
    result+=.085*(poleSlope+8.*meridian+4.*petalSlope);
    result+=.028*(poleSlope+21.*meridian+8.*petalSlope);
    if(high>.5)result+=.010*(poleSlope+55.*meridian+16.*petalSlope);''', '''    result+=.32*(poleSlope+2.*meridian+petalSlope+.6*(petalSlope+meridian));
    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;
    result+=.14*exp(-.5*pow(footprint*14.,2.))*(poleSlope+2.8*meridian+petalSlope);
    result+=.06*exp(-.5*pow(footprint*32.,2.))*(poleSlope+6.5*meridian+2.*petalSlope);
    if(high>.5)result+=.022*exp(-.5*pow(footprint*64.,2.))*(poleSlope+14.*meridian+4.*petalSlope);''')
start=source.index('   vec3 radiance(')
end=source.index('   void main(){', start)
source=source[:start]+'''   vec3 radiance(vec3 d,float roughness){
    // Broad spherical area-light lobes: no periodic angular bands/seams.
    float power=mix(5.,1.4,roughness),energy=1./(1.+2.*roughness);
    vec3 jewel=vec3(.008,.012,.024);
    jewel+=vec3(1.4,.46,.07)*pow(max(0.,dot(d,normalize(vec3(-.7,.5,.4)))),power);
    jewel+=vec3(.08,.75,1.3)*pow(max(0.,dot(d,normalize(vec3(.6,-.3,.7)))),power);
    jewel+=vec3(.7,.09,.45)*pow(max(0.,dot(d,normalize(vec3(.1,.8,-.6)))),power);
    return jewel*energy;
   }
'''+source[end:]
replace('i<1024', 'i<2048')
replace('i>=768', 'i>=1536')
start=source.index('     if(abs(value)<.065){')
end=source.index('     previousAlong=',start)
source=source[:start]+'''     // No Newton root acceptance: every forward step retains the bound.
     // Residual tolerance and floating-point limits are still not a proof.
'''+source[end:]
replace('distanceAlong+=max(stepSize,.000001);', 'distanceAlong+=stepSize;')
replace('vec3 reflected=radiance(reflect(rd,normal));', 'float roughness=.32+.18*(1.-facing);\n     vec3 reflected=radiance(reflect(rd,normal),roughness);')
replace('''     float light=max(0.,dot(normal,normalize(vec3(.6,.9,.7))));
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.06+.72*light+.14*facing)*recess;
     color+=reflected*(.015+.10*fresnel)*recess;
     color+=mix(pigment,vec3(1.),.18)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),10.)*.18*recess;
     float haze=1.-exp(-distanceAlong*.009);
     color=mix(color,vec3(.085,.008,.033),haze);''', '''     // Shadowing samples real material between the fold and the key light.
     // Finite sampling approximates visibility; never a painted gap mask.
     vec3 key=normalize(vec3(.6,.9,.7));
     float visibility=1.;
     for(int j=0;j<8;j++){
      float reach=.18*pow(1.65,float(j));
      float clearance=side*sheetSample(p+normal*.045+key*reach).w;
      visibility=min(visibility,smoothstep(-.10,.08,clearance));
     }
     float light=max(0.,dot(normal,key));
     float openness=recess*recess;
     color=pigment*(.018+.78*light*visibility+.12*facing*openness)*openness;
     color+=reflected*(.09+.28*fresnel)*openness*(.15+.85*visibility);
     color+=mix(pigment,vec3(1.),.25)*pow(max(0.,dot(reflect(rd,normal),key)),5.)*.24*visibility*openness;
     float haze=1.-exp(-distanceAlong*.005);
     color=mix(color,vec3(.018,.002,.009),haze);''')
assert not (HERE/'continuum-v23.js').exists(), 'Version archives are immutable'
(HERE/'continuum-v23.js').write_text(source)
(HERE/'continuum.js').write_text(source)
print('Installed continuum v23; fresh visual/functional acceptance pending')
