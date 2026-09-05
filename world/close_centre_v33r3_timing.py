"""Close the one-shot timing phase; preserve live code, images and prior evidence."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r3-timing'
OUT = HERE / 'centre-v33r3-timing-integrity.json'
assert not OUT.exists()

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def read(name):
    return json.loads((HERE / name).read_text())

parent = read('centre-v33r3-capture-integrity.json')
build = read(PREFIX + '-build.json')
s = read(PREFIX + '-receipts.json')
a = read(PREFIX + '-analysis.json')
for hashes in [parent['files'], parent['protected'], parent['display'], build['files']]:
    assert all(digest(n) == h for n, h in hashes.items())
assert digest(PREFIX + '-receipts.json') == a['receipt_sha256']
assert not s['settle_passed'] and s['protected_unchanged'] and s['source_unchanged']
assert s['failure']['operation'] == 'entry settle'
assert 'Timeout 90000ms exceeded' in s['failure']['exception']
assert not s['errors'] and not a['open_intervals']
assert a['trace_records'] == 538 and a['trace_dropped'] == 0
assert s['new_images'] == 0 and not list(HERE.glob(PREFIX + '*.png'))
assert a['final']['paused'] and a['final']['detail'] == 'high'
assert a['final']['position'] == [0, 1.7, 8] and a['final']['yaw'] == a['final']['pitch'] == 0
assert not a['after_pause']['invalidation_events']
assert a['raw_counts'].get('fence-result:37149', 0) == 0
assert not a['timing_state']['invalidated'] and a['timing_state']['fence']
assert digest('latest.png') == digest('diagnostic-centre-v32-deep-motion.png')
assert (HERE / 'status.txt').read_text().startswith('Isolated v33r3 HIGH CAPTURE FAIL:')
for name in ['build_centre_v33r3_timing.py', 'run_centre_v33r3_timing.py',
             'analyze_centre_v33r3_timing.py', Path(__file__).name]:
    ast.parse((HERE / name).read_text())

next_work = (
    'Build one isolated common-prefix reuse candidate from unchanged v33r3, not from timing copies: '
    'cheapParts and fieldPartsReach repeat the rotated Cartesian/radius/inverse/cube jets at the same p '
    'whenever the cheap certificate fails. Share those unchanged intermediates between cheap and full '
    'evaluation without changing scalar/materials, certificates, thresholds, budgets, brackets or rendering controls. '
    'Treat this as an unproven shader-work/complexity hypothesis: the timing trace does not separate cold asynchronous '
    'compilation from steady-state execution, and extra live intermediates may increase register cost. '
    'Before any fresh capture, independently revalidate cheap/full jets, conservative reaches, clearance and '
    'first roots on HIGH/LOW entry/deep including historical4.895 and observed2.4077/3.5242 clocks; '
    'compare matched numerical work/cost without asserting sparse-ray wall time predicts full-resolution performance. '
    'Then run a substantively changed candidate ONCE at original1200x800 HIGH/90s using native controls. '
    'Do not modify the frame pump, prewarm/bypass acceptance, relax limits or replay closed probes/captures. '
    'If reuse fails correctness or worsens measured work, record failure without promotion.'
)

review = f'''# v33r3 timing diagnostic — asynchronous completion delay; HIGH gate still FAIL

The changed instrumented diagnostic ran ONCE, exit1, at 1200×800 HIGH with the
original 90000ms entry-settle limit. It timed out after {a['failure_seconds']:.6f}s.
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

''' + next_work + '\n\nAll19 realism, remaining16 source gates, coverage, route and full acceptance remain unfinished.\n'

review_name = PREFIX + '-review.md'
assert not (HERE / review_name).exists()
(HERE / review_name).write_text(review)
notes_path = HERE / 'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE / 'NOTES-before-centre-v33r3-timing.md'
assert not archive.exists()
notes = original.decode('utf-8-sig')
notes = notes[:notes.index('## Exact next bounded work')]
notes = '# Active: REDIRECT4 — v33r3 timing CLOSED; asynchronous completion delay\n' + notes[notes.index('\n') + 1:]
notes += '''## v33r3 timing phase CLOSED — one run, no replay
- build_centre_v33r3_timing.py: insertion-only trip/fractal copies; marker removal restores originals byte-for-byte, JS/AST PASS. Shader/live/render decisions unchanged; bounded timestamps, counters and sampled console export only.
- run_centre_v33r3_timing.py ONCE exit1: original1200x800 HIGH/90000ms entry settle FAIL90.022001s.538 records,zero drops/errors/PNGs. Native controls only. No screenshot inspection or latest change.
- Chrysanthemum submission3 at2.4077 returned28.7ms(scene24.8ms),fence retired after90635.9ms. Paused clock3.5242 retained a legitimate queued redraw;zero invalidation events after pause.5495 raw timeout polls,3condition-satisfied,no WAIT_FAILED.89post-pause decision samples all pending-fence,88invalidated.
- Submission4 at paused3.5242 returned1.2ms promptly after fence3 retired. Final invalidated=false,fence=true,age1080.6ms;no open synchronous interval. Thus observed delay is asynchronous completion,not90s JS submission or recurring invalidation starvation. Do not change the frame pump on this evidence.
- Timing includes whole composite/driver/queue/polling;does NOT separate cold async compilation from steady-state execution or isolate marcher GPU cost. Instrumentation perturbs clocks;not matched benchmark,no speedup/realism credit. Review/analysis/receipts preserve evidence;centre-v33r3-timing-integrity.json binds files/protected/display. Prior NOTES archived in NOTES-before-centre-v33r3-timing.md.

## Exact next bounded work
''' + next_work + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'

readme_path = HERE / 'README.md'
readme = readme_path.read_text()
start = readme.index('Isolated **v33r3 two-tier marcher passes numerical checks but FAILS the')
end = readme.index('\n\nOld full defaults', start)
replacement = '''Isolated **v33r3 passes numerical checks but FAILS the original HIGH90s
entry gate**; visuals UNREVIEWED, no promotion. The one-shot instrumented timing
run also failed90.022s: first Chrysanthemum submission returned28.7ms but its
fence remained pending90.636s. No recurring invalidation after pause; the queued
paused frame submitted promptly on retirement. This isolates asynchronous
completion delay, not per-pass GPU cost or cold compilation versus execution.
No speedup established. See [numerical review](centre-v33r3-numerical-review.md),
[prior capture failure](diagnostic-centre-v33r3-review.md), and
[timing evidence](diagnostic-centre-v33r3-timing-review.md).
Next: isolated shared-jet-prefix optimization, independently revalidated before
one fresh original1200x800 HIGH/90s capture. No frame-pump change or limit relaxation.
Live/defaults/ledgers and latest inspected REJECTED GAME v32 diagnostic unchanged.'''
status = ('Isolated v33r3 timing CLOSED:HIGH entry FAIL90.022s;Chrysanthemum submission28.7ms,'
    'fence90635.9ms;no recurring invalidation after pause. Asynchronous completion delay,'
    'cold compilation vs execution unresolved.538records,zero drops/errors/PNGs. '
    'Next isolated common-prefix jet reuse with independent revalidation before fresh original1200x800 HIGH/90s capture. '
    'No frame-pump change,no speedup/realism claim,no promotion;latest.png remains inspected labelled REJECTED GAME v32 deep-motion. '
    'Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
readme_path.write_text(readme[:start] + replacement + readme[end:])
(HERE / 'status.txt').write_text(status)
archive.write_bytes(original)
notes_path.write_text(notes, encoding='utf-8-sig')
assert all(digest(n) == h for n, h in parent['protected'].items())
assert all(digest(n) == h for n, h in parent['files'].items())
files = set(parent['files']) | set(build['files']) | {
    'centre-v33r3-capture-integrity.json', PREFIX + '-build.json', PREFIX + '-receipts.json',
    PREFIX + '-analysis.json', review_name, 'run_centre_v33r3_timing.py', 'analyze_centre_v33r3_timing.py',
    'run-centre-v33r3-timing.log', archive.name, Path(__file__).name}
OUT.write_text(json.dumps({'integrity_passed': True, 'numeric_passed': True,
    'timing_run_count': 1, 'timing_renderer_exit_code': 1, 'capture_gate_passed': False,
    'visual_grade': 'UNREVIEWED', 'new_images': 0, 'inspections': 0,
    'protected': parent['protected'], 'files': {n: digest(n) for n in sorted(files)},
    'display': {n: digest(n) for n in ['README.md', 'status.txt', 'NOTES.md', 'latest.png']},
    'next': next_work}, indent=2) + '\n')
print('Timing phase CLOSED: one HIGH90s failure; asynchronous completion delay; all protected files unchanged.')
