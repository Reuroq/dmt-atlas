"""Independent float64 scalar evaluator; not extracted from GLSL."""
import numpy as np

PIXEL=2*np.tan(np.radians(34))/800

def parts(p,t,camera,high,pixel=PIXEL):
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(.075*t),np.sin(.075*t)
    x,y=c*px-s*py,s*px+c*py
    denominator=x*x+y*y+2.25
    u=(x+1j*y)/np.sqrt(denominator)
    h6,h18,h54=u**6,u**18,u**54
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    petal=np.real(h6*np.exp(1j*(.24*rho+.10*z+.65*h6.real-.21*t)))
    branch=np.real(h18*np.exp(1j*(.38*rho+.19*z+1.1*petal-.33*t)))
    footprint2=np.sum((p-camera)**2,axis=-1)*pixel**2
    def filt(w,k):return w*np.exp(-.5*k*k*footprint2)
    w=filt(petal,3)
    f=5.95-rho+.9*h6.real+.15*w
    a=w+.675/denominator
    b=filt(branch,8)
    if high:
        fine=np.real(h54*np.exp(1j*(.7*rho+.32*z+.8*h18.real-.47*t)))
        b=b+.25*filt(fine,20)
    return f,a,b

def components(p,t,camera,high,pixel=PIXEL):
    f,a,b=parts(p,t,camera,high,pixel)
    petals=np.maximum(f,np.maximum(abs(a)-.065,.16-abs(b)))
    branches=np.maximum(f+.45,np.maximum(abs(a)-.18,abs(b)-.03))
    return np.stack([petals,branches,f+12],axis=-1)

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
    petals=maximum(f,maximum(offset(aa,-.065),offset(-bb,.16)))
    branches=maximum(offset(f,.45),maximum(offset(aa,-.18),offset(bb,-.03)))
    backing=offset(f,12)
    result=np.where((branches[...,3]<petals[...,3])[...,None],branches,petals)
    return np.where((backing[...,3]<result[...,3])[...,None],backing,result)

def analytic_bounds():
    """Complex derivative triangle bounds, radial H valid for rho >=4.415."""
    def sup(a,b):
        if a==0:return 1.
        q=a/(2*b-a)
        return q**(a/2)/(1+q)**b
    def harmonic(m):
        L=m/1.5*(sup(m-1,m/2)+sup(m+1,m/2+1))
        H=(m*(m-1)*sup(m-2,m/2)+(2*m*m+m)*sup(m,m/2+1)+m*(m+2)*sup(m+2,m/2+2))/2.25
        return L,H
    def turn(h,phase):
        L,H=h;P,Q=phase
        return L+P,H+2*L*P+P*P+Q
    h6,h18,h54=map(harmonic,[6,18,54])
    petal=turn(h6,(.34+.65*h6[0],.24/4.415+.65*h6[1]))
    branch=turn(h18,(.57+1.1*petal[0],.38/4.415+1.1*petal[1]))
    fine=turn(h54,(1.02+.8*h18[0],.7/4.415+.8*h18[1]))
    def filtered(h,k):return np.array([h[1],2*h[0]*k*np.exp(-.5),k*k])
    fp=filtered(petal,3)
    polys=np.stack([np.array([1/4.415+.9*h6[1],0,0])+.15*fp,
        fp+np.array([.8,0,0]),filtered(branch,8)+.25*filtered(fine,20)])
    return {'harmonics':[h6,h18,h54],'petal':petal,'branch':branch,'fine':fine,
        'leaf_H_polynomials':polys.tolist()}
