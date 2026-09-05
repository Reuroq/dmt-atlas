"""Prepare independent checks for changed v33 smooth cells and union CSG."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def save(name,source):
    path=HERE/name
    assert not path.exists(),name
    path.write_text(source)

source=(HERE/'check_centre_v32_bounds.py').read_text().replace('v32','v33').replace('32001','33001')
source=source.replace('16+8*pixel','185+148*pixel')
source=source.replace('[7,305,87]','[4,388,4321]').replace('[1,190,65]','[1,522,6236]').replace('[1,110,54]','[1,468,4990]')
start=source.index('            petals=np.maximum(')
end=source.index('            free=',start)
source=source[:start]+'''            petals=np.maximum(reach(f,df,mf),reach(a,da,ma))
            children=np.maximum(reach(f+.3,df,mf),reach(b,db,mb))
            step=np.minimum(np.minimum(petals,children),reach(f+10,df,mf))
'''+source[end:]
source=source.replace('[[7,1,1],[305,190,110],[87,65,54]]','[[4,1,1],[388,522,468],[4321,6236,4990]]')
source=source.replace("max(analytic['leaf_L_constants'])<16","max(analytic['leaf_L_constants'])<185")
source=source.replace("max(analytic['leaf_L_pixel'])<8","max(analytic['leaf_L_pixel'])<148")
save('check_centre_v33_bounds.py',source)
save('probe_numeric_candidate_v33.py',(HERE/'probe_numeric_candidate_v32.py').read_text().replace('v32','v33'))
source=(HERE/'audit_centre_v32_first_roots.py').read_text().replace('v32','v33')
source=source.replace('305+190*PIXEL+110*PIXEL**2','4321+6236*PIXEL+4990*PIXEL**2')
start=source.index('def composed(v):')
end=source.index('\nresults=[]',start)
source=source[:start]+'''def composed(v):
    f,a,b=np.moveaxis(v,-1,0)
    return np.minimum(np.minimum(np.maximum(f,a),np.maximum(f+.3,b)),f+10)

def lower_bound(left,right,width):
    # Each smooth leaf >= endpoint minimum minus M*h²/8 and roundoff pad.
    # The v33 union/intersection is monotone in all three smooth leaves.
    pad=M*np.asarray(width)**2/8+1e-12
    return composed(np.minimum(left,right)-np.asarray(pad)[...,None])
'''+source[end:]
save('audit_centre_v33_first_roots.py',source)
save('render_centre_v33.py',(HERE/'render_centre_v32.py').read_text().replace('v32','v33'))
print('Prepared v33 numerical checks and unchanged real-control HIGH fixture; not run.')
