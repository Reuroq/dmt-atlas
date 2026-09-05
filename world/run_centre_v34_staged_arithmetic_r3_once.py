"""Exactly one foreground child with actual exit receipt; no retries."""
import os
import subprocess
import sys
from probe_centre_v34_staged_arithmetic_r3 import HERE, PREFIX, digest, gate, save


def main(label):
    assert label in ('static', 'close', 'runtime')
    gate(prepared=label == 'runtime')
    stem = PREFIX + '-' + label + '-once'
    if label == 'runtime':
        assert not any(HERE.glob(PREFIX + '-event-*'))
        for suffix in ('-started.json', '-result.json'):
            assert not (HERE / (PREFIX + suffix)).exists(), 'Never replay'
    for suffix in ('-' + label + '-once-launch.json', '-' + label + '-once-exit.json', '-' + label + '-once.log',
                   '-' + label + '-started.json', '-' + label + '.json'):
        assert not (HERE / (PREFIX + suffix)).exists(), 'Never replay'
    script = {'static': 'check_centre_v34_staged_arithmetic_r3.py', 'close': 'close_centre_v34_staged_arithmetic_r3_preparation.py',
              'runtime': 'probe_centre_v34_staged_arithmetic_r3.py'}[label]
    save(stem + '-launch.json', {'script': script, 'script_sha256': digest(script),
         'launcher_sha256': digest(PathName), 'child_pid_parent': os.getpid(),
         'freeze_sha256': digest(PREFIX + '-freeze.json'),
         'preparation_sha256': digest(PREFIX + '-preparation-integrity.json') if label == 'runtime' else None,
         'mode': 'foreground subprocess.run, one attempt, 180s timeout'})
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/ms-playwright', PYTHONDONTWRITEBYTECODE='1')
    actual_exit, launcher_error = None, None
    try:
        with (HERE / (stem + '.log')).open('x') as stream:
            try:
                result = subprocess.run([sys.executable, '-B', '-u', str(HERE / script)], cwd=HERE.parent,
                                        env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
                actual_exit = result.returncode
            finally:
                stream.flush(); os.fsync(stream.fileno())
    except Exception as exc:
        launcher_error = str(exc)
    save(stem + '-exit.json', {'actual_exit': actual_exit, 'launcher_error': launcher_error,
         'log_sha256': digest(stem + '.log') if (HERE / (stem + '.log')).exists() else None,
         'launch_sha256': digest(stem + '-launch.json'),
         'manifest_sha256': digest(PREFIX + '-preparation-integrity.json') if label == 'close' and (HERE / (PREFIX + '-preparation-integrity.json')).exists() else None})
    print('Actual exit:', actual_exit, 'launcher error:', launcher_error, flush=True)
    return actual_exit if actual_exit is not None and actual_exit >= 0 else 1


PathName = 'run_centre_v34_staged_arithmetic_r3_once.py'
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
