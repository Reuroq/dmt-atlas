import assert from 'node:assert/strict';
import {readFile, mkdtemp, writeFile, rm} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {sample, DESCRIPTORS} from './sampler.js';

const read = async name => JSON.parse(await readFile(new URL(name, import.meta.url), 'utf8'));
const [distribution, schema] = await Promise.all([read('distributions.json'), read('schema.json')]);
const enums = node => [...(node.enum ?? []), ...(node.anyOf ?? []).flatMap(enums),
  ...(node.items ? enums(node.items) : [])];
const values = (def, field) => enums(schema.$defs[def].properties[field]);
function seeded(seed) {
  return () => ((seed = (Math.imul(1664525, seed) + 1013904223) >>> 0) / 2 ** 32);
}
const copy = x => JSON.parse(JSON.stringify(x));
const get = (object, pointer) => pointer.slice(1).split('/').reduce((v, k) =>
  v[k.replace(/~1/g, '/').replace(/~0/g, '~')], object);

// Stratified uniforms cover [0,1) once per 1,000 draws, in permuted order.
// This is a deterministic quadrature-style marginal check, not 1,000 IID draws.
function stratified(seed) {
  const jitter = seeded(seed);
  let i = 0;
  return () => (((i++ * 613) % 1000) + jitter()) / 1000;
}
function verifyMarginals(distribution) {
let measured = 0, unavailable = 0, marginals = 0;
const close = (actual, expected, label) => {
  assert.ok(Math.abs(actual - expected) <= .03, `${label}: ${actual} vs ${expected}`);
  marginals++;
};
function histogram(units, field, h, label) {
  if (!h.denominator.n) { assert.equal(units.length, 0, label); return; }
  assert.ok(units.length, label + ' has no sampled units');
  for (const [value, groups] of Object.entries(h.values)) {
    close(units.filter(u => Array.isArray(u[field]) ? u[field].includes(value) : u[field] === value).length
      / units.length, groups.unqualified.frequency, `${label}/${value}`);
  }
}
function scalars(units, profiles, paths, label) {
  const n = profiles.reduce((n, p) => n + p.n, 0);
  if (!n) { assert.equal(units.length, 0); return; }
  const safeGet = (v, path) => path.slice(1).split('/').reduce((v, k) => v?.[k], v) ?? null;
  for (const path of paths) {
    const expected = new Map();
    for (const p of profiles) {
      const flagged = p.context_flagged || p.uncertain_fields.some(f => path === f || path.startsWith(f + '/'));
      const value = flagged ? null : safeGet(p.value, path);
      expected.set(value, (expected.get(value) ?? 0) + p.n);
    }
    for (const [value, count] of expected) {
      close(units.filter(u => safeGet(u, path) === value).length / units.length,
        count / n, `${label}${path}=${value}`);
    }
  }
}
for (const [realm, strata] of Object.entries(distribution.realms)) {
  const rng = stratified(42);
  const scenes = [], outgoing = [];
  for (let i = 0; i < 1000; i++) {
    const result = sample(distribution, realm, rng);
    if (realm === '__unknown__' || strata.unqualified.scenes.n === 0) {
      assert.equal(result.status, 'no_evidence');
      assert.equal(result.parameters, null);
      assert.deepEqual(result.report_ids, []);
      continue;
    }
    assert.equal(result.status, 'sampled');
    scenes.push(result.parameters);
    if (result.outgoing.status === 'sampled') outgoing.push(result.outgoing);
  }
  if (realm === '__unknown__' || !strata.unqualified.scenes.n) { unavailable++; continue; }
  measured++;
  const s = strata.unqualified;
  for (const field of DESCRIPTORS) histogram(scenes, field, s.descriptors[field], `${realm}/${field}`);
  close(scenes.filter(s => s.beings?.length).length / 1000,
    s.being_presence.coded_present.frequency, realm + '/being_presence');
  const beings = scenes.flatMap(s => s.beings ?? []);
  for (const field of ['form', 'behaviour', 'communication', 'affect']) {
    histogram(beings, field, s.beings.fields[field], `${realm}/being/${field}`);
  }
  scalars(beings, s.beings.joint_profiles, ['/entity', '/count/min', '/count/max'], realm + '/being');
  const dwell = scenes.map(s => s.dwell).filter(Boolean);
  close(dwell.length / 1000, s.dwell.observed.frequency, realm + '/dwell_presence');
  histogram(dwell, 'basis', s.dwell.basis, realm + '/dwell_basis');
  scalars(dwell, s.dwell.joint_profiles, ['/description', '/seconds_min', '/seconds_max'], realm + '/dwell');
  for (const [i, edge] of distribution.transitions.entries()) {
    if (edge.from !== realm) continue;
    const draws = outgoing.filter(o => o.selection.edge_pointer === '/transitions/' + i);
    const expected = edge.sampling_eligible ? edge.n / s.scenes.n : 0;
    close(draws.length / 1000, expected, `${realm}/edge/${i}`);
    for (const field of ['trigger', 'abruptness']) {
      for (const [value, groups] of Object.entries(edge[field].values)) {
        const hits = draws.filter(o => Array.isArray(o.parameters[field])
          ? o.parameters[field].includes(value) : o.parameters[field] === value).length;
        close(hits / 1000, expected * groups.unqualified.frequency, `${realm}/edge/${i}/${field}/${value}`);
      }
    }
  }
}
return {measured, unavailable, marginals};
}
const production = verifyMarginals(distribution);

