# v33r6 implementation CLOSED — runtime pending

## Isolated shader change

`jc` previously invoked separate sine/cosine helpers, each doing identical angle
reduction, fold comparisons and squaring. A new `preciseSinCos` computes that
shared prefix once and evaluates the two original Horner polynomials unchanged.
The cosine sign assignments have no dependency on the sine result. Two edits
reverse exactly to v33r5. Everything after `jc`, including field expressions,
gradients, material/shading, certificates, marcher budgets and hit acceptance,
is byte-identical. Existing standalone sin/cos functions remain unchanged.
No frame-pump, camera, movement, source or live-default change.

This is substantive shared arithmetic/control factoring, not an identifier-only
retry. Its benefit is unmeasured: the compiler may already eliminate duplicated
work, and new code shape/register use may worsen cost. No speedup is claimed.

## Offline evidence

Source dependency-graph checks and exact reversal PASS; the independent scalar
oracle is byte-identical. 26,149 boundary/seeded JavaScript float64 inputs,
including signed zero, matched both original outputs bit-for-bit. JS/AST and
fixture derivation checks PASS. This is NOT GLSL compilation or float32 evidence.
Bounds inherit the prior sampled checks through expression equivalence; zero
new bounds runs. New unchanged 48-case/75,996-ray GPU and 720-fixed/720-interval
root fixtures are prepared, not run. All actual GPU/compiler gates remain open.

## Cost-runner lifecycle

The new candidate is compared against v33r3 using the same 12 balanced pairs,
dimensions, four readbacks, JS/outer timing boundaries and acceptance formulas.
Per-arm start is fsync'd before the first outer clock; completion saves the full
result after the second clock and before the next arm. Exceptions and catchable
SIGTERM/SIGHUP/SIGINT save failure events. Page setup, browser close, partial raw
summary and review-ready events provide additional lifecycle evidence. All new
receipt I/O is outside timing; it can still perturb between-arm host/cache/queue
state. No warmup, new timeout, watchdog, frame-pump edit or preconditioning.

Offline checks PASS for clock/I/O order, result roundtrip, replay rejection,
exception/interrupt/signal propagation and actual self-SIGTERM with handler
restoration. No browser was launched. SIGKILL, container loss, repeated signals
or storage failure cannot guarantee a terminal receipt. A last started event
without completion means INCOMPLETE/unknown, never an inferred slowdown.

## Held state / next gate

v33r5 numerical PASS and its interrupted cost evidence remain unchanged and
must not be replayed. v33r6 numerical/cost/capture are NOT RUN. The renderer is
version-only equivalent to the original v33r3 renderer and remains blocked.
No new PNG, inspection, visual grade, source/coverage update or promotion.
latest.png remains the labelled REJECTED GAME v32 deep-motion image; this is
not new visual progress. All19 realism and remaining source/coverage/route/full
acceptance remain unfinished. No completion marker.

Run probe_numeric_candidate_v33r6.py ONCE with a unique saved log; wait for actual exit before checkpointing. Only PASS permits audit_centre_v33r6_first_roots.py ONCE, then measure_centre_v33r6_cost.py ONCE with its per-arm lifecycle journal. Environment: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. No bounds rerun. Preserve48cases/75996rays/720fixed+720interval roots and12balanced cost pairs against v33r3, unchanged hit/count/prefix/total-and-median wall gates. Inspect every exit/receipt; do not replay partial attempts. Only numerical+cost PASS permits creating centre-v33r6-integrity.json (integrity_passed,numeric_passed,capture_cost_gate_passed,files,protected) and the version-only original1200x800 HIGH/90000ms render ONCE. No prewarm, frame-pump change, relaxed gates or promotion.
