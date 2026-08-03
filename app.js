/* The DMT Atlas — three lenses over one cited database.
   Constellation (force graph of nodes ↔ the sources that report them),
   Atlas Map (positioned realms), The Journey (the breakthrough arc). */
(() => {
  "use strict";

  const CAT = {
    entity:   { label: "Entity",   color: "#b18cff" },
    realm:    { label: "Realm",    color: "#5ad1c9" },
    geometry: { label: "Geometry", color: "#7aa2ff" },
    theme:    { label: "Theme",    color: "#ff8fb1" },
    phase:    { label: "Phase",    color: "#f3c969" },
    source:   { label: "Source",   color: "#f4a85f" },
  };

  const App = {
    atlas: null, nodes: [], edges: [], byId: {}, srcByKey: {},
    view: "constellation", selected: null, hovered: null,
    cam: { x: 0, y: 0, scale: 1 },
    cv: null, ctx: null, W: 0, H: 0, dpr: 1,
    drag: null, anim: 0,
  };

  window.__atlas = App;
  const $ = (s) => document.querySelector(s);
  const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const esc = (s) => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  // research agents returned some HTML-escaped text; show it clean
  const clean = (s) => String(s == null ? "" : s)
    .replace(/&amp;/g, "&").replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&#39;/g, "'").replace(/&quot;/g, '"');

  /* ---------------- load ---------------- */
  fetch("data/atlas.json?v=" + Date.now())
    .then((r) => r.json())
    .then((data) => { App.atlas = data; boot(); })
    .catch((e) => {
      $("#stage").insertAdjacentHTML("beforeend",
        `<div class="hint" style="position:fixed;top:90px;bottom:auto">Could not load atlas.json — serve this folder over http (e.g. <code>python -m http.server</code>). ${esc(e.message)}</div>`);
    });

  function boot() {
    const m = App.atlas.meta || {};
    $("#charterText").textContent = clean(m.charter || "");
    const cl = $("#charterList");
    if (cl) cl.innerHTML = (m.honesty || []).map((h) => {
      const t = clean(h); const i = t.indexOf(".");
      const lead = (i > 2 && i < 48) ? `<strong>${esc(t.slice(0, i + 1))}</strong>${esc(t.slice(i + 1))}` : esc(t);
      return `<li>${lead}</li>`;
    }).join("");
    buildModel();
    setupCanvas();
    buildLegend();
    wireUI();
    setView("constellation");
    const A = App.atlas;
    $("#introStats").textContent =
      `${A.entities.length} entities · ${A.realms.length} realms · ${A.phases.length} stages · ${A.sources.length} sources`;
    // deep-link from the tool pages (#entity:slug or #about)
    const hash = decodeURIComponent((location.hash || "").replace(/^#/, ""));
    if (hash) {
      const intro = $("#intro"); if (intro) intro.classList.add("gone");
      if (hash === "about") { $("#aboutModal").classList.remove("hidden"); }
      else if (App.byId[hash]) { fitView(App.nodes); selectNode(App.byId[hash]); }
    }
    loop();
  }

  /* ---------------- model ---------------- */
  function addNode(cat, name, data, type) {
    const id = cat + ":" + slug(name);
    if (App.byId[id]) return App.byId[id];
    const n = {
      id, cat, type: type || null, name: clean(name), data,
      x: (Math.random() - 0.5) * 600, y: (Math.random() - 0.5) * 600,
      vx: 0, vy: 0, fx: null, fy: null, deg: 0, r: 6,
      srcKeys: [], mapx: null, mapy: null,
    };
    App.nodes.push(n); App.byId[id] = n; return n;
  }

  function srcKeysOf(item) {
    const out = [];
    (item.sources || []).forEach((s) => { if (s && s.source_key && !out.includes(s.source_key)) out.push(s.source_key); });
    return out;
  }

  function buildModel() {
    const A = App.atlas;
    (A.sources || []).forEach((s) => { App.srcByKey[s.key] = s; });

    // source nodes first (hubs)
    (A.sources || []).forEach((s) => {
      const label = s.author ? s.author.split(",")[0].split("&")[0].trim() : (s.work || s.key);
      const n = addNode("source", s.key, s, s.type);
      n.label = clean(label); n.fullName = clean(s.work || s.author || s.key);
    });

    const addItems = (arr, cat) => (arr || []).forEach((it) => {
      const n = addNode(cat, it.name, it, it.type);
      n.srcKeys = srcKeysOf(it);
      if (cat === "realm") { n.mapx = it.map_x; n.mapy = it.map_y; }
      if (it.phase != null) n.phase = it.phase;
    });
    addItems(A.entities, "entity");
    addItems(A.realms, "realm");
    addItems(A.geometries, "geometry");
    addItems(A.themes, "theme");
    (A.phases || []).forEach((p) => {
      const n = addNode("phase", p.name, p);
      n.srcKeys = srcKeysOf(p); n.order = p.order;
    });

    // edges: every item ↔ each source that reports it
    const seen = new Set();
    App.nodes.forEach((n) => {
      if (n.cat === "source") return;
      n.srcKeys.forEach((k) => {
        const sid = "source:" + slug(k);
        if (!App.byId[sid]) return;
        const key = n.id + "|" + sid;
        if (seen.has(key)) return; seen.add(key);
        App.edges.push({ a: n, b: App.byId[sid] });
        n.deg++; App.byId[sid].deg++;
      });
    });

    // Radius by degree — but the SUBJECT outranks its evidence.
    // Sources had both the larger base (7 vs 5) and far higher degree, so the
    // orange evidence nodes were always the biggest and brightest things on
    // screen and the graph read as a bibliography. The entities, realms,
    // geometry and themes are what the page is about; sources are the
    // connective tissue that proves them.
    App.nodes.forEach((n) => {
      n.r = n.cat === "source"
        ? 3.4 + Math.sqrt(n.deg) * 1.35
        : 6.5 + Math.sqrt(n.deg) * 2.7;
    });
  }

  /* ---------------- canvas / camera ---------------- */
  function setupCanvas() {
    App.cv = $("#canvas"); App.ctx = App.cv.getContext("2d");
    resize(); window.addEventListener("resize", resize);
    const cv = App.cv;
    cv.addEventListener("mousedown", onDown);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    cv.addEventListener("wheel", onWheel, { passive: false });
    // touch (basic)
    cv.addEventListener("touchstart", (e) => { if (e.touches[0]) onDown(toMouse(e.touches[0])); }, { passive: true });
    window.addEventListener("touchmove", (e) => { if (e.touches[0]) onMove(toMouse(e.touches[0])); }, { passive: true });
    window.addEventListener("touchend", () => onUp({}));
  }
  const toMouse = (t) => ({ clientX: t.clientX, clientY: t.clientY, _t: true });

  function resize() {
    App.dpr = Math.min(window.devicePixelRatio || 1, 2);
    App.W = window.innerWidth; App.H = window.innerHeight;
    App.cv.width = App.W * App.dpr; App.cv.height = App.H * App.dpr;
    App.cv.style.width = App.W + "px"; App.cv.style.height = App.H + "px";
    App.ctx.setTransform(App.dpr, 0, 0, App.dpr, 0, 0);
  }
  const s2w = (sx, sy) => ({ x: (sx - App.W / 2) / App.cam.scale + App.cam.x, y: (sy - App.H / 2) / App.cam.scale + App.cam.y });
  const w2s = (wx, wy) => ({ x: (wx - App.cam.x) * App.cam.scale + App.W / 2, y: (wy - App.cam.y) * App.cam.scale + App.H / 2 });

  function fitView(list) {
    const ns = list || visibleNodes();
    if (!ns.length) return;
    // Fit the CORE, not the extremes. A handful of single-citation sources
    // drift far out and, on a true min/max fit, shrank the whole constellation
    // to 45% to accommodate them — the interesting structure ended up a small
    // ball in the middle of an empty frame. Outliers stay reachable by panning.
    const q = (arr, p) => {
      const s = arr.slice().sort((a, b) => a - b);
      return s[Math.min(s.length - 1, Math.max(0, Math.floor(s.length * p)))];
    };
    const xs = ns.map((n) => n.x), ys = ns.map((n) => n.y);
    let minx = q(xs, 0.04), maxx = q(xs, 0.96), miny = q(ys, 0.04), maxy = q(ys, 0.96);
    if (!(maxx > minx)) { minx = Math.min(...xs); maxx = Math.max(...xs); }
    if (!(maxy > miny)) { miny = Math.min(...ys); maxy = Math.max(...ys); }
    // Tighter than it was: the constellation is the centrepiece, and at
    // pad 90 / -120 it sat in the middle of the frame surrounded by dead
    // space instead of filling it.
    const pad = 46;
    const w = Math.max(maxx - minx, 50), h = Math.max(maxy - miny, 50);
    App.cam.x = (minx + maxx) / 2; App.cam.y = (miny + maxy) / 2;
    App.cam.scale = Math.min((App.W - pad * 2) / w, (App.H - 70 - pad) / h, 1.6);
    App.cam.scale = Math.max(App.cam.scale, 0.15);
  }

  /* fitView called at the moment of entry fits the layout as it was BEFORE
     the force sim relaxed, so the camera ends up framing an extent the graph
     no longer has. Re-fit a few times while it settles. */
  function fitViewSettled(list) {
    fitView(list);
    [400, 1100, 2200].forEach((t) => setTimeout(() => fitView(list), t));
  }

  /* ---------------- interaction ---------------- */
  function pickNode(sx, sy) {
    const list = visibleNodes();
    for (let i = list.length - 1; i >= 0; i--) {
      const n = list[i], p = w2s(n.x, n.y);
      const rr = (n.r * App.cam.scale) + 6;
      if ((sx - p.x) ** 2 + (sy - p.y) ** 2 <= rr * rr) return n;
    }
    return null;
  }
  function onDown(e) {
    if (App.view === "journey") return;
    const sx = e.clientX, sy = e.clientY;
    const hit = pickNode(sx, sy);
    App.drag = { sx, sy, lastx: sx, lasty: sy, node: hit, moved: 0 };
    App.cv.classList.add("grabbing");
  }
  function onMove(e) {
    const sx = e.clientX, sy = e.clientY;
    if (!App.drag) {
      if (App.view !== "journey") {
        const h = pickNode(sx, sy);
        App.hovered = h; App.cv.style.cursor = h ? "pointer" : "grab";
      }
      return;
    }
    const dx = sx - App.drag.lastx, dy = sy - App.drag.lasty;
    App.drag.lastx = sx; App.drag.lasty = sy;
    App.drag.moved += Math.abs(dx) + Math.abs(dy);
    if (App.drag.node && App.view === "constellation") {
      const w = s2w(sx, sy); App.drag.node.fx = w.x; App.drag.node.fy = w.y;
      App.drag.node.x = w.x; App.drag.node.y = w.y;
    } else {
      App.cam.x -= dx / App.cam.scale; App.cam.y -= dy / App.cam.scale;
    }
  }
  function onUp() {
    App.cv.classList.remove("grabbing");
    if (App.drag) {
      if (App.drag.node && App.drag.moved < 6) selectNode(App.drag.node);
      if (App.drag.node) { App.drag.node.fx = null; App.drag.node.fy = null; }
    }
    App.drag = null;
  }
  function onWheel(e) {
    e.preventDefault();
    if (App.view === "journey") return;
    const before = s2w(e.clientX, e.clientY);
    const f = Math.exp(-e.deltaY * 0.0014);
    App.cam.scale = Math.max(0.12, Math.min(4, App.cam.scale * f));
    const after = s2w(e.clientX, e.clientY);
    App.cam.x += before.x - after.x; App.cam.y += before.y - after.y;
  }

  /* ---------------- force sim ---------------- */
  function step() {
    if (App.view !== "constellation") return;
    const ns = App.nodes, n = ns.length;
    for (let i = 0; i < n; i++) {
      const a = ns[i];
      for (let j = i + 1; j < n; j++) {
        const b = ns[j];
        let dx = a.x - b.x, dy = a.y - b.y; let d2 = dx * dx + dy * dy;
        if (d2 < 0.01) { d2 = 0.01; dx = Math.random() - 0.5; dy = Math.random() - 0.5; }
        const d = Math.sqrt(d2); const f = 3300 / d2;
        const ux = dx / d, uy = dy / d;
        a.vx += ux * f; a.vy += uy * f; b.vx -= ux * f; b.vy -= uy * f;
      }
    }
    const L = 108;
    App.edges.forEach((e) => {
      let dx = e.b.x - e.a.x, dy = e.b.y - e.a.y; const d = Math.hypot(dx, dy) || 0.01;
      const f = (d - L) * 0.012; const ux = dx / d, uy = dy / d;
      e.a.vx += ux * f; e.a.vy += uy * f; e.b.vx -= ux * f; e.b.vy -= uy * f;
    });
    ns.forEach((a) => {
      a.vx += (0 - a.x) * 0.0016; a.vy += (0 - a.y) * 0.0016;
      a.vx *= 0.84; a.vy *= 0.84;
      if (a.fx == null) { a.x += Math.max(-30, Math.min(30, a.vx)); a.y += Math.max(-30, Math.min(30, a.vy)); }
      else { a.x = a.fx; a.y = a.fy; a.vx = a.vy = 0; }
    });
  }

  /* ---------------- draw ---------------- */
  function visibleNodes() {
    if (App.view === "map") return App.nodes.filter((n) => n.cat === "realm");
    if (App.view === "constellation") return App.nodes;
    return [];
  }
  function loop() {
    App.anim = requestAnimationFrame(loop);
    step();
    const ctx = App.ctx; ctx.clearRect(0, 0, App.W, App.H);
    if (App.view === "constellation") drawConstellation(ctx);
    else if (App.view === "map") drawMap(ctx);
  }

  /* The constellation is drawn in three passes rather than one node-at-a-time
     loop. The old single pass labelled EVERY source unconditionally
     (`nd.cat === "source"` in the showLabel test) — with ~103 sources that
     produced a solid ring of colliding names around an unreadable core, and
     gave a 3-citation source exactly the same visual weight as the most-
     reported entity in the corpus. Passes: edges, then discs, then labels in
     descending importance with collision rejection. */

  function importance(nd) {
    // entities/realms/geometry are the subject; sources are the evidence.
    const kind = nd.cat === "source" ? 0.55 : 1;
    return (nd.deg || 0) * kind;
  }

  function drawConstellation(ctx) {
    const nodes = App.nodes;
    const maxDeg = Math.max(1, ...nodes.map((n) => n.deg || 0));

    // ---- pass 1: edges, brightness carried by the weaker endpoint ----------
    ctx.lineWidth = 1;
    App.edges.forEach((e) => {
      const hot = (App.selected && (e.a === App.selected || e.b === App.selected)) ||
        (App.hovered && (e.a === App.hovered || e.b === App.hovered));
      const a = w2s(e.a.x, e.a.y), b = w2s(e.b.x, e.b.y);
      if (hot) {
        ctx.strokeStyle = "rgba(190,155,255,.62)"; ctx.lineWidth = 1.6;
      } else {
        const w = Math.min(e.a.deg || 0, e.b.deg || 0) / maxDeg;
        ctx.strokeStyle = "rgba(139,126,214," + (0.07 + w * 0.30).toFixed(3) + ")";
        ctx.lineWidth = 0.6 + w * 1.1;
      }
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    });
    ctx.lineWidth = 1;

    // ---- pass 2: discs, least important first so the hubs sit on top -------
    const byImp = nodes.slice().sort((x, y) => importance(x) - importance(y));
    byImp.forEach((nd) => drawDisc(ctx, nd, maxDeg));

    // ---- pass 3: labels, most important first, skipping collisions ---------
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    const placed = [];
    // Narrow viewports get fewer, smaller labels: at phone widths the whole
    // constellation is ~300px across, and 34 labels at a 10px floor buried it.
    const narrow = App.W < 620;
    const budget = App.cam.scale > 1.4 ? 999 : (narrow ? 12 : 34);
    let drawn = 0;
    // The page promises "the shape of the corpus" — entities, realms, geometry
    // and themes ARE the subject; sources are the evidence for it. Sources have
    // far higher degree, so on raw importance they took every label slot and the
    // graph read as a bibliography. Subject nodes get first refusal.
    const subject = byImp.slice().reverse().filter((n) => n.cat !== "source");
    const sources = byImp.slice().reverse().filter((n) => n.cat === "source");
    subject.concat(sources).forEach((nd) => {
      const active = nd === App.selected || nd === App.hovered;
      if (!active && drawn >= budget) return;
      if (placeLabel(ctx, nd, placed, active, maxDeg)) drawn++;
    });
  }

  function drawDisc(ctx, nd, maxDeg) {
    const p = w2s(nd.x, nd.y), r = nd.r * App.cam.scale;
    if (p.x < -60 || p.y < -60 || p.x > App.W + 60 || p.y > App.H + 60) return;
    const col = CAT[nd.cat].color;
    const active = nd === App.selected || nd === App.hovered;
    const rel = (nd.deg || 0) / maxDeg;

    // hubs glow; the long tail recedes, so the eye has somewhere to land
    if (active || (rel > 0.15 && nd.cat !== "source")) {
      ctx.shadowColor = col;
      ctx.shadowBlur = active ? 26 : 8 + rel * 26;
    }
    ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 6.2832);
    ctx.fillStyle = col;
    ctx.globalAlpha = active ? 1 : (nd.cat === "source" ? 0.34 + rel * 0.34 : 0.66 + rel * 0.34);
    ctx.fill();
    ctx.shadowBlur = 0; ctx.globalAlpha = 1;
    if (active) { ctx.lineWidth = 2; ctx.strokeStyle = "#fff"; ctx.stroke(); ctx.lineWidth = 1; }
  }

  function placeLabel(ctx, nd, placed, active, maxDeg) {
    const p = w2s(nd.x, nd.y), r = nd.r * App.cam.scale;
    if (p.x < 0 || p.y < 0 || p.x > App.W || p.y > App.H) return false;
    const rel = (nd.deg || 0) / maxDeg;
    if (!active && rel < 0.06 && App.cam.scale < 1.4) return false;

    const floor = App.W < 620 ? 8.5 : 10;
    const size = Math.max(floor, Math.min(17, (10.5 + rel * 6) * Math.max(0.85, App.cam.scale)));
    const weight = rel > 0.3 ? "600 " : "";
    ctx.font = weight + size.toFixed(1) + "px Inter, sans-serif";
    const label = nd.cat === "source" ? (nd.label || nd.name) : nd.name;
    const w = ctx.measureText(label).width, h = size * 1.15;
    const x0 = p.x - w / 2 - 3, y0 = p.y + r + 3, x1 = p.x + w / 2 + 3, y1 = y0 + h;

    if (!active) {
      for (let i = 0; i < placed.length; i++) {
        const q = placed[i];
        if (x0 < q.x1 && x1 > q.x0 && y0 < q.y1 && y1 > q.y0) return false;
      }
    }
    placed.push({ x0, y0, x1, y1 });

    // a dark plate keeps text legible over the nebula without a hard box
    ctx.fillStyle = "rgba(7,5,20,.55)";
    ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
    ctx.fillStyle = active ? "#fff"
      : (nd.cat === "source" ? "rgba(200,193,240," + (0.55 + rel * 0.4).toFixed(2) + ")"
                             : "rgba(238,234,255," + (0.7 + rel * 0.3).toFixed(2) + ")");
    ctx.fillText(label, p.x, y0 + 1);
    return true;
  }

  function drawMap(ctx) {
    const realms = App.nodes.filter((n) => n.cat === "realm");
    // place realms from map coords into a world rect once
    realms.forEach((n, i) => {
      if (n._placed) return;
      const span = 760;
      if (typeof n.mapx === "number" && typeof n.mapy === "number") {
        n.x = (n.mapx - 0.5) * span; n.y = (n.mapy - 0.5) * span;
      } else {
        const a = (i / realms.length) * 6.2832; n.x = Math.cos(a) * 260; n.y = Math.sin(a) * 220;
      }
      n._placed = true;
    });
    // ambient links between realms (faint constellation of places)
    ctx.lineWidth = 1; ctx.strokeStyle = "rgba(90,209,201,.10)";
    for (let i = 0; i < realms.length; i++) for (let j = i + 1; j < realms.length; j++) {
      const a = w2s(realms[i].x, realms[i].y), b = w2s(realms[j].x, realms[j].y);
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
    realms.forEach((n) => {
      const p = w2s(n.x, n.y);
      const R = (70 + n.deg * 8) * App.cam.scale;
      const active = n === App.selected || n === App.hovered;
      const g = ctx.createRadialGradient(p.x, p.y, 2, p.x, p.y, R);
      g.addColorStop(0, active ? "rgba(122,162,255,.55)" : "rgba(90,209,201,.40)");
      g.addColorStop(1, "rgba(90,209,201,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, R, 0, 6.2832); ctx.fill();
      ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, 6.2832);
      ctx.fillStyle = active ? "#fff" : "#bdeee9"; ctx.fill();
      ctx.font = "600 " + Math.max(12, 15 * Math.max(.85, App.cam.scale)) + "px Inter, sans-serif";
      ctx.fillStyle = active ? "#fff" : "#dffaf6"; ctx.textAlign = "center"; ctx.textBaseline = "top";
      ctx.fillText(n.name, p.x, p.y + 10);
    });
  }

  /* ---------------- journey ---------------- */
  function renderJourney() {
    const A = App.atlas;
    const phases = (A.phases || []).slice().sort((a, b) => a.order - b.order);
    const related = (order) => App.nodes.filter((n) =>
      ["entity", "geometry", "theme"].includes(n.cat) && n.phase === order);
    const intro = `These are the stages people describe, in the order they tend to unfold — though every account differs. Each stage opens into what's reported there. <span class="muted">Tap any tag for its sourced dossier.</span>`;
    let html = `<div class="journey-inner"><p class="journey-intro">${intro}</p>`;
    phases.forEach((p) => {
      const rel = related(p.order);
      const chips = rel.map((n) =>
        `<button class="chip" data-id="${esc(n.id)}"><span class="swatch" style="background:${CAT[n.cat].color}"></span>${esc(n.name)}</button>`).join("");
      const pid = "phase:" + slug(p.name);
      html += `<div class="phase" data-order="${esc(p.order)}">
        <h3>${esc(clean(p.name))}</h3>
        <p>${esc(clean(p.description || ""))}</p>
        ${chips ? `<div class="chiprow">${chips}</div>` : ""}
        <div class="chiprow" style="margin-top:8px"><button class="chip" data-id="${esc(pid)}" style="opacity:.8">▸ phase sources</button></div>
      </div>`;
    });
    html += `</div>`;
    const host = $("#journey"); host.innerHTML = html;
    host.querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => {
      const n = App.byId[c.getAttribute("data-id")]; if (n) selectNode(n);
    }));
  }

  /* ---------------- dossier ---------------- */
  function statsFor(node) {
    const A = App.atlas; const names = [node.name].concat(node.data.aka || []).map((s) => String(s).toLowerCase());
    return (A.data_points || []).filter((dp) => {
      const hay = (clean(dp.claim) + " " + clean(dp.detail || "")).toLowerCase();
      return names.some((nm) => nm.length > 3 && hay.includes(nm));
    });
  }
  function crosslinksFor(node) {
    if (node.cat === "source") {
      return App.nodes.filter((n) => n.cat !== "source" && n.srcKeys.includes(node.name));
    }
    const out = new Set();
    node.srcKeys.forEach((k) => {
      App.nodes.forEach((n) => { if (n !== node && n.cat !== "source" && n.srcKeys.includes(k)) out.add(n); });
    });
    return [...out].slice(0, 14);
  }
  function srcCite(key) {
    const s = App.srcByKey[key]; if (!s) return esc(key);
    return `${esc(clean(s.author || s.work))}${s.work && s.author ? ", <em>" + esc(clean(s.work)) + "</em>" : ""}${s.year ? " (" + esc(s.year) + ")" : ""}`;
  }

  function dossierHTML(node) {
    const d = node.data, cat = node.cat;
    const typeLabel = node.type ? node.type.replace(/-/g, " ") : CAT[cat].label;
    let h = `<span class="d-type" style="background:${CAT[cat].color}22;color:${CAT[cat].color}">${esc(CAT[cat].label)}${node.type ? " · " + esc(typeLabel) : ""}</span>`;
    h += `<h2 class="d-name">${esc(node.cat === "source" ? clean(d.work || d.author) : node.name)}</h2>`;
    const aka = d.aka && d.aka.length ? d.aka.map(clean).join(" · ") : "";
    if (aka) h += `<p class="d-aka">also: ${esc(aka)}</p>`;

    const field = (k, v) => v ? `<div class="d-field"><div class="k">${k}</div><div class="v">${esc(clean(v))}</div></div>` : "";
    if (cat === "entity") {
      h += field("Appearance", d.appearance) + field("Behavior", d.behavior) + field("How it communicates", d.communication) +
        field("Emotional tone", d.emotional_tone) + field("Message / purpose", d.message_or_purpose) + field("How often reported", d.frequency);
    } else if (cat === "realm") {
      h += field("Description", d.description) + field("What happens there", d.what_happens_there);
    } else if (cat === "geometry" || cat === "theme" || cat === "phase") {
      h += field("Description", d.description);
    } else if (cat === "source") {
      h += field("Author", d.author) + field("Work", d.work) + field("Year", d.year) + field("Type", d.type) + field("Note", d.note);
      if (d.url) h += `<div class="d-field"><div class="k">Link</div><div class="v"><a href="${esc(d.url)}" target="_blank" rel="noopener" style="color:var(--accent)">${esc(d.url)}</a></div></div>`;
    }

    // stats
    const stats = statsFor(node);
    if (stats.length) {
      h += `<div class="d-section-h">By the numbers</div>`;
      stats.slice(0, 8).forEach((s) => {
        h += `<div class="quote"><div class="q"><strong>${esc(clean(s.stat_or_value))}</strong> — ${esc(clean(s.claim))}</div><div class="cite">${srcCite(s.source_key)}</div></div>`;
      });
    }

    // quotes / citations
    const qs = d.sources || [];
    if (qs.length) {
      h += `<div class="d-section-h">Reported in</div>`;
      qs.forEach((s) => {
        h += `<div class="quote"><div class="q">${esc(clean(s.detail || ""))}</div><div class="cite">${srcCite(s.source_key)}</div></div>`;
      });
    }

    // crosslinks
    const cl = crosslinksFor(node);
    if (cl.length) {
      h += `<div class="d-section-h">${node.cat === "source" ? "Reports that cite this" : "Connected (shares a source)"}</div><div class="crosslinks">`;
      cl.forEach((n) => { h += `<button class="chip" data-id="${esc(n.id)}"><span class="swatch" style="background:${CAT[n.cat].color}"></span>${esc(n.name)}</button>`; });
      h += `</div>`;
    }
    return h;
  }

  function selectNode(node) {
    App.selected = node;
    $("#dossierBody").innerHTML = dossierHTML(node);
    $("#dossier").classList.remove("closed");
    $("#dossierBody").querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => {
      const n = App.byId[c.getAttribute("data-id")]; if (n) selectNode(n);
    }));
  }
  function closeDossier() { $("#dossier").classList.add("closed"); App.selected = null; }

  /* ---------------- views / ui ---------------- */
  function setView(v) {
    App.view = v;
    $("#tabs").querySelectorAll("button").forEach((b) => b.classList.toggle("active", b.dataset.view === v));
    const journey = $("#journey"), canvas = $("#canvas"), legend = $("#legend"), hint = $("#hint");
    if (v === "journey") {
      journey.classList.remove("hidden"); canvas.classList.add("hidden"); legend.classList.add("hidden");
      hint.textContent = ""; renderJourney();
    } else {
      journey.classList.add("hidden"); canvas.classList.remove("hidden"); legend.classList.remove("hidden");
      if (v === "map") { App.nodes.forEach((n) => n._placed = false); drawMap(App.ctx); fitView(App.nodes.filter((n) => n.cat === "realm")); }
      else fitViewSettled(App.nodes);
      hint.textContent = v === "constellation"
        ? "Drag to pan · scroll to zoom · drag a node · click for its sourced dossier"
        : "The terrain people describe · pan & zoom · click a region to enter it";
    }
  }

  function buildLegend() {
    const order = ["entity", "realm", "geometry", "theme", "phase", "source"];
    $("#legend").innerHTML = order.map((c) =>
      `<div class="row"><span class="dot" style="background:${CAT[c].color}"></span>${CAT[c].label}</div>`).join("");
  }

  function wireUI() {
    const enter = $("#enterBtn"), intro = $("#intro");
    if (enter) enter.addEventListener("click", () => { intro.classList.add("gone"); fitViewSettled(App.nodes); });
    $("#tabs").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) setView(b.dataset.view); });
    $("#dossierClose").addEventListener("click", closeDossier);
    $("#aboutBtn").addEventListener("click", () => $("#aboutModal").classList.remove("hidden"));
    $("#aboutClose").addEventListener("click", () => $("#aboutModal").classList.add("hidden"));
    $("#aboutModal").addEventListener("click", (e) => { if (e.target.id === "aboutModal") $("#aboutModal").classList.add("hidden"); });
    window.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeDossier(); $("#aboutModal").classList.add("hidden"); } });
  }
})();
