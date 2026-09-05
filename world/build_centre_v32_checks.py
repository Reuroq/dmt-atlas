"""Prepare checks for changed v32 field; preserve completed v31 evidence."""
from pathlib import Path

HERE=Path(__file__).resolve().parent

def save(name,source):
    path=HERE/name
    assert not path.exists(),name
    path.write_text(source)

def geometry(source):
    # Only literals belonging to CSG expressions, not thresholds/test tolerances.
    for old,new in [('abs(a)-.065','abs(a)-.10'),('.16+b','.035+b'),('.16-b','.035-b'),
        ('.16-abs(b)','.035-abs(b)'),('abs(a)-.18','abs(a)-.25'),
        ('abs(b)-.03','abs(b)-.014'),('f+.45','f+.38'),('f+12','f+10'),
        ('al-.065','al-.10'),('.16-bu','.035-bu'),('al-.18','al-.25'),
        ('bl-.03','bl-.014'),('fl+.45','fl+.38'),('fl+12','fl+10')]:
        source=source.replace(old,new)
    return source

source=geometry((HERE/'check_centre_v31_bounds.py').read_text().replace('v31','v32'))
source=source.replace('31001','32001').replace('uniform(4.85,22,n)','uniform(5.4,22,n)')
source=source.replace('12+10*pixel','16+8*pixel')
source=source.replace('[11,22,140]','[7,305,87]').replace('[2,13,140]','[1,190,65]').replace('[2,10,170]','[1,110,54]')
source=source.replace('4.899','5.449').replace('[3,8,20]','[4,12,36]')
start=source.index("assert np.all(np.array(analytic['leaf_H_polynomials'])")
end=source.index('after={',start)
source=source[:start]+'''assert np.all(np.array(analytic['leaf_H_polynomials'])<np.array([[7,1,1],[305,190,110],[87,65,54]]))
assert max(analytic['leaf_L_constants'])<16
assert max(analytic['leaf_L_pixel'])<8
'''+source[end:]
save('check_centre_v32_bounds.py',source)
save('probe_numeric_candidate_v32.py',(HERE/'probe_numeric_candidate_v31.py').read_text().replace('v31','v32'))
source=geometry((HERE/'audit_centre_v31_first_roots.py').read_text().replace('v31','v32'))
source=source.replace('140+140*PIXEL+170*PIXEL**2','305+190*PIXEL+110*PIXEL**2')
source=source.replace('4.895','5.445').replace('<4.9','<5.45')
save('audit_centre_v32_first_roots.py',source)
save('render_centre_v32.py',(HERE/'render_centre_v31.py').read_text().replace('v31','v32'))
print('Prepared v32 independent numeric checks and unchanged timer-observed HIGH fixture; not run.')
