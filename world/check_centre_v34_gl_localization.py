"""Frozen static checks only: never starts a browser or evaluates field arithmetic."""
import ast
import copy
import json
import struct
import subprocess
import tempfile
from pathlib import Path
import probe_centre_v34_gl_localization as probe


def main():
    probe.gate(prepared=False)
    probe.save(probe.PREFIX + '-static-started.json', {'freeze_sha256': probe.digest(probe.PREFIX + '-freeze.json')})
    freeze = probe.read(probe.PREFIX + '-freeze.json')
    for name in freeze['sources']:
        if name.endswith('.py'):
            ast.parse((probe.HERE / name).read_text(), filename=name)
    html = (probe.HERE / 'gpu_centre_v34_gl_localization.html').read_text()
    js = html.split('<script>')[1].split('</script>')[0]
    subprocess.run(['node', '--check'], input=js, text=True, check=True, capture_output=True)
    checks = r'''
const vm=require('vm'), assert=require('assert');
const context={window:{},Float32Array,Uint8Array,Uint32Array};vm.createContext(context);
vm.runInContext(SOURCE,context);
const checks=`
const originalPerform=perform;
let calls=0, queue=[];
gl={NO_ERROR:0,getError:()=>queue.length?queue.shift():0,isContextLost:()=>false};
perform=()=>{calls++;queue.push(1282,1280);return {retained:42};};
let r=window.localizationStep({op:'mock'});
if(r.before.errors.length||r.after.errors.join(',')!=='1282,1280'||r.value.retained!==42||!r.after.drained)throw Error('post-errors not retained');
queue=[1281];r=window.localizationStep({op:'mock'});
if(!r.skipped||calls!==1||r.before.errors[0]!==1281)throw Error('dirty precondition executed');
perform=()=>{queue.push(1282);throw Error('deliberate exception');};
r=window.localizationStep({op:'mock'});
if(!r.exception.includes('deliberate exception')||r.after.errors[0]!==1282)throw Error('exception lost errors');
queue=Array(32).fill(1282);r=window.localizationStep({op:'mock'});
if(!r.skipped||r.before.drained||r.before.errors.length!==32)throw Error('unbounded/ignored queue');
perform=()=>({});gl.isContextLost=()=>true;r=window.localizationStep({op:'mock'});
if(!r.contextLost)throw Error('lost context omitted');
perform=originalPerform;
const packed=pack(new Float32Array([NaN,Infinity,-Infinity,-0]));
if(packed.values.slice(0,3).join(',')!=='NaN,Infinity,-Infinity'||packed.bits[3]!==2147483648)throw Error('nonfinite or signed-zero evidence lost');
window.staticResult={plan:makePlan(),controls:Object.fromEntries(cases.map(n=>[n,expected(n)]))};
`;
vm.runInContext(checks,context);
process.stdout.write(JSON.stringify(context.window.staticResult));
'''.replace('SOURCE', json.dumps(js), 1)
    checked = subprocess.run(['node', '-e', checks], text=True, check=True, capture_output=True)
    result = json.loads(checked.stdout)
    plan = result['plan']
    for name, values in result['controls'].items():
        assert values == probe.expected(name) and len(values) == 512
        steps = [s for s in plan if s.get('name') == name]
        ops = [s['op'] for s in steps]
        assert ops.count('framebuffer-status') == 2
        assert ops.index('compile') < ops.index('render') < ops.index('read-three') < ops.index('read-raw')
        assert all(i > ops.index('read-raw') for i, s in enumerate(steps) if s.get('query'))
        assert ops.index('debug-extension') > max(i for i, op in enumerate(ops) if op == 'shader-source')
        assert all(i > ops.index('debug-extension') for i, op in enumerate(ops) if op == 'translated-source')
        byte = name == 'byte-constant'
        bits = values if byte else [struct.unpack('<I', struct.pack('<f', x))[0] for x in values]
        good = {'step': {'name': name, 'op': 'read-three'}, 'before': {'errors': [], 'drained': True},
                'after': {'errors': [], 'drained': True}, 'skipped': False, 'contextLost': False,
                'exception': None, 'value': {'expected': values, 'values': values, 'bits': bits}}
        assert probe.assess(good) == 'ok'
        bad = copy.deepcopy(good); bad['value']['bits'][271] ^= 1
        assert probe.assess(bad) == 'fatal-readback', 'One-bit mismatch accepted'
        bad = copy.deepcopy(good); bad['value']['values'] = [165 if byte else -123.75] * 512
        assert probe.assess(bad) == 'fatal-readback', 'Unwritten sentinel accepted'
        bad = copy.deepcopy(good); bad['value']['values'][13] = 'NaN'
        assert probe.assess(bad) == 'fatal-readback'
    for mutation, want in [({'before': {'errors': [1282], 'drained': True}}, 'fatal-precondition'),
                           ({'after': {'errors': [], 'drained': False}}, 'fatal-context'),
                           ({'contextLost': True}, 'fatal-context'),
                           ({'after': {'errors': [1282], 'drained': True}}, 'fatal-operation'),
                           ({'exception': 'deliberate'}, 'fatal-operation')]:
        bad = copy.deepcopy(good); bad.update(mutation); assert probe.assess(bad) == want
    bad = copy.deepcopy(good)
    bad.update(step={'op': 'translated-source', 'query': True}, after={'errors': [1282], 'drained': True})
    assert probe.assess(bad) == 'query-error'
    bad.update(step={'op': 'framebuffer-status'}, after={'errors': [], 'drained': True}, value={'status': 0, 'completeEnum': 36053})
    assert probe.assess(bad) == 'fatal-framebuffer'
    bad.update(step={'op': 'program-link'}, value={'linked': False})
    assert probe.assess(bad) == 'fatal-shader'
    bad.update(step={'op': 'render'}, value={'callbacks': [{'event': 'shader-error-callback'}]})
    assert probe.assess(bad) == 'fatal-shader'
    # Exercise exclusive receipts and replay refusal in a disposable world/ directory.
    # No real subprocess or browser is launched by this synthetic launcher check.
    import run_centre_v34_gl_localization_once as launcher
    saved = (launcher.HERE, probe.HERE, launcher.gate, launcher.subprocess.run)
    calls = []
    try:
        with tempfile.TemporaryDirectory(prefix='gl-localization-static-', dir=probe.HERE) as temp:
            launcher.HERE = probe.HERE = Path(temp)
            for name in (launcher.PathName, 'probe_centre_v34_gl_localization.py', probe.PREFIX + '-preparation-integrity.json'):
                (probe.HERE / name).write_text('synthetic test input')
            launcher.gate = lambda: None
            def fake_run(*args, **kwargs):
                calls.append(args)
                return subprocess.CompletedProcess(args, 7)
            launcher.subprocess.run = fake_run
            assert launcher.main() == 7
            receipt = probe.read(probe.PREFIX + '-once-exit.json')
            assert receipt['actual_exit'] == 7 and receipt['launcher_error'] is None
            assert receipt['log_sha256'] == probe.digest(probe.PREFIX + '-once.log')
            try:
                launcher.main()
            except AssertionError:
                pass
            else:
                raise AssertionError('Replay allowed')
            assert len(calls) == 1
    finally:
        launcher.HERE, probe.HERE, launcher.gate, launcher.subprocess.run = saved
    probe.gate(prepared=False)
    probe.save(probe.PREFIX + '-static.json', {'passed': True, 'freeze_sha256': probe.digest(probe.PREFIX + '-freeze.json'),
               'plan': plan, 'control_count': 4, 'components_per_readback': 512,
               'checks': ['Python AST', 'Node syntax', 'mocked staged errors/exception/context/bound',
                          'nonfinite and signed-zero evidence', 'independent CPU controls',
                          'query ordering', 'one-bit/sentinel/NaN rejection', 'fatal/query classifications',
                          'synthetic mocked exit7 receipt and replay refusal'],
               'browser_runs': 0, 'field_evaluations': 0, 'new_images': 0})
    print('Static preparation PASS:', len(plan), 'stages; no browser/field runtime', flush=True)


if __name__ == '__main__':
    main()
