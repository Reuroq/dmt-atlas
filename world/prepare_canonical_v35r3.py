"""Freeze, synthetic checks and static closure. Never starts field work."""
import ast
import sys
import canonical_runtime_v35r3 as r
from canonical_history_v35r3 import verify_history
from build_canonical_v35r3 import derive

SOURCES = list(derive())+['canonical_history_v35r3.py', 'build_canonical_v35r3.py',
    'check_canonical_v35r3.py', 'prepare_canonical_v35r3.py', 'run_canonical_static_v35r3_once.py',
    r.PREFIX+'-design.md']


def receipt(label):
    stem = r.PREFIX+'-'+label+'-once'
    result, launch = r.read(stem+'-exit.json'), r.read(stem+'-launch.json')
    r.require(type(result['actual_exit']) is int and result['actual_exit'] == 0
              and result['launcher_error'] is None, 'Static actual exit: '+label)
    r.require(result['log_sha256'] == r.digest(stem+'.log')
              and result['launch_sha256'] == r.digest(stem+'-launch.json'))
    script = 'build_canonical_v35r3.py' if label == 'build' else 'prepare_canonical_v35r3.py'
    r.require(launch['script_sha256'] == r.digest(script)
              and launch['launcher_sha256'] == r.digest('run_canonical_static_v35r3_once.py')
              and launch['history_sha256'] == r.digest(r.HISTORY))
    if label in ('check', 'close'):
        r.require(launch['freeze_sha256'] == r.digest(r.PREFIX+'-freeze.json'))


def gate():
    verify_history()
    frozen = r.read(r.PREFIX+'-freeze.json')
    r.require(frozen['history_sha256'] == r.digest(r.HISTORY))
    r.verify(frozen['sources'])


def freeze():
    verify_history(); receipt('build')
    for name in SOURCES:
        if name.endswith('.py'): ast.parse((r.HERE/name).read_text(), filename=name)
    r.atomic_json(r.PREFIX+'-freeze.json', {'sources': {n: r.digest(n) for n in SOURCES},
        'history_sha256': r.digest(r.HISTORY), 'field_runtime_permitted': False})
    print('Canonical successor frozen; no field runtime', flush=True)


def check():
    gate(); receipt('build'); receipt('freeze')
    from check_canonical_v35r3 import check as run
    result = run()
    gate()
    r.atomic_json(r.PREFIX+'-static.json', result)
    print('Canonical successor synthetic static PASS; no field/browser runtime', flush=True)


