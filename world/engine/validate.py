"""Static validation of a room spec. No browser, no GPU, fails in milliseconds.

Three things are checked, in increasing order of what they protect:

1. GRAMMAR - the primitive exists and its options are real. The signatures are parsed out of
   fractal.js at run time rather than copied into a table here, so the grammar cannot drift
   away from the engine it claims to describe.

2. RANGES - numeric options are inside bounds that produce a scene a camera can stand in.
   Catches the class where a model writes a plausible number with the wrong magnitude.

3. CITATION - every element resolves to a real atlas node, and says why that source implies
   that shape. This is the one that matters. The site's charter forbids inventing content, and
   inventing a convincing room is precisely what a language model does well and cannot notice
   itself doing. A spec with an uncited element does not render.

Usage:  python validate.py rooms/library.json [...]        (exit 0 = valid)
        python validate.py --selftest                       (prove the checks can fail)
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
WORLD = HERE.parent
ROOT = WORLD.parent

# Options every primitive accepts through the shared (root, materials, motions, opts) shape.
RANGES = {
    'x': (-60, 60), 'y': (-30, 30), 'z': (-80, 40),
    'radius': (1, 40), 'length': (2, 120), 'height': (0.5, 40), 'width': (0.5, 60),
    'spread': (0.1, 30), 'w': (0.1, 60), 'h': (0.1, 40), 'd': (0.1, 60),
    'depth': (0, 5), 'rx': (-3.2, 3.2), 'ry': (-3.2, 3.2), 'seed': (0, 9999),
    'palette': (0, 4),
}


def primitives():
    """The grammar, read from the shipped engine rather than from a copy of it."""
    src = (WORLD / 'fractal.py').read_text(encoding='utf-8') if False else \
        (WORLD / 'fractal.js').read_text(encoding='utf-8')
    exported = set()
    m = re.search(r'window\.FractalWorld\s*=\s*\{(.*?)\}\s*;', src, re.S)
    if m:
        for piece in m.group(1).split(','):
            name = piece.split(':')[0].strip()
            if re.fullmatch(r'[A-Za-z_]\w*', name):
                exported.add(name)
    grammar = {}
    for name, args in re.findall(r'function\s+([A-Za-z_]\w*)\s*\(([^)]*)\)', src):
        if name not in exported:
            continue
        opts = re.findall(r'([a-zA-Z_]\w*)\s*=', args[args.find('{'):]) if '{' in args else []
        grammar[name] = {'options': sorted(set(opts)), 'takes_motions': 'motions' in args}
    return grammar


def atlas_keys():
    data = json.loads((ROOT / 'data' / 'atlas.json').read_text(encoding='utf-8'))
    keys = set()
    for kind, section in (('entity', 'entities'), ('realm', 'realms'), ('geometry', 'geometries'),
                          ('phase', 'phases'), ('theme', 'themes'), ('motif', 'motifs')):
        for node in data.get(section, []):
            keys.add(kind + '|' + node['name'])
    return keys


def check(spec_path, grammar, keys):
    problems = []
    try:
        spec = json.loads(pathlib.Path(spec_path).read_text(encoding='utf-8'))
    except Exception as exc:
        return ['unreadable spec: %s' % exc]

    for field in ('id', 'name', 'atlas_node', 'palette', 'hint', 'duration', 'elements', 'expect'):
        if field not in spec:
            problems.append('missing required field: %s' % field)
    if problems:
        return problems

    if not re.fullmatch(r'[a-z][a-z0-9]*', spec['id']):
        problems.append('id %r must be lowercase alphanumeric (it becomes a stage id)' % spec['id'])
    if spec['atlas_node'] not in keys:
        problems.append('atlas_node %r resolves to no node in atlas.json' % spec['atlas_node'])
    if not isinstance(spec['elements'], list) or not spec['elements']:
        problems.append('elements must be a non-empty list')

    for i, el in enumerate(spec.get('elements', [])):
        where = 'element %d' % i
        prim = el.get('primitive')
        if prim not in grammar:
            problems.append('%s: unknown primitive %r (grammar: %s)'
                            % (where, prim, ', '.join(sorted(grammar))))
            continue
        where = '%s (%s)' % (where, prim)
        allowed = set(grammar[prim]['options'])
        for k, v in (el.get('options') or {}).items():
            if k not in allowed:
                problems.append('%s: option %r is not accepted; %s takes %s'
                                % (where, k, prim, ', '.join(sorted(allowed)) or '(none)'))
                continue
            if k in RANGES and isinstance(v, (int, float)):
                lo, hi = RANGES[k]
                if not lo <= v <= hi:
                    problems.append('%s: %s=%s is outside %s..%s' % (where, k, v, lo, hi))
        cites = el.get('cites')
        if not cites:
            problems.append('%s: no `cites`. Every element must name the atlas node it comes '
                            'from - an uncited room is an invented one.' % where)
        elif cites not in keys:
            problems.append('%s: cites %r which resolves to no node in atlas.json' % (where, cites))
        because = (el.get('because') or '').strip()
        if len(because) < 12:
            problems.append('%s: `because` must say why that source implies this shape' % where)

    expect = spec.get('expect') or {}
    if not expect:
        problems.append('expect: a room must declare the measured ranges it intends to land in, '
                        'or the loop has nothing to close against')
    for axis, bounds in expect.items():
        if axis not in ('VARIETY', 'DETAIL', 'DEPTH', 'MATERIAL'):
            problems.append('expect: unknown axis %r' % axis)
        elif not (isinstance(bounds, list) and len(bounds) == 2 and bounds[0] < bounds[1]):
            problems.append('expect.%s must be [low, high] with low < high' % axis)
    return problems


def selftest(grammar, keys):
    """A validator that cannot fail is not a validator. Plant one defect per check."""
    base = {'id': 'probe', 'name': 'Probe', 'atlas_node': sorted(keys)[0], 'palette': 0,
            'hint': 'x', 'duration': 10, 'expect': {'VARIETY': [0.1, 1.0]},
            'elements': [{'primitive': 'vault', 'options': {'radius': 7},
                          'cites': sorted(keys)[0], 'because': 'a hall that recedes'}]}
    import copy
    import tempfile
    cases = [
        ('unknown primitive', lambda s: s['elements'][0].__setitem__('primitive', 'nope')),
        ('bogus option', lambda s: s['elements'][0]['options'].__setitem__('nope', 1)),
        ('out-of-range option', lambda s: s['elements'][0]['options'].__setitem__('radius', 900)),
        ('missing citation', lambda s: s['elements'][0].pop('cites')),
        ('dangling citation', lambda s: s['elements'][0].__setitem__('cites', 'realm|Nowhere')),
        ('empty because', lambda s: s['elements'][0].__setitem__('because', '')),
        ('no expectations', lambda s: s.__setitem__('expect', {})),
    ]
    ok = True
    clean = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
    json.dump(base, clean); clean.close()
    baseline = check(clean.name, grammar, keys)
    print('%-24s %s' % ('clean spec', 'no problems' if not baseline else 'UNEXPECTED: %s' % baseline))
    ok &= not baseline
    for label, mutate in cases:
        spec = copy.deepcopy(base)
        mutate(spec)
        tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(spec, tmp); tmp.close()
        found = check(tmp.name, grammar, keys)
        print('%-24s %s' % (label, 'caught' if found else 'NOT CAUGHT <-- validator is blind here'))
        ok &= bool(found)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('specs', nargs='*')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--emit', action='store_true',
                    help='write primitives.json so compile.js reads the same grammar')
    a = ap.parse_args()
    grammar, keys = primitives(), atlas_keys()
    if a.emit:
        # One source of truth: fractal.js -> primitives.json -> validator AND compiler.
        (HERE / 'primitives.json').write_text(json.dumps(grammar, indent=2), encoding='utf-8')
        print('wrote primitives.json: %d primitives' % len(grammar))
        if not a.specs:
            raise SystemExit(0)
    if a.selftest:
        print('grammar read from fractal.js: %s\n' % ', '.join(sorted(grammar)))
        raise SystemExit(0 if selftest(grammar, keys) else 1)
    if not a.specs:
        ap.error('give at least one spec, or --selftest')
    bad = 0
    for path in a.specs:
        problems = check(path, grammar, keys)
        name = pathlib.Path(path).name
        if problems:
            bad += 1
            print('%s: %d problem(s)' % (name, len(problems)))
            for p in problems:
                print('   -', p)
        else:
            print('%s: valid' % name)
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
