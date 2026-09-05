"""Close the new saved-only investigation; preserve all v34 evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(name):
    with (HERE / name).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    archive = 'NOTES-before-centre-v34-saved-investigation.md'
    output = 'centre-v34-saved-investigation-integrity.json'
    assert not (HERE / archive).exists() and not (HERE / output).exists()
    old = json.loads((HERE / 'centre-v34-numerical-failure-integrity.json').read_text())
    for group in ['files', 'protected', 'display']:
        for name, expected in old[group].items():
            assert digest(name) == expected, name
    receipt = json.loads((HERE / 'investigate-centre-v34-saved-once-exit.json').read_text())
    assert receipt['actual_exit'] == 0
    assert digest('investigate-centre-v34-saved-once.log') == receipt['log_sha256']
    assert digest('investigate-centre-v34-saved-once-launch.json') == receipt['launch_sha256']
    analysis = json.loads((HERE / 'centre-v34-saved-investigation.json').read_text())
    assert analysis['script_sha256'] == digest('investigate_centre_v34_saved.py')
    assert not analysis['numeric_passed'] and not analysis['capture_permitted']
    for leaf in ['childAxial', 'childAngular']:
        assert analysis['arithmetic'][leaf]['restricted_constant_folding_models']['sum_of_binary32_constants']['strictly_overlapping_all'] == 75996
    assert all(r['counts_cheap_full_skips_refinements'][3] == 0 for r in analysis['missing_references'])
    original = (HERE / 'NOTES.md').read_bytes()
    assert original.startswith(b'\xef\xbb\xbf')
    notes = original.decode('utf-8-sig')
    assert notes.startswith('# Active: REDIRECT4 — v34 numerical CLOSED FAIL; downstream blocked')
    marker = '## Exact next bounded work\n'
    assert notes.count(marker) == 1
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v34 saved investigation CLOSED; two new diagnostics designed', 1)
    notes = notes.split(marker)[0] + '''## v34 saved-only investigation CLOSED — numerical FAIL retained
- investigate_centre_v34_saved.py ONCE actual exit0;verified340historical/16protected/4display hashes. Zero field/browser/root/cost/capture/acceptance runs. Both mismatching leaves differ only in w;all xyz exact. Binary32-constant-folding inverse rounding cells strictly overlap for every75996pair/leaf;compatibility only,not compiler diagnosis. Decimal-sum-.42 model refuted for26124axial pairs. Equality unchanged.
- All4missing-reference hits have0refinement calls:local residual/directional acceptance,not bisection. Active saved leaves parentF839,childPositive745,childAxial807/809. Other nearby negative constraints do not prove a thin crossing. CPU reconstructed-vs-saved GPU points differ by up to5.154e-6;not causal evidence. No termination-time samples/GPU rays/scan values saved. Causes remain unresolved.
- centre-v34-saved-investigation.json/review.md and centre-v34-followup-experiment-design.md specify separate NEW diagnostics:synthetic constant-vs-uniform second-offset GPU microprobe;4ray CPU local ±.004/.00005 full/11leaf profiles with explicit brackets. Neither is full numerical acceptance or independent first-root gate. Prepare frozen inputs/one-shot runners/static checks next;NO runtime yet,NO v35 candidate yet. Uniform variant is falsifiable,not presumed fix;root profile cannot certify earliest root.
- New integrity binds historical failure evidence and new analysis/design/receipts;capture remains blocked. README/status current;latest unchanged inspected REJECTED GAME v33r6 entry. Live/defaults/ledgers unchanged. NOTES once,BOM retained,prior bytes archived.

## Exact next bounded work
Implement the two distinct bounded experiments in centre-v34-followup-experiment-design.md, freeze inputs and prepare one-shot foreground runners/static checks before runtime. Preserve every v34 artifact and failed original gate;no v34 replay/dependent roots/cost/capture. Only a supported microprobe result justifies a new isolated uniform-offset candidate;local root profiles cannot replace first-root evidence. All19/source/coverage/route/full acceptance unfinished;no WORLD_DONE.
'''
    status = 'Isolated v34 remains numerical FAIL; saved-only investigation CLOSED: scalar-only expanded-jet differences compatible with binary32 constant folding, not diagnosed. All4missing-reference hits accepted locally without bisection;root causes unresolved. New separate uniform-offset microprobe and4ray local-profile diagnostics DESIGNED,not run;no v35 candidate. Original gates/evidence preserved;no v34 replay or dependent roots/cost/capture. latest.png unchanged inspected REJECTED GAME v33r6 entry. Live/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n'
    readme = (HERE / 'README.md').read_text()
    lines = readme.splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith('Isolated **v34 numerical phase CLOSED — FAIL**.')]
    assert len(matches) == 1
    assert (HERE / 'status.txt').read_text().startswith('Isolated v34 numerical CLOSED FAIL:')
    lines[matches[0]] += ' New [saved-only investigation](centre-v34-saved-investigation-review.md): differences are scalar-only and compatible with binary32 constant folding, not attributed; all four unresolved hits used local acceptance without bisection. [Two distinct follow-up experiments](centre-v34-followup-experiment-design.md) are designed, not run. No new candidate or passing gate.'
    new_files = ['investigate_centre_v34_saved.py', 'centre-v34-saved-investigation.json',
                 'centre-v34-saved-investigation-review.md', 'centre-v34-followup-experiment-design.md',
                 'investigate-centre-v34-saved-once-launch.json', 'investigate-centre-v34-saved-once.log',
                 'investigate-centre-v34-saved-once-exit.json', 'close_centre_v34_saved_investigation.py']
    new_hashes = {name: digest(name) for name in new_files}
    with (HERE / archive).open('xb') as stream:
        stream.write(original)
    (HERE / 'README.md').write_text('\n'.join(lines) + '\n')
    (HERE / 'status.txt').write_text(status)
    (HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
    result = {'integrity_passed': True, 'numeric_passed': False, 'capture_permitted': False,
              'phase': 'Saved-only investigation CLOSED; new experiments designed, not run',
              'historical_failure_manifest': digest('centre-v34-numerical-failure-integrity.json'),
              'files': {**old['files'], **new_hashes, archive: digest(archive)},
              'protected': old['protected'], 'historical_display': old['display'],
              'display': {name: digest(name) for name in old['display']},
              'new_field_samples': 0, 'new_browser_runs': 0, 'new_images': 0}
    assert result['display']['latest.png'] == old['display']['latest.png']
    for group in ['files', 'protected', 'display']:
        for name, expected in result[group].items():
            assert digest(name) == expected, name
    with (HERE / output).open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('Saved-only investigation closure PASS; numerical FAIL unchanged; no runtime.')


if __name__ == '__main__':
    main()
