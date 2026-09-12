"""Give every cited entity a ladder of its own actions, and a body of its own to climb it with.

The division of labour is the reason this is allowed to exist:

    the fly decides WHEN and HOW HARD          the atlas decides WHAT

Nothing here invents a behaviour. Every rung is a verbatim phrase lifted from that entity's own
`behavior` field in atlas.json and carries the entity key it came from, so the page can cite it
the same way it cites a wall. The simulation supplies one number - how hard the descending
population is driving - and that number selects which cited phrase is currently true.

ONE WIRING DIAGRAM, MANY INDIVIDUALS. All 40 entities share the same FlyWire slice, because
there is only one fly connectome and pretending otherwise would be a lie. What differs per
entity is physiology: excitability, leak, noise floor, and which part of the visual sheet its
sensory drive lands on. That is the honest analogue of individuals of one species differing
while sharing a species-typical brain, and it costs one topology in memory instead of forty.

Physiology is derived deterministically from the entity's name, so the same entity is always
the same individual, across reloads and across machines.

This is NOT a claim that DMT entities are insects, or that a fly brain explains anything about
them. It is a way of making a depicted being move from measured biology instead of a sine wave,
and the page must say so plainly wherever it is used.
"""
import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# The four the walkthrough currently builds bodies for. Every other entity still gets a full
# ladder and physiology so it is ready the moment something depicts it.
IN_WORLD = {
    'Self-transforming machine elves': 'elf',
    'The Jester / Trickster / Clown': 'jester',
    'The Divine Feminine': 'mother',
    'Mantis & insectoid beings': 'mantis',
}

# Calibration overwrites these with measured values; they are only a starting bracket.
DRIVE_RANGE = (0.004, 0.072)


def slug(name):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return re.sub(r'-+', '-', s)


def phrases(text):
    """Split a cited field into the clauses it already contains, without cutting quotations.

    Splitting on any comma shredded "it is sound, but you see it" into halves that say nothing,
    so commas inside quotes are protected. A bare verb is still an action - dropping everything
    under thirteen characters silently deleted "Enfolds", "reassures" and "heals".
    """
    if not text:
        return []
    text = re.sub(r'\s+', ' ', text).strip()
    protected, quotes = text, []
    for i, q in enumerate(re.findall(r"'[^']{4,}'|‘[^’]{4,}’", text)):
        token = '@@%d@@' % i
        protected = protected.replace(q, token, 1)
        quotes.append(q)
    parts = re.split(r'\s*[;—]\s*|\s*,\s+(?:and\s+)?|\.\s+', protected)
    # "and" joins two distinct actions as often as a comma does ("shows the visitor their
    # wounds AND holds them"), but splitting on every "and" cut "leap in and out of the chest"
    # into two halves that are not actions. So only split a long clause, and only when both
    # sides can stand on their own.
    split = []
    for p in parts:
        halves = re.split(r'\s+and\s+', p, maxsplit=1)
        if len(p) > 40 and len(halves) == 2 and all(len(h.strip()) >= 12 for h in halves):
            split.extend(halves)
        else:
            split.append(p)
    out = []
    for p in split:
        for i, q in enumerate(quotes):
            p = p.replace('@@%d@@' % i, q)
        p = p.strip().strip('.').strip()
        if len(p) >= 5:
            out.append(p)
    return out


# A cited action has to become a POSE or the being does not perform it, it merely gets
# captioned. These are the only channels a being actually has: where it stands, how high its
# body rides, how far it leans, how far its arms lift and spread, and how fast it moves.
#
# The mapping is keyword-driven from the cited phrase itself, and every rung records which
# keyword matched, so a reader can check that "crowd forward" became a step forward because of
# the word "forward" and not because someone felt like it. Anything unmatched gets the neutral
# escalation, which is honest: we do not know what that phrase looks like.
MOTIONS = {
    'approach': (['crowd', 'forward', 'toward', 'closer', 'gather', 'press', 'follow'],
                 {'step': 1.0, 'lift': 0.0, 'lean': 0.35, 'arms': 0.30, 'spread': 0.2, 'tempo': 1.1}),
    'leap':     (['leap', 'jump', 'spring', 'dart', 'bound', 'flit', 'in and out'],
                 {'step': 0.35, 'lift': 1.0, 'lean': 0.1, 'arms': 0.55, 'spread': 0.7, 'tempo': 2.2}),
    'enfold':   (['enfold', 'hold', 'caress', 'embrace', 'cradle', 'reassur', 'heal', 'soothe'],
                 {'step': 0.45, 'lift': 0.15, 'lean': 0.45, 'arms': 0.85, 'spread': -0.6, 'tempo': 0.7}),
    'present':  (['sing', 'flash', 'show', 'display', 'present', 'lift', 'conjur', 'offer',
                  'urging', 'direct'],
                 {'step': 0.1, 'lift': 0.35, 'lean': -0.15, 'arms': 1.0, 'spread': 0.9, 'tempo': 1.6}),
    'loom':     (['operat', 'examin', 'surg', 'over you', 'peer', 'inspect', 'scan', 'harvest',
                  'clinical', 'procedure'],
                 {'step': 0.7, 'lift': -0.2, 'lean': 1.0, 'arms': 0.6, 'spread': -0.3, 'tempo': 0.8}),
    'recede':   (['withdraw', 'recede', 'retreat', 'vanish', 'dissolve', 'release'],
                 {'step': -0.8, 'lift': 0.0, 'lean': -0.4, 'arms': -0.3, 'spread': 0.3, 'tempo': 0.6}),
    'play':     (['playful', 'mischie', 'perform', 'mock', 'tease', 'caper', 'trick', 'game'],
                 {'step': 0.3, 'lift': 0.6, 'lean': 0.2, 'arms': 0.7, 'spread': 1.0, 'tempo': 2.0}),
}


