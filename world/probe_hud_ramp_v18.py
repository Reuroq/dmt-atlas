"""One-shot static compositor isolation; no live application mutations."""
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import json
import re
import time
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from verify import ARGS

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-hud-ramp-v18'
assert not list(HERE.glob(PREFIX + '*')), 'One-shot output already exists'
protected = ['trip.js', 'trip-v18.js', 'continuum.js', 'fractal.js', 'trip.css',
             'visual-chrysanthemum.png', 'visual-chrysanthemum.json',
             'accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-before.png',
             'accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-after.png',
             'VISUAL_RESEARCH.json', 'fidelity-grades.json', 'realism-grades.json']
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
baseline = {name: digest(HERE/name) for name in protected}
raw_path = HERE/'diagnostic-submission-v18-frame-9.rgba'
raw = raw_path.read_bytes()
assert len(raw) == 1200*800*4
assert np.frombuffer(raw, np.uint8).reshape(800,1200,4)[:,:,3].min() == 255
js = r'''
(() => {
const canvas=document.getElementById('world');
const gl=canvas.getContext('webgl2',{antialias:true,alpha:false,powerPreference:'high-performance'});
if(!gl)throw Error('WebGL2 unavailable');
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();
gl.attachShader(program,shader(gl.VERTEX_SHADER,`#version 300 es
out vec2 uv;void main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);uv=p;gl_Position=vec4(p*2.-1.,0.,1.);}`));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`#version 300 es
precision highp float;in vec2 uv;uniform sampler2D source;out vec4 colour;void main(){colour=texture(source,uv);}`));
gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const source=Uint8Array.from(atob('__RAW__'),c=>c.charCodeAt(0));
gl.bindTexture(gl.TEXTURE_2D,gl.createTexture());
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1200,800,0,gl.RGBA,gl.UNSIGNED_BYTE,source);
let high=true,frames=0,pending=false,fence=null;const submissions=[];
function settle(){if(!fence)return;const s=gl.clientWaitSync(fence,0,0);if(s===gl.TIMEOUT_EXPIRED){requestAnimationFrame(settle);return;}if(s===gl.WAIT_FAILED)throw Error('Fence failed');gl.deleteSync(fence);fence=null;pending=false;}
function draw(){
 if(fence)gl.deleteSync(fence);
 const ratio=Math.min(devicePixelRatio,high?1.5:.85);
 canvas.width=Math.floor(innerWidth*ratio);canvas.height=Math.floor(innerHeight*ratio);
 gl.viewport(0,0,canvas.width,canvas.height);gl.drawArrays(gl.TRIANGLES,0,3);
 frames++;pending=true;submissions.push({frames,now:performance.now(),width:canvas.width,height:canvas.height,high,error:gl.getError()});
 fence=gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE,0);gl.flush();requestAnimationFrame(settle);
}
const detail=document.getElementById('detail');
detail.addEventListener('click',()=>{high=!high;detail.textContent='Detail: '+(high?'high':'low');detail.setAttribute('aria-pressed',String(high));draw();});
addEventListener('resize',draw);
for(const id of ['pause','motion'])document.getElementById(id).addEventListener('click',e=>{const b=e.currentTarget;b.setAttribute('aria-pressed',String(b.getAttribute('aria-pressed')!=='true'));});
document.getElementById('welcome').hidden=true;document.getElementById('hud').hidden=false;
document.getElementById('sceneName').textContent='Static compositor diagnostic';
document.getElementById('sceneHint').textContent='Saved submission pixels. No live geometry or acceptance credit.';
document.getElementById('stateText').textContent='Isolated fixture';
if(new URLSearchParams(location.search).get('gradient')==='absent'){
 const style=document.createElement('style');style.textContent='#hud::before{background:none}';document.head.append(style);
}
window.staticProbe=()=>({frames,pending,high,width:canvas.width,height:canvas.height,context:gl.getContextAttributes(),submissions,gradient:getComputedStyle(document.getElementById('hud'),'::before').backgroundImage});
draw();
})();
'''.replace('__RAW__', base64.b64encode(raw).decode())
html = (HERE/'index.html').read_text()
html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S)
html = html.replace('</head>', '<style>#hud::before{background: url(hud-alpha-ramp-v18.png) center / 100% 100% no-repeat}</style></head>')
html = html.replace('</body>', f'<script src="{PREFIX}.js"></script></body>')
(HERE/f'{PREFIX}.js').write_text(js)
(HERE/f'{PREFIX}.html').write_text(html)
receipt = {'purpose':'Changed deterministic HUD PNG fixture; not live acceptance', 'asset_sha256':digest(HERE/'hud-alpha-ramp-v18.png'),
           'source':{'file':raw_path.name,'sha256':digest(raw_path),'bottom_up':True},
           'baseline':baseline, 'cycles_per_case':6, 'interval_ms':800,
           'timeout_ms':90000, 'cases':[], 'browser_errors':[]}
