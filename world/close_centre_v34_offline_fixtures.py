"""One-shot static fixture closure, including synthetic interval contracts only."""
import ast
import hashlib
import json
from pathlib import Path

from csg_interval_v34 import contract_checks

HERE = Path(__file__).resolve().parent
OUT = HERE/'centre-v34-offline-fixtures.json'
START = HERE/'centre-v34-offline-fixtures-started.json'
assert not OUT.exists() and not START.exists()


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def verify(group):
    for name, want in group.items():
        assert digest(name) == want, name


prior = json.loads((HERE/'centre-v34-implementation.json').read_text())
for group in ['files', 'protected', 'display']:
    verify(prior[group])
assert prior['static_passed'] and not prior['capture_permitted']
names = ['check_centre_v34_bounds.py', 'csg_interval_v34.py', Path(__file__).name,
         'centre-v34-offline-fixtures-review.md']
START.write_text(json.dumps({'started': True, 'sources': {n: digest(n) for n in names}})+'\n')
for name in names[:3]:
    ast.parse((HERE/name).read_text(), filename=name)
contracts = contract_checks()
assert contracts['passed'] and contracts['v34_field_samples'] == 0
for name in ['centre-v34-bounds-started.json', 'centre-v34-bounds-check.json',
             'centre-v34-bounds-failure.json', 'centre-v34-fixture-integrity.json']:
    assert not (HERE/name).exists(), name
assert not list(HERE.glob('diagnostic-centre-v34*'))
assert (HERE/'status.txt').read_text().startswith('Isolated v34 lamina rebuild implementation/proof CLOSED:')

notes_path = HERE/'NOTES.md'
original = notes_path.read_bytes()
assert original.startswith(b'\xef\xbb\xbf')
archive = HERE/'NOTES-before-centre-v34-offline-fixtures.md'
assert not archive.exists()
notes = original.decode('utf-8-sig')
notes = notes.replace(notes.splitlines()[0],
    '# Active: REDIRECT4 — v34 offline fixtures prepared; GPU/cost fixtures next; no runtime', 1)
start = notes.index('## Exact next bounded work')
notes = notes[:start]+'''## v34 offline fixture subphase CLOSED — no numerical field runs
- Prepared check_centre_v34_bounds.py:72000base leaf/reach+12000clearance;five smooth fields/11expanded leaves,FD/certified-segment/cheap≤full/CSG replay gates. Additional cap-join straddles,Gaussian4/6/9 derivative checks and clipped shared-root neighborhoods across all7times/2cameras/2modes. Local attachment samples will not prove global connectivity.
- csg_interval_v34.py expands signed endpoints BEFORE Taylor error and monotone CSG composition. Four synthetic crease/sign/union/quadratic contracts PASS;zero v34 field samples. Python AST PASS. Candidate/oracle/renderer and all historical evidence unchanged;no desktop acceptance/browser/numerical/cost/capture/PNG/inspection.
- centre-v34-offline-fixtures.json binds this partial fixture closure;not a full fixture or numerical gate. Bounds runner requires FUTURE centre-v34-fixture-integrity.json with fixtures_complete=true. No bounds started/check/failure exists. README/status current;latest still inspected REJECTED GAME v33r6 entry. NOTES once,BOM preserved,prior notes archived verbatim.

## Exact next bounded work
Prepare NEW v34 GPU five-base/eleven-expanded-leaf jet fixture and48case/75996ray runner,720fixed+720interval first-root audit using csg_interval_v34.enclosure,and12balanced shared/unshared cost fixture with durable lifecycle. Retain both grids/modes/entry/deep and all prior times incl2.4077/3.5242/4.895. Follow centre-v34-implementation-review.md plus centre-v34-offline-fixtures-review.md;do not copy old nonsmooth a/b Hessian assumptions. Cost identical NEW v34 scalar/march,shared versus full-trace commonParts recomputation;exact hit/count,lower common-prefix work,total/median wall<=1. Not v34-v33r6 speedup. Close complete fixtures into centre-v34-fixture-integrity.json BEFORE any numerical run;then bounds→GPU→independent roots→cost ONCE with unique logs/durable actual exits. Only allPASS permits centre-v34-integrity.json and original1200x800 HIGH/90s capture ONCE. No replay/prewarm/relaxed limits/frame-pump change/promotion.

All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.
'''
readme_path = HERE/'README.md'
readme = readme_path.read_text()
old = 'Next: prepare new smooth-leaf and matched-cost fixtures, then one-shot gates.'
assert readme.count(old) == 1
readme = readme.replace(old,
    'Offline bounds/clearance/attachment and signed-leaf interval fixtures are now prepared; '
    'four synthetic interval contracts and Python AST checks PASS, with zero v34 field samples. '
    'See [offline fixture scope](centre-v34-offline-fixtures-review.md). '
    'Next: prepare GPU/first-root and matched-cost fixtures before one-shot numerical gates.')
with archive.open('xb') as stream:
    stream.write(original)
readme_path.write_text(readme)
(HERE/'status.txt').write_text(
    'Isolated v34 offline fixtures prepared:72000leaf/reach+12000clearance,cap/attachment checks '
    'and11-smooth-leaf interval helper. Four synthetic contracts/AST PASS;zero v34 field samples. '
    'Next GPU/720+720roots/12pair-cost fixture preparation;complete fixture gate required before '
    'any numerical run. No browser/cost/capture/realism claim. latest.png remains inspected '
    'REJECTED GAME v33r6 entry,not v34. Live/defaults/ledgers unchanged;all19/source/coverage/'
    'route/full unfinished;no promotion/replay/prewarm/relaxed limits.\n')
notes_path.write_bytes(b'\xef\xbb\xbf'+notes.encode())
for group in ['files', 'protected']:
    verify(prior[group])
assert digest('latest.png') == prior['display']['latest.png']
files = dict(prior['files'])
for name in names+[START.name, archive.name, 'centre-v34-implementation.json']:
    files[name] = digest(name)
OUT.write_text(json.dumps({'integrity_passed': True, 'static_passed': True,
    'fixtures_complete': False, 'numerical_run': False, 'capture_permitted': False,
    'synthetic_contracts': contracts, 'files': files, 'protected': prior['protected'],
    'display': {n: digest(n) for n in prior['display']}, 'new_images': 0,
    'limits': 'Only offline fixture preparation and synthetic contracts, no v34 numerical field sample/GPU/cost/capture. GPU/root/cost fixture preparation outstanding.'}, indent=2)+'\n')
print(json.dumps({'static_passed': True, 'synthetic_contracts': 4,
                  'v34_field_samples': 0, 'fixtures_complete': False, 'bound_files': len(files)}))
