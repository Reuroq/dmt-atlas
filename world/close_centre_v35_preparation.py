"""Saved-only static preparation closure; never execute a field or browser."""
import v35_preparation as p

NEXT = (
    'Verify centre-v35-fixture-integrity.json files/protected/display and '
    'centre-v35-close-once actual-exit0 receipt hashes. Static v35 uniform-offset '
    'candidate is frozen, not an established field fix. Before field runtime, design '
    'and statically close a distinct additive strict root-isolation fixture using '
    'the existing four-ray local-profile evidence and centre-v34-followup-experiment-design.md '
    'section B. Preserve the original .003 scan/results and every all-720 requirement; '
    'require explicit local brackets plus unchanged global independent first-root '
    'certification, never nearest-root substitution. Do not edit/replay frozen v34/v35 '
    'fixtures or relax exact jets, tolerances, budgets, cost, capture or acceptance gates.'
)
STATUS = (
    'Isolated v35 uniform-offset preparation CLOSED static PASS; no field/browser runtime. '
    'Only two second-offset literals become runtime uniforms, with exact binary32 bindings '
    'in six high/low construction paths. Shape/material/march/CPU oracle unchanged; '
    '48cases/75996rays, exact jets, 720fixed+720independent roots and 12cost pairs retained. '
    'Synthetic r3 support is not actual-field correctness; original exact-jet and '
    '716/720 failures remain. Next: distinct additive strict root-isolation design/static '
    'preparation before runtime. latest.png unchanged inspected REJECTED GAME v33r6 entry, '
    'not v35. Live/defaults/ledgers unchanged; all19/source/coverage/route/full acceptance '
    'unfinished. No promotion, new render or acceptance pass.'
)


