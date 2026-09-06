'use strict';
(() => {
  const bits = values => Array.from(new Uint32Array(new Float32Array(values).buffer));
  function inspect(mode, payload) {
    let values;
    if (mode === 'float') values = payload;
    else if (mode === 'bits') {
      if (!payload.every(x => Number.isInteger(x) && x >= 0 && x <= 0xffffffff)) throw Error('invalid uint32');
      values = Array.from(new Float32Array(new Uint32Array(payload).buffer));
    } else if (mode === 'json') values = JSON.parse(payload);
    else if (mode === 'local') values = [0, -0, 1, -1];
    else throw Error('unknown transport');
    return {ingressBits: bits(values), cpuBits: bits(new Float32Array(values)),
      negativeZeroIndices: values.flatMap((x, i) => Object.is(x, -0) ? [i] : []),
      jsonRoundtripBits: bits(JSON.parse(JSON.stringify(values)))};
  }
  function cleanup(entries, renderer, primaryFailure = null) {
    const registered = entries.map(x => x.id), attempted = [], succeeded = [], errors = [];
    if (new Set(registered).size !== registered.length) throw Error('duplicate registration');
    for (const entry of entries) {
      attempted.push(entry.id);
      try { entry.resource.dispose(); succeeded.push(entry.id); }
      catch (e) { errors.push({id: entry.id, error: String(e)}); }
    }
    let rendererAttempted = false, rendererDisposed = false;
    if (renderer) {
      rendererAttempted = true;
      try { renderer.dispose(); rendererDisposed = true; }
      catch (e) { errors.push({id: 'renderer', error: String(e)}); }
    }
    return {registered, attempted, succeeded, errors, rendererAttempted, rendererDisposed,
      primaryFailure, complete: errors.length === 0 && succeeded.length === registered.length && (!renderer || rendererDisposed)};
  }
  globalThis.transportProbe = {inspect, cleanup};
})();
