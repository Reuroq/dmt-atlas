"""Independent float64 scalar evaluator for v30; no GLSL extraction."""
import numpy as np

PIXEL = 2*np.tan(np.radians(34))/800

def parts(p,t,camera,high,pixel=PIXEL):
    p=np.asarray(p,dtype=float)
    px,py,z=p[...,0],p[...,1]-1.7,p[...,2]
    c,s=np.cos(t*.075),np.sin(t*.075)
    x,y=c*px-s*py,s*px+c*py
    def rose(k):
        return (np.cos(k*x)+np.cos(k*(x/2+np.sqrt(3)*y/2))+np.cos(k*(-x/2+np.sqrt(3)*y/2)))/3
    footprint2=np.sum((p-camera)**2,axis=-1)*pixel**2
    def filt(wave,k):
        return wave*np.exp(-.5*k*k*footprint2)
    r0=rose(.46)*np.cos(.28*z-.31*t)
    r1=rose(1.25)*np.cos(.72*z+r0-.43*t)
    r2=rose(3.4)*np.cos(1.45*z+.9*r1-.57*t)
    w1,w2=filt(r1,4),filt(r2,10)
    rho=np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5,0)**2)
    f=5.95-rho+.35*r0+.12*w1
    a,b=w1+.24*w2,w2
    if high:
        r3=rose(9.1)*np.cos(2.8*z+.8*r2-.71*t)
        b=b+.24*filt(r3,26)
    return f,a,b

def components(p,t,camera,high,pixel=PIXEL):
    f,a,b=parts(p,t,camera,high,pixel)
    petals=np.maximum(f,np.maximum(np.abs(a)-.19,.10-np.abs(b)))
    branches=np.maximum(f+.32,np.maximum(np.abs(a)-.40,np.abs(b)-.055))
    return np.stack([petals,branches,f+9],axis=-1)

def field(p,t,camera,high,pixel=PIXEL):
    return np.min(components(p,t,camera,high,pixel),axis=-1)

def compose_jets(jets):
    """Replay GLSL CSG tie-breaking from actual float32 leaf values."""
    f,a,b=np.moveaxis(np.asarray(jets,dtype=np.float32),-2,0)
    def offset(v,c):
        v=v.copy();v[...,3]+=np.float32(c);return v
    def absolute(v):
        v=v.copy();v[...,:3]*=np.sign(v[...,3,None]);v[...,3]=abs(v[...,3]);return v
    def maximum(u,v):
        return np.where((u[...,3]>v[...,3])[...,None],u,v)
    aa,bb=absolute(a),absolute(b)
    petals=maximum(f,maximum(offset(aa,-.19),offset(-bb,.10)))
    branches=maximum(offset(f,.32),maximum(offset(aa,-.40),offset(bb,-.055)))
    backing=offset(f,9)
    result=np.where((branches[...,3]<petals[...,3])[...,None],branches,petals)
    return np.where((backing[...,3]<result[...,3])[...,None],backing,result)
