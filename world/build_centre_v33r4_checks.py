"""Prepare fresh v33r4 fixtures; never execute historical probes."""
import ast
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

def save(name, source):
    assert not (HERE / name).exists(), name
    (HERE / name).write_text(source)

def change(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new)

def versioned(name):
    return (HERE / name).read_text().replace('v33r3', 'v33r4')

probe = versioned('gpu_probe_v33r3_candidate.html')
probe = probe.replace('cheapReach(p,rd)', 'cheapReach(p,rd,common)')
probe = probe.replace('traceSample(p,rd,safeStep)', 'traceSample(p,rd,common,safeStep)')
save('gpu_probe_v33r4_candidate.html', probe)
leaves = versioned('gpu_probe_v33r3_leaves.html')
# Exercise exactly the shared path used by the marcher, not just fresh wrappers.
leaves = change(leaves, ' fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);',
    ' CommonJets common=commonParts(p);\n fieldPartsReachShared(p,common,f,a,b,axA,axB,angA,angB,shellA,shellB);')
leaves = change(leaves, 'cheapParts(p,cheapF,cheapA,cheapB);', 'cheapPartsShared(p,common,cheapF,cheapA,cheapB);')
save('gpu_probe_v33r4_leaves.html', leaves)

bounds = versioned('check_centre_v33r3_bounds.py')
bounds = change(bounds, '[4.,4.895,8.,221.,900.]', '[2.4077,3.5242,4.,4.895,8.,221.,900.]')
save('check_centre_v33r4_bounds.py', bounds)
numeric = versioned('probe_numeric_candidate_v33r3.py')
numeric = change(numeric, '[(48,32,[4,4.895,8]), (49,33,[4,4.895,8,221,900])]',
    '[(48,32,[2.4077,3.5242,4,4.895,8]), (49,33,[2.4077,3.5242,4,4.895,8,221,900])]')
numeric = change(numeric, 'len(root_errors)==32*15', 'len(root_errors)==48*15')
numeric = change(numeric, 'times4/4.895/8/221/900', 'times2.4077/3.5242/4/4.895/8/221/900')
save('probe_numeric_candidate_v33r4.py', numeric)
roots = change(versioned('audit_centre_v33r3_first_roots.py'), 'len(flat)==480', 'len(flat)==720')
save('audit_centre_v33r4_first_roots.py', roots)
save('render_centre_v33r4.py', versioned('render_centre_v33r3.py'))
save('centre-v33r4-bounds.md', '''# v33r4 — common-prefix reuse only

The scalar oracle and every analytic bound are unchanged from v33r3. See
[parent derivation](centre-v33r3-bounds.md) and its v33r2 references. v33r4
factors the identical Cartesian/radius/inverse/cube expressions into commonParts.
Five jets (z, radius, inv, r6, i6) are constructed once at p after the envelope
test and passed to both cheap and full evaluations. Full-only r18/r36, shells,
angular costs and materials stay outside the cheap path. Standalone field/cheap
wrappers compute their own common prefix for independent calls and refinement.

Seven reversible edits recover the parent byte-for-byte; scalar and material
expressions, filter, MAX/MIN composition, padded lower leaves, .08 branch,
.4 reach cap, budgets, brackets and controls are unchanged. This structural
claim is not GLSL compilation, floating-point equivalence or performance proof.

Prepared validation retains independent scalar/FD/reach/clearance/fixed-grid
and first-root interval tests, with HIGH/LOW entry/deep and both grids at
2.4077, 3.5242 and 4.895. 48 GPU cases/75996 rays,
720 fixed-grid and 720 interval references. No universal convergence or
directed-rounding GPU proof. No numerical, cost or visual gate has run yet.
''')

# Check fixture syntax and shader-patch anchor uniqueness against actual source.
# No WebGL context, browser, screenshot or timing probe.
candidate = (HERE / 'continuum-v33r4-candidate.js').read_text()
for anchor in ['vec4 sampleValue=vec4(0.);', 'p=ro+rd*distanceAlong;\n     float bound=',
    'float fastStep=cheapReach(p,rd,common);', 'distanceAlong+=fastStep;havePrevious=false;',
    'float safeStep;sampleValue=traceSample(p,rd,common,safeStep);',
    'float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;', '    vec3 color;']:
    assert candidate.count(anchor) == 1, anchor
for name in ['build_centre_v33r4.py', Path(__file__).name, 'field_centre_v33r4.py',
             'check_centre_v33r4_bounds.py', 'probe_numeric_candidate_v33r4.py',
             'audit_centre_v33r4_first_roots.py', 'render_centre_v33r4.py']:
    ast.parse((HERE / name).read_text(), filename=name)
subprocess.run(['node', '--check', str(HERE / 'continuum-v33r4-candidate.js')], check=True)
for source in [probe, leaves]:
    inline = re.findall(r'<script>([\s\S]*?)</script>', source)
    assert len(inline) == 1
    subprocess.run(['node', '--check'], input=inline[0], text=True, check=True)
print('Prepared 48 GPU cases / 75996 rays / 720 first roots; JS/AST and unique anchors PASS. No numerical run.')
