# GL localization runtime CLOSED — exact controls; translated-query errors

The frozen foreground launcher ran ONCE and returned actual exit **1**, with no
launcher exception. All 117 stages completed. The saved-only reviewer returned
exit0 after verifying receipts, source/preparation bindings, all 358 hash-chained
events, ordered intent/result/assessment triples and clean resource/browser close.
The review's success does not replace the diagnostic's failure.

## Observed evidence

- Byte constant, float constant, float texture row0 and row1 each produced exact
  512-component Three and raw readbacks: eight arrays, 4096 components, including
  exact binary32 bits. No sentinel remained. All eight framebuffer status checks
  were COMPLETE. Setup, compilation, rendering and readback intervals were clean.
- All programs linked. Both shader handles in each program returned isShader=true,
  DELETE_STATUS=true and COMPILE_STATUS=true without GL errors. Shader source/log
  queries were clean. Being marked for deletion did not invalidate every query.
- Only the eight individual getTranslatedShaderSource calls raised GL1282. Each
  began with an empty error queue, returned an empty string and ended with [1282].
  Eight browser warnings explicitly say "attempt to use a deleted object".
  Four readPixels stall warnings and one Three deprecation warning also survive.
- Backend: WebGL2 / ANGLE Vulkan SwiftShader, fragment highp precision23. No
  context loss, exception, dirty precondition or shader-error callback occurred.
- 109 stages classified ok; eight classified query-error. complete=true but
  infrastructure_clean=false. No error was waived, cleared without recording,
  or converted into a passing arithmetic result.

## What this establishes, and does not

In THIS new diagnostic the GL1282 operation is localized to translated-source
queries on deletion-marked Three shader objects, supported by driver warnings.
The older arithmetic probe's final error check did not preserve operation-local
evidence. This is a concrete explanation to investigate there, not proof that its
render/readback was otherwise correct or that it had only this error source.
No translated compiler text was recovered; no constant-folding conclusion follows.

The original arithmetic attempt remains immutable/incomplete. The controls test
transport of known texels, not either child leaf. Uniform support remains false;
original expanded-jet and716/720 reference failures remain. No new candidate,
independent first-root certification, cost run, capture, image or acceptance run.
latest.png remains the once-inspected REJECTED GAME v33r6 entry.

## Next bounded phase: prepare a distinct staged arithmetic diagnostic

Use new filenames; never edit or retry any frozen/completed probe. Read only the
old arithmetic sources and experiment design needed to preserve the synthetic
inputs, exact separately rounded CPU comparison and literal/uniform hypotheses.
Keep this distinct from an actual-field numerical rerun.

Port durable staged pre/post errors, framebuffer evidence and before-assessment
full Three/raw readback values/bits to BOTH leaf/literal/uniform arms, with a known
float control first. Preserve shader sources, uniforms, input texture hashes and
program link evidence. Exclude optional translated-source queries from this new
arithmetic protocol, explicitly documenting their absence and this localization
result; they are not prerequisites for arithmetic evidence. Do not change Three
internals or silently suppress GL errors. Core errors/invalid readbacks halt with
saved evidence; arithmetic mismatches are recorded and allow the other independent
arm to be measured. Preserve finite/sentinel/bit checks and literal-control gates.

Require the existing exact support criterion for BOTH leaves, not an epsilon or
one passing arm. Freeze sources and statically verify staged ordering, independent
expected arithmetic, error/exception evidence, mismatch continuation versus fatal
infrastructure handling, and replay refusal before a separately bounded one-shot
foreground runtime phase. No runtime in that preparation phase. Even synthetic
support would only justify considering v35; it cannot certify field roots or
visual realism. All19/source/coverage/route/full acceptance remain unfinished.
