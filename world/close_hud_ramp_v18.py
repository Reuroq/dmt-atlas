"""One-shot evidence closure; preserve historical failures and manual grade ledgers."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
out = HERE/'hud-ramp-v18-integrity.json'
assert not out.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
fixture = json.loads((HERE/'diagnostic-hud-ramp-v18.json').read_text())
promotion = json.loads((HERE/'hud-ramp-v18-promotion.json').read_text())
live = json.loads((HERE/'accessibility-hud-ramp-v18.json').read_text())
d = live['capture_diagnostics']
assert len(live['checks']) == 6 and not live['errors']
assert d['detail'] == 'high' and d['paused'] and d['reduced']
assert not d['renderPending'] and d['renderedAnimTime'] == d['animTime']
assert d['position'] == [0,1.7,8] and d['frames'] == 10
assert not d['missingEvidence'] and not d['uncitedMeshes'] and live['veil_opacity'] == 0
from fidelity import render_signature
assert live['render_signature'] == promotion['render_signature'] == render_signature()
assert digest(live['file']) == live['capture_sha256'] == digest('latest.png')
preserved = {n:digest(n) == h for n,h in promotion['before'].items() if n not in ['trip.css','fidelity.py']}
assert all(preserved.values())
assert all(digest(n) == h for n,h in promotion['after'].items())
assert all(not s['error'] for case in fixture['cases'] for key in ['final','mobile_final'] for s in case[key]['submissions'])
scripts = ['build_hud_ramp_v18.py','probe_hud_ramp_v18.py','promote_hud_ramp_v18.py','close_hud_ramp_v18.py','fidelity.py']
for name in scripts:
    ast.parse((HERE/name).read_text())
subprocess.run(['node','--check',str(HERE/'diagnostic-hud-ramp-v18.js')],check=True,capture_output=True)
assert 'overall: False' in (HERE/'fidelity-hud-ramp-v18.log').read_text()
review = '''# HUD alpha-ramp v18 — corrective phase complete

## Change and bounded evidence

The procedural `#hud::before` gradient is replaced by a deterministic 1×4097
RGBA PNG, stretched to the unchanged fixed inset `48% 0 0`. RGB stays #04020a;
alpha endpoints are 0, 112 at 75%, and 176 at 100%. No geometry, movement,
runtime JavaScript, antialiasing, waiting rules or equality thresholds changed.
`fidelity.py` now includes the PNG bytes in render signatures. The asset is
generated arithmetically, not AI imagery or a source depiction.

The changed-only derivative of the completed v18r2 static fixture passed all
18 desktop and 3 narrow-viewport comparisons: native detail/resize controls,
800 ms separation, 90,000 ms guards, strict zero pixel differences and unchanged
submissions within every pair. Browser and GL errors: zero. The unchanged
gradient-absent case was not rerun. The earlier exact signed 9,457-pixel
reproduction and both initial diagnostic failures remain immutable.

Against the prior full static image, pixels above y384 are exactly identical.
Full-image appearance delta is at most 2/255 per channel (mean absolute 0.142534);
the unobstructed overlay region has mean absolute delta 0.267456. Against the
ideal continuous blend, that region's max error is 1.554249 and mean 0.346398.
These are appearance comparisons, NOT relaxed stillness tolerances. Desktop
and 390×844 fixture images were inspected once after exit: text remains readable,
darkening is preserved, no obvious banding. The narrow fixture stretches the
saved scene texture; this is not a live mobile geometry capture.

## Affected original live acceptance

After promotion, the unchanged `render_visual.py --stage chrysanthemum
--check-stillness --check-sources --capture-name accessibility-hud-ramp-v18`
completed at 1200×800 HIGH with all six checks PASS: paused pixel stillness,
paused resize restoration, reduced-motion stillness, detail-toggle route/pose,
restored-detail reduced stillness, and Sources/fidelity/provenance. Four pixel
comparisons remain strict equality. Browser errors: zero. Final entry pose
[0,1.7,8], yaw/pitch 0, paused/reduced, frame10, animation/rendered time
6.14270000019074, no pending frame, no veil or missing/uncited evidence.

The closure hash guard caught `render_visual.py`'s automatic named-capture copy
over the two default files. Both defaults were restored byte-for-byte from the
hash-matching `accessibility-chrysanthemum-v25` originals; the new named image,
receipt and latest display are untouched. Initial closure failure and recovery
receipts are retained. No test was rerun and no renderer change was needed.

The current affected HIGH failure is corrected on this evidence; historical
failure receipts are retained, not rewritten. This is not full acceptance or
a universal browser-mechanism proof. Internal dithering/cache details remain
unproven. No unchanged navigation or full desktop suite was replayed.

## Fresh visual review

`accessibility-hud-ramp-v18.png` was inspected exactly once after renderer exit.
**GAME**: broad smooth saturated sheets around a small clover/button centre,
sparse resolved nested hierarchy, smeared highlights and no convincing black
openings. This single paused image grants no temporal realism grade. Both new
fixture images are also GAME, diagnostic only. Do not re-view these three PNGs.
`latest.png` equals the fresh LIVE image, no longer a static diagnostic.

`fidelity.py --check` regenerated outputs once after the signature change;
expected exit1, overall false. Manual source/grade ledgers and old default
renders are unchanged/stale. Chrysanthemum coverage remains historical84.7%,
dark ABSENT, source decisions50/20. No full acceptance or realism promotion.

## Next

Return to substantive nested-geometry construction from the rejected v29
candidate's selected code and numerical/bounds reviews. Do not promote v29 or
replay its unchanged probes/renders. New field needs independent gradient,
first-root, clearance/bounds and filtering checks, then fresh HIGH entry/deep
temporal inspection. All19 realism, remaining16 source gates, coverage, route
review and full desktop/mobile/paced/fallback acceptance remain unfinished.
'''
(HERE/'hud-ramp-v18-review.md').write_text(review)
readme_path = HERE/'README.md'
readme = readme_path.read_text()
old = '''without geometry rendering. No correction yet; original HIGH remains FAIL.
See [static isolation and next correction](static-compositor-v18r2-review.md).

latest.png now shows the inspected1200×800 **labelled static compositor fixture**,
still GAME (broad smooth colour sheets, small clover centre, sparse detail and
smeared highlights), not a new live capture. The failed v18 pair remains preserved. Old full defaults'''
new = '''without geometry rendering. The historical failed pair remains preserved.
See [static isolation](static-compositor-v18r2-review.md).

The HUD-only deterministic alpha-ramp correction is now live: all21 changed
static comparisons and all6 affected original1200×800 HIGH stillness/detail/
Sources checks PASS, zero browser/GL errors. Colour/opacity stops and responsive
readability are preserved; PNG bytes are included in render signatures.
See [correction evidence and visual review](hud-ramp-v18-review.md).

latest.png now shows the freshly inspected1200×800 **live Chrysanthemum**,
still GAME (broad smooth colour sheets, small clover centre, sparse detail,
smeared highlights and no convincing black openings). This is not a temporal
regrade or full acceptance. Next: substantive nested-geometry successor.
Old full defaults'''
assert readme.count(old) == 1
readme_path.write_text(readme.replace(old,new))
status_path = HERE/'status.txt'
assert 'Static compositor v18r2' in status_path.read_text()
status_path.write_text('Live v25 / trip v18 plus HUD alpha-ramp correction. Changed static21/21 strict PASS; original1200x800 HIGH stillness/detail/Sources6/6 PASS,zero errors. Historical9457-pixel failure preserved; current affected HIGH gate corrected. Geometry/movement JS unchanged. latest.png=fresh inspected LIVE Chrysanthemum,GAME: broad sheets,clover centre,sparse hierarchy,smeared highlights,no convincing dark openings. Next substantive geometry successor; rejectedv29 stays rejected. Ledgers/defaults unchanged/stale; coverage84.7% FAIL,dark ABSENT,sources50/20. All19 realism/source/coverage/route/full acceptance unfinished.\n')
notes_path = HERE/'NOTES.md'
archive = HERE/'NOTES-before-hud-ramp-v18.md'
assert not archive.exists()
archive.write_bytes(notes_path.read_bytes())
notes = notes_path.read_text(encoding='utf-8-sig')
notes = notes.replace('# Active: REDIRECT4 — live v25 / trip v18; HIGH defect reproduced in static HUD gradient', '# Active: REDIRECT4 — live v25 / trip v18 + HUD ramp; affected HIGH PASS, geometry GAME',1)
start = notes.index('1. Static compositor isolation COMPLETE;')
end = notes.index('3. Other18 realism targets', start)
notes = notes[:start]+'''1. HUD causal correction COMPLETE (below): deterministic PNG live, changed static21/21 strict PASS and original affected HIGH6/6 PASS. Do not replay completed builders/fixtures/checks or re-view their PNGs. Original failures retained; no full acceptance claim.
2. Resume substantive structural visual successor from selected continuum-v29-candidate.js / build_centre_candidate_v29.py / centre-v29-numerical-review.md / centre-v29-bounds.md. Rejectedv29 remains rejected. New nested geometry must fix broad sheets,button centre,sparse hierarchy,smeared highlights and absent black openings; independent NEW-field numerical/bounds/filtering checks then fresh HIGH entry/deep temporal inspection. No unchanged desktop/navigation acceptance rerun.
'''+notes[end:]
notes += '''
## Completed deterministic HUD correction (do not replay)
- build_hud_ramp_v18.py creates arithmetic1×4097 RGBA hud-alpha-ramp-v18.png,RGB#04020a,alpha0/112at75%/176at100%; unchanged inset48%,responsive100% stretch. probe_hud_ramp_v18.py derives from completed staticv18r2,only CHANGED ramp:18desktop+3narrow390×844 comparisons,800ms/90000ms,strict all21 zero,unchanged submissions,zero browser/GL errors. No absent-case replay.
- Desktop overlay appearance versus prior static: above y384 exactly identical; full-frame max2/255,mean absolute.142534; unobstructed overlay mean.267456. Ideal blend max1.554249,mean.346398. These are appearance metrics,not stillness tolerances. Desktop/mobile candidates inspected ONCE,readable,no obvious banding; fixture-only mobile scene stretch. Both GAME.
- promote_hud_ramp_v18.py ONCE verified proof/protected hashes,archived prior CSS/fidelity.py,promoted ONLY #hud::before background; PNG added to fidelity.py RENDER_FILES. All live runtime JS,geometry,movement unchanged. Promotion receipt binds new signature324b7f317aa3c4211b53a9a6fb01377029222a35b63dde91ab04ade77787bd0c. Old signed9457 failure evidence unchanged; internal browser dithering/cache mechanism still unproven.
- render_visual.py --stage chrysanthemum --check-stillness --check-sources --capture-name accessibility-hud-ramp-v18 ONCE exit0: original1200×800 HIGH all6 PASS (four strict pixel pairs,detail pose/route,Sources),zero errors. Final entry[0,1.7,8],yaw/pitch0,paused/reduced,frame10,time/rendered6.14270000019074,settled,veil0,zero missing/uncited evidence. Current affected HIGH failure corrected;not full acceptance/universal proof.
- accessibility-hud-ramp-v18.png inspected ONCE after exit:GAME,broad smooth saturated sheets,small clover/button centre,sparse nested detail,smeared highlights,no convincing black openings. No temporal regrade. latest.png equals this fresh LIVE full image;no longer static. Do not re-view any of these3 new PNGs. Old failed pair/defaults/manual ledgers unchanged.
- Closure initially stopped before documentation writes: render_visual.py lines198–200 auto-copy named captures over defaults. Restored both defaults byte-for-byte from hash-matching accessibility-chrysanthemum-v25 originals;new named capture/latest untouched. Initial-failure/default-recovery receipts retained. Future named live captures must preserve/restore defaults around this known behavior;no renderer/test replay needed.
- fidelity.py --check ONCE regenerated outputs after signature change,expected exit1 overallFalse;all prior full acceptance remains stale. hud-ramp-v18-review.md/integrity.json bind artifacts,AST/JS checks,protected hashes and display. README/status current;NOTES once this phase,BOM preserved,archive NOTES-before-hud-ramp-v18.md. Next substantive geometry successor;no completion marker.
'''
notes_path.write_text(notes,encoding='utf-8-sig')
assert notes_path.read_bytes().startswith(b'\xef\xbb\xbf')
names = set(scripts + ['diagnostic-hud-ramp-v18.html','diagnostic-hud-ramp-v18.js',
    'hud-ramp-v18-review.md','hud-ramp-v18-appearance.json','hud-ramp-v18-promotion.json',
    'hud-ramp-v18-build.json','hud-alpha-ramp-v18.png','probe-hud-ramp-v18.log',
    'hud-ramp-v18-closure-initial-failure.json','hud-ramp-v18-default-recovery.json',
    'render-accessibility-hud-ramp-v18.log','fidelity-hud-ramp-v18.log',
    'trip.css','latest.png','README.md','status.txt','NOTES.md'])
names.update(p.name for pattern in ['diagnostic-hud-ramp-v18*.png','diagnostic-hud-ramp-v18.json','accessibility-hud-ramp-v18*.json','accessibility-hud-ramp-v18.png'] for p in HERE.glob(pattern))
out.write_text(json.dumps({'phase':'HUD causal correction complete; geometry goal unfinished',
    'protected_unchanged':preserved, 'render_signature':render_signature(),
    'live_checks':live['checks'],'live_errors':live['errors'],
    'static_strict_passes':21,'latest_matches_live':True,
    'python_ast':scripts,'node_syntax':['diagnostic-hud-ramp-v18.js'],
    'fidelity_check_exit':1,'fidelity_overall':False,
    'artifact_hashes':{n:digest(n) for n in sorted(names)},
},indent=2)+'\n')
print('Closed HUD correction: strict static/live checks PASS; visual GAME; notes/status/display current.')
