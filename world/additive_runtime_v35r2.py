"""Exclusive foreground evidence stages. Importing this module samples no field."""
import hashlib
import json
import math
import os
import signal
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v35r2-additive'
MANIFEST = PREFIX+'-integrity.json'
HISTORY = 'centre-v35r2-root-contract-integrity.json'
STAGES = ('bounds', 'numerical', 'local', 'global', 'combination')
SCRIPTS = dict(zip(STAGES, ('bounds_additive_v35r2.py', 'numeric_additive_v35r2.py',
    'local_additive_v35r2.py', 'global_additive_v35r2.py', 'combine_additive_v35r2.py')))
READY = dict(zip(STAGES, ('passed', 'non_reference_checks_passed',
    'root_certification_ready', 'global_roots_passed', 'numeric_passed')))


def require(condition, message='Evidence contract failed'):
    if not condition:
        raise AssertionError(message)


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def read(name):
    def invalid(value):
        raise ValueError('Nonfinite JSON: '+value)
    return json.loads((HERE/name).read_text(), parse_constant=invalid)


def atomic_json(path, data):
    """No replacement of final OR partial evidence; fsync file and directory."""
    path = Path(path)
    if not path.is_absolute():
        path = HERE/path
    require(path.resolve().is_relative_to(HERE), 'Writes must stay under world/')
    pending = path.with_suffix(path.suffix+'.pending')
    require(not path.exists() and not pending.exists(), 'Never overwrite/replay')
    with pending.open('x') as stream:
        json.dump(data, stream, allow_nan=False, separators=(',', ':'))
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.link(pending, path)  # Exclusive publication, unlike replace().
    pending.unlink()
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def verify(group):
    for name, want in group.items():
        require(digest(name) == want, 'Hash mismatch: '+name)


def directory(stage):
    require(stage in STAGES)
    return HERE/(PREFIX+'-'+stage)


def artifact(stage, name):
    return str((directory(stage)/name).relative_to(HERE))


def static_receipt(label):
    stem=PREFIX+'-'+label+'-once'
    receipt, launch=read(stem+'-exit.json'), read(stem+'-launch.json')
    require(type(receipt['actual_exit']) is int and receipt['actual_exit'] == 0 and receipt['launcher_error'] is None)
    require(receipt['log_sha256'] == digest(stem+'.log'))
    require(receipt['launch_sha256'] == digest(stem+'-launch.json'))
    require(launch['script_sha256'] == digest('prepare_additive_v35r2.py'))
    require(launch['launcher_sha256'] == digest('run_additive_static_v35r2_once.py'))
    if label == 'close':
        require(receipt['manifest_sha256'] == digest(MANIFEST))


def fixture_gate():
    gate=read(MANIFEST)
    require(gate['static_passed'] is True and gate['runtime_fixtures_complete'] is True)
    require(gate['numerical_run'] is False and gate['capture_permitted'] is False)
    for group in ('files', 'protected', 'display'):
        verify(gate[group])
    for label in ('freeze', 'check', 'close'):
        static_receipt(label)
    return gate


def inventory(stage, exclude=()):
    root=directory(stage)
    return {str(p.relative_to(HERE)):digest(str(p.relative_to(HERE)))
            for p in sorted(root.rglob('*')) if p.is_file() and p.name not in exclude}


def stage_receipt(stage):
    receipt=read(artifact(stage, 'exit.json'))
    require(type(receipt['actual_exit']) is int and receipt['actual_exit'] == 0 and receipt['launcher_error'] is None, stage+' exit')
    require(receipt['files'] == inventory(stage, ('exit.json',)), stage+' inventory')
    launch=read(artifact(stage, 'launch.json'))
    require(launch['stage'] == stage and launch['manifest_sha256'] == digest(MANIFEST))
    require(launch['script_sha256'] == digest(SCRIPTS[stage]))
    require(launch['launcher_sha256'] == digest('run_additive_v35r2_once.py'))
    require(launch['prerequisites'] == prerequisite_hashes(stage))
    started=read(artifact(stage,'started.json'))
    require(started == {'stage':stage,'launch_sha256':digest(artifact(stage,'launch.json'))})
    complete=read(artifact(stage, 'completed.json'))
    require(complete['result_sha256'] == digest(artifact(stage, 'result.json')))
    require(not (directory(stage)/'failure.json').exists())
    require(not list(directory(stage).rglob('*.pending')), 'Partial evidence')
    result=read(artifact(stage, 'result.json'))
    require(result[READY[stage]] is True, stage+' not eligible')
    return result


