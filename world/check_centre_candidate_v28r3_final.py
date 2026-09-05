"""Correct the historical latest.png baseline without rerunning numeric samples."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-candidate-v28r3-final-check.json'
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()

name = 'centre-candidate-v28r3-integrity.json'
previous = json.loads((HERE/name).read_text())
assert previous['numeric_passed'] and all(s['passed'] for s in previous['curvature_sampling'])
assert [n for n, ok in previous['protected_unchanged'].items() if not ok] == ['latest.png']
hashes = {n: digest(n)==sha for n, sha in previous['source_hashes'].items()}
assert all(hashes.values())
visual = json.loads((HERE/'diagnostic-centre-v27r2-integrity.json').read_text())
assert all(digest(n)==sha for n, sha in visual['evidence_hashes'].items())
assert digest('latest.png') == digest('diagnostic-centre-v27r2-entry.png')
old = json.loads((HERE/'diagnostic-centre-v27r2-receipts.json').read_text())
assert all(digest(n)==sha for n, sha in old['protected_after'].items() if n!='latest.png')
files = [name, Path(__file__).name, 'check-centre-candidate-v28r3.log',
    'check-centre-candidate-v28r3-r2.log', 'diagnostic-centre-v27r2-integrity.json',
    'diagnostic-centre-v27r2-entry.png', 'latest.png']
out = {'integrity_passed': True, 'numeric_passed': True, 'curvature_sampling_passed': True,
    'previous_report': name, 'previous_source_hashes_valid': hashes,
    'baseline_correction': 'The previous render receipts predate the prior phase latest.png update. The prior phase integrity receipt and isolated entry image establish the current display baseline. Only that mistaken comparison is corrected; no numerical or curvature checks repeated.',
    'preserved_checker_failures': ['Initial checker broadcasting error before receipt creation; script/log preserved.',
        'Completed checker failed solely on historical latest.png baseline; report/log preserved.'],
    'live_assets_ledgers_and_default_unchanged': True, 'latest_still_previous_labelled_diagnostic': True,
    'files': {n: digest(n) for n in files}, 'candidate_promoted': False,
    'visual_sequence_passed': False, 'overall_passed': False}
OUT.write_text(json.dumps(out, indent=2)+'\n')
print('PASS: numeric/curvature evidence verified; corrected display baseline; live unchanged.')
