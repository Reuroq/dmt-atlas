"""Saved-only closure of failed frozen static check; never runs Node or Chromium."""
import probe_centre_v34_staged_arithmetic as p


def main():
    output = p.PREFIX + '-preparation-failure-integrity.json'
    assert not (p.HERE / output).exists(), 'Never replay failure closure'
    p.gate(prepared=False)
    history = p.read(p.HISTORY)
    stem = p.PREFIX + '-static-once'
    r, launch = p.read(stem + '-exit.json'), p.read(stem + '-launch.json')
    assert r['actual_exit'] == 1 and r['launcher_error'] is None
    assert r['log_sha256'] == p.digest(stem + '.log')
    assert r['launch_sha256'] == p.digest(stem + '-launch.json')
    assert launch['script_sha256'] == p.digest(launch['script'])
    assert launch['launcher_sha256'] == p.digest('run_centre_v34_staged_arithmetic_once.py')
    assert launch['freeze_sha256'] == p.digest(p.PREFIX + '-freeze.json')
    log = (p.HERE / (stem + '.log')).read_text()
    assert 'line 101, in main' in log and 'subprocess.CalledProcessError:' in log
    assert "returned non-zero exit status 1" in log
    assert not (p.HERE / (p.PREFIX + '-static.json')).exists()
    assert not (p.HERE / (p.PREFIX + '-preparation-integrity.json')).exists()
    assert not (p.HERE / (p.PREFIX + '-runtime-once-launch.json')).exists()
    assert not any(p.HERE.glob(p.PREFIX + '-event-*'))
    review = '''# Staged arithmetic preparation CLOSED — static FAIL; runtime NOT RUN

The distinct sources were frozen against the verified GL-localization runtime
closure. The foreground static launcher ran ONCE: actual exit1, no launcher
exception. Sources, launch/log/exit, and started/freeze receipts are preserved.
Do not edit or retry this frozen attempt. The passing preparation closure did
not run; no passing static or preparation manifest exists.

## Saved evidence and limits

The traceback reaches checker line101, the Node VM mock-check subprocess.
Earlier hash gates, Python AST, original shader-function byte identity,
translated-query absence assertions, and standalone HTML-JS syntax check returned
without an exception. The Node mock command then returned1. Its full command is
in the log, but `capture_output=True` combined with the uncaught CalledProcessError
failed to persist its stdout/stderr. The saved traceback does NOT identify which
Node mock failed or its internal error. Do not invent a cause or claim these
checks passed. The Python plan/independent-rational arithmetic/assessment/support/
launcher-replay checks after this subprocess were NOT reached.

The sources propose 126 stages: known-float first, both leaves/literal+uniform,
shared frozen texture/target, durable before-assessment Three/raw values/bits,
operation-local errors, exact both-leaf criterion and no translated-source queries.
These remain unvalidated implementation, NOT a runnable prepared diagnostic.
The original input texture/seeds and shader construction are unchanged.

## Next bounded preparation

Verify this failure-integrity manifest and its bound static exit1 receipt.
Prepare a separately named revision; do not alter this freeze or rerun this checker.
First fix diagnostic observability in that revision: durably save Node command
hash/source and full stdout/stderr/actual exit BEFORE classifying nonzero status;
avoid throwing away captured output or logging a giant argv traceback alone.
Use separately staged mock checks to identify the failed mock precisely. Preserve
the same arithmetic shader/input provenance and full static requirements. New
source paths/protocol/one-shot receipts are required. Freeze/static only in that
phase; no arithmetic GPU runtime until a new preparation actually passes.

No Chromium/GLSL/GPU arithmetic, field, roots, cost, image or acceptance ran.
No uniform support or v35 candidate. Original exact-jet and716/720 reference
failures persist. latest remains the once-inspected REJECTED GAME v33r6 entry;
live/default/ledger bytes unchanged. All19 realism/source/coverage/route/full
acceptance remain unfinished. The closed GL-localization result is unchanged.
'''
    review_name = p.PREFIX + '-preparation-failure-review.md'
    with (p.HERE / review_name).open('x') as f: f.write(review)
    old_title = '# Active: REDIRECT4 — GL localization CLOSED; exact controls, translated-query GL1282'
    notes_bytes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes_bytes.startswith(b'\xef\xbb\xbf')
    notes = notes_bytes.decode('utf-8-sig'); assert notes.startswith(old_title)
    marker = '## Exact next bounded work\n'; assert notes.count(marker) == 1
    section = '''## Distinct staged arithmetic preparation CLOSED — static FAIL, runtime NOT RUN
- Frozen10 NEW/source/input files against verified GL-localization closure. Proposed126stages:known-float first,both leaves/literal+uniform,shared frozen original texture/target,durable full Three/raw values/bits before validation,staged GL errors,no translated-source queries. Original shader construction byte-identical. Implementation NOT statically validated;no preparation pass.
- Frozen foreground static ONCE actual exit1/no launcher exception. Python AST/source-identity/absence assertions and standalone JS syntax returned;Node VM mock subprocess failed at checker line101. Full command/traceback retained,but capture_output=True discarded stdout/stderr on uncaught CalledProcessError. Specific failed mock/cause NOT established. Python plan/rational-oracle/assessment/support/replay checks NOT reached. Never edit/retry this attempt.
- Failure integrity binds frozen/history/receipts/protected/current display;prior display archived,NOTES once/BOM retained. No static.json or passing preparation manifest;runtime blocked. No browser/GLSL/GPU/field/roots/cost/capture/acceptance/support/v35. latest unchanged inspected REJECTED GAME v33r6;all19 unfinished.

'''
    next_work = ('Verify centre-v34-staged-arithmetic-preparation-failure-integrity.json files/protected/display '
                 'and the bound static actual-exit1 receipt. Prepare a separately named revision per '
                 'centre-v34-staged-arithmetic-preparation-failure-review.md: durable Node source/hash/stdout/stderr/'
                 'actual-exit BEFORE assessment,staged mocks to localize failure;retain exact inputs/shader/both-leaf '
                 'criterion and all static requirements. Freeze/static only;no runtime until new preparation PASS. '
                 'Never edit/retry frozen diagnostics or call superseded display gates. All19/source/coverage/'
                 'route/full acceptance unfinished;no WORLD_DONE.\n')
    new_notes = notes.split(marker)[0].replace(old_title,
        '# Active: REDIRECT4 — staged arithmetic preparation CLOSED static FAIL; runtime NOT RUN', 1)
    new_notes += section + marker + next_work
    readme = (p.HERE / 'README.md').read_text()
    matching = [s for s in readme.splitlines() if s.startswith('Distinct [GL-localization runtime]')]
    assert len(matching) == 1
    assert 'GL localization runtime CLOSED' in (p.HERE / 'status.txt').read_text()
    replacement = ('Distinct [staged arithmetic preparation](centre-v34-staged-arithmetic-preparation-failure-review.md) '
                   'is **CLOSED static FAIL; runtime NOT RUN**. Frozen checker actual exit1 in Node mocks;captured '
                   'stderr was not persisted,so the specific failure is unresolved. No passing preparation or '
                   'arithmetic support. Next:separately named revision with durable static error evidence. '
                   'GL-localization findings and original numerical/realism failures retained.')
    status = ('Isolated v34 numerical FAIL retained. NEW staged arithmetic preparation CLOSED static FAIL '
              'actual exit1 in Node mocks;stderr not persisted,specific mock/cause unresolved. Frozen attempt '
              'immutable;runtime NOT RUN/blocked. Next:separately named preparation with durable Node evidence '
              'and staged mocks. No support/v35/roots/cost/capture/acceptance. latest unchanged inspected '
              'REJECTED GAME v33r6;live/defaults/ledgers unchanged;all19 unfinished.\n')
    archives = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name + '-before-' + p.PREFIX + '-failed-preparation'
        assert not (p.HERE / archive).exists(); archives[archive] = p.digest(name)
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        with (p.HERE / (name + '-before-' + p.PREFIX + '-failed-preparation')).open('xb') as f:
            f.write((p.HERE / name).read_bytes())
    (p.HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + new_notes.encode('utf-8'))
    (p.HERE / 'README.md').write_text(readme.replace(matching[0], replacement, 1))
    (p.HERE / 'status.txt').write_text(status)
    files = dict(history['files']); files[p.HISTORY] = p.digest(p.HISTORY)
    files.update(p.read(p.PREFIX + '-freeze.json')['sources'])
    for suffix in ('-freeze.json','-static-started.json','-static-once-launch.json','-static-once-exit.json',
                   '-static-once.log','-preparation-failure-review.md','-failure-close-once-launch.json'):
        files[p.PREFIX+suffix] = p.digest(p.PREFIX+suffix)
    files['close_centre_v34_staged_arithmetic_preparation_failure.py'] = p.digest('close_centre_v34_staged_arithmetic_preparation_failure.py')
    files.update(archives); p.verify(files); p.verify(history['protected'])
    assert p.digest('latest.png') == history['display']['latest.png']
    display = {n:p.digest(n) for n in history['display']}
    p.save(output, {'phase':'staged arithmetic preparation CLOSED static FAIL', 'files':files,
                   'protected':history['protected'],'display':display,'archived_display':archives,
                   'prior_display':history['display'],'static_passed':False,'static_actual_exit':1,
                   'runtime_run':False,'numeric_passed':False,'synthetic_uniform_candidate_supported':False,
                   'capture_permitted':False,'new_images':0})
    p.verify(p.read(output)['files']); p.verify(display)
    print('Failure closure verified:',len(files),'evidence hashes;static exit1 retained;runtime NOT RUN',flush=True)


if __name__=='__main__': main()
