"""Saved-only pass/failure closure for r2, with one display update. No Node/GPU."""
import os
import probe_centre_v34_staged_arithmetic_r2 as p


def main():
    p.gate(prepared=False)
    stem = p.PREFIX + '-static-once'
    receipt, launch = p.read(stem + '-exit.json'), p.read(stem + '-launch.json')
    assert receipt['launcher_error'] is None and type(receipt['actual_exit']) is int
    assert receipt['log_sha256'] == p.digest(stem + '.log')
    assert receipt['launch_sha256'] == p.digest(stem + '-launch.json')
    assert launch['script_sha256'] == p.digest(launch['script'])
    assert launch['launcher_sha256'] == p.digest('run_centre_v34_staged_arithmetic_r2_once.py')
    assert launch['freeze_sha256'] == p.digest(p.PREFIX + '-freeze.json')
    assert p.read(p.PREFIX + '-close-once-launch.json')['child_pid_parent'] == os.getppid()
    assert not any(p.HERE.glob(p.PREFIX + '-event-*'))
    assert not (p.HERE / (p.PREFIX + '-runtime-once-launch.json')).exists()
    passed = receipt['actual_exit'] == 0
    if passed:
        p.receipt('static')
        check = p.read(p.PREFIX + '-static.json')
        assert check['passed'] and not check['runtime_run'] and check['integer_oracle_components'] == 1024
    else:
        assert not (p.HERE / (p.PREFIX + '-static.json')).exists()
    history = p.read(p.HISTORY)
    p.save(p.PREFIX + '-close-started.json', {'static_actual_exit': receipt['actual_exit'], 'static_passed': passed})
    # Verify durable Node receipts and command/source identities, including expected failure.
    import hashlib
    import json
    node_results = []
    for name in sorted(p.HERE.glob(p.PREFIX + '-node-*-exit.json')):
        r = p.read(name.name); ns = name.name[:-len('-exit.json')]
        l = p.read(ns + '-launch.json')
        assert l['command_sha256'] == hashlib.sha256(json.dumps(l['command'], separators=(',', ':')).encode()).hexdigest()
        assert r['launch_sha256'] == p.digest(ns + '-launch.json')
        assert r['source_sha256'] == l['source_sha256'] == p.digest(l['source'])
        assert r['stdout_sha256'] == p.digest(ns + '-stdout.log')
        assert r['stderr_sha256'] == p.digest(ns + '-stderr.log')
        node_results.append({'stage': ns[len(p.PREFIX + '-node-'):], 'actual_exit': r['actual_exit'],
                             'timed_out': r['timed_out'], 'launcher_error': r['launcher_error']})
    if passed:
        assert len(node_results) == 13
        assert all(r['actual_exit'] == (1 if r['stage'] == 'original-reproduction' else 0)
                   and not r['timed_out'] and r['launcher_error'] is None for r in node_results)
    grade = 'PASS' if passed else 'FAIL'
    manifest = p.PREFIX + ('-preparation-integrity.json' if passed else '-preparation-failure-integrity.json')
    assert not (p.HERE / manifest).exists()
    next_work = ("Verify centre-v34-staged-arithmetic-r2-preparation-integrity.json files/protected/display and "
                 "static/close actual-exit0 receipts with the r2 probe helpers. In a separate bounded phase run ONLY "
                 "python3 -B world/run_centre_v34_staged_arithmetic_r2_once.py runtime ONCE; review saved evidence "
                 "before inference. No field/roots/cost/capture/acceptance/v35 without subsequent justified gates."
                 if passed else
                 "Verify centre-v34-staged-arithmetic-r2-preparation-failure-integrity.json files/protected/display "
                 "and bound static/close receipts. Read saved failed stage stderr/log; prepare a separately named "
                 "revision without editing/retrying r2. Runtime blocked until genuinely passing preparation.")
    detail = ("Original-source reproduction actual exit1 saved before classification: TypeError at missing "
              "window.arithmeticStep. This is new reproduction evidence, NOT recovered historical stderr. "
              "Inserted only the prior localization wrapper renamed; original shader/inputs and Python "
              "arithmetic/assessment/support/runtime-loop AST unchanged."
              if passed else
              "Frozen static failed; inspect the bound static log and per-stage durable stdout/stderr/exit "
              "receipts. Do not infer unreached checks or support. Sources remain immutable.")
    checks = ("All static requirements PASS: AST/JS, insertion-only HTML, exact shader/inputs, 126-stage "
              "ordering, ten independent API/GL/packing/shader/material/readback mocks, original combined "
              "mock, 1024 independent rational-oracle components, signed-zero/nonfinite/sentinel/bit handling, "
              "result-before-assessment, mismatch continuation/fatal stop/transport, exact both-leaf support "
              "criterion, exit7/replay/exclusive-receipt launcher mocks. Mock checks are not GPU correctness."
              if passed else "No passing static or preparation manifest; runtime NOT RUN/blocked.")
    review = (f'# Staged arithmetic r2 preparation CLOSED — static {grade}; runtime NOT RUN\n\n'
              f'Frozen foreground checker actual exit {receipt["actual_exit"]}; no launcher error.\n\n'
              f'{detail}\n\n{checks}\n\n'
              'Every Node stage has exclusive fsynced source/command-hash/stdout/stderr/actual-exit evidence '
              'before classification. Original failed attempt and history remain immutable.\n\n'
              '## Next bounded phase\n\n' + next_work + '\n\n'
              'No browser/GLSL/GPU/field/roots/cost/capture/acceptance or uniform support in this phase. '
              'No v35 or promotion. Original exact-jet and 716/720 reference failures persist. '
              'latest.png remains the previously inspected REJECTED GAME v33r6 entry. Live/default/ledger '
              'bytes unchanged; all19 realism/source/coverage/route/full acceptance unfinished.\n')
    review_name = p.PREFIX + '-preparation-review.md'
    with (p.HERE / review_name).open('x') as f:
        f.write(review); f.flush(); os.fsync(f.fileno())
    notes_bytes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes_bytes.startswith(b'\xef\xbb\xbf')
    notes = notes_bytes.decode('utf-8-sig')
    head, old_next = notes.rsplit('## Exact next bounded work', 1)
    assert 'preparation-failure-integrity.json' in old_next
    section = (f'## Staged arithmetic r2 preparation CLOSED — static {grade}; runtime NOT RUN\n'
               f'- {detail}\n- {checks}\n'
               f'- Foreground frozen static ONCE actual exit{receipt["actual_exit"]}; Node evidence durable before assessment. '
               'Sources/inputs/history/receipts/protected/current display bound; prior display archived; NOTES once/BOM preserved. '
               'No browser/GPU/support/v35/field/roots/cost/capture/acceptance. latest unchanged REJECTED GAME v33r6; all19 unfinished.\n\n')
    new_notes = head + section + '## Exact next bounded work\n' + next_work + ' Never call superseded display gates.\n'
    new_notes = new_notes.replace(new_notes.splitlines()[0],
        f'# Active: REDIRECT4 — staged arithmetic r2 preparation CLOSED static {grade}; runtime NOT RUN', 1)
    readme = (p.HERE / 'README.md').read_text()
    matching = [line for line in readme.splitlines() if line.startswith('Distinct [staged arithmetic preparation]')]
    assert len(matching) == 1
    replacement = (f'Distinct [staged arithmetic r2 preparation]({review_name}) is **CLOSED static {grade}; runtime NOT RUN**. '
                   f'Foreground static actual exit{receipt["actual_exit"]}; Node source, command, stdout/stderr and exit receipts retained. '
                   + ('Missing operation API reproduced and repaired insertion-only; all original static requirements pass. ' if passed else 'No preparation pass; review saved failure evidence. ')
                   + 'No GPU arithmetic support, v35 or visual progress claimed; original numerical/realism failures retained.')
    assert 'staged arithmetic preparation CLOSED static FAIL' in (p.HERE / 'status.txt').read_text()
    status = (f'Isolated v34 numerical FAIL retained. Staged arithmetic r2 preparation CLOSED static {grade} actual exit{receipt["actual_exit"]}; '
              + ('missing arithmeticStep reproduced; insertion-only wrapper repair and full static PASS. ' if passed else 'durable per-stage failure evidence; runtime blocked. ')
              + 'Runtime NOT RUN. No support/v35/field/roots/cost/capture/acceptance. latest unchanged inspected REJECTED GAME v33r6; '
              'live/defaults/ledgers unchanged;all19 unfinished. ' + next_work + '\n')
    archives = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name + '-before-' + p.PREFIX + '-preparation'
        with (p.HERE / archive).open('xb') as f:
            f.write((p.HERE / name).read_bytes()); f.flush(); os.fsync(f.fileno())
        archives[archive] = p.digest(archive)
    updates = {'NOTES.md': b'\xef\xbb\xbf' + new_notes.encode(),
               'README.md': readme.replace(matching[0], replacement, 1).encode(), 'status.txt': status.encode()}
    for name, data in updates.items():
        with (p.HERE / name).open('wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
    files = dict(history['files']); files[p.HISTORY] = p.digest(p.HISTORY)
    files.update(p.read(p.PREFIX + '-freeze.json')['sources']); files.update(archives)
    for path in p.HERE.glob(p.PREFIX + '-*'):
        assert path.is_file()
        # The launcher closes this log and writes its exit receipt after we return.
        if path.name in (p.PREFIX + '-close-once.log', p.PREFIX + '-close-once-exit.json'):
            continue
        files[path.name] = p.digest(path.name)
    p.verify(files); p.verify(history['protected'])
    assert p.digest('latest.png') == history['display']['latest.png']
    display = {n: p.digest(n) for n in history['display']}
    p.save(manifest, {'phase': 'staged arithmetic r2 preparation CLOSED static ' + grade,
        'files': files, 'protected': history['protected'], 'display': display,
        'prior_display': history['display'], 'archived_display': archives, 'node_results': node_results,
        'static_passed': passed, 'static_actual_exit': receipt['actual_exit'], 'runtime_run': False,
        'numeric_passed': False, 'synthetic_uniform_candidate_supported': False,
        'capture_permitted': False, 'new_images': 0})
    p.verify(p.read(manifest)['files']); p.verify(display)
    print('R2 preparation closure:', grade, len(files), 'evidence hashes; runtime NOT RUN', flush=True)


if __name__ == '__main__':
    main()
