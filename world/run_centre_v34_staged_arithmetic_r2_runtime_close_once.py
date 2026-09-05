"""Single foreground saved-evidence closure with durable actual exit."""
import os
import subprocess
import sys
import probe_centre_v34_staged_arithmetic_r2 as p

stem = p.PREFIX + '-runtime-close-once'
script = 'close_centre_v34_staged_arithmetic_r2_runtime.py'
for suffix in ('-launch.json', '-exit.json', '.log'):
    assert not (p.HERE / (stem + suffix)).exists(), 'Never replay'
p.gate()
argv = [sys.executable, '-B', '-u', str(p.HERE / script)]
p.save(stem + '-launch.json', {'argv': argv, 'script': script, 'script_sha256': p.digest(script),
       'launcher_sha256': p.digest(os.path.basename(__file__)),
       'preparation_sha256': p.digest(p.PREFIX + '-preparation-integrity.json')})
actual, error = None, None
try:
    with (p.HERE / (stem + '.log')).open('x') as f:
        try:
            actual = subprocess.run(argv, cwd=p.HERE.parent, stdout=f, stderr=subprocess.STDOUT, timeout=60).returncode
        finally:
            f.flush(); os.fsync(f.fileno())
except Exception as exc:
    error = str(exc)
p.save(stem + '-exit.json', {'actual_exit': actual, 'launcher_error': error,
       'log_sha256': p.digest(stem + '.log'), 'launch_sha256': p.digest(stem + '-launch.json'),
       'manifest_sha256': p.digest(p.PREFIX + '-runtime-integrity.json') if (p.HERE / (p.PREFIX + '-runtime-integrity.json')).exists() else None})
print('Actual closure exit:', actual, 'launcher error:', error)
sys.exit(actual if actual is not None and actual >= 0 else 1)
