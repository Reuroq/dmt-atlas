"""Frozen v35 preparation support; no field evaluation or browser imports."""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v35'
HISTORY = 'centre-v34-staged-arithmetic-r3-runtime-integrity.json'


def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def write(name, data):
    with (HERE / name).open('xb') as stream:
        stream.write(data if isinstance(data, bytes) else data.encode())
        stream.flush(); os.fsync(stream.fileno())


def save(name, value):
    write(name, json.dumps(value, indent=2) + '\n')


def verify(group):
    for name, want in group.items():
        assert digest(name) == want, name


def history(display=True):
    prior = read(HISTORY)
    for key in ('files', 'protected') + (('display',) if display else ()):
        verify(prior[key])
    stem = 'centre-v34-staged-arithmetic-r3-runtime-close-once'
    receipt, launch = read(stem + '-exit.json'), read(stem + '-launch.json')
    assert receipt['actual_exit'] == 0 and receipt['launcher_error'] is None
    for key, name in [('log_sha256', stem + '.log'), ('launch_sha256', stem + '-launch.json'), ('manifest_sha256', HISTORY)]:
        assert receipt[key] == digest(name), key
    for key, name in [('script_sha256', launch['script']),
                      ('launcher_sha256', 'run_centre_v34_staged_arithmetic_r3_runtime_close_once.py'),
                      ('preparation_sha256', 'centre-v34-staged-arithmetic-r3-preparation-integrity.json')]:
        assert launch[key] == digest(name), key
    assert prior['synthetic_uniform_candidate_supported'] is True
    return prior


def frozen(display=True):
    freeze = read(PREFIX + '-freeze.json')
    assert freeze['history_sha256'] == digest(HISTORY)
    verify(freeze['sources'])
    history(display)
    return freeze


def receipt(label):
    stem = PREFIX + '-' + label + '-once'
    result, launch = read(stem + '-exit.json'), read(stem + '-launch.json')
    assert result['actual_exit'] == 0 and result['launcher_error'] is None, label
    assert result['log_sha256'] == digest(stem + '.log')
    assert result['launch_sha256'] == digest(stem + '-launch.json')
    assert launch['script_sha256'] == digest(launch['script'])
    assert launch['launcher_sha256'] == digest('run_centre_v35_preparation_once.py')
    if label != 'build':
        assert launch['freeze_sha256'] == digest(PREFIX + '-freeze.json')
    if label == 'close':
        assert result['manifest_sha256'] == digest(PREFIX + '-fixture-integrity.json')
    return result


def closed():
    frozen(display=False)
    for label in ('build', 'static', 'close'):
        receipt(label)

