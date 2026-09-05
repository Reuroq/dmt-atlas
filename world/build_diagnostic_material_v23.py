"""Second isolated plate: separate material terms at identical geometry/clock."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'continuum-v22.js').read_text()
def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)
replace('    vec2 uv=screenUV*2.-1.;', '''    float column=floor(screenUV.x*3.),row=floor(screenUV.y*2.);
    float panel=(1.-row)*3.+column;
    vec2 uv=fract(screenUV*vec2(3.,2.))*2.-1.;
    uv.x*=2./3.;''')
replace('     float light=max', '''     if(panel>1.5&&panel<2.5 || panel>3.5)recess=1.;
     if(panel>.5&&panel<1.5 || panel>3.5)reflected=vec3(0.);
     float light=max''')
replace('     color+=mix(pigment,vec3(1.),.18)', '     if(panel<2.5)color+=mix(pigment,vec3(1.),.18)')
replace('     float haze=1.-exp(-distanceAlong*.009);', '''     if(panel>4.5)color=radiance(reflect(rd,normal));
     float haze=1.-exp(-distanceAlong*.009);''')
replace('material.uniforms.pixelScale.value=2*','material.uniforms.pixelScale.value=4*')
outputs={
 'diagnostic-material-v23.js':source,
 'render_diagnostic_material_v23.py':(HERE/'render_diagnostic_v23.py').read_text()
   .replace("PREFIX = 'diagnostic-chrysanthemum-v23'", "PREFIX = 'diagnostic-chrysanthemum-v23-material'")
   .replace('diagnostic-continuum-v23','diagnostic-material-v23')
   .replace("'root_delta_tolerance':.002, 'reference_max_steps':4096", "'material_ablation':True, 'max_steps':1024")
   .replace('CPU/GPU float comparison, not proof;', 'Material isolation only;')
}
html=(HERE/'index.html').read_text().replace('src="continuum.js"','src="diagnostic-material-v23.js"')
labels=['V22 MATERIAL', 'NO ENVIRONMENT REFLECTION', 'NO RECESS DARKENING',
        'NO SPECULAR HIGHLIGHT', 'PIGMENT + NEUTRAL LIGHT ONLY', 'ENVIRONMENT RADIANCE ONLY']
overlay=''.join(f'<div style="position:fixed;pointer-events:none;z-index:9999;left:{(i%3)*33.333}%;top:{(i//3)*50+14}%;background:#000c;color:white;padding:4px;font:12px monospace">{label}</div>' for i,label in enumerate(labels))
outputs['diagnostic-material-v23.html']=html.replace('</body>',overlay+'</body>')
assert not any((HERE/name).exists() for name in outputs),'Immutable diagnostic files already exist'
for name,contents in outputs.items():
    (HERE/name).write_text(contents)
print('Created isolated material ablation; runtime unchanged')
