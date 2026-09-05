"""One-time offline preparation and evidence closure. No browser execution."""
import os
import subprocess
import sys
import probe_centre_v34_transport as t
p = t.p


def write_exclusive(name, data):
    with (p.HERE / name).open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def main():
    history = t.prior(True)
    prefix = t.PREFIX
    p.save(prefix + '-prepare-started.json', {'browser_run': False})
    p.save(prefix + '-freeze.json', {'sources': {n: p.digest(n) for n in t.SOURCES},
           'history_sha256': p.digest(t.HISTORY), 'environment': t.environment()})
    argv = [sys.executable, '-B', str(p.HERE / 'run_centre_v34_transport_once.py'), 'static']
    p.save(prefix + '-static-launcher-invocation.json', {'argv': argv})
    actual = subprocess.run(argv, cwd=p.HERE.parent, timeout=65).returncode
    p.save(prefix + '-static-launcher-exit.json', {'actual_exit': actual})
    receipt = p.read(prefix + '-static-once-exit.json')
    launch = p.read(prefix + '-static-once-launch.json')
    assert actual == receipt['actual_exit'] == 0 and receipt['launcher_error'] is None
    assert receipt['log_sha256'] == p.digest(prefix + '-static-once.log')
    assert receipt['launch_sha256'] == p.digest(prefix + '-static-once-launch.json')
    assert launch['freeze_sha256'] == p.digest(prefix + '-freeze.json')
    assert launch['script_sha256'] == p.digest('probe_centre_v34_transport.py')
    assert launch['launcher_sha256'] == p.digest('run_centre_v34_transport_once.py')
    assert p.read(prefix + '-static.json')['passed']
    t.prior(True)
    summary = ('Distinct transport preparation CLOSED static PASS; browser NOT RUN. Installed Playwright '
               'Python serializer maps positive float zero to wire -0 because equality with float("-0") '
               'also matches +0. Offline original-texture reproduction changes exactly 905 zero signs; '
               '119 nonzero components remain exact and the resulting bits match saved r2 input. '
               'This localizes a defect in the installed serializer, not a recovered historical wire trace. '
               'Mixed signed-zero/finite fixtures, integer-bit and JSON-text transport pass strict offline '
               'Node reconstruction; JSON stringify explicitly loses negative-zero signs. No dependency patch. '
               'Five fake-resource cleanup cases pass identity accounting and exception continuation; '
               'saved r2 reported three disposals after three registrations, with its fixed-eight fatal '
               'classification unchanged. No actual GPU cleanup/leak conclusion.')
    next_work = ('Verify centre-v34-transport-preparation-integrity.json files/protected/display and '
                 'static-once actual-exit0 launch/log/freeze/script hashes. Then run '
                 'PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright python3 -B world/run_centre_v34_transport_once.py runtime '
                 'ONCE foreground. This is transport-only: no Three/WebGL/arithmetic/field/image calls. '
                 'Wait for actual exit, then close saved case/lifecycle evidence and all receipts before '
                 'considering a distinct arithmetic successor. Preserve failures and strict bit equality; '
                 'no r2 replay, v35, field/roots/cost/capture/acceptance yet.')
    review = ('# Transport-only preparation — static PASS; browser NOT RUN\n\n' + summary +
              '\n\nPrepared seven browser cases: original and mixed fixtures via float, uint32 and JSON-text '
              'transport, plus JS-local signed-zero control. Full wire/ingress/CPU/JSON-roundtrip bits are '
              'saved before validation. Only integer bits are proposed as the authoritative future arithmetic '
              'input route. Float-list failures are diagnostic, never excused as exact inputs.\n\n'
              'Frozen r2, original exact-jet/716-of-720 failures and all visual gates remain. '
              'latest.png is unchanged inspected REJECTED GAME v33r6; no new render or acceptance.\n\n'
              '## Next bounded phase\n\n' + next_work + '\n')
    write_exclusive(prefix + '-preparation-review.md', review.encode())
    notes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes.startswith(b'\xef\xbb\xbf')
    body, old_next = notes.decode('utf-8-sig').split('## Exact next bounded work\n')
    assert 'Prepare a distinct transport-only investigation' in old_next
    body = body.split('\n', 1)[1]
    new_notes = ('# Active: REDIRECT4 — transport preparation CLOSED static PASS; browser NOT RUN\n' + body +
                 '## Distinct transport preparation CLOSED — static PASS; no browser\n- ' + summary +
                 '\n- Verified prior943 evidence/16protected/4display and closure actual exit0 hashes. '
                 'Frozen r2 untouched; all19 realism/source/coverage/route/full acceptance unfinished. '
                 'Prior display archived; NOTES once/BOM retained; latest unchanged inspected REJECTED GAME v33r6.\n\n'
                 '## Exact next bounded work\n' + next_work + '\n')
    readme = (p.HERE / 'README.md').read_text()
    anchor = [line for line in readme.splitlines() if line.startswith('Distinct [staged arithmetic r2 runtime]')]
    assert len(anchor) == 1
    addition = ('Distinct [transport-only preparation](centre-v34-transport-preparation-review.md) is '
                '**static PASS; browser NOT RUN**. Offline evidence localizes positive-zero corruption '
                'in the installed Playwright Python serializer. Strict uint32 transport and partial '
                'cleanup accounting fixtures pass offline; no arithmetic, GPU cleanup or visual claim.')
    assert 'r2 runtime CLOSED actual exit1' in (p.HERE / 'status.txt').read_text()
    updates = {'NOTES.md': b'\xef\xbb\xbf' + new_notes.encode(),
               'README.md': readme.replace(anchor[0], anchor[0] + '\n\n' + addition, 1).encode(),
               'status.txt': (summary + ' latest unchanged inspected REJECTED GAME v33r6; all19 unfinished. ' + next_work + '\n').encode()}
    archives = {}
    for name in updates:
        archived = name + '-before-' + prefix + '-preparation'
        write_exclusive(archived, (p.HERE / name).read_bytes())
        archives[archived] = p.digest(name)
    for name, data in updates.items():
        with (p.HERE / name).open('wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
    files = dict(history['files'])
    files[t.HISTORY] = p.digest(t.HISTORY)
    for name in (p.PREFIX + '-runtime-close-once-launch.json', p.PREFIX + '-runtime-close-once-exit.json', p.PREFIX + '-runtime-close-once.log'):
        files[name] = p.digest(name)
    files.update({n: p.digest(n) for n in t.SOURCES})
    files.update({f.name: p.digest(f.name) for f in p.HERE.glob(prefix + '-*') if f.is_file()})
    files.update(archives)
    p.verify(files); p.verify(history['protected'])
    assert p.digest('latest.png') == history['display']['latest.png']
    display = {name: p.digest(name) for name in history['display']}
    manifest = prefix + '-preparation-integrity.json'
    p.save(manifest, {'files': files, 'protected': history['protected'], 'display': display,
           'prior_display': history['display'], 'archived_display': archives,
           'static_passed': True, 'runtime_run': False, 'arithmetic_support': False,
           'capture_permitted': False, 'new_images': 0})
    for key in ('files', 'protected', 'display'): p.verify(p.read(manifest)[key])
    print('Transport preparation CLOSED:', len(files), 'evidence hashes; browser NOT RUN')


if __name__ == '__main__':
    main()
