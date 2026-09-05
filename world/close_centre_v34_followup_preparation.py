"""Close preparation only after saved static/actual-exit receipts; no runtime."""
from centre_v34_followup_common import HERE, PREFIX, HISTORY, read, save, digest, historical, frozen, receipt, verify


def main():
    history = historical()
    inputs = frozen()
    receipt('prepare'); receipt('static')
    check = read(PREFIX + '-static-check.json')
    assert check['static_passed'] and check['new_field_samples'] == check['new_browser_runs'] == 0
    assert check['inputs_sha256'] == digest(PREFIX + '-inputs.json')
    archive = 'NOTES-before-centre-v34-followup-preparation.md'
    result_name = PREFIX + '-preparation-integrity.json'
    assert not (HERE / archive).exists() and not (HERE / result_name).exists()
    assert not list(HERE.glob(PREFIX + '-arithmetic*'))
    assert not list(HERE.glob(PREFIX + '-profiles*'))
    original = (HERE / 'NOTES.md').read_bytes()
    assert original.startswith(b'\xef\xbb\xbf')
    notes = original.decode('utf-8-sig')
    marker = '## Exact next bounded work\n'
    assert notes.count(marker) == 1
    assert notes.startswith('# Active: REDIRECT4 — v34 saved investigation CLOSED; two new diagnostics designed')
    assert (HERE/'status.txt').read_text().startswith('Isolated v34 remains numerical FAIL; saved-only investigation CLOSED:')
    notes = notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v34 follow-up preparation CLOSED; diagnostics ready, not run', 1)
    notes = notes.split(marker)[0] + '''## v34 distinct follow-up preparation CLOSED — static PASS, no runtime
- New centre-v34-followup-* frozen inputs and one-shot foreground launcher are separate from every completed v34 probe. Synthetic texture <=128 finite binary32 predecessors/leaf includes 12 deterministically selected saved mismatch cells, representable endpoints/midpoint and neighbours, cancellation/domain endpoints. Empty representable cells reported; no recovered GPU-intermediate claim.
- Arithmetic runner records literal/runtime-uniform arms, full 128texel readbacks/bits and folded diagnostic control, exact separately rounded CPU and saved-microprobe-parent replay, shader/link/backend/lifecycle/close evidence. Candidate support requires literal scalar-only failure plus exact uniform arm for BOTH leaves; no epsilon/correction. All failures retained. Optional translated shader text; synthetic result never replaces actual-field gates.
- Four-ray float64 oracle profiles:161 depths at savedGPUdepth±.004/.00005 plus actual savedGPUpoint separately; full/11leaves/branch and active labels preserved. Every observed full/leaf strict bracket receives24bisections with complete midpoint profiles, signs, zeros, widths and entering/exiting orientation. Minima/sign/leaf/branch changes saved. Old .003 grid compared by indices only; no old scan/first-root claim.
- prepare/static/close use unique foreground launch/log/actual-exit receipts. Static checks include AST/JS/exact single-offset shader transform, frozen texture/ray checks, synthetic one-ULP rejection, bracket/zero/24bisection/grid contracts and actual synthetic launcher exit7/replay refusal. Zero field/browser/GLSL/cost/capture/acceptance runs; no new image or v35 candidate. Original numerical FAIL and blocked gates retained.
- Preparation integrity binds all frozen scripts/inputs/static results/receipts/historical349/protected16/display4;runtime also requires actual closure exit0. README/status current;latest unchanged inspected REJECTED GAME v33r6 entry. NOTES updated once/BOM retained/prior bytes archived;live/defaults/ledgers unchanged.

## Exact next bounded work
Run the NEW diagnostics once in foreground: python3 -B world/run_centre_v34_followup_once.py arithmetic then profiles (independent; arithmetic failure does not waive or require skipping profiles). Inspect saved complete results and actual exits;never rerun preparation/static/closure or a partial diagnostic. No v34 replay/dependent roots/cost/capture. If literal fails and uniform is exact for BOTH leaves under the recorded support criterion, prepare isolated v35 second-offset-uniform candidate and NEW unchanged full-gate fixtures/static review before runtime;otherwise no claimed fix. Local profiles remain local evidence;unbracketed rays unresolved and all first-root/original reference requirements intact. All19/source/coverage/route/full acceptance unfinished;no WORLD_DONE.
'''
    seeds = read(PREFIX + '-seeds.json')
    summary = [(leaf['name'], leaf['count'], len(leaf['all_no_binary32_flat_rays'])) for leaf in seeds['leaves']]
    review = '''# v34 distinct follow-up preparation — static closure only

New inputs and runners implement the two designed diagnostics; no GPU, GLSL,
field evaluation, old scan, independent first-root gate, cost, render or acceptance ran.
The original v34 numerical FAIL remains; no v35 candidate exists.

## Frozen inputs

Leaf / unique binary32 inputs / saved-pair outer cells with no binary32 predecessor:
''' + '\n'.join('- ' + str(row) for row in summary) + '''

Each leaf selects 12 evenly indexed historical mismatches BEFORE checking
representability. Selected empty cells are retained, and all empty-cell flat IDs
are saved. Nonempty cells supply low/middle/high representable values and binary32
neighbours; domain ends, cancellation points and zero have neighbours too.
Closed inverse cells overapproximate tie boundaries. These are synthetic seeds,
not recovered GPU intermediates or compiler evidence. Texture is little-endian
RGBA32F, 128×2; padding is +0, recorded but not part of the unique input count.

Four complete saved identities/points/depths/CPU rays and the unchanged float64
oracle hash are frozen. The 161-point local grid is new, not the failed forward scan.
All eleven leaf brackets AND full-field brackets are refined, including exits.
Exact midpoint zeros are retained as zero endpoints while completing24bisections;
the original strict bracket, every midpoint profile and final endpoint signs remain.
No bracket means unresolved. Algebraic grid enclosure requires two observed full
crossings; this does not isolate a unique negative component or exclude earlier roots.

## Static checks

''' + '\n'.join('- ' + item for item in check['checks']) + '''

## Runtime boundary and interpretation

`python3 -B world/run_centre_v34_followup_once.py arithmetic`

`python3 -B world/run_centre_v34_followup_once.py profiles`

Both are NEW, independent, one-shot foreground runs. Runtime verifies this
closure, frozen inputs/sources, historical/protected/display hashes and actual
prepare/static/close exit0 receipts. Partial attempts are never replayed. A hard
kill or storage failure can leave an unknown partial cause; no automatic retry.

Arithmetic uses bundled Three160, highp and the original Chromium/SwiftShader
flags. Shared texture/target/browser; only second-offset literal becomes uniform.
All readback texels and bits, shader/link logs, original/generated and optional
translated GLSL, errors and resource/browser close events are retained. Exact
comparisons are bitwise (numeric counts also retained); no epsilon or correction.
The explicit folded expression is a diagnostic, never a replacement child oracle.
Subnormals/cancellation failures are retained, not filtered away.

The conservative support criterion requires literal child-vs-parent failure,
exact literal predecessor/parent/folded control, and exact uniform outputs plus
saved-microprobe-parent replay for BOTH leaves. Otherwise no supported candidate.
Synthetic support justifies preparation only: all48cases/75996rays, actual-field
expanded/composite/normal/cheap-full exactness, original tolerances/budgets and
fixed/independent first-root gates remain required. No geometry/material/colour,
frame pump, live/default/ledger or original gate changed. latest remains the
once-inspected REJECTED GAME v33r6 entry. All19 acceptance remains unfinished.
'''
    readme = (HERE / 'README.md').read_text()
    old_line = next(line for line in readme.splitlines() if line.startswith('Isolated **v34 numerical phase CLOSED — FAIL**.'))
    new_line = old_line + ' [Distinct diagnostic preparation](centre-v34-followup-preparation-review.md) is now static-checked with frozen inputs and one-shot runners; both runtime experiments remain NOT RUN. No acceptance or realism pass.'
    with (HERE / archive).open('xb') as stream:
        stream.write(original)
    with (HERE / (PREFIX + '-preparation-review.md')).open('x') as stream:
        stream.write(review)
    (HERE / 'README.md').write_text(readme.replace(old_line, new_line, 1))
    (HERE / 'status.txt').write_text('Isolated v34 numerical FAIL retained. NEW distinct follow-up preparation CLOSED: synthetic literal/uniform offset microprobe and four-ray local profiles frozen/static PASS; both runtime experiments NOT RUN. No v35 candidate, v34 replay, dependent roots/cost/capture or acceptance rerun. latest.png unchanged inspected REJECTED GAME v33r6 entry. Live/defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
    (HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
    names = [PREFIX + x for x in ['-inputs.json', '-static-check.json', '-static-started.json', '-preparation-review.md']]
    names += [PREFIX + '-' + label + '-once' + suffix for label in ['prepare', 'static'] for suffix in ['-launch.json', '-exit.json', '.log']]
    names += [archive, HISTORY]
    result = {'static_passed': True, 'numeric_passed': False, 'capture_permitted': False,
        'phase': 'Preparation CLOSED; NEW experiments NOT RUN', 'files': {**history['files'], **inputs['files'], **{n:digest(n) for n in names}},
        'protected': history['protected'], 'display': {name:digest(name) for name in history['display']},
        'prior_display': history['display'], 'new_field_samples': 0, 'new_browser_runs': 0, 'new_images': 0}
    assert result['display']['latest.png'] == history['display']['latest.png']
    verify(result['files']); verify(result['protected']); verify(result['display'])
    save(result_name, result)
    print('Preparation CLOSED static PASS; new diagnostics NOT RUN; numeric FAIL unchanged', flush=True)


if __name__ == '__main__':
    main()
