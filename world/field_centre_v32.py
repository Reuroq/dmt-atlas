"""Independent float64 local curled-petal volume; not GLSL extraction."""
import numpy as np

PIXEL=2*np.tan(np.radians(34))/800

def parts(p,t,camera,high,pixel=PIXEL):
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(.075*t),np.sin(.075*t)
    x,y=c*px-s*py,s*px+c*py
    denominator=x*x+y*y+2.25
    u=(x+1j*y)/np.sqrt(denominator)
    h6,h18=u**6,u**18
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    radial=1.05*rho+.22*z+.65*h6.real-.13*t
    local=.65*z-.4*rho+.6*h6.imag-.18*t
    curl=radial+1.1*np.cos(local)
    child=3*curl+.65*np.cos(3*local)+.4*h18.real-.17*t
    split=local+.5*np.cos(curl)
    twig=3*local+.6*curl+.4*h18.imag
    footprint2=np.sum((p-camera)**2,axis=-1)*pixel**2
    def filt(w,k):return w*np.exp(-.5*k*k*footprint2)
    f=6.2-rho+.65*h6.real+.1*np.cos(local)
    a=filt(np.cos(curl)-.85*np.cos(local)-.3*h6.real,4)
    a+=.18*filt(np.cos(child),12)+6.3/denominator
    b=filt(np.cos(split),4)+.26*filt(np.cos(twig),12)
    if high:
        fine=3*child+.35*(u**54).real
        a+=.035*filt(np.cos(fine),36)
    return f,a,b

def components(p,t,camera,high,pixel=PIXEL):
    f,a,b=parts(p,t,camera,high,pixel)
    petals=np.maximum(f,np.maximum(abs(a)-.10,.035-abs(b)))
    branches=np.maximum(f+.38,np.maximum(abs(a)-.25,abs(b)-.014))
    return np.stack([petals,branches,f+10],axis=-1)

def field(p,t,camera,high,pixel=PIXEL):
    return np.min(components(p,t,camera,high,pixel),axis=-1)

def compose_jets(jets):
    f,a,b=np.moveaxis(np.asarray(jets,dtype=np.float32),-2,0)
    def offset(v,c):
        v=v.copy();v[...,3]+=np.float32(c);return v
    def absolute(v):
        v=v.copy();v[...,:3]*=np.sign(v[...,3,None]);v[...,3]=abs(v[...,3]);return v
    def maximum(u,v):return np.where((u[...,3]>v[...,3])[...,None],u,v)
    aa,bb=absolute(a),absolute(b)
    petals=maximum(f,maximum(offset(aa,-.10),offset(-bb,.035)))
    branches=maximum(offset(f,.38),maximum(offset(aa,-.25),offset(bb,-.014)))
    backing=offset(f,10)
    result=np.where((branches[...,3]<petals[...,3])[...,None],branches,petals)
    return np.where((backing[...,3]<result[...,3])[...,None],backing,result)

def analytic_bounds():
    """(L,H) triangle calculus on rho>=4.965, global regularized harmonics."""
    def sup(a,b):
        if a==0:return 1.
        q=a/(2*b-a)
        return q**(a/2)/(1+q)**b
    def harmonic(m):
        L=m/1.5*(sup(m-1,m/2)+sup(m+1,m/2+1))
        H=(m*(m-1)*sup(m-2,m/2)+(2*m*m+m)*sup(m,m/2+1)+m*(m+2)*sup(m+2,m/2+2))/2.25
        return np.array([L,H])
    def cosine(v):return np.array([v[0],v[1]+v[0]**2])
    h6,h18,h54=map(harmonic,[6,18,54])
    radial=np.array([1.27,1.05/4.965])+.65*h6
    local=np.array([1.05,.4/4.965])+.6*h6
    curl=radial+1.1*cosine(local)
    child=3*curl+.65*cosine(3*local)+.4*h18
    fine=3*child+.35*h54
    primary=cosine(curl)+.85*cosine(local)+.3*h6
    split=cosine(local+.5*cosine(curl))
    twig=cosine(3*local+.6*curl+.4*h18)
    def filtered(v,k,amplitude=1):
        return np.array([v[1],2*v[0]*k*np.exp(-.5),amplitude*k*k])
    f=np.array([1/4.965+.65*h6[1]+.1*cosine(local)[1],0,0])
    a=filtered(primary,4,2.15)+.18*filtered(cosine(child),12)+.035*filtered(cosine(fine),36)+[8,0,0]
    b=filtered(split,4)+.26*filtered(twig,12)
    # Rational core 6.3/(r^2+2.25): L<2.5, H<8 globally.
    slopes=[1+.65*h6[0]+.1*local[0],primary[0]+.18*child[0]+.035*fine[0]+2.5,split[0]+.26*twig[0]]
    filter_slopes=np.exp(-.5)*np.array([0,2.15*4+.18*12+.035*36,4+.26*12])
    return {'harmonics':[v.tolist() for v in [h6,h18,h54]],
        'curl':curl.tolist(),'child':child.tolist(),'fine':fine.tolist(),
        'leaf_L_constants':slopes,'leaf_L_pixel':filter_slopes.tolist(),
        'leaf_H_polynomials':np.stack([f,a,b]).tolist()}
