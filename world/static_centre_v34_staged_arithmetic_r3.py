"""Durable, foreground, separately identified Node mock stages. No browser."""
import hashlib
import json
import os
import subprocess
import probe_centre_v34_staged_arithmetic_r3 as p


def durable_node(label, source, syntax=False, expected_exit=0):
    stem = p.PREFIX + '-node-' + label
    source_name = stem + '.js'
    with (p.HERE / source_name).open('x') as f:
        f.write(source); f.flush(); os.fsync(f.fileno())
    command = ['node'] + (['--check'] if syntax else []) + [str(p.HERE / source_name)]
    command_hash = hashlib.sha256(json.dumps(command, separators=(',', ':')).encode()).hexdigest()
    p.save(stem + '-launch.json', {'command': command, 'command_sha256': command_hash,
        'source': source_name, 'source_sha256': p.digest(source_name), 'timeout_seconds': 20})
    actual_exit, error, timed_out = None, None, False
    with (p.HERE / (stem + '-stdout.log')).open('xb') as out, (p.HERE / (stem + '-stderr.log')).open('xb') as err:
        try:
            child = subprocess.Popen(command, cwd=p.HERE, stdout=out, stderr=err)
            try:
                actual_exit = child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                timed_out = True
                child.kill(); actual_exit = child.wait()
        except Exception as exc:
            error = repr(exc)
        finally:
            for stream in (out, err):
                stream.flush(); os.fsync(stream.fileno())
    # Receipt must exist before any status classification or output decoding.
    p.save(stem + '-exit.json', {'actual_exit': actual_exit, 'launcher_error': error, 'timed_out': timed_out,
        'launch_sha256': p.digest(stem + '-launch.json'), 'source_sha256': p.digest(source_name),
        'stdout_sha256': p.digest(stem + '-stdout.log'), 'stderr_sha256': p.digest(stem + '-stderr.log')})
    assert error is None and not timed_out and actual_exit == expected_exit, 'Node stage failed: ' + label
    return ((p.HERE / (stem + '-stdout.log')).read_text(), (p.HERE / (stem + '-stderr.log')).read_text())


def staged_checks(js, combined):
    base = "let queue=[],calls=0; gl={NO_ERROR:0,getError:()=>queue.length?queue.shift():0,isContextLost:()=>false};\n"
    stages = [
        ('api', "assert.strictEqual(typeof window.arithmeticStep,'function'); assert.strictEqual(typeof window.arithmeticPlan,'function');"),
        ('post-errors', "perform=()=>{calls++;queue.push(1282,1280);return {kept:42};}; const r=window.arithmeticStep({op:'mock'}); assert.strictEqual(calls,1); assert.strictEqual(r.before.errors.length,0); assert.strictEqual(r.after.errors.join(','),'1282,1280'); assert.strictEqual(r.value.kept,42);"),
        ('dirty-precondition', "queue=[1281];perform=()=>{calls++;};const r=window.arithmeticStep({op:'mock'});assert(r.skipped);assert.strictEqual(calls,0);assert.strictEqual(r.before.errors[0],1281);"),
        ('exception', "perform=()=>{queue.push(1282);throw Error('deliberate');};const r=window.arithmeticStep({op:'mock'});assert(r.exception.includes('deliberate'));assert.strictEqual(r.after.errors[0],1282);"),
        ('bounded-drain', "queue=Array(32).fill(1282);perform=()=>{calls++;};const r=window.arithmeticStep({op:'mock'});assert(r.skipped);assert(!r.before.drained);assert.strictEqual(r.before.errors.length,32);assert.strictEqual(calls,0);"),
        ('context-loss', "perform=()=>({});gl.isContextLost=()=>true;assert(window.arithmeticStep({op:'mock'}).contextLost);"),
        ('packing', "const r=pack(new Float32Array([NaN,Infinity,-Infinity,-0]));assert.strictEqual(r.values.slice(0,3).join(','),'NaN,Infinity,-Infinity');assert.strictEqual(r.bits[3],2147483648);"),
        ('shader-arms', "for(let leaf=0;leaf<2;leaf++){const a=window.shaderSource(leaf,'literal'),b=window.shaderSource(leaf,'uniform'),t='offset(parent,'+(leaf===0?'.20':'.28')+')';assert.strictEqual(a.split(t).length,2);assert.strictEqual(a.replace(t,'offset(parent,secondOffset)'),b);}"),
        ('materials', "globalThis.THREE={NoBlending:0,ShaderMaterial:class{constructor(o){Object.assign(this,o);}}};mesh={};texture={};for(let leaf=0;leaf<2;leaf++)for(const arm of ['literal','uniform']){const r=window.arithmeticStep({op:'material',name:leaf?'childAngular':'childAxial',leaf,arm});assert.strictEqual(r.exception,null);assert.strictEqual(r.after.errors.length,0);assert.strictEqual(material.uniforms.inputTex.value,texture);assert.strictEqual(mesh.material,material);}"),
        ('readbacks', "let methods=[];function fill(p){assert.strictEqual(p.length,512);assert(Array.from(p).every(x=>x===-123.75));p.fill(.125);} renderer={readRenderTargetPixels:(t,x,y,w,h,p)=>{methods.push('three');fill(p);}};gl.readPixels=(x,y,w,h,f,t,p)=>{methods.push('raw');fill(p);};for(const op of ['read-three','read-raw']){const r=window.arithmeticStep({op});assert.strictEqual(r.exception,null);assert.strictEqual(r.value.values.length,512);assert.strictEqual(r.value.bits.length,512);assert.strictEqual(r.value.method,op);assert.strictEqual(r.value.values[0],.125);}assert.strictEqual(methods.join(','),'three,raw');"),
    ]
    for label, body in stages:
        source = "const vm=require('vm'),assert=require('assert');const context={window:{},Float32Array,Uint32Array,assert};vm.createContext(context);\n"
        source += 'vm.runInContext(' + json.dumps(js) + ',context);\n'
        source += 'vm.runInContext(' + json.dumps(base + body) + ',context);\n'
        durable_node(label, source)
    stdout, stderr = durable_node('combined', combined)
    assert not stderr
    return json.loads(stdout)
