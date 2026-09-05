"""Create a distinct, unfrozen arithmetic successor; never execute its probe."""
import ast
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = 'centre_v34_staged_arithmetic_r2'
NEW = 'centre_v34_staged_arithmetic_r3'
PREFIX = 'centre-v34-staged-arithmetic-r3'
changes = {}


def write(name, text):
    with (HERE / name).open('x') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())


def revise(name, edits):
    original = (HERE / name).read_text()
    text = original.replace(OLD, NEW).replace('centre-v34-staged-arithmetic-r2', PREFIX)
    for before, after in edits:
        assert text.count(before) == 1, (name, before[:100], text.count(before))
        text = text.replace(before, after, 1)
    target = name.replace(OLD, NEW)
    if target.endswith('.py'):
        ast.parse(text, filename=target)
    write(target, text)
    changes[target] = {'base': name, 'base_sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest(),
                       'edits': edits, 'sha256': hashlib.sha256(text.encode()).hexdigest()}


def main():
    assert not (HERE / (PREFIX + '-source-delta.json')).exists(), 'Never replay builder'
    helpers = '''
const identities=new Map(), cleanupOrder=[];
function register(resource,kind) {
 if(identities.has(resource))throw Error('Duplicate resource identity');
 const entry={id:'resource-'+resources.length,kind,resource,attempted:false,succeeded:false,error:null};
 identities.set(resource,entry);resources.push(entry);return resource;
}
function resourceSnapshot() {
 return resources.map(({resource,...entry})=>({...entry}));
}
function cleanup() {
 for(const e of [...resources.filter(e=>e.kind!=='renderer'),...resources.filter(e=>e.kind==='renderer')]) {
  if(e.attempted)continue;
  e.attempted=true;cleanupOrder.push(e.id);
  try {e.resource.dispose();e.succeeded=true;}catch(error){e.error=String(error.stack||error);}
 }
 const registered=resourceSnapshot();
 return {registered,attempted:cleanupOrder.slice(),succeeded:registered.filter(e=>e.succeeded).map(e=>e.id),
  errors:registered.filter(e=>e.error!==null).map(e=>({id:e.id,error:e.error})),
  rendererDisposed:registered.some(e=>e.kind==='renderer'&&e.succeeded),
  complete:registered.every(e=>e.attempted&&e.succeeded&&e.error===null)};
}
function cleanupDrain() {
 try{return drainErrors();}catch(error){return {errors:[],drained:false,exception:String(error.stack||error)};}
}
'''
    revise('gpu_' + OLD + '.html', [
        ('const vertexShader=', helpers + '\nconst vertexShader='),
        ('renderer=new THREE.WebGLRenderer({antialias:false});', "renderer=register(new THREE.WebGLRenderer({antialias:false}),'renderer');"),
        ('const data=new Float32Array(s.data);', "if(!Array.isArray(s.dataBits)||s.dataBits.length!==1024||!s.dataBits.every(b=>Number.isInteger(b)&&b>=0&&b<=0xffffffff))throw Error('Invalid uint32 input');\n  const words=new Uint32Array(s.dataBits),data=new Float32Array(words.buffer);"),
        ('target=new THREE.WebGLRenderTarget(W,1,{type:THREE.FloatType,minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,depthBuffer:false});resources.push(target);', "target=register(new THREE.WebGLRenderTarget(W,1,{type:THREE.FloatType,minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,depthBuffer:false}),'target');"),
        ('texture=new THREE.DataTexture(data,W,2,THREE.RGBAFormat,THREE.FloatType);', "texture=register(new THREE.DataTexture(data,W,2,THREE.RGBAFormat,THREE.FloatType),'texture');"),
        ('texture.needsUpdate=true;resources.push(texture);', 'texture.needsUpdate=true;'),
        ('geometry=new THREE.PlaneGeometry(2,2);resources.push(geometry);', "geometry=register(new THREE.PlaneGeometry(2,2),'geometry');"),
        ('mesh=new THREE.Mesh(geometry);', 'mesh=new THREE.Mesh(geometry,null);'),
        ('material=new THREE.ShaderMaterial({vertexShader,fragmentShader,uniforms,depthTest:false,depthWrite:false,blending:THREE.NoBlending});\n  resources.push(material);', "material=register(new THREE.ShaderMaterial({vertexShader,fragmentShader,uniforms,depthTest:false,depthWrite:false,blending:THREE.NoBlending}),'material');\n  "),
        ("case 'dispose': for(const resource of resources)resource.dispose();if(renderer)renderer.dispose();return {resourcesDisposed:resources.length,rendererDisposed:!!renderer};", "case 'dispose': return cleanup();"),
        ('const before=drainErrors();\n const r=', "const disposing=s.op==='dispose',before=disposing?cleanupDrain():drainErrors();\n const r="),
        ("if(!before.drained||before.errors.length){r.skipped=true;r.reason='dirty pre-operation error queue';return r;}", "if(!disposing&&(!before.drained||before.errors.length)){r.skipped=true;r.reason='dirty pre-operation error queue';r.resources=resourceSnapshot();return r;}"),
        ('finally {r.after=drainErrors();r.contextLost=gl?gl.isContextLost():false;}', "finally {\n  r.resources=resourceSnapshot();r.after=disposing?cleanupDrain():drainErrors();\n  try{r.contextLost=gl?gl.isContextLost():false;}catch(error){r.contextLost=true;r.contextException=String(error.stack||error);}\n }"),
    ])
    gate = '''def prior(display=False):
    import probe_centre_v34_transport as t
    history = read(HISTORY)
    for key in ('files', 'protected') + (('display',) if display else ()):
        verify(history[key])
    stem = t.PREFIX + '-runtime-close-once'
    r, launch = read(stem + '-exit.json'), read(stem + '-launch.json')
    assert r['actual_exit'] == 0 and r['launcher_error'] is None
    for key, name in [('log_sha256', stem + '.log'), ('launch_sha256', stem + '-launch.json'), ('manifest_sha256', HISTORY)]:
        assert r[key] == digest(name)
    assert launch['script_sha256'] == digest(launch['script'])
    assert launch['launcher_sha256'] == digest('run_centre_v34_transport_runtime_close_once.py')
    assert launch['preparation_sha256'] == digest(t.PREFIX + '-preparation-integrity.json')
    assert read(t.PREFIX + '-freeze.json')['environment'] == t.environment()
    return history


def gate(prepared=True):
    freeze = read(PREFIX + '-freeze.json')
    verify(freeze['sources'])
    assert digest(HISTORY) == freeze['history_sha256']
    prior(display=not prepared)
    if prepared:
        prep = read(PREFIX + '-preparation-integrity.json')
        for key in ('files', 'display', 'protected'): verify(prep[key])
        assert prep['static_passed'] and not prep['runtime_run']
        assert read(PREFIX + '-static.json')['passed']
        receipt('static'); receipt('close')
        assert read(PREFIX + '-close-once-exit.json')['manifest_sha256'] == digest(PREFIX + '-preparation-integrity.json')


'''
    probe = (HERE / ('probe_' + OLD + '.py')).read_text()
    oldgate = probe[probe.index('def gate('):probe.index('def receipt(')]
    helpers_py = '''def source_bits():
    return list(struct.unpack('<1024I', (HERE / TEXTURE).read_bytes()))


def exact_words(words, expected):
    return isinstance(words, list) and len(words) == len(expected) and all(type(b) is int and 0 <= b <= 0xffffffff for b in words) and words == expected


def resource_valid(entries):
    if not isinstance(entries, list): return False
    kinds = ('renderer', 'target', 'texture', 'geometry', 'material')
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or set(e) != {'id','kind','attempted','succeeded','error'}: return False
        if e['id'] != 'resource-' + str(i) or e['kind'] not in kinds: return False
        if type(e['attempted']) is not bool or type(e['succeeded']) is not bool: return False
        if e['error'] is not None and (type(e['error']) is not str or not e['error']): return False
        if e['succeeded'] and (not e['attempted'] or e['error'] is not None): return False
        if e['error'] is not None and (not e['attempted'] or e['succeeded']): return False
    return sum(e['kind'] == 'renderer' for e in entries) <= 1


def cleanup_valid(v, entries):
    if not resource_valid(entries) or not isinstance(v, dict) or v.get('registered') != entries: return False
    expected_order = [e['id'] for e in entries if e['kind'] != 'renderer'] + [e['id'] for e in entries if e['kind'] == 'renderer']
    return (v.get('attempted') == expected_order and v.get('succeeded') == [e['id'] for e in entries]
            and v.get('errors') == [] and v.get('complete') is True
            and v.get('rendererDisposed') is any(e['kind'] == 'renderer' for e in entries)
            and all(e['attempted'] and e['succeeded'] and e['error'] is None for e in entries))


'''
    revise('probe_' + OLD + '.py', [
        ("HISTORY = 'centre-v34-staged-arithmetic-preparation-failure-integrity.json'", "HISTORY = 'centre-v34-transport-runtime-integrity.json'"),
        (oldgate, gate),
        ('def assess(', helpers_py + 'def assess('),
        ("if op == 'dispose' and (not v['rendererDisposed'] or v['resourcesDisposed'] != 8):", "if op == 'dispose' and not cleanup_valid(v, r.get('resources')):"),
        ("if op == 'shared' and (v['input']['values'] != texels or v['input']['bits'] != [bit(x) for x in texels]", "if op == 'shared' and (not exact_words(s.get('dataBits'), source_bits()) or v['input']['values'] != texels\n                           or not exact_words(v['input']['bits'], source_bits())"),
        ("request['data'] = texels", "request['dataBits'] = source_bits()"),
        ('readbacks = {}\n    for step in plan:', 'readbacks = {}\n    previous_resources = []\n    for step in plan:'),
        ('a = assess(r, leaves, texels, readbacks)\n        assessments.append(a);', "resources = r.get('resources')\n        identity_ok = resource_valid(resources) and resources[:len(previous_resources)] == previous_resources\n        a = assess(r, leaves, texels, readbacks) if identity_ok else {'step': r['step'], 'classification': 'fatal-resource-identity'}\n        if identity_ok: previous_resources = resources\n        assessments.append(a);"),
        ('failure = None\n    leaves,', 'failure = cleanup_failure = None\n    leaves,'),
        ("failure = 'Resource disposal failed; see durable evidence'", "cleanup_failure = failure = 'Resource disposal failed; see durable evidence'"),
        ("failure = 'Resource disposal incomplete'", "cleanup_failure = failure = 'Resource disposal incomplete'"),
        ('a = assess(r, leaves, texels, {})\n                        event', "prior_steps = [read(n)['payload'] for n in events if read(n)['kind'] == 'step-result']\n                        prior_resources = prior_steps[-1].get('resources', []) if prior_steps else []\n                        ids = lambda es: [(e['id'], e['kind']) for e in es]\n                        registry_ok = resource_valid(r.get('resources')) and ids(r['resources']) == ids(prior_resources)\n                        a = assess(r, leaves, texels, {}) if registry_ok else {'step': r['step'], 'classification': 'fatal-resource-identity'}\n                        event"),
        ("'browser_messages': messages,", "'cleanup_failure': cleanup_failure, 'browser_messages': messages,"),
    ])
    revise('run_' + OLD + '_once.py', [
        ("'launch_sha256': digest(stem + '-launch.json')})", "'launch_sha256': digest(stem + '-launch.json'),\n         'manifest_sha256': digest(PREFIX + '-preparation-integrity.json') if label == 'close' and (HERE / (PREFIX + '-preparation-integrity.json')).exists() else None})"),
    ])
    static = (HERE / ('static_' + OLD + '.py')).read_text()
    oldrepro = static[static.index('    old_html ='):static.index('    base =')]
    revise('static_' + OLD + '.py', [(oldrepro, '')])
    check = (HERE / ('check_' + OLD + '.py')).read_text()
    oldpreserve = check[check.index('    baseline ='):check.index("    durable_node('syntax'")]
    newpreserve = '''    from checks_centre_v34_staged_arithmetic_r3 import check_changes, extra_checks
    check_changes()
    prior_tree = ast.parse((p.HERE / 'probe_centre_v34_staged_arithmetic_r2.py').read_text())
    current_tree = ast.parse((p.HERE / 'probe_centre_v34_staged_arithmetic_r3.py').read_text())
    for name in ('f32','bit','inputs','expected','compare','supported'):
        pick = lambda tree: next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(pick(prior_tree)) == ast.dump(pick(current_tree)), name
    extra_checks(js)

'''
    # revise() applies the mechanical rename before the targeted replacements.
    oldpreserve = oldpreserve.replace(OLD, NEW)
    revise('check_' + OLD + '.py', [
        (oldpreserve, newpreserve),
        ("'skipped': False, 'contextLost': False, 'exception': None,", "'skipped': False, 'contextLost': False, 'exception': None, 'resources': [],"),
    ])
    write(PREFIX + '-source-delta.json', json.dumps(changes, indent=2) + '\n')
    print('Distinct r3 sources created; not frozen or executed')


if __name__ == '__main__':
    main()
