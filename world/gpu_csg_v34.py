"""Float32 replay of the exact nested GLSL selections; no smooth-max claim."""
import numpy as np

BASE_KEYS = ['f', 'axial', 'angular', 'parent_shell', 'child_shell']
EXPANDED_KEYS = ['parentF', 'parentAxial', 'parentAngular', 'parentPositive',
                 'parentNegative', 'childF', 'childAxial', 'childAngular',
                 'childPositive', 'childNegative', 'backingF']


def offset(jet, value):
    result = jet.copy()
    result[..., 3] += np.float32(value)
    return result


def expand_jets(base):
    f, ax, ang, shell, child = np.moveaxis(np.asarray(base, dtype=np.float32), -2, 0)
    return np.stack([f, ax, ang, offset(shell, -.095), offset(-shell, -.095),
                     offset(f, .3), offset(ax, .20), offset(ang, .28),
                     offset(child, -.062), offset(-child, -.062), offset(f, 10.)], axis=-2)


def replay(jets):
    """Tie policy: jmax chooses right; union keeps earlier on equality."""
    jets = np.asarray(jets, dtype=np.float32)
    def maximum(left, right):
        return np.where(jets[..., left, 3] > jets[..., right, 3], left, right)
    def choose(left, right, is_max):
        lv = np.take_along_axis(jets[..., 3], np.asarray(left)[..., None], -1)[..., 0]
        rv = np.take_along_axis(jets[..., 3], np.asarray(right)[..., None], -1)[..., 0]
        return np.where(lv > rv if is_max else rv < lv,
                        left if is_max else right, right if is_max else left)
    shape = jets.shape[:-2]
    ids = [np.full(shape, i, dtype=int) for i in range(11)]
    a = choose(maximum(3, 4), maximum(1, 2), True)
    b = choose(maximum(8, 9), maximum(6, 7), True)
    parent = choose(ids[0], a, True)
    child = choose(ids[5], b, True)
    selected = choose(choose(parent, child, False), ids[10], False)
    def get(indices):
        return np.take_along_axis(jets, indices[..., None, None], -2)[..., 0, :]
    return get(a), get(b), get(selected), selected


def contract_checks():
    # Synthetic inputs only: exercise every leaf, negative signs and all ties.
    rng = np.random.default_rng(34002)
    base = rng.normal(size=(1000, 5, 4)).astype(np.float32)
    expanded = expand_jets(base)
    a, b, composed, selected = replay(expanded)
    def jmax(x, y):
        return x if x[3] > y[3] else y
    expected = []
    for row in expanded:
        aa = jmax(jmax(row[3], row[4]), jmax(row[1], row[2]))
        bb = jmax(jmax(row[8], row[9]), jmax(row[6], row[7]))
        parent, child = jmax(row[0], aa), jmax(row[5], bb)
        chosen = child if child[3] < parent[3] else parent
        chosen = row[10] if row[10, 3] < chosen[3] else chosen
        expected.append(chosen)
    assert np.array_equal(composed, expected)
    tie = np.zeros((1, 11, 4), dtype=np.float32)
    tie[0, :, 0] = np.arange(11)
    aa, bb, cc, chosen = replay(tie)
    assert aa[0, 0] == 2 and bb[0, 0] == 7 and chosen[0] == 2 and cc[0, 0] == 2
    # Every expanded leaf can independently control an artificial CSG tree.
    for leaf in range(11):
        row = np.zeros((1, 11, 4), dtype=np.float32)
        row[..., 3] = -2
        if leaf < 5:
            row[0, 5:11, 3] = 2
        elif leaf < 10:
            row[0, :5, 3] = 2; row[0, 10, 3] = 2
        else:
            row[..., 3] = 2
        row[0, leaf, 3] = -1
        assert replay(row)[3][0] == leaf
    return {'passed': True, 'synthetic_replays': 1012, 'v34_field_samples': 0}
