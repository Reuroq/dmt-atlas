"""One-shot common-prefix reuse candidate; no live edits or browser execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'centre-v33r4-build.json'
assert not OUT.exists(), 'Do not replay this build'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

def save(name, source):
    path = HERE / name
    assert not path.exists(), name
    path.write_text(source)

gate = json.loads((HERE / 'centre-v33r3-timing-integrity.json').read_text())
for group in ['files', 'protected', 'display']:
    for name, expected in gate[group].items():
        assert digest(name) == expected, name

parent = (HERE / 'continuum-v33r3-candidate.js').read_text()
source = parent
edits = []

def change(old, new):
    global source
    assert source.count(old) == 1, old[:100]
    source = source.replace(old, new)
    edits.append({'old': old, 'new': new})

# Extract actual parent expressions, preserving all arithmetic and ordering.
full_start = parent.index('   void fieldPartsReach(')
cheap_start = parent.index('   void cheapParts(')
prefix_start = parent.index('    vec3 q=p-', full_start)
prefix_end = parent.index('    vec4 r6=', prefix_start)
cartesian = parent[prefix_start:prefix_end]
cheap_prefix_start = parent.index('    vec3 q=p-', cheap_start)
cheap_prefix_end = parent.index('    vec4 r6=', cheap_prefix_start)
assert parent[cheap_prefix_start:cheap_prefix_end] == cartesian
sixth = '    vec4 r6=jm(r3,r3)-jm(i3,i3),i6=2.*jm(r3,i3);\n'
assert parent[cheap_prefix_end:].startswith(sixth)
full_sixth = sixth.replace('i3);', 'i3),r18,i18;')
assert parent[prefix_end:].startswith(full_sixth)
signature = parent[full_start:prefix_start]
common = '''   // Same five jets at the same p: retain once across a failed cheap test.
   // No full-only harmonics or shell work on the certified-skip path.
   struct CommonJets { vec4 z; vec4 radius; vec4 inv; vec4 r6; vec4 i6; };
   CommonJets commonParts(vec3 p){
''' + cartesian + sixth + '''    return CommonJets(z,radius,inv,r6,i6);
   }
'''
aliases = '    vec4 z=common.z,radius=common.radius,inv=common.inv,r6=common.r6,i6=common.i6;\n'
shared_signature = signature.replace('fieldPartsReach(vec3 p,', 'fieldPartsReachShared(vec3 p,CommonJets common,')
change(signature + cartesian + full_sixth,
       common + shared_signature + aliases + '    vec4 r18,i18;\n')
wrapper = signature + '''    fieldPartsReachShared(p,commonParts(p),f,a,b,axA,axB,angA,angB,shellA,shellB);
   }

'''
change('   void fieldParts(vec3 p,', wrapper + '   void fieldParts(vec3 p,')
cheap_signature = parent[cheap_start:cheap_prefix_start]
change(cheap_signature + cartesian + sixth,
       cheap_signature.replace('cheapParts(vec3 p,', 'cheapPartsShared(vec3 p,CommonJets common,') + aliases)
cheap_wrapper = cheap_signature + '''    cheapPartsShared(p,commonParts(p),f,axA,axB);
   }
'''
change('   float cheapReach(vec3 p,vec3 rd){\n    vec4 f,axA,axB;cheapParts(p,f,axA,axB);',
       cheap_wrapper + '   float cheapReach(vec3 p,vec3 rd,CommonJets common){\n    vec4 f,axA,axB;cheapPartsShared(p,common,f,axA,axB);')
change('   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){\n    vec4 f,a,b,axA,axB,angA,angB,shellA,shellB;float layer;\n    fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);',
       '   vec4 traceSample(vec3 p,vec3 rd,CommonJets common,out float safeStep){\n    vec4 f,a,b,axA,axB,angA,angB,shellA,shellB;float layer;\n    fieldPartsReachShared(p,common,f,a,b,axA,axB,angA,angB,shellA,shellB);')
change('     float fastStep=cheapReach(p,rd);',
       '     CommonJets common=commonParts(p);\n     float fastStep=cheapReach(p,rd,common);')
change('     float safeStep;sampleValue=traceSample(p,rd,safeStep);',
       '     float safeStep;sampleValue=traceSample(p,rd,common,safeStep);')

restored = source
for edit in reversed(edits):
    assert restored.count(edit['new']) == 1
    restored = restored.replace(edit['new'], edit['old'])
assert restored.encode() == (HERE / 'continuum-v33r3-candidate.js').read_bytes()
save('continuum-v33r4-candidate.js', source)
save('centre-v33r4-edits.json', json.dumps(edits, indent=2) + '\n')
# Independent scalar implementation is intentionally byte-identical, not ported
# from the new GLSL, so subsequent FD/reach/root checks retain an outside oracle.
save('field_centre_v33r4.py', (HERE / 'field_centre_v33r3.py').read_text())
prior = json.loads((HERE / 'centre-v33r3-build.json').read_text())
save(OUT.name, json.dumps({
    'candidate': 'continuum-v33r4-candidate.js', 'sha256': digest('continuum-v33r4-candidate.js'),
    'parent': 'continuum-v33r3-candidate.js', 'parent_sha256': digest('continuum-v33r3-candidate.js'),
    'parent_gate_sha256': digest('centre-v33r3-timing-integrity.json'),
    'lower_H_upper': prior['lower_H_upper'], 'analytic': prior['analytic'],
    'cheap_threshold': .08, 'shared_jets': ['z', 'radius', 'inv', 'r6', 'i6'],
    'edit_count': len(edits), 'exact_parent_after_reversing_edits': True,
    'protected': gate['protected'], 'display': gate['display'],
    'state': 'IMPLEMENTED; GLSL, numerical, cost and visual validation PENDING. No promotion.',
    'limits': 'Fewer source-level duplicate prefix evaluations, not measured GPU savings. Struct lifetime may increase register/compilation cost; frame pump unchanged.'
}, indent=2) + '\n')
print('v33r4 built: seven reversible edits, five shared jets, unchanged scalar oracle; no probes run.')
