"""Foreground only, unique launch/log/actual-exit receipts, no retries."""
import os
import subprocess
import sys
from centre_v34_followup_common import HERE, PREFIX, digest, save, historical, frozen, runtime_gate, receipt

TASKS = {'prepare': 'prepare_centre_v34_followup.py', 'static': 'check_centre_v34_followup.py',
         'close': 'close_centre_v34_followup_preparation.py',
         'arithmetic': 'microprobe_centre_v34_offsets.py', 'profiles': 'profile_centre_v34_four_rays.py'}


def main():
    label = sys.argv[1]
    script = TASKS[label]
    if label == 'prepare':
        historical()
    elif label == 'static':
        frozen(); receipt('prepare')
    elif label == 'close':
        frozen(); receipt('prepare'); receipt('static')
    else:
        runtime_gate()
    stem = PREFIX + '-' + label + '-once'
    assert not any((HERE / (stem + suffix)).exists() for suffix in ['-launch.json', '-exit.json', '.log']), 'Never replay'
    save(stem + '-launch.json', {'script': script, 'script_sha256': digest(script),
         'launcher_sha256': digest(PathName), 'label': label,
         'input_manifest': None if label == 'prepare' else digest(PREFIX + '-inputs.json'),
         'preparation_manifest': digest(PREFIX + '-preparation-integrity.json') if label in ['arithmetic', 'profiles'] else None})
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/ms-playwright', PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH='/home/clawd/pixelvision-venv/lib/python3.12/site-packages')
    with (HERE / (stem + '.log')).open('x') as stream:
        result = subprocess.run([sys.executable, '-B', '-u', str(HERE / script)], cwd=HERE.parent,
                                stdout=stream, stderr=subprocess.STDOUT, env=env)
        stream.flush(); os.fsync(stream.fileno())
    save(stem + '-exit.json', {'actual_exit': result.returncode,
         'log_sha256': digest(stem + '.log'), 'launch_sha256': digest(stem + '-launch.json')})
    print(label, 'actual exit', result.returncode, 'log', stem + '.log', flush=True)
    return result.returncode if result.returncode >= 0 else 128-result.returncode


PathName = 'run_centre_v34_followup_once.py'
if __name__ == '__main__':
    sys.exit(main())
