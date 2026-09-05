"""Create a distinct corrected static successor; never edit/replay frozen v35."""
import ast
import v35_preparation as p


def main():
    p.frozen(); p.receipt('build')
    failure = p.read('centre-v35-static-once-exit.json')
    assert failure['actual_exit'] == 1 and failure['launcher_error'] is None
    assert failure['log_sha256'] == p.digest('centre-v35-static-once.log')
    assert failure['launch_sha256'] == p.digest('centre-v35-static-once-launch.json')
    log = (p.HERE / 'centre-v35-static-once.log').read_text()
    assert 'assert new_result.count(new) == 1' in log and log.endswith('AssertionError\n')
    assert not (p.HERE / 'centre-v35-static.json').exists()
    frozen = p.read('centre-v35-freeze.json')
    names = set(frozen['sources']) | {path.name for path in p.HERE.glob('centre-v35-*') if path.is_file()}
    p.save('centre-v35-preparation-failure.json', {'files': {n: p.digest(n) for n in sorted(names)},
        'actual_exit': 1, 'static_passed': False, 'runtime_run': False,
        'cause': 'Checker reversal incorrectly includes the existing time/high/pixelScale declaration; probe instrumentation adds probeMode there. New offset binding checks completed, but full static gate did not pass.',
        'action': 'Preserve frozen attempt. Distinct v35r2 checker reverses only the inserted declaration line.'})
    controls = ['v35_preparation.py', 'build_centre_v35.py', 'check_centre_v35_static.py',
                'check_centre_v35_uniforms.cjs', 'run_centre_v35_preparation_once.py', 'close_centre_v35_preparation.py']
    changes = {}
    for base in controls:
        target = base.replace('v35', 'v35r2')
        text = (p.HERE / base).read_text().replace('v35', 'v35r2')
        edits = []
        if base == 'check_centre_v35_static.py':
            edits.append(('for old, new in reversed(EDITS[1:]):',
                "for old, new in reversed([('', '\\n   uniform float childAxialOffset,childAngularOffset;')] + EDITS[2:]):"))
        if base == 'build_centre_v35.py':
            edits.append(("sources = list(delta) + CONTROL + [p.PREFIX + '-source-delta.json']",
                "failure = p.read('centre-v35-preparation-failure.json')\n"
                "    p.verify(failure['files'])\n"
                "    extras = list(failure['files']) + ['centre-v35-preparation-failure.json',\n"
                "        'prepare_centre_v35_static_r2.py', 'centre-v35-static-r2-source-delta.json']\n"
                "    extras += [path.name for path in p.HERE.glob('centre-v35-static-r2-prepare-once*') if path.is_file()]\n"
                "    sources = list(delta) + CONTROL + [p.PREFIX + '-source-delta.json'] + extras"))
        if base == 'close_centre_v35_preparation.py':
            edits.append(('Four reversible source edits per candidate/reference:',
                'The first frozen v35 static run exited1 at its declaration-reversal checker:\n'
                'instrumentation adds probeMode to the existing declaration. All six binding\n'
                'paths had passed, but the complete static gate had not. Its source, receipts\n'
                'and outputs are preserved in centre-v35-preparation-failure.json. This distinct\n'
                'v35r2 successor corrects only that checker reversal to remove the inserted\n'
                'line, not the existing instrumented declaration. Runtime sources are\n'
                'version-only equivalents of the unexecuted v35 candidate/fixtures.\n\n'
                'Four reversible source edits per candidate/reference:'))
            edits.append(('- Frozen18derived files plus preparation controls before static.',
                '- Frozen v35 static actual exit1 at checker declaration reversal (probeMode instrumentation changes the existing declaration); all source/log/exit/Node evidence retained in centre-v35-preparation-failure.json. Distinct v35r2 corrects only that checker reversal, with version-only runtime sources; no frozen attempt edited or replayed.\n- Frozen18derived files plus preparation controls before static.'))
        for before, after in edits:
            assert text.count(before) == 1, (base, before[:80])
            text = text.replace(before, after, 1)
        if target.endswith('.py'):
            ast.parse(text, filename=target)
        p.write(target, text)
        changes[target] = {'base': base, 'base_sha256': p.digest(base),
                           'rename': ['v35', 'v35r2'], 'edits': edits, 'sha256': p.digest(target)}
    p.save('centre-v35-static-r2-source-delta.json', changes)
    print('Distinct v35r2 correction sources created; original v35 failure preserved, no field runtime')


if __name__ == '__main__':
    main()
