// The whole chain, end to end: a traveller walks toward a being and the being responds.
//
//   distance  ->  looming drive  ->  FlyWire slice (LIF)  ->  descending rate  ->  cited action
//   ----------------------------   ------------------------   -------------------------------
//         this file                  sim.js + real wiring        behaviour.json, verbatim atlas
//
// The fly decides WHEN and HOW HARD. The atlas decides WHAT. Nothing in the output is written
// here; every phrase is lifted from the entity's own record and carries its citation.
//
// Run: node approach.js [being]
const fs = require('fs');
const zlib = require('zlib');
const S = require('./sim.js');

const being = process.argv[2] || 'elf';
const behaviour = JSON.parse(fs.readFileSync(__dirname + '/behaviour.json', 'utf8'));
if (!behaviour[being]) {
  console.error('no such being: %s (have %s)', being, Object.keys(behaviour).join(', '));
  process.exit(1);
}
const raw = zlib.gunzipSync(fs.readFileSync(__dirname + '/data/circuit.bin.gz'));
const brain = new S.Brain(raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength));

// Looming: the classic approach cue. An object of fixed size subtends an angle that grows as
// 1/distance, and it is the RATE of that growth a visual system reacts to. Anything closer
// than arm's reach is already maximal, so the curve saturates rather than diverging.
function loomingDrive(distance) {
  const d = Math.max(0.6, distance);
  return Math.min(0.5, 1.6 / (d * d));
}

function actionFor(rate) {
  const ladder = behaviour[being].ladder;
  for (const rung of ladder) {
    if (rate >= rung.descendingRate[0] && rate < rung.descendingRate[1]) return rung;
  }
  return rate < ladder[0].descendingRate[0] ? null : ladder[ladder.length - 1];
}

console.log('%s  <-  %s', being, behaviour[being].entity);
console.log('every phrase below is verbatim from that entity record (%s)\n',
  behaviour[being].cites);
console.log('  dist   drive   descending   what the being does');
console.log('  ----   -----   ----------   -------------------');

let last = null;
for (const distance of [14, 11, 9, 7, 5.5, 4.5, 3.5, 2.8, 2.2, 1.6, 1.1]) {
  const drive = loomingDrive(distance);
  // Let the slice equilibrate at this distance before reading it: the readout is a leaky
  // rate estimate, so sampling it mid-transient would report the previous distance.
  for (let s = 0; s < 120; s++) brain.step(drive);
  const r = brain.readout();
  const act = actionFor(r.descendingRate);
  const changed = act && (!last || act.says !== last.says);
  console.log('  %s   %s   %s   %s%s',
    String(distance).padStart(4),
    drive.toFixed(3),
    r.descendingRate.toFixed(5).padStart(10),
    act ? '"' + act.says + '"' : '(below threshold - still)',
    changed ? '   <- changes here' : '');
  if (act) last = act;
}

const rungsReached = new Set();
for (const distance of [14, 11, 9, 7, 5.5, 4.5, 3.5, 2.8, 2.2, 1.6, 1.1]) {
  for (let s = 0; s < 120; s++) brain.step(loomingDrive(distance));
  const a = actionFor(brain.readout().descendingRate);
  if (a) rungsReached.add(a.says);
}
console.log('\n%d of %d cited actions were reached by walking in from 14 units to arm\'s length',
  rungsReached.size, behaviour[being].ladder.length);
