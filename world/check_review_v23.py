"""One-shot checks of v23 review evidence; no automatic visual grading."""
import json
import subprocess
from pathlib import Path
from fidelity import digest, render_signature

HERE = Path(__file__).resolve().parent
OUT = HERE / 'redirect4-v23-check.json'
assert not OUT.exists(), 'Preserve prior checks'

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def run(args, log):
    result = subprocess.run(args, cwd=HERE.parent, capture_output=True, text=True)
    (HERE / log).write_text(result.stdout + result.stderr)
    return result.returncode

assert digest(HERE / 'continuum.js') == '5486919206afcc282f4428a3cb344f8123714b2392b6802bac79631860269ca3'
assert (HERE / 'continuum.js').read_bytes() == (HERE / 'continuum-v23.js').read_bytes()
assert run(['node', '--check', 'world/continuum.js'], 'syntax-v23.log') == 0
assert run(['python3', 'world/check_realism.py'], 'realism-gate-v23.log') == 0
# fidelity.py --check already ran once after the review, returning 1.
# Inspect its generated result and retained log without regenerating unchanged data.
gate_exit = 1
assert 'overall: False' in (HERE / 'fidelity-v23-review.log').read_text()
images, receipts = set(), set()

def verify(value):
    if isinstance(value, dict):
        if value.get('file', '').endswith('.png') and value.get('sha256'):
            p = HERE / value['file']
            assert digest(p) == value['sha256'], p
            images.add(p.name)
            if value.get('receipt_sha256'):
                assert digest(p.with_suffix('.json')) == value['receipt_sha256'], p
                receipts.add(p.with_suffix('.json').name)
        for child in value.values():
            verify(child)
    elif isinstance(value, list):
        for child in value:
            verify(child)

for name in ['realism-grades.json', 'fidelity-grades.json']:
    verify(read(name))
bundle = read('fidelity-results.json')
assert bundle['render_signature'] == render_signature() and not bundle['passed']
target = next(t for t in bundle['targets'] if t['id'] == 'chrysanthemum')
access = read('accessibility-v23-initial-failure.json')
assert not access['passed']
assert digest(HERE / access['log']) == access['log_sha256']
diagnostic = read('diagnostic-stillness-v23-review.json')
verify(diagnostic)
physical = read('verification-continuum-v23.json')
assert physical['render_signature'] == render_signature()
assert physical['exit_walk_timeout_ms'] == 45000
assert (HERE / 'latest.png').read_bytes() == (HERE / 'realism-chrysanthemum-close-v23-motion.png').read_bytes()
for suffix in ['png', 'json']:
    assert (HERE / ('visual-chrysanthemum.' + suffix)).read_bytes() == (HERE / ('realism-chrysanthemum-close-v23.' + suffix)).read_bytes()
out = {'iteration': 'rough-jewel-corolla-v23', 'render_signature': render_signature(),
       'runtime_sha256': digest(HERE / 'continuum.js'),
       'realism': read('realism-grades.json')['targets']['chrysanthemum']['grade'],
       'coverage': target['coverage'], 'coverage_passed': target['passed'],
       'coverage_blockers': target['blockers'], 'source_audit': target['passage_audit'],
       'node_syntax': 'PASS', 'realism_gate_regression': 'PASS', 'fidelity_check_exit': gate_exit,
       'verified_ledger_pngs': len(images), 'verified_ledger_receipts': len(receipts),
       'accessibility': access, 'stillness_diagnostic': diagnostic, 'physical_exit': physical,
       'latest': 'realism-chrysanthemum-close-v23-motion.png',
       'display_receipt': 'realism-chrysanthemum-close-v23.json',
       'full_acceptance': 'PENDING; no unchanged desktop rerun', 'overall_passed': bundle['passed'],
       'artifacts': {name: digest(HERE / name) for name in [
           'review_chrysanthemum_v23.py', 'verify_continuum_v23.py', 'fidelity-v23-review.log',
           'accessibility-v23-initial-failure.json', 'diagnostic-stillness-v23-review.json',
           'render_stillness_v23.py', 'diagnostic-stillness-v23.log', 'verification-continuum-v23.json',
           'verification-continuum-v23.log', 'continuum-v23-implementation-check.json']}}
OUT.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: out[k] for k in ['realism', 'coverage', 'coverage_passed', 'verified_ledger_pngs', 'verified_ledger_receipts', 'overall_passed']}))
