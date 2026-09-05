"""One-shot numerical-phase closure; no promotion, grading or live rerender."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v30-integrity.json'
assert not OUT.exists()
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
bounds=json.loads((HERE/'centre-v30-bounds-check.json').read_text())
gpu=json.loads((HERE/'numeric-candidate-v30-check.json').read_text())
roots=json.loads((HERE/'centre-v30-first-root-check-r2.json').read_text())
assert bounds['passed'] and roots['passed'] and roots['reference_rays']==360
assert not gpu['passed'] and roots['original_fixed_grid_passed'] is False
assert roots['unresolved_intervals']==0 and not gpu['errors']
for receipt,key in [(bounds,'source_hashes'),(gpu,'files'),(roots,'source_hashes')]:
    assert all(digest(n)==h for n,h in receipt[key].items())
assert all(digest(n)==h for n,h in bounds['protected_before'].items())
assert bounds['protected_before']==bounds['protected_after']
assert digest('continuum.js')==digest('continuum-v25.js')
assert digest('trip.js')==digest('trip-v18.js')
assert digest('latest.png')==digest('accessibility-hud-ramp-v18.png')

# Prepare next phase, never execute the historical renderer or this derivative here.
render=HERE/'render_centre_v30.py'
assert not render.exists()
render.write_text((HERE/'render_centre_v29.py').read_text().replace('v29','v30'))
scripts=['build_centre_candidate_v30.py','build_centre_v30_checks.py',
    'field_centre_v30.py','check_centre_v30_bounds.py','probe_numeric_candidate_v30.py',
    'audit_centre_v30_first_roots.py','audit_centre_v30_first_roots_r2.py',
    render.name,Path(__file__).name]
for n in scripts:ast.parse((HERE/n).read_text())
subprocess.run(['node','--check',str(HERE/'continuum-v30-candidate.js')],check=True,capture_output=True)
for n in ['gpu_probe_v30_candidate.html','gpu_probe_v30_leaves.html']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/n).read_text())
    assert len(inline)==1
    subprocess.run(['node','--check'],input=inline[0],text=True,check=True,capture_output=True)

review='''# v30 volumetric petal network — numerical phase closed

## Substantive change; not promoted

The isolated `continuum-v30-candidate.js` replaces v29's two coaxial perforated
membranes with split petal volumes and finer transverse branches. Parent waves
change child phases; three spatial scales affect actual zero sets, not texture.
Openings expose deeper structure and a dark outer backing. The cap contracts
at .85 rather than .45 and still begins beyond physical exit at z=-27.5.
Self-lit material fill is increased; whether this improves detail is ungraded.
Sources remain the existing audited Chrysanthemum/mandala/fractal/breathing/fold
interpretation; no source audit or descriptor ledger is changed.

Clearance lower bound5.48 preserves x±4 and exit−22. HIGH2048/LOW1536 budgets,
14 bisections, .00015 residual plus directional-depth acceptance and no forced
minimum step remain. The shared camera, pause clock, movement and HUD are intact.
The opening constraint `.10-|b|` has a free-side cusp: its reach is explicitly
the minimum of the two smooth arms, not a smooth-Hessian approximation.

## Independent CPU and actual GPU evidence

`check_centre_v30_bounds.py`: all72,000 smooth-leaf derivative/curvature and
four-point free-side reach samples PASS, across entry/deep, HIGH/LOW and
pixelScale×1/2/4. Maximum derivative/bound .20436421, curvature/bound .06549536;
minimum advanced field7.68867e−8. Another12,000 corridor/inner-clearance samples
PASS. Gaussian attenuation and directional derivative checks PASS. These are
sampled bounds/filter checks, not alias-free temporal proof or formal intervals.

`probe_numeric_candidate_v30.py`: all38,160 actual GPU rays hit; maximum249
iterations. All smooth-leaf scalar errors <.000085481 and gradients <.000395940,
against unchanged .001/.005 limits. Actual float32 CSG selection and saved
normal replay are EXACT. Maximum scalar/root-field disagreement .000086620;
directional/bound ratio .175208. No browser errors. All42 composite-FD crease
disagreements remain explicitly recorded, not labelled differentiable normals.

The original fixed-.003 first-crossing gate **FAILS** one of360 references:
LOW entry, time8,49×33 ray969. Original difference .08192336 exceeds .03.
The retained local .00001 investigation finds a real occupied sliver from
about12.492135 to12.492839 that the coarse reference stepped over. GPU depth
12.492027 is before this first entry; the later12.573951 root is not first.
This subpixel sliver is a temporal/filtering concern to inspect, not visual credit.

## Offline first-entry reference correction

Every saved reference ray, not just the failed ray, receives a separate new
audit. Independent float64 leaf endpoints and prospective curvature bounds
exclude intervals using the linear-interpolation departure M*h²/8. The free
envelope avoids any axis Hessian claim. Left-first subdivision of the earliest
possible occupied interval must find a real positive/negative bracket <=1e−7;
unresolved intervals fail. No GPU rays are rerun, no .03 tolerance is enlarged,
and neither small residuals nor misses count as intersections.

Initial offline audit reached JSON serialization but failed on numpy.bool_.
Its script/log and failure receipt remain. `_r2` only makes the result boolean
serializable (and removes an unused placeholder); numerical rules are unchanged.
All360 audited first roots PASS, zero unresolved intervals, maximum depth error
.001436692. The originally failed ray differs from its first bracket midpoint
by .000107529. Original fixed-grid FAIL remains unchanged in its own receipt.
This uses ordinary float64 with1e−12 outward padding, NOT a formally directed-
rounding interval library or a universal convergence/tangency proof.

The combined numerical gate is bounds + smooth-leaf/CSG GPU evidence + this
first-entry audit, not a retroactive pass for the original fixed-grid method.

## Exact next phase

`render_centre_v30.py` is prepared but NOT run. It derives from the completed
v29 fixture with only candidate/receipt labels changed; uses current live trip18,
HUD PNG,1200×800 HIGH,90s settled guards, real controls, entry/deep and ≥3s pairs.
It never copies over default captures or latest. Run it ONCE, wait for exit,
then inspect each NEW completed PNG exactly once. Update latest with a labelled
new diagnostic only after capture, and write specific temporal/realism reasons.
Reject GAME/CLOSE and rebuild; do not promote merely because numerics pass.

No new visual render exists this phase; latest.png remains the inspected LIVE
HUD-corrected Chrysanthemum, GAME. Live v25/trip18, all runtime assets, failed
history, old defaults, source and manual grade ledgers are byte-identical.
No unchanged desktop acceptance or fidelity regeneration was run.
All19 realism, remaining16 source gates, coverage, route and full acceptance
remain unfinished. No completion marker.
'''
(HERE/'centre-v30-numerical-review.md').write_text(review)
readme_path=HERE/'README.md'
readme=readme_path.read_text()
anchor='regrade or full acceptance. Next: substantive nested-geometry successor.'
assert readme.count(anchor)==1
readme=readme.replace(anchor,'''regrade or full acceptance. Isolated **v30** now replaces the coaxial sheets
with a volumetric split-petal/branch network. Sampled bounds, actual GPU leaf
gradients/CSG and360 interval-audited first intersections pass. The original
coarse-reference failure is preserved, not relabelled. No visual grade or promotion;
next is fresh HIGH entry/deep temporal inspection.
See [v30 numerical evidence and limits](centre-v30-numerical-review.md).''')
readme_path.write_text(readme)
status_path=HERE/'status.txt'
assert 'isolated v30' in status_path.read_text()
status_path.write_text('Isolated v30 volumetric split-petal/branch successor built; CPU72000 bounds/clearance/filter PASS, GPU38160 rays/all leaves/exactCSG PASS,360 interval-audited first roots PASS. Original coarse-grid FAIL preserved. NEXT fresh1200x800 HIGH entry/deep temporal inspection; render_centre_v30.py prepared,not run. No promotion. Live v25/trip18/HUD unchanged; latest.png=inspected live GAME. All19/source/coverage/route/full acceptance unfinished.\n')
notes_path=HERE/'NOTES.md'
archive=HERE/'NOTES-before-centre-v30.md'
assert not archive.exists()
archive.write_bytes(notes_path.read_bytes())
notes=notes_path.read_text(encoding='utf-8-sig')
notes=notes.replace('# Active: REDIRECT4 — live v25 / trip v18 + HUD ramp; affected HIGH PASS, geometry GAME',
    '# Active: REDIRECT4 — isolated v30 numerics closed; NEXT fresh HIGH visual pairs; live v25 GAME',1)
start=notes.index('2. Resume substantive structural visual successor')
end=notes.index('\n3. Other18 realism targets',start)
notes=notes[:start]+'''2. Isolated v30 substantive split-petal/branch volume BUILT; numerical phase closed,not promoted/ungraded. Exact next: run prepared render_centre_v30.py ONCE (1200×800 HIGH,90s guards,entry/deep≥3s pairs,real controls/current trip18+HUD); wait for exit,inspect each NEW completed PNG ONCE,review/label then update latest. No old PNG re-view or unchanged acceptance/numerical rerun. centre-v30-integrity.json binds all inputs/protected files; centre-v30-numerical-review.md explains original coarse-grid failure and separate corrected first-entry audit. Reject GAME/CLOSE and rebuild.''' + notes[end:]
old='- Start future geometry work from targeted continuum-v29-candidate.js, build_centre_candidate_v29.py, centre-v29-numerical-review.md and centre-v29-bounds.md (selected sections).'
assert notes.count(old)==1
notes=notes.replace(old,'- v30 supersedes v29 for NEXT isolated visual inspection; v29 stays rejected. New sources: continuum-v30-candidate.js/build_centre_candidate_v30.py,field_centre_v30.py,centre-v30-bounds.md and numerical review.')
notes+='''
## Completed v30 numerical phase (do not replay)
- New geometry is a branching outer VOLUME,not two coaxial sheets. CSG P=max(f,|a|−.19,.10−|b|),B=max(f+.32,|a|−.40,|b|−.055),F=min(P,B,f+9). Parent-modulated levels physically change zero sets;HIGH third scale changes b,LOW retains first2. Clearance5.48,cap starts−27.5 with axial.85,exit−22 and x±4 unchanged. Self-lit fill increased;ungraded. No live edits/promotion.
- Smooth-leaf L13+12pixel,M160+250pixel+600pixel²;Gaussian derivatives included. Free-side cusp .10−|b| uses min of TWO smooth-arm reaches,not smooth abs curvature. Existing2048/1536,14bisections,.00015residual/directional-depth and no minimum step retained. centre-v30-bounds.md derives bounds;not universal proof.
- check_centre_v30_bounds.py ONCE PASS72000 leaf/curvature/four-point reach samples,pixel×1/2/4,HIGH/LOW,entry/deep. Max ratios.20436421/.06549536,min advanced7.68867e−8;12000 clearance samples and Gaussian attenuation/derivatives PASS. Not CSG temporal filtering proof.
- probe_numeric_candidate_v30.py ONCE38160 actual GPU rays,no misses,max249iterations;all smooth-leaf scalars<.000085481,gradients<.000395940,exact float32 CSG and saved normal replay,error0;42 composite-FD crease disagreements retained,zero browser errors. Fixed.003 first-root gate FAIL1/360:LOW entry time8,49×33ray969,error.08192336. Preserve original raw/check/log. centre-v30-first-root-adverse.json local.00001 scan finds true occupied sliver12.492135–12.492839 skipped by coarse reference,not GPU root failure. Subpixel slivers remain temporal concern.
- Offline audit_centre_v30_first_roots.py reached serialization then failed numpy.bool_;script/log/failure receipt preserved. r2 only serializes explicit bool/removes unused placeholder;no numeric-rule change. No GPU replay. Independent float64 leaf interval exclusion M*h²/8 plus free envelope,left-first actual sign brackets≤1e−7 at EVERY360 saved reference:PASS,max error.001436692,zero unresolved;ray969 corrected error.000107529. Original fixed-grid FAIL unchanged. Ordinary float64 with1e−12 pad,not formal interval arithmetic/universal proof. Separate corrected gate in centre-v30-first-root-check-r2.json.
- close_centre_v30_numerical.py ONCE binds AST/JS/protected hashes,all evidence and prepared render_centre_v30.py (NOT run). Review/README/status current;NOTES once,prior archived NOTES-before-centre-v30.md,BOM retained. latest.png remains inspected accessibility-hud-ramp-v18.png LIVE GAME;NO NEW image this phase. Live v25/trip18/HUD,defaults/manual ledgers immutable. No fidelity or unchanged acceptance rerun. Next fresh v30 visuals only;all19/source/coverage/route/full unfinished.
'''
notes_path.write_text(notes,encoding='utf-8-sig')
assert notes_path.read_bytes().startswith(b'\xef\xbb\xbf')
protected={n:digest(n) for n in bounds['protected_before']}
assert protected==bounds['protected_before']
files=set(scripts+['continuum-v30-candidate.js','gpu_probe_v30_candidate.html','gpu_probe_v30_leaves.html',
    'centre-v30-build.json','centre-v30-bounds.md','centre-v30-numerical-review.md',
    'centre-v30-bounds-check.json','numeric-candidate-v30-check.json','numeric-candidate-v30-raw.json',
    'centre-v30-first-root-adverse.json','centre-v30-first-root-check-r2.json',
    'centre-v30-first-root-serialization-failure.json','check-centre-v30-bounds.log',
    'probe-numeric-candidate-v30.log','audit-centre-v30-first-roots.log','audit-centre-v30-first-roots-r2.log'])
OUT.write_text(json.dumps({'integrity_passed':True,'numeric_passed':True,'promoted':False,
    'visual_grade':'UNREVIEWED; no new renders','original_fixed_grid_passed':False,
    'corrected_first_entry_passed':True,'protected':protected,'files':{n:digest(n) for n in sorted(files)},
    'documentation':{n:digest(n) for n in ['README.md','status.txt','NOTES.md','NOTES-before-centre-v30.md']},
    'next':'Run prepared render_centre_v30.py ONCE; inspect only new completed images after exit. All realism/source/coverage/route/full gates remain.'},indent=2)+'\n')
print('Closed v30 numerical phase: corrected sampled gate PASS; original failure preserved; visual UNREVIEWED; live unchanged.')
