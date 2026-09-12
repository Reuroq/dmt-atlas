"""Turn each being's CITED behaviour text into a small ladder the connectome can climb.

The division of labour matters and is the whole reason this is allowed to exist:

    the fly decides WHEN and HOW HARD          the atlas decides WHAT

Nothing here invents a behaviour. Every rung is a verbatim phrase lifted from that entity's
own `behavior` / `communication` / `emotional_tone` field in atlas.json, and carries the
entity key it came from so the page can cite it the same way it cites a wall. The simulation
supplies one number - how hard the descending population is driving - and that number selects
which cited phrase is currently true.

This is not a claim that DMT entities are insects, or that a fly brain explains anything about
them. It is a way of making a depicted being move from measured biology instead of a sine
wave, and the page must say so plainly wherever it is used.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# Which being in the world maps to which atlas entity. These four are the ones trip.js builds.
BEINGS = {
    'elf': 'Self-transforming machine elves',
    'jester': 'The Jester / Trickster / Clown',
    'mother': 'The Divine Feminine',
    'mantis': 'Mantis & insectoid beings',
}

# The descending-rate band the ladder spans. Measured, not chosen: selftest.js drives the
# slice from 0 to 0.5 and the descending population moves from silent to 0.0721, crossing
# threshold around 0.006. Below that the slice is genuinely quiet and the being should be too.
# The thresholds are the engine's; the text they select is not.
DRIVE_RANGE = (0.004, 0.072)


def phrases(text):
    """Split a cited field into the clauses it already contains, without cutting quotations.

    Splitting on any comma shredded "it is sound, but you see it" into halves that say nothing.
    Commas inside quotes are left alone, and a clause has to be long enough to stand up on its
    own before it is allowed to become a rung.
    """
    if not text:
        return []
    text = re.sub(r'\s+', ' ', text).strip()
    protected, quotes = text, []
    for i, q in enumerate(re.findall(r"'[^']{4,}'|‘[^’]{4,}’", text)):
        token = '@@%d@@' % i
        protected = protected.replace(q, token, 1)
        quotes.append(q)
    # "and" joins two distinct actions as often as a comma does ("shows the visitor their
    # wounds AND holds them"), and a bare verb is still an action - dropping everything under
    # thirteen characters silently deleted "Enfolds", "reassures" and "heals", which left the
    # Divine Feminine with a one-rung ladder and nothing for the simulation to move along.
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
    parts = split
    out = []
    for p in parts:
        for i, q in enumerate(quotes):
            p = p.replace('@@%d@@' % i, q)
        p = p.strip().strip('.').strip()
        if len(p) >= 5:
            out.append(p)
    return out


def main():
    atlas = json.loads((ROOT / 'data' / 'atlas.json').read_text(encoding='utf-8'))
    by_name = {e['name']: e for e in atlas['entities']}
    built = {}
    for being, entity_name in BEINGS.items():
        e = by_name.get(entity_name)
        if not e:
            raise SystemExit('no atlas entity %r' % entity_name)
        # Rungs come ONLY from `behavior`, because rungs are things the being DOES. Tone and
        # communication describe how it feels and how it speaks; promoting those to rungs is
        # how the first pass ended up with "awe shaded with apprehension" as an action.
        pool = [{'says': p, 'field': 'behavior'} for p in phrases(e.get('behavior'))]
        ambient = {f: phrases(e.get(f)) for f in ('communication', 'emotional_tone')}
        if len(pool) < 2:
            raise SystemExit('%s: %d cited actions is not a ladder' % (being, len(pool)))
        # Every cited action becomes a rung, in the order the source wrote them. Fixing the
        # ladder at four forced two beings to be truncated and let the fourth rung fall on
        # whatever happened to sit at that index; using the whole pool means the source sets
        # both the content AND the resolution, and nothing gets dropped to fit a shape.
        ladder = []
        span = DRIVE_RANGE[1] - DRIVE_RANGE[0]
        for i, pick in enumerate(pool):
            lo = DRIVE_RANGE[0] + span * (i / float(len(pool)))
            hi = DRIVE_RANGE[0] + span * ((i + 1) / float(len(pool)))
            ladder.append({
                'rung': i,
                'descendingRate': [round(lo, 4), round(hi, 4) if i < len(pool) - 1 else 1.0],
                'says': pick['says'],
                'from_field': pick['field'],
                'cites': 'entity|' + entity_name,
            })
        built[being] = {
            'being': being,
            'entity': entity_name,
            'cites': 'entity|' + entity_name,
            'ladder': ladder,
            'ambient': ambient,
            'all_cited_phrases': len(pool),
        }
        print('%-7s %-32s %d cited phrases -> %d rungs' % (being, entity_name, len(pool), len(ladder)))

    (HERE / 'behaviour.json').write_text(json.dumps(built, indent=2, ensure_ascii=False),
                                         encoding='utf-8')
    (HERE / 'behaviour.js').write_text(
        '// GENERATED by flybrain/build_behaviour.py from data/atlas.json - do not hand-edit.\n'
        '// Every phrase is verbatim from the cited entity record. The simulation selects among\n'
        '// these; it never writes one.\n'
        'window.FlyBehaviour=' + json.dumps(built, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8')
    print('\nwrote behaviour.json and behaviour.js for %d beings' % len(built))


if __name__ == '__main__':
    main()
