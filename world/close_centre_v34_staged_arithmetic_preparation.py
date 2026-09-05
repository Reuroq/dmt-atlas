"""Saved-only preparation closure; one display/NOTES update, no runtime."""
import probe_centre_v34_staged_arithmetic as p


def main():
    manifest = p.PREFIX + '-preparation-integrity.json'
    assert not (p.HERE / manifest).exists(), 'Never replay closure'
    p.gate(prepared=False); p.receipt('static')
    history = p.read(p.HISTORY); check = p.read(p.PREFIX + '-static.json')
    assert check['passed'] and check['runtime_run'] is False
    assert not any(p.HERE.glob(p.PREFIX + '-event-*'))
    assert not (p.HERE / (p.PREFIX + '-runtime-once-launch.json')).exists()
    p.save(p.PREFIX + '-close-started.json', {'freeze_sha256': p.digest(p.PREFIX + '-freeze.json')})
    review = '''# Staged synthetic arithmetic preparation CLOSED — static PASS, runtime NOT RUN

Frozen distinct protocol/HTML/runner/launcher/checker/closure. Original arithmetic
attempt and closed GL-localization evidence remain immutable. The original
synthetic seeds and texture are reused unchanged; no inputs were regenerated.

Static checks (no Chromium, GLSL compile, GPU arithmetic, field, image or acceptance):

''' + '\n'.join('- ' + x for x in check['checks']) + '''

The rational integer oracle independently checked all 1024 expected output
components over both 128-texel rows, including padding. Static mocks establish
protocol handling, not GL correctness or actual uniform support. Read
[the frozen protocol](centre-v34-staged-arithmetic-protocol.md) for evidence,
stopping rules and exact BOTH-leaf literal/uniform support criterion.

Translated-source queries are explicitly absent, following the new localization
evidence; no Three internals or GL-error suppression changed. This neither
retrospectively proves the old error's source nor compiler constant folding.

## Next separately bounded phase

Verify this preparation manifest's files/protected/display, and static/close
actual-exit0 receipts. Use only the new frozen foreground runtime launcher ONCE:
`python3 -B world/run_centre_v34_staged_arithmetic_once.py runtime`.
Keep partial/failure evidence; never retry. Save/read-only review must follow
before conclusions. An exit0 means clean completion, not arithmetic support.

No new candidate, actual-field numerical run, roots, cost, capture, promotion or
acceptance. Original expanded-jet and716/720 reference failures remain blocked.
latest.png is unchanged, previously inspected REJECTED GAME v33r6 entry.
All19 RECOGNISE/source/coverage/route/full acceptance remain unfinished.
'''
    review_name = p.PREFIX + '-preparation-review.md'
    with (p.HERE / review_name).open('x') as f:
        f.write(review)
    notes_bytes = (p.HERE / 'NOTES.md').read_bytes()
    assert notes_bytes.startswith(b'\xef\xbb\xbf')
    notes = notes_bytes.decode('utf-8-sig')
    old_title = '# Active: REDIRECT4 — GL localization CLOSED; exact controls, translated-query GL1282'
    assert notes.startswith(old_title)
    marker = '## Exact next bounded work\n'
    assert notes.count(marker) == 1
    section = '''## Distinct staged arithmetic preparation CLOSED — static PASS, runtime NOT RUN
- Frozen NEW gpu_centre_v34_staged_arithmetic.html/probe/check/run/closure and protocol; old diagnostics untouched. Original followup seeds/128x2RGBA32F texture reused by hash, including empty-cell records/subnormals/padding. Original shader function byte-identical; only second literal becomes uniform in each arm.
- 126stages:known-float control first,then both leaves/literal+uniform on shared texture/target. Durable chained intent/result/assessment;full512component Three/raw values/bits BEFORE validation;operation-local pre/post/errors/exceptions,framebuffer/link/source/uniform/input evidence. No translated-source queries,explicitly documented from GL localization;no Three changes/error suppression.
- Frozen static ONCE actual exit0:AST/JS,ordering,1024components vs independent exact-rational binary32 oracle,GL/exception/context/drain mocks,sentinel/nonfinite/bit/signed-zero,transport disagreement,fatal stop versus mismatch continuation,both-leaf support criterion,launcher exit7/replay-refusal mocks PASS. No browser/GLSL/runtime or arithmetic support.
- Preparation integrity binds sources/inputs/history/static receipts/protected/current display;prior display archived;NOTES once/BOM retained. latest unchanged inspected REJECTED GAME v33r6. Original numerical/716-of-720 first-root failure and downstream blocks retained;no v35/roots/cost/capture/acceptance/promotion.

'''
    next_work = ('Verify centre-v34-staged-arithmetic-preparation-integrity.json files/protected/display and '
                 'static/close actual-exit0 receipts using the new probe helpers. Then run ONLY '
                 'run_centre_v34_staged_arithmetic_once.py runtime ONCE in a separately bounded foreground '
                 'phase; preserve actual exit and all staged evidence,then saved-only review. Exit0 is clean '
                 'completion,not support;exact BOTH-leaf criterion remains. Never retry/edit frozen probes, '
                 'call superseded preparation gates after display changes,or replay old acceptance. '
                 'All19/source/coverage/route/full acceptance unfinished;no WORLD_DONE.\n')
    new_notes = notes.split(marker)[0].replace(old_title,
        '# Active: REDIRECT4 — staged arithmetic frozen/static PASS; runtime NOT RUN', 1)
    new_notes += section + marker + next_work
    readme = (p.HERE / 'README.md').read_text()
    matching = [s for s in readme.splitlines() if s.startswith('Distinct [GL-localization runtime]')]
    assert len(matching) == 1
    replacement = ('Distinct [staged arithmetic preparation](centre-v34-staged-arithmetic-preparation-review.md) '
                   'is **CLOSED static PASS; runtime NOT RUN**. Known-float control then both-leaf literal/uniform '
                   'arms;126durable stages,exact Three/raw values/bits and operation-local errors. '
                   'Translated-source queries explicitly absent after GL localization. Original failures retained; '
                   'no arithmetic support,v35,numerical or realism pass.')
    status = ('Isolated v34 numerical FAIL retained. NEW staged arithmetic preparation CLOSED static PASS; '
              'runtime NOT RUN.126stages:known-float control then both-leaf literal/uniform;durable exact Three/raw '
              'evidence,operation-local errors;no translated-source queries. Next:separate one-shot foreground '
              'runtime then saved-only review. No support/v35/roots/cost/capture/acceptance. latest unchanged '
              'inspected REJECTED GAME v33r6;live/defaults/ledgers unchanged;all19 unfinished.\n')
    archives = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name + '-before-' + p.PREFIX + '-preparation'
        assert not (p.HERE / archive).exists()
        archives[archive] = p.digest(name)
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        with (p.HERE / (name + '-before-' + p.PREFIX + '-preparation')).open('xb') as f:
            f.write((p.HERE / name).read_bytes())
    (p.HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + new_notes.encode('utf-8'))
    (p.HERE / 'README.md').write_text(readme.replace(matching[0], replacement, 1))
    (p.HERE / 'status.txt').write_text(status)
    files = dict(history['files']); files[p.HISTORY] = p.digest(p.HISTORY)
    files.update(p.read(p.PREFIX + '-freeze.json')['sources'])
    for suffix in ('-freeze.json', '-static-started.json', '-static.json', '-static-once-launch.json',
                   '-static-once-exit.json', '-static-once.log', '-close-started.json',
                   '-close-once-launch.json', '-preparation-review.md'):
        files[p.PREFIX + suffix] = p.digest(p.PREFIX + suffix)
    files.update(archives)
    p.verify(files); p.verify(history['protected'])
    assert p.digest('latest.png') == history['display']['latest.png']
    display = {n: p.digest(n) for n in history['display']}
    p.save(manifest, {'phase': 'staged arithmetic preparation CLOSED; runtime NOT RUN',
                     'files': files, 'protected': history['protected'], 'display': display,
                     'prior_display': history['display'], 'archived_display': archives,
                     'static_passed': True, 'runtime_run': False, 'numeric_passed': False,
                     'synthetic_uniform_candidate_supported': False, 'capture_permitted': False, 'new_images': 0})
    p.verify(p.read(manifest)['files']); p.verify(display)
    print('Preparation closure verified:', len(files), 'evidence hashes; runtime NOT RUN', flush=True)


if __name__ == '__main__':
    main()
