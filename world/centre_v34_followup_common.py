"""Isolated follow-up infrastructure; never authorizes a v34 acceptance replay."""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v34-followup'
HISTORY = 'centre-v34-saved-investigation-integrity.json'
SOURCES = ['centre_v34_followup_common.py', 'prepare_centre_v34_followup.py',
           'check_centre_v34_followup.py', 'run_centre_v34_followup_once.py',
           'microprobe_centre_v34_offsets.py', 'profile_centre_v34_four_rays.py',
           'close_centre_v34_followup_preparation.py',
           'gpu_centre_v34_offsets.html', 'field_centre_v34.py',
           'vendor/three.min.js', 'centre-v34-followup-experiment-design.md']
LEAVES = ['parentF', 'parentAxial', 'parentAngular', 'parentPositive', 'parentNegative',
          'childF', 'childAxial', 'childAngular', 'childPositive', 'childNegative', 'backingF']
ARGS = ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
        '--allow-file-access-from-files']


def digest(name):
    with (HERE / name).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def save(name, value):
    """Exclusive durable evidence; a partial write also blocks replay."""
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def verify(hashes):
    for name, expected in hashes.items():
        assert digest(name) == expected, name


def historical(display=True):
    manifest = read(HISTORY)
    assert manifest['integrity_passed'] and not manifest['numeric_passed']
    assert not manifest['capture_permitted']
    for group in ['files', 'protected'] + (['display'] if display else []):
        verify(manifest[group])
    return manifest


def frozen():
    manifest = read(PREFIX + '-inputs.json')
    assert manifest['historical_manifest'] == digest(HISTORY)
    verify(manifest['files'])
    historical(display=False)
    return manifest


def receipt(label):
    stem = PREFIX + '-' + label + '-once'
    value = read(stem + '-exit.json')
    assert value['actual_exit'] == 0, label
    assert value['log_sha256'] == digest(stem + '.log')
    assert value['launch_sha256'] == digest(stem + '-launch.json')
    launch = read(stem + '-launch.json')
    assert launch['script_sha256'] == digest(launch['script'])
    assert launch['launcher_sha256'] == digest('run_centre_v34_followup_once.py')
    if launch['input_manifest'] is not None:
        assert launch['input_manifest'] == digest(PREFIX + '-inputs.json')


def runtime_gate():
    frozen()
    receipt('prepare')
    receipt('static')
    receipt('close')
    closure = read(PREFIX + '-preparation-integrity.json')
    assert closure['static_passed'] and not closure['numeric_passed']
    assert not closure['capture_permitted']
    verify(closure['files'])
    verify(closure['display'])


def bits(values):
    import numpy as np
    return np.asarray(values, dtype=np.float32).view(np.uint32)


def compare_arm(rows, inputs, c1, c2):
    import numpy as np
    got = np.asarray(rows, dtype=np.float32).reshape(-1, 4)
    x = np.asarray(inputs, dtype=np.float32)
    parent = np.float32(x + np.float32(c1))
    child = np.float32(parent + np.float32(c2))
    folded = np.float32(x + np.float32(np.float32(c1) + np.float32(c2)))
    expected = np.stack([x, parent, child, folded], axis=-1)
    separate = bits(got) != bits(expected)
    replay = bits(got[:, 2]) != bits(np.float32(got[:, 1] + np.float32(c2)))
    return {'expected_separately_rounded_and_folded_control': expected.astype(float).tolist(),
            'bit_mismatches_per_channel': separate.sum(axis=0).tolist(),
            'numeric_mismatches_per_channel': (got != expected).sum(axis=0).tolist(),
            'child_vs_saved_microprobe_parent_mismatches': int(replay.sum()),
            'failed_indices': np.flatnonzero(np.any(separate, axis=1) | replay).tolist(),
            'exact': bool(not np.any(separate) and not np.any(replay))}
