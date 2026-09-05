"""Close static implementation/proof phase only; no numeric or browser runs."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-v34-implementation.json'
assert not OUT.exists()


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE/name).read_text())


def verify(group):
    for name, expected in group.items():
        assert digest(name) == expected, name


ast.parse(Path(__file__).read_text())
prior = read('centre-v33r6-capture-integrity.json')
build = read('centre-v34-build.json')
exit_receipt = read('build-centre-v34-once-exit.json')
assert prior['integrity_passed'] and prior['visual_grade'] == 'GAME'
assert build['implementation_checks_passed'] and exit_receipt['exit_code'] == 0
assert exit_receipt['command'] == 'python3 -u world/build_centre_v34.py'
for group in ['files', 'protected', 'display']:
    verify(prior[group])
verify(build['files'])
for key in ['browser_runs', 'sampled_numerical_runs', 'cost_runs', 'capture_runs']:
    assert build[key] == 0
assert not (HERE/'centre-v34-integrity.json').exists()
assert not list(HERE.glob('diagnostic-centre-v34*'))
assert digest('latest.png') == digest('diagnostic-centre-v33r6-entry.png')
assert (HERE/'status.txt').read_text().startswith('Isolated v33r6 capture CLOSED FAIL:')

notes_path = HERE/'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE/'NOTES-before-centre-v34-implementation.md'
assert not archive.exists()
notes = original.decode('utf-8-sig')
notes = notes.replace(notes.splitlines()[0],
                      '# Active: REDIRECT4 — isolated v34 lamina rebuild implementation CLOSED; runtime untested', 1)
start = notes.index('## Exact next bounded work')
notes = notes[:start]+'''## v34 implementation/proof phase CLOSED — no runtime or numerical runs
- Replaced isolated v33r6 squared petal-cell costs with clipped curled parent laminae and offset child laminae. Shared root bands overlap volumetrically; narrower child cuts, nonuniform2.3/4.3/6.1 fine folds, real displacement and open black cuts. Attachment proof is conditional on permitted child cross-sections,not universal topology/realism. Materials unchanged;no palette/source/coverage credit.
- Five smooth base fields expand to11 signed/offset CSG leaves. a/b are now nonsmooth maxima: never use old3-smooth-leaf Hessian/interval assumptions. Explicit per-leaf Taylor reaches,intersectionMAX/unionMIN,identical cheap/full axial helper. Coefficientwise padded analytic Hessians f/axial/angular/parent/child: [5,1,1]/[4,1,1]/[47,1,1]/[15,4,3]/[22,11,9] in pixelScale. Prospective real-arithmetic calculus,not GPUroundoff proof.
- Removed h18/h36,squared-shell costs and independent fast child shell;paired local/angle trig. CommonJets7 vs5 may increase registers. No measured speedup. One reversible section restores v33r6;shader prefix/material-march suffix,compose/envelope/positiveReach exact. JS/AST/leaf-wiring/coefficient/conditional-attachment checks PASS. build_centre_v34.py ONCE exit0;unique log and actual exit saved.
- centre-v34-implementation.json binds sources,proof,static results,log/exit and historical/protected/display hashes. NOT a passing centre-v34-integrity.json. Version-only original render_centre_v34.py prepared,never run;no diagnostic HTML yet. Zero browser/sampled numerical/cost/capture runs,PNGs or inspections. Live/defaults/ledgers unchanged,latest still labelled inspected REJECTED GAME v33r6 entry. NOTES once,BOM preserved,prior notes archived verbatim.

## Exact next bounded work
Prepare NEW v34 bounds/clearance,GPU smooth-leaf/first-root and matched-cost fixtures using centre-v34-implementation-review.md and field_centre_v34.py. Preserve72000leaf/reach+12000clearance,48cases/75996rays,720fixed+720interval roots,both grids/modes/entry/deep and prior times incl2.4077/3.5242/4.895. Expand five smooth fields into11 CSG leaves;do not version-copy old nonsmooth a/b Hessian assumptions. Add clipped attachment/cap checks;report topology limitations honestly. Cost uses identical NEW v34 scalar/march,shared versus full-trace commonParts recomputation;preserve exact hit/count and lower common-prefix work,total/median wall<=1,12balanced pairs/durable lifecycle. This does not measure v34-v33r6 speedup. Close fixture implementation before one-shot gates;no prewarm/replay/relaxed limits/frame-pump changes. Only numerical+cost PASS permits centre-v34-integrity.json and original1200x800 HIGH/90s renderer ONCE. No current numerical/runtime/visual claim or live promotion.

All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.
'''

readme_path = HERE/'README.md'
readme = readme_path.read_text()
old = ('Next: substantive continuous curled-petal geometry rebuild, not another colour/arithmetic-only '
       'revision. No frame-pump change, prewarm, replay or limit relaxation. Live/defaults/ledgers '
       'unchanged; latest is the inspected REJECTED GAME v33r6 entry diagnostic.')
assert readme.count(old) == 1
readme = readme.replace(old,
    'Isolated **v34 lamina rebuild implementation/proof CLOSED; runtime untested**. '
    'Curled parent shells now intersect separate petal cuts, with volumetric child attachment bands '
    'and finer geometric folds. Five smooth base fields expand into eleven certified CSG boundaries. '
    'JS/AST, exact preservation and prospective bound checks PASS; no actual GLSL, sampled numerical, '
    'cost or visual result. See [v34 design, proof and next gates](centre-v34-implementation-review.md). '
    'Next: prepare new smooth-leaf and matched-cost fixtures, then one-shot gates. No frame-pump '
    'change, prewarm, replay or limit relaxation. Live/defaults/ledgers unchanged; latest remains '
    'the inspected REJECTED GAME v33r6 entry diagnostic, not a v34 image.')

status = ('Isolated v34 lamina rebuild implementation/proof CLOSED: curled parent shells,attached '
          'child folds,separate black cuts;5 smooth fields/11 CSG leaves. Static JS/AST/reversal/'
          'preservation/prospective-bounds PASS;builder ONCE exit0. Zero browser/numerical/cost/'
          'capture runs;no realism or speed claim. Next prepare new v34 smooth-leaf/root/cost '
          'fixtures before one-shot gates. latest.png remains inspected REJECTED GAME v33r6 '
          'entry,not v34. Live/defaults/ledgers unchanged;all19/source/coverage/route/full '
          'unfinished;no promotion/replay/prewarm/relaxed limits.\n')

with archive.open('xb') as stream:
    stream.write(original)
readme_path.write_text(readme)
(HERE/'status.txt').write_text(status)
# Exactly one NOTES write this phase, with the original BOM preserved.
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
verify(prior['files'])
verify(prior['protected'])
assert digest('latest.png') == prior['display']['latest.png']
assert archive.read_bytes() == original
files = dict(prior['files'])
files.update(build['files'])
for name in ['centre-v33r6-capture-integrity.json', 'centre-v34-build.json',
             'build-centre-v34-once.log', 'build-centre-v34-once-exit.json',
             'centre-v34-implementation-review.md', Path(__file__).name, archive.name]:
    files[name] = digest(name)
with OUT.open('x') as stream:
    json.dump({'integrity_passed': True, 'static_passed': True,
               'phase': 'implementation/proof closed; fixture implementation next',
               'numeric_passed': False, 'capture_cost_gate_passed': False,
               'capture_permitted': False, 'browser_runs': 0, 'new_images': 0,
               'inspections': 0, 'promotion': False, 'files': files,
               'protected': prior['protected'],
               'display': {name: digest(name) for name in prior['display']},
               'limits': 'No sampled bounds, GLSL compile, GPU/first-root/cost/capture, topology or realism pass. New CSG requires five smooth base fields/eleven expanded leaves. No numerical inheritance.'},
              stream, indent=2)
    stream.write('\n')
print(json.dumps({'integrity_passed': True, 'static_passed': True,
                  'capture_permitted': False, 'bound_files': len(files),
                  'protected_files': len(prior['protected']), 'new_images': 0}))
