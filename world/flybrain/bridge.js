// Page-side handle on the connectome. Everything here is opt-in and lazy.
//
// The circuit is 1.7 MB gzipped, roughly three times the walkthrough's entire critical path.
// It must never load because someone opened the page. It loads because someone asked for it,
// and until then this file costs a few hundred bytes and does nothing.
(function () {
  'use strict';

  // Resolve against THIS script's own URL, not the page's. Hard-coding 'flybrain/' worked
  // from world/index.html and asked for flybrain/flybrain/... from the bench inside the
  // directory, which is a 404 that only shows up in whichever context you did not test.
  const SELF = (document.currentScript && document.currentScript.src)
    || new URL('flybrain/bridge.js', location.href).href;
  const DIR = SELF.slice(0, SELF.lastIndexOf('/') + 1);
  let worker = null, ready = false, loading = null, info = null;
  // The looming constant lives in sim.js and is reported by the worker on ready, so the
  // page never carries a second copy that can drift from the calibration.
  let loom = null;
  function driveFn(d) {
    if (!loom) return 0;   // not loaded yet: drive nothing rather than guess
    const x = Math.max(1, d);
    const v = loom.k * (1 / (x * x) - loom.base);
    return v <= 0 ? 0 : Math.min(loom.max, v);
  }
  const listeners = [];
  let latest = {};

  function emit(ev) { listeners.forEach(function (fn) { try { fn(ev); } catch (e) {} }); }

  // Do NOT assume the transport undoes the gzip. dmtatlas.com serves circuit.bin.gz as
  // application/octet-stream with no Content-Encoding, so the browser hands back the raw
  // compressed bytes and the parse fails on a bad magic number. The local test server was
  // setting that header, which made the harness kinder than production and hid the bug until
  // it was live. So: look at the bytes and decide, rather than trusting either server.
  function maybeGunzip(buf) {
    const head = new Uint8Array(buf, 0, Math.min(2, buf.byteLength));
    if (!(head[0] === 0x1f && head[1] === 0x8b)) return Promise.resolve(buf);  // already FLYW
    if (typeof DecompressionStream !== 'function') {
      return Promise.reject(new Error('circuit arrived gzipped and this browser cannot inflate it'));
    }
    return new Response(
      new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'))
    ).arrayBuffer();
  }
  // The cited-behaviour table is 21 KB gzipped - four per cent of the walkthrough's whole
  // critical path, for a feature most visitors will never switch on. So it is fetched with
  // the circuit, not shipped with the page. Only this file (2 KB) is always present.
  function loadBehaviour() {
    if (window.FlyBehaviour) return Promise.resolve(window.FlyBehaviour);
    return new Promise(function (resolve, reject) {
      const s = document.createElement('script');
      s.src = DIR + 'behaviour.js';
      s.onload = function () { resolve(window.FlyBehaviour); };
      s.onerror = function () { reject(new Error('behaviour.js failed to load')); };
      document.head.appendChild(s);
    });
  }

  function load() {
    if (loading) return loading;
    loading = loadBehaviour()
      .then(function () { return fetch(DIR + 'data/circuit.bin.gz'); })
      .then(function (r) {
        if (!r.ok) throw new Error('circuit fetch failed: HTTP ' + r.status);
        return r.arrayBuffer();
      })
      .then(maybeGunzip)
      .then(function (buf) {
        return new Promise(function (resolve, reject) {
          worker = new Worker(DIR + 'worker.js');
          worker.onerror = function (e) { reject(new Error('worker: ' + e.message)); };
          worker.onmessage = function (ev) {
            const m = ev.data;
            if (m.type === 'ready') {
              ready = true;
              info = m;
              loom = m.loom;
              emit({ type: 'ready', info: m });
              resolve(m);
            } else if (m.type === 'state') {
              latest = m.beings;
              emit({ type: 'state', beings: m.beings });
            } else if (m.type === 'error') {
              emit({ type: 'error', message: m.message });
            }
          };
          // The absolute URL matters: importScripts inside the worker resolves against the
          // worker's own location, not the page's.
          const simUrl = new URL(DIR + 'sim.js', location.href).href;
          worker.postMessage({ type: 'init', buffer: buf, simUrl: simUrl }, [buf]);
        });
      });
    return loading;
  }

  window.FlyBrain = {
    available: function () { return typeof Worker === 'function' && typeof fetch === 'function'; },
    loaded: function () { return ready; },
    info: function () { return info; },
    load: load,

    // id is whatever the caller wants to key a being by; spec comes from window.FlyBehaviour.
    spawn: function (id, beingKey) {
      const specs = window.FlyBehaviour || {};
      const spec = specs[beingKey];
      if (!spec) throw new Error('no cited behaviour for ' + beingKey);
      if (!ready) throw new Error('spawn before the circuit finished loading');
      worker.postMessage({ type: 'spawn', id: id, spec: spec });
    },
    despawn: function (id) { if (ready) worker.postMessage({ type: 'despawn', id: id }); },

    // drives: { id: 0..1 }. Called once per frame; the worker answers when it answers, so a
    // slow step never holds up a draw.
    tick: function (drives, steps) {
      if (!ready) return;
      worker.postMessage({ type: 'tick', drives: drives, steps: steps || 8, t: performance.now() });
    },

    // The shared definition, fetched with the circuit, so the page cannot drift from the
    // calibration that set its thresholds.
    drive: function (distance) { return driveFn(distance); },

    state: function () { return latest; },
    on: function (fn) { listeners.push(fn); }
  };
})();
