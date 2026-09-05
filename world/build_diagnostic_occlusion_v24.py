"""One-shot ablation of CURRENT v23 geometry/material with trip v16 controls."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
source = (HERE/'continuum.js').read_text()
assert source == (HERE/'continuum-v23.js').read_text()
assert (HERE/'trip.js').read_bytes() == (HERE/'trip-v16.js').read_bytes()
def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)

replace('    vec2 uv=screenUV*2.-1.;', '''    float column=floor(screenUV.x*3.),row=floor(screenUV.y*2.);
    float panel=(1.-row)*3.+column;
    vec2 uv=fract(screenUV*vec2(3.,2.))*2.-1.;
    uv.x*=2./3.;''')
replace('     float light=max', '''     if(panel>.5&&panel<1.5 || panel>2.5&&panel<3.5)visibility=1.;
     if(panel>1.5&&panel<3.5)recess=1.;
     float light=max''')
replace('     vec4 clip=viewProjection*vec4(p,1.);', '''     // Diagnostic channels bypass haze/material, but keep shared postprocessing.
     if(panel>3.5&&panel<4.5)color=normal*.5+.5;
     if(panel>4.5)color=vec3(clamp(distanceAlong/60.,0.,1.));
     vec4 clip=viewProjection*vec4(p,1.);''')
replace('     gl_FragDepthEXT=.999999;', '''     if(panel>3.5)color=vec3(1.,0.,1.); // Explicit missed-ray marker.
     gl_FragDepthEXT=.999999;''')
replace('material.uniforms.pixelScale.value=2*', 'material.uniforms.pixelScale.value=4*')

renderer = (HERE/'render_diagnostic_material_v23.py').read_text()
renderer = renderer.replace("PREFIX = 'diagnostic-chrysanthemum-v23-material'", "PREFIX = 'diagnostic-chrysanthemum-v24-occlusion'")
renderer = renderer.replace('diagnostic-material-v23', 'diagnostic-occlusion-v24')
renderer = renderer.replace("'material_ablation':True, 'max_steps':1024", "'material_ablation':True, 'max_steps':2048, 'depth_scale':60, 'miss_marker':'magenta in normal/depth panels'")
renderer = renderer.replace("'continuum-v22.js'", "'continuum-v23.js','trip-v16.js','render_diagnostic_occlusion_v24.py','build_diagnostic_occlusion_v24.py','index.html','data.js','fidelity-data.js','vendor/three.min.js'")
renderer = renderer.replace('Material isolation only;', 'Current v23 visibility/recess ablation plus normals/depth;')
renderer = renderer.replace('    browser.close()', '''    assert not errors, errors
    browser.close()''')
html = (HERE/'index.html').read_text().replace('src="continuum.js"', 'src="diagnostic-occlusion-v24.js"')
labels = ['CURRENT V23 MATERIAL', 'NO KEY VISIBILITY', 'NO RECESS DARKENING',
          'NEITHER VISIBILITY NOR RECESS', 'SURFACE NORMAL (MISS = MAGENTA)', 'DEPTH / 60 (MISS = MAGENTA)']
overlay = ''.join(f'<div style="position:fixed;pointer-events:none;z-index:9999;left:{(i%3)*33.333}%;top:{(i//3)*50+14}%;background:#000c;color:white;padding:4px;font:12px monospace">{label}</div>' for i,label in enumerate(labels))
html = html.replace('</body>', overlay+'</body>')
outputs = {'diagnostic-occlusion-v24.js':source, 'diagnostic-occlusion-v24.html':html,
           'render_diagnostic_occlusion_v24.py':renderer}
assert not any((HERE/name).exists() for name in outputs), 'Do not replay immutable builder'
runtime = ['continuum.js','trip.js','fractal.js','index.html','fidelity-data.js','data.js']
hashes = {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in runtime}
for name, content in outputs.items():
    (HERE/name).write_text(content)
(HERE/'diagnostic-occlusion-v24-runtime-before.json').write_text(json.dumps(hashes, indent=2)+'\n')
print('Created current-v23 diagnostic; live runtime unchanged')
