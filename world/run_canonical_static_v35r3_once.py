"""Exclusive synchronous static stages; receipts contain actual child exit."""
import os
import subprocess
import sys
import additive_runtime_v35r2 as io
from canonical_history_v35r3 import HISTORY, verify_history

PREFIX = 'centre-v35r3-canonical'


def main():
    label = sys.argv[1]; io.require(label in ('build', 'freeze', 'check', 'close'))
    stem = PREFIX+'-'+label+'-once'
    io.require(not any((io.HERE/(stem+s)).exists() for s in
        ('-launch.json', '-exit.json', '.log', '-launch.json.pending')), 'Never replay static attempts')
    verify_history()
    if label != 'build':
        import prepare_canonical_v35r3 as p
        p.receipt('build')
        if label in ('check', 'close'): p.gate(); p.receipt('freeze')
        if label == 'close': p.receipt('check')
    script = 'build_canonical_v35r3.py' if label == 'build' else 'prepare_canonical_v35r3.py'
    argv = [sys.executable, '-B', '-u', str(io.HERE/script)]+([] if label == 'build' else [label])
    io.atomic_json(stem+'-launch.json', {'argv': argv, 'script_sha256': io.digest(script),
        'launcher_sha256': io.digest(os.path.basename(__file__)), 'history_sha256': io.digest(HISTORY),
        'freeze_sha256': io.digest(PREFIX+'-freeze.json') if label in ('check', 'close') else None})
    actual, error = None, None
    try:
        with (io.HERE/(stem+'.log')).open('x') as stream:
            try:
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH='/home/clawd/pixelvision-venv/lib/python3.12/site-packages')
                actual = subprocess.run(argv, cwd=io.HERE.parent, env=env,
                    stdout=stream, stderr=subprocess.STDOUT, timeout=300).returncode
            finally:
                stream.flush(); os.fsync(stream.fileno())
    except BaseException as exc:
        error = repr(exc)
    manifest = PREFIX+'-integrity.json'
    io.atomic_json(stem+'-exit.json', {'actual_exit': actual, 'launcher_error': error,
        'log_sha256': io.digest(stem+'.log'), 'launch_sha256': io.digest(stem+'-launch.json'),
        'manifest_sha256': io.digest(manifest) if label == 'close' and (io.HERE/manifest).exists() else None})
    print(label, 'actual exit', actual, 'launcher error', error, flush=True)
    return actual if actual is not None and actual >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
