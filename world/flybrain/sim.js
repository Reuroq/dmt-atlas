// A leaky integrate-and-fire simulation over a real slice of the FlyWire fly connectome.
//
// Source data: FlyWire FAFB v783 (Dorkenwald et al. 2024; Schlegel et al. 2024), CC BY-NC 4.0.
// The slice is a sensorimotor pathway taken by FlyWire's OWN classification: every
// visual_projection neuron, every descending neuron, and the central neurons that both
// receive from the former and project to the latter. 13,104 neurons, 295,075 connections at
// a 5-synapse threshold.
//
// What this is NOT: the export carries no canonical cell-type labels, so this is a pathway at
// the level of FlyWire's super_class annotation and must never be described as a named circuit
// such as the looming-escape pathway. Sign comes from the measured transmitter - acetylcholine
// excitatory, GABA and glutamate inhibitory, which is the usual Drosophila case because
// glutamate gates a chloride channel there.
//
// Runs event-driven: only neurons that actually spiked push charge, so cost tracks activity
// rather than the size of the wiring diagram. That is what makes 295k connections affordable
// next to a WebGL scene.
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.FlyBrainSim = api;
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const LAYER = { VP: 0, CE: 1, DN: 2 };

  function parse(buffer) {
    const dv = new DataView(buffer);
    if (String.fromCharCode(dv.getUint8(0), dv.getUint8(1), dv.getUint8(2), dv.getUint8(3)) !== 'FLYW') {
      throw new Error('not a FLYW circuit file');
    }
    const version = dv.getUint32(4, true);
    const n = dv.getUint32(8, true);
    const m = dv.getUint32(12, true);
    let o = 16;
    const layer = new Uint8Array(n), side = new Uint8Array(n);
    for (let i = 0; i < n; i++) { layer[i] = dv.getUint8(o++); side[i] = dv.getUint8(o++); }
    const pre = new Int32Array(m), post = new Int32Array(m), w = new Float32Array(m);
    for (let e = 0; e < m; e++) {
      pre[e] = dv.getInt32(o, true); o += 4;
      post[e] = dv.getInt32(o, true); o += 4;
      w[e] = dv.getFloat32(o, true); o += 4;
    }
    return { version: version, n: n, m: m, layer: layer, side: side, pre: pre, post: post, w: w };
  }

  // Compressed sparse row, keyed by the PREsynaptic neuron, because propagation is driven by
  // who spiked. Built once; the per-step loop then never touches a neuron that stayed quiet.
  function index(c) {
    const off = new Int32Array(c.n + 1);
    for (let e = 0; e < c.m; e++) off[c.pre[e] + 1]++;
    for (let i = 0; i < c.n; i++) off[i + 1] += off[i];
    const cursor = off.slice(0, c.n);
    const tgt = new Int32Array(c.m), wt = new Float32Array(c.m);
    for (let e = 0; e < c.m; e++) {
      const p = cursor[c.pre[e]]++;
      tgt[p] = c.post[e];
      wt[p] = c.w[e];
    }
    return { off: off, tgt: tgt, wt: wt };
  }

  function Brain(buffer, opts) {
    opts = opts || {};
    const c = parse(buffer);
    const g = index(c);
    const n = c.n;

    this.n = n;
    this.m = c.m;
    this.layer = c.layer;
    this.csr = g;

    this.v = new Float32Array(n);          // membrane potential, arbitrary units
    this.inbox = new Float32Array(n);      // charge arriving this step
    this.refractory = new Uint8Array(n);
    this.spiked = new Uint8Array(n);
    this.rate = new Float32Array(n);       // leaky spike-rate estimate, for readout

    this.leak = opts.leak != null ? opts.leak : 0.88;       // per-step membrane decay
    this.threshold = opts.threshold != null ? opts.threshold : 1.0;
    this.refractorySteps = opts.refractorySteps != null ? opts.refractorySteps : 2;
    this.gain = opts.gain != null ? opts.gain : 0.55;        // synaptic scale
    this.noise = opts.noise != null ? opts.noise : 0.004;    // keeps the slice from going silent
    this.rateDecay = opts.rateDecay != null ? opts.rateDecay : 0.95;

    this.vpIndex = [];
    this.dnIndex = [];
    for (let i = 0; i < n; i++) {
      if (c.layer[i] === LAYER.VP) this.vpIndex.push(i);
      else if (c.layer[i] === LAYER.DN) this.dnIndex.push(i);
    }
    this.vpIndex = Int32Array.from(this.vpIndex);
    this.dnIndex = Int32Array.from(this.dnIndex);

    // Where this individual's sensory drive lands on the visual sheet, and how broadly.
    // All entities share one wiring diagram - there is only one fly connectome, and
    // pretending otherwise would be a lie - so what makes them different individuals is
    // physiology: excitability, leak, noise floor, and this receptive patch.
    this.sensoryPhase = opts.sensoryPhase != null ? opts.sensoryPhase : 0.5;
    this.sensorySpread = opts.sensorySpread != null ? opts.sensorySpread : 0.75;
    this.sensoryWeight = new Float32Array(this.vpIndex.length);
    this.retune();
    this.steps = 0;
  }

  // A stable position in 0..1 for each visual neuron, so a given entity always sees through
  // the same part of the sheet. Hash-derived rather than anatomical: this export carries no
  // retinotopic coordinates, so it must not be described as a visual field position.
  Brain.prototype.retune = function () {
    const vp = this.vpIndex, w = this.sensoryWeight;
    const phase = this.sensoryPhase;
    const sigma = Math.max(0.06, this.sensorySpread * 0.5);
    for (let k = 0; k < vp.length; k++) {
      const u = (((vp[k] * 2654435761) >>> 8) & 1023) / 1023;
      let d = Math.abs(u - phase);
      if (d > 0.5) d = 1 - d;                       // the sheet wraps
      w[k] = Math.exp(-(d * d) / (2 * sigma * sigma));
    }
  };

  // drive: 0..1, how strongly the visual layer is being excited this step. The caller decides
  // what that means physically; this function only knows it as current into the visual sheet.
  Brain.prototype.step = function (drive) {
    const n = this.n, v = this.v, inbox = this.inbox, ref = this.refractory;
    const spiked = this.spiked, rate = this.rate, csr = this.csr;

    // Sensory current, landing on this individual's receptive patch rather than on the whole
    // sheet at once - a real optic lobe does not fire as one block.
    if (drive > 0) {
      const vp = this.vpIndex, sw = this.sensoryWeight;
      for (let k = 0; k < vp.length; k++) inbox[vp[k]] += drive * sw[k];
    }

    let fired = 0;
    for (let i = 0; i < n; i++) {
      spiked[i] = 0;
      if (ref[i]) { ref[i]--; v[i] = 0; inbox[i] = 0; continue; }
      v[i] = v[i] * this.leak + inbox[i] + (this.noise > 0 ? (Math.random() - 0.5) * this.noise : 0);
      inbox[i] = 0;
      if (v[i] >= this.threshold) {
        spiked[i] = 1;
        v[i] = 0;
        ref[i] = this.refractorySteps;
        fired++;
      }
      rate[i] *= this.rateDecay;
    }

    // Event-driven propagation: only what fired pushes charge.
    const off = csr.off, tgt = csr.tgt, wt = csr.wt, gain = this.gain;
    for (let i = 0; i < n; i++) {
      if (!spiked[i]) continue;
      rate[i] += 1 - this.rateDecay;
      for (let e = off[i]; e < off[i + 1]; e++) inbox[tgt[e]] += wt[e] * gain;
    }
    this.steps++;
    return fired;
  };

  // The motor readout: how hard the descending population is driving right now, and how
  // asymmetric it is left-to-right. Those are the two things a body can actually act on.
  Brain.prototype.readout = function () {
    const dn = this.dnIndex, rate = this.rate;
    let sum = 0, left = 0, right = 0, active = 0;
    for (let k = 0; k < dn.length; k++) {
      const r = rate[dn[k]];
      sum += r;
      if (r > 0.02) active++;
      if (k % 2) right += r; else left += r;
    }
    const mean = dn.length ? sum / dn.length : 0;
    const total = left + right;
    return {
      descendingRate: mean,
      descendingActive: active,
      descendingFraction: dn.length ? active / dn.length : 0,
      asymmetry: total > 1e-6 ? (right - left) / total : 0,
      steps: this.steps
    };
  };

  Brain.prototype.settle = function (steps, drive) {
    let fired = 0;
    for (let s = 0; s < steps; s++) fired += this.step(drive);
    return fired;
  };

  // Selecting a rung by which rate-band you happen to land in loses actions: the descending
  // response saturates on approach, so adjacent thresholds collapse together and a walk steps
  // straight over the rungs between them. 23 of 40 entities lost cited actions that way.
  //
  // The cited text does not read as a set of bands, it reads as an escalation - "greet, crowd
  // forward, leap in and out, sing, urge". So the ladder is a ratchet: rising drive advances
  // it, it will not skip a rung, and each action is held briefly before the next can start.
  // Falling drive lets it settle back down, but only after sustained quiet, so a being does
  // not flicker between two actions at a threshold.
  function Ladder(rungs, opts) {
    opts = opts || {};
    this.rungs = rungs;
    this.at = 0;
    this.dwell = 0;
    this.quiet = 0;
    this.minDwell = opts.minDwell != null ? opts.minDwell : 25;
    this.releaseAfter = opts.releaseAfter != null ? opts.releaseAfter : 60;
    this.reached = { 0: true };
  }

  Ladder.prototype.update = function (rate) {
    this.dwell++;
    const next = this.rungs[this.at + 1];
    if (next && rate >= next.descendingRate[0] && this.dwell >= this.minDwell) {
      this.at++;
      this.dwell = 0;
      this.quiet = 0;
      this.reached[this.at] = true;
    } else if (rate < this.rungs[this.at].descendingRate[0] * 0.7) {
      if (++this.quiet >= this.releaseAfter) {
        if (this.at > 0) this.at--;
        this.quiet = 0;
        this.dwell = 0;
      }
    } else {
      this.quiet = 0;
    }
    return this.rungs[this.at];
  };

  Ladder.prototype.reachedCount = function () {
    return Object.keys(this.reached).length;
  };

  // Looming: an object of fixed size subtends an angle growing as 1/distance, and it is the
  // rate of that growth a visual system reacts to. Saturates rather than diverging.
  //
  // K is set from the world, not from taste. In the walkthrough a traveller meets the beings
  // at roughly 15 units and can close to about 6.5; the first K here was tuned on a bench
  // where the approach ran to arm's length, so in the actual scene NOTHING ever woke up - the
  // beings were driven, reported, and silent. One definition, used by the page, the
  // calibrator and the tests alike, so those three can never drift apart again.
  // FAR is where a traveller meets the beings in the walkthrough and NEAR is as close as the
  // scene lets them get. That is a span of only about 2.5x in distance, so raw inverse-square
  // covers barely 6x in drive - which left two entities unable to wake at all and thirteen
  // unable to finish their repertoire. The curve keeps the inverse-square SHAPE but is
  // referenced to that span: nothing at FAR, full drive at NEAR. Choosing the scale is the
  // same as choosing how large the being is, which in a procedural scene is arbitrary anyway.
  const LOOM_FAR = 16.0, LOOM_NEAR = 6.5, LOOM_MAX = 0.5;
  const LOOM_BASE = 1 / (LOOM_FAR * LOOM_FAR);
  const LOOM_K = LOOM_MAX / (1 / (LOOM_NEAR * LOOM_NEAR) - LOOM_BASE);
  function loomingDrive(distance) {
    const d = Math.max(1.0, distance);
    const v = LOOM_K * (1 / (d * d) - LOOM_BASE);
    return v <= 0 ? 0 : Math.min(LOOM_MAX, v);
  }

  return { Brain: Brain, Ladder: Ladder, parse: parse, LAYER: LAYER,
           loomingDrive: loomingDrive, LOOM_K: LOOM_K,
           LOOM_FAR: LOOM_FAR, LOOM_NEAR: LOOM_NEAR, LOOM_MAX: LOOM_MAX, LOOM_BASE: LOOM_BASE };
}));
