// The only path from a room spec to a scene.
//
// A room is data. This turns that data into geometry by calling primitives that already ship
// in fractal.js, and nothing else: no spec can introduce a shader, a texture or a material
// the engine did not already have. That is the point. A bounded grammar is what makes a model
// able to author rooms reliably, and what makes a bad room a validation error rather than a
// runtime one.
//
// Arities come from window.RoomPrimitives, generated from fractal.js itself, because the
// primitives do not share a signature: most take (root, materials, motions, opts), panel and
// cabinet take (root, materials, opts), and language takes (root, materials, motions).
(function () {
  'use strict';

  function callPrimitive(name, F, root, materials, motions, options) {
    const grammar = window.RoomPrimitives || {};
    const meta = grammar[name];
    const fn = F[name];
    if (typeof fn !== 'function') throw new Error('room engine: no primitive ' + name);
    if (!meta) throw new Error('room engine: ' + name + ' is not in the generated grammar');
    // A primitive with no declared options takes no options object - passing one would land
    // in a positional slot it does not have.
    if (!meta.options.length) return fn(root, materials, motions);
    return meta.takes_motions
      ? fn(root, materials, motions, options)
      : fn(root, materials, options);
  }

  // Returns the evidence keys the room is built from, so the page can stamp provenance the
  // same way a hand-written stage does. Every key here was checked against atlas.json before
  // rooms.js was written, so a room cannot cite something that does not exist.
  function build(spec, F, root, materials, motions) {
    if (!spec) throw new Error('room engine: no spec');
    const built = [];
    spec.elements.forEach(function (el, i) {
      try {
        callPrimitive(el.primitive, F, root, materials, motions, el.options || {});
        built.push(el.primitive);
      } catch (err) {
        // Name the element, not just the error: a spec author needs to know WHICH line failed.
        throw new Error('room ' + spec.id + ' element ' + i + ' (' + el.primitive + '): '
          + err.message);
      }
    });
    const evidence = spec.evidence && spec.evidence.length
      ? spec.evidence.slice()
      : Array.from(new Set(spec.elements.map(function (e) { return e.cites; })));
    // Per-element provenance, so a drawable can answer which cited source put it there rather
    // than inheriting the whole room's bundle.
    root.traverse(function (o) {
      if ((o.isMesh || o.isPoints || o.isLine) && !o.userData.evidence) {
        o.userData.evidence = evidence;
      }
    });
    return { evidence: evidence, built: built };
  }

  function stage(spec) {
    // The shape trip.js's route table expects, produced from the spec rather than hand-written.
    return {
      id: spec.id,
      name: spec.name,
      hint: spec.hint,
      duration: spec.duration,
      evidence: spec.evidence.slice(),
      fromSpec: true
    };
  }

  window.RoomEngine = {
    build: build,
    stage: stage,
    specs: function () { return window.RoomSpecs || {}; },
    ids: function () { return Object.keys(window.RoomSpecs || {}); }
  };
})();
