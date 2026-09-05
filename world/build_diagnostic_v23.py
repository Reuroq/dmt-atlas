"""Create immutable, isolated v23 shader diagnosis; never change the live runtime."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / 'continuum-v22.js').read_text()

def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)

start = source.index('    float distanceAlong=0.')
end = source.index('    vec3 color;', start)
march = source[start:end]
# Both solvers retain the same envelope, derivative bound and residual threshold.
# The reference disables Newton and raises only its iteration budget. It remains
# a floating-point comparison, not a mathematical proof of the first hit.
march = march.replace('i<1024', 'i<4096').replace('if(i>=768&&high<.5)break;',
    'if(useNewton&&i>=1024)break;')
march = march.replace('if(abs(value)<.065)', 'if(useNewton&&abs(value)<.065)')
source = source[:start] + '''    bool hit=false;
    float distanceAlong=traceRay(ro,rd,panel<4.5,hit);
''' + source[end:]
replace('   void main(){', '''   float traceRay(vec3 ro,vec3 rd,bool useNewton,out bool found){
    vec3 p;
''' + march + '''    found=hit;return distanceAlong;
   }
   void main(){''')
replace('    vec2 uv=screenUV*2.-1.;', '''    float column=floor(screenUV.x*3.),row=floor(screenUV.y*2.);
    float panel=(1.-row)*3.+column;
    vec2 uv=fract(screenUV*vec2(3.,2.))*2.-1.;
    uv.x*=2./3.;''')
replace('     vec4 clip=viewProjection*vec4(p,1.);', '''     if(panel>.5&&panel<1.5 || panel>4.5)
      color=vec3(.72)*(.08+.75*light+.08*facing);
     if(panel>1.5&&panel<2.5)color=normal*.5+.5;
     if(panel>2.5&&panel<3.5)color=vec3(distanceAlong/55.);
     vec4 clip=viewProjection*vec4(p,1.);''')
replace('    gl_FragColor=vec4(color,1.);', '''    if(panel>3.5&&panel<4.5){
     bool strictHit=false;
     float strictDistance=traceRay(ro,rd,false,strictHit);
     color=vec3(0.,.42,0.);
     if(hit&&strictHit){
      float delta=distanceAlong-strictDistance;
      if(delta>.002)color=vec3(1.,.6,0.);
      if(delta<-.002)color=vec3(.25,.1,1.);
     }else if(hit)color=vec3(1.,0.,0.);
     else if(strictHit)color=vec3(0.,1.,1.);
     else color=vec3(1.,0.,1.);
    }else if(!hit)color=vec3(1.,0.,1.);
    gl_FragColor=vec4(color,1.);''')
replace('material.uniforms.pixelScale.value=2*', 'material.uniforms.pixelScale.value=4*')
shader = HERE / 'diagnostic-continuum-v23.js'
page = HERE / 'diagnostic-continuum-v23.html'
assert not shader.exists() and not page.exists(), 'Diagnostic artifacts are immutable'
shader.write_text(source)
html = (HERE / 'index.html').read_text().replace('src="continuum.js"', 'src="diagnostic-continuum-v23.js"')
labels = ['V22 MATERIAL / NEWTON', 'NEUTRAL LIGHT / NEWTON', 'FACING NORMAL / NEWTON',
          'LINEAR DEPTH / NEWTON', 'ROOT DELTA: GREEN = WITHIN .002', 'NEUTRAL LIGHT / NO NEWTON']
overlay = ''.join(f'<div style="position:fixed;pointer-events:none;z-index:9999;left:{(i%3)*33.333}%;top:{(i//3)*50+14}%;background:#000c;color:white;padding:4px;font:12px monospace">{label}</div>' for i, label in enumerate(labels))
page.write_text(html.replace('</body>', overlay+'</body>'))
print('Created isolated six-panel v23 diagnosis; live runtime unchanged')
