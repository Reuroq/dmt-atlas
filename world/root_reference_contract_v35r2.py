"""Oracle-free evidence-shape contract; not a root solver or source verifier."""
import math


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def strict(a, b):
    return finite(a) and finite(b) and ((a > 0 and b < 0) or (a < 0 and b > 0))


def bracket_valid(record, samples):
    index = record['index']
    if type(index) is not int or not 0 <= index < len(samples)-1:
        return False
    lo, lv = samples[index]; hi, hv = samples[index+1]
    entering = lv > 0 and hv < 0
    if not strict(lv, hv) or record['entering'] is not entering:
        return False
    steps = record['steps']
    if len(steps) != 24:
        return False
    for step in steps:
        if not all(finite(v) for v in step['before'] + step['after']) or not finite(step['mid']):
            return False
        if step['before'] != [lo, hi, lv, hv]:
            return False
        mid = (lo + hi)/2
        if step['mid'] != mid or not lo < mid < hi:
            return False
        mv = step['value']
        if not finite(mv) or mv == 0:
            return False
        if (mv > 0) == (lv > 0):
            lo, lv = mid, mv
        else:
            hi, hv = mid, mv
        if step['after'] != [lo, hi, lv, hv] or not strict(lv, hv):
            return False
    return all(finite(v) for v in record['final']) and record['final'] == [lo, hi, lv, hv]


def validate_ray(record):
    """False on malformed/unresolved data. Does not authenticate oracle values."""
    try:
        gpu = record['gpu_depth']
        if not finite(gpu) or gpu < .004:
            return False
        samples = record['local']['samples']
        # Match the frozen CPU-local grid construction, not a tolerance band.
        expected = [gpu + (i-80)*.00005 for i in range(161)]
        if len(samples) != 161:
            return False
        for i, (depth, value) in enumerate(samples):
            if not finite(depth) or depth != expected[i] or not finite(value) or value == 0:
                return False
        observed = [i for i in range(160) if strict(samples[i][1], samples[i+1][1])]
        brackets = record['local']['brackets']
        if [b['index'] for b in brackets] != observed or not observed:
            return False
        if not all(bracket_valid(b, samples) for b in brackets):
            return False
        independent = record['independent']
        if independent['passed'] is not True or independent['unresolved'] != []:
            return False
        lo, hi, lv, hv = independent['first_bracket']
        if not all(finite(v) for v in (lo, hi, lv, hv)):
            return False
        if not (0 <= lo < hi and hi-lo <= 1e-7 and lv > 0 and hv < 0):
            return False
        difference = abs((lo+hi)/2-gpu)
        if not difference < .03 or not finite(independent['difference']) or independent['difference'] != difference:
            return False
        cells = [b['index'] for b in brackets if b['entering']
                 and samples[b['index']][0] <= lo and hi <= samples[b['index']+1][0]]
        if len(cells) != 1:
            return False
        legacy = record['legacy']
        if type(legacy['ray']) is not int:
            return False
        if legacy.get('missing_reference') is True:
            return set(legacy) == {'ray', 'missing_reference'}
        depth = legacy['reference_depth']
        old_difference = legacy['difference']
        return (finite(depth) and depth >= 0 and finite(old_difference) and finite(legacy['gpu_depth'])
                and legacy['gpu_depth'] == gpu and old_difference == abs(depth-gpu)
                and old_difference < .03 and 'missing_reference' not in legacy)
    except (KeyError, TypeError, ValueError, IndexError, OverflowError):
        return False


def combine(expected, records):
    """Record coverage/shape only; NEVER numerical acceptance or root proof."""
    failed = {'additive_reference_contract_passed': False, 'numeric_passed': False}
    try:
        expected = [tuple(key) for key in expected]
        keys = [tuple(r['key']) for r in records]
        if len(expected) != 720 or len(set(expected)) != 720 or len(keys) != 720:
            return failed
        if len(set(keys)) != 720 or set(keys) != set(expected):
            return failed
        if not all(len(key) == 6 and all(finite(v) for v in key) for key in keys):
            return failed
        if not all(r['legacy']['ray'] == r['key'][-1] and validate_ray(r) for r in records):
            return failed
        missing = [r['key'] for r in records if r['legacy'].get('missing_reference') is True]
        return {'additive_reference_contract_passed': True, 'numeric_passed': False,
                'original_fixed_grid_passed': not missing, 'legacy_missing_keys': missing,
                'reference_rays': 720,
                'requires_external_nonroot_exactjet_and_global_provenance_gates': True}
    except (KeyError, TypeError, ValueError, IndexError, OverflowError):
        return failed
