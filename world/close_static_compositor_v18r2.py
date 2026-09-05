"""One-shot review closure after inspecting all three new r2 images once."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

p=Path(__file__).resolve().parent
prefix='diagnostic-static-compositor-v18r2'
assert not (p/'static-compositor-v18r2-integrity.json').exists()
def digest(name):return hashlib.sha256((p/name).read_bytes()).hexdigest()
d=json.loads((p/f'{prefix}.json').read_text())
assert not d['browser_errors'] and all(d['protected_unchanged'].values())
assert all(digest(n)==h for n,h in d['baseline'].items())
present,absent=d['cases']
failed=[x for x in present['comparisons'] if x['changed_pixels']]
assert len(failed)==2 and all(x['changed_pixels']==9457 and x['max_channel_delta']==1 for x in failed)
assert len(absent['comparisons'])==18 and not any(x['changed_pixels'] for x in absent['comparisons'])
def delta(stem):
    a=np.asarray(Image.open(p/(stem+'-before.png')).convert('RGB')).astype(np.int16)
    b=np.asarray(Image.open(p/(stem+'-after.png')).convert('RGB')).astype(np.int16)
    return b-a
new=delta(prefix+'-present-failure')
old=delta('accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness')
assert np.array_equal(new,old), 'Exact original signed difference not reproduced'
(p/'static-compositor-v18r2-review.md').write_text('''# Static compositor isolation — original pixel failure reproduced

Live v25 / trip v18 and all grades remain unchanged. Original HIGH strict
equality is still **FAIL**; this diagnostic establishes a correction target,
not acceptance or a runtime repair.

## Method and bounded results

- Immutable opaque 1200×800 bottom-up submission-v18 frame9 uploaded once as
  a nearest-sampled WebGL2 texture. Antialiasing remains enabled; no geometry
  shader, application navigation, clock, PBO readback or recurring render loop.
- Actual index.html HUD markup and trip.css, real detail clicks (HIGH/LOW/HIGH
  pixel ratios) and viewport resize/restoration. Simplified diagnostic handlers
  are not application acceptance. Native dimension and fence guards, 90000ms
  timeout, original 1000×380 crop and strict equality over 800ms remain.
- Six cycles per gradient-present/absent case: baseline, resize-restored and
  detail-restored comparisons. 36 pairs total; zero browser/GL errors.
- Present: 2/18 FAIL, at cycle3 baseline and resize-restored; both 9457 pixels,
  maximum channel delta1, crop bbox[411,277,1000,380]. First has 4853 positive
  and 4859 negative channel deltas; the second reverses the counts.
- Absent: 18/18 exact-equality PASS. Both cases submit25 static frames; every
  pair's before/after diagnostics (including submission list) are identical.
- The saved first static failure has the **exact same signed per-channel
  difference array** as the original live restored-detail failure, not just
  equal counts or bounding boxes. Historical images analyzed numerically only.

This reproduces the original failure signature without running the geometry
shader and with unchanged submissions during each failing interval. Removing
only the gradient background eliminates it in the bounded negative control.
The HUD gradient's browser presentation is therefore the demonstrated defect
site; internal tile dithering/raster-cache details are not established.

## Instrumentation / limitations

Passive CDP LayerTree events recorded153/147 tree updates, including updates
during comparisons. No layerPainted events were emitted. The gradient's final
1200×416 layer draws content with paintCount13 when present, and does not draw
content with paintCount0 when absent. Layer telemetry alone does not identify
the raster algorithm. This is not a claim about all browsers or GPU hardware.

Initial v18 fixture stopped on an asynchronous resize-observer race: it checked
the previous pending=false before native resize delivery. Preserved initial
files/log and static-compositor-v18-initial-failure.json distinguish this harness
failure. v18r2 waits for actual drawing dimensions and fence retirement, with no
blind delay or relaxed comparison. Neither one-shot run may be replayed unchanged.

## New images inspected once after exit0

The full r2 fixture and its first failed crop pair were each inspected once.
No visible geometric difference in the pair. Full image visibly labelled
“Static compositor diagnostic”: saved broad smooth saturated sheets, small
clover/button centre, sparse hierarchy and smeared highlights, still **GAME**.
No new temporal or live realism grade. latest.png now equals that labelled
1200×800 fixture. Original failed pair and default full captures are preserved.

## Next correction phase

Build an isolated replacement for the CSS procedural gradient, preserving
readability, transparent start at48% and the existing dark colour/alpha stops.
A deterministic narrow pre-rasterized alpha-ramp PNG is the first candidate;
stretch it responsively with no geometry/input/AA changes. Test the CHANGED
static candidate using the same detail/resize and strict equality cases, inspect
one new full image and compare its overlay numerically to the original ramp.
Do not remove the HUD gradient or widen tolerance. If the candidate passes,
apply only that HUD correction and run affected original HIGH stillness/detail/
Sources checks. Preserve the original failure and avoid unchanged desktop runs.
Then resume substantive structural visual rebuilding; rejected v29 stays rejected.

All19 RECOGNISE plus source/coverage/route/full acceptance remain unfinished.
''')
(p/'latest.png').write_bytes((p/f'{prefix}.png').read_bytes())
(p/'status.txt').write_text('Live v25 / trip v18 unchanged. Static compositor v18r2 reproduced EXACT original signed9457-pixel failure twice with HUD gradient present; absent18/18 strict PASS,zero browser/GL errors. Browser gradient presentation isolated; correction NOT yet applied,original HIGH FAIL remains. Next deterministic alpha-ramp candidate preserving HUD readability,then changed-fixture and affected live checks. latest.png=inspected1200x800 STATIC diagnostic,GAME. Navigation repair PASS preserved; ledgers/defaults unchanged/stale. Coverage84.7% FAIL,dark ABSENT,sources50/20. All19 realism/source/coverage/route/full acceptance unfinished.\n')
notes=(p/'NOTES.md').read_text(encoding='utf-8-sig')
(p/'NOTES-before-static-compositor-v18r2.md').write_bytes((p/'NOTES.md').read_bytes())
notes=notes.replace('# Active: REDIRECT4 — live v25 / trip v18; HIGH failure unresolved, valid PBO diagnostic', '# Active: REDIRECT4 — live v25 / trip v18; HIGH defect reproduced in static HUD gradient')
a='''1. Test browser overlay raster/composition hypothesis using a bounded STATIC fixture from saved opaque diagnostic-submission-v18-frame-9.rgba (1200×800,bottom-up RGBA). Actual HUD gradient plus real detail/resize controls; gradient-present/absent diagnostic cases,layer/raster observations if useful. Avoid expensive unchanged shader rerenders. Goal is causal reproduction,not a lucky pass. Original HIGH failure remains. Do not replay Canvas2D after-presentation copy or unchanged PBO run,disable AA/add blind delays/loosen equality.'''
b='''1. Static compositor isolation COMPLETE; exact signed9457-pixel original failure reproduced (see below). Next build isolated deterministic alpha-ramp PNG replacement for procedural CSS #hud::before gradient: preserve start48%, dark colour #04020a and alpha stops0/112at75%/176at100%,responsive stretch/readability. Test CHANGED static candidate with original real detail/resize controls,90000ms guards,800ms interval,strict equality; inspect fresh full candidate and numerically compare overlay. No blind delays/AA removal/tolerance changes. Do not replay completed fixture/PBO/Canvas2D runs. Only after candidate proof apply HUD-only correction and affected original HIGH stillness/detail/Sources checks.'''
assert notes.count(a)==1
notes=notes.replace(a,b)
notes+='''
## Completed static compositor isolation — correction target established
- probe_static_compositor_v18.py stopped on fixture resize-observer race after4 pairs; preserved script/generated JS+HTML/log/failure receipt. build_static_compositor_v18r2.py fixes actual drawing-dimension guard before comparing; no runtime edit/blind delay/relaxed tolerance. Both one-shot builders/runs completed; never replay unchanged.
- probe_static_compositor_v18r2.py exit0, immutable opaque frame9 as WebGL texture, actual HUD CSS/markup, diagnostic native detail/resize controls. Six cycles/case,18pairs gradient-present and18absent,1200×800,original crop/800ms/90000ms. Present FAIL twice(cycle3 baseline,resize-restored):9457 pixels,max1,bbox[411,277,1000,380]. Absent18/18 exact PASS. Static submissions unchanged within every pair,zero browser/GL errors,25frames/case.
- First static failure signed per-channel delta array EXACTLY EQUAL to original live restored-detail failure,verified numerically without re-viewing old images. Demonstrates HUD gradient browser presentation defect independently of geometry shader. Internal tile dithering/cache mechanism not proven. Passive CDP tree events153/147;no paint events;gradient final layer1200×416 drawsContent/paintCount13 vs absent false/0. No live correction/acceptance credit yet.
- New diagnostic-static-compositor-v18r2.png and present-failure-before/after.png each viewed exactly ONCE after exit0;do not re-view. Full fixture labelled static;GAME,broad smooth saturated sheets,clover/button centre,sparse hierarchy,smeared highlights;pair no visible geometric change. latest.png now equals labelled full STATIC fixture,not live capture. Prior failed pair/defaults/ledgers/live runtime unchanged.
- static-compositor-v18r2-review.md/integrity.json bind method,36 comparisons,exact signed-delta reproduction,images/protected hashes. README/status updated. NOTES once this phase;prior archived NOTES-before-static-compositor-v18r2.md. Next candidate alpha-ramp correction,then affected live checks and substantive visual successor;no WORLD_DONE.
'''
(p/'NOTES.md').write_text(notes,encoding='utf-8-sig')
names=['probe_static_compositor_v18.py','build_static_compositor_v18r2.py','probe_static_compositor_v18r2.py','close_static_compositor_v18r2.py','static-compositor-v18-initial-failure.json','probe-static-compositor-v18.log','probe-static-compositor-v18r2.log','static-compositor-v18r2-review.md','latest.png','status.txt','NOTES.md','README.md']
names += [x.name for x in p.glob('diagnostic-static-compositor-v18*') if x.is_file()]
(p/'static-compositor-v18r2-integrity.json').write_text(json.dumps({'exact_original_signed_delta_reproduced':True,'original_high_failure':'not repaired','protected_unchanged':{n:digest(n)==h for n,h in d['baseline'].items()},'artifacts':{n:digest(n) for n in names}},indent=2)+'\n')
print('Static isolation review closed; exact original delta reproduced; live unchanged.')
