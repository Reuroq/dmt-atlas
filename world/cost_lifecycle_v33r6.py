"""Durable, one-shot cost receipts. All I/O is outside measured boundaries."""
import hashlib
import json
import os
import signal
import time
from pathlib import Path


def atomic_json(path, data):
    path = Path(path)
    pending = path.with_suffix(path.suffix + '.pending')
    with pending.open('x') as stream:
        json.dump(data, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class CostSignal(BaseException):
    pass


def install_signal_receipts():
    def stop(signum, frame):
        raise CostSignal(f'signal {signal.Signals(signum).name}')
    old = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)}
    for s in old:
        signal.signal(s, stop)
    return old


def restore_signals(old):
    for s, handler in old.items():
        signal.signal(s, handler)


class Lifecycle:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir()  # Existing partial attempt is never overwritten.
        self.sequence = 0

    def record(self, event, **payload):
        path = self.directory / f'{self.sequence:03d}-{event}.json'
        assert not path.exists()
        atomic_json(path, {'sequence': self.sequence, 'event': event,
                           'monotonic': time.monotonic(), 'pid': os.getpid(), **payload})
        self.sequence += 1

    def arm(self, identity, callback, clock=time.monotonic):
        self.record('arm_started', identity=identity)
        try:
            start = clock()
            case = callback()
            case['outer_four_readbacks_seconds'] = clock() - start
        except BaseException as exc:
            self.record('arm_failed', identity=identity, failure=repr(exc))
            raise
        self.record('arm_completed', identity=identity, result=case)
        return case

    def hashes(self):
        return {str(p.relative_to(self.directory.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(self.directory.glob('*.json'))}
