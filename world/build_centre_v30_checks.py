"""One-shot changed-field probes; no historical evidence or live edits."""
from pathlib import Path
import ast

HERE=Path(__file__).resolve().parent
target=HERE/'probe_numeric_candidate_v30.py'
assert not target.exists()
source=(HERE/'probe_numeric_candidate_v29.py').read_text().replace('v29','v30')
source=source.replace('from field_centre_v30 import field','from field_centre_v30 import field, parts, compose_jets')
def replace(old,new):
    global source
    assert source.count(old)==1,old[:80]
    source=source.replace(old,new)
replace("        page.goto((HERE/'gpu_probe_v30_candidate.html').as_uri())", """        page.goto((HERE/'gpu_probe_v30_candidate.html').as_uri())
        leaf_page=browser.new_page()
        leaf_page.on('pageerror',lambda e:errors.append(str(e)))
        leaf_page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        leaf_page.goto((HERE/'gpu_probe_v30_leaves.html').as_uri())""")
replace("                        cases.append(case)","""                        case['leaves']=leaf_page.evaluate('c=>auditLeaves(c)',case)
                        cases.append(case)""")
replace("        eps = 1e-4", """        eps = 1e-4
        leaf_scalar=np.stack(parts(actual,t,camera,high),axis=1)
        leaf_fd=np.stack([(np.stack(parts(actual+np.eye(3)[a]*eps,t,camera,high),axis=1)-np.stack(parts(actual-np.eye(3)[a]*eps,t,camera,high),axis=1))/(2*eps) for a in range(3)],axis=-1)
        jets=np.stack([np.array(case['leaves'][key]).reshape(-1,4) for key in ['base','apertureA','apertureB']],axis=1)
        selected=compose_jets(jets)
        composed=np.array(case['leaves']['composed']).reshape(-1,4)
        leaf_scalar_error=float(np.max(abs(leaf_scalar-jets[:,:,3])))
        leaf_gradient_error=float(np.max(abs(leaf_fd-jets[:,:,:3])))
        csg_error=float(np.max(abs(selected-composed)))
        replay_error=float(np.max(abs(composed[:,:3]-grad[:,:3])))""")
replace("        summary['passed'] = (summary['misses']==0 and summary['max_gradient_error']<.005", """        discrepancies=np.flatnonzero(np.max(abs(finite-grad[:,:3]),axis=1)>.005)
        summary.update({'max_all_leaf_scalar_error':leaf_scalar_error,
            'max_all_leaf_gradient_error':leaf_gradient_error,
            'max_csg_replay_error':csg_error,'max_saved_gradient_replay_error':replay_error,
            'composite_fd_discrepancies':[{'ray':int(j),'error':float(np.max(abs(finite[j]-grad[j,:3]))),'actual_leaf_values':jets[j,:,3].tolist()} for j in discrepancies]})
        summary['passed'] = (summary['misses']==0 and leaf_gradient_error<.005
                             and leaf_scalar_error<.001 and csg_error==0 and replay_error==0""")
replace("'build_centre_candidate_v30.py','gpu_probe_v30_candidate.html'", "'build_centre_candidate_v30.py','build_centre_v30_checks.py','gpu_probe_v30_leaves.html','gpu_probe_v30_candidate.html'")
replace("'method':'Actual float GLSL fields, analytic gradients and .4 bounds versus independent float64 field/finite differences. Original six plus central 3x3 .003 first-sign-crossing scans. Even legacy grids and odd exact-axis grids. Late times 221/900s. Sparse numerical evidence only; no universal root, precision, performance or realism proof.'", "'method':'New v30 actual float GLSL rays plus all smooth-leaf jets at saved actual roots. Independent float64 scalar/leaf FD; exact float32 CSG selection and original normal replay. Composite FD disagreements retained at creases, not a unique-normal assertion. Original six plus central3x3 dense .003 first-crossing references, even/odd grids, HIGH/LOW, entry/deep, times4/8/221/900. Sampled evidence only; no universal convergence, filtering, realism or performance proof.'")
replace("    print(json.dumps([{k:v for k,v in s.items() if k not in ['references','gpu_three_readbacks_seconds']} for s in summaries]),flush=True)", "    print(json.dumps({'failed_cases':[{k:v for k,v in s.items() if k not in ['references','composite_fd_discrepancies']} for s in summaries if not s['passed']], 'composite_fd_discrepancies':sum(len(s['composite_fd_discrepancies']) for s in summaries)}),flush=True)")
ast.parse(source)
target.write_text(source)
print('Created integrated new-field GPU ray/leaf/first-root probe, strict original tolerances.')
