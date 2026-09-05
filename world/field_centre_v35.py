"""Independent float64 v35 scalar oracle and prospective smooth-leaf bounds.

The composite a/b petals are nonsmooth. Numerical/interval fixtures MUST use
smooth_parts (f, axial, angular, parent shell, child shell), not a/b Hessians.
"""
import numpy as np

PIXEL = 2*np.tan(np.radians(34))/800
LEAF_NAMES = ['f', 'axial', 'angular', 'parent_shell', 'child_shell']


def smooth_parts(p, t, camera, high, pixel=PIXEL):
    p = np.asarray(p, dtype=float)
    px, py, z = p[..., 0], p[..., 1]-1.7, p[..., 2]
    c, s = np.cos(.075*t), np.sin(.075*t)
    x, y = c*px-s*py, s*px+c*py
    u = (x+1j*y)/np.sqrt(x*x+y*y+2.25)
    h6, h12 = u**6, u**12
    rho = np.sqrt(px*px+py*py+.7225*np.minimum(z+27.5, 0)**2)
    radial = 1.05*rho+.16*z+.10*h6.real-.12*t
    local = .62*z-.28*rho+.12*h6.imag-.19*t
    cl, sl = np.cos(local), np.sin(local)
    phase = .42*sl+.16*np.cos(radial)+.20*t
    footprint2 = np.sum((p-camera)**2, axis=-1)*pixel**2

    def filtered(v, k):
        return v*np.exp(-.5*k*k*footprint2)

    shell = np.cos(radial+.92*sl)-.72*cl
    scale = 1+.24*filtered(np.cos(2.3*radial+.25*h6.real), 4)
    if high:
        shell += .045*filtered(np.cos(4.3*radial+.35*h6.real), 6)
        scale += .07*filtered(np.cos(6.1*local+.20*h6.imag), 9)
    shift = .30*(1-cl)*scale
    return np.stack([6.2-rho+.4*h6.real, -cl-.62,
                     abs(h6)**2-(h12*np.exp(1j*phase)).real-.90,
                     shell, shell-shift], axis=-1)


def parts(p, t, camera, high, pixel=PIXEL):
    f, axial, angular, shell, child = np.moveaxis(
        smooth_parts(p, t, camera, high, pixel), -1, 0)
    a = np.maximum(np.abs(shell)-.095, np.maximum(axial, angular))
    b = np.maximum(np.abs(child)-.062, np.maximum(axial+.20, angular+.28))
    return f, a, b


def components(p, t, camera, high, pixel=PIXEL):
    f, a, b = parts(p, t, camera, high, pixel)
    return np.stack([np.maximum(f, a), np.maximum(f+.3, b), f+10], axis=-1)


def field(p, t, camera, high, pixel=PIXEL):
    return np.min(components(p, t, camera, high, pixel), axis=-1)


def expanded_leaves(values):
    """Eleven signed, offset smooth CSG leaves; groups 5/5/1."""
    f, axial, angular, shell, child = np.moveaxis(np.asarray(values), -1, 0)
    return np.stack([f, axial, angular, shell-.095, -shell-.095,
                     f+.3, axial+.20, angular+.28, child-.062, -child-.062,
                     f+10], axis=-1)


def compose_expanded(values):
    return np.minimum(np.minimum(np.max(values[..., :5], axis=-1),
                                 np.max(values[..., 5:10], axis=-1)), values[..., 10])


def analytic_bounds():
    """Real-arithmetic amplitude/gradient/Hessian norm bounds, rho>=4.965.

    Coefficients are polynomials in nonnegative pixelScale. Time and camera
    have no spatial derivatives. Complex norms bound real/imag projections.
    C1 cap join has an a.e. bounded Hessian, enough for Taylor remainder.
    These ordinary float64 calculations are not directed-rounding proof.
    """
    class Bound:
        def __init__(self, amplitude, gradient=0., hessian=0.):
            self.A = amplitude
            self.L = np.array([gradient, 0.]) if np.ndim(gradient) == 0 else np.array(gradient)
            self.H = np.array([hessian, 0., 0.]) if np.ndim(hessian) == 0 else np.array(hessian)

        def __add__(self, b):
            return Bound(self.A+b.A, self.L+b.L, self.H+b.H)

        def scale(self, k):
            return Bound(abs(k)*self.A, abs(k)*self.L, abs(k)*self.H)

        def product(self, b):
            return Bound(self.A*b.A, self.A*b.L+b.A*self.L,
                         self.A*b.H+b.A*self.H+2*np.convolve(self.L, b.L))

        def trig(self):
            return Bound(1, self.L, self.H+np.convolve(self.L, self.L))

        def filtered(self, k):
            return Bound(self.A, self.L+np.array([0, self.A*k*np.exp(-.5)]),
                         self.H+2*k*np.exp(-.5)*np.array([0, *self.L])
                         +np.array([0, 0, self.A*k*k]))

    def sup(a, b):
        if a == 0:
            return 1.
        q = a/(2*b-a)
        return q**(a/2)/(1+q)**b

    def harmonic(m):
        # Product differentiation of w^m*(|w|^2+1.5^2)^(-m/2).
        L = m/1.5*(sup(m-1, m/2)+sup(m+1, m/2+1))
        H = (m*(m-1)*sup(m-2, m/2)+(2*m*m+m)*sup(m, m/2+1)
             +m*(m+2)*sup(m+2, m/2+2))/2.25
        return Bound(1, L, H)

    h6, h12 = harmonic(6), harmonic(12)
    radial = Bound(0, 1.21, 1.05/4.965)+h6.scale(.10)
    local = Bound(0, .90, .28/4.965)+h6.scale(.12)
    lc = local.trig()
    curl = radial+lc.scale(.92)
    phase = lc.scale(.42)+radial.trig().scale(.16)
    shell = curl.trig()+lc.scale(.72)
    shell = shell+(radial.scale(4.3)+h6.scale(.35)).trig().filtered(6).scale(.045)
    scale = Bound(1)+(radial.scale(2.3)+h6.scale(.25)).trig().filtered(4).scale(.24)
    scale = scale+(local.scale(6.1)+h6.scale(.20)).trig().filtered(9).scale(.07)
    shift = (Bound(1)+lc).product(scale).scale(.30)
    child = shell+shift
    f = Bound(0, 1, 1/4.965)+h6.scale(.4)
    angular = h6.product(h6)+h12.product(phase.trig())
    leaves = [f, lc, angular, shell, child]
    return {'leaf_names': LEAF_NAMES,
            'L': [v.L.tolist() for v in leaves],
            'H': [v.H.tolist() for v in leaves],
            'harmonics': {str(m): {'L': v.L.tolist(), 'H': v.H.tolist()}
                          for m, v in [(6, h6), (12, h12)]},
            'rho_domain': 4.965, 'modes': 'HIGH bounds dominate LOW'}
