"""Successor-specific static checks using the actual staged HTML; no GPU."""
import ast
import copy
import json
import probe_centre_v34_staged_arithmetic_r3 as p
from static_centre_v34_staged_arithmetic_r3 import durable_node


def check_changes():
    delta = p.read(p.PREFIX + '-source-delta.json')
    for name, entry in delta.items():
        assert p.digest(entry['base']) == entry['base_sha256']
        text = (p.HERE / entry['base']).read_text()
        text = text.replace('centre_v34_staged_arithmetic_r2', 'centre_v34_staged_arithmetic_r3').replace('centre-v34-staged-arithmetic-r2', p.PREFIX)
        for before, after in entry['edits']:
            assert text.count(before) == 1
            text = text.replace(before, after, 1)
        assert text == (p.HERE / name).read_text() and p.digest(name) == entry['sha256']
    old = (p.HERE / 'gpu_centre_v34_staged_arithmetic_r2.html').read_text()
    new = (p.HERE / p.HTML).read_text()
    for start, end in [('window.shaderSource=', 'function drainErrors'), ('function makePlan()', 'function perform')]:
        assert old[old.index(start):old.index(end)] == new[new.index(start):new.index(end)]
    a = ast.parse((p.HERE / 'check_centre_v34_staged_arithmetic_r2.py').read_text())
    b = ast.parse((p.HERE / 'check_centre_v34_staged_arithmetic_r3.py').read_text())
    for name in ('integer_add', 'frombit'):
        pick = lambda tree: next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(pick(a)) == ast.dump(pick(b))


