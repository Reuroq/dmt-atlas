"""New launcher amendment: a PASS receipt cannot bypass a failed actual exit."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import run_centre_v34_gate_once as launcher
from cost_lifecycle_v34 import atomic_json

HERE = Path(__file__).resolve().parent


def check():
    old = launcher.HERE, launcher.GATES, launcher.fixture_gate, launcher.passed, launcher.digest, sys.argv
    checks = []
    try:
        with tempfile.TemporaryDirectory(prefix='v34-exit-contract-', dir=HERE) as directory:
            target = Path(directory)
            launcher.HERE = target
            launcher.GATES = {'prior': ('fake.py', []), 'next': ('fake.py', [('passed.json','source_hashes')])}
            launcher.fixture_gate = launcher.passed = lambda *args: {'passed':True}
            launcher.digest = lambda name: hashlib.sha256((target/name).read_bytes()).hexdigest()
            sys.argv = ['launcher','next']
            (target/'centre-v34-fixture-integrity.json').write_text('{}\n')
            (target/'fake.py').write_text("print('synthetic successful child')\n")
            def blocked():
                try:
                    launcher.main()
                except (AssertionError,FileNotFoundError):
                    pass
                else:
                    raise AssertionError('bad actual exit accepted')
                assert not list(target.glob('run-centre-v34-next-*'))
            blocked(); checks.append('missing actual exit blocks despite PASS')
            log = target/'run-centre-v34-prior-once.log';log.write_text('synthetic prior\n')
            launch = target/'run-centre-v34-prior-once-launch.json'
            launch.write_text(json.dumps({'fixture_manifest':launcher.digest('centre-v34-fixture-integrity.json')}))
            exit_file = target/'run-centre-v34-prior-once-exit.json'
            receipt = {'actual_exit':7,'log_sha256':launcher.digest(log.name),'launch_sha256':launcher.digest(launch.name)}
            exit_file.write_text(json.dumps(receipt));blocked();checks.append('nonzero actual exit blocks despite PASS')
            receipt.update(actual_exit=0,log_sha256='bad')
            exit_file.write_text(json.dumps(receipt));blocked();checks.append('changed prior log blocks')
            receipt['log_sha256']=launcher.digest(log.name)
            exit_file.write_text(json.dumps(receipt))
            assert launcher.main()==0
            assert json.loads((target/'run-centre-v34-next-once-exit.json').read_text())['actual_exit']==0
            checks.append('verified prior zero exit permits one foreground child')
    finally:
        launcher.HERE,launcher.GATES,launcher.fixture_gate,launcher.passed,launcher.digest,sys.argv = old
    return {'passed':True,'checks':checks,'browser_runs':0,'v34_field_samples':0,
            'source_hashes':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
                [Path(__file__).name,'run_centre_v34_gate_once.py','cost_lifecycle_v34.py','runtime_centre_v34.py']}}


if __name__ == '__main__':
    destination=HERE/'centre-v34-launcher-exit-check.json'
    assert not destination.exists()
    result=check();atomic_json(destination,result)
    print(json.dumps(result))