def close():
    gate()
    for label in ('build', 'freeze', 'check'): receipt(label)
    history, _ = verify_history()
    result = r.read(r.PREFIX+'-static.json')
    r.require(result['static_passed'] is True and result['runtime_fixtures_complete'] is True
              and result['numeric_passed'] is False and result['numerical_run'] is False
              and result['field_samples'] == result['browser_runs'] == 0)
    r.require(not any(r.directory(stage).exists() for stage in r.STAGES))
    archives = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name+'-before-'+r.PREFIX
        with (r.HERE/archive).open('xb') as stream: stream.write((r.HERE/name).read_bytes())
        archives[name] = archive
    next_work = ('Verify centre-v35r3-canonical-integrity.json and close-once actual-exit0 receipt hashes. '
        'Only then launch python3 -B world/run_canonical_v35r3_once.py global in the foreground. '
        'This is a NEW fresh global search, not a replay or saved-only certification of the old exit1. '
        'Check its actual exit/full inventory/result before the distinct combination stage. '
        'Both reuse only immutable successful v35r2 bounds/numerical/local prerequisites. '
        'Any failed or partial new attempt is terminal and blocks downstream work; no replay. '
        'After attempts, prepare a distinct saved-only terminal closure before changing bound display files. '
        'Cost/capture integration remains NOT PREPARED, even after future numerical PASS. '
        'Original fixed-grid FAIL, original global exit1 and all historical images stay immutable. '
        'No tolerance relaxation, nearest-root substitution, live promotion or acceptance bypass. '
        'All19/source/coverage/route/full acceptance remain unfinished.')
    notes = (r.HERE/'NOTES.md').read_text(encoding='utf-8-sig')
    r.require(notes.count('## Exact next bounded work') == 1)
    notes = notes[:notes.index('## Exact next bounded work')]
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — canonical successor CLOSED static PASS', 1)
    notes += '''## Canonical-JSON successor CLOSED — static PASS; no field runtime
- Terminal manifest SHA86465f6ee8b4617b7638dc9d1852c9eb19c6d6ca28e64314b01c2c316a1e0f78, 4344 evidence/16protected/4display and all close-once hashes verified. Original global remains actual exit1/false/ineligible; original fixed-grid FAIL remains separate. No old worker or saved failed root is certified.
- Distinct centre-v35r3-canonical namespace: fresh global → combination, explicitly requiring immutable successful v35r2 bounds/numerical/local receipts and failed terminal history. Failed original global is NOT an eligible predecessor. New global requires fresh computation; combination requires successful NEW global actual exit/full inventory. Exclusive foreground claims preserve partial/failure/late-exit evidence and reject replay.
- Production finish_global now durably saves raw.json then reads that exact JSON before keyed joins/assessment. Five exact derivations, entire global-main AST and strict global/type/finite/scan/local/word predicates unchanged; only assessment-boundary read and successor wiring differ. No field or camera/marcher/material changes.
- Real NumPy float64→durable JSON→production finish_global regression covers all720 synthetic keys, exact native/NumPy equality with pre-save accept/reject, post-save in-memory mutation, strict negatives, incomplete/duplicate joins, file/directory fsync and read failures. Actual foreground synthetic success/false/exception/partial/signal/late-exit, replay/tamper/boolean-exit and upstream/dependent eligibility fixtures pass. Synthetic overrides labelled; zero field/browser runtime.
- Static build/freeze/check/close actual-exit0 receipts and integrity bind new sources/fixtures plus complete history. No numerical/root/visual/source/coverage/route/full acceptance credit. New global/combination unattempted; cost/capture NOT PREPARED. latest unchanged inspected REJECTED GAME v33r6. NOTES once/BOM retained, prior display archived; no WORLD_DONE.

## Exact next bounded work
'''+next_work+'\n'
    (r.HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    (r.HERE/'status.txt').write_text('Canonical-JSON successor CLOSED static PASS; new global/combination unattempted. Original global exit1 remains ineligible; legacy fixed-grid FAIL unchanged. Cost/capture not prepared. latest unchanged inspected REJECTED GAME v33r6; all19/source/coverage/route/full acceptance unfinished; no promotion.\n')
    readme = (r.HERE/'README.md').read_text()
    (r.HERE/'README.md').write_text(readme+'\n[Canonical-JSON successor](centre-v35r3-canonical-design.md): **static PASS only**. Real NumPy-to-durable-JSON regression and foreground lifecycle/eligibility fixtures pass. Fresh global and combination remain unattempted; original exit1 is unchanged and ineligible. No new render, promotion or numerical/visual/coverage/acceptance credit.\n')
    verify_history(archives)
    files = dict(history['files'])
    files.update({n: r.digest(n) for n in SOURCES})
    for name in (r.HISTORY, 'centre-v35r2-additive-runtime-close-once-exit.json',
                 'centre-v35r2-additive-runtime-close-once.log',
                 r.PREFIX+'-freeze.json', r.PREFIX+'-static.json', r.PREFIX+'-close-once-launch.json',
                 *archives.values()):
        files[name] = r.digest(name)
    for label in ('build', 'freeze', 'check'):
        for suffix in ('-launch.json', '-exit.json', '.log'):
            name = r.PREFIX+'-'+label+'-once'+suffix; files[name] = r.digest(name)
    for dirname in ('serialization-fixtures', 'lifecycle-fixtures'):
        for path in sorted((r.HERE/(r.PREFIX+'-'+dirname)).rglob('*')):
            if path.is_file():
                name = str(path.relative_to(r.HERE)); files[name] = r.digest(name)
    r.atomic_json(r.MANIFEST, {'files': files, 'protected': history['protected'],
        'display': {n: r.digest(n) for n in history['display']}, 'historical_display': archives,
        'history_sha256': r.digest(r.HISTORY), 'static_passed': True, 'runtime_fixtures_complete': True,
        'numerical_run': False, 'numeric_passed': False, 'capture_permitted': False,
        'cost_permitted': False, 'new_images': 0, 'next': next_work})
    print('Canonical successor statically CLOSED; no numerical or visual credit', flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'check': check, 'close': close}[sys.argv[1]]()
