"""One frozen static check: no browser, GLSL compile, field or GPU runtime."""
import ast
import copy
import json
import struct
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
import probe_centre_v34_staged_arithmetic as p


def integer_add(a, b):
    """Exact rational sum, independently rounded to IEEE binary32 ties-to-even."""
    v = Fraction(a) + Fraction(b)
    if not v:
        return 0x80000000 if p.bit(a) == p.bit(b) == 0x80000000 else 0
    sign = 0x80000000 if v < 0 else 0
    v = abs(v)
    e = v.numerator.bit_length() - v.denominator.bit_length()
    if v < Fraction(2) ** e:
        e -= 1
    scaled = v * Fraction(2) ** (149 if e < -126 else 23-e)
    q, rem = divmod(scaled.numerator, scaled.denominator)
    if 2*rem > scaled.denominator or (2*rem == scaled.denominator and q % 2):
        q += 1
    if e < -126:
        return sign | q
    if q == 1 << 24:
        q >>= 1; e += 1
    return sign | ((e+127) << 23) | (q - (1 << 23))


def frombit(b):
    return struct.unpack('<f', struct.pack('<I', b))[0]


def main():
    p.gate(prepared=False)
    p.save(p.PREFIX + '-static-started.json', {'freeze_sha256': p.digest(p.PREFIX + '-freeze.json')})
    freeze = p.read(p.PREFIX + '-freeze.json')
    for name in freeze['sources']:
        if name.endswith('.py'):
            ast.parse((p.HERE / name).read_text(), filename=name)
    html = (p.HERE / p.HTML).read_text()
    js = html.split('<script>')[1].split('</script>')[0]
    old = (p.HERE / 'gpu_centre_v34_offsets.html').read_text()
    shader = old[old.index('window.shaderSource='):old.index('function reportProgram')]
    assert shader in js, 'Original shader construction changed'
    assert 'getTranslatedShaderSource' not in js and 'WEBGL_debug_shaders' not in js
    assert 'forceContextLoss' not in js
    subprocess.run(['node', '--check'], input=js, text=True, check=True, capture_output=True)
    node = r'''
const vm=require('vm'),assert=require('assert');
const context={window:{},Float32Array,Uint32Array};vm.createContext(context);
vm.runInContext(SOURCE,context);
vm.runInContext(`
const savedPerform=perform;let calls=0, queue=[];
gl={NO_ERROR:0,getError:()=>queue.length?queue.shift():0,isContextLost:()=>false};
perform=()=>{calls++;queue.push(1282,1280);return {kept:42};};
let r=window.arithmeticStep({op:'mock'});
if(r.before.errors.length||r.after.errors.join(',')!=='1282,1280'||r.value.kept!==42)throw Error('post errors lost');
queue=[1281];r=window.arithmeticStep({op:'mock'});
if(!r.skipped||calls!==1||r.before.errors[0]!==1281)throw Error('dirty operation executed');
perform=()=>{queue.push(1282);throw Error('deliberate');};r=window.arithmeticStep({op:'mock'});
if(!r.exception.includes('deliberate')||r.after.errors[0]!==1282)throw Error('exception evidence lost');
queue=Array(32).fill(1282);r=window.arithmeticStep({op:'mock'});
if(!r.skipped||r.before.drained||r.before.errors.length!==32)throw Error('unbounded error drain');
perform=()=>({});gl.isContextLost=()=>true;r=window.arithmeticStep({op:'mock'});
if(!r.contextLost)throw Error('context loss omitted');
gl.isContextLost=()=>false;perform=savedPerform;
const packed=pack(new Float32Array([NaN,Infinity,-Infinity,-0]));
if(packed.values.slice(0,3).join(',')!=='NaN,Infinity,-Infinity'||packed.bits[3]!==2147483648)throw Error('invalid float evidence lost');
window.sources=[];
for(let leaf=0;leaf<2;leaf++){
 const literal=window.shaderSource(leaf,'literal'), uniform=window.shaderSource(leaf,'uniform');
 const token='offset(parent,'+(leaf===0?'.20':'.28')+')';
 if(literal.split(token).length!==2||literal.replace(token,'offset(parent,secondOffset)')!==uniform)throw Error('not second-offset only');
 window.sources.push({leaf,literal,uniform});
}
globalThis.THREE={NoBlending:0,ShaderMaterial:class {constructor(o){Object.assign(this,o);}}};
mesh={};texture={};window.uniforms=[];
for(let leaf=0;leaf<2;leaf++)for(const arm of ['literal','uniform']){
 const r=window.arithmeticStep({op:'material',name:leaf?'childAngular':'childAxial',leaf,arm});
 if(r.exception||r.after.errors.length||material.uniforms.inputTex.value!==texture||mesh.material!==material)throw Error('material binding');
 window.uniforms.push(r.value);
}
let methods=[];
function fill(p){if(p.length!==512||!Array.from(p).every(x=>x===-123.75))throw Error('sentinel not initialized');p.fill(.125);}
renderer={readRenderTargetPixels:(t,x,y,w,h,p)=>{methods.push('three');fill(p);}};
gl.readPixels=(x,y,w,h,format,type,p)=>{methods.push('raw');fill(p);};
for(const op of ['read-three','read-raw']){
 const r=window.arithmeticStep({op});
 if(r.exception||r.value.values.length!==512||r.value.bits.length!==512||r.value.method!==op||r.value.values[0]!==.125)throw Error('readback packing');
}
if(methods.join(',')!=='three,raw')throw Error('not independent read APIs');
window.staticResult={plan:makePlan(),sources:window.sources,uniforms:window.uniforms};
`,context);
process.stdout.write(JSON.stringify(context.window.staticResult));
'''.replace('SOURCE', json.dumps(js), 1)
    checked = subprocess.run(['node', '-e', node], text=True, check=True, capture_output=True)
    result = json.loads(checked.stdout); plan = result['plan']
    assert [s['op'] for s in plan[:6]] == ['renderer', 'metadata', 'renderer-extension', 'unmasked-renderer', 'float-extension', 'shared']
    identities = [('float-control', None)] + [(name, arm) for name in ('childAxial', 'childAngular') for arm in ('literal', 'uniform')]
    ops = ['material', 'bind', 'framebuffer-status', 'framebuffer-binding', 'attachment-type',
           'implementation-format', 'implementation-type', 'compile', 'program-reference', 'program-link', 'program-log',
           'render', 'framebuffer-status', 'framebuffer-binding', 'read-three', 'read-raw']
    for i, (name, arm) in enumerate(identities):
        steps = plan[6+i*24:6+(i+1)*24]
        assert len(steps) == 24 and all((s['name'], s.get('arm')) == (name, arm) for s in steps)
        assert [s['op'] for s in steps[:16]] == ops
        assert [(s['shader'], s['op']) for s in steps[16:]] == [(shader, op) for shader in ('vertexShader', 'fragmentShader') for op in ('shader-is', 'shader-compiled', 'shader-log', 'shader-source')]
    assert len(plan) == 126 and not any(s.get('query') for s in plan)
    seeds = p.read(p.SEEDS); leaves = seeds['leaves']; texels = p.inputs()
    assert seeds['synthetic_not_recovered_gpu_intermediates'] and len(leaves) == 2
    oracle_components = 0
    for leaf in leaves:
        row, n = leaf['row'], leaf['count']; xs = texels[row*512:(row+1)*512:4]
        assert 0 < n <= 128 and [p.bit(x) for x in xs[:n]] == leaf['bits']
        assert xs[:n] == leaf['values'] and all(p.bit(x) == 0 for x in xs[n:])
        assert all(texels[row*512+4*i+c] == 0 for i in range(128) for c in (1, 2, 3))
        want = p.expected(leaf, xs)
        for i, x in enumerate(xs):
            parent = integer_add(x, leaf['c1'])
            child = integer_add(frombit(parent), leaf['c2'])
            folded = integer_add(x, frombit(integer_add(leaf['c1'], leaf['c2'])))
            assert [p.bit(v) for v in want[i*4:i*4+4]] == [p.bit(x), parent, child, folded]
            oracle_components += 4
        for u in result['uniforms'][row*2:row*2+2]:
            assert u['uniforms']['textureRow'] == row and u['uniforms']['secondOffsetBits'] == p.bit(leaf['c2'])
    for a,b,want in [(1., 2**-24, 0x3f800000), (frombit(0x3f800001), 2**-24, 0x3f800002),
                     (-0., -0., 0x80000000), (1., -1., 0), (2**-149, 2**-149, 2)]:
        assert integer_add(a,b) == p.bit(p.f32(a+b)) == want

    def good(step, values=None, value=None):
        return {'step': step, 'before': {'errors': [], 'drained': True}, 'after': {'errors': [], 'drained': True},
                'skipped': False, 'contextLost': False, 'exception': None,
                'value': value if value is not None else {'values': values, 'bits': [p.bit(x) for x in values], 'method': step['op'], 'sentinel': -123.75}}
    control = good({'op': 'read-three', 'name': 'float-control'}, [.125,-.5,2.,1.]*128)
    classify = lambda r: p.assess(r, leaves, texels, {})['classification']
    assert classify(control) == 'ok'
    for mutation, want in [({'before': {'errors': [1282], 'drained': True}}, 'fatal-precondition'),
                           ({'before': {'errors': [], 'drained': False}}, 'fatal-precondition'),
                           ({'after': {'errors': [], 'drained': False}}, 'fatal-context'),
                           ({'contextLost': True}, 'fatal-context'), ({'after': {'errors': [1282], 'drained': True}}, 'fatal-operation'),
                           ({'exception': 'deliberate'}, 'fatal-operation')]:
        bad = copy.deepcopy(control); bad.update(mutation); assert classify(bad) == want
    for mutate in (lambda v: v['bits'].__setitem__(17, v['bits'][17]^1), lambda v: v['values'].__setitem__(17,'NaN'),
                   lambda v: v['values'].__setitem__(17, -123.75), lambda v: v['bits'].pop(),
                   lambda v: v['bits'].__setitem__(17, -1)):
        bad = copy.deepcopy(control); mutate(bad['value']); assert classify(bad) == 'fatal-readback'
    bad = good(control['step'], [.25,-.5,2.,1.]*128); assert classify(bad) == 'fatal-control'
    for op, value, want in [('framebuffer-status', {'status':0,'completeEnum':36053}, 'fatal-framebuffer'),
                            ('framebuffer-binding', {'bound':False}, 'fatal-framebuffer'),
                            ('program-link', {'linked':False}, 'fatal-shader'), ('render', {'callbacks':[{}]}, 'fatal-shader'),
                            ('shader-compiled', {'compiled':False}, 'fatal-shader'), ('float-extension', {'supported':False}, 'fatal-backend')]:
        assert classify(good({'op':op},value=value)) == want
    # Mock only browser evaluation; execute the real durability/assessment loop.
    records, assessments, mock_plan, response = [], [], [], {}
    for leaf in leaves:
        xs=texels[leaf['row']*512:(leaf['row']+1)*512:4]
        for arm in ('literal','uniform'):
            values=p.expected(leaf,xs)
            if arm=='literal':
                for i in range(128): values[4*i+2]=values[4*i+3]
            for method in ('read-three','read-raw'):
                step={'op':method,'name':leaf['name'],'leaf':leaf['row'],'arm':arm}
                mock_plan.append(step); response[json.dumps(step)]=good(step,values)
    class Page:
        def evaluate(self, expression, step):
            return copy.deepcopy(response[json.dumps(step)])
    saved_assess = p.assess
    def after_saved(r, *args):
        assert records[-1] == ('step-result', r), 'Assessment preceded evidence'
        assert len(r['value']['values']) == len(r['value']['bits']) == 512
        return saved_assess(r, *args)
    try:
        p.assess = after_saved
        p.run_steps(Page(),mock_plan,lambda k,v:records.append((k,v)),leaves,texels,assessments)
    finally:
        p.assess = saved_assess
    assert len(assessments)==8 and any(a['classification']=='arithmetic-mismatch' for a in assessments)
    assert [k for k,v in records]==['step-intent','step-result','assessment']*8
    assert p.supported(assessments,True) and not p.supported(assessments,False)
    assert not p.supported(assessments[:4],True), 'One leaf is insufficient'
    for index in range(8):
        bad=copy.deepcopy(assessments)
        if bad[index]['step']['arm']=='uniform': bad[index]['unique']['exact']=False
        else: bad[index]['unique']['bit_mismatches_per_channel'][0]=1
        assert not p.supported(bad,True), 'Support criterion relaxed'
    # Fatal transport mismatch stops before the next arm, with evidence intact.
    key=json.dumps(mock_plan[1]); response[key]['value']['bits'][0]^=1
    records=[]
    try:
        p.run_steps(Page(),mock_plan,lambda k,v:records.append((k,v)),leaves,texels,[])
    except RuntimeError as e:
        assert str(e).startswith('fatal-readback')
    else: raise AssertionError('Invalid readback did not halt')
    assert len(records)==6 and records[-2][0]=='step-result'
    response[key]=good(mock_plan[1],p.expected(leaves[0],texels[:512:4]))
    records=[]
    try: p.run_steps(Page(),mock_plan,lambda k,v:records.append((k,v)),leaves,texels,[])
    except RuntimeError as e: assert str(e).startswith('fatal-transport-disagreement')
    else: raise AssertionError('Transport mismatch accepted')
    class ThrowPage:
        def evaluate(self,*args): raise RuntimeError('evaluation failed')
    records=[]
    try: p.run_steps(ThrowPage(),mock_plan,lambda k,v:records.append((k,v)),leaves,texels,[])
    except RuntimeError: pass
    assert [k for k,v in records]==['step-intent','step-exception']
    # JSON may convert -0 to +0, but retained bits must still produce a mismatch.
    step=mock_plan[0]; vals=p.expected(leaves[0],texels[:512:4]); vals[0]=-0.
    z=good(step,vals); z['value']['values'][0]=0
    a=p.assess(z,leaves,texels,{})
    assert a['classification']=='arithmetic-mismatch' and 0 in a['all_texels']['mismatched_components']

    import run_centre_v34_staged_arithmetic_once as launcher
    saved=(launcher.HERE,p.HERE,launcher.gate,launcher.subprocess.run)
    calls=[]
    try:
        with tempfile.TemporaryDirectory(prefix='staged-arithmetic-static-',dir=p.HERE) as temp:
            launcher.HERE=p.HERE=Path(temp);launcher.gate=lambda **kwargs:None
            for name in (launcher.PathName,'probe_centre_v34_staged_arithmetic.py',p.PREFIX+'-freeze.json',p.PREFIX+'-preparation-integrity.json'):
                (p.HERE/name).write_text('mock only')
            def fake(*args,**kwargs): calls.append(args);return subprocess.CompletedProcess(args,7)
            launcher.subprocess.run=fake
            assert launcher.main('runtime')==7
            r=p.read(p.PREFIX+'-runtime-once-exit.json')
            assert r['actual_exit']==7 and r['launcher_error'] is None and r['log_sha256']==p.digest(p.PREFIX+'-runtime-once.log')
            try: launcher.main('runtime')
            except AssertionError: pass
            else: raise AssertionError('Replay accepted')
            assert len(calls)==1
            try: p.save(p.PREFIX+'-runtime-once-exit.json',{})
            except FileExistsError: pass
            else: raise AssertionError('Receipt overwritten')
    finally: launcher.HERE,p.HERE,launcher.gate,launcher.subprocess.run=saved
    p.save(p.PREFIX+'-static.json',{'passed':True,'plan':plan,'shader_sources':result['sources'],
        'integer_oracle_components':oracle_components,'runtime_run':False,'numeric_passed':False,
        'checks':['Python AST / JS syntax; no browser','Original shader function byte-identical; second-offset-only arms',
                  '126 ordered stages; known float first; link before rendering; both full readbacks before shader queries',
                  'Original frozen seeds/texture exact; 1024 arithmetic components vs rational ties-even oracle',
                  'GL pre/post/exception/context/bounded-drain mocks; signed-zero/nonfinite/sentinel/bit checks',
                  'Durable result-before-assessment; mismatch continuation; fatal stop; evaluation exception receipt',
                  'Both leaf/method literal controls and uniform exact criterion; one-leaf support rejected',
                  'Foreground launcher actual exit7 mock, exclusive receipt and replay refusal']})
    print('Static PASS: 126 stages; 1024 independently rounded components; no browser/runtime',flush=True)


if __name__=='__main__':
    main()
