# Distinct infrastructure-only GL localization — preparation, NOT RUN

The old arithmetic attempt is immutable and must never be retried. Its final
GL1282 check spans too many operations to identify the source. Saved-source review
shows Three.js deletes its shader handles after linking and retains handles in the
program wrapper; this motivates lifetime queries but DOES NOT establish a cause.
No arithmetic expressions, leaf inputs, candidate geometry or journey code run here.

## Controls and ordering

One fresh Chromium/SwiftShader session, four independent target/material controls:
128x1 RGBA8 constant, RGBA32F constant, and two RGBA32F copies of separate rows of
a 128x2 nearest-filtered Float32 DataTexture. All expected components are exact
binary fractions; signed values, values above one and varying x/row test the path.
The original probe's target size, triangle plane, UV sampling and float texture
shape are retained. Byte and float readback buffers start with distinct sentinels.
Both Three readback and raw readPixels must match ALL 512 values and exact bits.

Each control stages object creation, target binding, framebuffer completeness,
binding/attachment/read-format/read-type evidence, compile, render, another
completeness check, Three readback and raw readback. Only then inspect linked
program and retained shader handles. Each shader isShader, DELETE_STATUS,
COMPILE_STATUS, log and source query gets its own recorded error interval.
Finally isolate WEBGL_debug_shaders extension acquisition and each translated
source query. An unavailable extension is explicitly skipped, not a failure.
An empty source is evidence, not compiler attribution. These constant/copy
shaders cannot supply either-leaf arithmetic support or authorize v35.

## Durability and failure policy

Python exclusively creates and fsyncs an intent before every browser step, then
the entire result before validation, then its classification. Events form a hash
chain. Each JS step records a bounded pre-error drain and post-error drain,
including every consumed nonzero code; errors are NEVER silently cleared.
A dirty precondition skips the operation and stops execution. Context loss,
undrained queue, core GL error, exception, shader callback, incomplete framebuffer
or exact-readback mismatch stops further controls, retaining the failing readback.
Only explicitly flagged read-only shader/debug queries may continue after a
fully drained error, with a recorded query-error classification and nonzero exit.
Three method intervals contain internal calls: they localize intervals, not an
individual internal GL call. The first renderer interval includes context setup.
The error-drain bound is 32; a non-drained queue is fatal. Disposal has its own
intent/result, then page/browser closure evidence. Abrupt termination leaves an
unanswered intent; it does not become a claimed completed operation.

One foreground launcher has exclusive launch/log/actual-exit receipts and a
180s timeout. Timeout records null actual_exit plus launcher failure, never a
fabricated child exit. Any launch/partial artifact prevents replay. Browser
messages are retained and preclude a clean result. An optional-query error can
coexist with a complete diagnostic, but not an infrastructure-clean result.

## Freeze/static review and scope

Freeze all new code/design plus bundled Three against the current runtime
integrity and closure receipt. Static validation uses AST/JS syntax, generated
plan and independent CPU controls, mocked stage error/throw/context handling,
one-bit/sentinel readback rejection and query-order checks. No browser or GLSL
compilation occurs during preparation. The preparation integrity binds the
freeze/static evidence, preserved historical/protected hashes and updated display
hashes; do not call the superseded follow-up runtime_gate().

Runtime, if continued in the next phase, uses only the new frozen launcher.
Review its durable evidence before designing any further experiment. No old
arithmetic/profile/scan replay, first-root/cost/capture/acceptance run, image or
promotion is included. Original numerical FAIL and all19 unfinished remain.
