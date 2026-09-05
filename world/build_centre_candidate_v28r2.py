"""Tighten grazing hit acceptance; preserve the failed v28 probe unchanged."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = HERE / 'continuum-v28r2-candidate.js'
assert not out.exists()
source = (HERE / 'continuum-v28-candidate.js').read_text()
old = 'if(abs(value)<.00015 || abs(value)/max(1.,length(sampleValue.xyz))<tolerance){hit=true;break;}'
assert source.count(old) == 1
source = source.replace(old, '''// Require BOTH the existing residual and a ray-direction depth
     // estimate. Normal-distance alone can accept a near-tangent non-root.
     // This is still local sampled acceptance, not a tangency proof.
     if(abs(value)<.00015 && abs(value)/max(.00001,abs(dot(sampleValue.xyz,rd)))<tolerance){hit=true;break;}''')
source = source.replace('// It is a local surface-distance estimate, not an exact-root proof.',
                        '// Use ray-direction depth below, not normal-distance acceptance.')
out.write_text(source)
(HERE/'gpu_probe_v28r2_candidate.html').write_text((HERE/'gpu_probe_v28_candidate.html').read_text().replace('v28','v28r2'))
probe = (HERE/'probe_numeric_candidate_v28.py').read_text().replace('v28','v28r2').replace('field_centre_v28r2','field_centre_v28')
(HERE/'probe_numeric_candidate_v28r2.py').write_text(probe)
print('Created v28r2: identical field and bounds; strictly tighter hit acceptance.')
