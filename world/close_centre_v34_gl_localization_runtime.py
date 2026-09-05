"""Saved-only closure; update display records once, preserving their prior bytes."""
from probe_centre_v34_gl_localization import HERE, PREFIX, digest, gate, read, save, verify


def main():
    manifest = PREFIX + '-runtime-integrity.json'
    assert not (HERE / manifest).exists(), 'Never replay closure'
    gate()
    prep = read(PREFIX + '-preparation-integrity.json')
    review = read(PREFIX + '-saved-review.json')
    assert review['saved_evidence_verified'] and review['actual_exit'] == 1
    assert review['result_sha256'] == digest(PREFIX + '-result.json')
    verify(read(PREFIX + '-result.json')['events'])
    notes = (HERE / 'NOTES.md').read_bytes()
    assert notes.startswith(b'\xef\xbb\xbf')
    note_text = notes.decode('utf-8-sig')
    old_title = '# Active: REDIRECT4 — GL localization frozen/static PASS; runtime NOT RUN'
    assert note_text.startswith(old_title)
    marker = '## Exact next bounded work\n'
    assert note_text.count(marker) == 1
    next_work = ('Verify centre-v34-gl-localization-runtime-integrity.json files/protected/display hashes '
                 'and its bound actual-exit1 receipt; do not call superseded preparation gate() after display updates. '
                 'Then prepare a NEW separately named staged synthetic arithmetic diagnostic as specified in '
                 'centre-v34-gl-localization-runtime-review.md: exact both-leaf literal/uniform arms, '
                 'known-float control, durable Three/raw values/bits before validation, staged errors, '
                 'no translated-source queries. Freeze/static checks only in the next preparation phase; '
                 'no runtime until preparation closes. Never edit/retry frozen diagnostics or rerun old '
                 'scans/acceptance. Original numerical/first-root/cost/capture gates remain blocked; '
                 'all19 unfinished; no WORLD_DONE.\n')
    section = ('## Distinct GL localization runtime CLOSED — controls exact; query errors retained\n'
               '- Frozen foreground launcher ONCE actual exit1/no launcher exception; all117stages/358events complete. '
               'Saved-only review exit0 independently checked chained intents/results/assessments, receipts, '
               '8exact512component Three/raw values/bits,8complete framebuffers and clean disposal/browser close.\n'
               '- 109ok/8query-error: only individually isolated translated-source queries raised GL1282; '
               '8browser warnings explicitly identify deleted objects. isShader=true,DELETE_STATUS=true, '
               'COMPILE_STATUS=true and other shader queries clean. All known-texel setup/render/readbacks clean. '
               '13warnings retained(8query,4readPixels stall,1deprecation);infrastructure_clean=false.\n'
               '- This establishes the failing operation in NEW controls,not retrospective proof of the old '
               'arithmetic failure or compiler arithmetic. No arithmetic support/v35/first-root/cost/capture/acceptance; '
               'original exact-jet and716/720FAIL retained. No new image/inspection/promotion.\n'
               '- Runtime review defines a distinct staged arithmetic preparation next. Integrity binds '
               'historical/frozen/runtime/review evidence,protected files and current display;prior display bytes '
               'archived,NOTES updated once/BOM retained. latest remains inspected REJECTED GAME v33r6; '
               'live/defaults/ledgers unchanged.\n\n')
    new_notes = note_text.split(marker)[0].replace(old_title,
        '# Active: REDIRECT4 — GL localization CLOSED; exact controls, translated-query GL1282', 1)
    new_notes += section + marker + next_work
    readme = (HERE / 'README.md').read_text()
    matching = [line for line in readme.splitlines() if line.startswith('Distinct [GL-localization preparation]')]
    assert len(matching) == 1
    replacement = ('Distinct [GL-localization runtime](centre-v34-gl-localization-runtime-review.md) is **CLOSED, actual exit1 retained**: '
                   'all117stages complete;8exact known-texel Three/raw readbacks. Only8translated-source queries raised GL1282; '
                   'driver warnings identify deleted objects. This is infrastructure localization,not old arithmetic proof or v35 support. '
                   'Next:prepare a distinct staged arithmetic diagnostic;no numerical or realism pass.')
    new_readme = readme.replace(matching[0], replacement, 1)
    new_status = ('Isolated v34 numerical FAIL retained. GL localization runtime CLOSED actual exit1:117stages/358events, '
                  '8exact known-texel readbacks;8translated-source GL1282 queries with deleted-object warnings. '
                  'Saved-only review PASS;infrastructure_clean=false. Next:NEW staged arithmetic preparation,not runtime. '
                  'No old arithmetic proof/support/v35/roots/cost/capture/acceptance. latest unchanged inspected REJECTED GAME v33r6; '
                  'live/defaults/ledgers unchanged;all19 unfinished.\n')
    archived = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name + '-before-' + PREFIX + '-runtime'
        assert not (HERE / archive).exists()
        archived[archive] = digest(name)
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        with (HERE / (name + '-before-' + PREFIX + '-runtime')).open('xb') as stream:
            stream.write((HERE / name).read_bytes())
    (HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + new_notes.encode('utf-8'))
    (HERE / 'README.md').write_text(new_readme)
    (HERE / 'status.txt').write_text(new_status)
    files = dict(prep['files'])
    for p in HERE.glob(PREFIX + '-*'):
        if p.is_file(): files[p.name] = digest(p.name)
    for name in ('review_centre_v34_gl_localization_saved.py', 'close_centre_v34_gl_localization_runtime.py'):
        files[name] = digest(name)
    files.update(archived)
    verify(files); verify(prep['protected'])
    assert digest('latest.png') == prep['display']['latest.png']
    display = {n: digest(n) for n in prep['display']}
    save(manifest, {'phase': 'GL localization runtime CLOSED; actual exit1 retained',
                   'files': files, 'protected': prep['protected'], 'display': display,
                   'prior_display': prep['display'], 'archived_display': archived,
                   'runtime_run': True, 'actual_exit': 1, 'infrastructure_clean': False,
                   'saved_evidence_verified': True, 'numeric_passed': False,
                   'synthetic_uniform_candidate_supported': False, 'capture_permitted': False,
                   'new_images': 0})
    verify(read(manifest)['files']); verify(display)
    print('Runtime closure verified:', len(files), 'evidence,', len(prep['protected']), 'protected,', len(display), 'display hashes')


if __name__ == '__main__':
    main()