// Synthetic mechanics only: enums from canonical schema, no retained-data writes.
const realm = values('scene', 'place')[0];
const [lightA, lightB] = values('scene', 'light');
const [colourA, colourB] = values('scene', 'colour');
const blank = () => ({place: realm, ...Object.fromEntries(DESCRIPTORS.map(f => [f, []])),
  beings: [], dwell: null});
function profile(n, value, uncertain_fields = []) {
  return {n, value, uncertain_fields, context_flagged: false,
    report_ids: ['synthetic-only'], observations: Array.from({length: n}, (_, i) =>
      ({report_id: 'synthetic-only', pointer: `/scenes/${i}`}))};
}
const a = profile(3, {...blank(), light: [lightA], colour: [colourA]});
const b = profile(1, {...blank(), light: [lightB], colour: [colourB]});
b.observations[0].pointer = '/scenes/3';
const fixture = profiles => ({format_version: '2.0.0', status: 'synthetic_test_only',
  transitions: [],
  realms: {[realm]: {unqualified: {scenes: {n: profiles.reduce((n, p) => n + p.n, 0)},
    joint_profiles: profiles}}}});
const d = fixture([a, b]);
const before = JSON.stringify(d);
assert.equal(sample(d, realm, () => 0).parameters.light[0], lightA);
assert.equal(sample(d, realm, () => .75).parameters.light[0], lightB);
assert.equal(sample(d, realm, () => 1 - Number.EPSILON).parameters.light[0], lightB);
let hits = 0;
const rng = seeded(42);
for (let i = 0; i < 1000; i++) {
  const out = sample(d, realm, rng);
  const first = out.parameters.light[0] === lightA;
  hits += first;
  assert.equal(out.parameters.colour[0], first ? colourA : colourB);
  assert.equal(out.evidence['/light/0'].n, first ? 3 : 1);
  assert.deepEqual(out.evidence['/light/0'].report_ids, ['synthetic-only']);
  out.parameters.light.push('output-only-mutation');
  out.evidence['/light/0'].report_ids.push('output-only-mutation');
}
assert.ok(Math.abs(hits / 1000 - .75) <= .03);
assert.equal(JSON.stringify(d), before);

