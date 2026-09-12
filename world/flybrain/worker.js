// The connectome runs here, off the main thread, because a frame that has to wait for 13,104
// neurons is a dropped frame. The page sends distances; this sends back which cited action
// each being is currently performing.
//
// One wiring diagram is parsed once and shared. Each being is a separate Brain over it with
// its own physiology, which is what makes them individuals rather than copies.
'use strict';

let S = null;
let buffer = null;
const beings = new Map();   // id -> { brain, ladder, spec }

function reply(msg) { self.postMessage(msg); }

self.onmessage = function (ev) {
  const msg = ev.data || {};
  try {
    switch (msg.type) {
      case 'init': {
        // sim.js is imported here rather than bundled so there is exactly one copy of the
        // simulation in the repository, shared by the worker, the tests and node.
        self.importScripts(msg.simUrl);
        S = self.FlyBrainSim;
        buffer = msg.buffer;
        const probe = new S.Brain(buffer);
        reply({ type: 'ready', neurons: probe.n, connections: probe.m,
                visual: probe.vpIndex.length, descending: probe.dnIndex.length,
                loom: { k: S.LOOM_K, base: S.LOOM_BASE, max: S.LOOM_MAX } });
        break;
      }
      case 'spawn': {
        if (!S) throw new Error('spawn before init');
        const spec = msg.spec;
        beings.set(msg.id, {
          brain: new S.Brain(buffer, spec.physiology),
          ladder: new S.Ladder(spec.ladder),
          spec: spec
        });
        reply({ type: 'spawned', id: msg.id, entity: spec.entity, rungs: spec.ladder.length });
        break;
      }
      case 'despawn':
        beings.delete(msg.id);
        break;
      case 'tick': {
        // msg.drives: { id: drive }. Steps are budgeted by the caller, not by wall clock, so
        // the simulation advances the same amount per frame on a fast machine and a slow one.
        const steps = msg.steps || 8;
        const out = {};
        for (const [id, b] of beings) {
          const drive = msg.drives[id];
          if (drive == null) continue;
          let rung = null;
          for (let s = 0; s < steps; s++) {
            b.brain.step(drive);
            rung = b.ladder.update(b.brain.readout().descendingRate);
          }
          const r = b.brain.readout();
          out[id] = {
            says: rung ? rung.says : null,
            motion: rung ? rung.motion : null,
            rung: rung ? rung.rung : -1,
            cites: rung ? rung.cites : null,
            entity: b.spec.entity,
            descendingRate: r.descendingRate,
            active: r.descendingActive,
            awake: r.descendingRate > 0.0005,
            reached: b.ladder.reachedCount(),
            of: b.spec.ladder.length
          };
        }
        reply({ type: 'state', t: msg.t, beings: out });
        break;
      }
      default:
        throw new Error('unknown message ' + msg.type);
    }
  } catch (err) {
    reply({ type: 'error', what: msg.type, message: String(err && err.message || err) });
  }
};
