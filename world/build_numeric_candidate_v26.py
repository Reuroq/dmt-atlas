"""One-shot isolated candidate; does not promote or change journey assets."""
from pathlib import Path
import hashlib
import re

HERE = Path(__file__).resolve().parent
destination = HERE/'continuum-v26-candidate.js'
assert not destination.exists()
source = (HERE/'continuum-v25.js').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == '6b55368f4f3d31cbd71dc0420707c8860e99a1b471f9108a53a77416f871106d'
diagnostic = (HERE/'diagnostic_precisetrig_v25_r2.html').read_text()
helper = diagnostic.split('const precise=`', 1)[1].split('`;', 1)[0]
source = re.sub(r'\bsin\(', 'preciseSin(', source)
source = re.sub(r'\bcos\(', 'preciseCos(', source)
assert source.count('   mat2 rot(') == 1
source = source.replace('   mat2 rot(', helper+'   mat2 rot(')
destination.write_text(source)
probe = (HERE/'gpu_probe_v25.html').read_text().replace('v25', 'v26-candidate')
probe = probe.replace('const width=48,height=32;', 'let width=48,height=32;')
probe = probe.replace('window.runCase=(z,time,high)=>{', '''window.runCase=(z,time,high,w=48,h=32)=>{
 width=w;height=h;renderer.setSize(w,h);target.setSize(w,h);''')
probe = probe.replace("for(let mode=0;mode<2;mode++){", "for(let mode=0;mode<3;mode++){")
probe = probe.replace('vec4(root.xyz,raySlope(p,rd));', 'probeMode<1.5?vec4(root.xyz,raySlope(p,rd)):vec4(p,length(p-ro)*pixelScale);')
probe = probe.replace("output[mode?'gradientSlope':'hits']", "output[['hits','gradientSlope','points'][mode]]")
(HERE/'gpu_probe_v26_candidate.html').write_text(probe)
print('Isolated candidate', hashlib.sha256(source.encode()).hexdigest())