def main():
    freeze = p.frozen(); prior = p.history()
    for label in ('build', 'static'):
        p.receipt(label)
    checks = p.read(p.PREFIX + '-static.json')
    assert checks['static_passed'] and checks['browser_runs'] == checks['actual_glsl_runs'] == checks['field_samples'] == 0
    assert checks['binding_paths'] and checks['fixed_references'] == checks['interval_references'] == 720
    # Inspect every durable Node exit/output receipt without rerunning a stage.
    exits = sorted(p.HERE.glob(p.PREFIX + '-static-node-*-exit.json'))
    assert len(exits) == 17, len(exits)
    for path in exits:
        receipt = p.read(path.name); stem = path.name[:-len('-exit.json')]
        assert receipt['actual_exit'] == 0 and receipt['launcher_error'] is None
        for key, suffix in [('stdout_sha256', '-stdout.txt'), ('stderr_sha256', '-stderr.txt'), ('launch_sha256', '-launch.json')]:
            assert receipt[key] == p.digest(stem + suffix)
        assert (p.HERE / (stem + '-stderr.txt')).read_bytes() == b''
        launch = p.read(stem + '-launch.json')
        if launch['stdin_sha256'] is not None:
            assert launch['stdin_sha256'] == p.digest(stem + '.js')
    for pattern in ('centre-v35-*-started.json', 'run-centre-v35-*-once-launch.json',
                    'numeric-candidate-v35-*.json', 'diagnostic-centre-v35*'):
        assert not list(p.HERE.glob(pattern)), pattern
    assert not (p.HERE / 'centre-v35-integrity.json').exists()
    review = '''# Isolated v35 preparation — CLOSED static PASS, no field runtime

The prerequisite r3 runtime closure verified 1,617 historical evidence files,
16 protected files and four display files plus actual-exit0 closure receipts.
Both-leaf synthetic support permits testing this candidate; it does not prove
GPU field correctness or compiler attribution.

## Minimal candidate change

Four reversible source edits per candidate/reference: insert runtime bindings
`Math.fround(.20)` and `Math.fround(.28)`, add one separate uniform declaration,
and replace only the child axial/angular second offsets with those uniforms.
Uniform binary32 words are 0x3e4ccccd and 0x3e8f5c29. Every other shader byte,
shape/material/colour, certificate, marcher and frame integration is unchanged.
The unshared cost reference retains exactly its original one-call difference.
No cached shader text or ad-hoc material path omits the new bindings.

## Frozen static evidence

- 18 derived files reproduced exactly from frozen v34 sources, version-only
  except the four candidate/reference edits and a preparation-closure receipt
  prerequisite in the runtime gate. Scalar oracle and Hessian/CSG mathematics,
  bounds, numerical, fixed-reference, independent-root and cost code unchanged.
- AST/JS syntax PASS. Seventeen durable Node stages include six actual-source
  construction paths (candidate, unshared reference, GPU rays, GPU leaves,
  both cost arms), both detail modes and 36 rejected binding/declaration/use
  regressions. HTML paths execute with Three stubs, including fail-closed
  shader callbacks; resulting instrumented shaders reverse exactly to v34.
- Prior CSG, lifecycle and launcher contract evidence inherited by exact
  version-only source equivalence and verified receipts, not replayed. No
  claim that mock draws compile GLSL or validate GPU rounding.
- All 48 cases / 75,996 rays, exact expanded/composite/normal/cheap-full replay,
  original 720 fixed references plus 720 independent first roots, and 12 balanced
  shared/unshared cost pairs retained. Original renderer is version-only:
  1200x800 HIGH/90s waits, native controls and prior acceptance untouched.

## Original root failure remains open

Existing local float64 profiles establish two crossings per failed ray inside
one .003 grid cell: width bounds .00088364 (839), .000587943 (745), and
.000864969 (807/809). This supports local scan-resolution evidence only,
not earliest-root certification, GPU-ray equivalence or unique components.
The four failures and original exact-jet failures remain immutable.

No root algorithm has changed in v35. Prepare a DISTINCT additive strict root
fixture before field runtime: preserve original scans/results, retain all 720
requirements and require explicit brackets AND unchanged independent global
first-root certificates. Do not choose the nearest root or relabel a missing
reference as a pass. Design/review/static closure is the next bounded task.

No browser, field samples, roots, cost, capture, PNG, image inspection or desktop
acceptance ran in this preparation. No live promotion. latest.png remains the
inspected REJECTED GAME v33r6 entry, not a v35 render. All19 unfinished.
'''
    p.write(p.PREFIX + '-preparation-review.md', review)
    archives = {}
    for name in ('NOTES.md', 'README.md', 'status.txt'):
        archive = name + '-before-centre-v35-preparation'
        p.write(archive, (p.HERE / name).read_bytes()); archives[archive] = p.digest(archive)
    old_notes = (p.HERE / 'NOTES.md').read_text(encoding='utf-8-sig')
    assert old_notes.count('## Exact next bounded work') == 1
    notes = old_notes[:old_notes.index('## Exact next bounded work')]
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — isolated v35 preparation CLOSED static PASS', 1)
    notes += '''## Isolated v35 preparation CLOSED — static PASS, no field runtime
- Verified r3 runtime1617 evidence/16protected/4display and actual-exit0 closure receipts. New v35 candidate/reference change only two second-offset literals to runtime uniforms, one declaration and exact binary32 bindings (.20/.28). Four reversible edits restore each v34 source byte-for-byte; unshared reference retains exactly one full-trace call difference. Shape/material/march/frame-pump unchanged.
- Frozen18derived files plus preparation controls before static. Foreground build/static actual exit0. Seventeen durable Node stages PASS; six actual-source constructor/fixture paths checked HIGH/LOW and36binding/declaration/use negative cases. AST/JS and full instrumented shader reversal PASS. Prior CSG/lifecycle/launcher contracts inherited through exact version-only source equivalence, not replayed. No actual GLSL or GPU claim.
- Scalar oracle/Hessian/CSG,48cases/75996rays,exact expanded/composite/normal/cheap-full jets,720fixed+720independent roots,12balanced cost pairs and original renderer unchanged. Runtime gate additionally requires actual preparation closure receipts. Frozen v34/v35 evidence immutable. No field/browser/root/cost/capture/acceptance run,new image/inspection or promotion.
- Existing four local CPU-profile crossing pairs inside old .003 cells guide a DISTINCT additive root-isolation fixture next; no root algorithm changed here, no earliest-root proof. Original exact-jet/716-of-720 failures remain. centre-v35-fixture-integrity.json binds preparation/historical/protected/current display. Prior display archived; NOTES once/BOM retained. latest unchanged inspected REJECTED GAME v33r6;all19 unfinished.

## Exact next bounded work
''' + NEXT + '\n'
    readme = (p.HERE / 'README.md').read_text()
    readme += '\nIsolated [v35 uniform-offset preparation](centre-v35-preparation-review.md) is **CLOSED static PASS; no field runtime**. Six HIGH/LOW binding paths and exact source/shader reversal pass. All original numerical/root/cost/capture gates retained; original failures remain. Next: distinct additive strict root-isolation design and static preparation. No new image or promotion; latest remains inspected REJECTED GAME v33r6.\n'
    (p.HERE / 'README.md').write_text(readme)
    (p.HERE / 'status.txt').write_text(STATUS + '\n')
    (p.HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
    p.frozen(display=False)
    assert p.digest('latest.png') == prior['display']['latest.png']
    files = dict(prior['files']); files[p.HISTORY] = p.digest(p.HISTORY)
    stem = 'centre-v34-staged-arithmetic-r3-runtime-close-once'
    for suffix in ('-launch.json', '-exit.json', '.log'):
        files[stem + suffix] = p.digest(stem + suffix)
    files.update(freeze['sources']); files.update(archives)
    for path in p.HERE.glob(p.PREFIX + '-*'):
        if path.is_file() and path.name != 'centre-v35-close-once.log':
            files[path.name] = p.digest(path.name)
    p.save(p.PREFIX + '-fixture-integrity.json', {
        'files': files, 'protected': prior['protected'],
        'display': {name: p.digest(name) for name in prior['display']},
        'prior_display': prior['display'], 'archived_display': archives,
        'static_passed': True, 'fixtures_complete': True, 'numerical_run': False,
        'numeric_passed': False, 'first_root_certified': False, 'capture_permitted': False,
        'new_images': 0, 'next': NEXT,
    })
    print('Saved-only v35 preparation CLOSED; no numerical or visual pass')


if __name__ == '__main__':
    main()
