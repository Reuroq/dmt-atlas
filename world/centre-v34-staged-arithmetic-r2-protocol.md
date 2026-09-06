# Distinct staged synthetic arithmetic — preparation only

Reuses the immutable followup seeds and 128×2 RGBA32F texture, including all
selected empty inverse cells, neighbours, subnormals, cancellation and padding.
These are synthetic predecessors, not recovered GPU intermediates. No old probe
is edited/retried. No actual-field numerical, root, cost, image or acceptance run.

One browser, texture and float render target; known float control first, then
childAxial literal/uniform and childAngular literal/uniform. The arithmetic shader
function is byte-identical to the old source. Only the second-offset expression
differs between arms. Runtime uniforms contain the same binary32 .20/.28 values.

## Evidence and stopping rules

Every operation has durable hash-chained intent, result, assessment events. The
full result is fsynced BEFORE CPU validation. Each GL interval records bounded
pre/post error queues, exceptions and context loss; dirty preconditions do not
execute. A Three operation is an interval, not localization of its internal calls.
Framebuffer status/binding/attachment/read-format/type, original shader strings,
runtime uniforms, shared texture values/bits and hashes, program link/log,
shader source/log/compile status and browser warnings/errors are preserved.

Both full 512-component Three/raw readbacks include values, binary32 bits and
sentinels. Nonfinite, partial/unwritten, malformed, value/bit inconsistency,
Three/raw disagreement, failed known-float control, shader/link/GL/context errors
are fatal; durable evidence survives. Bits preserve signed zero even when JSON
numeric serialization loses it. Expected texture bits validate the shared input.

Arithmetic mismatches are saved and do NOT stop other independent arms. Compare
against separately rounded binary32 CPU additions, plus child against the saved
microprobe parent plus c2; the folded channel is only a diagnostic control.
All 128 outputs are compared and retained, including padding. As in the original
criterion, support uses the labelled unique inputs, with both readback methods:
for BOTH leaves literal child-vs-parent must fail while predecessor, parent and
folded channels are bit-exact; uniform must be bit-exact in all four channels
and in child-vs-parent replay. No epsilon, filtering or post-readback correction.
Complete/clean diagnostic exit0 does not imply support; support is a separate flag.

`getTranslatedShaderSource` and `WEBGL_debug_shaders` are deliberately omitted.
The closed GL-localization run isolated eight GL1282 calls to these queries on
deletion-marked shader handles, with explicit driver warnings. That finding does
not prove the old arithmetic error's cause or any compiler arithmetic hypothesis.
Translated text is optional and unnecessary for exact arithmetic comparisons.
No Three internals change, no error is cleared without recording. Console warnings
remain saved; like the original arithmetic protocol, warnings alone are not fatal.
Page/console errors prevent clean completion and support. Resource disposal and
page/browser closure are recorded on normal completion and caught failures.
Hard kill/storage failure can leave incomplete evidence; never retry it.

## Freeze and separate runtime boundary

Freeze all new sources, protocol, immutable input sources and localization closure.
Static checks only: AST/JS parsing, exact shader provenance, plan ordering, mock
operation/error/exception/transport handling, independent CPU expectations,
mismatch continuation, both-leaf criterion, exclusive receipts/replay refusal.
No Chromium, GLSL compilation or GPU arithmetic during preparation.

After static preparation closes, a separately bounded foreground phase may use
`python3 -B world/run_centre_v34_staged_arithmetic_r2_once.py runtime` ONCE, after
verifying the new preparation manifest and static/close receipts. Sources and
partial/completed attempts remain immutable. Do not call old preparation gates
whose display snapshots were superseded. Runtime must be reviewed from saved
evidence before any inference or further candidate preparation.

Even synthetic support can only justify considering an isolated v35; it certifies
no field equality or roots. Original exact-jet/716-of-720 reference failures and
downstream blocks remain. All19 RECOGNISE/source/coverage/route/full acceptance
remain unfinished. Live/default/ledger and latest rejected GAME image unchanged.

## Revision 2 static observability and repair

The frozen first attempt is immutable. Its HTML lacks arithmeticStep. This
revision inserts only the existing GL-localization operation wrapper, renamed;
shader, plan, input and support/assessment/runtime-loop functions are unchanged.
The checker proves HTML insertion-only and Python function AST identity.
Before interpreting every Node status, exclusive source, argv/hash, stdout,
stderr and actual-exit receipts are fsynced. A separate original-source mock
reproduction must fail specifically at the missing API; it does not recover
the lost historical stderr. Independent stages name API, GL errors, exception,
bounded drain, context loss, packing, shaders, materials and readbacks. The
original combined mock and all original Python static requirements still run.
Freeze/static only in this phase. No GPU or browser until separate runtime.
