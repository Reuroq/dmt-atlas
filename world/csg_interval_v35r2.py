"""Endpoint Taylor enclosures of v35r2's eleven SMOOTH signed CSG leaves.

Ordinary float64 with outward pad, not directed-rounding interval arithmetic.
Callers must exclude the singular envelope and supply the bound pixelScale.
"""
import numpy as np
from field_centre_v35r2 import expanded_leaves, compose_expanded


def enclosure(left, right, width, expanded_hessian, pad=1e-12):
    # Expand before taking endpoint extrema: negative shells reverse order.
    a, b = expanded_leaves(left), expanded_leaves(right)
    error = np.asarray(expanded_hessian)*np.asarray(width)[..., None]**2/8+pad
    lower = np.minimum(a, b)-error
    upper = np.maximum(a, b)+error
    return compose_expanded(lower), compose_expanded(upper)


def contract_checks():
    """Synthetic crease/negative-sign/union regressions; no v35r2 field samples."""
    hessian = np.zeros(11)
    left = np.array([-2., -2., -2., -1., 4.])
    right = np.array([-2., -2., -2., 1., 4.])
    lower, upper = enclosure(left, right, 1., hessian)
    # abs(S)-.095 has positive endpoints but a negative interior. Treating
    # the selected max leaf as a single smooth scalar would miss this root.
    assert min(compose_expanded(expanded_leaves(left)),
               compose_expanded(expanded_leaves(right))) > 0
    middle = compose_expanded(expanded_leaves((left+right)/2))
    assert middle < 0 and lower <= middle <= upper
    # Negative shell branch controls the endpoint. Both signed branches must
    # be present even when the positive shell branch is never selected there.
    a = np.array([-2., -2., -2., -.5, 4.])
    b = np.array([-2., -2., -2., -.2, 4.])
    lo, hi = enclosure(a, b, .3, hessian)
    assert lo > 0 and lo <= .105 and hi >= .405
    # A negative child cannot be excluded by a positive parent/backing.
    a = np.array([-2., -2., -2., 2., 0.])
    lo, hi = enclosure(a, a, .1, hessian)
    assert lo < 0 and hi < 0
    # Quadratic smooth-shell excursion: endpoints alone miss the crossing.
    a = np.array([-2., -2., -2., .2, 4.])
    hessian[[3, 4]] = 4.
    lo, hi = enclosure(a, a, 1., hessian)
    assert lo < 0 < hi
    return {'passed': True, 'synthetic_contracts': 4, 'v35r2_field_samples': 0}
