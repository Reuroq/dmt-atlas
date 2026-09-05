"""Conservative second-order advancement for the unchanged v28 field."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = HERE / 'continuum-v28r3-candidate.js'
assert not out.exists()
source = (HERE / 'continuum-v28r2-candidate.js').read_text()
old = 'float stepSize=min(.4,abs(value)*.95/raySlope(p,rd));'
assert source.count(old) == 1
source = source.replace(old, '''// Both steps bound field change over the entire next .4 segment.
     // The second uses |F'|s + M*s*s/2 <= .95*|F|. Stable quadratic
     // evaluation avoids subtractive cancellation at almost-tangent rays.
     // Derivation and independent checks: centre-v28-curvature.md.
     float curvature=160.+25.*pixelScale+92.*pixelScale*pixelScale;
     float slope=abs(dot(sampleValue.xyz,rd)),remaining=.95*abs(value);
     float quadraticStep=2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining));
     float stepSize=min(.4,max(remaining/raySlope(p,rd),quadraticStep));''')
out.write_text(source)
(HERE/'gpu_probe_v28r3_candidate.html').write_text((HERE/'gpu_probe_v28r2_candidate.html').read_text().replace('v28r2','v28r3'))
probe = (HERE/'probe_numeric_candidate_v28r2.py').read_text().replace('v28r2','v28r3')
(HERE/'probe_numeric_candidate_v28r3.py').write_text(probe)
print('Created v28r3: same geometry, stricter hits, bounded quadratic advancement.')
