"""Independent float64 scalar field, not extracted from the GLSL implementation."""
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
    warp = 2.6*np.cos(.65*x+t*.11)*np.cos(.65*y-t*.09)
    v = .72*z+(1.8+.22*np.sin(t*.61))*u-.57*t+cw*warp
    petal = 8*angle+.32*np.sin(.5*v+.31*t)
    f = u-1.18*np.sin(v+.65*pole*np.cos(petal))-.4*pole*np.cos(petal+.6*np.sin(v))
    f -= .28*cw*np.cos(1.7*x+.07*t)*np.cos(1.7*y-.09*t)
    bands = [(.30, 1.3, 6), (.15, 2.9, 13)]
    if high:
        bands.append((.07, 6.1, 28))
    for amplitude, k, frequency in bands:
        wave = np.cos(k*x+.07*t)*np.cos(k*y-.09*t)*np.cos(.7*k*z-.13*t)
        f -= amplitude*np.exp(-.5*(footprint*frequency)**2)*wave
    return f
