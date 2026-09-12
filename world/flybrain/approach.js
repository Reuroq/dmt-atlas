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
const buf = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
// This entity's own physiology over the shared wiring - every entity is a different
// individual of one species, not a different animal.
const brain = new S.Brain(buf, behaviour[being].physiology);
const ladder = new S.Ladder(behaviour[being].ladder);

// Looming: the classic approach cue. An object of fixed size subtends an angle that grows as
// 1/distance, and it is the RATE of that growth a visual system reacts to. Anything closer
// than arm's reach is already maximal, so the curve saturates rather than diverging.
const loomingDrive = S.loomingDrive;


console.log('%s  <-  %s', being, behaviour[being].entity);
console.log('every phrase below is verbatim from that entity record (%s)\n',
  behaviour[being].cites);
console.log('  dist   drive   descending   what the being does');
console.log('  ----   -----   ----------   -------------------');

let last = null;
let awake = false;
for (const distance of [16, 14, 12, 11, 10, 9, 8.5, 8, 7.5, 7, 6.5]) {
  const drive = loomingDrive(distance);
  // Let the slice equilibrate at this distance before reading it: the readout is a leaky rate
  // estimate, so sampling mid-transient reports the previous distance.
  let act = null;
  for (let s = 0; s < 160; s++) { brain.step(drive); act = ladder.update(brain.readout().descendingRate); }
  const r = brain.readout();
  if (r.descendingRate > 0.0005) awake = true;
  const shown = awake ? act : null;
  const changed = shown && (!last || shown.says !== last.says);
  console.log('  %s   %s   %s   %s%s',
    String(distance).padStart(4),
    drive.toFixed(3),
    r.descendingRate.toFixed(5).padStart(10),
    shown ? '"' + shown.says + '"' : '(below threshold - still)',
    changed ? '   <- changes here' : '');
  if (shown) last = shown;
}

console.log('');
console.log('%d of %d cited actions were performed walking in from 16 units to 6.5',
  ladder.reachedCount(), behaviour[being].ladder.length);
