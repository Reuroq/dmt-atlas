"""Independent float64 tapered petal cells and prospective derivative calculus."""
import numpy as np

PIXEL=2*np.tan(np.radians(34))/800

def parts(p,t,camera,high,pixel=PIXEL):
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(.075*t),np.sin(.075*t)
    x,y=c*px-s*py,s*px+c*py
    denominator=x*x+y*y+2.25
    u=(x+1j*y)/np.sqrt(denominator)
    h6,h12,h18,h36=u**6,u**12,u**18,u**36
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    radial=1.35*rho+.12*z+.15*h6.real-.12*t
    local=.9*z-.25*rho+.2*h6.imag-.19*t
    curl=radial+.9*np.sin(local)
    phase=.7*np.sin(local)+.22*np.cos(radial)+.2*t
    child=3*curl+.35*np.cos(local)-.21*t
    child_local=3*local+.4*np.cos(radial)
    child_phase=3*phase+.3*np.sin(child_local)
    footprint2=np.sum((p-camera)**2,axis=-1)*pixel**2
    def filt(w,k):return w*np.exp(-.5*k*k*footprint2)
    parent_shell=filt(np.cos(curl)-.6*np.cos(local),4)
    child_shell=filt(np.cos(child)-.55*np.cos(child_local),12)
    if high:
        child_shell+=.11*filt(np.cos(3*child+.25*h36.real),36)
    angular12=abs(h6)**2-filt((h12*np.exp(1j*phase)).real,4)
    angular36=abs(h18)**2-filt((h36*np.exp(1j*child_phase)).real,12)
    f=6.2-rho+.4*h6.real
    a=4*parent_shell**2+.55*(1-filt(np.cos(local),4))+.65*angular12-.16+1.6/denominator
    b=3*child_shell**2+.45*(1-filt(np.cos(child_local),12))+1.1*angular36-.105+1.1/denominator
    return f,a,b

def components(p,t,camera,high,pixel=PIXEL):
    f,a,b=parts(p,t,camera,high,pixel)
    return np.stack([np.maximum(f,a),np.maximum(f+.3,b),f+10],axis=-1)

def field(p,t,camera,high,pixel=PIXEL):
    return np.min(components(p,t,camera,high,pixel),axis=-1)

def compose_jets(jets):
    f,a,b=np.moveaxis(np.asarray(jets,dtype=np.float32),-2,0)
    def offset(v,c):
        v=v.copy();v[...,3]+=np.float32(c);return v
    def maximum(u,v):return np.where((u[...,3]>v[...,3])[...,None],u,v)
    parent,child=maximum(f,a),maximum(offset(f,.3),b)
    backing=offset(f,10)
    result=np.where((child[...,3]<parent[...,3])[...,None],child,parent)
    return np.where((backing[...,3]<result[...,3])[...,None],backing,result)

