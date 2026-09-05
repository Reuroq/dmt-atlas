"""Independent float64 scalar evaluator for v29; no GLSL extraction."""
import numpy as np

PIXEL = 2*np.tan(np.radians(34))/800

def parts(p, t, camera, high):
    p = np.asarray(p, dtype=float)
    px, py, z = p[..., 0], p[..., 1]-1.7, p[..., 2]
    c, s = np.cos(t*.065), np.sin(t*.065)
    x, y = c*px-s*py, s*px+c*py
    def rose(k):
        return (np.cos(k*x)+np.cos(k*(x/2+np.sqrt(3)*y/2))+np.cos(k*(-x/2+np.sqrt(3)*y/2)))/3
    footprint2 = np.sum((p-camera)**2, axis=-1)*PIXEL**2
    def filtered(wave, frequency):
        return wave*np.exp(-.5*frequency**2*footprint2)
    r0 = rose(.62)*np.cos(.24*z-.30*t)
    r1 = rose(1.65)*np.cos(.58*z+1.2*r0-.36*t)
    r2 = rose(4.4)*np.cos(1.1*z+1.1*r1-.41*t)
    w1, w2 = filtered(r1, 4), filtered(r2, 11)
    rho = np.sqrt(px*px+py*py+.2025*np.minimum(z+27.5, 0)**2)
    f = rho-7-.86*np.cos(.68*z+1.1*r0-.48*t)-.55*r0-.32*w1-.14*w2
    if high:
        r3 = rose(11.7)*np.cos(2.3*z+.9*r2-.47*t)
        f -= .06*filtered(r3, 27)
    return f, w1-.05, w2+.35*r0-.14

def components(p, t, camera, high):
    f, a, b = parts(p, t, camera, high)
    return np.stack([np.maximum(np.abs(f)-.14, a),
                     np.maximum(np.abs(f-2.6)-.18, b), 6-f], axis=-1)

def field(p, t, camera, high):
    return np.min(components(p, t, camera, high), axis=-1)
