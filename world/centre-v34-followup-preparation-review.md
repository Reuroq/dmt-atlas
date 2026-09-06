# v34 distinct follow-up preparation — static closure only

New inputs and runners implement the two designed diagnostics; no GPU, GLSL,
field evaluation, old scan, independent first-root gate, cost, render or acceptance ran.
The original v34 numerical FAIL remains; no v35 candidate exists.

## Frozen inputs

Leaf / unique binary32 inputs / saved-pair outer cells with no binary32 predecessor:
- ('childAxial', 55, 0)
- ('childAngular', 66, 0)

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

- Python AST; oracle imported only inside profile runtime
- Frozen binary texture, non-favourable cell selection records, neighbours, exact replay and one-ULP rejection
- Four ray identities/CPU directions; 161 depths; synthetic strict/exit/zero/24-bisection and algebraic-grid contracts
- Shader JS syntax and literal-to-uniform-only arms PASS; no GLSL or browser execution
- Actual foreground launcher synthetic exit7/log binding and replay refusal; no retry

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
