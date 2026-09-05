"""Independent float64 scalar field for centre candidate geometry validation."""
import numpy as np

PIXEL = 2*np.tan(np.radians(34))/800

def field(p, t, camera, high):
    p = np.asarray(p, dtype=float)
    footprint = np.linalg.norm(p-camera, axis=-1)*PIXEL
    x, y, z = p[..., 0], p[..., 1]-1.7, p[..., 2]
    r2 = x*x+y*y
    cap = np.minimum(z+27.5, 0)
    u = np.sqrt(r2+.2025*cap*cap)-7
    pole, cw = r2/(r2+4), cap*cap/(cap*cap+4)
    angle = np.arctan2(y, x)-t*.065
    warp = 2.6*np.cos(.85*x)*np.cos(.85*y)+.75*np.sin(1.7*x+t*.19)*np.cos(1.7*y-t*.17)
    v = z*.72+(1.8+.22*np.sin(t*.61))*u-t*.57+cw*warp
    petal = 8*angle+.32*np.sin(v*.5+t*.31)
    f = u-1.18*np.sin(v+.65*pole*np.cos(petal))-.4*pole*np.cos(petal+.6*np.sin(v))
    f -= .28*cw*np.cos(1.7*x+.4*np.sin(v))*np.cos(1.7*y-.4*np.cos(v))
    chart = pole*np.sin(petal)+cw*(np.sin(.8*x)+np.cos(.8*y))
    bands = [(.30, 2.7, 2, 6, 1.3), (.15, 5.7, -4, 13, 2.9)]
    if high:
        bands.append((.07, 12.1, 7, 28, 6.1))
    for amplitude, fv, fc, frequency, k in bands:
        side = np.sin(fv*v+fc*chart)
        crossed = np.cos(k*x+.3*np.sin(v)+t*.07)*np.cos(k*y+.3*np.cos(v)-t*.09)
        f -= amplitude*np.exp(-.5*(footprint*frequency)**2)*((1-cw)*side+cw*crossed)
    return f
