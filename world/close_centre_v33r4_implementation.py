"""Close static implementation/preparation only; no numerical or render runs."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r4-implementation.json'
assert not OUT.exists(), 'Do not replay closure'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def save(name, source):
    assert not (HERE / name).exists(), name
    (HERE / name).write_text(source)

old_gate = json.loads((HERE / 'centre-v33r3-timing-integrity.json').read_text())
for group in ['files', 'protected', 'display']:
    assert all(digest(n) == h for n, h in old_gate[group].items()), group
parent = (HERE / 'continuum-v33r3-candidate.js').read_text()
candidate = (HERE / 'continuum-v33r4-candidate.js').read_text()
restored = candidate
edits = json.loads((HERE / 'centre-v33r4-edits.json').read_text())
assert len(edits) == 7
for edit in reversed(edits):
    assert restored.count(edit['new']) == 1
    restored = restored.replace(edit['new'], edit['old'])
assert restored.encode() == (HERE / 'continuum-v33r3-candidate.js').read_bytes()
assert digest('field_centre_v33r4.py') == digest('field_centre_v33r3.py')
assert (HERE / 'render_centre_v33r4.py').read_text() == (HERE / 'render_centre_v33r3.py').read_text().replace('v33r3', 'v33r4')
build = json.loads((HERE / 'centre-v33r4-build.json').read_text())
assert build['sha256'] == digest('continuum-v33r4-candidate.js')

# Stronger local expression checks than general edit reversibility: both suffixes
# are literally unchanged after the common prefix; certificate bodies and main
# control flow only differ in common-jet plumbing.
def section(source, start, end):
    return source[source.index(start):source.index(end, source.index(start))]

full_tail = '    cubePair(r6,i6,r18,i18);'
assert section(parent, full_tail, '   void fieldParts(vec3 p,').rstrip() == section(candidate, full_tail, '   void fieldPartsReach(vec3 p,').rstrip()
cheap_tail = '    vec4 radial=offset(1.35*radius+.12*z+.15*r6,-time*.12);'
parent_cheap = section(parent, '   void cheapParts(', '   float cheapReach(')
candidate_cheap = section(candidate, '   void cheapPartsShared(', '   void cheapParts(')
assert parent_cheap[parent_cheap.index(cheap_tail):] == candidate_cheap[candidate_cheap.index(cheap_tail):]
def normalize(source):
    return source.replace(',CommonJets common', '').replace('(p,rd,common', '(p,rd').replace(
        'cheapPartsShared(p,common,', 'cheapParts(p,').replace(
        'fieldPartsReachShared(p,common,', 'fieldPartsReach(p,').replace(
        '     CommonJets common=commonParts(p);\n', '')
assert section(parent, '   float cheapReach(', '   vec4 traceSample(') == normalize(section(candidate, '   float cheapReach(', '   vec4 traceSample('))
assert parent[parent.index('   vec4 traceSample('):] == normalize(candidate[candidate.index('   vec4 traceSample('):])

# Dedicated paired-cost fixtures: same instrumentation, independently loaded
# materials, same readback boundary. No old runner or old evidence is replayed.
cost_sources = {}
for arm, version in [('parent', 'v33r3'), ('candidate', 'v33r4')]:
    html = (HERE / f'gpu_probe_{version}_candidate.html').read_text()
    html = re.sub(r'<title>.*?</title>', f'<title>New v33r4 paired cost — {arm}; not journey evidence</title>', html)
    cost_sources[arm] = html
    save(f'gpu_cost_v33r4_{arm}.html', html)
assert normalize(cost_sources['candidate']).replace('v33r4-candidate.js', 'v33r3-candidate.js').replace('— candidate;', '— parent;') == cost_sources['parent']
scripts = ['build_centre_v33r4.py', 'build_centre_v33r4_checks.py', 'field_centre_v33r4.py',
           'check_centre_v33r4_bounds.py', 'probe_numeric_candidate_v33r4.py',
           'audit_centre_v33r4_first_roots.py', 'measure_centre_v33r4_cost.py',
           'render_centre_v33r4.py', Path(__file__).name]
for name in scripts:
    ast.parse((HERE / name).read_text(), filename=name)
subprocess.run(['node', '--check', str(HERE / 'continuum-v33r4-candidate.js')], check=True)
for name in ['gpu_probe_v33r4_candidate.html', 'gpu_probe_v33r4_leaves.html',
             'gpu_cost_v33r4_parent.html', 'gpu_cost_v33r4_candidate.html']:
    inline = re.findall(r'<script>([\s\S]*?)</script>', (HERE / name).read_text())
    assert len(inline) == 1
    subprocess.run(['node', '--check'], input=inline[0], text=True, check=True)
assert not list(HERE.glob('diagnostic-centre-v33r4*'))
for name in ['centre-v33r4-bounds-check.json', 'numeric-candidate-v33r4-raw.json',
             'centre-v33r4-first-root-check.json', 'centre-v33r4-cost-raw.json', 'centre-v33r4-integrity.json']:
    assert not (HERE / name).exists(), name

next_step = ('Run check_centre_v33r4_bounds.py, probe_numeric_candidate_v33r4.py, '
    'audit_centre_v33r4_first_roots.py, then measure_centre_v33r4_cost.py ONCE each, '
    'sequentially with saved unique logs and inspection of each exit/result. Use '
    'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/clawd/pixelvision-venv/lib/python3.12/site-packages '
    'PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright. No browser/GLSL run has occurred. '
    'Numerical grid:48cases/75996rays/720fixed+720interval roots; clocks2.4077/3.5242/4.895 '
    'on both grids,HIGH/LOW,entry/deep. Cost is a NEW 12-pair balanced-order parent/candidate '
    'experiment, identical instrumentation/boundaries, no warmup; partial receipt prevents replay. '
    'Cost hold if bitwise hits/counters differ, inferred prefix work worsens, or either '
    'total/median paired wall cost worsens. This conservative gate is not a significance '
    'test or full-resolution prediction. If all checks pass, close numerical evidence '
    'in centre-v33r4-integrity.json (must include protected/files,integrity_passed,numeric_passed '
    'and cost gate); only then run unchanged-version-only render_centre_v33r4.py ONCE '
    'at original1200x800 HIGH/90000ms with native controls. No prewarm,frame-pump change, '
    'relaxed limits,unchanged historical reruns or promotion on failure.')
review = '''# v33r4 implementation CLOSED — numerical/cost/visual gates pending

Five unchanged jets (z, radius, inv, r6, i6) are computed once at each p after
the envelope test and shared across cheap/full evaluation. The cheap skip path
does no full-only harmonics or shell work. Standalone field/cheap wrappers
construct a fresh prefix where necessary. No live or frame-pump changes.

Static PASS: seven reversed edits recover v33r3 byte-for-byte; cheap/full suffix
expressions remain exact; normalized certificates, marcher and all material
code are byte-identical; independent scalar oracle is byte-identical; original
renderer differs only by version. JS/AST and instrumentation anchors pass.
This does NOT establish GLSL compilation, runtime equivalence, performance,
convergence, imagery or realism. Extra live jets may increase register cost.

Expanded independent checks and a new balanced paired-cost fixture are prepared,
not run. Numerical and original capture gates remain pending. No new PNG or
inspection; latest.png is unchanged, labelled REJECTED GAME v32 deep-motion.
All19 realism,16 source gates,coverage,route/full acceptance remain unfinished.

## Next

''' + next_step + '\n'
save('centre-v33r4-implementation-review.md', review)

readme = (HERE / 'README.md').read_text()
old = 'Next: isolated shared-jet-prefix optimization, independently revalidated before\none fresh original1200x800 HIGH/90s capture. No frame-pump change or limit relaxation.'
new = ('Isolated **v33r4 shared-prefix implementation is complete**, static checks PASS;\n'
       'numerical/cost/visual gates PENDING. Five unchanged jets are shared after a failed\n'
       'cheap certificate. No speedup claim. Expanded clock coverage and a new paired-cost\n'
       'experiment are prepared before any original1200x800 HIGH/90s capture. See\n'
       '[implementation and next gates](centre-v33r4-implementation-review.md).\n'
       'No frame-pump change or limit relaxation.')
assert readme.count(old) == 1
(HERE / 'README.md').write_text(readme.replace(old, new))
(HERE / 'status.txt').write_text('Isolated v33r4 implementation CLOSED:five shared jets,seven reversible edits,static JS/AST/expression checks PASS. Numerical/cost/visual PENDING;48cases/75996rays/720roots and new12-pair cost fixture prepared,not run. No speedup claim,no frame-pump change,no capture or promotion. latest.png remains inspected labelled REJECTED GAME v32 deep-motion. Live v25/trip18/HUD,defaults/ledgers unchanged;all19/source/coverage/route/full unfinished.\n')
notes_raw = (HERE / 'NOTES.md').read_bytes()
archive = HERE / 'NOTES-before-centre-v33r4-implementation.md'
assert not archive.exists()
archive.write_bytes(notes_raw)
notes = notes_raw.decode('utf-8-sig')
notes = notes.replace('# Active: REDIRECT4 — v33r3 timing CLOSED; asynchronous completion delay',
                      '# Active: REDIRECT4 — v33r4 implementation CLOSED; validation next', 1)
notes = notes[:notes.index('## Exact next bounded work')] + '''## v33r4 implementation CLOSED — no numerical/browser run
- Built from unchanged continuum-v33r3-candidate.js,not timing copies. CommonJets retains z/radius/inv/r6/i6 once after envelope for cheap/full paths; wrappers preserve standalone calls. All scalar/material/certificate/march expressions unchanged;no full-only work on cheap skip.
- Seven reversible edits recover parent byte-for-byte. Exact suffix/normalized-control checks,independent scalar byte-equality,JS/AST and unique instrumentation anchors PASS. No GLSL compile or runtime/cost/realism claim. Extra live jets may worsen registers/compilation.
- Prepared bounds/clearance/GPU/independent first-root fixtures:48cases/75996rays,720fixed+720interval references;2.4077/3.5242/4.895 on both grids,HIGH/LOW,entry/deep. Prepared NEW matched12-pair cost experiment (balanced order,same instrumentation/boundaries,no warmup);not historical probe rerun. No numerical fixture or browser has run.
- centre-v33r4-implementation.json binds new sources/fixtures and prior protected/display. README/status updated;NOTES once,BOM preserved,old notes archived. No new PNG/inspection;latest unchanged,no promotion. Original renderer version-only copy still requires passing numerical closure.

## Exact next bounded work
''' + next_step + '\n\nAll19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.\n'
(HERE / 'NOTES.md').write_bytes(b'\xef\xbb\xbf' + notes.encode())
files = scripts + ['continuum-v33r4-candidate.js', 'centre-v33r4-build.json',
    'centre-v33r4-edits.json', 'centre-v33r4-bounds.md', 'centre-v33r4-implementation-review.md',
    'gpu_probe_v33r4_candidate.html', 'gpu_probe_v33r4_leaves.html',
    'gpu_cost_v33r4_parent.html', 'gpu_cost_v33r4_candidate.html',
    'build-centre-v33r4.log', 'build-centre-v33r4-checks.log', archive.name,
    'centre-v33r3-timing-integrity.json', 'continuum-v33r3-candidate.js']
assert all(digest(n) == h for n, h in old_gate['protected'].items())
OUT.write_text(json.dumps({'static_passed': True, 'numerical_run_count': 0,
    'browser_run_count': 0, 'new_images': 0, 'inspections': 0,
    'exact_reversal': True, 'exact_expression_checks': True,
    'files': {n: digest(n) for n in files}, 'protected': old_gate['protected'],
    'display': {n: digest(n) for n in old_gate['display']}, 'next': next_step}, indent=2) + '\n')
print(f'v33r4 static closure PASS: {len(files)} files,17 protected,zero browser runs/PNGs; numerical/cost pending.')
