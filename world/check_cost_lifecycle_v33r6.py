"""Offline failure-injection contracts; no browser, shader or cost experiment."""
import json
import os
import signal
import tempfile
from pathlib import Path
from cost_lifecycle_v33r6 import Lifecycle, CostSignal, install_signal_receipts, restore_signals

HERE = Path(__file__).resolve().parent


def check():
    checks = []
    with tempfile.TemporaryDirectory(prefix='v33r6-lifecycle-check-', dir=HERE) as temp:
        directory = Path(temp)
        journal = Lifecycle(directory / 'success')
        phases = []
        original = journal.record
        def record(event, **payload):
            phases.append(event)
            original(event, **payload)
        journal.record = record
        def clock():
            phases.append('clock')
            return float(len(phases))
        def callback():
            phases.append('evaluate')
            return {'hits': [1, 2], 'gpu_three_readbacks_seconds': .1}
        result = journal.arm({'pair': 1, 'arm': 'parent'}, callback, clock)
        assert phases == ['arm_started', 'clock', 'evaluate', 'clock', 'arm_completed']
        assert result['outer_four_readbacks_seconds'] == 2
        saved = json.loads((journal.directory / '001-arm_completed.json').read_text())
        assert saved['result'] == result and len(journal.hashes()) == 2
        assert not list(journal.directory.glob('*.pending'))
        checks += ['I/O outside both clock calls', 'completed arm saved before next arm', 'durable result roundtrip']
        try:
            Lifecycle(journal.directory)
        except FileExistsError:
            checks.append('partial journal blocks replay')
        else:
            raise AssertionError('replay allowed')
        for label, failure in [('exception', RuntimeError('mock GLSL failure')),
                               ('interrupt', KeyboardInterrupt()), ('signal', CostSignal('mock SIGTERM'))]:
            failed = Lifecycle(directory / label)
            def fail():
                raise failure
            try:
                failed.arm({'arm': 'candidate'}, fail)
            except BaseException as exc:
                assert exc is failure
            else:
                raise AssertionError('failure swallowed')
            events = [json.loads(p.read_text()) for p in sorted(failed.directory.glob('*.json'))]
            assert [e['event'] for e in events] == ['arm_started', 'arm_failed']
            assert events[1]['failure'] == repr(failure)
            checks.append(label + ' saved and rethrown')
        old = install_signal_receipts()
        try:
            try:
                os.kill(os.getpid(), signal.SIGTERM)
            except CostSignal as exc:
                assert 'SIGTERM' in str(exc)
            else:
                raise AssertionError('signal not captured')
        finally:
            restore_signals(old)
        assert all(signal.getsignal(s) == handler for s, handler in old.items())
        checks.append('actual self-SIGTERM caught; handlers restored')
    return {'passed': True, 'checks': checks, 'browser_runs': 0,
            'limits': 'SIGKILL, process/container loss and filesystem failure cannot guarantee a terminal receipt; last durable started event remains incomplete, never a measured regression.'}


if __name__ == '__main__':
    print(json.dumps(check()))
