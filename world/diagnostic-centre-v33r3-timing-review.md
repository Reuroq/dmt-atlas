# v33r3 timing diagnostic — asynchronous completion delay; HIGH gate still FAIL

The changed instrumented diagnostic ran ONCE, exit1, at 1200×800 HIGH with the
original 90000ms entry-settle limit. It timed out after 90.022001s.
Native navigation/pause only; no screenshots, browser errors, extra GPU queries,
blocking readbacks, gl.finish, scheduling changes or acceptance bypass.

## Observations

| Submission | Stage / animation clock | Synchronous compositor call | Fence age at observed retirement |
| --- | --- | ---: | ---: |
| 1 | Onset / −0.0255 | 145.2ms | 796.4ms |
| 2 | Onset / 0.9578 | 18.0ms | 1434.8ms |
| 3 | Chrysanthemum / 2.4077 | 28.7ms | 90635.9ms |
| 4 | Chrysanthemum, paused / 3.5242 | 1.2ms | Not retired; age1080.6ms at export |

Submission3's synchronous scene call was24.8ms; blur-horizontal0.4ms,
blur-vertical2.7ms and finish0.3ms. Flush returned within timestamp resolution.
These measure CPU-facing call boundaries, **not per-pass GPU durations**.

At the pre-settle checkpoint, submission3 owned the fence; the view was paused
at clock3.5242 with a pending redraw for that newer clock. The trace contains
538 records with zero ring/stream drops. Across the run,5495 nonblocking fence
polls returned TIMEOUT_EXPIRED and3 returned CONDITION_SATISFIED; no WAIT_FAILED.
After pause,89 sampled decisions all saw a fence,88 also saw invalidation;
89 sampled polls returned timeout (maximum call8.6ms). **No invalidation setter
events recurred after pause.** The existing queued invalidation was retained
while submission3 was pending, then served promptly when it retired. The final
state was invalidated=false,fence=true with submitted clock equal to paused clock.

## Interpretation and limits

The observed wait is dominated by asynchronous completion of submission3,
not a90s synchronous JavaScript compositor call or recurring-invalidation
starvation. The held invalidation was legitimate: it requested the paused view
after an earlier animation frame. The frame pump should not be changed on this
evidence. Fence timing includes driver/queue/completion/polling latency and the
whole composite, not an isolated shader timer. Cold asynchronous shader/pipeline
compilation is **not separated** from steady-state GPU execution; submission4
did not finish before the deadline. This trace cannot attribute all90s to marcher
arithmetic, prove a driver fault, or predict hardware-GPU performance.

Timestamps, sampled console streaming and checkpoint serialization perturb the
run. The clocks differ from the prior uninstrumented failed capture; this is not
a matched speed comparison. Negative initial onset clock is recorded unchanged,
not injected or corrected. No speedup, visual grade or full-acceptance credit.

The two instrumented JS files are insertion-only. Removing marked additions
recovers trip.js/fractal.js byte-for-byte; original readiness and WAIT_FAILED
semantics remain untouched. The v33r3 candidate shader is unchanged. Live code,
17 protected files, defaults and ledgers remain unchanged. latest.png remains
the inspected labelled REJECTED GAME v32 deep-motion image. No new image to inspect.

## Next bounded work

Build one isolated common-prefix reuse candidate from unchanged v33r3, not from timing copies: cheapParts and fieldPartsReach repeat the rotated Cartesian/radius/inverse/cube jets at the same p whenever the cheap certificate fails. Share those unchanged intermediates between cheap and full evaluation without changing scalar/materials, certificates, thresholds, budgets, brackets or rendering controls. Treat this as an unproven shader-work/complexity hypothesis: the timing trace does not separate cold asynchronous compilation from steady-state execution, and extra live intermediates may increase register cost. Before any fresh capture, independently revalidate cheap/full jets, conservative reaches, clearance and first roots on HIGH/LOW entry/deep including historical4.895 and observed2.4077/3.5242 clocks; compare matched numerical work/cost without asserting sparse-ray wall time predicts full-resolution performance. Then run a substantively changed candidate ONCE at original1200x800 HIGH/90s using native controls. Do not modify the frame pump, prewarm/bypass acceptance, relax limits or replay closed probes/captures. If reuse fails correctness or worsens measured work, record failure without promotion.

All19 realism, remaining16 source gates, coverage, route and full acceptance remain unfinished.