const being = {entity: values('being', 'entity')[0], form: values('being', 'form').slice(0, 2),
  count: {min: 1, max: 2}, behaviour: [values('being', 'behaviour')[0]],
  communication: [values('being', 'communication')[0]], affect: []};
const raw = {...blank(), light: [lightA, lightB], beings: [being],
  dwell: {description: 'synthetic duration', basis: values('dwell', 'basis')[1],
    seconds_min: 2, seconds_max: 5}};
const p = profile(1, raw, ['/light/0', '/beings/0/entity', '/beings/0/form/0', '/dwell/seconds_max']);
const out = sample(fixture([p]), realm, () => 0);
assert.deepEqual(out.parameters.light, [lightB]);
assert.equal(out.parameters.beings[0].entity, null);
assert.deepEqual(out.parameters.beings[0].form, [being.form[1]]);
assert.equal(out.parameters.dwell.seconds_max, null);
assert.equal(out.parameters.dwell.basis, raw.dwell.basis);
assert.equal(out.evidence['/light/0'].observations[0].pointer, '/scenes/0/light/1');
assert.equal(out.evidence['/beings/0/form/0'].observations[0].pointer, '/scenes/0/beings/0/form/1');
for (const [pointer, evidence] of Object.entries(out.evidence)) {
  for (const observation of evidence.observations) {
    assert.equal(get(out.parameters, pointer), get({scenes: [raw]}, observation.pointer));
  }
}
assert.ok(!Object.hasOwn(out.evidence, '/beings/0/entity'));
assert.ok(!Object.hasOwn(out.parameters, 'transition'));
const never = () => {throw new Error('No-evidence must not consume RNG');};
assert.equal(sample(fixture([]), realm, never).status, 'no_evidence');
assert.equal(sample(d, 'unlisted', never).status, 'no_evidence');
assert.equal(sample(d, '__unknown__', never).status, 'no_evidence');
for (const flags of [{context_flagged: true}, {uncertain_fields: ['/place']}]) {
  assert.equal(sample(fixture([{...a, ...flags}]), realm, never).status, 'no_evidence');
}
for (const bad of [-1, 1, NaN, Infinity, '0.5']) {
  assert.throws(() => sample(d, realm, () => bad), RangeError);
}
assert.throws(() => sample({...d, format_version: '1.0.0'}, realm), TypeError);
const broken = copy(d);
broken.realms[realm].unqualified.scenes.n++;
assert.throws(() => sample(broken, realm), TypeError);
assert.throws(() => sample(fixture([{...a, report_ids: ['wrong']}]), realm), TypeError);
const repeated = copy(a);
repeated.observations[1] = copy(repeated.observations[0]);
assert.throws(() => sample(fixture([repeated]), realm), /Duplicate scene/);
assert.throws(() => sample(fixture([a, copy(a)]), realm), /Duplicate scene/);
for (const pointer of ['/scenes/00', '/scenes/-1', '/scenes/1/extra']) {
  const bad = profile(1, blank());
  bad.observations[0].pointer = pointer;
  assert.throws(() => sample(fixture([bad]), realm), /Invalid joint-profile observation/);
}
// No cache: in-place replacement must affect the next call as well as new objects.
const replaced = copy(d);
sample(replaced, realm, () => 0);
replaced.realms[realm].unqualified.joint_profiles[0].value.light = [lightB];
assert.equal(sample(replaced, realm, () => 0).parameters.light[0], lightB);
const transition = {trigger: values('transition', 'trigger').slice(0, 2),
  abruptness: values('transition', 'abruptness')[0]};
