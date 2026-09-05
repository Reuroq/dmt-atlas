"""Verify the four immutable diagnostic receipts and unchanged live display."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    out=HERE/'diagnostic-chrysanthemum-v23-check.json'
    assert not out.exists(), 'One-shot diagnostic verification record already exists'
    captures=[]
    for suffix in ['entry','deep','material-entry','material-deep']:
        receipt=HERE/f'diagnostic-chrysanthemum-v23-{suffix}.json'
        r=json.loads(receipt.read_text())
        assert digest(HERE/r['file'])==r['capture_sha256']
        for name,sha in r['source_hashes'].items():
            assert digest(HERE/name)==sha,name
        d=r['capture_diagnostics']
        assert d['detail']=='high' and d['paused'] and not d['renderPending']
        assert d['renderedAnimTime']==d['animTime'] and d['stage']=='chrysanthemum'
        assert not r['errors'] and not d['missingEvidence'] and d['uncitedMeshes']==0
        captures.append({'receipt':receipt.name,'receipt_sha256':digest(receipt),
                         'file':r['file'],'sha256':r['capture_sha256'],
                         'position':d['position'],'animTime':d['animTime']})
    assert digest(HERE/'continuum.js')==digest(HERE/'continuum-v22.js')=='db2b4e328ba49b0157a7dd2b988d28cb10bcdda5d646557419b20880ef32db2e'
    for display,archive in [('latest.png','realism-chrysanthemum-close-v22-motion.png'),
                            ('visual-chrysanthemum.png','realism-chrysanthemum-close-v22.png'),
                            ('visual-chrysanthemum.json','realism-chrysanthemum-close-v22.json')]:
        assert digest(HERE/display)==digest(HERE/archive),display
    result={'pass':True,'diagnostic_only':True,'runtime':'v22 unchanged',
            'coverage_or_realism_regrade':False,'captures':captures,
            'display':'Reviewed v22 deep motion unchanged',
            'finding':'Environment radiance is the main source of widespread contour loops in four inspected plates; root differences are sparse, not proven safe',
            'review_sha256':digest(HERE/'diagnostic-chrysanthemum-v23-review.md'),
            'tool_hashes':{p.name:digest(p) for p in [HERE/'build_diagnostic_v23.py',HERE/'build_diagnostic_material_v23.py',HERE/'render_diagnostic_v23.py',HERE/'render_diagnostic_material_v23.py']}}
    out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four diagnostic PNG/receipt/dependency hashes, HIGH settled provenance, unchanged v22 runtime/display')
if __name__=='__main__':
    main()
