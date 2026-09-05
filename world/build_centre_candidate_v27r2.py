"""Tighten the cap blend bound; preserve failed v27, geometry and step limits."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE/'continuum-v27r2-candidate.js'
assert not OUT.exists()
source = (HERE/'continuum-v27-candidate.js').read_text()
old = '    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;'
assert source.count(old) == 1
source = source.replace(old, '''    // cw is monotone in |cap|. These extrema cover the entire .4 step,
    // including a step that crosses the start of the cap.
    float capLo=max(0.,-p.z-27.5-.4*abs(rd.z));
    float capHi=max(0.,-p.z-27.5+.4*abs(rd.z));
    float cwLo=capLo*capLo/(capLo*capLo+4.);
    float cwHi=capHi*capHi/(capHi*capHi+4.);
'''+old)
old = 'if(cap)waveSlope=max(waveSlope,k*crosswise+.6*meridian)+2.*capSlope;'
assert source.count(old) == 1
source = source.replace(old, 'if(cap)waveSlope=(1.-cwLo)*waveSlope+cwHi*(k*crosswise+.6*meridian)+2.*capSlope;')
OUT.write_text(source)
(HERE/'gpu_probe_v27r2_candidate.html').write_text((HERE/'gpu_probe_v27_candidate.html').read_text().replace('v27','v27r2'))
probe = (HERE/'probe_numeric_candidate_v27.py').read_text().replace('v27','v27r2')
probe = probe.replace('field_centre_v27r2','field_centre_v27')
(HERE/'probe_numeric_candidate_v27r2.py').write_text(probe)
print('Created v27r2 with identical geometry and tighter interval cap bound')