const linked = fixture([profile(3, {...blank(), transition})]);
function edge(index, to) {
  return {from: realm, to, order_confidence: values('scene', 'order_confidence')[0],
    flagged_endpoints: false, flagged_order: false, flagged_episode: false, sampling_eligible: true,
    observations: [{report_id: 'synthetic-only', transition_pointer: `/scenes/${index}/transition`,
      destination_pointer: `/scenes/${index + 1}`}], joint_profiles: [{...profile(1, transition),
        observations: [{report_id: 'synthetic-only', pointer: `/scenes/${index}/transition`}],
        uncertain_fields: ['/trigger/0', '/abruptness']}]};
}
const targetA = values('scene', 'place')[1], targetB = values('scene', 'place')[2];
linked.transitions = [edge(0, targetA), edge(1, targetB)];
assert.equal(sample(linked, realm, () => 0).outgoing.parameters.to, targetA);
assert.equal(sample(linked, realm, () => .34).outgoing.parameters.to, targetB);
assert.equal(sample(linked, realm, () => .8).outgoing.status, 'no_evidence');
const linkResult = sample(linked, realm, () => 0).outgoing;
assert.deepEqual(linkResult.parameters.trigger, [transition.trigger[1]]);
assert.equal(linkResult.parameters.abruptness, null);
assert.equal(linkResult.evidence['/trigger/0'].observations[0].pointer, '/scenes/0/transition/trigger/1');
assert.equal(linkResult.evidence['/to'].n, 1);
for (const override of [{flagged_endpoints: true}, {flagged_order: true}, {flagged_episode: true},
  {sampling_eligible: false}, {order_confidence: values('scene', 'order_confidence')[2]},
  {order_confidence: null}, {to: '__unknown__'}]) {
  const d = copy(linked);
  Object.assign(d.transitions[0], override);
  assert.equal(sample(d, realm, () => 0).outgoing.status, 'no_evidence');
}
const duplicate = copy(linked);
duplicate.transitions.push(copy(duplicate.transitions[0]));
assert.throws(() => sample(duplicate, realm, () => 0), /Duplicate outgoing/);
const badDestination = copy(linked);
badDestination.transitions[0].observations[0].destination_pointer = '/scenes/2';
assert.throws(() => sample(badDestination, realm, () => 0), /next scene/);
const absentProfile = copy(linked);
absentProfile.transitions[0].joint_profiles = [];
assert.throws(() => sample(absentProfile, realm, () => 0), /missing or ambiguous/);
const mismatched = copy(linked);
mismatched.transitions[0].joint_profiles[0].value.trigger = [];
assert.throws(() => sample(mismatched, realm, () => 0), /bundles disagree/);
const badLinkEvidence = copy(linked);
badLinkEvidence.transitions[0].joint_profiles[0].n++;
assert.throws(() => sample(badLinkEvidence, realm, () => 0), /Invalid joint-profile evidence/);
// Exercise actual aggregate output without creating fixtures or loading retained examples.
const synthetic = JSON.parse(execFileSync('/home/clawd/corpus-venv/bin/python', ['-c', `
import json
from copy import deepcopy
from aggregate import aggregate, enums, DESCRIPTORS
s=json.load(open('schema.json')); v=json.load(open('vocab.json'))
records=[]; tagged=[]
for ri, realm in enumerate(v['catalog']['realm']):
 for kind in range(4):
  rid=f'synthetic-only-{ri}-{kind}'
  scenes=[]
  for index in range(3):
   scene={f:enums(s,'scene',f)[kind%2:kind%2+1] for f in DESCRIPTORS}
   scene.update(place=realm['slug'],order_confidence=enums(s,'scene','order_confidence')[kind%3],
    episode_index=0 if kind!=3 else index,quotes=[],uncertain_fields=[],beings=[],dwell=None,
    transition={'trigger':enums(s,'transition','trigger')[:2],
                'abruptness':enums(s,'transition','abruptness')[kind%2]} if index<2 and kind!=3 else None)
   if kind<3:
    being={f:enums(s,'being',f)[kind:kind+2] for f in ('form','behaviour','communication','affect')}
    being.update(entity=enums(s,'being','entity')[kind],count={'min':kind+1,'max':None if kind==2 else kind+1})
    scene['beings']=[being,deepcopy(being)] if kind==1 else [being]
    scene['dwell']={'description':f'synthetic duration {kind}', 'basis':enums(s,'dwell','basis')[kind],
                    'seconds_min':kind+1,'seconds_max':kind+2}
   if kind==1:
    scene['uncertain_fields']=[f'/scenes/{index}/light/0',f'/scenes/{index}/beings/0/entity',
     f'/scenes/{index}/beings/1/form/0',f'/scenes/{index}/dwell/seconds_max']
    if index<2: scene['uncertain_fields'] += [f'/scenes/{index}/transition/trigger/0',f'/scenes/{index}/transition/abruptness']
   if kind==2 and index==1: scene['uncertain_fields']=[f'/scenes/{index}/order_confidence']
   scenes.append(scene)
  records.append({'report_id':rid,'is_trip_report':True,'scenes':scenes})
  tagged.append({'id':rid,'seq':[['realm',realm['name']]]})
summary={'reports':len(tagged),'per_node':[{'kind':'realm','name':r['name'],'reports':4} for r in v['catalog']['realm']]}
print(json.dumps({'distribution':aggregate(records,s,v,tagged,summary),'records':records},separators=(',',':')))
`], {cwd: new URL('.', import.meta.url), env: {...process.env, PYTHONDONTWRITEBYTECODE: '1'},
  maxBuffer: 24 * 1024 * 1024, encoding: 'utf8'}));
