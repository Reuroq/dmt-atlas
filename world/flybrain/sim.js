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
    this.steps = 0;
  }

  // drive: 0..1, how strongly the visual layer is being excited this step. The caller decides
  // what that means physically; this function only knows it as current into the visual sheet.
  Brain.prototype.step = function (drive) {
    const n = this.n, v = this.v, inbox = this.inbox, ref = this.refractory;
    const spiked = this.spiked, rate = this.rate, csr = this.csr;

    // Sensory current. Spread across the visual projection layer with a fixed per-neuron
    // offset so the sheet does not fire as one block - a real optic lobe does not.
    if (drive > 0) {
      const vp = this.vpIndex;
      for (let k = 0; k < vp.length; k++) {
        const i = vp[k];
        inbox[i] += drive * (0.55 + 0.9 * (((i * 2654435761) >>> 8 & 1023) / 1023));
      }
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

  return { Brain: Brain, parse: parse, LAYER: LAYER };
}));
