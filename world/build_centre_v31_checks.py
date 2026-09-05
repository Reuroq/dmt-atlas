"""Prepare changed-field checks and real-input fixture; no old probes replayed."""
from pathlib import Path
import ast

HERE=Path(__file__).resolve().parent

def changed(source,old,new):
    assert old in source,old[:100]
    return source.replace(old,new)

def save(name,source):
    target=HERE/name
    assert not target.exists()
    ast.parse(source)
    target.write_text(source)

def geometry(source):
    for old,new in [('.19','.065'),('.10','.16'),('.32','.45'),('.40','.18'),('.055','.03'),('f+9','f+12'),('fl+9','fl+12')]:
        source=changed(source,old,new) if old in source else source
    return source

source=(HERE/'check_centre_v30_bounds.py').read_text().replace('v30','v31')
source=source.replace('PIXEL,parts,field','PIXEL,parts,field,analytic_bounds')
source=source.replace('30001','31001').replace('uniform(5.05,18,n)','uniform(4.85,22,n)')
source=changed(source,'L,M=13+12*pixel,160+250*pixel+600*pixel**2',
    'L=12+10*pixel\n    Ms=np.array([11,22,140])+np.array([2,13,140])*pixel+np.array([2,10,170])*pixel**2')
source=changed(source,'def reach(v,deriv):','def reach(v,deriv,M):')
start=source.index('            petals=')
end=source.index('            free=',start)
source=source[:start]+'''            mf,ma,mb=Ms
            petals=np.maximum(reach(f,df,mf),np.maximum(reach(abs(a)-.065,np.sign(a)*da,ma),
                np.minimum(reach(.16+b,db,mb),reach(.16-b,-db,mb))))
            branches=np.maximum(reach(f+.45,df,mf),np.maximum(reach(abs(a)-.18,np.sign(a)*da,ma),reach(abs(b)-.03,np.sign(b)*db,mb)))
            step=np.minimum(np.minimum(petals,branches),reach(f+12,df,mf))
'''+source[end:]
source=changed(source,'float(np.max(abs(curvature))/M)','float(np.max(abs(curvature)/Ms))')
source=source.replace('5.479','4.899').replace('[4,10,26]','[3,8,20]')
start=source.index('# Symbolic recurrence')
end=source.index('after={',start)
source=source[:start]+'''# Independently computed analytic coefficients, not shader-extracted constants.
analytic=analytic_bounds()
assert np.all(np.array(analytic['leaf_H_polynomials'])<np.array([[11,2,2],[22,13,10],[140,140,170]]))
assert analytic['branch'][0]+.25*analytic['fine'][0]<12
assert np.exp(-.5)*(8+.25*20)<10
'''+source[end:]
source=changed(source,"'recurrence_L':Ls,'recurrence_H':Hs,'b_H_polynomial':b_hessian,","'analytic':analytic,")
source=changed(source,"'recurrence_H':Hs,'b_H_polynomial':b_hessian,'clearance':clearance", "'analytic':analytic,'clearance':clearance")
save('check_centre_v31_bounds.py',source)

source=(HERE/'probe_numeric_candidate_v30.py').read_text().replace('v30','v31')
save('probe_numeric_candidate_v31.py',source)

source=(HERE/'audit_centre_v30_first_roots_r2.py').read_text().replace('v30','v31')
source=source.replace('first-root-check-r2','first-root-check')
source=source.replace('160+250*PIXEL+600*PIXEL**2','140+140*PIXEL+170*PIXEL**2')
source=geometry(source).replace('<5.48','<4.9')
source=source.replace('Original .003 grid FAIL retained.', 'Original .003 grid result retained separately.')
source=source.replace('Retains failed fixed-grid receipt.', 'Retains the independent fixed-grid receipt.')
save('audit_centre_v31_first_roots.py',source)

source=(HERE/'render_centre_v30.py').read_text().replace('v30','v31')
start=source.index("                    mark('real walk")
end=source.index('                first = capture',start)
source=source[:start]+'''                    mark('real walk to z -6; timer-observed stop and native pause')
                    before_walk=diag(page)
                    page.keyboard.press('Space')
                    page.keyboard.down('w')
                    try:
                        # RAF polling can wait behind an expensive frame while
                        # the independent movement timer keeps integrating input.
                        # This is a fixture change, not a proven cause of v30.
                        page.wait_for_function('journeyDiagnostics().stage!=="chrysanthemum" || journeyDiagnostics().position[2]<=-6', polling=50, timeout=45000)
                        observed_stop=diag(page)
                    finally:
                        page.keyboard.up('w')
                    page.keyboard.press('Space')
                    stopped=diag(page)
                    timings.append({'operation': operation, 'wall_seconds': time.monotonic()-operation_start,
                        'before':before_walk,'observed_stop':observed_stop,'after_release_pause':stopped,
                        'polling_ms':50,'native_controls':True})
                    save()
                    assert stopped['stage']=='chrysanthemum' and not stopped['transition']
                    assert -8<=stopped['position'][2]<=-6, 'Deep stop overshoot; do not accept wrong pose'
'''+source[end:]
source=source.replace("                page.locator('#pause').click()\n                page.wait_for_function('(t)=>journeyDiagnostics().animTime>=t', arg=first['animTime']+3)\n                page.locator('#pause').click()",
    "                page.keyboard.press('Space')\n                page.wait_for_function('(t)=>journeyDiagnostics().animTime>=t', arg=first['animTime']+3, polling=50)\n                page.keyboard.press('Space')")
save('render_centre_v31.py',source)
print('Prepared v31 bounds/GPU/interval checks and HIGH real-input timer-observed capture; no runs.')
