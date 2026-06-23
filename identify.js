/* What Did I Meet? — maps a described encounter to the atlas's reported archetypes. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const clean = (s) => String(s == null ? "" : s).replace(/&amp;/g, "&").replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&#39;/g, "'").replace(/&quot;/g, '"');
  const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Question model. value tokens are matched against each entity's trait map.
  const QUESTIONS = [
    { key: "look", q: "What did it look like?", w: 3, opts: [
      ["elf", "Small, frantic, shape-shifting — elf- or imp-like"],
      ["insect", "A tall insect — a praying-mantis form"],
      ["reptile", "A reptile, lizard, or a great serpent"],
      ["feminine", "A feminine, motherly presence"],
      ["deity", "A vast, god-like / divine presence"],
      ["grey", "A 'grey' or classic alien"],
      ["clown", "A clown, jester, or harlequin"],
      ["deceased", "Someone who has died"],
      ["machine", "Living geometry, a machine, or a being of light"],
      ["formless", "No real form — a presence, a voice, or pure void"],
    ]},
    { key: "feel", q: "How did it feel toward you?", w: 2, opts: [
      ["loving", "Loving, warm, nurturing"],
      ["clinical", "Clinical, examining, detached"],
      ["playful", "Playful, mischievous"],
      ["menacing", "Menacing or frightening"],
      ["indifferent", "Impersonal, indifferent"],
      ["sacred", "Authoritative, sacred, vast"],
    ]},
    { key: "did", q: "What did it do?", w: 2, opts: [
      ["telepathy", "Communicated by telepathy / a wordless 'knowing'"],
      ["showed", "Showed me objects or a visible language"],
      ["operated", "Examined or 'operated on' me"],
      ["welcomed", "Welcomed me — seemed to expect me"],
      ["gated", "Tested me, or blocked my way"],
      ["silent", "Just watched, or said nothing"],
    ]},
    { key: "where", q: "Where were you? (optional)", w: 1, opts: [
      ["waiting", "A waiting room / reception"],
      ["cathedral", "A cathedral, temple, or throne room"],
      ["void", "The void, or a white light"],
      ["workshop", "A workshop, factory, or market"],
      ["circus", "A circus or playground"],
      ["any", "Not sure / somewhere else"],
    ]},
  ];

  // Entity name -> matching tokens per question. (Names match atlas.json exactly.)
  const TRAITS = {
    "Self-transforming machine elves": { look: ["elf"], feel: ["playful", "loving"], did: ["showed", "telepathy", "welcomed"], where: ["workshop"] },
    "The Divine Feminine": { look: ["feminine"], feel: ["loving", "sacred"], did: ["telepathy", "welcomed"], where: ["cathedral", "void"] },
    "Deities & god-like presences": { look: ["deity"], feel: ["sacred"], did: ["telepathy"], where: ["cathedral"] },
    "The generic 'Other' — guides, spirits & helpers": { look: ["formless"], feel: ["loving"], did: ["telepathy", "welcomed"], where: ["waiting"] },
    "Alien & 'Grey' forms": { look: ["grey"], feel: ["clinical", "indifferent"], did: ["operated", "telepathy"], where: ["workshop"] },
    "Mantis & insectoid beings": { look: ["insect"], feel: ["clinical"], did: ["operated"], where: ["waiting"] },
    "Reptilian beings": { look: ["reptile"], feel: ["menacing", "indifferent"], did: ["silent", "telepathy"], where: [] },
    "The Jester / Trickster / Clown": { look: ["clown"], feel: ["playful"], did: ["showed"], where: ["circus"] },
    "Guardians & gatekeepers — 'the bouncer'": { look: ["formless"], feel: ["sacred", "menacing"], did: ["gated"], where: ["waiting"] },
    "Impersonal geometric intelligences — 'the machine'": { look: ["machine"], feel: ["indifferent"], did: ["silent"], where: ["workshop"] },
    "Light beings & angels": { look: ["machine"], feel: ["loving", "sacred"], did: ["telepathy"], where: ["cathedral"] },
    "Dark entities & demons": { look: ["formless"], feel: ["menacing"], did: ["silent"], where: ["void"] },
    "Deceased loved ones & ancestors": { look: ["deceased"], feel: ["loving"], did: ["welcomed", "telepathy"], where: ["waiting"] },
    "The Cosmic Serpent": { look: ["reptile"], feel: ["sacred"], did: ["telepathy"], where: ["cathedral"] },
    "The Logos — the Voice": { look: ["formless"], feel: ["sacred"], did: ["telepathy"], where: ["void"] },
  };

  let ATLAS = null;
  const answers = {};

  fetch("data/atlas.json?v=" + Date.now()).then((r) => r.json()).then((d) => { ATLAS = d; renderQuiz(); })
    .catch((e) => { $("#quiz").innerHTML = `<p class="tiny-note">Could not load the atlas data (${esc(e.message)}). Serve this folder over http.</p>`; });

  function renderQuiz() {
    $("#quiz").innerHTML = QUESTIONS.map((Q, qi) => `
      <fieldset class="qblock">
        <legend>${esc(Q.q)}</legend>
        <div class="opts">${Q.opts.map(([v, label]) =>
          `<button type="button" class="opt" data-q="${Q.key}" data-v="${v}">${esc(label)}</button>`).join("")}</div>
      </fieldset>`).join("");
    $("#quiz").querySelectorAll(".opt").forEach((b) => b.addEventListener("click", () => {
      const q = b.dataset.q;
      $("#quiz").querySelectorAll(`.opt[data-q="${q}"]`).forEach((o) => o.classList.remove("sel"));
      b.classList.add("sel"); answers[q] = b.dataset.v;
      // need at least look + feel + did
      const ready = answers.look && answers.feel && answers.did;
      $("#reveal").disabled = !ready;
    }));
    $("#reveal").addEventListener("click", reveal);
    $("#reset").addEventListener("click", () => { location.reload(); });
  }

  function scoreEntities() {
    const out = [];
    (ATLAS.entities || []).forEach((ent) => {
      const t = TRAITS[ent.name]; if (!t) return;
      let score = 0, hits = [];
      QUESTIONS.forEach((Q) => {
        const a = answers[Q.key]; if (!a || a === "any") return;
        if ((t[Q.key] || []).includes(a)) { score += Q.w; hits.push(Q.key); }
      });
      if (score > 0) out.push({ ent, score, hits });
    });
    out.sort((a, b) => b.score - a.score);
    return out;
  }

  function srcLine(ent) {
    const s = (ent.sources || [])[0]; if (!s) return "";
    const src = (ATLAS.sources || []).find((x) => x.key === s.source_key);
    if (!src) return "";
    return `${clean(src.author || src.work)}${src.year ? " (" + src.year + ")" : ""}`;
  }

  function reveal() {
    const ranked = scoreEntities();
    const host = $("#results");
    if (!ranked.length) {
      host.innerHTML = `<p class="tiny-note">No clear match — your encounter may be a rarer or blended form. Explore the full taxonomy in <a href="index.html">the Atlas</a>.</p>`;
      $("#reset").hidden = false; host.scrollIntoView({ behavior: "smooth" }); return;
    }
    const max = ranked[0].score;
    const top = ranked.slice(0, 3);
    host.innerHTML = `
      <h2 class="results-h">What others reported meeting</h2>
      <p class="results-sub">Your closest matches among the documented archetypes${top.length > 1 ? " — many encounters blend more than one" : ""}.</p>
      ${top.map((r, i) => card(r, max, i)).join("")}
      <p class="tiny-note results-foot">This ranks how your description lines up with the most commonly reported archetypes in the literature. It is a mirror of what people report — not a diagnosis, and not a claim these beings exist independently of the experience.</p>`;
    $("#reset").hidden = false;
    host.scrollIntoView({ behavior: "smooth" });
  }

  function card(r, max, i) {
    const e = r.ent;
    const pct = Math.round((r.score / max) * 100);
    const id = "entity:" + slug(e.name);
    const tag = e.type ? e.type.replace(/-/g, " ") : "entity";
    return `<article class="match">
      <div class="match-top">
        <span class="match-rank">${i + 1}</span>
        <div>
          <h3>${esc(clean(e.name))}</h3>
          <span class="match-type">${esc(tag)}</span>
        </div>
        <div class="match-bar" title="match strength"><span style="width:${pct}%"></span></div>
      </div>
      <p class="match-purpose">${esc(clean(e.message_or_purpose || e.appearance || ""))}</p>
      ${e.frequency ? `<p class="match-freq"><strong>How often reported:</strong> ${esc(clean(e.frequency))}</p>` : ""}
      <div class="match-foot">
        ${srcLine(e) ? `<span class="match-src">${esc(srcLine(e))}</span>` : "<span></span>"}
        <a class="match-link" href="index.html#${esc(id)}">Open in the Atlas →</a>
      </div>
    </article>`;
  }
})();