def motion_for(says, index, total):
    """Pick the pose a cited phrase implies, and say which word decided it."""
    low = says.lower()
    for name, (words, pose) in MOTIONS.items():
        for w in words:
            if w in low:
                out = dict(pose)
                out['name'] = name
                out['matched'] = w
                return out
    # Unmatched: escalate neutrally with position on the ladder rather than invent a gesture.
    f = (index + 1) / float(total)
    return {'name': 'escalate', 'matched': None, 'step': 0.25 * f, 'lift': 0.2 * f,
            'lean': 0.3 * f, 'arms': 0.8 * f, 'spread': 0.3 * f, 'tempo': 0.8 + 0.7 * f}


def physiology(name):
    """A deterministic individual: same entity, same body, every time.

    Ranges are deliberately narrow. These are individuals of one species, not different
    animals, and a wide spread would just be four knobs of noise dressed up as character.
    """
    h = hashlib.sha256(name.encode('utf-8')).digest()
    u = [b / 255.0 for b in h[:8]]
    return {
        'gain': round(0.46 + 0.18 * u[0], 4),          # synaptic scale
        'leak': round(0.855 + 0.05 * u[1], 4),         # membrane decay per step
        'threshold': round(0.92 + 0.16 * u[2], 4),     # spike threshold
        'noise': round(0.0025 + 0.003 * u[3], 5),      # keeps the slice from going silent
        'sensoryPhase': round(u[4], 4),                # where on the visual sheet drive lands
        'sensorySpread': round(0.55 + 0.4 * u[5], 4),  # how broadly it lands
        'seed': int.from_bytes(h[8:12], 'big'),
    }


def main():
    atlas = json.loads((ROOT / 'data' / 'atlas.json').read_text(encoding='utf-8'))
    built, skipped = {}, []
    for e in sorted(atlas['entities'], key=lambda x: x['name']):
        name = e['name']
        pool = phrases(e.get('behavior'))
        if len(pool) < 2:
            skipped.append((name, len(pool)))
            continue
        key = IN_WORLD.get(name) or slug(name)
        ladder = []
        span = DRIVE_RANGE[1] - DRIVE_RANGE[0]
        for i, says in enumerate(pool):
            lo = DRIVE_RANGE[0] + span * (i / float(len(pool)))
            hi = DRIVE_RANGE[0] + span * ((i + 1) / float(len(pool)))
            ladder.append({
                'rung': i,
                'descendingRate': [round(lo, 5), round(hi, 5) if i < len(pool) - 1 else 1.0],
                'says': says,
                'from_field': 'behavior',
                'cites': 'entity|' + name,
                'motion': motion_for(says, i, len(pool)),
            })
        built[key] = {
            'being': key,
            'entity': name,
            'cites': 'entity|' + name,
            'depicted': name in IN_WORLD,
            'physiology': physiology(name),
            'ladder': ladder,
            'ambient': {f: phrases(e.get(f)) for f in ('communication', 'emotional_tone')},
            'purpose': (e.get('message_or_purpose') or '').strip(),
        }

    depicted = sum(1 for v in built.values() if v['depicted'])
    rungs = sum(len(v['ladder']) for v in built.values())
    print('%d entities -> %d ladders, %d cited actions in total' % (len(atlas['entities']), len(built), rungs))
    print('  depicted in the walkthrough today: %d' % depicted)
    print('  ready but not yet depicted:        %d' % (len(built) - depicted))
    if skipped:
        print('  skipped for having under two cited actions:')
        for n, c in skipped:
            print('     %s (%d)' % (n, c))

    (HERE / 'behaviour.json').write_text(json.dumps(built, indent=2, ensure_ascii=False),
                                         encoding='utf-8')
    print('\nwrote behaviour.json (calibrate.js sets the thresholds from measurement)')


if __name__ == '__main__':
    main()
