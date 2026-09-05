"""One-shot centre-scale rebuild. Leaves live assets and prior evidence untouched."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
OUT = HERE/'continuum-v27-candidate.js'
assert not OUT.exists()
source = (HERE/'continuum-v26-candidate.js').read_text()
def replace(old, new):
    global source
    assert source.count(old) == 1, old[:90]
    source = source.replace(old, new)

replace('float amplitude=octave==0?.18:(octave==1?.08:.035);',
        'float amplitude=octave==0?.30:(octave==1?.15:.07);')
replace('float frequency=octave==0?30.:(octave==1?64.:130.);', '''// Resolved world-scale bands, not the old global worst-case filter.
     // Approximate Gaussian antialiasing; not a strict local Nyquist proof.
     float frequency=octave==0?6.:(octave==1?13.:28.);
     float k=octave==0?1.3:(octave==1?2.9:6.1);''')
replace('''     f-=amplitude*weight*preciseSin(phase);
     g-=amplitude*(gweight*preciseSin(phase)+weight*preciseCos(phase)*gphase);''', '''     // Blend angular side folds into genuine crossed Cartesian cap folds.
     // The latter retain finite, nonzero scale at the axis, at every octave.
     float ax=k*p.x+.3*preciseSin(v)+time*.07;
     float ay=k*p.y+.3*preciseCos(v)-time*.09;
     vec3 gax=vec3(k,0.,0.)+.3*preciseCos(v)*gv;
     vec3 gay=vec3(0.,k,0.)-.3*preciseSin(v)*gv;
     float crossed=preciseCos(ax)*preciseCos(ay);
     vec3 gcross=-preciseSin(ax)*preciseCos(ay)*gax-preciseCos(ax)*preciseSin(ay)*gay;
     float wave=mix(preciseSin(phase),crossed,cw);
     vec3 gwave=(1.-cw)*preciseCos(phase)*gphase+cw*gcross+gcw*(crossed-preciseSin(phase));
     f-=amplitude*weight*wave;
     g-=amplitude*(gweight*wave+weight*gwave);''')
replace('// |displacement| <=2.155. Clearance >=4.84 for z>=-27.5.',
        '// |displacement| <=2.38. Clearance >=4.615 for z>=-27.5.')
replace('return abs(rho-7.)-2.16;', 'return abs(rho-7.)-2.385;')
replace('''    result+=.18*exp(-.5*pow(footprint*30.,2.))*(2.7*meridian+2.*chartSlope);
    result+=.08*exp(-.5*pow(footprint*64.,2.))*(5.7*meridian+4.*chartSlope);
    if(high>.5)result+=.035*exp(-.5*pow(footprint*130.,2.))*(12.1*meridian+7.*chartSlope);
    // Max filter derivative: sum(amplitude*frequency)*exp(-.5)<9.2.
    return result+9.2*pixelScale;''', '''    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.30:(octave==1?.15:.07);
     float frequency=octave==0?6.:(octave==1?13.:28.);
     float k=octave==0?1.3:(octave==1?2.9:6.1);
     float fv=octave==0?2.7:(octave==1?5.7:12.1);
     float fc=octave==0?2.:(octave==1?4.:7.);
     float waveSlope=fv*meridian+fc*chartSlope;
     if(cap)waveSlope=max(waveSlope,k*crosswise+.6*meridian)+2.*capSlope;
     result+=amplitude*exp(-.5*pow(footprint*frequency,2.))*waveSlope;
    }
    // Global filter derivative: (.30*6+.15*13+.07*28)*exp(-.5)<3.47.
    return result+3.47*pixelScale;''')
replace('''     float hue=.14*preciseSin(a*3.+time*.12)+p.z*.039+time*.025;''', '''     vec2 pigmentXY=p.xy-vec2(0.,1.7);
     float pigmentR2=dot(pigmentXY,pigmentXY);
     // Angular pigment smoothly vanishes at the axis; Cartesian colour
     // follows the central folds without converging into a radial colour fan.
     float pigmentPole=pow(pigmentR2/(pigmentR2+9.),2.);
     float pigmentCap=pow(min(p.z+27.5,0.),2.);
     pigmentCap/=pigmentCap+4.;
     float hue=.14*pigmentPole*preciseSin(a*3.+time*.12)+p.z*.039+time*.025;
     hue+=pigmentCap*(.17*preciseSin(.95*pigmentXY.x+time*.13)*preciseCos(.95*pigmentXY.y-time*.11)
                    +.055*preciseSin(2.9*pigmentXY.x+2.1*pigmentXY.y+time*.17));''')
OUT.write_text(source)
probe = (HERE/'gpu_probe_v26_candidate.html').read_text().replace('v26-candidate','v27-candidate')
(HERE/'gpu_probe_v27_candidate.html').write_text(probe)
probe = (HERE/'probe_numeric_candidate_v26.py').read_text()
probe = probe.replace('from probe_continuum_v25 import field', 'from field_centre_v27 import field')
probe = probe.replace('v26','v27').replace('build_numeric_candidate_v27.py','build_centre_candidate_v27.py')
probe = probe.replace("'probe_continuum_v25.py'", "'field_centre_v27.py'")
(HERE/'probe_numeric_candidate_v27.py').write_text(probe)
print('Isolated centre candidate', hashlib.sha256(source.encode()).hexdigest())
