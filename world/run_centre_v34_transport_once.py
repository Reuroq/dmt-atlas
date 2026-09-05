"""Exclusive foreground launch; incomplete attempts remain non-replayable."""
import os
import subprocess
import sys
import probe_centre_v34_transport as t
p = t.p
mode = sys.argv[1]
assert mode in ('static', 'runtime')
stem = t.PREFIX + '-' + mode + '-once'
t.prior(mode == 'static')
freeze = p.read(t.PREFIX + '-freeze.json')
p.verify(freeze['sources'])
assert freeze['environment'] == t.environment()
if mode == 'runtime':
    prep = p.read(t.PREFIX + '-preparation-integrity.json')
    for key in ('files', 'protected', 'display'): p.verify(prep[key])
    assert prep['static_passed'] and not prep['runtime_run']
    assert p.read(t.PREFIX + '-static-once-exit.json')['actual_exit'] == 0
    assert not list(p.HERE.glob(t.PREFIX + '-event-*')) and not (p.HERE / (t.PREFIX + '-result.json')).exists()
for suffix in ('-launch.json', '-exit.json', '.log'):
    assert not (p.HERE / (stem + suffix)).exists(), 'Never replay'
argv = [sys.executable, '-B', '-u', str(p.HERE / 'probe_centre_v34_transport.py'), mode]
p.save(stem + '-launch.json', {'argv': argv, 'freeze_sha256': p.digest(t.PREFIX + '-freeze.json'),
       'script_sha256': p.digest('probe_centre_v34_transport.py'), 'launcher_sha256': p.digest(os.path.basename(__file__)),
       'preparation_sha256': p.digest(t.PREFIX + '-preparation-integrity.json') if mode == 'runtime' else None})
actual, error = None, None
try:
    with (p.HERE / (stem + '.log')).open('x') as f:
        try: actual = subprocess.run(argv, cwd=p.HERE.parent, stdout=f, stderr=subprocess.STDOUT, timeout=60).returncode
        finally: f.flush(); os.fsync(f.fileno())
except Exception as exc: error = str(exc)
p.save(stem + '-exit.json', {'actual_exit': actual, 'launcher_error': error,
       'log_sha256': p.digest(stem + '.log'), 'launch_sha256': p.digest(stem + '-launch.json')})
print(mode, 'actual exit:', actual, 'launcher error:', error)
sys.exit(actual if actual is not None and actual >= 0 else 1)
