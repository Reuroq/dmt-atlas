"""Close implementation only. Numerical and original capture gates stay pending."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

HERE=Path(__file__).resolve().parent
OUT=HERE/'centre-v33r3-implementation.json'
assert not OUT.exists()
def digest(n):return hashlib.sha256((HERE/n).read_bytes()).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
def save(n,text):
    assert not (HERE/n).exists(),n
    (HERE/n).write_text(text)

prior=read('centre-v33r2-integrity.json')
for hashes in [prior['protected'],prior['files']]:
    assert all(digest(n)==h for n,h in hashes.items()), 'Prior evidence changed'
capture=read('diagnostic-centre-v33r2-receipts.json')
assert not capture['passed'] and not capture['receipts']
assert digest('latest.png')==digest('diagnostic-centre-v32-deep-motion.png')
old=(HERE/'continuum-v33r2-candidate.js').read_text()
new=(HERE/'continuum-v33r3-candidate.js').read_text()
start=new.index('   void cheapParts(');end=new.index('   vec4 traceSample(',start)
cheap=new[start:end]
skip_start=new.index('     // This threshold selects a useful certificate;')
skip_end=new.index('     float safeStep;sampleValue=traceSample(p,rd,safeStep);',skip_start)
skip=new[skip_start:skip_end]
assert new.replace(cheap,'').replace(skip,'')==old
assert all(s not in cheap for s in ['r12','r18','r36','childShell','parentShell','angular12','angular36','fieldPartsReach('])
assert 'if(fastStep>.08)' in skip and 'distanceAlong+=fastStep;havePrevious=false;' in skip
assert read('centre-v33r3-build.json')['sha256']==digest('continuum-v33r3-candidate.js')
old_field=(HERE/'field_centre_v33r2.py').read_text()
new_field=(HERE/'field_centre_v33r3.py').read_text()
assert new_field.startswith(old_field)
assert (HERE/'render_centre_v33r3.py').read_text()==(HERE/'render_centre_v33r2.py').read_text().replace('v33r2','v33r3')
scripts=['build_centre_v33r3.py','build_centre_v33r3_checks.py','field_centre_v33r3.py',
    'check_centre_v33r3_bounds.py','probe_numeric_candidate_v33r3.py',
    'audit_centre_v33r3_first_roots.py','measure_centre_v33r3_cost.py','render_centre_v33r3.py',Path(__file__).name]
for n in scripts:ast.parse((HERE/n).read_text(),filename=n)
subprocess.run(['node','--check',str(HERE/'continuum-v33r3-candidate.js')],check=True,capture_output=True)
for kind in ['candidate','leaves']:
    inline=re.findall(r'<script>([\s\S]*?)</script>',(HERE/f'gpu_probe_v33r3_{kind}.html').read_text())
    assert len(inline)==1
    subprocess.run(['node','--check'],input=inline[0],text=True,check=True,capture_output=True)
# Verify that every instrumentation replacement actually has one production
# anchor. Syntax checks alone cannot establish that string replacements fire.
for anchor in ['vec4 sampleValue=vec4(0.);','p=ro+rd*distanceAlong;\n     float bound=',
    'float fastStep=cheapReach(p,rd);','distanceAlong+=fastStep;havePrevious=false;',
    'float safeStep;sampleValue=traceSample(p,rd,safeStep);',
    'float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;','    vec3 color;']:
    assert new.count(anchor)==1,anchor
assert not list(HERE.glob('diagnostic-centre-v33r3*'))
assert not (HERE/'centre-v33r3-bounds-check.json').exists()
assert not (HERE/'numeric-candidate-v33r3-raw.json').exists()
assert not (HERE/'centre-v33r3-integrity.json').exists()

next_step=('Run check_centre_v33r3_bounds.py, then probe_numeric_candidate_v33r3.py, '
    'then audit_centre_v33r3_first_roots.py and measure_centre_v33r3_cost.py ONCE each, '
    'saving logs. Original cases plus failed clock4.895:32 GPU cases/50772 rays/480 '
    'fixed-grid and480 interval roots; preserve all limits. Inspect failures before '
    'any correction; never replay unchanged completed probes. If numerical checks '
    'pass, write a numerical closure binding sources/protected hashes and cost '
    '(centre-v33r3-integrity.json); only then may prepared render_centre_v33r3.py '
    'run ONCE at original1200x800 HIGH/90s. No capture is authorized by this static receipt.')
review='''# v33r3 implementation — complete; numerical/visual validation pending

Isolated axial-only certificate path added. Segments over .08 advance by the
certified reach (maximum .4) and reset bracket history. Otherwise v33r2's full
path is unchanged. This is a performance hypothesis, not a measured fix.

Static checks PASS: removing two inserted blocks recovers v33r2 byte-for-byte;
independent full scalar reference unchanged; original HIGH fixture differs only
by candidate version; Python AST and JavaScript syntax pass; instrumentation
anchors are unique. This does not establish GLSL compilation or numerical safety.

Prepared bounds/GPU/interval/cost fixtures include clock4.895, cheap jet checks,
free-segment sampling and cheap/full/skip/refinement counters. No numerical or
render fixture has run. The renderer still requires a passing numerical closure.

Live v25/trip18/HUD, defaults, source/manual ledgers and old evidence are unchanged.
latest.png remains the inspected, labelled REJECTED GAME v32 deep-motion image.
No new PNG; v33r3 is visually UNREVIEWED. All19 realism/source/coverage/route/full
acceptance remain open.

## Next

'''+next_step+'\n'
save('centre-v33r3-implementation-review.md',review)
status=('Isolated v33r3 two-tier marcher IMPLEMENTED; static invariance/AST/JS PASS, '
    'numerical and visual UNVALIDATED. Prepared32 GPU cases including failed '
    'clock4.895,cheap/full counters,bounds/480first-root checks and cost comparison. '
    'Next numerical checks and closure before original1200x800 HIGH/90s capture. '
    'v33/v33r2 FAIL90s preserved;no unchanged replay,no promotion. latest.png remains '
    'inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/'
    'ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
(HERE/'status.txt').write_text(status)
readme=(HERE/'README.md').read_text()
old_next=('Next:isolated v33r3 cheap certified-free fast path before expensive full-field\n'
    'evaluation,with independent validation/cost measurement before another original\n'
    'HIGH/90s attempt. No unchanged v33/v33r2 replay;zero-set,root/control limits,\n'
    'live/defaults/ledgers and latest v32 diagnostic remain unchanged.')
assert readme.count(old_next)==1
readme=readme.replace(old_next,'''Isolated **v33r3 two-tier marcher is implemented, numerically and visually
UNVALIDATED**. Static invariance and syntax checks pass; expanded numerical/cost
fixtures are prepared, including failed clock4.895 and cheap/full counters.
See [implementation review](centre-v33r3-implementation-review.md). Next: numerical
checks and closure before any original HIGH/90s attempt. No unchanged v33/v33r2
replay; zero-set,root/control limits,live/defaults/ledgers and latest v32 diagnostic
remain unchanged.''')
(HERE/'README.md').write_text(readme)
notes_path=HERE/'NOTES.md'
save('NOTES-before-centre-v33r3-implementation.md',notes_path.read_text())
notes=notes_path.read_text(encoding='utf-8-sig')
notes=notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v33r3 IMPLEMENTED / UNVALIDATED; NEXT numerical checks',1)
old_next='2. v33r2 HIGH capture phase CLOSED:entry settle timeout90.0097s,zero PNGs,visually UNREVIEWED. No replay. Exact next:isolated v33r3 cheap axial-only certified-free fast path,independently validate/measure before original1200x800 HIGH/90s capture.'
assert notes.count(old_next)==1
notes=notes.replace(old_next,'2. v33r3 implementation phase CLOSED;static invariance/AST/JS PASS,numerical/visual UNVALIDATED. Next prepared bounds→GPU→interval→cost checks,then numerical closure before original1200x800 HIGH/90s capture. Prior v33/r2 timeouts immutable.')
notes+='\n## Completed v33r3 implementation phase (no numerical/capture run)\n'
notes+='- build_centre_v33r3.py and build_centre_v33r3_checks.py ONCE exit0. Isolated cheap f/axial-only jets omit shells/angular powers; intersectionMAX/unionMIN certified reach>.08 skips full evaluation,retains.4cap/105limit and clears bracket history. Threshold is a branch selector,not a forced minimum step. Otherwise unchanged v33r2 path;budgets/bisections/tolerances/clearance unchanged. No proven speedup or GLSL/numerical pass.\n'
notes+='- close_centre_v33r3_implementation.py ONCE:two-insertion reversal recovers parent byte-for-byte,full scalar prefix unchanged,renderer only version-renamed,PythonAST/JSsyntax and unique instrumentation anchors PASS. centre-v33r3-implementation.json is NOT a numerical gate. Prepared32cases/50772GPUrays/480+480roots include failed4.895 on both grids,HIGH/LOW,entry/deep;original derivative/clearance/filter checks plus cheap scalar/FD/reach checks. Fourth readback counters cheap/full/skips/refinement;first-three time excludes RPC unlike saved r2,comparison explicitly indicative.\n'
notes+='- No numerical probe,capture,fidelity or acceptance rerun. No new PNG;latest remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers/prior evidence unchanged. README/status current;NOTES once,BOM preserved,archive NOTES-before-centre-v33r3-implementation.md.\n'
notes+='- Exact next:'+next_step+' All19/source/coverage/route/full unfinished;no completion marker.\n'
notes_path.write_text(notes,encoding='utf-8-sig')
assert all(digest(n)==h for n,h in prior['protected'].items())
files=scripts+['continuum-v33r3-candidate.js','gpu_probe_v33r3_candidate.html','gpu_probe_v33r3_leaves.html',
    'centre-v33r3-build.json','centre-v33r3-bounds.md','centre-v33r3-implementation-review.md',
    'build-centre-v33r3.log','build-centre-v33r3-checks.log','README.md','status.txt','NOTES.md']
OUT.write_text(json.dumps({'implementation_static_passed':True,'numeric_run':False,'capture_run':False,
    'exact_parent_after_removing_insertions':True,'protected':prior['protected'],
    'files':{n:digest(n) for n in files},'next':next_step},indent=2)+'\n')
print('v33r3 implementation closed: static PASS; numerical/GPU/cost/capture NOT RUN; protected hashes unchanged.')
