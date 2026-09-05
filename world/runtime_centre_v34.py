"""One-shot v34 prerequisite checks and durable failure receipts."""
import hashlib
import json
from pathlib import Path
from cost_lifecycle_v34 import atomic_json, install_signal_receipts, restore_signals

HERE = Path(__file__).resolve().parent


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def verify(group):
    for name, want in group.items():
        assert digest(name) == want, name


def fixture_gate():
    gate = json.loads((HERE/'centre-v34-fixture-integrity.json').read_text())
    assert gate['static_passed'] and gate['fixtures_complete'] and not gate['numerical_run']
    for group in ['files', 'protected', 'display']:
        verify(gate[group])
    return gate


def passed(name, hashes='source_hashes', key='passed'):
    receipt = json.loads((HERE/name).read_text())
    assert receipt[key], name
    verify(receipt[hashes])
    return receipt


def one_shot(label, callback):
    start = HERE/f'centre-v34-{label}-started.json'
    failure = HERE/f'centre-v34-{label}-failure.json'
    assert not start.exists() and not failure.exists(), 'Preserve partial attempt; no replay'
    fixture_gate()
    atomic_json(start, {'started': True, 'fixture_manifest': digest('centre-v34-fixture-integrity.json')})
    signals = install_signal_receipts()
    try:
        return callback()
    except BaseException as exc:
        atomic_json(failure, {'passed': False, 'failure': repr(exc),
                             'action': 'Hold downstream gates; preserve run, never replay'})
        raise
    finally:
        restore_signals(signals)
