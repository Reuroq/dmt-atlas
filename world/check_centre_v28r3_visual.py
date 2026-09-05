"""One-shot saved-evidence verification and dashboard copy; no render/probe runs."""
import hashlib
import json
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v28r3'
OUT = HERE / (PREFIX+'-integrity.json')
assert not OUT.exists(), 'Preserve one-shot verification'

def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

summary = json.loads((HERE/(PREFIX+'-receipts.json')).read_text())
assert summary['passed'] and summary['protected_unchanged'] and not summary['errors']
assert summary['protected_before'] == summary['protected_after']
assert all(digest(n) == h for n, h in summary['protected_after'].items())
assert all(digest(n) == h for n, h in summary['source_hashes'].items())
receipts = summary['receipts']
assert len(receipts) == 4
labels = ['entry', 'entry-motion', 'deep', 'deep-motion']
for receipt, label in zip(receipts, labels):
    name = PREFIX+'-'+label+'.png'
    assert receipt['file'] == name and digest(name) == receipt['capture_sha256']
    assert json.loads((HERE/name).with_suffix('.json').read_text()) == receipt
    header = (HERE/name).read_bytes()[:24]
    assert header[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', header[16:24]) == (1200, 800)
    assert receipt['resolution'] == [1200, 800]
    assert receipt['source_hashes'] == summary['source_hashes']
    assert not receipt['errors'] and receipt['veil_opacity'] == 0
    assert 0 <= receipt['settle_seconds'] < 90
    d = receipt['capture_diagnostics']
    assert d['stage'] == 'chrysanthemum' and d['paused'] and d['detail'] == 'high'
    assert not d['renderPending'] and d['renderedAnimTime'] == d['animTime']
    assert not d['transition'] and not d['missingEvidence'] and d['uncitedMeshes'] == 0
for a, b in [(receipts[0], receipts[1]), (receipts[2], receipts[3])]:
    x, y = a['capture_diagnostics'], b['capture_diagnostics']
    assert all(x[k] == y[k] for k in ['position', 'yaw', 'pitch', 'stage', 'detail'])
    assert y['animTime'] - x['animTime'] >= 3
assert receipts[0]['capture_diagnostics']['position'] == [0, 1.7, 8]
assert receipts[2]['capture_diagnostics']['position'][2] <= -6

# All saved capture/source/protected checks precede the authorised display copy.
old_latest = digest('latest.png')
new_latest = receipts[-1]['file']
shutil.copyfile(HERE/new_latest, HERE/'latest.png')
assert digest('latest.png') == receipts[-1]['capture_sha256']
assert all(digest(n) == h for n, h in summary['protected_after'].items() if n != 'latest.png')
files = list(summary['source_hashes']) + [
    PREFIX+'-receipts.json', PREFIX+'-review.md', 'render-centre-v28r3.log',
    'centre-candidate-v28r3-final-check.json', Path(__file__).name,
    'NOTES.md', 'README.md', 'status.txt', 'latest.png']
for r in receipts:
    files += [r['file'], str(Path(r['file']).with_suffix('.json'))]
result = {
    'integrity_passed': True, 'visual_capture_sequence_passed': True,
    'visual_grade_entry': 'GAME', 'visual_grade_deep': 'GAME',
    'candidate_promoted': False, 'overall_passed': False,
    'live_assets_ledgers_sources_and_default_unchanged': True,
    'latest_display_only': {'previous_sha256': old_latest, 'copied_from': new_latest,
                           'current_sha256': digest('latest.png')},
    'limits': 'Saved evidence verification only; no repeated renders or numerical samples. Sequence completion is not realism, smooth-motion, hardware performance or original 45-second exit acceptance.',
    'files': {n: digest(n) for n in dict.fromkeys(files)},
}
OUT.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: v for k, v in result.items() if k != 'files'}))