const aggregateChecks = verifyMarginals(synthetic.distribution);
const sources = new Map(synthetic.records.map(r => [r.report_id, r]));
let links = 0;
for (const realm of Object.keys(synthetic.distribution.realms)) {
  const rng = stratified(13);
  for (let i = 0; i < 1000; i++) {
    const result = sample(synthetic.distribution, realm, rng);
    if (result.status !== 'sampled') continue;
    for (const bundle of [result, result.outgoing]) {
      if (bundle.status !== 'sampled') continue;
      for (const [pointer, e] of Object.entries(bundle.evidence)) {
        for (const o of e.observations) assert.equal(get(bundle.parameters, pointer), get(sources.get(o.report_id), o.pointer));
      }
    }
    if (result.outgoing.status !== 'sampled') continue;
    links++;
    const o = result.outgoing.selection.observations[0];
    const source = get(sources.get(o.report_id), result.selection.sampled_observation.pointer);
    const dest = get(sources.get(o.report_id), o.destination_pointer);
    assert.equal(source.episode_index, dest.episode_index);
    assert.ok(values('scene', 'order_confidence').slice(0, 2).includes(dest.order_confidence));
    assert.equal(o.report_id, result.selection.sampled_observation.report_id);
  }
}
console.log(`Production: 1,000 calls/realm; ${production.measured} measured realms, ${production.marginals} marginals; ${production.unavailable} unavailable.`);
console.log(`Synthetic mechanics PASS; weighted draw ${(hits / 1000).toFixed(3)} vs 0.750. No corpus fidelity claim.`);
console.log(`Synthetic aggregate: ${aggregateChecks.measured} realms, ${aggregateChecks.marginals} marginals within .03; ${links} qualified links checked against source records.`);

