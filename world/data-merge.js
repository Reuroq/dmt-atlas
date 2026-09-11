// The evidence atlas IS the report trail, so unlike the walkthrough it needs the full
// bundle. reports+depictions were split out of data.js so /world/ does not download
// 3.35 MB it only reads when a drawer opens; world.js still expects them on WORLD_DATA.
// Must be an external deferred file: `defer` is ignored on inline scripts, which would
// run this before data.js had executed.
Object.assign(window.WORLD_DATA, window.WORLD_REPORTS);
