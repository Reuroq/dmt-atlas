# Isolated v35r2 preparation — CLOSED static PASS, no field runtime

The prerequisite r3 runtime closure verified 1,617 historical evidence files,
16 protected files and four display files plus actual-exit0 closure receipts.
Both-leaf synthetic support permits testing this candidate; it does not prove
GPU field correctness or compiler attribution.

## Minimal candidate change

The first frozen v35 static run exited1 at its declaration-reversal checker:
instrumentation adds probeMode to the existing declaration. All six binding
paths had passed, but the complete static gate had not. Its source, receipts
and outputs are preserved in centre-v35-preparation-failure.json. This distinct
v35r2 successor corrects only that checker reversal to remove the inserted
line, not the existing instrumented declaration. Runtime sources are
version-only equivalents of the unexecuted v35 candidate/fixtures.

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

No root algorithm has changed in v35r2. Prepare a DISTINCT additive strict root
fixture before field runtime: preserve original scans/results, retain all 720
requirements and require explicit brackets AND unchanged independent global
first-root certificates. Do not choose the nearest root or relabel a missing
reference as a pass. Design/review/static closure is the next bounded task.

No browser, field samples, roots, cost, capture, PNG, image inspection or desktop
acceptance ran in this preparation. No live promotion. latest.png remains the
inspected REJECTED GAME v33r6 entry, not a v35r2 render. All19 unfinished.
