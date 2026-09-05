/* Procedural interpretive architecture. No witness imagery is simulated or fetched. */
'use strict';
(() => {
const $ = id => document.getElementById(id);
const D = window.WORLD_DATA;
if (!D) { $('notice').hidden = false; $('notice').textContent = 'The evidence bundle did not load. Reload with world/data.js present.'; return; }
const nodes = new Map(D.nodes.map(n => [n.key, n]));
const sources = new Map(D.sources.map(s => [s.key, s]));
const key = (kind, name) => `${kind}|${name}`;
const R = name => key('realm', name), G = name => key('geometry', name), E = name => key('entity', name), M = name => key('motif', name);
const rooms = [
 {title:'The Threshold',short:'Threshold',realm:R('The Waiting Room'),subtitle:'A place between arrival and elsewhere.',color:0x79cfc5,fog:0x071b22,style:'threshold',exhibits:[G('The Chrysanthemum'),G('The Aperture / Iris Opening'),R('The Membrane / Veil'),key('phase','Arrival — The Waiting Room')]},
 {title:'The Domed Cathedral',short:'Cathedral',realm:R('The Domed Cathedral'),subtitle:'Vaulted scale. Jeweled surfaces. A sense of impossible architecture.',color:0xe6c780,fog:0x071820,style:'cathedral',exhibits:[G('Fractal lattices & jeweled tilings'),G('Hyper-dimensional objects'),G('Mandalas & symmetry fields'),R('Geometric Palaces & the Lattice')]},
 {title:'The Workshop',short:'Workshop',realm:R('The Workshop / Factory / Market'),subtitle:'An architecture of making, where language becomes an object.',color:0xe8a36d,fog:0x1d1219,style:'workshop',exhibits:[E('Self-transforming machine elves'),G('Living language / visible sound'),E("Impersonal geometric intelligences — 'the machine'"),M("The Presentation — 'the show'")]},
 {title:'The Garden',short:'Garden',realm:R('The Garden'),subtitle:'Luminous growth, mercurial structures, an engineered nature.',color:0xb6d797,fog:0x091d1c,style:'garden',exhibits:[E('Plant spirits & devas'),G('Breathing & Liquid Surfaces'),E('The Divine Feminine'),M('The Love-Flood — the healing touch')]},
 {title:'The Operating Theater',short:'Operating room',realm:R('The Hospital / Operating Theater'),subtitle:'An ambiguous encounter with care, instruments and scrutiny.',color:0x9ccfe7,fog:0x12232f,style:'theater',exhibits:[E('The Surgeons — hyperspace medical team'),E('Mantis & insectoid beings'),M('The Examination — being scanned'),R('The Testing Laboratory')]},
 {title:'The Living Library',short:'Library',realm:R('The Library / Hall of Records'),subtitle:'Receding shelves. Unreadable script. Knowledge that feels complete.',color:0xd3ae6d,fog:0x181611,style:'library',exhibits:[G('Alien Glyphs & Unreadable Writing Systems'),M('The Download — compressed information transfer'),E('The Teacher — professor of hyperspace'),M('Losing the Message — the amnesia on return')]},
 {title:'The Void',short:'Void',realm:R('The Void'),subtitle:'The inverse of ornament: a reported absence of content.',color:0xd6d6e0,fog:0x080b17,style:'void',exhibits:[E('The Silent Witness — felt presence without form'),G('Body Dissolution & Merging with the Geometry'),key('phase','The Return'),key('phase','Afterglow / Integration')]},
 {title:'The Observatory',short:'Observatory',realm:R('Hyperspace'),subtitle:'Step outside the interpretation. See the shape of the evidence.',color:0x88bed1,fog:0x081322,style:'observatory',exhibits:[R('The Grid Plain'),G('Dimensional Layering & Space-Folding'),key('theme','More real than real'),R('The Uncanny Interior')]}
];
let current = 1, entered = false, reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
let tour = -1, panelReturnFocus = null, lastSelection = null, activePointer = null;
const route = [0,1,2,3,4,5,6,7];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = n => Number(n).toLocaleString('en-US');
const validURL = url => { try { const u = new URL(url); return ['https:','http:'].includes(u.protocol) ? esc(u.href) : ''; } catch { return ''; } };
const link = (url, label, cls='') => validURL(url) ? `<a class="${cls}" href="${validURL(url)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>` : `<span class="${cls}">${label}</span>`;
const reportURL = id => `https://www.reddit.com/r/${D.reports[id]?.sub || 'DMT'}/comments/${encodeURIComponent(id)}/`;
function notify(message) { $('notice').textContent = message; $('notice').hidden = false; clearTimeout(notify.timer); notify.timer = setTimeout(() => $('notice').hidden = true, 4500); }
function openPanel(label, html) {
 if ($('panel').hidden) panelReturnFocus = document.activeElement;
 clearMovement(); $('panel').hidden = false; document.body.classList.add('panel-open');
 $('panelLabel').textContent = label; $('panelContent').innerHTML = html; $('panelContent').scrollTop = 0;
 $('closePanel').focus({preventScroll:true});
}
function closePanel() { $('panel').hidden = true; document.body.classList.remove('panel-open'); panelReturnFocus?.focus?.({preventScroll:true}); }
$('closePanel').onclick = closePanel;
function renderIndex() {
 openPanel('THE COMPLETE COLLECTION', `<span class="tag">${D.nodes.length} cited entries</span><h2>A field guide<br>to the reported.</h2><p>Browse every realm, being, pattern, motif, phase and theme. The eight spaces are a curated entry point, not the full vocabulary.</p><div class="search"><input id="search" type="search" aria-label="Search the atlas" placeholder="Search names, aliases, descriptions…"><select id="kindFilter" aria-label="Filter by category"><option value="">All kinds</option>${['realm','entity','geometry','motif','phase','theme'].map(k => `<option>${k}</option>`).join('')}</select></div><div id="indexCount" class="index-count" aria-live="polite"></div><div id="indexResults"></div>`);
 const update = () => {
  const q = $('search').value.trim().toLowerCase(), kind = $('kindFilter').value;
  const filtered = D.nodes.filter(n => (!kind || n.kind === kind) && [n.name,...(n.aka || []),n.description || n.appearance || ''].join(' ').toLowerCase().includes(q));
  $('indexCount').textContent = `${filtered.length} entries · untagged does not mean unreported`;
  $('indexResults').innerHTML = filtered.length ? filtered.map((n,i) => `<button class="index-item" data-node="${esc(n.key)}"><span class="number">${String(i+1).padStart(2,'0')}</span><span><strong>${esc(n.name)}</strong><small>${n.kind.toUpperCase()} · ${n.report_count == null ? 'outside tagged vocabulary' : fmt(n.report_count)+' tagged reports'}</small></span><span class="arrow">↗</span></button>`).join('') : '<p>No matches. Try a shorter name or another category.</p>';
 };
 $('search').oninput = update; $('kindFilter').onchange = update; update(); $('search').focus();
}
function sourceHTML(ref) {
 const s = sources.get(ref.source_key);
 if (!s) return `<div class="source">Unresolved source key: ${esc(ref.source_key)}<p>${esc(ref.detail)}</p></div>`;
 return `<details class="source"><summary>${esc(s.author)} <small> · ${esc(s.year)} · ${esc(s.type)}</small></summary><p>${esc(s.work)}</p><p>${esc(ref.detail)}</p>${s.note ? `<p>${esc(s.note)}</p>` : ''}${s.url ? link(s.url,'Open source') : '<small>No direct URL supplied in the atlas. Bibliographic citation above.</small>'}</details>`;
}
function renderNode(nodeKey, changeHash=true) {
 const n = nodes.get(nodeKey); if (!n) return;
 lastSelection = nodeKey;
 if (changeHash) history.replaceState(null,'',`#node=${encodeURIComponent(nodeKey)}`);
 const housed = rooms.findIndex(r => r.realm === nodeKey || r.exhibits.includes(nodeKey));
 const descriptions = ['description','appearance','behavior','communication','emotional_tone','message_or_purpose','what_happens_there','interpretations','frequency','frequency_note'];
 const labels = {appearance:'Reported appearance',behavior:'Reported interaction',communication:'Communication',emotional_tone:'Emotional tone',message_or_purpose:'Reported meaning',what_happens_there:'What is reported here',interpretations:'Interpretations',frequency:'Study context',frequency_note:'Study context'};
 const refs = n.sources || [];
 const matchedReports = n.report_ids || [];
 const pct = n.report_count == null ? null : (100 * n.report_count / D.n_reports).toFixed(2);
 const art = (n.depiction_ids || []).map(id => D.depictions[id]).filter(Boolean);
 const co = D.cooccurrence.filter(e => e.a.join('|') === nodeKey || e.b.join('|') === nodeKey).slice(0,5);
 const trans = D.transitions.filter(e => e.from.join('|') === nodeKey).slice(0,5);
 openPanel('EVIDENCE / '+n.kind.toUpperCase(), `<button class="back-link" data-action="index">← All entries</button><br><span class="tag">${n.kind}</span><span class="tag">${refs.length} citation records</span><h2>${esc(n.name)}</h2>${n.aka?.length ? `<p style="font-size:11px">Also described as ${n.aka.map(esc).join(' · ')}</p>` : ''}<div class="evidence-note">The scene is a procedural interpretation of cited descriptions, not a witness image or a literal reconstruction. Layout, scale, palette and exhibit positions are design choices.</div>${housed >= 0 ? `<button class="action-button" data-room="${housed}">Walk in ${esc(rooms[housed].short)} ↗</button>` : '<p style="font-size:11px">An index entry; no dedicated 3D reconstruction.</p>'}${descriptions.filter(f => n[f]).map(f => `${labels[f] ? `<h3>${labels[f]}</h3>` : ''}<p>${esc(n[f])}</p>`).join('')}<h3>Corpus mentions</h3>${pct !== null ? `<div class="stats-row"><span><strong>${fmt(n.report_count)}</strong>TAGGED REPORTS</span><span><strong>${pct}%</strong>OF ${fmt(D.n_reports)} REPORTS</span></div><p style="font-size:11px">Automated vocabulary matches in this archive, not population prevalence or a clinical study. A mention can be negated, metaphorical or about ordinary surroundings. Tags need human review.</p>` : '<p>This entry is outside the 128-node tagged vocabulary. No corpus frequency is available; this is not a count of zero.</p>'}<h3>Published & community sources</h3>${refs.map(sourceHTML).join('')}<h3>Tagged report trail</h3><p style="font-size:11px">Only tags, dates and mention order are stored locally. Open the original to check context; posts may be unavailable.</p><div id="reportList"></div>${matchedReports.length > 8 ? '<button class="action-button" id="moreReports">Show more reports</button>' : ''}<h3>Human-made depictions</h3><p style="font-size:11px">Candidate links from the depiction index, not verified representations of this entry. Credit stays with the original creator. No community images are downloaded.</p>${art.length ? art.slice(0,8).map(a => link(a.permalink,`<strong>${esc(a.title)}</strong><small>u/${esc(a.author || '[unknown]')} · ${esc(a.kind)} · ${fmt(a.score || 0)} score in archive</small>`,'art-link')).join('') : '<p>No associated depiction links in this index.</p>'}<h3>Mention-order connections</h3><p style="font-size:11px">Counts are adjacent tag events in narrative text, not verified travel between realms. A report can contribute multiple events.</p>${trans.length ? trans.map(e => pairHTML(nodeKey,e.to.join('|'),e.n,'adjacent mentions')).join('') : '<p>No outgoing mention-order matches.</p>'}<h3>Appearing in the same reports</h3><p style="font-size:11px">From the 400 stored co-occurrence pairs. Shared mention does not establish an encounter or causal relationship.</p>${co.length ? co.map(e => pairHTML(nodeKey,e.a.join('|')===nodeKey?e.b.join('|'):e.a.join('|'),e.n,'co-occurrences',true)).join('') : '<p>No pair in the stored co-occurrence shortlist.</p>'}`);
 let shown = 0;
 function addReports() {
  const ids = matchedReports.slice(shown, shown+8); shown += ids.length;
  if (!matchedReports.length) { $('reportList').innerHTML = '<p>No matching report records in the tagged archive.</p>'; return; }
  $('reportList').insertAdjacentHTML('beforeend',ids.map(id => {
   const r = D.reports[id]; return `<div class="report-link">${link(reportURL(id),`${esc(id)} · r/${esc(r.sub)} · ${new Date(r.date*1000).toISOString().slice(0,10)}`)}<small>${r.seq.map(k => esc(k.split('|').slice(1).join('|'))).join(' → ')}</small></div>`;
  }).join(''));
  if ($('moreReports')) { $('moreReports').hidden = shown >= matchedReports.length; $('moreReports').textContent = `Show more reports (${shown} / ${matchedReports.length})`; }
 }
 addReports(); if ($('moreReports')) $('moreReports').onclick = addReports;
}
function pairHTML(a,b,n,unit,co=false) {
 const matches = (nodes.get(a)?.report_ids || []).filter(id => {
  const seq = D.reports[id].seq;
  return co ? seq.includes(b) : seq.some((k,i) => k === a && seq[i+1] === b);
 }).slice(0,3);
 return `<div class="pair"><button data-node="${esc(b)}">${esc(b.split('|').slice(1).join('|'))} ↗</button><small>${fmt(n)} ${unit}</small>${matches.map(id => link(reportURL(id),id)).join('')}${!matches.length?'<small>No example resolved from local records.</small>':''}</div>`;
}
function methodPanel() {
 const sat = D.saturation, firstFull = sat.curve.find(p => p[1] === sat.nodes_seen);
 const curve = sat.curve.map((p,i) => `${i?'L':'M'}${(35+p[0]/sat.n_reports*325).toFixed(1)},${(135-p[1]/sat.vocab_nodes*108).toFixed(1)}`).join(' ');
 openPanel('HOW TO READ THIS WORLD', `<span class="tag">A source-grounded interpretation</span><h2>Reports, not<br>metaphysics.</h2><p>${esc(D.meta.charter)}</p><h3>What the architecture means</h3><p>Eight spaces translate selected descriptions into walkable sculptures and architecture. Decorative lighting, material, scale, room order and positions are editorial choices, not measured features of an external place. Every room has a “Read this space” dossier; every glowing exhibit opens its own evidence.</p><p>Other entries remain fully browsable in the index. Abstract beings are symbols, not claimed likenesses. No generated or community witness imagery appears in the 3D scenes.</p><h3>Three different kinds of evidence</h3><p><b>Atlas citations:</b> ${D.sources.length} bibliographic sources spanning studies, clinical narratives, comparative scholarship and community accounts. Their populations and standards differ. Cross-substance parallels are not direct evidence about N,N-DMT.</p><p><b>Corpus tags:</b> ${fmt(D.n_reports)} report records matched against a fixed 128-node vocabulary. Counts describe this archive only. Keyword tags can miss synonyms or match negations and ordinary settings.</p><p><b>Depiction candidates:</b> ${fmt(D.depiction_total)} indexed community posts. Links preserve author credit. Association is a tag, not endorsement or validation.</p><h3>Reading the Observatory</h3><p>The 128 points represent the fixed tagged vocabulary. Point radius uses a minimum size plus square-root scaling of report count. Positions follow an arbitrary golden-angle sphere, not measured similarity or geography. The 80 lines are the strongest stored co-occurrence pairs, not travel paths. Click a point for its evidence.</p><h3>Discovery, with a boundary</h3><svg class="curve" viewBox="0 0 390 170" role="img" aria-label="The fixed 128-node vocabulary reaches full coverage by report ${firstFull?.[0]}"><path class="axis" d="M35 20V135H365"/><path d="${curve}"/><text x="5" y="30">128</text><text x="19" y="139">0</text><text x="35" y="158">0 reports</text><text x="306" y="158">14,309</text></svg><p>All ${sat.nodes_seen} predefined tags were observed by report ${fmt(firstFull?.[0])}. This is saturation of a fixed vocabulary, <em>not</em> evidence that every possible experience or place has been discovered.</p><h3>At the edge of the vocabulary</h3><p>A separate phrase scan covered ${fmt(D.discovery.reports_scanned)} records. These are candidates for review, not new confirmed realms; “living room” might refer to someone's actual room. Its legacy “head_in_atlas” flag can be stale: the atlas now includes some of these places.</p>${D.discovery.candidates.slice(0,10).map(c => `<div class="pair"><span>${esc(c.phrase)}</span><small>${c.reports} phrase-matched reports</small>${c.examples.slice(0,3).map(id => link(reportURL(id),id)).join('')}</div>`).join('')}<h3>Navigation</h3><p>WASD or arrow keys move; drag the scene to look. Hold Shift to move faster. Click a glowing exhibit or press E to inspect the one in the crosshair. Press I for the index, H to return to this room's entrance, and Escape to close a panel. On touch screens use the arrow pad and drag to look. The room bar and curated route need no movement controls.</p><button class="action-button" data-action="motion">${reduced?'Resume':'Pause'} ambient motion</button><h3>Curated route ≠ reported sequence</h3><p>The guided route is a museum itinerary. Corpus connections show adjacent mentions in written narratives; they do not establish event chronology, probabilities, or a universal journey.</p><h3>Research files</h3>${['atlas.json','corpus/transitions.json','corpus/summary.json','corpus/saturation.json','corpus/discovery.json','corpus/depictions.json','corpus/reports.jsonl'].map(f => `<div class="source"><a href="../data/${f}" target="_blank" rel="noopener">${f} ↗</a></div>`).join('')}<p style="font-size:11px">The browser evidence bundle is built from these files by world/build_data.py. Input hashes are recorded in <a href="manifest.json" target="_blank">manifest.json</a>. Three.js © its authors, <a href="vendor/THREE-LICENSE.txt" target="_blank">MIT license</a>.</p>`);
}
$('panelContent').onclick = ev => {
 const target = ev.target.closest('[data-node],[data-room],[data-action]'); if (!target) return;
 if (target.dataset.node) renderNode(target.dataset.node);
 else if (target.dataset.room) { closePanel(); enter(); setRoom(Number(target.dataset.room)); }
 else if (target.dataset.action === 'index') renderIndex();
 else if (target.dataset.action === 'motion') { toggleMotion(); methodPanel(); }
};
$('atlasButton').onclick = renderIndex; $('methodButton').onclick = methodPanel;
function toggleMotion() { reduced = !reduced; $('motionButton').textContent = reduced ? 'Resume motion' : 'Pause motion'; $('motionButton').setAttribute('aria-pressed',String(reduced)); }
if (reduced) { $('motionButton').textContent = 'Resume motion'; $('motionButton').setAttribute('aria-pressed','true'); }
$('motionButton').onclick = toggleMotion;

// The visual engine is optional: the complete evidence index works without WebGL.
let renderer, scene, camera, environment, glowTexture, raycaster;
let sceneGeneration=0, renderedGeneration=-1;
let yaw=0, pitch=0, clock=0, lastTime=performance.now(), currentTarget=null, hovered=null;
const keys = new Set(), touchMoves = new Set(), animations=[], pickables=[], obstacles=[];
const T = window.THREE;
function clearMovement() { keys.clear(); touchMoves.clear(); activePointer = null; }
function fallback(message) { $('enterButton').textContent='Explore the evidence →'; $('enterButton').onclick=renderIndex; $('controlsHint').textContent='3D unavailable · the full evidence index is still accessible'; notify(message); }
if (!T) { fallback('The 3D library did not load. The evidence index remains available.'); return; }
try {
 renderer = new T.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.6)); renderer.setSize(innerWidth,innerHeight);
 renderer.outputColorSpace=T.SRGBColorSpace; renderer.toneMapping=T.ACESFilmicToneMapping; renderer.toneMappingExposure=1.25;
 $('world').appendChild(renderer.domElement); renderer.domElement.setAttribute('aria-label','Walkable interpretive architecture. Use WASD or the room navigation.'); renderer.domElement.tabIndex=0;
 scene = new T.Scene(); camera = new T.PerspectiveCamera(60,innerWidth/innerHeight,.08,190); camera.rotation.order='YXZ'; raycaster = new T.Raycaster();
 const c=document.createElement('canvas'); c.width=c.height=128; const ctx=c.getContext('2d'), grad=ctx.createRadialGradient(64,64,0,64,64,64); grad.addColorStop(0,'rgba(255,255,255,1)');grad.addColorStop(.12,'rgba(255,255,255,.5)');grad.addColorStop(.4,'rgba(255,255,255,.12)');grad.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=grad;ctx.fillRect(0,0,128,128);glowTexture=new T.CanvasTexture(c);
} catch (error) { fallback('WebGL is unavailable on this device. Browse the complete evidence collection instead.'); return; }
let seed=1;
function rand(){seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296;}
const mat=(color,metal=.4,rough=.4)=>new T.MeshStandardMaterial({color,metalness:metal,roughness:rough});
const basic=(color,opacity=1)=>new T.MeshBasicMaterial({color,transparent:opacity<1,opacity,depthWrite:opacity===1});
function mesh(geo,material,x=0,y=0,z=0,parent=environment) { const m=new T.Mesh(geo,material);m.position.set(x,y,z);parent.add(m);return m; }
function box(x,y,z,w,h,d,m,parent=environment){return mesh(new T.BoxGeometry(w,h,d),m,x,y,z,parent);}
function instanceBoxes(records,material){const m=new T.InstancedMesh(new T.BoxGeometry(1,1,1),material,records.length),dummy=new T.Object3D();records.forEach(([x,y,z,w,h,d],i)=>{dummy.position.set(x,y,z);dummy.scale.set(w,h,d);dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);});m.instanceMatrix.needsUpdate=true;environment.add(m);return m;}
function ring(radius,tube,color,x=0,y=0,z=0,parent=environment){return mesh(new T.TorusGeometry(radius,tube,6,100),basic(color),x,y,z,parent);}
function line(points,color,opacity=.6,parent=environment){const l=new T.Line(new T.BufferGeometry().setFromPoints(points.map(p=>new T.Vector3(...p))),new T.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false}));parent.add(l);return l;}
function glow(x,y,z,color,size,parent=environment){const s=new T.Sprite(new T.SpriteMaterial({map:glowTexture,color,transparent:true,opacity:.5,depthWrite:false,blending:T.AdditiveBlending}));s.position.set(x,y,z);s.scale.set(size,size,1);parent.add(s);return s;}
function rod(a,b,radius,material,parent=environment){const av=new T.Vector3(...a),bv=new T.Vector3(...b),diff=bv.clone().sub(av);const m=mesh(new T.CylinderGeometry(radius,radius,diff.length(),6),material,0,0,0,parent);m.position.copy(av.add(bv).multiplyScalar(.5));m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),diff.normalize());return m;}
function animate(object,type,speed=1){animations.push({object,type,speed,base:object.position.y});return object;}
function starfield(color=0xb6d9dd){const points=[];for(let i=0;i<950;i++) points.push((rand()-.5)*130,8+rand()*70,(rand()-.5)*130);const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(points,3));environment.add(new T.Points(geo,new T.PointsMaterial({color,size:.075,transparent:true,opacity:.55,sizeAttenuation:true})));}
function floor(color){
 const m=new T.ShaderMaterial({uniforms:{uColor:{value:new T.Color(color)},uBase:{value:new T.Color(0x0b2026)}},vertexShader:'varying vec3 vPos; void main(){vPos=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec3 vPos; uniform vec3 uColor; uniform vec3 uBase; void main(){vec2 p=vPos.xy; float d=length(p); vec2 g=abs(fract(p*.32-.5)-.5)/fwidth(p*.32);float grid=1.-min(min(g.x,g.y),1.);float radial=pow(.5+.5*cos(d*2.5),55.);float fade=exp(-d*.026);vec3 c=uBase+uColor*(grid*.09+radial*.045)*fade; gl_FragColor=vec4(c,1.);}',extensions:{derivatives:true}});
 const f=mesh(new T.PlaneGeometry(180,180),m);f.rotation.x=-Math.PI/2;f.position.y=-.05;
 const path=mat(0x22383a,.6,.25);box(0,.005,9,5,.035,27,path);
 [-2.65,2.65].forEach(x=>box(x,.035,9,.027,.01,27,basic(color,.55)));
}
function platform(radius,color,y=.15){const m=mat(0x173138,.65,.27);mesh(new T.CylinderGeometry(radius,radius+.2,.3,80),m,0,y,0);const r=ring(radius,.025,color,0,y+.16,0);r.rotation.x=Math.PI/2;}
function arch(a,b,height,color,parent=environment){const points=[];for(let j=0;j<=48;j++){const t=j/48;points.push([a[0]+(b[0]-a[0])*t,Math.sin(t*Math.PI)*height+2,a[1]+(b[1]-a[1])*t]);}line(points,color,.8,parent);}
function crystal(parent,color,size=1){const core=mesh(new T.IcosahedronGeometry(size,0),new T.MeshStandardMaterial({color:0x3d777b,metalness:.65,roughness:.24,emissive:color,emissiveIntensity:.17}),0,0,0,parent);const wire=new T.LineSegments(new T.EdgesGeometry(core.geometry),new T.LineBasicMaterial({color,transparent:true,opacity:.8}));core.add(wire);mesh(new T.OctahedronGeometry(size*.56),basic(color),0,0,0,core);glow(0,0,0,color,size*5,core);return core;}
function jewelMandala(parent,color,radius=4){
 for(let layer=0;layer<3;layer++){
  const group=new T.Group();parent.add(group);group.rotation.z=layer*.19;
  for(let j=0;j<12;j++){const a=j*Math.PI/6;const rr=radius*(.52+layer*.22),petal=ring(rr*.5,.023,color,Math.sin(a)*rr*.54,Math.cos(a)*rr*.54,layer*.12,group);petal.scale.x=.38;petal.rotation.z=-a;}
  const r=ring(radius*(.5+layer*.22),.019,color,0,0,0,group);animate(group,'z',(layer%2?-.022:.016));
 }
 crystal(parent,0x80d6d0,radius*.34);
 for(let i=0;i<12;i++){const a=i*Math.PI/6,jewel=mesh(new T.OctahedronGeometry(radius*.12),new T.MeshStandardMaterial({color:i%2?0x7fbbb1:color,metalness:.65,roughness:.25,emissive:i%2?0x397e76:0x6f5526,emissiveIntensity:.4}),Math.sin(a)*radius*.8,Math.cos(a)*radius*.8,.15,parent);jewel.scale.set(.5,1.65,.5);jewel.rotation.z=-a;}
}
function cathedral(room){
 const stone=mat(0x264147,.55,.33),gold=mat(room.color,.75,.3);platform(7.2,room.color);platform(4.4,room.color,.38);
 const N=16,radius=15;
 for(let i=0;i<N;i++){
  const a=i/N*Math.PI*2,x=Math.sin(a)*radius,z=Math.cos(a)*radius;
  if(z>10 && Math.abs(x)<8)continue; // Open axial entrance; avoid columns across the visitor's sightline.
  mesh(new T.CylinderGeometry(.29,.52,11,8),stone,x,5.5,z);obstacles.push([x,z,.8]);
  for(const y of [.25,1,9.4,10.8])mesh(new T.CylinderGeometry(.67,.67,.14,8),gold,x,y,z);
  box(x,5.5,z,.055,8.2,.64,basic(room.color,.6));glow(x,10.9,z,room.color,3.5);
  const b=(i+1)/N*Math.PI*2;arch([x,z],[Math.sin(b)*radius,Math.cos(b)*radius],11.8,room.color);
  const dome=[];for(let j=0;j<=40;j++){const t=j/40*Math.PI/2;dome.push([Math.sin(a)*radius*Math.cos(t),10.8+Math.sin(t)*13,Math.cos(a)*radius*Math.cos(t)]);}line(dome,room.color,.6);
  const inner=[];for(let j=0;j<=40;j++){const t=j/40*Math.PI/2;inner.push([Math.sin(a+.04)*radius*Math.cos(t),10.8+Math.sin(t)*12.6,Math.cos(a+.04)*radius*Math.cos(t)]);}line(inner,0x77bbb7,.22);
 }
 for(let j=0;j<7;j++){const t=j/7*Math.PI/2,r=ring(15*Math.cos(t),.025,j%2?0x76bfb8:room.color,0,10.8+13*Math.sin(t),0);r.rotation.x=Math.PI/2;}
 const altar=new T.Group();altar.position.set(0,7,0);environment.add(altar);jewelMandala(altar,room.color,4.8);animate(altar,'float',.25);
 for(let i=0;i<3;i++){const r=ring(3.5+i*.5,.025,0x80d6d0,0,7,0);r.rotation.set(i*.8,.6+i*.7,0);animate(r,'y',.06*(i%2?1:-1));}
 glow(0,7,0,0x5ec9cd,17);glow(0,1,0,room.color,11);
}
function threshold(room){
 const stone=mat(0x213c42,.65,.28);platform(6,room.color);
 for(let j=0;j<11;j++){
  const z=5-j*3.1,group=new T.Group();group.position.set(0,5,z);environment.add(group);
  const r=ring(5.6,.085,j%2?room.color:0xe3bf87,0,0,0,group);r.scale.y=1.14;line([[-5.6,-5,0],[-5.6,0,0]],room.color);line([[5.6,-5,0],[5.6,0,0]],room.color);
  for(const x of [-5.9,5.9])box(x,4.5,z,.3,9,.7,stone);
 }
 const mandala=new T.Group();mandala.position.set(0,5.2,-10);environment.add(mandala);jewelMandala(mandala,0xe0b97e,4.4);glow(0,5,-11,room.color,17);
}
function workshop(room){
 const metal=mat(0x392e32,.8,.35);platform(6.5,room.color);
 for(const x of [-11,11])for(let j=0;j<7;j++){
  const z=8-j*4;box(x,4,z,.65,8,.65,metal);box(x,8,z,3,.18,.3,basic(room.color,.6));
  const r=ring(2,.07,room.color,x,5,z);r.rotation.y=Math.PI/2;animate(r,'x',.1);
 }
 for(let j=0;j<5;j++){const r=ring(2.3+j*.4,.05,j%2?0xe3ac88:0x96d9c9,0,5.5,0);r.rotation.set(j*.6,j*.7,0);animate(r,'y',.12*(j%2?-1:1));}
 const group=new T.Group();group.position.y=5.5;environment.add(group);const c=crystal(group,0xe6b274,1.65);animate(c,'y',.18);
 for(const x of [-6,6]){
  box(x,1.4,-3,2.4,.4,24,metal);
  for(let j=0;j<10;j++) {const g=new T.Group();g.position.set(x,2.5,7-j*2.1);environment.add(g);const c=crystal(g,j%2?0x81c9c4:room.color,.33+rand()*.3);animate(c,'y',.2);}
 }
 for(let i=0;i<5;i++){const a=i/5*Math.PI*2,x=Math.sin(a)*3.4,z=Math.cos(a)*3.4;const g=new T.Group();g.position.set(x,2,z);environment.add(g);crystal(g,room.color,.6);ring(.7,.03,0x77d7ce,0,.2,0,g);animate(g,'float',.5);}
 glow(0,5.5,0,room.color,14);
}
function garden(room){
 const bark=mat(0x284439,.35,.6);platform(6.5,room.color);
 for(let i=0;i<22;i++){
  const a=i/22*Math.PI*2,r=10+rand()*10,x=Math.sin(a)*r,z=Math.cos(a)*r,h=3+rand()*5;
  if(z>5 && Math.abs(x)<4.5)continue;
  rod([x,0,z],[x,h,z],.08,bark);obstacles.push([x,z,.45]);
  for(let j=0;j<4;j++){
   const b=j*Math.PI/2+i,xx=x+Math.sin(b)*2,zz=z+Math.cos(b)*2;
   rod([x,h*.6,z],[xx,h+1,zz],.035,bark);
   const leaf=mesh(new T.OctahedronGeometry(.9,0),mat(j%2?0x519d87:0xc5b974,.55,.3),xx,h+.8,zz);leaf.scale.set(.6,1.8,.6);leaf.rotation.z=.45*Math.sin(b);glow(xx,h+.5,zz,0xa2dca3,2.8);
  }
 }
 const flower=new T.Group();flower.position.y=4.5;environment.add(flower);
 for(let layer=0;layer<3;layer++)for(let j=0;j<9;j++){
  const a=j/9*Math.PI*2+layer*.25,r=2+layer*.6,petal=mesh(new T.SphereGeometry(1,16,12),new T.MeshStandardMaterial({color:layer%2?0xc2c698:0x58a99d,metalness:.5,roughness:.3,transparent:true,opacity:.7}),Math.sin(a)*r,layer*.5,Math.cos(a)*r,flower);
  petal.scale.set(.58,.22,2.15);petal.rotation.set(-.35-layer*.12,a,0);
 }
 crystal(flower,0xf1d89c,1);animate(flower,'y',.025);glow(0,5,0,0xdbe6a4,13);
 const fireflies=[];for(let i=0;i<250;i++)fireflies.push((rand()-.5)*37,rand()*8,(rand()-.5)*37);const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(fireflies,3));const flies=new T.Points(geo,new T.PointsMaterial({color:0xc6e49b,size:.07,transparent:true,opacity:.8}));environment.add(flies);animate(flies,'y',.006);
}
function theater(room){
 const white=mat(0x769092,.7,.25),dark=mat(0x203e48,.65,.3);platform(8,room.color);
 for(let i=0;i<12;i++){
  const a=i/12*Math.PI*2,x=Math.sin(a)*12,z=Math.cos(a)*12;
  const b=box(x,4,z,3.6,8,.4,dark);b.rotation.y=a;
  const glowPanel=box(x*.97,5,z*.97,.09,5,.09,basic(room.color));glow(x,5,z,room.color,4);
 }
 box(0,1.5,0,2.3,.45,5,white);box(0,.7,0,1,1.4,2,dark);
 for(let i=0;i<4;i++) {const r=ring(2.5+i*.8,.07,room.color,0,7+i*.2,0);r.rotation.x=Math.PI/2;}
 for(const side of [-1,1])for(const z of [-3,3]){
  const x=side*5;rod([x,0,z],[x,5,z],.14,white);rod([x,5,z],[side*2.8,6,z*.4],.11,white);rod([side*2.8,6,z*.4],[side*1.2,3.4,z*.3],.075,white);glow(side*1.2,3.4,z*.3,room.color,2);
 }
 glow(0,7,0,0xd6efff,17);
}
function library(room){
 const wood=mat(0x3d372b,.45,.5),pages=[mat(0xa28857,.35,.5),mat(0x547875,.4,.4),mat(0x73614e,.4,.5)];platform(6,room.color);
 const structure=[],trim=[],books=[[],[],[]];
 for(const side of [-1,1])for(let j=0;j<6;j++){
  const x=side*10,z=7-j*5;
  structure.push([x,5,z,1,10,4.4]);obstacles.push([x,z,2.1]);
  for(let shelf=0;shelf<6;shelf++){
   const y=1+shelf*1.45;structure.push([x-side*.65,y,z,2,.12,4.7]);trim.push([x-side*1.66,y+.04,z,.03,.04,4.6]);
   for(let b=0;b<8;b++){const h=.6+rand()*.6;books[b%3].push([x-side*.65,y+h*.5+.1,z-1.9+b*.49,.65,h,.16+rand()*.15]);}
  }
  arch([x,z-2],[x,z+2],10.5,room.color);
 }
 instanceBoxes(structure,wood);instanceBoxes(trim,basic(room.color,.6));books.forEach((b,i)=>instanceBoxes(b,pages[i]));
 const g=new T.Group();g.position.set(0,4.3,0);environment.add(g);
 for(const side of [-1,1]){const page=box(side*1.12,0,0,2.2,.1,3,mat(0xd3bd87,.3,.4),g);page.rotation.z=side*.23;
  for(let i=0;i<8;i++)line([[side*.3,.25,-1.1+i*.3],[side*1.7,.55,-1.1+i*.3]],0xf4d697,.75,g);
 }
 animate(g,'float',.3);const r=ring(3.5,.035,room.color,0,4.5,0);r.rotation.x=.35;glow(0,4.5,0,room.color,13);
}
function voidSpace(room){
 scene.fog=new T.FogExp2(room.fog,.025);
 const floor=mesh(new T.CircleGeometry(80,64),mat(0x060a13,.3,.65));floor.rotation.x=-Math.PI/2;
 const r=ring(4.2,.018,0xd2cfdf,0,5,-6);glow(0,5,-6,0x7882ac,9);
 for(let i=0;i<3;i++){const rr=ring(8+i*9,.009,0x687491,0,.02,0);rr.rotation.x=Math.PI/2;}
}
function observatory(room){
 platform(8,room.color);const group=new T.Group();group.position.set(0,6,0);environment.add(group);
 const positions=new Map();
 D.nodes.filter(n=>n.report_count!=null).forEach((n,i)=>{
  const theta=i*2.39996323,y=1-(i/127)*2,r=Math.sqrt(1-y*y),p=new T.Vector3(Math.cos(theta)*r*5,y*5,Math.sin(theta)*r*5);positions.set(n.key,p);
  const colors={realm:0xe0c588,entity:0x88cfc7,geometry:0xbba6d6,motif:0xde9a85,phase:0xccdcd3};
  const m=mesh(new T.SphereGeometry(.045+Math.sqrt(n.report_count/D.n_reports)*.28,8,6),basic(colors[n.kind]||0xa4bfd1),p.x,p.y,p.z,group);m.userData.node=n.key;pickables.push(m);
 });
 const pts=[];D.cooccurrence.slice(0,80).forEach(e=>{const a=positions.get(e.a.join('|')),b=positions.get(e.b.join('|'));if(a&&b)pts.push(a.x,a.y,a.z,b.x,b.y,b.z);});
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pts,3));group.add(new T.LineSegments(geo,new T.LineBasicMaterial({color:0x80aebc,transparent:true,opacity:.17})));
 for(let i=0;i<3;i++){const r=ring(5.5,.025,room.color,0,6,0);r.rotation.set(i*.6,i*.7,0);}
 animate(group,'y',.025);glow(0,6,0,0x659dac,15);
}
function labelSprite(text,color){
 const c=document.createElement('canvas');c.width=768;c.height=128;const ctx=c.getContext('2d');ctx.fillStyle='rgba(5,20,27,.82)';ctx.fillRect(0,0,768,128);ctx.strokeStyle='#698786';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(768,0);ctx.stroke();
 const short=text.length>49?text.slice(0,47)+'…':text;ctx.fillStyle='#e0dfd1';ctx.font='27px Segoe UI';ctx.textAlign='center';ctx.fillText(short,384,54);ctx.fillStyle='#a5bfba';ctx.font='17px Segoe UI';ctx.fillText('CLICK TO TRACE THE EVIDENCE',384,91);
 const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;const sprite=new T.Sprite(new T.SpriteMaterial({map:tex,transparent:true,depthTest:true}));sprite.scale.set(4.4,.73,1);return sprite;
}
function exhibits(room){
 const ped=mat(0x243b40,.55,.35);room.exhibits.forEach((k,i)=>{
  if(!nodes.has(k))return;
  const x=i%2===0?-6.1:6.1,z=i<2?10:0.5,g=new T.Group();g.position.set(x,0,z);environment.add(g);
  mesh(new T.CylinderGeometry(.8,1,1.05,6),ped,0,.55,0,g);const r=ring(.8,.02,room.color,0,1.08,0,g);r.rotation.x=Math.PI/2;
  const c=crystal(g,i%2?0x8ed4cb:room.color,.52);c.position.y=2.15;animate(c,'y',.15);animate(c,'float',.5);
  const hit=mesh(new T.SphereGeometry(.9,10,8),new T.MeshBasicMaterial({visible:false}),0,2.2,0,g);hit.userData.node=k;pickables.push(hit);
  const label=labelSprite(nodes.get(k).name,room.color);label.position.set(0,3.35,0);g.add(label);label.userData.node=k;label.userData.isLabel=true;label.visible=entered;pickables.push(label);obstacles.push([x,z,1.2]);
 });
}
function disposeEnvironment(){
 if(!environment)return;const geometries=new Set(),materials=new Set(),textures=new Set();environment.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{materials.add(m);if(m.map&&m.map!==glowTexture)textures.add(m.map);});});
 scene.remove(environment);geometries.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());textures.forEach(x=>x.dispose());
}
function setRoom(index,updateHash=true){
 sceneGeneration++;
 current=index;const room=rooms[index];clearMovement();disposeEnvironment();animations.length=pickables.length=obstacles.length=0;currentTarget=null;$('inspectButton').hidden=true;seed=11+index*300;
 environment=new T.Group();scene.add(environment);scene.background=new T.Color(room.fog);scene.fog=new T.FogExp2(room.fog,.014);
 environment.add(new T.HemisphereLight(0xb1d9df,0x182529,2));const main=new T.PointLight(room.color,95,48,1.6);main.position.set(0,8,2);environment.add(main);const fill=new T.DirectionalLight(0xb0d3de,2);fill.position.set(5,12,15);environment.add(fill);
 if(room.style!=='void'){floor(room.color);starfield();}
 ({cathedral,threshold,workshop,garden,theater,library,void:voidSpace,observatory})[room.style](room);exhibits(room);resetCamera();
 $('roomTitle').textContent=room.title;$('roomNumber').textContent=`SPACE ${String(index+1).padStart(2,'0')} / 08 · ${index===7?'THE CORPUS':'REPORTED ARCHITECTURE'}`;$('roomSubtitle').textContent=room.subtitle;
 $('roomEvidence').textContent=index===7?'Read the map & methods ↗':'Read this space ↗';
 $('sceneCaption').innerHTML=`<span class="live-dot"></span> ${esc(room.title.toUpperCase())}<small>${index===7?'TAG SIZE = CORPUS MENTIONS · POSITIONS ARE ARBITRARY':'PROCEDURAL INTERPRETATION / CITATIONS AVAILABLE'}</small>`;
 document.querySelectorAll('.room-button').forEach((b,i)=>{b.classList.toggle('active',i===index);b.setAttribute('aria-current',i===index?'location':'false');});
 if(entered&&updateHash)history.replaceState(null,'',`#space=${room.style}`);
}
function resetCamera(){camera.position.set(entered?0:-1.8,entered?2.2:4.1,entered?19:24);yaw=entered?0:.16;pitch=entered?.06:.14;camera.rotation.set(pitch,yaw,0,'YXZ');}
function enter(){if(entered)return;entered=true;environment.traverse(o=>{if(o.userData.isLabel)o.visible=true;});document.body.classList.add('entered');$('intro').hidden=true;$('location').hidden=false;$('crosshair').hidden=false;if(matchMedia('(pointer:coarse)').matches){$('touchControls').hidden=false;$('controlsHint').textContent='Arrow pad to move · drag to look · tap exhibits';}resetCamera();}
$('enterButton').onclick=()=>{enter();history.replaceState(null,'',`#space=${rooms[current].style}`);renderer.domElement.focus();};
$('roomEvidence').onclick=()=>current===7?methodPanel():renderNode(rooms[current].realm);
$('roomNav').innerHTML=rooms.map((r,i)=>`<button class="room-button" data-index="${i}"><small>${String(i+1).padStart(2,'0')} / ${i===7?'EVIDENCE':'SPACE'}</small>${r.short}</button>`).join('');
$('roomNav').onclick=ev=>{const b=ev.target.closest('[data-index]');if(!b)return;stopTour();closePanel();enter();setRoom(Number(b.dataset.index));};
function updateTour(){enter();setRoom(route[tour]);$('tourBar').hidden=false;document.body.classList.add('touring');$('tourLabel').textContent=`CURATED ROUTE ${tour+1} / ${route.length}`;$('tourNext').textContent=tour===route.length-1?'Finish at the evidence ↗':'Next space →';}
function stopTour(){tour=-1;$('tourBar').hidden=true;document.body.classList.remove('touring');}
$('tourButton').onclick=()=>{closePanel();tour=0;updateTour();};$('tourNext').onclick=()=>{if(tour===route.length-1){stopTour();methodPanel();}else{tour++;updateTour();}};$('tourStop').onclick=stopTour;
function pick(clientX,clientY){const p=new T.Vector2(clientX/innerWidth*2-1,-clientY/innerHeight*2+1);raycaster.setFromCamera(p,camera);const hits=raycaster.intersectObjects(pickables,false);return hits.length&&hits[0].distance<32?hits[0].object.userData.node:null;}
renderer.domElement.addEventListener('pointerdown',ev=>{if(!entered||!$('panel').hidden)return;activePointer={id:ev.pointerId,x:ev.clientX,y:ev.clientY,total:0};renderer.domElement.setPointerCapture(ev.pointerId);});
renderer.domElement.addEventListener('pointermove',ev=>{
 if(activePointer?.id===ev.pointerId){const dx=ev.clientX-activePointer.x,dy=ev.clientY-activePointer.y;activePointer.total+=Math.abs(dx)+Math.abs(dy);activePointer.x=ev.clientX;activePointer.y=ev.clientY;yaw-=dx*.0035;pitch=Math.max(-1.15,Math.min(1.35,pitch-dy*.0035));}
 else if(entered){hovered=pick(ev.clientX,ev.clientY);renderer.domElement.style.cursor=hovered?'pointer':'grab';}
});
renderer.domElement.addEventListener('pointerup',ev=>{if(activePointer?.id===ev.pointerId){if(activePointer.total<7){const k=pick(ev.clientX,ev.clientY);if(k)renderNode(k);}activePointer=null;}});
renderer.domElement.addEventListener('pointercancel',clearMovement);
renderer.domElement.addEventListener('webglcontextlost',ev=>{ev.preventDefault();clearMovement();notify('The graphics context was lost. Reload to restore 3D; the evidence index still works.');});
window.addEventListener('keydown',ev=>{
 if(ev.key==='Escape'){closePanel();clearMovement();return;}
 if(!$('panel').hidden){
  if(ev.key==='Tab'){const focusables=[...$('panel').querySelectorAll('button:not([hidden]),input,select,a,summary')].filter(e=>e.getClientRects().length);const first=focusables[0],last=focusables.at(-1);if(ev.shiftKey&&document.activeElement===first){ev.preventDefault();last?.focus();}else if(!ev.shiftKey&&document.activeElement===last){ev.preventDefault();first?.focus();}}
  return;
 }
 if(ev.ctrlKey||ev.metaKey||ev.altKey||/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName))return;
 const k=ev.key.toLowerCase();if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright','shift'].includes(k)&&entered){ev.preventDefault();keys.add(k);}
 if(k==='i')renderIndex();if(k==='h'&&entered)resetCamera();if(k==='e'&&currentTarget&&entered)renderNode(currentTarget);
});
window.addEventListener('keyup',ev=>keys.delete(ev.key.toLowerCase()));window.addEventListener('blur',clearMovement);document.addEventListener('visibilitychange',clearMovement);
document.querySelectorAll('[data-move]').forEach(b=>{b.onpointerdown=ev=>{ev.preventDefault();b.setPointerCapture(ev.pointerId);touchMoves.add(b.dataset.move);};b.onpointerup=b.onpointercancel=()=>touchMoves.delete(b.dataset.move);});
$('inspectButton').onclick=()=>currentTarget&&renderNode(currentTarget);
function move(dt){
 if(!entered||!$('panel').hidden)return;
 let forward=Number(keys.has('w')||keys.has('arrowup')||touchMoves.has('forward'))-Number(keys.has('s')||keys.has('arrowdown')||touchMoves.has('back'));
 let right=Number(keys.has('d')||keys.has('arrowright')||touchMoves.has('right'))-Number(keys.has('a')||keys.has('arrowleft')||touchMoves.has('left'));
 const len=Math.hypot(forward,right);if(!len)return;forward/=len;right/=len;
 const speed=(keys.has('shift')?8:4.2)*dt,dx=(-Math.sin(yaw)*forward+Math.cos(yaw)*right)*speed,dz=(-Math.cos(yaw)*forward-Math.sin(yaw)*right)*speed;
 const x=Math.max(-27,Math.min(27,camera.position.x+dx)),z=Math.max(-29,Math.min(29,camera.position.z+dz));
 if(!obstacles.some(([ox,oz,r])=>Math.hypot(x-ox,z-oz)<r+.28)){camera.position.x=x;camera.position.z=z;}
}
let frameCount=0;
function frame(time){
 requestAnimationFrame(frame);const dt=Math.min((time-lastTime)/1000,.045);lastTime=time;if(document.hidden)return;
 move(dt);camera.rotation.set(pitch,yaw,0,'YXZ');if(!reduced){clock+=dt;animations.forEach(a=>{if(a.type==='float')a.object.position.y=a.base+Math.sin(clock*a.speed)*.17;else a.object.rotation[a.type]+=dt*a.speed;});}
 if(entered&&$('panel').hidden&&frameCount++%8===0){currentTarget=pick(innerWidth/2,innerHeight/2);$('inspectButton').hidden=!currentTarget;if(currentTarget)$('inspectButton').textContent=`E · ${nodes.get(currentTarget)?.name || 'Read exhibit'} ↗`;}
 $('compassNeedle').setAttribute('transform',`rotate(${-yaw*180/Math.PI} 60 60)`);renderer.render(scene,camera);renderedGeneration=sceneGeneration;
}
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
setRoom(current,false);requestAnimationFrame(frame);
function readHash(){const h=new URLSearchParams(location.hash.slice(1));if(h.has('space')){const i=rooms.findIndex(r=>r.style===h.get('space'));if(i>=0){enter();setRoom(i,false);}}if(h.has('node')&&nodes.has(h.get('node')))renderNode(h.get('node'),false);}
window.addEventListener('hashchange',readHash);readHash();
// A read-only diagnostic surface for headless acceptance checks.
window.worldDiagnostics=()=>({room:rooms[current].style,renderReady:sceneGeneration===renderedGeneration,entered,position:camera.position.toArray(),yaw,pitch,reduced,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,nodes:D.nodes.length,pickables:pickables.length,missingExhibits:rooms.flatMap(r=>[r.realm,...r.exhibits]).filter(k=>!nodes.has(k))});
})();
