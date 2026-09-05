"""Saved-evidence closure only; no browser, oracle sampling, or acceptance replay."""
from centre_v34_followup_common import HERE, PREFIX, LEAVES, read, save, digest, verify, runtime_gate


def main():
    runtime_gate()
    preparation = read(PREFIX + '-preparation-integrity.json')
    archive = 'NOTES-before-centre-v34-followup-runtime.md'
    result_name = PREFIX + '-runtime-integrity.json'
    review_name = PREFIX + '-runtime-review.md'
    for name in [archive, result_name, review_name]:
        assert not (HERE / name).exists(), 'Never replay closure'
    for label, expected in [('arithmetic', 1), ('profiles', 0)]:
        stem = PREFIX + '-' + label + '-once'
        receipt = read(stem + '-exit.json')
        launch = read(stem + '-launch.json')
        assert receipt['actual_exit'] == expected
        assert receipt['log_sha256'] == digest(stem + '.log')
        assert receipt['launch_sha256'] == digest(stem + '-launch.json')
        assert launch['script_sha256'] == digest(launch['script'])
        assert launch['launcher_sha256'] == digest('run_centre_v34_followup_once.py')
        assert launch['input_manifest'] == digest(PREFIX + '-inputs.json')
        assert launch['preparation_manifest'] == digest(PREFIX + '-preparation-integrity.json')
    arithmetic = read(PREFIX + '-arithmetic-result.json')
    assert not arithmetic['complete'] and not arithmetic['synthetic_uniform_candidate_supported']
    assert not arithmetic['arms'] and not arithmetic['errors']
    assert 'GL error 1282' in arithmetic['failure']
    for i, event in enumerate(arithmetic['events']):
        assert event == read(PREFIX + '-arithmetic-event-' + str(i).zfill(2) + '.json')
    events = {e['event']: e for e in arithmetic['events']}
    assert events['arm_started']['leaf'] == 0 and events['arm_started']['arm'] == 'literal'
    assert 'resources_closed' in events and 'browser_closed' in events
    reports = events['shader_reports']['reports']
    assert len(reports) == 1
    assert all(reports[0][k] for k in ['linked', 'vertexCompiled', 'fragmentCompiled'])
    assert all(not reports[0][k] for k in ['programLog', 'vertexLog', 'fragmentLog'])
    profiles = read(PREFIX + '-profiles-result.json')
    rays = read(PREFIX + '-rays.json')
    assert profiles['complete'] and len(profiles['profiles']) == 4
    assert not any(profiles[k] for k in ['numeric_passed', 'capture_permitted', 'first_root_certified',
                                        'old_full_forward_scan_replayed', 'dependent_independent_gate_run'])
    rows, total_brackets, midpoint_count = [], 0, 0
    for i, profile in enumerate(profiles['profiles']):
        assert profile == read(PREFIX + '-profiles-ray-' + str(i) + '-brackets.json')
        samples = read(PREFIX + '-profiles-ray-' + str(i) + '-samples.json')
        assert samples['identity'] == {k: rays['rays'][i][k] for k in samples['identity']}
        assert len(samples['samples']) == 161
        assert set(profile['channels']) == set(['full'] + LEAVES)
        for name, channel in profile['channels'].items():
            for bracket in channel['brackets']:
                total_brackets += 1
                lo, hi = bracket['original']['depths']
                lv, hv = bracket['original']['values']
                assert lv * hv < 0 and len(bracket['bisections']) == 24
                assert len(bracket['midpoint_full_profiles']) == 24
                for midpoint, full in zip(bracket['bisections'], bracket['midpoint_full_profiles']):
                    midpoint_count += 1
                    mid, mv = midpoint['depth'], midpoint['value']
                    assert mid == (lo + hi) / 2 and full['depth'] == mid
                    assert mv == (full['full'] if name == 'full' else full['expanded'][name])
                    if mv * lv > 0:
                        lo, lv = mid, mv
                    else:
                        hi, hv = mid, mv
                assert bracket['final']['depths'] == [lo, hi]
                assert bracket['final']['values'] == [lv, hv] and lv * hv <= 0
                assert bracket['final']['width'] == hi - lo
        full = profile['channels']['full']['brackets']
        assert [b['orientation'] for b in full] == ['enter', 'exit']
        assert len(profile['old_grid_algebra']) == 1
        grid = profile['old_grid_algebra'][0]
        outer_lo, outer_hi = full[0]['final']['depths'][0], full[1]['final']['depths'][1]
        left, right = grid['old_grid_positions_algebraic_only']
        assert left < outer_lo < outer_hi < right
        assert grid['both_crossings_enclosed_between_grid_positions']
        assert grid['outer_width_bound'] == outer_hi - outer_lo
        rows.append({'identity': samples['identity'], 'enter': full[0]['final'], 'exit': full[1]['final'],
                     'outer_width_bound': grid['outer_width_bound'], 'grid_positions': [left, right],
                     'active_leaves': sorted({s['active_leaf'] for s in samples['samples']})})
    review = '''# v34 distinct follow-up runtime — CLOSED; numerical FAIL retained

Both frozen diagnostics ran once in foreground with bound launch/log/actual-exit receipts.

## Arithmetic: INCOMPLETE, actual exit 1

Chromium149/Three160/WebGL2/highp23/SwiftShader launched. The first childAxial
literal arm failed with GL_INVALID_OPERATION (1282) at the final error check.
Zero complete arms or readback arrays were persisted; neither uniform arm ran.
One saved shader report has successful vertex/fragment compilation and linking,
empty compile/link logs, and empty optional translated-source strings. Resources
and browser closed; no page/console errors were recorded. The GL error is real.
Its origin is NOT localized: setup, render, shader/debug queries and readback
precede the sole error check. Successful linking does not identify the failing call.
No arithmetic conclusion, compiler attribution, supported uniform fix or v35 candidate.
The failed attempt and all frozen sources remain immutable; never retry it.

## Four local profiles: complete, actual exit 0

161 float64 CPU-ray depths per ray, all full/11-leaf channels retained. All four
have an entering and exiting full-field strict bracket. Every observed leaf/full
bracket completed24bisections with saved full midpoint profiles. Closure replays
the saved bracket arithmetic only; it does not evaluate the oracle or rerun scans.

| Grid / z / time / mode / ray | Local outer width bound | Old grid positions |
|---|---:|---|
'''
    for row in rows:
        r = row['identity']
        review += f"| {r['width']}x{r['height']} / {r['z']} / {r['time']} / {r['high']} / {r['ray']} | {row['outer_width_bound']:.15g} | {row['grid_positions']} |\n"
    review += f'''
Total retained brackets: {total_brackets}; midpoint full profiles: {midpoint_count}.
Each pair lies strictly between two algebraic positions of the old .003 grid.
This supports a local scan-resolution explanation, NOT unique-component isolation,
absence of earlier roots, GPU-ray equivalence, or first-root certification.
The old scan was not replayed. Original716/720reference failure and exact expanded
jet failure remain. Unbracketed leaf channels remain unresolved, not absent.

## Next bounded work

Design a NEW, separately named infrastructure-only GL-error localization diagnostic
with staged durable error/framebuffer/readback/debug-query evidence and simple known
texel controls. Inspect saved source first; separate optional translated-shader queries
from render/readback. Do not assume the responsible operation or silently clear errors.
Freeze and statically review that design before runtime. This is not permission to
retry the failed arithmetic probe or to prepare v35 without both-leaf support.

No independent first-root, cost, capture or acceptance ran. No image was produced
or inspected; latest remains the inspected REJECTED GAME v33r6 entry. Live/defaults,
ledgers, original gates and historical evidence unchanged. All19 remains unfinished.
'''
    original = (HERE / 'NOTES.md').read_bytes()
    assert original.startswith(b'\xef\xbb\xbf')
    notes = original.decode('utf-8-sig')
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v34 follow-up runtime CLOSED; arithmetic GL failure, four local crossing pairs', 1)
    assert notes.count('## Exact next bounded work') == 1
    notes = notes.split('## Exact next bounded work')[0] + '''## v34 distinct follow-up runtime CLOSED — arithmetic INCOMPLETE; profiles complete
- Both frozen foreground runs ONCE: arithmetic actual exit1, profiles actual exit0; launch/log/actual-exit hashes verified. Arithmetic first axial literal arm GL1282 at final check;zero complete arms/readbacks,uniforms not reached. Compile/link success and empty logs retained;resource/browser close recorded. Failing operation unlocalized across setup/render/debug queries/readback. No support for v35,not evidence against the arithmetic hypothesis;never retry/edit frozen probe.
- All4local float64 CPU-ray profiles complete:161depths/full+11leaves,2full crossings each,16total full/leaf brackets and384midpoint full profiles. Outer enter/exit width bounds839=.0008836397051723566;745=.0005879427164856565;807/809=.0008649691015563121,all strictly inside one old .003 grid cell. Local scan-resolution evidence only;no unique-component/earliest-root/GPU-ray certification. Unbracketed leaf channels unresolved. Original716/720and exact-jet FAIL remain.
- Saved-evidence closure verifies every event/receipt/profile and replays saved24bisections without oracle sampling. Runtime review/integrity bind new evidence and frozen/historical/protected files. No original probe/scan/independent roots/cost/capture/acceptance replay,new PNG/inspection or promotion. latest unchanged inspected REJECTED GAME v33r6 entry. README/status current;NOTES once/BOM preserved/prior bytes archived.

## Exact next bounded work
Design a separately named infrastructure-only GL1282 localization diagnostic: staged durable errors/framebuffer/readback/debug-query evidence and known texel controls. Inspect saved source; isolate optional translated-shader queries from render/readback;no assumed cause or silently ignored errors. Freeze/static-check before runtime. Do NOT rerun either completed diagnostic or modify frozen scripts. No v35 until recorded synthetic support for BOTH leaves; original numerical/first-root/cost/capture gates intact. All19/source/coverage/route/full acceptance unfinished;no WORLD_DONE.
'''
    readme = (HERE / 'README.md').read_text()
    old = next(line for line in readme.splitlines() if line.startswith('Isolated **v34 numerical phase CLOSED — FAIL**.'))
    new = old.replace('are designed, not run.', 'have now run once; see the runtime result below.').replace(
        'both runtime experiments remain NOT RUN.',
        'runtime is now CLOSED: arithmetic actual exit1 (GL1282 before first complete arm; no uniform support), profiles actual exit0 (four local crossing pairs inside old grid cells, not first-root certification). See [runtime review](centre-v34-followup-runtime-review.md). No v35 candidate; numerical FAIL and downstream blocks remain.')
    assert new != old and 'remain NOT RUN' not in new
    with (HERE / archive).open('xb') as stream:
        stream.write(original)
    with (HERE / review_name).open('x') as stream:
        stream.write(review)
    (HERE / 'README.md').write_text(readme.replace(old, new, 1))
    (HERE / 'status.txt').write_text('Isolated v34 numerical FAIL retained. Follow-up runtime CLOSED: arithmetic ONCE actual exit1 GL1282 before first complete arm; no uniform support/v35. Profiles ONCE actual exit0: four local enter/exit pairs inside old .003 grid cells, not first-root certification. Next: distinct staged GL-error localization design/static preparation. No replay/dependent roots/cost/capture/acceptance. latest.png unchanged inspected REJECTED GAME v33r6 entry. Live/defaults/ledgers unchanged;all19 unfinished.\n')
    (HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
    names = [p.name for p in HERE.glob(PREFIX + '-arithmetic-*') if p.is_file()]
    names += [p.name for p in HERE.glob(PREFIX + '-profiles-*') if p.is_file()]
    names += [archive, review_name, 'close_centre_v34_followup_runtime.py', PREFIX + '-preparation-integrity.json']
    names += [PREFIX + '-close-once' + suffix for suffix in ['-launch.json', '-exit.json', '.log']]
    result = {'phase': 'Follow-up runtime CLOSED; arithmetic incomplete, local profiles complete',
              'integrity_passed': True, 'numeric_passed': False, 'capture_permitted': False,
              'synthetic_uniform_candidate_supported': False, 'first_root_certified': False,
              'arithmetic_actual_exit': 1, 'profiles_actual_exit': 0, 'local_profiles': rows,
              'saved_brackets_verified': total_brackets, 'saved_midpoint_profiles_verified': midpoint_count,
              'files': {**preparation['files'], **{n: digest(n) for n in names}},
              'protected': preparation['protected'], 'prior_display': preparation['display'],
              'display': {n: digest(n) for n in preparation['display']}, 'new_images': 0}
    assert result['display']['latest.png'] == preparation['display']['latest.png']
    verify(result['files']); verify(result['protected']); verify(result['display'])
    save(result_name, result)
    print('Runtime closure PASS; arithmetic INCOMPLETE exit1; profiles complete exit0; numerical FAIL retained', flush=True)


if __name__ == '__main__':
    main()
