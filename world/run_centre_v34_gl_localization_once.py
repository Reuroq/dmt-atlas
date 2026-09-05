"""Exactly one foreground child with actual exit receipt; no retries."""
import os
import subprocess
import sys
from probe_centre_v34_gl_localization import HERE, PREFIX, digest, gate, save


def main():
    gate()
    stem = PREFIX + '-once'
    assert not any(HERE.glob(PREFIX + '-event-*'))
    for suffix in ('-once-launch.json', '-once-exit.json', '-once.log', '-started.json', '-result.json'):
        assert not (HERE / (PREFIX + suffix)).exists(), 'Never replay'
    script = 'probe_centre_v34_gl_localization.py'
    save(stem + '-launch.json', {'script': script, 'script_sha256': digest(script),
         'launcher_sha256': digest(PathName), 'child_pid_parent': os.getpid(),
         'preparation_sha256': digest(PREFIX + '-preparation-integrity.json'),
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
         'launch_sha256': digest(stem + '-launch.json')})
    print('Actual exit:', actual_exit, 'launcher error:', launcher_error, flush=True)
    return actual_exit if actual_exit is not None and actual_exit >= 0 else 1


PathName = 'run_centre_v34_gl_localization_once.py'
if __name__ == '__main__':
    sys.exit(main())
