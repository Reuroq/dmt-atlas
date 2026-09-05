"""Regression checks for REDIRECT4's independent, fail-closed receipt gate."""
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from realism import evaluate

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


with TemporaryDirectory(dir=HERE, prefix='realism-check-') as temp:
    root = Path(temp)
    captures = []
    for index in range(2):
        # Synthetic receipt fixtures only: never included in the project review ledger.
        image = root / f'fixture-{index}.png'
        image.write_bytes(b'receipt fixture' + bytes([index]))
        receipt = {'file': image.name, 'capture_sha256': digest(image), 'render_signature': 'current', 'errors': [],
                   'veil_opacity': 0, 'capture_diagnostics': {'stage': 'chrysanthemum', 'detail': 'high', 'paused': True,
                   'transition': False, 'missingEvidence': [], 'uncitedMeshes': 0, 'position': [0, 1.7, 8],
                   'yaw': 0, 'pitch': 0, 'animTime': index * 4}}
        image.with_suffix('.json').write_text(json.dumps(receipt), encoding='utf-8')
        captures.append({'file': image.name, 'sha256': digest(image), 'receipt_sha256': digest(image.with_suffix('.json')), 'inspection': 'fixture'})
    base = {'targets': {'chrysanthemum': {'grade': 'RECOGNISE', 'reason': 'fixture', 'temporal_observation': 'fixture', 'captures': captures}}}

    def check(ledger, expected, signature='current', targets=('chrysanthemum',), beings=None):
        (root / 'realism-grades.json').write_text(json.dumps(ledger), encoding='utf-8')
        result = evaluate(root, targets, beings or {}, signature, digest)
        assert result['passed'] == expected, result

    check(base, True)
    check(base, False, signature='changed')
    check(base, False, targets=('chrysanthemum', 'garden'))
    for grade in ['GAME', 'CLOSE', 'PENDING', None]:
        ledger = copy.deepcopy(base)
        ledger['targets']['chrysanthemum']['grade'] = grade
        check(ledger, False)
    for field in ['reason', 'temporal_observation']:
        ledger = copy.deepcopy(base)
        del ledger['targets']['chrysanthemum'][field]
        check(ledger, False)
    ledger = copy.deepcopy(base)
    ledger['targets']['chrysanthemum']['captures'] = [captures[0], captures[0]]
    check(ledger, False)
    ledger = copy.deepcopy(base)
    ledger['targets']['chrysanthemum']['captures'][0]['inspection'] = ''
    check(ledger, False)
    receipt_path = root / 'fixture-1.json'
    original = receipt_path.read_text(encoding='utf-8')
    for field, value in [('detail', 'lower'), ('transition', True), ('paused', False), ('position', [1, 1.7, 8]), ('animTime', 1), ('uncitedMeshes', 1)]:
        receipt = json.loads(original)
        receipt['capture_diagnostics'][field] = value
        receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
        ledger = copy.deepcopy(base)
        ledger['targets']['chrysanthemum']['captures'][1]['receipt_sha256'] = digest(receipt_path)
        check(ledger, False)
    receipt_path.write_text(original, encoding='utf-8')
    (root / captures[0]['file']).write_bytes(b'tampered')
    check(base, False)
print('Realism gate: valid fixture passes; stale, missing, uninspected, changed, non-HIGH, non-temporal, uncited and non-RECOGNISE reviews fail.')