def analytic_bounds():
    """Amplitude, gradient polynomial, Hessian polynomial; rho>=4.965.

    Harmonic bounds are global; constants in phases have zero derivatives.
    Complex norm bounds also bound each real or imaginary component.
    """
    class Bound:
        def __init__(self,A,L=0,H=0):
            self.A=A
            self.L=np.broadcast_to(L,(2,)).copy() if np.ndim(L) else np.array([L,0.])
            self.H=np.broadcast_to(H,(3,)).copy() if np.ndim(H) else np.array([H,0.,0.])
        def __add__(self,b):return Bound(self.A+b.A,self.L+b.L,self.H+b.H)
        def scale(self,k):return Bound(abs(k)*self.A,abs(k)*self.L,abs(k)*self.H)
        def product(self,b):
            return Bound(self.A*b.A,self.A*b.L+b.A*self.L,
                self.A*b.H+b.A*self.H+2*np.convolve(self.L,b.L))
        def trig(self):return Bound(1,self.L,self.H+np.convolve(self.L,self.L))
        def filtered(self,k):
            return Bound(self.A,self.L+np.array([0,self.A*k*np.exp(-.5)]),
                self.H+2*k*np.exp(-.5)*np.array([0,*self.L])+np.array([0,0,self.A*k*k]))
    def sup(a,b):
        if a==0:return 1.
        q=a/(2*b-a)
        return q**(a/2)/(1+q)**b
    def harmonic(m):
        L=m/1.5*(sup(m-1,m/2)+sup(m+1,m/2+1))
        H=(m*(m-1)*sup(m-2,m/2)+(2*m*m+m)*sup(m,m/2+1)+m*(m+2)*sup(m+2,m/2+2))/2.25
        return Bound(1,L,H)
    h6,h12,h18,h36=map(harmonic,[6,12,18,36])
    radial=Bound(0,1.47,1.35/4.965)+h6.scale(.15)
    local=Bound(0,1.15,.25/4.965)+h6.scale(.2)
    curl=radial+local.trig().scale(.9)
    phase=local.trig().scale(.7)+radial.trig().scale(.22)
    child=curl.scale(3)+local.trig().scale(.35)
    child_local=local.scale(3)+radial.trig().scale(.4)
    child_phase=phase.scale(3)+child_local.trig().scale(.3)
    parent_shell=(curl.trig()+local.trig().scale(.6)).filtered(4)
    child_shell=(child.trig()+child_local.trig().scale(.55)).filtered(12)
    child_shell=child_shell+(child.scale(3)+h36.scale(.25)).trig().filtered(36).scale(.11)
    # |h_m|^2: complex inner product, NOT separate real/imag sums of bounds.
    # Rotated h has L<=L_h+L_phase,H<=H_h+2L_h L_phase+H_phase+L_phase².
    angular12=h6.product(h6)+h12.product(phase.trig()).filtered(4)
    angular36=h18.product(h18)+h36.product(child_phase.trig()).filtered(12)
    # 6.3/(r²+2.25) has global L<2.5,H<8; scale for these cores.
    core=Bound(6.3/2.25,2.5,8)
    f=Bound(0,1,1/4.965)+h6.scale(.4)
    a=parent_shell.product(parent_shell).scale(4)+local.trig().filtered(4).scale(.55)+angular12.scale(.65)+core.scale(1.6/6.3)
    b=child_shell.product(child_shell).scale(3)+child_local.trig().filtered(12).scale(.45)+angular36.scale(1.1)+core.scale(1.1/6.3)
    lower=[local.trig().filtered(4).scale(.55)+core.scale(1.6/6.3),
        child_local.trig().filtered(12).scale(.45)+core.scale(1.1/6.3),
        angular12.scale(.65)+core.scale(1.6/6.3),
        angular36.scale(1.1)+core.scale(1.1/6.3),
        parent_shell.scale(1.6),parent_shell.scale(1.6),
        child_shell.scale(1.128),child_shell.scale(1.128)]
    return {'lower_L_polynomials':[v.L.tolist() for v in lower],
        'lower_H_polynomials':[v.H.tolist() for v in lower],
        'leaf_L_constants' :[v.L[0] for v in [f,a,b]],
        'leaf_L_pixel':[v.L[1] for v in [f,a,b]],
        'leaf_H_polynomials':[v.H.tolist() for v in [f,a,b]],
        'harmonics':{str(m):[v.L[0],v.H[0]] for m,v in zip([6,12,18,36],[h6,h12,h18,h36])}}


def lower_parts(p,t,camera,high,pixel=PIXEL):
    """Independent scalar lower leaves, each <= its original parent/child leaf."""
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(.075*t),np.sin(.075*t)
    x,y=c*px-s*py,s*px+c*py
    den=x*x+y*y+2.25
    h=(x+1j*y)/np.sqrt(den)
    h6,h12,h18,h36=h**6,h**12,h**18,h**36
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    R=1.35*rho+.12*z+.15*h6.real-.12*t
    T=.9*z-.25*rho+.2*h6.imag-.19*t
    C=R+.9*np.sin(T);P=.7*np.sin(T)+.22*np.cos(R)+.2*t
    D=3*C+.35*np.cos(T)-.21*t;U=3*T+.4*np.cos(R)
    V=3*P+.3*np.sin(U)
    footprint2=pixel**2*np.sum((p-camera)**2,axis=-1)
    def G(v,k):return v*np.exp(-.5*k*k*footprint2)
    s=G(np.cos(C)-.6*np.cos(T),4)
    q=G(np.cos(D)-.55*np.cos(U),12)
    if high:q+=.11*G(np.cos(3*D+.25*h36.real),36)
    A=abs(h6)**2-G((h12*np.exp(1j*P)).real,4)
    B=abs(h18)**2-G((h36*np.exp(1j*V)).real,12)
    return np.stack([.39-.55*G(np.cos(T),4)+1.6/den,
        .345-.45*G(np.cos(U),12)+1.1/den,
        -.16+.65*A+1.6/den,-.105+1.1*B+1.1/den,
        1.6*s-.32,-1.6*s-.32,1.128*q-.211032,-1.128*q-.211032],axis=-1)-.00001


def cheap_parts(p,t,camera,pixel=PIXEL):
    """Independent scalar f/axial certificates; no full-field construction."""
    p=np.asarray(p,dtype=float)
    x,y,z=p[...,0],p[...,1]-1.7,p[...,2]
    den=x*x+y*y+2.25
    h6=((x+1j*y)*np.exp(.075j*t)/np.sqrt(den))**6
    rho=np.sqrt(x*x+y*y+.7225*np.minimum(z+27.5,0)**2)
    R=1.35*rho+.12*z+.15*h6.real-.12*t
    T=.9*z-.25*rho+.2*h6.imag-.19*t
    U=3*T+.4*np.cos(R)
    footprint2=pixel**2*np.sum((p-camera)**2,axis=-1)
    return np.stack([6.2-rho+.4*h6.real,
        .38999-.55*np.cos(T)*np.exp(-8*footprint2)+1.6/den,
        .34499-.45*np.cos(U)*np.exp(-72*footprint2)+1.1/den],axis=-1)