clip = {'x':100,'y':110,'width':1000,'height':380}
def stats(a,b):
    d=np.asarray(b).astype(np.int16)-np.asarray(a).astype(np.int16)
    mask=np.any(d!=0,axis=2); y,x=np.where(mask)
    return {'changed_pixels':int(mask.sum()),'max_channel_delta':int(np.abs(d).max()),
            'bbox': [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None,
            'positive_channels':int((d>0).sum()),'negative_channels':int((d<0).sum()),
            'changed_pixels_per_row':mask.sum(axis=1).tolist() if len(x) else []}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=ARGS)
    for mode in ['ramp']:
        page=browser.new_page(viewport={'width':1200,'height':800},device_scale_factor=1)
        page.set_default_timeout(90000)
        page.on('pageerror',lambda e: receipt['browser_errors'].append(str(e)))
        page.on('console',lambda m: receipt['browser_errors'].append(m.text) if m.type=='error' else None)
        cdp=page.context.new_cdp_session(page)
        events=[]
        def record(kind,payload):
            if len(events)<5000: events.append({'kind':kind,'observed_at':time.monotonic(),**payload})
        cdp.on('LayerTree.layerTreeDidChange',lambda e:record('tree',e))
        cdp.on('LayerTree.layerPainted',lambda e:record('paint',e))
        cdp.send('LayerTree.enable')
        page.goto((HERE/f'{PREFIX}.html').as_uri()+'?gradient='+mode)
        page.wait_for_function('window.staticProbe && !staticProbe().pending')
        case={'gradient':mode,'comparisons':[],'layer_events':events}
        receipt['cases'].append(case)
        saved_failure=False
        def settled():
            # A viewport API acknowledgement can precede native resize delivery.
            # Observe actual drawing dimensions, not just the previous fence.
            page.wait_for_function('''() => {const s=staticProbe();const r=Math.min(devicePixelRatio,s.high?1.5:.85);
                return !s.pending && s.width===Math.floor(innerWidth*r) && s.height===Math.floor(innerHeight*r);}''')
        def pair(label):
            global saved_failure
            settled();before=page.evaluate('staticProbe()');start=len(events)
            a=page.screenshot(clip=clip)
            page.wait_for_timeout(800)
            b=page.screenshot(clip=clip)
            after=page.evaluate('staticProbe()')
            assert before==after, 'Static submission changed during comparison'
            result={'label':label,'snapshot':before,'layer_event_range':[start,len(events)],
                    **stats(Image.open(BytesIO(a)).convert('RGB'),Image.open(BytesIO(b)).convert('RGB'))}
            case['comparisons'].append(result)
            if result['changed_pixels'] and not saved_failure:
                for suffix,data in [('before',a),('after',b)]:
                    (HERE/f'{PREFIX}-{mode}-failure-{suffix}.png').write_bytes(data)
                saved_failure=True
            print(mode,label,result['changed_pixels'],result['bbox'],flush=True)
        for cycle in range(6):
            pair(f'{cycle}:baseline')
            page.set_viewport_size({'width':1180,'height':800});settled()
            page.set_viewport_size({'width':1200,'height':800});settled()
            pair(f'{cycle}:resize-restored')
            page.locator('#detail').click();page.locator('#detail').click()
            pair(f'{cycle}:detail-restored')
        case['final']=page.evaluate('staticProbe()')
        page.screenshot(path=str(HERE/f'{PREFIX}.png'))
        desktop_clip = clip
        page.set_viewport_size({'width':390,'height':844});settled()
        clip = {'x':40,'y':410,'width':300,'height':50}
        pair('mobile:baseline')
        page.set_viewport_size({'width':410,'height':844});settled()
        page.set_viewport_size({'width':390,'height':844});settled()
        pair('mobile:resize-restored')
        page.locator('#detail').click();page.locator('#detail').click()
        pair('mobile:detail-restored')
        page.screenshot(path=str(HERE/f'{PREFIX}-mobile.png'))
        case['mobile_final']=page.evaluate('staticProbe()')
        clip = desktop_clip
        page.close()
    browser.close()
receipt['protected_unchanged']={name:digest(HERE/name)==h for name,h in baseline.items()}
receipt['artifact_hashes']={name:digest(HERE/name) for name in [Path(__file__).name,f'{PREFIX}.html',f'{PREFIX}.js',f'{PREFIX}.png',f'{PREFIX}-mobile.png','hud-alpha-ramp-v18.png']}
(HERE/f'{PREFIX}.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert all(receipt['protected_unchanged'].values()) and not receipt['browser_errors']
assert all(c['changed_pixels']==0 for case in receipt['cases'] for c in case['comparisons']), 'Strict candidate stillness failed'
print('Changed HUD ramp fixture passed; no live runtime changes.',flush=True)