def eligibility(stage):
    fixture_gate()
    require(stage in STAGES)
    return {prior:stage_receipt(prior) for prior in STAGES[:STAGES.index(stage)]}


def prerequisite_hashes(stage):
    return {artifact(prior,'exit.json'):digest(artifact(prior,'exit.json'))
            for prior in STAGES[:STAGES.index(stage)]}


def worker(stage, callback):
    """Only a claimed launcher attempt can enter; a late failure blocks exit0."""
    eligibility(stage)
    launch=read(artifact(stage, 'launch.json'))
    require(launch['stage'] == stage and launch['script_sha256'] == digest(SCRIPTS[stage]))
    require(launch['manifest_sha256'] == digest(MANIFEST))
    require(launch['launcher_sha256'] == digest('run_additive_v35r2_once.py'))
    require(launch['prerequisites'] == prerequisite_hashes(stage))
    atomic_json(artifact(stage, 'started.json'), {'stage':stage, 'launch_sha256':digest(artifact(stage,'launch.json'))})
    def stop(signum, frame):
        raise RuntimeError('Worker signal '+str(signum))
    old={s:signal.signal(s,stop) for s in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP)}
    try:
        callback()
        eligibility(stage)
        result=read(artifact(stage,'result.json'))
        require(result[READY[stage]] is True, stage+' result failed; preserve attempt')
        atomic_json(artifact(stage,'completed.json'), {'result_sha256':digest(artifact(stage,'result.json'))})
    except BaseException as exc:
        atomic_json(artifact(stage,'failure.json'), {'failure':repr(exc), 'numeric_passed':False,
            'action':'Hold every downstream stage; never replay this attempt'})
        raise
    finally:
        for sig,handler in old.items():
            signal.signal(sig,handler)


def expected_cases():
    # Independently enumerated, NOT inferred from GPU hits or existing records.
    return [(w,h,z,t,high) for w,h,times in
            [(48,32,[2.4077,3.5242,4,4.895,8]),(49,33,[2.4077,3.5242,4,4.895,8,221,900])]
            for z in (8,-6) for t in times for high in (1,0)]


def expected_keys():
    keys=[]
    for w,h,z,t,high in expected_cases():
        indices={i*(w*h-1)//5 for i in range(6)}
        indices.update((h//2+dy)*w+w//2+dx for dy in (-1,0,1) for dx in (-1,0,1))
        keys.extend((w,h,z,t,high,index) for index in sorted(indices))
    require(len(keys) == len(set(keys)) == 720)
    return keys


def key(record):
    result=tuple(record[k] for k in ('width','height','z','time','high'))
    require(all(type(v) in (int,float) and math.isfinite(v) for v in result))
    require(all(type(result[i]) is int for i in (0,1,2,4)))
    return result


def bijection(expected, records, get_key):
    expected=[tuple(k) for k in expected]
    result={}
    require(len(expected)==len(set(expected)))
    for record in records:
        k=tuple(get_key(record))
        require(all(type(v) in (int,float) and math.isfinite(v) for v in k))
        require(k not in result, 'Duplicate identity')
        result[k]=record
    require(set(result)==set(expected) and len(result)==len(expected), 'Incomplete/extra identities')
    return result


class Journal:
    def __init__(self, path):
        self.path=Path(path); self.path.mkdir(); self.sequence=0

    def record(self, event, **data):
        atomic_json(self.path/f'{self.sequence:04d}-{event}.json',
                    {'sequence':self.sequence,'event':event,**data})
        self.sequence+=1

    def hashes(self):
        return {str(p.relative_to(HERE)):digest(str(p.relative_to(HERE))) for p in sorted(self.path.iterdir())}