def extra_checks(js):
    import playwright._impl._js_handle as wire
    bits = p.source_bits()
    assert bits == [p.bit(x) for x in p.inputs()] and len(bits) == 1024
    request = {'op': 'shared', 'dataBits': bits}
    serialized = wire.serialize_argument(request)
    p.save(p.PREFIX + '-uint32-wire.json', {'source_bits': bits, 'request': request, 'wire': serialized})
    # The installed Playwright serializer is exercised, not replaced with a mock.
    prefix = r'''
const vm=require('vm'),assert=require('assert');
function decode(w) {
 if('n' in w)return w.n;if('s' in w)return w.s;if('b' in w)return w.b;
 if(w.v==='-0')return -0;if(w.v==='null')return null;
 if('a' in w)return w.a.map(decode);
 if('o' in w)return Object.fromEntries(w.o.map(e=>[e.k,decode(e.v)]));
 throw Error('Unexpected wire type');
}
const request=decode(WIRE.value),expected=BITS;
function run(mode) {
 if(mode==='mixed-bits'){request.dataBits=request.dataBits.slice();expected.splice(0,8,0,2147483648,1065353216,3212836864,1,2147483649,2139095039,4286578687);request.dataBits=expected.slice();}
 if(mode==='bad-length')request.dataBits.pop();
 if(mode==='bad-word')request.dataBits[0]=-1;
 if(mode==='bad-float')request.dataBits[0]=0.5;
 if(mode==='bad-bool')request.dataBits[0]=false;
 const context={window:{},Float32Array,Uint32Array,assert,request,expected,mode};vm.createContext(context);
 vm.runInContext(SOURCE,context);
 vm.runInContext(`
const calls=[];let queue=[],next=0;
gl={NO_ERROR:0,getError:()=>{if(mode==='drain-throws')throw Error('injected drain');return queue.length?queue.shift():0;},isContextLost:()=>false};
const mockgl=gl;
function disposable(kind){return {dispose(){calls.push(kind);if(mode==='dispose-'+kind)throw Error('injected '+kind);}};}
globalThis.THREE={REVISION:'160',FloatType:1015,NearestFilter:1003,RGBAFormat:1023,NoBlending:0,
 WebGLRenderer:class {constructor(){Object.assign(this,disposable('renderer'));this.debug={};this.capabilities={isWebGL2:true,precision:'highp'};}getContext(){if(mode==='renderer-setup')throw Error('injected getContext');return mockgl;}setSize(){}},
 WebGLRenderTarget:class {constructor(w,h,o){if(mode==='target-constructor')throw Error('injected target');Object.assign(this,disposable('target'));this.width=w;this.height=h;this.texture={type:o.type};}},
 DataTexture:class {constructor(data,w,h,f,t){Object.assign(this,disposable('texture'));this.data=data;}set needsUpdate(v){if(mode==='texture-setter')throw Error('injected texture setter');}},
 PlaneGeometry:class {constructor(){if(mode==='geometry-constructor')throw Error('injected geometry');Object.assign(this,disposable('geometry'));}},
 Scene:class {add(m){if(mode==='scene-add')throw Error('injected scene');}},Camera:class {},
 Mesh:class {constructor(g,m){assert.strictEqual(m,null);this.geometry=g;this.material=m;}set material(m){if(m!==null&&mode==='material-setter')throw Error('injected material setter');this.savedMaterial=m;}},
 ShaderMaterial:class {constructor(o){if(mode==='material-constructor')throw Error('injected material');Object.assign(this,o,disposable('material'));}}};
if(mode==='empty'){const v=window.arithmeticStep({op:'dispose'}).value;assert(v.complete);assert.strictEqual(v.registered.length,0);window.result={mode,v};}
else {
 let r=window.arithmeticStep({op:'renderer'});
 if(mode==='renderer-setup')assert(r.exception.includes('getContext'));
 else {assert.strictEqual(r.exception,null);r=window.arithmeticStep(request);
  if(['target-constructor','texture-setter','geometry-constructor','scene-add','bad-length','bad-word','bad-float','bad-bool'].includes(mode))assert(r.exception);
  else {assert.strictEqual(r.exception,null);assert.strictEqual(JSON.stringify(r.value.input.bits),JSON.stringify(expected));assert.strictEqual(JSON.stringify(r.step.dataBits),JSON.stringify(expected));
   r=window.arithmeticStep({op:'material',name:'childAxial',leaf:0,arm:'uniform'});
   if(mode==='material-constructor'||mode==='material-setter')assert(r.exception);else assert.strictEqual(r.exception,null);
   if(mode==='full')for(let i=0;i<4;i++){r=window.arithmeticStep({op:'material',name:'childAngular',leaf:1,arm:'literal'});assert.strictEqual(r.exception,null);}
  }
 }
 const count=({'full':9,'renderer-setup':1,'target-constructor':1,'texture-setter':3,'geometry-constructor':3,'scene-add':4,'material-constructor':4,'bad-length':1,'bad-word':1,'bad-float':1,'bad-bool':1})[mode]||5;
 assert.strictEqual(resources.length,count);assert.strictEqual(resourceSnapshot()[0].kind,'renderer');
 if(mode==='duplicate')assert.throws(()=>register(renderer,'renderer'),/Duplicate/);
 if(mode==='dirty')queue=[1282];
 if(mode==='drain-throws'){} // getError is changed below, after allocations.
 const before=resourceSnapshot();r=window.arithmeticStep({op:'dispose'});const v=r.value;
 assert.strictEqual(r.skipped,false);assert.strictEqual(v.registered.length,count);
 assert.deepStrictEqual(Array.from(v.attempted),before.filter(e=>e.kind!=='renderer').concat(before.filter(e=>e.kind==='renderer')).map(e=>e.id));
 assert.deepStrictEqual(Array.from(calls),before.filter(e=>e.kind!=='renderer').concat(before.filter(e=>e.kind==='renderer')).map(e=>e.kind));
 assert.strictEqual(v.complete,!mode.startsWith('dispose-'));
 assert.strictEqual(v.rendererDisposed,mode!=='dispose-renderer');
 if(mode.startsWith('dispose-')){assert.strictEqual(v.errors.length,1);assert.strictEqual(v.succeeded.length,count-1);}
 if(mode==='dirty')assert.deepStrictEqual(Array.from(r.before.errors),[1282]);
 const repeated=window.arithmeticStep({op:'dispose'}).value;
 assert.deepStrictEqual(repeated,v);assert.strictEqual(calls.length,count);
 window.result={mode,before,result:r};
}
`,context);
 return context.window.result;
}
'''.replace('WIRE', json.dumps(serialized), 1).replace('BITS', json.dumps(bits), 1).replace('SOURCE', json.dumps(js), 1)
    # Each stage has separate durable source, command, stdout/stderr and actual-exit receipts.
    modes = ['empty','normal','renderer-setup','target-constructor','texture-setter','geometry-constructor',
             'scene-add','material-constructor','duplicate','dirty','dispose-target','dispose-texture',
             'dispose-geometry','dispose-material','dispose-renderer','drain-throws','mixed-bits',
             'bad-length','bad-word','bad-float','bad-bool','full','material-setter']
    results = []
    for mode in modes:
        source = prefix
        if mode == 'drain-throws':
            source = source.replace("if(mode==='drain-throws')throw Error('injected drain');", '')
            source = source.replace("if(mode==='drain-throws'){}", "if(mode==='drain-throws')gl.getError=()=>{throw Error('injected drain');}")
        stdout, stderr = durable_node('resource-' + mode, source + '\nprocess.stdout.write(JSON.stringify(run(' + json.dumps(mode) + ')));\n')
        assert not stderr
        results.append(json.loads(stdout))
    p.save(p.PREFIX + '-resource-mocks.json', results)
    leaves, texels = p.read(p.SEEDS)['leaves'], p.inputs()
    def good(step, value):
        return {'step':step,'value':value,'resources':[], 'before':{'errors':[],'drained':True},
                'after':{'errors':[],'drained':True},'contextLost':False,'exception':None,'skipped':False}
    shared = good(request, {'input':{'bits':bits,'values':texels},'width':128,'height':1,'textureHeight':2,'targetType':1015})
    classify = lambda r: p.assess(r, leaves, texels, {})['classification']
    assert classify(shared) == 'ok'
    for where in ('request', 'cpu'):
        for replacement in (0x80000000, 0.0, False):
            bad = copy.deepcopy(shared)
            words = bad['step']['dataBits'] if where == 'request' else bad['value']['input']['bits']
            words[bits.index(0)] = replacement
            assert classify(bad) == 'fatal-input'
    for result in results:
        if 'result' not in result: continue
        r = result['result']
        if result['mode'].startswith('dispose-'): assert classify(r) == 'fatal-disposal'
        elif result['mode'] in ('dirty','drain-throws'): assert classify(r) == 'fatal-precondition'
        else: assert classify(r) == 'ok'
    v = next(r['result'] for r in results if r['mode'] == 'normal')
    for mutate in (lambda r:r['value']['attempted'].pop(),lambda r:r['value']['registered'].pop(),
                   lambda r:r['resources'][0].update(id='wrong'),lambda r:r['value'].update(rendererDisposed=False),
                   lambda r:r['value'].update(complete=False),lambda r:r['value']['succeeded'].reverse()):
        bad=copy.deepcopy(v);mutate(bad);assert classify(bad)=='fatal-disposal'
    # Real run_steps must persist exact integer request, then full result, before assessment.
    records=[]
    class Page:
        def evaluate(self, expression, s):
            assert s == request and p.exact_words(s['dataBits'], bits)
            return copy.deepcopy(shared)
    saved=p.assess
    def after_saved(r,*args):
        assert records[-1] == ('step-result',r)
        return saved(r,*args)
    try:
        p.assess=after_saved
        p.run_steps(Page(),[{'op':'shared'}],lambda k,v:records.append((k,v)),leaves,texels,[])
    finally: p.assess=saved
    assert [k for k,v in records]==['step-intent','step-result','assessment']
    assert records[-1][1]['classification']=='ok'
    # Registry loss between operations is fatal, with the returned evidence saved first.
    class MissingRegistry:
        def evaluate(self, expression, s):
            r=good(s,{})
            if s['op']=='first': r['resources']=[{'id':'resource-0','kind':'renderer','attempted':False,'succeeded':False,'error':None}]
            return r
    records=[]
    try:
        p.run_steps(MissingRegistry(),[{'op':'first'},{'op':'second'}],lambda k,v:records.append((k,v)),leaves,texels,[])
    except RuntimeError as e: assert str(e).startswith('fatal-resource-identity')
    else: raise AssertionError('Registry loss accepted')
    assert records[-2][0]=='step-result' and records[-1][1]['classification']=='fatal-resource-identity'
    p.save(p.PREFIX + '-successor-checks.json', {'passed':True,'transport_components':len(bits),'resource_cases':modes,
        'source_request_cpu_bits_strict':True,'partial_allocation_and_exception_continuation':True,
        'identity_loss_rejected':True,'browser_run':False,'gpu_cleanup_proven':False})