// Optional real browser smoke, foreground only; temporary files stay under corpus/.
if (process.argv.includes('--browser')) {
  const dir = await mkdtemp(new URL('.sampler-browser-', import.meta.url));
  try {
    const page = `${dir}/index.html`;
    await writeFile(page, `<!doctype html><body><script type="module">
import {sample} from ${JSON.stringify(new URL('sampler.js', import.meta.url).href)};
try {
  const d = ${JSON.stringify(d)}, linked = ${JSON.stringify(linked)}, realm = ${JSON.stringify(realm)};
  const check = (ok) => {if (!ok) throw new Error('browser assertion');};
  check(typeof process === 'undefined' && typeof require === 'undefined');
  const first = sample(d, realm, () => 0);
  check(first.parameters.light[0] === ${JSON.stringify(lightA)});
  check(first.evidence['/light/0'].observations[0].pointer === '/scenes/0/light/0');
  check(sample(d, realm, () => .75).parameters.colour[0] === ${JSON.stringify(colourB)});
  check(sample(linked, realm, () => 0).outgoing.parameters.to === ${JSON.stringify(targetA)});
  check(sample(linked, realm, () => .8).outgoing.status === 'no_evidence');
  check(sample(d, '__unknown__', () => {throw new Error('RNG consumed');}).status === 'no_evidence');
  first.parameters.light.push('detached');
  check(d.realms[realm].unqualified.joint_profiles[0].value.light.length === 1);
  let rejected = false;
  try {sample(d, realm, () => 1);} catch (e) {rejected = e instanceof RangeError;}
  check(rejected);
  document.body.dataset.result = 'pass';
} catch (error) {document.body.dataset.result = 'fail'; document.body.textContent = String(error);}
</script>`);
    const browser = process.env.SAMPLER_BROWSER || '/usr/bin/google-chrome';
    const dom = execFileSync(browser, ['--headless', '--no-sandbox', '--disable-gpu',
      '--disable-background-networking', '--disable-component-update', '--no-first-run',
      '--no-default-browser-check', '--disable-crash-reporter', '--allow-file-access-from-files',
      `--user-data-dir=${dir}/profile`, `--crash-dumps-dir=${dir}/crashes`,
      '--dump-dom', pathToFileURL(page).href], {encoding: 'utf8', timeout: 30000,
      env: {...process.env, TMPDIR: dir, XDG_CONFIG_HOME: dir, XDG_CACHE_HOME: dir},
      stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 4 * 1024 * 1024});
    assert.match(dom, /<body data-result="pass">/, 'Browser module smoke failed');
    console.log('Headless Chrome ES-module smoke PASS (scene, links, evidence, RNG, detached output).');
  } finally {await rm(dir, {recursive: true, force: true});}
}

// Opt-in synthetic scale measurements, not a hardware-dependent pass threshold.
if (process.argv.includes('--benchmark')) {
  function measure(label, data, draws) {
    const rng = seeded(42), times = [];
    for (let i = 0; i < draws + 5; i++) {
      const start = performance.now();
      assert.equal(sample(data, realm, rng).status, 'sampled');
      if (i >= 5) times.push(performance.now() - start);
    }
    times.sort((a, b) => a - b);
    console.log(`Scale ${label}: ${draws} draws; p50=${times[Math.floor(draws * .5)].toFixed(2)}ms, p95=${times[Math.floor(draws * .95)].toFixed(2)}ms.`);
  }
  for (const n of [100, 1000, 10000]) {
    const profiles = Array.from({length: n}, (_, i) => {
      const p = profile(1, {...blank(), transition,
        dwell: {description: `synthetic-${i}`, basis: values('dwell', 'basis')[0],
          seconds_min: null, seconds_max: null}});
      p.report_ids = [`scale-${i}`];
      p.observations[0].report_id = p.report_ids[0];
      return p;
    });
    const data = fixture(profiles), e = edge(0, targetA);
    e.observations = profiles.map(p => ({report_id: p.report_ids[0],
      transition_pointer: '/scenes/0/transition', destination_pointer: '/scenes/1'}));
    e.joint_profiles = [{...profile(n, transition), report_ids: profiles.map(p => p.report_ids[0]).sort(),
      observations: profiles.map(p => ({report_id: p.report_ids[0], pointer: '/scenes/0/transition'}))}];
    data.transitions = [e];
    measure(`${n} distinct profiles + links`, data, 100);
  }
  measure('one profile / 10000 support observations',
    fixture([profile(10000, {...blank(), light: [lightA], colour: [colourA]})]), 25);
}
