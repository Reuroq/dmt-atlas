/** Offline, dependency-free ES module. See SAMPLER.md for evidence semantics. */
export const DESCRIPTORS = Object.freeze([
  'light', 'colour', 'motion', 'geometry', 'material', 'density',
  'scale', 'sound_seen', 'affect',
]);
const FIELDS = ['place', ...DESCRIPTORS, 'beings', 'dwell'];
const escapePointer = key => String(key).replace(/~/g, '~0').replace(/\//g, '~1');
const clone = value => JSON.parse(JSON.stringify(value));

function checkDistribution(d) {
  if (d?.format_version !== '2.0.0' || !d.realms || !Array.isArray(d.transitions)) {
    throw new TypeError('Expected aggregate distribution format 2.0.0');
  }
}

function checkEvidence(p, pointerPattern, seen = new Set()) {
  if (!Number.isSafeInteger(p.n) || p.n <= 0 ||
      !Array.isArray(p.observations) || p.observations.length !== p.n ||
      !Array.isArray(p.report_ids) || !p.report_ids.length ||
      !Array.isArray(p.uncertain_fields) || typeof p.context_flagged !== 'boolean') {
    throw new TypeError('Invalid joint-profile evidence');
  }
  const ids = new Set();
  for (const o of p.observations) {
    if (!o || typeof o.report_id !== 'string' || !o.report_id ||
        typeof o.pointer !== 'string' || !pointerPattern.test(o.pointer)) {
      throw new TypeError('Invalid joint-profile observation');
    }
    const key = JSON.stringify([o.report_id, o.pointer]);
    if (seen.has(key)) throw new TypeError('Duplicate scene/profile observation');
    seen.add(key);
    ids.add(o.report_id);
  }
  if (JSON.stringify([...ids].sort()) !== JSON.stringify(p.report_ids) ||
      p.uncertain_fields.some(f => typeof f !== 'string' || !f.startsWith('/'))) {
    throw new TypeError('Invalid joint-profile evidence');
  }
}

function checkProfile(p, realm, seen) {
  checkEvidence(p, /^\/scenes\/(0|[1-9]\d*)$/, seen);
  if (p.value?.place !== realm || FIELDS.some(f => !Object.hasOwn(p.value, f)) ||
      DESCRIPTORS.some(f => !Array.isArray(p.value[f])) ||
      !Array.isArray(p.value.beings)) {
    throw new TypeError('Invalid scene joint profile');
  }
}

function noEvidence(d, realm, reason) {
  return {status: 'no_evidence', realm, reason, dataset_status: d.status,
    parameters: null, evidence: {}, report_ids: [], selection: null};
}

// Project a bundle without assuming independence or manufacturing missing values.
function projectFields(profile, fields) {
  const evidence = {}, suppressed = [];
  function project(value, sourcePath, outputPath) {
    if (profile.uncertain_fields.some(p => sourcePath === p || sourcePath.startsWith(p + '/'))) {
      suppressed.push(sourcePath);
      return undefined;
    }
    if (value === null) return null;
    if (Array.isArray(value)) {
      const result = [];
      value.forEach((v, i) => {
        const child = project(v, sourcePath + '/' + i, outputPath + '/' + result.length);
        if (child !== undefined) result.push(child);
      });
      return result;
    }
    if (typeof value === 'object') {
      return Object.fromEntries(Object.entries(value).map(([key, v]) => [key,
        project(v, sourcePath + '/' + escapePointer(key), outputPath + '/' + escapePointer(key)) ?? null]));
    }
    evidence[outputPath] = {n: profile.n, report_ids: [...profile.report_ids],
      observations: profile.observations.map(o => ({report_id: o.report_id,
        pointer: o.pointer + sourcePath}))};
    return value;
  }
  return {parameters: Object.fromEntries(fields.map(field =>
    [field, project(profile.value[field], '/' + field, '/' + field) ?? null])),
    evidence, suppressed};
}

function outgoingLink(d, realm, sceneProfile, source) {
  const none = {status: 'no_evidence', reason: 'no_eligible_observed_link',
    parameters: null, evidence: {}, report_ids: [], selection: null};
  const pointer = source.pointer + '/transition';
  const matches = [];
  for (const [edgeIndex, edge] of d.transitions.entries()) {
    if (edge.from !== realm) continue;
    if (!Array.isArray(edge.observations)) throw new TypeError('Invalid transition observations');
    for (const observation of edge.observations) {
      if (observation.report_id === source.report_id && observation.transition_pointer === pointer) {
        matches.push({edge, edgeIndex, observation});
      }
    }
  }
  if (!matches.length) return none;
  if (matches.length !== 1) throw new TypeError('Duplicate outgoing observation');
  const {edge, edgeIndex, observation} = matches[0];
  // Never rely on the eligibility boolean alone to clear qualifications.
  if (edge.sampling_eligible !== true || edge.flagged_endpoints !== false ||
      edge.flagged_order !== false || edge.flagged_episode !== false ||
      !['high', 'medium'].includes(edge.order_confidence) ||
      typeof edge.to !== 'string' || edge.to === '__unknown__' ||
      sceneProfile.uncertain_fields.includes('/episode_index')) return none;
  const expectedDestination = '/scenes/' + (Number(source.pointer.split('/')[2]) + 1);
  if (observation.destination_pointer !== expectedDestination) {
    throw new TypeError('Transition destination must be the next scene');
  }
  if (!Array.isArray(edge.joint_profiles)) throw new TypeError('Invalid transition profiles');
  const profiles = edge.joint_profiles.filter(p => p.observations?.some(o =>
    o.report_id === source.report_id && o.pointer === pointer));
  if (profiles.length !== 1) throw new TypeError('Transition profile evidence is missing or ambiguous');
  const p = profiles[0];
  checkEvidence(p, /^\/scenes\/(0|[1-9]\d*)\/transition$/);
  if (p.context_flagged !== false) return none;
  if (!Array.isArray(p.uncertain_fields) ||
      p.uncertain_fields.some(f => typeof f !== 'string' || !f.startsWith('/')) ||
      !Array.isArray(p.value?.trigger) ||
      !Object.hasOwn(p.value, 'abruptness') ||
      JSON.stringify(p.value.trigger) !== JSON.stringify(sceneProfile.value.transition?.trigger) ||
      p.value.abruptness !== sceneProfile.value.transition?.abruptness) {
    throw new TypeError('Scene and transition bundles disagree');
  }
  // Also honor the originating scene's flags; link qualification is not field qualification.
  const flags = [...p.uncertain_fields, ...sceneProfile.uncertain_fields
    .filter(f => f.startsWith('/transition/')).map(f => f.slice('/transition'.length))];
  if (sceneProfile.uncertain_fields.includes('/transition')) return none;
  const projected = projectFields({...p, uncertain_fields: flags, n: 1,
    report_ids: [source.report_id], observations: [{report_id: source.report_id, pointer}]},
  ['trigger', 'abruptness']);
  const one = suffix => ({n: 1, report_ids: [source.report_id], observations: [
    {report_id: source.report_id, pointer: observation.destination_pointer + suffix}]});
  return {status: 'sampled', parameters: {to: edge.to,
    order_confidence: edge.order_confidence, ...projected.parameters},
    evidence: {'/to': one('/place'), '/order_confidence': one('/order_confidence'),
      ...projected.evidence}, report_ids: [source.report_id],
    selection: {method: 'outgoing_link_of_selected_scene_observation', n: 1,
      edge_pointer: '/transitions/' + edgeIndex, observations: [clone(observation)],
      suppressed_fields: projected.suppressed}};
}

/** Draw one observed scene bundle, with replacement. rng() must be in [0, 1). */
export function sample(distributions, realm, rng = Math.random) {
  checkDistribution(distributions);
  if (typeof realm !== 'string' || typeof rng !== 'function') {
    throw new TypeError('Expected a realm slug and RNG function');
  }
  if (realm === '__unknown__') return noEvidence(distributions, realm, 'unknown_realm');
  if (!Object.hasOwn(distributions.realms, realm)) {
    return noEvidence(distributions, realm, 'realm_not_in_distribution');
  }
  const stratum = distributions.realms[realm].unqualified;
  if (!Array.isArray(stratum?.joint_profiles) ||
      !Number.isSafeInteger(stratum.scenes?.n) || stratum.scenes.n < 0) {
    throw new TypeError('Invalid realm stratum');
  }
  let total = 0;
  const eligible = [];
  const seen = new Set();
  for (const [index, profile] of stratum.joint_profiles.entries()) {
    checkProfile(profile, realm, seen);
    total += profile.n;
    // A flagged place is contextual, even if incorrectly filed as unqualified.
    if (!profile.context_flagged && !profile.uncertain_fields.includes('/place')) {
      eligible.push({profile, index});
    }
  }
  if (!Number.isSafeInteger(total) || total !== stratum.scenes.n) {
    throw new TypeError('Scene counts and joint-profile weights disagree');
  }
  const eligibleN = eligible.reduce((sum, {profile}) => sum + profile.n, 0);
  if (!eligibleN) return noEvidence(distributions, realm, 'no_eligible_scene_profiles');
  const u = rng();
  if (!Number.isFinite(u) || u < 0 || u >= 1) {
    throw new RangeError('rng() must return a finite number in [0, 1)');
  }
  let threshold = u * eligibleN;
  let selected = eligible[eligible.length - 1];
  for (const entry of eligible) {
    if (threshold < entry.profile.n) { selected = entry; break; }
    threshold -= entry.profile.n;
  }
  const {profile, index} = selected;
  // The residual selects one observation uniformly within the chosen profile,
  // using the same RNG draw. This preserves scene/link correlations and endings.
  const source = profile.observations[Math.min(profile.n - 1, Math.floor(threshold))];
  const {parameters, evidence, suppressed} = projectFields(profile, FIELDS);
  return {status: 'sampled', realm, dataset_status: distributions.status,
    parameters, evidence, report_ids: [...profile.report_ids],
    outgoing: outgoingLink(distributions, realm, profile, source),
    selection: {method: 'scene_joint_profile_weighted_by_n',
      profile_pointer: '/realms/' + escapePointer(realm) + '/unqualified/joint_profiles/' + index,
      n: profile.n, eligible_n: eligibleN, probability: profile.n / eligibleN,
      observations: clone(profile.observations),
      sampled_observation: clone(source),
      excluded_context_n: total - eligibleN,
      suppressed_fields: suppressed,
      omitted_fields: ['order_confidence', 'transition']}};
}
