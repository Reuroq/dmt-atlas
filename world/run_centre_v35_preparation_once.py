"""Exclusive foreground preparation stages, durable output and actual child exit."""
import os
import subprocess
import sys
import v35_preparation as p


def main():
    label = sys.argv[1]
    script = {'build': 'build_centre_v35.py', 'static': 'check_centre_v35_static.py',
              'close': 'close_centre_v35_preparation.py'}[label]
    stem = p.PREFIX + '-' + label + '-once'
    for suffix in ('-launch.json', '-exit.json', '.log'):
        assert not (p.HERE / (stem + suffix)).exists(), 'Never replay'
    if label == 'build':
        p.history()
    else:
        p.frozen(); p.receipt('build')
        if label == 'close':
            p.receipt('static')
    argv = [sys.executable, '-B', '-u', str(p.HERE / script)]
    p.save(stem + '-launch.json', {'argv': argv, 'script': script,
        'script_sha256': p.digest(script), 'launcher_sha256': p.digest(__file__),
        'history_sha256': p.digest(p.HISTORY),
        'freeze_sha256': p.digest(p.PREFIX + '-freeze.json') if label != 'build' else None})
    actual, error = None, None
    try:
        with (p.HERE / (stem + '.log')).open('x') as stream:
            try:
                actual = subprocess.run(argv, cwd=p.HERE.parent, stdout=stream,
                    stderr=subprocess.STDOUT, timeout=60,
                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')).returncode
            finally:
                stream.flush(); os.fsync(stream.fileno())
    except Exception as exc:
        error = repr(exc)
    manifest = p.PREFIX + '-fixture-integrity.json'
    p.save(stem + '-exit.json', {'actual_exit': actual, 'launcher_error': error,
        'log_sha256': p.digest(stem + '.log'), 'launch_sha256': p.digest(stem + '-launch.json'),
        'manifest_sha256': p.digest(manifest) if label == 'close' and (p.HERE / manifest).exists() else None})
    print(label, 'actual exit', actual, 'launcher error', error)
    return actual if actual is not None and actual >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
