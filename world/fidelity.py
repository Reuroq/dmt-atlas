"""Offline report-grounded fidelity ledger. Writes only beside this file.

--collect rebuilds counts from all tagged reports and their local raw passages.
Default regenerates the ledger/drawer from saved counts and human render grades.
--check exits nonzero until every target, route audit and fresh acceptance passes.
No screenshot is graded by this script; reviewers must inspect actual captures.
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORPUS = ROOT / 'data/corpus'
THRESHOLD = .80
WINDOW = 240
RENDER_FILES = ['index.html', 'trip.js', 'fractal.js', 'continuum.js', 'beings.js', 'trip.css', 'hud-alpha-ramp-v18.png', 'fidelity-ui.js', 'fidelity.css', 'vendor/three.min.js']
TARGETS = {
    'onset': ['phase|Inhalation / Onset'],
    'geometry': ['geometry|Static Pattern Overlay & filigree', 'geometry|Breathing & Liquid Surfaces', 'geometry|Fractal lattices & jeweled tilings'],
    'chrysanthemum': ['phase|The Chrysanthemum', 'geometry|The Chrysanthemum'],
    'rush': ['phase|The Rush', 'geometry|Zooming / Rushing Tunnel Flight'],
    'membrane': ['phase|Through the Membrane', 'realm|The Membrane / Veil', 'geometry|The Aperture / Iris Opening'],
    'waiting': ['realm|The Waiting Room', 'phase|Arrival — The Waiting Room'],
    'cathedral': ['realm|The Domed Cathedral'],
    'contact': ['phase|Entity Contact'],
    'download': ['phase|The Download / Lesson', 'geometry|Living language / visible sound'],
    'return': ['phase|The Return'],
    'afterglow': ['phase|Afterglow / Integration'],
    'workshop': ['realm|The Workshop / Factory / Market'],
    'garden': ['realm|The Garden'],
    'clinical': ['realm|The Hospital / Operating Theater'],
    'void': ['realm|The Void'],
    'elf': ['entity|Self-transforming machine elves'],
    'jester': ['entity|The Jester / Trickster / Clown'],
    'mother': ['entity|The Divine Feminine'],
    'mantis': ['entity|Mantis & insectoid beings'],
}
BEING_STAGES = {'elf': ['cathedral', 'contact', 'download', 'workshop'], 'jester': ['waiting', 'contact', 'download'], 'mother': ['garden'], 'mantis': ['clinical']}
# Frozen before visual grading. Count once per descriptor per report per target.
# These lexical families are inspectable measurements, not semantic certainty.
LEXICON = {
 'colour': {
  'multicoloured': r'rainbow\w*|multi[- ]?colou?re?d?|all (?:the )?colou?rs|every colou?r|many colou?rs|colou?rful|kaleidoscop\w*',
  'saturated / vivid': r'vivid\w*|vibrant\w*|saturat\w*|neon\w*|intense colou?rs?',
  'impossible colours': r'impossible colou?rs?|colou?rs? (?:I had |I have |i.ve )?never seen|new colou?rs?',
  'red': r'red|crimson|scarlet', 'orange': r'orange', 'yellow / gold': r'yellow\w*|gold(?:en)?',
  'green': r'green\w*|emerald', 'blue': r'blue\w*|azure|cyan|turquoise',
  'purple / pink': r'purple|violet|magenta|pink', 'white': r'white|whitish',
 },
 'light': {
  'bright / luminous': r'bright\w*|glow\w*|luminous|luminescen\w*|radiant|shining',
  'dark / black': r'dark(?:ness)?|black(?!\s*out)|pitch[- ]black',
  'flashing / pulsing light': r'flash\w*|flicker\w*|strob\w*|puls(?:ing|ating) light',
 },
 'motion': {
  'moving / animated': r'mov(?:e|es|ed|ing|ement)|animat\w*|in motion',
  'morphing / transforming': r'morph\w*|transform\w*|shape[- ]?shift\w*|chang(?:ing|ed) (?:shape|form)',
  'spinning / rotating': r'spin(?:ning|s)?|spun|rotat\w*|whirl\w*|swirl\w*',
  'breathing / undulating': r'breath(?:ing|ed) (?:walls|surfaces)|walls (?:were )?breathing|undulat\w*|rippl\w*|pulsat\w*|waving',
  'rushing / flying': r'rush(?:ing|ed)?|flying|flew|zoom\w*|accelerat\w*|propell\w*|launch\w*',
  'folding / unfolding': r'unfold\w*|fold(?:ing|ed|s)|bloom\w*|unfurl\w*',
  'receding / dissolving': r'reced\w*|fad(?:e|es|ing|ed)|dissolv\w*|disintegrat\w*|melt\w*',
 },
 'density': {
  'intricate / detailed': r'intricat\w*|detail\w*|complex\w*|elaborate',
  'dense / overwhelming': r'dense\w*|overwhelm\w*|filled (?:with|my vision)|everywhere|countless',
  'repeated / symmetrical': r'repeat\w*|symmetr\w*|tessellat\w*|tile[ds]?|tiling',
  'layered / multidimensional': r'layer\w*|dimensions?|dimensional|4[- ]?d|higher[- ]dimensional',
 },
 'form': {
  'geometry / patterns': r'geometr\w*|patterns?|shapes?',
  'fractals': r'fractal\w*', 'lattice / grid': r'lattic\w*|grids?|honeycomb\w*|cobweb\w*|mesh',
  'tunnel / corridor': r'tunnels?|corridors?|hallways?',
  'room / architecture': r'rooms?|walls?|ceilings?|buildings?|architectur\w*|palaces?|temples?|cathedrals?|domes?',
  'flower / mandala': r'flowers?|petals?|chrysanthem\w*|mandala\w*|rosettes?',
  'spirals / circles': r'spirals?|circl\w*|rings?|spheres?|orbs?',
  'faces': r'faces?|facial|masks?', 'eyes': r'eyes?|eyeballs?',
  'beings / presences': r'beings?|entit(?:y|ies)|presences?|creatures?|elves|elf|jesters?|mantis|insectoids?|goddess',
  'humanoid / bodies': r'humanoid\w*|bodies|body|heads?|limbs?|arms?|hands?',
  'insectoid anatomy': r'mantis|mantids?|insect\w*|antennae|claws?|mandibles?',
  'jester / clown form': r'jesters?|clowns?|tricksters?|harlequins?',
  'feminine form': r'feminine|female|woman|women|mother\w*|maternal|goddess',
  'plants / organic growth': r'plants?|trees?|leaves|leaf|vines?|vegetation|gardens?',
  'glyphs / writing': r'glyph\w*|hieroglyph\w*|symbols?|written|writing|letters?|runes?',
  'circuitry / machinery': r'circuit\w*|machin\w*|mechanical|gears?|clockwork|conduits?|wires?',
 },
 'material': {
  'jewelled / crystalline': r'jewel\w*|crystal\w*|diamonds?|gemstones?|gems?|facets?',
  'metallic / reflective': r'metall?ic|metal|chrome|silver|reflective|mirrors?|iridescen\w*',
  'liquid / flowing': r'liquid|fluid|flow(?:ing|ed|s)?|molten|watery',
  'transparent / ethereal': r'transparen\w*|translucen\w*|ethereal|hologra\w*|see[- ]through',
 },
 'scale': {
  'vast / infinite': r'vast|infinite\w*|endless\w*|boundless|enormous|massive|gigantic|huge|immense',
  'small / miniature': r'small|tiny|miniature|little (?:beings|elves|people|creatures)',
 },
 'sound-as-seen': {
  'visible sound / language': r'visible (?:sound|language)|see (?:the )?(?:sound|music)|sound.{0,35}(?:became|made|into) (?:a |the )?(?:shapes?|objects?|patterns?)|sing\w*.{0,35}(?:objects?|shapes?|into existence)',
 },
 'behaviour': {
  'communicating / teaching': r'communicat\w*|telepath\w*|teach\w*|taught|show(?:ed|ing)|told me',
  'welcoming / loving': r'welcom\w*|loving|love|caring|comfort\w*|embrac\w*|hug\w*|benevolen\w*',
  'playful / laughing': r'playful\w*|laugh\w*|giggl\w*|joking|mischiev\w*|teas(?:e|ing|ed)',
  'watching / examining': r'watch(?:ing|ed)|observ\w*|examin\w*|inspect\w*|operat(?:ing|ed)|surgery|surgical',
  'gesturing / offering': r'gestur\w*|offer\w*|beckon\w*|hand(?:ing|ed) me|present(?:ed|ing) (?:me|an? object)',
  'autonomous / intelligent': r'autonomous|intelligen\w*|sentient|conscious beings?',
 }
}
NEGATION = re.compile(r"\b(?:no|not|never|without|didn.t|wasn.t|weren.t|isn.t|aren.t|couldn.t)\s+(?:\w+\s+){0,3}$", re.I)
PATTERNS = [(name, category, re.compile(r'(?<![\w])(?:'+pattern+r')(?![\w])', re.I)) for category, items in LEXICON.items() for name, pattern in items.items()]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_signature():
    return hashlib.sha256(''.join(digest(HERE / f) for f in RENDER_FILES).encode()).hexdigest()


def excerpt(text, start, end, radius=WINDOW):
    lo, hi = max(0, start-radius), min(len(text), end+radius)
    # Keep boundary words whole while retaining original-text character offsets.
    if lo:
        space = text.find(' ', lo, start)
        if space >= 0:
            lo = space+1
    if hi < len(text):
        space = text.rfind(' ', end, hi)
        if space >= end:
            hi = space
    return lo, hi, text[lo:hi]


def collect():
    reports = [json.loads(s) for s in (CORPUS/'reports.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(reports) == 14309, 'Corpus changed: review the method before rebaselining.'
    indexed = {(r['sub'], r['id']): r for r in reports}
    assert len(indexed) == len(reports), 'Duplicate report identifiers'
    atlas = read(ROOT/'data/atlas.json')
    nodes = {kind+'|'+e['name']: e for kind, group in [('entity','entities'),('realm','realms'),('geometry','geometries'),('phase','phases')] for e in atlas[group]}
    targets_by_node = defaultdict(list)
    for target, keys in TARGETS.items():
        for key in keys:
            assert key in nodes, key
            targets_by_node[key].append(target)
    counts = {t: Counter() for t in TARGETS}
    report_ids = {t: defaultdict(list) for t in TARGETS}
    samples = {t: defaultdict(list) for t in TARGETS}
    tagged = Counter()
    available = Counter()
    passages = Counter()
    found = set()
    all_hits = Counter()
    for r in reports:
        for key in set('|'.join(n) for n in r['seq']):
            all_hits[key] += 1
        for target in {t for n in r['seq'] for t in targets_by_node['|'.join(n)]}:
            tagged[target] += 1
    with (HERE/'fidelity-passages.jsonl').open('w', encoding='utf-8') as out:
        for path in sorted((CORPUS/'raw').glob('*_posts.jsonl')):
            sub = path.name.removesuffix('_posts.jsonl')
            with path.open(encoding='utf-8') as raw:
                for line in raw:
                    r = json.loads(line)
                    identity = (sub, r.get('id'))
                    if identity not in indexed or identity in found:
                        continue
                    found.add(identity)
                    tagged_report = indexed[identity]
                    text = (r.get('title') or '')+'\n'+(r.get('selftext') or '')
                    assert len(text) == tagged_report['chars'], f'Raw offsets changed: {identity}'
                    per_target = defaultdict(list)
                    for node, pos in zip(tagged_report['seq'], tagged_report['pos'], strict=True):
                        key = '|'.join(node)
                        assert 0 <= pos < len(text)
                        for target in targets_by_node[key]:
                            per_target[target].append((key, pos))
                    for target, hits in per_target.items():
                        available[target] += 1
                        matches = {}
                        for key, pos in hits:
                            lo, hi, quote = excerpt(text, pos, pos+1)
                            descriptors = []
                            for name, category, pattern in PATTERNS:
                                for match in pattern.finditer(quote):
                                    if NEGATION.search(quote[max(0,match.start()-50):match.start()]):
                                        continue
                                    descriptors.append(name)
                                    qlo, qhi, sample = excerpt(text, lo+match.start(), lo+match.end(), 85)
                                    matches.setdefault(name, {'id': r['id'], 'sub': sub, 'node': key, 'node_offset': pos, 'match_offset': lo+match.start(), 'quote_start': qlo, 'quote_end': qhi, 'quote': sample})
                                    break
                            out.write(json.dumps({'target':target, 'id':r['id'], 'sub':sub, 'node':key, 'node_offset':pos, 'start':lo, 'end':hi, 'text':quote, 'descriptors':descriptors}, ensure_ascii=False)+'\n')
                            passages[target] += 1
                        for name, sample in matches.items():
                            counts[target][name] += 1
                            report_ids[target][name].append(sub+'/'+r['id'])
                            if len(samples[target][name]) < 3:
                                samples[target][name].append(sample)
    assert len(found) == len(reports), f'Missing raw reports: {len(reports)-len(found)}'
    summary = read(CORPUS/'summary.json')
    assert all(all_hits[x['kind']+'|'+x['name']] == x['reports'] for x in summary['per_node']), 'Summary mismatch'
    depictions = read(CORPUS/'depictions.json')
    result = {'method_version':1, 'reports':len(reports), 'raw_reports_resolved':len(found), 'window_chars_each_side':WINDOW,
              'input_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in [CORPUS/'reports.jsonl',CORPUS/'summary.json',CORPUS/'transitions.json',ROOT/'data/atlas.json',CORPUS/'depictions.json',*sorted((CORPUS/'raw').glob('*_posts.jsonl'))]},
              'lexicon_sha256':hashlib.sha256(json.dumps(LEXICON, sort_keys=True).encode()).hexdigest(), 'targets':{}}
    for target, keys in TARGETS.items():
        art_ids = list(dict.fromkeys(i for key in keys for i in depictions['per_node'].get(key, [])))
        rows = [{'descriptor':name, 'category':next(c for n,c,_ in PATTERNS if n==name), 'count':count, 'fraction':round(count/available[target],5), 'report_ids':report_ids[target][name], 'examples':samples[target][name]} for name,count in sorted(counts[target].items(), key=lambda x:(-x[1],x[0]))]
        result['targets'][target] = {'nodes':keys, 'tagged_reports':tagged[target], 'available_reports':available[target], 'passages':passages[target], 'minimum_passages':min(40,tagged[target]), 'descriptors':rows,
            'atlas':[{'key':key, 'description':nodes[key].get('appearance',nodes[key].get('description','')), 'sources':nodes[key].get('sources',[])} for key in keys],
            'depiction_candidates':len(art_ids), 'depiction_title_examples':[{k:depictions['items'][i].get(k) for k in ['id','title','author','kind','permalink']} for i in art_ids[:5] if i in depictions['items']]}
    write(HERE/'fidelity-corpus.json', result)
    return result


def route_audit():
    source = (HERE/'trip.js').read_text(encoding='utf-8')
    route = re.findall(r"\{id:'([^']+)'[^\n]*?duration:(\d+)", source)
    phases = {e['name']:e for e in read(ROOT/'data/atlas.json')['phases']}
    phase_map = {'geometry':'Inhalation / Onset', 'cathedral':'Breakthrough', 'void':'The Peak / Throne / Apex'}
    for target, keys in TARGETS.items():
        phase = next((key[6:] for key in keys if key.startswith('phase|')), None)
        if phase:
            phase_map[target] = phase
    transitions = read(CORPUS/'transitions.json')['transitions']
    counts = {(tuple(e['from']),tuple(e['to'])):e['n'] for e in transitions}
    edges = []
    for (a,_),(b,_) in zip(route,route[1:]):
        na, nb = ('phase',phase_map[a]), ('phase',phase_map[b])
        edges.append({'from':a, 'to':b, 'from_node':'|'.join(na), 'to_node':'|'.join(nb), 'forward':counts.get((na,nb),0), 'reverse':counts.get((nb,na),0),
            'atlas_order':[phases[na[1]]['order'],phases[nb[1]]['order']], 'shared_phase':na==nb})
    branch_edges = []
    for b in ['workshop','garden','clinical','void']:
        na,nb = tuple(TARGETS['cathedral'][0].split('|')),tuple(TARGETS[b][0].split('|'))
        branch_edges.append({'branch':b,'forward':counts.get((na,nb),0),'reverse':counts.get((nb,na),0)})
    return {'route':[{'stage':s,'seconds':int(d),'phase':phase_map[s]} for s,d in route], 'configured_seconds':sum(int(d) for _,d in route), 'edges':edges, 'branches':branch_edges,
        'limitations':'Transitions count adjacent first non-negated vocabulary mentions in narrative prose, not verified chronology or dwell times. Phase order is an atlas synthesis, not measured durations.',
        'departures':['Geometry subdivides onset; not a distinct measured phase.', 'Waiting (atlas phase 6) precedes Cathedral/Breakthrough (phase 5): an explicit atlas-order inversion, retained as the REDIRECT2 exploration hub; not claimed to follow every narrative.', 'Optional realms return to Cathedral for navigation; counts do not establish mandatory loops.', 'Peak is optional (Void), not a required throne encounter.', 'Configured stage seconds are editorial reading/exploration time, not corpus-derived experience timing. Free exploration, pauses and accessibility modes change duration.']}


def receipt_errors(review, signature):
    errors = []
    captures = review.get('captures', [])
    if not captures:
        return ['No inspected HIGH-detail capture receipts']
    for capture in captures:
        path = (HERE/capture.get('file','')).resolve()
        if not path.is_relative_to(HERE) or not path.is_file() or digest(path) != capture.get('sha256'):
            errors.append('Capture missing or changed')
        if capture.get('detail') != 'high' or capture.get('render_signature') != signature or not capture.get('inspection'):
            errors.append('Capture quality, freshness or visual inspection missing')
    return errors


def passage_audit(corpus, make_queue=False):
    """Keep raw lexical matches separate from manually confirmed local descriptions.

    Sampling order is a stable hash of target/sub/id, never chosen by how well
    descriptions fit the renderer. Exclusions stay in the ledger with reasons.
    """
    path = HERE/'fidelity-passage-review.json'
    if not path.exists():
        write(path, {'corpus_sha256':digest(HERE/'fidelity-corpus.json'), 'targets':{}})
    ledger = read(path)
    fresh = ledger.get('corpus_sha256') == digest(HERE/'fidelity-corpus.json')
    extra_path=HERE/'fidelity-extra-passages.jsonl'
    fresh &= ledger.get('extra_passages_sha256') == (digest(extra_path) if extra_path.exists() else None)
    records = {t:defaultdict(list) for t in TARGETS}
    for source_path in [HERE/'fidelity-passages.jsonl']+([extra_path] if extra_path.exists() else []):
        with source_path.open(encoding='utf-8') as source:
            for line in source:
                p=json.loads(line)
                identity=p['sub']+'/'+p['id']
                if source_path == extra_path:
                    assert identity in records[p['target']], 'Supplement must belong to an existing tagged candidate'
                    assert p.get('reason') and p['node'] in TARGETS[p['target']]
                records[p['target']][identity].append(p)
    result, queue = {}, {}
    for target, candidates in records.items():
        reviews = ledger.get('targets',{}).get(target,{}) if fresh else {}
        valid, excluded, errors = {}, [], []
        tally, examples = Counter(), defaultdict(list)
        order = sorted(candidates,key=lambda identity:hashlib.sha256((target+'/'+identity).encode()).hexdigest())
        for identity, review in reviews.items():
            if identity not in candidates or not review.get('reason'):
                errors.append('Unknown report or missing passage-review reason: '+identity)
                continue
            if review.get('decision') == 'exclude':
                excluded.append(identity)
                continue
            names=review.get('descriptors',[])
            allowed={d for p in candidates[identity] for d in p['descriptors']}
            # Relevant setting descriptions can have no dictionary match. Keep
            # them in the sample denominator without inventing a visual trait.
            if review.get('decision') != 'include' or not isinstance(names, list) or not set(names) <= allowed:
                errors.append('Invalid or ungrounded confirmed descriptors: '+identity)
                continue
            valid[identity]=names
            for name in set(names):
                tally[name]+=1
                if len(examples[name]) < 3:
                    p=next(p for p in candidates[identity] if name in p['descriptors'])
                    pattern=next(rx for n,_,rx in PATTERNS if n==name)
                    match=next(m for m in pattern.finditer(p['text']) if not NEGATION.search(p['text'][max(0,m.start()-50):m.start()]))
                    lo,hi,quote=excerpt(p['text'],match.start(),match.end(),85)
                    examples[name].append({'id':p['id'],'sub':p['sub'],'node':p['node'],'node_offset':p['node_offset'],'match_offset':p['start']+match.start(),'quote_start':p['start']+lo,'quote_end':p['start']+hi,'quote':quote})
        # A reviewer cannot skip difficult candidates to raise the score.
        decided=set(valid)|set(excluded)
        prefix=0
        for identity in order:
            if identity not in decided:
                break
            prefix+=1
        if decided-set(order[:prefix]):
            errors.append('Review must follow the fixed queue without skipping candidates')
        exhausted=len(decided)==len(candidates)
        enough=len(valid)>=40 or (exhausted and bool(valid))
        confirmed=[{'descriptor':name,'category':next(c for n,c,_ in PATTERNS if n==name),'count':count,'fraction':round(count/max(1,len(valid)),5),'examples':examples[name]} for name,count in sorted(tally.items(),key=lambda item:(-item[1],item[0]))]
        result[target]={'passed':fresh and enough and not errors,'reviewed_reports':len(decided),'included_reports':len(valid),'excluded_reports':len(excluded),'candidate_reports':len(candidates),'candidate_passages':sum(len(p) for p in candidates.values()),'exhausted':exhausted,'errors':errors,'descriptors':confirmed}
        if make_queue:
            queue[target]=[{'identity':i,'windows':candidates[i]} for i in order if i not in decided][:60]
    if make_queue:
        write(HERE/'fidelity-review-queue.json',queue)
    return result


def generate(corpus):
    grades_path = HERE/'fidelity-grades.json'
    if not grades_path.exists():
        write(grades_path, {'threshold':THRESHOLD, 'targets':{}, 'route_review':{}, 'acceptance':{}, 'history':[]})
    grades = read(grades_path)
    signature = render_signature()
    audit = route_audit()
    passages = passage_audit(corpus)
    rows = []
    for target, data in corpus['targets'].items():
        review = grades.get('targets',{}).get(target,{})
        errors = receipt_errors(review, signature)
        validated=passages[target]
        if not validated['passed']:
            errors.append('Ground-truth passage validation incomplete')
        descriptors = validated['descriptors'] if validated['passed'] else data['descriptors']
        if target in BEING_STAGES and not review.get('close_up'):
            errors.append('Being close-up not inspected')
        top = []
        for n,descriptor in enumerate(descriptors[:15]):
            name = descriptor['descriptor']
            grade = review.get('descriptors',{}).get(name,{})
            state = grade.get('grade','UNREVIEWED')
            observation = grade.get('observation','No render comparison yet.')
            if state not in ['PRESENT','PARTIAL','ABSENT','UNREVIEWED']:
                errors.append('Invalid grade: '+name)
                state = 'UNREVIEWED'
            if state != 'UNREVIEWED' and not grade.get('observation'):
                errors.append('Missing observation: '+name)
            if descriptor['category'] in ['motion','behaviour','sound-as-seen'] and state == 'PRESENT':
                times = {c.get('animTime') for c in review.get('captures',[]) if c.get('animTime') is not None}
                if len(times) < 2 or not grade.get('temporal_observation'):
                    errors.append('No temporal inspection: '+name)
            top.append({k:descriptor[k] for k in ['descriptor','category','count','fraction','examples']} | {'rank':n+1, 'grade':state, 'observation':observation})
        denominator = sum(d['count'] for d in top)
        coverage = sum(d['count']*{'PRESENT':1,'PARTIAL':.5,'ABSENT':0,'UNREVIEWED':0}[d['grade']] for d in top)/max(denominator,1)
        if len(top) < 15:
            errors.append('Fewer than 15 recurring descriptors')
        if data['passages'] < data['minimum_passages']:
            errors.append('Insufficient passages')
        if any(d['grade'] in ['ABSENT','UNREVIEWED'] for d in top[:10]):
            errors.append('Top ten contains ABSENT or UNREVIEWED')
        if any(d['grade']=='UNREVIEWED' for d in top):
            errors.append('Top fifteen not fully graded')
        if coverage < THRESHOLD:
            errors.append('Coverage below 80%')
        rows.append({'id':target,'reports':validated['included_reports'] if validated['passed'] else data['available_reports'],'candidate_reports':data['available_reports'],'passages':validated['candidate_passages'],'nodes':data['nodes'],'basis':'validated sample' if validated['passed'] else 'UNVALIDATED lexical candidates','passage_audit':{k:v for k,v in validated.items() if k!='descriptors'},'coverage':round(coverage,5),'passed':not errors,'blockers':list(dict.fromkeys(errors)),'descriptors':top})
    route_review = grades.get('route_review',{})
    route_pass = route_review.get('grade') == 'PASS' and route_review.get('audit_sha256') == hashlib.sha256(json.dumps(audit,sort_keys=True).encode()).hexdigest() and bool(route_review.get('rationale'))
    acceptance = grades.get('acceptance',{})
    acceptance_pass = True
    for section in ['desktop','mobile','paced','fallback']:
        item = acceptance.get(section,{})
        path = HERE/f'verification-{section}.json'
        acceptance_pass &= bool(item.get('passed') and item.get('render_signature') == signature and path.exists() and item.get('sha256') == digest(path) and read(path).get('passed') and read(path).get('render_signature') == signature)
    from realism import evaluate as evaluate_realism
    realism = evaluate_realism(HERE, TARGETS, BEING_STAGES, signature, digest)
    bundle = {'method_version':2,'threshold':THRESHOLD,'render_signature':signature,'passed':all(r['passed'] for r in rows) and route_pass and acceptance_pass and realism['passed'],'realism':realism,'route_passed':route_pass,'acceptance_passed':acceptance_pass,'route_audit':audit,'targets':sorted(rows,key=lambda r:(r['coverage'],r['id'])),'being_stages':BEING_STAGES}
    write(HERE/'fidelity-results.json',bundle)
    # Omit quotes from the shipped drawer bundle: full local audit samples remain in JSON/Markdown.
    public = json.loads(json.dumps(bundle))
    for target in public['targets']:
        for descriptor in target['descriptors']:
            descriptor['report_links'] = [{'id':e['id'],'sub':e['sub']} for e in descriptor.pop('examples')]
    (HERE/'fidelity-data.js').write_text('/* Generated by fidelity.py; measured lexical counts, manual render grades. */\nwindow.WORLD_FIDELITY = '+json.dumps(public,ensure_ascii=False)+';\n',encoding='utf-8')
    markdown(bundle,corpus,grades)
    for row in bundle['targets']:
        print(f"{row['id']:14} {row['coverage']:6.1%} {'PASS' if row['passed'] else 'PENDING/FAIL':12} {row['reports']:5} reports / {row['passages']:5} passages")
    print(f"Realism: {realism['passed']}; route review: {route_pass}; fresh acceptance: {acceptance_pass}; overall: {bundle['passed']}")
    return bundle['passed']


def cell(value):
    return str(value).replace('|',' / ').replace('\n',' ').replace('\r',' ')


def markdown(bundle, corpus, grades):
    lines = ['# Report-grounded fidelity test', '', '**Status: '+('PASS' if bundle['passed'] else 'NOT PASSED — incomplete or failing visual/route/functional review')+'**', '',
        '## Independent realism gate (REDIRECT4)', '',
        'Realism: **'+('PASS' if bundle['realism']['passed'] else 'NOT PASSED')+'**. See [REALISM.md](REALISM.md) for RECOGNISE / CLOSE / GAME judgments and specific visual/temporal reasons for all 15 stages and 4 beings. PENDING is uninspected, not a passing grade. Each target requires two fresh inspected HIGH frames from the actual walking camera; beings also require close-up observations. Hash-bound image and capture receipts are checked independently of descriptor coverage. Anything CLOSE or GAME must be rebuilt. This is an adversarial visual judgment, not witness certification. All realism, coverage, route and previous acceptance gates must pass.', '',
        '## Method fixed before grading', '',
        f"All {corpus['reports']:,} tagged records resolved to local raw posts. Each target uses the explicit node mapping below; being tallies are separate from scene tallies. All available matching reports are included (no popularity sampling). Extract ±{WINDOW} characters around every stored first node hit, preserving raw offsets; overlapping windows count a descriptor only once per report per target. At least 40 passages are required wherever 40 matching reports exist.", '',
        'A declared lexical family dictionary covers colour, light, motion, density, form, material, scale, sound-as-seen and being behaviour. Word boundaries and a limited preceding-negation filter reduce obvious false positives. Counts mean **reports with a local lexical match**, not independently validated perceptions, population prevalence or causal association with a stage. Nearby phrases may refer to other moments, quoted accounts, imagined comparisons or nonvisual experiences. Node words themselves can dominate form counts. Inspect the retained passages; do not treat an automated match as semantic proof. No descriptor dictionary changes should be made merely to improve a render score.', '',
        '**Passage-validation gate:** Initial spot checks found real-backyard Garden tags, earlier-trip beings near afterglow tags, and instructional/comparative prose near entity tags. Raw tallies therefore are candidate evidence, not ground truth. `fidelity-review-queue.json` orders reports by a fixed SHA256(target/sub/id); inspect in order, recording include/exclude with reasons and only locally confirmed descriptors in `fidelity-passage-review.json`. Continue until at least 40 relevant reports per target, or exhaust its entire candidate pool. Only then use the top 15 **confirmed sample** counts for visual scoring; keep the full-corpus lexical tallies separately. Do not add hallucinated beings to afterglow because a nearby earlier-trip mention was misattributed. Sample counts are not full-corpus prevalence estimates. Exclusions and small-sample limits remain visible.', '',
        'A title-only or truncated first-hit window may omit the actual vision. `fidelity-extra-passages.jsonl` retains explicitly justified, exact-offset supplementary windows around later mentions in the same tagged report. These supplement manual validation only, never inflate the original full-corpus lexical counts. Their file hash is bound to the passage-review ledger. Garden exhausted 27 candidates with only four relevant visionary settings; ordinary gardens (including open-eye alterations of real gardens) are excluded from this distinct-realm comparison. This tiny sample cannot support precise prevalence or a universal Garden design.', '',
        '`fidelity-corpus.json` retains all descriptor counts, report IDs, three exact-offset examples per descriptor, atlas descriptions/source references, credited depiction-title examples and input hashes. `fidelity-passages.jsonl` retains every node-hit window. Atlas text and depiction titles are corroboration, never added to report counts; no depiction images were fetched. Windows come from the existing first-hit tags, not an exhaustive re-tagging of every mention.', '',
        '**Coverage = Σ(report count × grade weight) / Σ(top-15 report counts)**; PRESENT=1, PARTIAL=.5, ABSENT=0. UNREVIEWED contributes zero but is not an observed absence. The fixed threshold is **80%**, with no ABSENT in the top ten and all fifteen reviewed. This allows limited representational compromises without passing a missing dominant motif. It is a practical visual proxy test, not certification of a subjective experience.', '',
        'Every grade needs a concrete visible observation and fresh HIGH-detail capture receipts (file hash, render signature, inspection label). Every being also needs a close-up. PRESENT motion/behaviour/sound-as-seen needs multiple animation times and a temporal observation: changed pixels alone do not prove morphing or communication. Impossible colours, felt intelligence, emotional love, bodily sensations and infinite resolution cannot be literally demonstrated by a monitor; use PARTIAL at most unless the descriptor itself describes a directly observable proxy, and state the limitation. Accessibility reductions are deliberate; do not add hazardous flashing to satisfy a lexical count.', '',
        'Workshop source review exhausted all 76 candidates: 28 included, 48 excluded, with eleven exact-offset supplements. Exclusions distinguish retail/film/metaphor matches, ordinary-room overlays, a mushroom experience, a later dream and the repeated market narrative DMT/9fbqsk (retaining DMT/crzkws). Mixed-substance reports remain explicitly identified. Relevant descriptions without dictionary matches remain in the denominator with zero descriptor votes. Markets, colourful manufacturing, minimalist white factories and black-and-white grids are contrasting variants, not one universal setting or population prevalence. Source validation is separate from the still-pending HIGH temporal visual review.', '',
        '## Worst target first', '', '| Target | Reports / passages | Coverage | Result |', '|---|---:|---:|---|']
    for row in bundle['targets']:
        lines.append(f"| {row['id']} | {row['reports']} / {row['passages']} | {row['coverage']:.1%} | {'PASS' if row['passed'] else 'PENDING / FAIL'} |")
    for row in bundle['targets']:
        pa=row['passage_audit']
        lines += ['', '## '+row['id'], '', 'Nodes: '+ '; '.join('`'+n+'`' for n in row['nodes']), '', f"Count basis: **{row['basis']}**. Passage review: {pa['included_reports']} included, {pa['excluded_reports']} excluded, {pa['candidate_reports']} candidate reports.", '', '| # | What reports say | Category | Reports | What the render shows | Grade |', '|---:|---|---|---:|---|---|']
        for d in row['descriptors']:
            lines.append(f"| {d['rank']} | {d['descriptor']} | {d['category']} | {d['count']} ({d['fraction']:.1%}) | {cell(d['observation'])} | {d['grade']} |")
        lines += ['', 'Blockers: '+('; '.join(row['blockers']) or 'none'), '', '### Passage audit samples', '']
        for d in row['descriptors']:
            if d['examples']:
                e=d['examples'][0]
                lines.append(f"- **{d['descriptor']}** — [{e['id']}](https://www.reddit.com/r/{e['sub']}/comments/{e['id']}/), raw offset {e['match_offset']}: “{cell(e['quote'])}”")
    audit=bundle['route_audit']
    lines += ['', '## Order and timing audit', '', audit['limitations'], '', '| Route edge (phase proxies) | Forward mentions | Reverse mentions | Atlas phase order |', '|---|---:|---:|---|']
    for e in audit['edges']:
        lines.append(f"| {e['from']} → {e['to']} | {'same phase' if e['shared_phase'] else e['forward']} | {'same phase' if e['shared_phase'] else e['reverse']} | {e['atlas_order'][0]} → {e['atlas_order'][1]} |")
    lines += ['', 'Cathedral ↔ optional realms (realm-node adjacent mentions):', '', '| Branch | Outward | Return |','|---|---:|---:|']
    lines += [f"| {e['branch']} | {e['forward']} | {e['reverse']} |" for e in audit['branches']]
    lines += ['', *['- '+s for s in audit['departures']], '', f"Configured main route: {audit['configured_seconds']} seconds before transition overhead; "+', '.join(f"{s['stage']} {s['seconds']}s" for s in audit['route'])+'.', '',
        '**Route/timing review: '+('PASS' if bundle['route_passed'] else 'PENDING — measured departures require explicit review, not automatic approval')+'**', '',
        'The corpus stores prose positions, not onset timestamps or phase dwell durations. Timing fidelity is unestablished; atlas phase descriptions provide qualitative constraints, not a measured distribution. A passing audit must justify each inversion/editorial departure and compare fresh real-time paced acceptance, without claiming empirical timing accuracy.', '',
        '## Visual iterations and functional gate', '',
        'Render edits, before/after grades and capture receipts belong in `fidelity-grades.json` history; an empty history means no completed visual correction loop. Older renders cannot pass after a renderer signature change.', '',
        'Fresh desktop, mobile, paced and fallback acceptance: **'+('PASS' if bundle['acceptance_passed'] else 'PENDING')+'**. Do not add the done marker until all targets, the route review and these regressions pass.', '',
        '## Reproduce', '', '```bash', '# Use the frozen corpus; do not recollect during visual/source review.', 'python3 world/fidelity.py --queue', 'python3 world/fidelity.py', 'python3 world/fidelity.py --check', '```', '',
        '`--collect` reads the local corpus only; default uses saved counts. `--check` exits 1 for incomplete/failing work. See `fidelity-grades.schema.md` for manual review receipts.', '']
    (HERE/'FIDELITY.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--queue',action='store_true',help='Write next 60 unreviewed reports per target in deterministic order')
    args=parser.parse_args()
    corpus=collect() if args.collect else read(HERE/'fidelity-corpus.json')
    if args.queue:
        passage_audit(corpus,make_queue=True)
    passed=generate(corpus)
    if args.check and not passed:
        raise SystemExit(1)
