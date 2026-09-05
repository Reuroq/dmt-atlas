"""Foreground launcher: unique log, durable actual child exit; no automatic retries."""
import json
import os
import subprocess
import sys
from pathlib import Path
from cost_lifecycle_v35r2 import atomic_json
from runtime_centre_v35r2 import fixture_gate, passed, digest

HERE = Path(__file__).resolve().parent
GATES = {
    'bounds': ('check_centre_v35r2_bounds.py', []),
    'gpu': ('probe_numeric_candidate_v35r2.py', [('centre-v35r2-bounds-check.json', 'source_hashes')]),
    'roots': ('audit_centre_v35r2_first_roots.py', [('numeric-candidate-v35r2-check.json', 'files')]),
    'cost': ('measure_centre_v35r2_cost.py', [('centre-v35r2-first-root-check.json', 'source_hashes')]),
}


def main():
    label = sys.argv[1]
    script, prerequisites = GATES[label]
    fixture_gate()
    for name, hashes in prerequisites:
        passed(name, hashes)
    # A PASS JSON written before a later process failure is insufficient.
    for prior in list(GATES)[:list(GATES).index(label)]:
        receipt = json.loads((HERE/f'run-centre-v35r2-{prior}-once-exit.json').read_text())
        assert receipt['actual_exit'] == 0, prior
        assert receipt['log_sha256'] == digest(f'run-centre-v35r2-{prior}-once.log'), prior
        assert receipt['launch_sha256'] == digest(f'run-centre-v35r2-{prior}-once-launch.json'), prior
        previous_launch = json.loads((HERE/f'run-centre-v35r2-{prior}-once-launch.json').read_text())
        assert previous_launch['fixture_manifest'] == digest('centre-v35r2-fixture-integrity.json'), prior
    log = HERE/f'run-centre-v35r2-{label}-once.log'
    exit_path = HERE/f'run-centre-v35r2-{label}-once-exit.json'
    launch = HERE/f'run-centre-v35r2-{label}-once-launch.json'
    assert not any(p.exists() for p in [log, exit_path, launch]), 'Never replay'
    atomic_json(launch, {'started': True, 'script': script, 'script_sha256': digest(script),
                         'fixture_manifest': digest('centre-v35r2-fixture-integrity.json')})
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/ms-playwright',
               PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH='/home/clawd/pixelvision-venv/lib/python3.12/site-packages')
    with log.open('x') as stream:
        result = subprocess.run([sys.executable, '-u', str(HERE/script)], stdout=stream,
                                stderr=subprocess.STDOUT, env=env, cwd=HERE.parent)
        stream.flush(); os.fsync(stream.fileno())
    atomic_json(exit_path, {'actual_exit': result.returncode, 'script': script,
                            'log_sha256': digest(log.name), 'launch_sha256': digest(launch.name)})
    print(json.dumps({'gate': label, 'actual_exit': result.returncode, 'log': log.name}), flush=True)
    return result.returncode if result.returncode >= 0 else 128-result.returncode


if __name__ == '__main__':
    sys.exit(main())
