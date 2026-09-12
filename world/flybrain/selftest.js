// Does the slice actually behave like a circuit, or is it an expensive random number?
//
// Three things have to be true before any of this is allowed to drive a being:
//   1. descending output rises with visual drive - otherwise the wiring is doing nothing
//   2. the real wiring beats shuffled wiring - otherwise the connectome is decoration
//   3. it runs fast enough to sit next to a WebGL scene
//
// Run: node selftest.js
const fs = require('fs');
const zlib = require('zlib');
const S = require('./sim.js');

function load() {
  const raw = zlib.gunzipSync(fs.readFileSync(__dirname + '/data/circuit.bin.gz'));
  return raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
}

function fresh(buf, opts) {
  const b = new S.Brain(buf, opts);
  return b;
}

function run(b, drive, steps) {
  const t = Date.now();
  let fired = 0;
  for (let s = 0; s < steps; s++) fired += b.step(drive);
  const r = b.readout();
  r.ms = Date.now() - t;
  r.fired = fired;
  return r;
}

const buf = load();
const probe = fresh(buf);
console.log('loaded %d neurons, %d connections', probe.n, probe.m);
console.log('  visual_projection %d, central %d, descending %d',
  probe.vpIndex.length, probe.n - probe.vpIndex.length - probe.dnIndex.length,
  probe.dnIndex.length);

console.log('\n1. does descending output track visual drive?');
const curve = [];
for (const d of [0, 0.05, 0.1, 0.2, 0.35, 0.5]) {
  const b = fresh(buf);
  const r = run(b, d, 300);
  curve.push([d, r.descendingRate]);
  console.log('   drive %s  %sms/300 steps  spikes %s  descendingRate %s  active %s/%d',
    d.toFixed(2), String(r.ms).padStart(4), String(r.fired).padStart(7),
    r.descendingRate.toFixed(4), String(r.descendingActive).padStart(4), b.dnIndex.length);
}
const monotone = curve.every((p, i) => i === 0 || p[1] >= curve[i - 1][1] - 1e-6);
const spread = curve[curve.length - 1][1] - curve[0][1];
console.log('   monotonic: %s   range: %s', monotone, spread.toFixed(4));

console.log('\n2. does the real wiring matter? (same statistics, shuffled targets)');
const real = fresh(buf);
const realR = run(real, 0.2, 300);
const shuf = fresh(buf);
// Degree-preserving shuffle: identical weight multiset and identical out-degree per neuron,
// only the targets are randomised. If the connectome carries structure, this should differ.
const tgt = shuf.csr.tgt;
for (let i = tgt.length - 1; i > 0; i--) {
  const j = (Math.random() * (i + 1)) | 0;
  const t = tgt[i]; tgt[i] = tgt[j]; tgt[j] = t;
}
const shufR = run(shuf, 0.2, 300);
console.log('   real     descendingRate %s   active %d', realR.descendingRate.toFixed(4), realR.descendingActive);
console.log('   shuffled descendingRate %s   active %d', shufR.descendingRate.toFixed(4), shufR.descendingActive);
const differs = Math.abs(realR.descendingRate - shufR.descendingRate) > 1e-3
  || Math.abs(realR.descendingActive - shufR.descendingActive) > 5;
console.log('   wiring changes the outcome: %s', differs);

console.log('\n3. is it fast enough to sit next to a 3D scene?');
const perf = fresh(buf);
const p = run(perf, 0.2, 600);
const perStep = p.ms / 600;
console.log('   %sms for 600 steps = %sms/step -> %d steps/sec',
  p.ms, perStep.toFixed(3), Math.round(1000 / perStep));
console.log('   a 60fps frame budget of 16.7ms allows ~%d steps/frame', Math.floor(16.7 / perStep));

const ok = monotone && spread > 0.001 && differs && perStep < 8;
console.log('\n%s', ok ? 'PASS - the slice responds, the wiring matters, and it runs in budget'
  : 'FAIL - see above');
process.exit(ok ? 0 : 1);
