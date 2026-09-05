"""One-shot receipt/runtime checks; not acceptance or a realism grade."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE/'diagnostic-occlusion-v24-check.json'
assert not OUT.exists(), 'Do not replay completed checks'
def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
before = json.loads((HERE/'diagnostic-occlusion-v24-runtime-before.json').read_text())
assert all(digest(name)==sha for name,sha in before.items()), 'Live runtime changed'
assert digest('continuum.js')==digest('continuum-v23.js')
assert digest('trip.js')==digest('trip-v16.js')
prefix = 'diagnostic-chrysanthemum-v24-occlusion'
receipts = []
for label in ['entry','deep']:
    stem = f'{prefix}-{label}'
    receipt = json.loads((HERE/f'{stem}.json').read_text())
    d = receipt['capture_diagnostics']
    assert digest(stem+'.png') == receipt['capture_sha256']
    assert all(digest(name)==sha for name,sha in receipt['source_hashes'].items())
    assert d['stage']=='chrysanthemum' and d['detail']=='high' and d['paused']
    assert not d['transition'] and not d['renderPending']
    assert d['animTime']==d['renderedAnimTime']
    assert not receipt['errors'] and not d['missingEvidence'] and d['uncitedMeshes']==0
    with Image.open(HERE/f'{stem}.png') as im:
        assert im.size==(1800,800)
    receipts.append(receipt)
assert receipts[0]['capture_diagnostics']['position']==[0,1.7,8]
assert -22 < receipts[1]['capture_diagnostics']['position'][2] <= -6
assert len({r['capture_sha256'] for r in receipts})==2
subprocess.run(['node','--check',str(HERE/'diagnostic-occlusion-v24.js')],check=True)
for name in ['build_diagnostic_occlusion_v24.py','render_diagnostic_occlusion_v24.py']:
    compile((HERE/name).read_text(),name,'exec')
shutil.copyfile(HERE/f'{prefix}-deep.png',HERE/'latest.png')
assert digest('latest.png')==receipts[1]['capture_sha256']
assert digest('visual-chrysanthemum.png')==digest('idle-reduced-v16.png')
assert digest('visual-chrysanthemum.json')==digest('idle-reduced-v16.json')
artifacts = [f'{prefix}-{label}.{ext}' for label in ['entry','deep'] for ext in ['png','json']]
artifacts += [f'{prefix}-receipts.json','diagnostic-occlusion-v24.js','diagnostic-occlusion-v24.html',
              'build_diagnostic_occlusion_v24.py','render_diagnostic_occlusion_v24.py',
              'build_diagnostic_occlusion_v24-initial.py','diagnostic-occlusion-v24-initial-failure.json',
              'render-diagnostic-occlusion-v24.log','diagnostic-occlusion-v24-runtime-before.json',
              'diagnostic-occlusion-v24-review.md','check_diagnostic_occlusion_v24.py']
OUT.write_text(json.dumps({'diagnostic_checks':'PASS','runtime_unchanged':before,
    'additional_dependencies':{name:digest(name) for name in ['beings.js','fidelity-ui.js','verify.py']},
    'artifacts':{name:digest(name) for name in artifacts},
    'latest':'inspected deep diagnostic plate, not a qualifying realism capture',
    'default_capture':'idle-reduced-v16 entry; unchanged',
    'inspection':'Both plates inspected once with view_image after renderer completion',
    'visual_observation':'GAME; recess causes hard patches; visibility dims broadly; axial fan persists',
    'unresolved':'Sparse rim misses, geometry/realism, stale coverage, physical exit and overall gates',
    'acceptance_rerun':False,'grades_changed':False,'overall_complete':False},indent=2)+'\n')
print('PASS: fresh diagnostic receipts, settled HIGH states, syntax, runtime equality and display hashes; overall unfinished')
