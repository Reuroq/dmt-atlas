"""One-shot local curled/branching petal volume; no live edits."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
OUT=HERE/'continuum-v32-candidate.js'
assert not OUT.exists()
source=(HERE/'continuum-v31-candidate.js').read_text()
start=source.index('    // Radially swept angular fins:')
end=source.index('\n   vec4 ja(',start)
source=source[:start]+'''
    // Two local coordinates bend in radius AND depth. Parent curl is reused
    // inside each child, so branches follow the folded volume, not its pigment.
    vec4 radial=offset(1.05*radius+.22*z+.65*r6,-time*.13);
    vec4 local=offset(.65*z-.4*radius+.6*i6,-time*.18);
    vec4 curl=radial+1.1*jc(local);
    vec4 child=offset(3.*curl+.65*jc(3.*local)+.4*r18,-time*.17);
    vec4 split=local+.5*jc(curl);
    vec4 twig=3.*local+.6*curl+.4*i18;
    f=offset(-radius,6.2)+.65*r6+.1*jc(local);
    a=filtered(jc(curl)-.85*jc(local)-.3*r6,4.,p);
    a+=.18*filtered(jc(child),12.,p)+6.3*jm(inv,inv);
    b=filtered(jc(split),4.,p)+.26*filtered(jc(twig),12.,p);
    if(high>.5){
     vec4 r54,i54;cubePair(r18,i18,r54,i54);
     a+=.035*filtered(jc(3.*child+.35*r54),36.,p);
    }
   }
'''+source[end:]
for old,new in [
    ('offset(aa,-.065)','offset(aa,-.10)'),('offset(-bb,.16)','offset(-bb,.035)'),
    ('offset(f,.45)','offset(f,.38)'),('offset(aa,-.18)','offset(aa,-.25)'),
    ('offset(bb,-.03)','offset(bb,-.014)'),('offset(f,12.)','offset(f,10.)'),
    ('excludedBandReach(b,.16','excludedBandReach(b,.035'),
    ('4.895-rho','5.445-rho'),('12.+10.*pixelScale','16.+8.*pixelScale'),
    ('vec3(11.,22.,140.)+vec3(2.,13.,140.)*s+vec3(2.,10.,170.)*s*s',
     'vec3(7.,305.,87.)+vec3(1.,190.,65.)*s+vec3(1.,110.,54.)*s*s')]:
    assert old in source,old
    source=source.replace(old,new)
OUT.write_text(source)
for kind in ['candidate','leaves']:
    target=HERE/f'gpu_probe_v32_{kind}.html'
    assert not target.exists()
    target.write_text((HERE/f'gpu_probe_v31_{kind}.html').read_text().replace('v31','v32'))
(HERE/'centre-v32-build.json').write_text(json.dumps({
    'candidate':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'parent':'continuum-v31-candidate.js','live_modified':False,
    'structure':'Local radius/depth curled petal cups; 3x and 9x parent-following folded surfaces; narrow split openings and connecting branch volumes; excluded bright axis, dark backing',
    'clearance_lower_bound':5.45,'cap_begins_z':-27.5,
    'unchanged':'materials,2048/1536 budgets,14 bisections,.00015 residual,no forced minimum step,actual camera and shared clock',
    'state':'Unvalidated; no realism or promotion'},indent=2)+'\n')
print('Built isolated v32 local curled-petal volume; no live changes.')
