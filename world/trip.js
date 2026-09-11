/* Through: all imagery is procedural interpretation. Scene keys resolve into the local evidence bundle. */
(() => {
'use strict';
const $ = id => document.getElementById(id), D = window.WORLD_DATA;
if (!window.THREE || !D) { $('failure').hidden = false; return; }
const T = THREE, F = window.FractalWorld, nodeMap = new Map(D.nodes.map(n => [n.key,n])), sourceMap = new Map(D.sources.map(s => [s.key,s]));
const keys = {
 onset:'phase|Inhalation / Onset', flower:'geometry|The Chrysanthemum', rush:'geometry|Zooming / Rushing Tunnel Flight',
 membrane:'phase|Through the Membrane', waiting:'realm|The Waiting Room', cathedral:'realm|The Domed Cathedral',
 elves:'entity|Self-transforming machine elves', jester:'entity|The Jester / Trickster / Clown', mother:'entity|The Divine Feminine',
 mantis:'entity|Mantis & insectoid beings', language:'geometry|Living language / visible sound', breathing:'geometry|Breathing & Liquid Surfaces',
 workshop:'realm|The Workshop / Factory / Market', garden:'realm|The Garden', clinical:'realm|The Hospital / Operating Theater', void:'realm|The Void'
};
const route = [
 {id:'onset',name:'The familiar room',hint:'A quiet beginning. Walk toward the light as the room starts to change.',duration:18,evidence:[keys.onset,keys.breathing]},
 {id:'geometry',name:'The room falls away',hint:'Pattern no longer sits on the walls. It becomes the walls.',duration:18,evidence:[keys.breathing,keys.flower,keys.onset]},
 {id:'chrysanthemum',name:'The chrysanthemum',hint:'A shifting-colour flower, folding into itself. Move through its centre.',duration:22,evidence:['phase|The Chrysanthemum',keys.flower]},
 {id:'rush',name:'The rush',hint:'The passage stretches around you. The far opening draws closer.',duration:16,evidence:['phase|The Rush',keys.rush]},
 {id:'membrane',name:'The threshold',hint:'The surface yields. Another space is waiting beyond it.',duration:17,evidence:[keys.membrane,'geometry|The Aperture / Iris Opening']},
 {id:'waiting',name:'The waiting room',hint:'An enclosed, living room. A figure notices you and gestures toward the opening.',duration:26,evidence:[keys.waiting,'phase|Arrival — The Waiting Room',keys.jester,keys.breathing]},
 {id:'cathedral',name:'Under an impossible dome',hint:'Look up. Continue through the central arch, or take a side passage.',duration:32,evidence:[keys.cathedral,'phase|Breakthrough',keys.breathing,keys.elves]},
 {id:'contact',name:'They seem to be expecting you',hint:'Small beings gather. Their hands shape something that will not stay still.',duration:27,evidence:['phase|Entity Contact',keys.elves,keys.jester,keys.cathedral]},
 {id:'download',name:'A language made visible',hint:'Gesture becomes form. Patterns unfold between the beings and you.',duration:25,evidence:['phase|The Download / Lesson',keys.language,keys.elves,keys.jester,keys.cathedral]},
 {id:'return',name:'The way back',hint:'The forms loosen and recede. Ordinary space comes into view.',duration:20,evidence:['phase|The Return',keys.breathing]},
 {id:'afterglow',name:'Here, again',hint:'The room is still. The journey is complete; its meaning is left open.',duration:0,evidence:['phase|Afterglow / Integration','phase|The Return']}
];
const branches = {
 workshop:{id:'workshop',name:'The workshop',hint:'Jeweled makers pass changing objects between their hands. Approach to see their work.',evidence:[keys.workshop,keys.elves,keys.language]},
 garden:{id:'garden',name:'The luminous garden',hint:'A maternal presence opens her arms. Living forms surround the path.',evidence:[keys.garden,keys.mother,keys.breathing]},
 clinical:{id:'clinical',name:'The examination room',hint:'A tall insectoid presence bends its articulated limbs toward you.',evidence:[keys.clinical,keys.mantis]},
 void:{id:'void',name:'Without a room',hint:'Architecture gives way to near-darkness. There is no required encounter here.',evidence:[keys.void,'phase|The Peak / Throne / Apex']}
};
let renderer;
try { renderer = new T.WebGLRenderer({canvas:$('world'),antialias:true,powerPreference:'high-performance'}); }
catch { $('failure').hidden=false; return; }
renderer.setPixelRatio(Math.min(devicePixelRatio,F.quality==='high'?1.5:1)); renderer.setSize(innerWidth,innerHeight);
// Adaptive render scale: the stage shaders were tuned on a software renderer, so a
// real GPU meets a few (the chrysanthemum fold field) that cannot hold 60 Hz at full
// resolution. Step the pixel ratio down while frames run long, back up when they don't.
let prTarget=Math.min(devicePixelRatio,F.quality==='high'?1.5:1),prNow=prTarget,frameEma=16,prCooldown=0;const prMemo={},prBad={};
function setPR(v){prNow=v;renderer.setPixelRatio(v);renderer.setSize(innerWidth,innerHeight);if(typeof composite!=='undefined')composite.resize();drawInvalidated=true;}
renderer.outputColorSpace=T.SRGBColorSpace; renderer.toneMapping=T.ACESFilmicToneMapping; renderer.toneMappingExposure=1.2;
const scene=new T.Scene(), camera=new T.PerspectiveCamera(68,innerWidth/innerHeight,.06,180);
const composite=F.compositor(renderer);
let drawInvalidated=true,lastDrawFrozen=false;
const drawnPosition=new T.Vector3(),drawnRotation=new T.Quaternion();let drawnInteractions=-1;
const renderGL=renderer.getContext();let renderFence=null,renderedAnimTime=0;
const GPU_FENCE=!!navigator.webdriver||new URLSearchParams(location.search).has('capture');
camera.rotation.order='YXZ';
let root, stage=route[0], routeIndex=0, entered=false, paused=false, paced=true;
let reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let elapsed=0, animTime=0, stageAnimStart=0, yaw=0, pitch=0, transition=null, renderReady=false, frames=0;
const signalStages=['onset','geometry','rush','membrane','return'],echoStages=['geometry','membrane','download','return'];
let actors=[], motions=[], materials=[], portals=[], solids=[], visited=[], entities=[], currentEvidence=[], pointedAt=null;
let bounds={x:7,zMin:-11,zMax:8}, entryZ=7, exitZ=-10, lastFrame=performance.now(), manualUntil=0;
let lastMovement=performance.now(),movementTimer=null;
const input=new Set(), up=new T.Vector3(0,1,0);
const geometry={sphere:new T.SphereGeometry(1,20,14),box:new T.BoxGeometry(1,1,1),cylinder:new T.CylinderGeometry(1,1,1,16),cone:new T.ConeGeometry(1,1,16),ico:new T.IcosahedronGeometry(1,1)};
const mat=(color,metal=.2,emissive=0,intensity=.2)=>new T.MeshStandardMaterial({color,metalness:metal,roughness:.38,emissive,emissiveIntensity:intensity});
let gold, dark, ivory, teal, rose;
function mesh(geo,material,x=0,y=0,z=0,sx=1,sy=sx,sz=sx,parent=root) {
 const o=new T.Mesh(geo,material);o.position.set(x,y,z);o.scale.set(sx,sy,sz);parent.add(o);return o;
}
function ball(material,x,y,z,sx,sy=sx,sz=sx,parent=root){return mesh(geometry.sphere,material,x,y,z,sx,sy,sz,parent);}
function box(material,x,y,z,sx,sy,sz,parent=root){return mesh(geometry.box,material,x,y,z,sx,sy,sz,parent);}
function rod(a,b,r,material,parent=root){const av=new T.Vector3(...a),bv=new T.Vector3(...b),d=bv.clone().sub(av);const o=mesh(geometry.cylinder,material,...av.clone().add(bv).multiplyScalar(.5).toArray(),r,d.length(),r,parent);o.quaternion.setFromUnitVectors(up,d.normalize());return o;}
function tube(points,r,material,parent=root){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));return mesh(new T.TubeGeometry(curve,Math.max(16,points.length*4),r,6,false),material,0,0,0,1,1,1,parent);}
function torus(radius,t,material,x,y,z,rx=0,ry=0,parent=root){const o=mesh(new T.TorusGeometry(radius,t,8,80),material,x,y,z,1,1,1,parent);o.rotation.set(rx,ry,0);return o;}
function patterned(palette=0,scale=5,strength=1) {
 return F.surface(palette,scale,strength,materials);
}
function plane(w,h,material,x,y,z,rx=0,ry=0,parent=root){const segments=material.uniforms?.relief?32:1;const o=mesh(new T.PlaneGeometry(w,h,segments,segments),material,x,y,z,1,1,1,parent);o.rotation.set(rx,ry,0);return o;}
function light(color,intensity,x,y,z,dist=80){const l=new T.PointLight(color,intensity,dist,1.3);l.position.set(x,y,z);root.add(l);return l;}
function arch(x,z,width,height,material=gold,ry=0){if(!['onset','afterglow'].includes(stage.id))return F.arcade(root,materials,motions,{x,z,width,height,ry,palette:stage.id==='clinical'?2:3});const g=new T.Group();g.position.set(x,0,z);g.rotation.y=ry;root.add(g);const r=width/2,shoulder=height-r;rod([-r,0,0],[-r,shoulder,0],.16,material,g);rod([r,0,0],[r,shoulder,0],.16,material,g);const pts=[];for(let i=0;i<=24;i++){const a=i/24*Math.PI;pts.push([Math.cos(a)*r,shoulder+Math.sin(a)*r,0]);}tube(pts,.16,material,g);return g;}
function opening(x,z,width,height,target,ry=0,color=0x85eadb){const a=arch(x,z,width,height,gold,ry);const glow=new T.MeshBasicMaterial({color,transparent:true,opacity:.075,side:T.DoubleSide,depthWrite:false});plane(width,height,glow,0,height/2,-.25,0,0,a);if(target)portals.push({x,z,width,target});return a;}
function dust(count=250,color=0xd9c49e,spread=24){const coords=[];for(let i=0;i<count;i++)coords.push(Math.sin(i*83.17)*spread,1+(Math.sin(i*13.3)*.5+.5)*spread,Math.cos(i*39.31)*spread);const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(coords,3));const p=new T.Points(g,new T.PointsMaterial({color,size:.035,transparent:true,opacity:.6,depthWrite:false}));root.add(p);motions.push(t=>{p.rotation.y=t*.007;});}
function disposeScene(){if(!root)return;const gs=new Set(),ms=new Set();root.traverse(o=>{if(o.isInstancedMesh)o.dispose();if(o.geometry&&!Object.values(geometry).includes(o.geometry))gs.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>ms.add(m));});gs.forEach(g=>g.dispose());ms.forEach(m=>m.dispose());scene.remove(root);}
function build(s){
 drawInvalidated=true;
 disposeScene();root=new T.Group();scene.add(root);actors=[];motions=[];materials=[];portals=[];solids=[];entities=[];
 gold=mat(0xe8b969,.72,0xa96722,.24);dark=mat(0x0c1230,.25);ivory=mat(0xe2e0cd,.25,0x806244,.08);teal=mat(0x49cbbb,.5,0x139c99,.3);rose=mat(0xbb357b,.5,0x780947,.22);
 scene.background=new T.Color(s.id==='void'?0x04060d:0x171122);scene.fog=new T.FogExp2(scene.background,.009);
 root.add(new T.HemisphereLight(0xbacbed,0x6d3753,2.3));const sun=new T.DirectionalLight(0xffda9d,2.4);sun.position.set(-4,14,8);root.add(sun);light(0x67dccc,40,4,7,-6);
 bounds={x:7,zMin:-13,zMax:10};entryZ=8;exitZ=-11;
 if(['onset','afterglow'].includes(s.id))ordinary(s.id==='afterglow');
 else if(['geometry','chrysanthemum','rush','membrane','return'].includes(s.id))passage(s.id);
 else if(s.id==='waiting')waiting();
 else if(['cathedral','contact','download'].includes(s.id))cathedral(s.id);
 else if(s.id==='workshop')workshop();else if(s.id==='garden')garden();else if(s.id==='clinical')clinical();else if(s.id==='void')voidSpace();
 const motifs=s.id==='afterglow'?[]:['geometry|Fractal lattices & jeweled tilings','geometry|Static Pattern Overlay & filigree','geometry|Breathing & Liquid Surfaces'];
 if(!['onset','afterglow','void'].includes(s.id))motifs.push('geometry|Dimensional Layering & Space-Folding','geometry|Hyperbolic Space & Negative Curvature','geometry|Ultra-Detail & Infinite Resolution','geometry|Energy Conduits & Living Circuitry');
 if(['geometry','chrysanthemum','rush','membrane','return'].includes(s.id))motifs.push('geometry|Mandalas & symmetry fields',keys.flower);
 if(actors.length)motifs.push('geometry|Embedded Faces & the Pareidolia Cascade','geometry|Hyper-dimensional objects');
 if(!['onset','afterglow','geometry','chrysanthemum','rush','membrane','waiting','cathedral','contact','download','return','void','workshop','garden','clinical'].includes(s.id))F.lattice(root,materials,motions,{radius:s.id==='cathedral'||s.id==='contact'||s.id==='download'?19:8,height:s.id==='garden'?8:10,palette:s.id==='garden'?2:3});
 if(signalStages.includes(s.id))motifs.push('geometry|TV Static & the Signal-Noise Transition');
 if(echoStages.includes(s.id)){
  motifs.push('geometry|Time Geometry — Moments as Objects & Loops');
  if(s.id!=='geometry'&&s.id!=='membrane'&&s.id!=='download'&&s.id!=='return'){
   const echoes=F.timeLayers(root,materials,motions,{z:s.id==='download'?2:0,palette:s.id==='return'?4:2,loosening:s.id==='return'});
   echoes.traverse(o=>{if(o.isMesh)o.userData.evidence=['geometry|Time Geometry — Moments as Objects & Loops','geometry|Dimensional Layering & Space-Folding'];});
  }
 }
 currentEvidence=[...new Set([...s.evidence,...motifs])];pointedAt=null;root.userData.evidence=currentEvidence;
 root.traverse(o=>{if(o.isMesh||o.isPoints||o.isLine)o.userData.evidence=o.userData.evidence||currentEvidence;});
 if(actors.length)for(const m of materials)if(m.uniforms.radiance&&!m.userData.entity)m.uniforms.radiance.value=.3;
 camera.position.set(0,1.7,entryZ);yaw=0;pitch=s.id==='cathedral'?.12:0;camera.rotation.set(pitch,yaw,0);elapsed=0;stageAnimStart=animTime;renderReady=false;frameEma=16;prCooldown=2;if(!GPU_FENCE){const want=prMemo[s.id]??prTarget;if(want!==prNow)setPR(want);}
 for(const m of materials)m.uniforms.time.value=animTime;for(const fn of motions)fn(animTime);animateBeings(animTime);
}
function ordinary(after=false){
 bounds={x:6.6,zMin:-8.5,zMax:8};entryZ=6.5;exitZ=-7.7;scene.background=new T.Color(0x181c2b);scene.fog.density=.018;
 if(after){
  // Ordinary bounced daylight, without the journey's coloured fill lights.
  for(const o of root.children){
   if(o.isHemisphereLight){o.color.set(0xdce4ee);o.groundColor.set(0x756553);o.intensity=1.55;}
   else if(o.isDirectionalLight){o.color.set(0xffedda);o.intensity=1.5;o.position.set(3.5,5,-8);}
   else if(o.isPointLight)o.intensity=0;
  }
 }
 const wall=mat(after?0x686375:0x454554,0),wood=mat(0x493b36,.05),cloth=mat(0x646376,0),floor=mat(0x433f40,.1);
 plane(14,18,floor,0,0,0,-Math.PI/2);plane(18,7,wall,-7,3.5,0,0,Math.PI/2);plane(18,7,wall,7,3.5,0,0,-Math.PI/2);plane(14,7,wall,0,3.5,9,0,Math.PI);plane(14,18,wall,0,7,0,Math.PI/2);
 const windowSurround=[[1.8,3.5,.6,7],[5.95,3.5,2.1,7],[3.5,1.175,2.8,2.35],[3.5,6.025,2.8,1.95]];
 box(wall,-4.25,3.5,-9,5.5,7,.3);box(wall,0,5.75,-9,3,2.5,.3);
 {
  for(const [x,y,w,h] of windowSurround)box(wall,x,y,-9,w,h,.3);
  // The onward opening contains actual space, not an opaque gold panel.
  portals.push({x:0,z:-8.95,width:3,target:'next'});
  const reveal=mat(0xa59a86,0),passageWall=mat(0x7c7064,0);
  for(const x of [-1.56,1.56]){
   box(reveal,x,2.25,-9.1,.18,4.5,.9);
   box(passageWall,x,2.25,-12,.16,4.5,6);
  }
  box(reveal,0,4.52,-9.1,3.3,.18,.9);box(reveal,0,.045,-9.1,3.3,.09,.9);
  plane(3,6,wood,0,.01,-12,-Math.PI/2);plane(3,6,passageWall,0,4.5,-12,Math.PI/2);
  const beyond=new T.ShaderMaterial({uniforms:{time:{value:0},sky:{value:0}},
   vertexShader:'varying vec2 apertureUV; void main(){apertureUV=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
   fragmentShader:`
    uniform float time,sky;varying vec2 apertureUV;
    void main(){
     vec2 q=apertureUV;float t=time*.06;
     vec3 col;
     if(sky>.5){
      float cloud=sin(q.x*7.+sin(q.y*8.)+t)+.35*sin(q.x*19.-q.y*11.-t*.7);
      col=mix(vec3(.75,.43,.3),vec3(.12,.23,.37),smoothstep(.22,.95,q.y));
      col+=vec3(.27,.18,.15)*exp(-pow((q.y-.45+cloud*.025)*12.,2.));
      col+=vec3(.85,.5,.22)*exp(-length((q-vec2(.66,.44))*vec2(5.,9.)));
      for(int i=0;i<4;i++){
       float k=float(i),ridge=.2-k*.038+.028*sin(q.x*(9.+k*3.)+k*7.)+.016*sin(q.x*23.+k);
       col=mix(col,vec3(.085,.14,.17)*(1.-k*.14),1.-smoothstep(ridge-.003,ridge+.003,q.y));
      }
     }else{
      float glow=exp(-length((q-vec2(.68+.045*sin(t*3.),.58))*vec2(2.7,1.5)));
      col=mix(vec3(.28,.2,.15),vec3(1.4,1.05,.63),glow);
      col+=vec3(.12,.09,.06)*sin(q.y*3.+t*2.);
     }
     gl_FragColor=vec4(col,1.);
     #include <tonemapping_fragment>
     #include <colorspace_fragment>
    }`});
  materials.push(beyond);plane(3,4.5,beyond,0,2.25,-15);
  light(0xffd5a1,18,.5,3,-12,12);
  const sky=beyond.clone();sky.uniforms.sky.value=1;materials.push(sky);
  plane(12,8,sky,3.5,4,-16);
 }
 const rug=mat(after?0x817365:0x51414b,0);plane(7,8,rug,0,.012,1,-Math.PI/2);
 // Familiar objects soften and breathe in onset; the return room keeps its own forms.
 const furnitureTime={value:0},furnitureMaterials=new Map();
 function furnish(base,x,y,z,w,h,d){
  let material=furnitureMaterials.get(base);
  if(!material){
   const timber=base===wood;
   material=new T.MeshPhysicalMaterial({color:base.color,roughness:timber?(after?.74:.32):(after?.88:.78),
    metalness:0,clearcoat:timber&&!after?.32:0,clearcoatRoughness:.38,
    sheen:timber?0:(after?.22:.75),sheenColor:new T.Color(0xc6bacf),sheenRoughness:.65});
   material.onBeforeCompile=shader=>{
    shader.uniforms.furnitureTime=furnitureTime;
    shader.vertexShader='uniform float furnitureTime; varying vec3 furnitureP;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`
     #include <begin_vertex>
     furnitureP=position;
     vec3 anchor=(modelMatrix*vec4(0.,0.,0.,1.)).xyz;
     float wave=sin(position.z*1.8+position.x*.9+anchor.z*.35-furnitureTime*.95);
     transformed+=normal*(.045+.025*sin(position.y*3.+furnitureTime*.7))*wave*${after?'0.':'1.'};
     transformed.y+=.035*sin(position.z*1.3+anchor.x-furnitureTime*.95)*${after?'0.':'1.'};
    `);
    shader.fragmentShader=`varying vec3 furnitureP;
     ${after?`float timberHash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
     float timberNoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(timberHash(i),timberHash(i+vec2(1,0)),f.x),
       mix(timberHash(i+vec2(0,1)),timberHash(i+vec2(1,1)),f.x),f.y);}`:''}
    `+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`
     #include <color_fragment>
     vec3 p=furnitureP;
     ${after&&timber?`vec2 grainUV=vec2(p.x*32.,(p.z+p.y)*1.7);
      float grain=timberNoise(grainUV+vec2(timberNoise(grainUV*.09)*2.,0.));
      float pores=timberNoise(grainUV*vec2(7.,2.));
      diffuseColor.rgb*=.89+.11*grain+.025*pores;`:
     after?`float weave=sin(p.x*190.)*sin((p.y+p.z)*210.);
      diffuseColor.rgb*=.96+.012*weave;`:
     timber?`float grain=sin(p.x*38.+sin(p.z*2.1)*3.+sin(p.x*8.+p.z)*1.4);
      float pore=sin(p.x*170.+sin(p.z*3.)*8.);
      diffuseColor.rgb*=.77+.15*grain+.05*pore;`:
     `float weave=sin(p.x*190.)*sin((p.y+p.z)*210.);
      float fold=.5+.5*sin(p.z*8.+sin(p.x*6.)*.45);
      diffuseColor.rgb*=.82+.05*weave+.12*fold;`}
    `);
   };
   furnitureMaterials.set(base,material);
  }
  const radius=Math.min(.24,Math.min(w,h,d)*.42),g=new T.BoxGeometry(w,h,d,24,16,24);
  const pos=g.attributes.position,norm=g.attributes.normal,half=new T.Vector3(w/2-radius,h/2-radius,d/2-radius);
  const v=new T.Vector3(),inner=new T.Vector3(),n=new T.Vector3();
  for(let i=0;i<pos.count;i++){
   v.fromBufferAttribute(pos,i);inner.copy(v).clamp(half.clone().negate(),half);
   n.copy(v).sub(inner).normalize();v.copy(inner).addScaledVector(n,radius);
   pos.setXYZ(i,v.x,v.y,v.z);norm.setXYZ(i,n.x,n.y,n.z);
  }
  return mesh(g,material,x,y,z);
 }
 if(!after)motions.push(t=>{furnitureTime.value=t;});
 furnish(cloth,-5,.62,-.8,2.6,1.1,5);furnish(cloth,-6,1.5,-.8,.7,1.3,5);furnish(cloth,-5,1.2,-3.25,2.7,.9,.45);furnish(cloth,-5,1.2,1.65,2.7,.9,.45);
 const cushion=mat(0x999183,0);
 for(let i=0;i<3;i++){
  furnish(cushion,-4.95,1.24,-2.2+i*1.4,1.8,.28,1.3);
  {const back=furnish(cloth,-5.58,1.7,-2.2+i*1.4,.42,1.05,1.3);back.rotation.z=.12;}
 }
 furnish(wood,-2.1,.7,-.5,2.5,.15,3);for(const x of [-3.1,-1.1])for(const z of [-1.6,.6])rod([x,0,z],[x,.7,z],.07,wood);solids.push({x:-2.1,z:-.5,w:3,d:3.5},{x:-5,z:-.8,w:3,d:5.7},{x:5,z:-4,w:2,d:.65},{x:4.5,z:0,w:.25,d:.25},{x:3.5,z:3,w:.8,d:.8});
 box(ivory,-2.1,.83,-.8,.6,.12,.85);ball(ivory,-1.5,.94,.1,.12,.17,.12);
 furnish(wood,5,.85,-4,2,1.7,.65);
 if(after){
  const pages=mat(0xb9b09a,0);pages.roughness=.95;
  for(let i=0;i<8;i++){
   const book=new T.Group();root.add(book);book.position.set(4.29+i*.175,1.72,-4);
   book.rotation.z=i===6?-.10:(i===0?.07:0);
   const h=.49+(i%3)*.065,d=.35+(i%2)*.04,cover=mat([0x68584a,0x3e5451,0x8b7554,0x554d58][i%4],0);
   cover.roughness=.85;
   box(pages,0,h/2,0,.105,h-.035,d-.035,book);
   for(const x of [-.061,.061])box(cover,x,h/2,0,.017,h,d,book);
   box(cover,0,h/2,d/2,.14,h,.025,book);
   for(const y of [h*.15,h*.84])box(pages,0,y,d/2+.013,.082,.009,.002,book);
  }
 }else for(let i=0;i<9;i++)box(mat([0x816763,0x536f71,0xaa9061][i%3]),4.25+i*.17,1.99,-4,.12,.6+(i%3)*.06,.4);
 {
  for(const x of [4.51,5.49]){furnish(wood,x,.86,-3.64,.91,1.42,.08);ball(gold,x+(x<5?.3:-.3),.95,-3.55,.035);}
  const shadow=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{time:{value:0}},
   vertexShader:'varying vec2 uvShadow; void main(){uvShadow=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
   fragmentShader:'varying vec2 uvShadow; void main(){vec2 p=(uvShadow-.5)*2.;float a=1.-smoothstep(.3,1.,length(p));gl_FragColor=vec4(.035,.025,.045,a*.56);}'});
  const shadowY=after?.031:.3;
  plane(4.1,5,shadow,-2.1,shadowY,-.5,-Math.PI/2);plane(4.2,6.4,shadow,-5,shadowY,-.8,-Math.PI/2);plane(3.3,2,shadow,5,shadowY,-4,-Math.PI/2);
 }
 if(after){
  const stand=mat(0x665b49,.3);stand.roughness=.65;
  mesh(new T.CylinderGeometry(.34,.38,.07,48),stand,4.5,.065,0);
  rod([4.5,.1,0],[4.5,3.24,0],.027,stand);
  const linen=new T.MeshStandardMaterial({color:0xb7a98c,roughness:.94,metalness:0,side:T.DoubleSide});
  linen.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec2 shadeUV;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nshadeUV=uv;');
   shader.fragmentShader='varying vec2 shadeUV;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`
    #include <color_fragment>
    float yarn=sin(shadeUV.x*1800.)*sin(shadeUV.y*600.);
    diffuseColor.rgb*=.97+.018*yarn;
   `).replace('#include <emissivemap_fragment>',`
    #include <emissivemap_fragment>
    float transmitted=exp(-pow((shadeUV.y-.4)*2.3,2.));
    totalEmissiveRadiance+=vec3(.46,.29,.12)*transmitted;
   `);
  };
  mesh(new T.CylinderGeometry(.54,.73,.72,64,8,true),linen,4.5,3,0);
  const binding=mat(0xc0ad89,0);binding.roughness=.9;
  for(const [y,r] of [[2.64,.73],[3.36,.54]]){
   const ring=mesh(new T.TorusGeometry(r,.016,8,64),binding,4.5,y,0);ring.rotation.x=Math.PI/2;
  }
  for(let i=0;i<3;i++){const a=i*Math.PI*2/3;rod([4.5,2.78,0],[4.5+Math.cos(a)*.7,2.66,Math.sin(a)*.7],.009,stand);}
  ball(new T.MeshStandardMaterial({color:0xffe8c4,emissive:0xffd39a,emissiveIntensity:1}),4.5,2.94,0,.105,.16,.105);
 }else{
  rod([4.5,0,0],[4.5,3,0],.045,gold);mesh(new T.CylinderGeometry(.58,.83,.8,32,1,true),mat(0xf5d4a0,0,0xffb553,.55),4.5,3,0);
 }
 light(0xffc48b,23,4.5,2.7,0,15);
 {
  const lining=mat(0x938777,0),frame=mat(0x4a4037,0);
  for(const x of [2.08,4.92]){box(lining,x,3.7,-9.16,.14,2.84,.8);box(frame,x,3.7,-8.7,.14,2.96,.14);}
  for(const y of [2.33,5.07]){box(lining,3.5,y,-9.16,2.98,.14,.8);box(frame,3.5,y,-8.7,2.98,.14,.14);}
  box(lining,3.5,2.25,-8.85,3.2,.14,1.15);
  box(frame,3.5,3.7,-9.42,.065,2.7,.12);box(frame,3.5,3.7,-9.42,2.8,.065,.12);
  const glass=new T.MeshPhysicalMaterial({color:0xb5cede,metalness:.15,roughness:.07,transparent:true,opacity:.12,depthWrite:false,side:T.DoubleSide});
  plane(2.7,2.62,glass,3.5,3.7,-9.45);
  light(0xaccbff,7,3.5,4,-9.15,9);
 }
 if(after){
  const ceramic=mat(0x8b7661,0);ceramic.roughness=.88;
  const profile=[[.30,0],[.32,.035],[.41,.54],[.43,.57],[.43,.60],[.39,.60],[.38,.55],[.29,.07]].map(p=>new T.Vector2(...p));
  mesh(new T.LatheGeometry(profile,64),ceramic,3.5,.03,3);
  const soil=mat(0x2d231a,0);soil.roughness=1;
  mesh(new T.CylinderGeometry(.382,.382,.025,48),soil,3.5,.56,3);
  const stem=mat(0x53603b,0);stem.roughness=.9;
  const foliage=new T.MeshStandardMaterial({color:0x50643d,roughness:.82,metalness:0,side:T.DoubleSide});
  foliage.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec2 leafUV;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nleafUV=uv;');
   shader.fragmentShader='varying vec2 leafUV;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`
    #include <color_fragment>
    float mid=exp(-abs(leafUV.x-.5)*160.);
    float ribs=pow(.5+.5*cos((leafUV.y-abs(leafUV.x-.5)*.43)*95.),14.);
    diffuseColor.rgb*=.80+.17*sin(leafUV.y*3.14159)+.12*mid+.035*ribs;
   `);
  };
  for(let i=0;i<15;i++){
   const a=i*2.399,dx=Math.cos(a),dz=Math.sin(a),h=1.02+i*.074;
   const start=new T.Vector3(3.5+dx*.15,h,3+dz*.15),length=.50+.18*Math.sin(i*3.7)**2;
   const curve=new T.CatmullRomCurve3([new T.Vector3(3.5,.56,3),new T.Vector3(3.5+dx*.07,h*.78,3+dz*.07),start]);
   mesh(new T.TubeGeometry(curve,18,.012,6,false),stem);
   const g=new T.PlaneGeometry(1,1,12,24),pos=g.attributes.position,uv=g.attributes.uv;
   for(let j=0;j<pos.count;j++){
    const t=uv.getY(j),v=uv.getX(j)*2-1,width=Math.pow(Math.sin(t*Math.PI),.8)*(.11+.025*Math.sin(i));
    pos.setXYZ(j,start.x+dx*length*t-dz*v*width,
     start.y+.27*Math.sin(t*Math.PI)-.20*t*t+.075*v*v*Math.sin(t*Math.PI),
     start.z+dz*length*t+dx*v*width);
   }
   g.computeVertexNormals();mesh(g,foliage);
  }
 }else{
  for(let i=0;i<8;i++){const x=3.5+Math.cos(i*2.4)*.45,z=3+Math.sin(i*2.4)*.35;rod([3.5,.5,3],[x,1.4+i*.1,z],.025,teal);const leaf=ball(mat(0x355d51),x,1.4+i*.1,z,.16,.44,.06);leaf.rotation.z=i*.8;}mesh(geometry.cylinder,wood,3.5,.3,3,.38,.6,.38);
 }
 {
  // Onset breathes; afterglow keeps settled surfaces under slowly changing daylight.
  const overlay=new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,
   extensions:{derivatives:true},uniforms:{time:{value:0},alpha:{value:0},relief:{value:after?0:.16},settled:{value:after?1:0}},
   vertexShader:`
    uniform float time,relief; varying vec3 place,surfaceNormal; varying vec2 tex;
    void main(){
     tex=uv;vec3 world=(modelMatrix*vec4(position,1.)).xyz;place=world;
     surfaceNormal=normalize(mat3(modelMatrix)*normal);
     float breath=.5+.5*sin(world.x*.51+world.z*.37+world.y*.6-time*.85);
     float edge=pow(max(0.,sin(uv.x*3.14159)*sin(uv.y*3.14159)),.65);
     // Keep the material behind mounted window trim and below furniture feet.
     float clearance=surfaceNormal.y>.5||(world.z<-8.7&&surfaceNormal.z>.5)?.12:1.;
     vec3 p=position+normal*relief*edge*(.25+breath)*clearance;
     gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);
    }`,
   fragmentShader:`
    precision highp float;
    uniform float time,alpha,settled; varying vec3 place,surfaceNormal; varying vec2 tex;
    void main(){
     vec3 p=place;float t=time*.42;
     float field=sin(p.x*.52+p.z*.38+sin(p.y*.55)-t)
       +.38*sin(p.y*.82-p.z*.44+sin(p.x*.4)+t*.73);
     // Low-frequency normals keep highlights broad; material grain never swims.
     float height=field*(.17+.16*alpha)*(1.-settled);
     vec3 baseN=normalize(surfaceNormal),dx=dFdx(place),dy=dFdy(place);
     vec3 tx=cross(dy,baseN),ty=cross(baseN,dx);
     float det=dot(dx,tx);
     vec3 grad=(tx*dFdx(height)+ty*dFdy(height))*sign(det)/max(abs(det),.000001);
     vec3 n=normalize(baseN-grad),v=normalize(cameraPosition-place);
     vec3 lamp=vec3(4.5,2.7,0.)-place,windowLight=vec3(3.5,4.2,-7.8)-place;
     vec3 l=normalize(lamp),w=normalize(windowLight);
     float warm=3.6/(1.+dot(lamp,lamp)*.11),cool=2.8/(1.+dot(windowLight,windowLight)*.065);
     float floorMask=step(.5,baseN.y),ceilingMask=step(.5,-baseN.y);
     float board=floor((p.x+7.)/.48),across=fract((p.x+7.)/.48);
     float seed=fract(sin(board*127.1+31.7)*43758.5453);
     float along=fract((p.z+seed*3.6)/3.6);
     float seam=smoothstep(0.,.014,min(across,1.-across))
       *smoothstep(0.,.004,min(along,1.-along));
     float grainPhase=p.x*135.+sin(p.z*.8+seed*9.)*2.5+sin(p.x*19.)*.8;
     float grain=sin(grainPhase)*exp(-fwidth(grainPhase)*.6);
     float plaster=sin(p.x*53.+p.y*79.+p.z*67.)*sin(p.x*91.-p.y*47.+p.z*39.);
     vec3 timber=vec3(.24,.135,.073)*(.86+seed*.24+grain*.055)*mix(.52,1.,seam);
     vec3 albedo=mix(vec3(.37,.34,.3)*(1.+plaster*.012),timber,floorMask);
     albedo=mix(albedo,vec3(.43,.405,.36),ceilingMask);
     // Soft contact falloff seats furnishings and joins the room's boundaries.
     vec2 table=max(abs(p.xz-vec2(-2.1,-.5))-vec2(1.1,1.35),0.);
     vec2 sofa=max(abs(p.xz-vec2(-5.,-.8))-vec2(1.15,2.4),0.);
     vec2 cabinet=max(abs(p.xz-vec2(5.,-4.))-vec2(.95,.3),0.);
     float contact=1.-floorMask*max(.36*exp(-dot(table,table)*1.8),
       max(.5*exp(-dot(sofa,sofa)*3.),.48*exp(-dot(cabinet,cabinet)*5.)));
     float corner=min(7.-abs(p.x),min(9.-abs(p.z),min(p.y,7.-p.y)));
     // Distance to the OTHER planes, not to the surface being shaded.
     if(floorMask+ceilingMask>.5)corner=min(7.-abs(p.x),9.-abs(p.z));
     else if(abs(baseN.x)>.5)corner=min(9.-abs(p.z),min(p.y,7.-p.y));
     else corner=min(7.-abs(p.x),min(p.y,7.-p.y));
     float legContact=0.;
     for(int ix=0;ix<2;ix++)for(int iz=0;iz<2;iz++){
      vec2 foot=vec2(-3.1+float(ix)*2.,-1.6+float(iz)*2.2);
      legContact=max(legContact,exp(-dot(p.xz-foot,p.xz-foot)*45.));
     }
     contact*=1.-settled*floorMask*.45*legContact;
     contact*=mix(.72+.28*smoothstep(0.,.65,corner),.91+.09*smoothstep(0.,.9,corner),settled);
     vec3 illumination=vec3(.29,.31,.36)+vec3(1.,.7,.4)*warm*max(dot(n,l),0.);
     illumination+=vec3(.55,.75,1.)*cool*max(dot(n,w),0.);
     float gloss=mix(10.,34.,floorMask);
     float spec=warm*pow(max(dot(n,normalize(l+v)),0.),gloss);
     spec+=cool*pow(max(dot(n,normalize(w+v)),0.),gloss);
     float fresnel=pow(1.-max(dot(n,v),0.),3.);
     vec3 film=.5+.5*cos(vec3(.3,2.4,4.5)+field*1.4+fresnel*3.-t*.2);
     vec3 col=(albedo*illumination+mix(vec3(.9,.85,.76),film,.18)*spec*mix(.14,.025,settled))*contact;
     col+=film*fresnel*(.012+.024*alpha)*(1.-settled);
     // A broad, soft window-light patch moves with passing cloud, not the room.
     float sunPatch=exp(-pow((p.x-1.1-p.z*.20)/2.1,4.)-pow((p.z+3.8)/4.,4.));
     col+=albedo*vec3(.8,.62,.38)*sunPatch*floorMask*settled*(.7+.13*sin(time*.2));
     gl_FragColor=vec4(col,1.);
     #include <tonemapping_fragment>
     #include <colorspace_fragment>
    }`});
  materials.push(overlay);
  plane(18,7,overlay,-6.97,3.5,0,0,Math.PI/2);plane(18,7,overlay,6.97,3.5,0,0,-Math.PI/2);
  plane(5.5,7,overlay,-4.25,3.5,-8.82);
  for(const [x,y,w,h] of windowSurround)plane(w,h,overlay,x,y,-8.82);
  plane(3,2.5,overlay,0,5.75,-8.82);
  plane(after?14:13.8,after?18:17.8,overlay,0,.025,0,-Math.PI/2);plane(after?14:13.8,after?18:17.8,overlay,0,6.98,0,Math.PI/2);
  if(!after)motions.push(()=>{overlay.uniforms.alpha.value=Math.min(.95,.18+elapsed/22);});
 }
 if(after){
  // Leaf/stem and trim materials lose the metallic toy finish in the settled room.
  teal.color.set(0x455b32);teal.metalness=0;teal.roughness=.92;teal.emissiveIntensity=0;
  gold.color.set(0x8b795e);gold.metalness=.18;gold.roughness=.68;gold.emissiveIntensity=0;
  root.traverse(o=>{if(o.isMesh&&o.material?.color?.getHex()===0x355d51){o.material.roughness=.9;o.material.metalness=0;}});
 }
 dust(70,0xd9b689,7);
}
function passage(id){
 const rushing=id==='rush',returning=id==='return';bounds={x:4,zMin:rushing?-58:-25,zMax:10};entryZ=8;exitZ=rushing?-54:-22;
 if(id==='membrane'){
  F.membraneField(root,materials);
  portals.push({x:0,z:exitZ-1,width:3.5,target:'next'});
  return;
 }
 if(id==='geometry'){
  F.geometryField(root,materials);
  portals.push({x:0,z:exitZ-1,width:3.5,target:'next'});
  return;
 }
 if(rushing){
  F.rushField(root,materials);
  portals.push({x:0,z:exitZ-1,width:3.5,target:'next'});
  return;
 }
 if(id==='chrysanthemum'){
  ContinuousWorld.chrysanthemum(root,materials,camera);
  portals.push({x:0,z:exitZ-1,width:3.5,target:'next'});
  return;
 }
 if(returning){
  F.returnField(root,materials);
  portals.push({x:0,z:exitZ-1,width:3.5,target:'next'});
 }
}
function roomShell(w,l,h,palette=1){
 const skin=(w,h,x,y,z,rx=0,ry=0,depth=.65)=>F.panel(root,materials,{w,h,x,y,z,rx,ry,palette,depth});
 skin(w,l,0,-.12,0,-Math.PI/2,0,.13);skin(l,h,-w/2,h/2,0,0,Math.PI/2);skin(l,h,w/2,h/2,0,0,-Math.PI/2);skin(w,l,0,h,0,Math.PI/2);skin(w,h,0,h/2,l/2,0,Math.PI);
 const side=(w-4)/2;skin(side,h,-(w+4)/4,h/2,-l/2);skin(side,h,(w+4)/4,h/2,-l/2);skin(4,h-6,0,6+(h-6)/2,-l/2);
 opening(0,-l/2,4,6,'next');bounds={x:w/2-.65,zMin:-l/2+.2,zMax:l/2-.7};entryZ=l/2-3;exitZ=-l/2+1;
 for(const x of [-w/2+.25,w/2-.25])for(let z=-l/2+2;z<l/2;z+=6)F.growth(root,materials,motions,{x,z,height:h*.83,spread:1.5,palette,seed:z});
}
function waiting(){
 bounds={x:8.35,zMin:-13.8,zMax:13.3};entryZ=11;exitZ=-13;
 portals.push({x:0,z:-14,width:4,target:'next'});
 F.waitingField(root,materials);
 for(const x of [-7,7])solids.push({x,z:-1,w:1.6,d:14});
 being('jester',-2.8,0,-4,1.3,GeometricBeings.createWaitingUsher);
}
function cathedral(id){
 bounds={x:22,zMin:-27,zMax:23};entryZ=id==='cathedral'?19:9;exitZ=id==='cathedral'?-23:-11;
 if(id==='cathedral'){
  scene.fog.density=.006;F.cathedralField(root,materials);
  for(const x of [-13,13])for(const z of [-20,-10,0,10,20])solids.push({x,z,w:1.9,d:1.9});
  portals.push({x:0,z:-25,width:9,target:'next'});
  for(const [x,z,target] of [[-22,-6,'workshop'],[-22,9,'garden'],[22,-6,'clinical'],[22,9,'void']])portals.push({x,z,width:5,target});
  being('elf',-3,0,-16,1);being('elf',3,0,-16,1);return;
 }
 if(id==='contact'){
  scene.fog.density=.006;F.contactField(root,materials);
  for(const x of [-13,13])for(const z of [-20,-10,0,10,20])solids.push({x,z,w:1.9,d:1.9});
  portals.push({x:0,z:-25,width:9,target:'next'});
  for(const [x,z,target] of [[-22,-6,'workshop'],[-22,9,'garden'],[22,-6,'clinical'],[22,9,'void']])portals.push({x,z,width:5,target});
  being('elf',-2.9,0,-4,1.25,GeometricBeings.createContactBeing);being('elf',2.9,0,-4,1.25,GeometricBeings.createContactBeing);
  being('elf',0,0,-6,1,GeometricBeings.createContactBeing);being('jester',-5,0,-6,1.4,GeometricBeings.createContactBeing);
  offering(0,2.05,-2,1.1);return;
 }
 // Download: continuous vault, floor and piers with a deep arched forward throat.
 scene.fog.density=.006;F.contactField(root,materials,true);
 for(const x of [-13,13])for(const z of [-20,-10,0,10,20])solids.push({x,z,w:1.9,d:1.9});
 portals.push({x:0,z:-25,width:9,target:'next'});
 for(const [x,z,target] of [[-22,-6,'workshop'],[-22,9,'garden'],[22,-6,'clinical'],[22,9,'void']])portals.push({x,z,width:5,target});
 // Solid, morphing interpreters grow from spreading bases instead of dotted skeletons.
 being('elf',-2.9,0,-4,1.25,GeometricBeings.createContactBeing);being('elf',2.9,0,-4,1.25,GeometricBeings.createContactBeing);
 being('elf',0,0,-6,1,GeometricBeings.createContactBeing);being('jester',-5,0,-6,1.4,GeometricBeings.createContactBeing);
 offering(0,2.05,-2,1.1);visibleLanguage();dust(320,0xf1c5a1,26);
}
function workshop(){
 // Long lateral production wings; retain the original central passage distance.
 F.workshopShell(root,materials);
 opening(0,-14,4,6,'next');bounds={x:10.35,zMin:-13.8,zMax:13.3};entryZ=11;exitZ=-13;
 F.workshopDetails(root,materials,motions);
 for(const x of [-7,7])for(const z of [-9,-1,7])solids.push({x,z,w:4.8,d:5.8});
 being('elf',-2.6,0,-3,1.25);being('elf',2.6,0,-3,1.25);being('elf',0,0,-6,1.1);being('elf',-5,0,3,.9);being('elf',5,0,3,.9);offering(0,2,-2,1.15);visibleLanguage();dust();
}
function garden(){
 bounds={x:13,zMin:-20,zMax:17};entryZ=13;exitZ=-17;scene.background=new T.Color(0x1d2438);scene.fog=new T.FogExp2(0x393048,.018);
 F.gardenGround(root,materials);
 for(const x of [-14,-8,8,14])F.growth(root,materials,motions,{x,z:-23,height:14,spread:7,palette:3,seed:x,organic:true});
 for(let i=0;i<18;i++){
  const side=i%2?-1:1,z=14-Math.floor(i/2)*4,x=side*(7+Math.sin(i*6)*2);F.growth(root,materials,motions,{x,z,height:6+(i%4),spread:4.5,palette:i%3===0?4:2,seed:i*1.7,organic:true});
 }
 for(let i=0;i<28;i++){const x=(i%2?1:-1)*(3.7+(i%7)*.9),z=14-Math.floor(i/7)*8;F.growth(root,materials,motions,{x,z,height:.7+(i%3)*.3,spread:1.5,palette:4,seed:i,organic:true});}
 const details=F.gardenDetails(root,materials,motions);details.traverse(o=>{if(o.isMesh)o.userData.evidence=[keys.garden,keys.breathing];});
 solids.push({x:8,z:-1,w:4.8,d:5.2},{x:8,z:3.1,w:2,d:2.6});
 being('mother',0,0,-4.8,1.15,GeometricBeings.createContactBeing);opening(0,-19,5,8,'next');dust(300,0xf4c8e5,20);
}
function clinical(){
 bounds={x:9.35,zMin:-13.8,zMax:13.3};entryZ=11;exitZ=-13;
 portals.push({x:0,z:-14,width:4,target:'next'});
 F.clinicalField(root,materials);
 for(const x of [-8,8])solids.push({x,z:-3,w:2,d:18});
 being('mantis',0,0,-2.8,1.35,GeometricBeings.createClinicalBeing);dust(100,0xb2eddb,12);
}
function voidSpace(){
 bounds={x:18,zMin:-23,zMax:18};entryZ=8;exitZ=-19;
 // Sparse luminous folds occupy depth, without a floor, ring or star sprites.
 const m=new T.ShaderMaterial({side:T.BackSide,uniforms:{time:{value:0}},
 vertexShader:'varying vec3 voidWorld;void main(){voidWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(voidWorld,1.);}',
 fragmentShader:`precision highp float;uniform float time;varying vec3 voidWorld;
 float hash(vec3 p){p=fract(p*.3183099+vec3(.13,.27,.41));p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
 float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
 float folds(vec3 p){float h=0.,w=.56;for(int j=0;j<4;j++){h+=w*noise(p);p=p.yzx*2.13+vec3(3.1,1.7,4.2);w*=.46;}return h;}
 float weave(vec3 p){return dot(sin(p),cos(p.yzx));}
 void main(){
  vec3 ro=cameraPosition,rd=normalize(voidWorld-ro),col=vec3(.0005,.0007,.0015);float transmission=1.;
  for(int i=0;i<96;i++){
   float distance=1.+float(i)*.6;vec3 p=ro+rd*distance;
   vec3 q=p*.095+vec3(0.,-time*.037,time*.021);
   q+=vec3(folds(q.zxy+time*.026),folds(q.yzx+4.7),folds(q+9.2)) * 2.8;
   // Nested porous sheets have a shaded body, fine ribs and openings through it.
   vec3 v=q*2.2;float inner=weave(v*2.7+vec3(0.,time*.12,1.7));
   float sheet=weave(v)+inner*.18;
   float pores=smoothstep(.16,.62,abs(inner));
   float rib=exp(-pow((abs(inner)-.65)*5.,2.));
   float lace=.5+.5*sin(weave(v*6.3)*3.+inner*4.);
   float veil=exp(-sheet*sheet*26.)*(.16+.84*pores);
   // Unequal drifting depth islands, not a radial wall enclosing the viewer.
   vec3 drift=p+vec3(2.8*sin(p.z*.11+time*.18),2.*sin(p.x*.13-time*.21),2.4*cos(p.y*.15+time*.16));
   vec3 nearFold=(drift-vec3(-12.,8.,-10.))/vec3(6.,4.,8.);
   vec3 deepFold=(drift-vec3(14.,-5.,-24.))/vec3(10.,5.,7.);
   vec3 farFold=(drift-vec3(-6.,15.,-40.))/vec3(8.,4.,6.);
   float islands=max(exp(-dot(nearFold,nearFold)),max(exp(-dot(deepFold,deepFold)),exp(-dot(farFold,farFold))*.65));
   float cloudMask=smoothstep(.035,.6,islands)*smoothstep(.3,.59,folds(q*.65+vec3(8.,2.,4.)));
   float density=veil*cloudMask*.19*smoothstep(1.,9.,distance);
   vec3 normal=normalize(cos(v)*cos(v.yzx)-sin(v.zxy)*sin(v)+vec3(.001));
   float light=.16+.84*pow(abs(dot(normal,normalize(vec3(-.5,.8,.3)))),3.);
   float edge=pow(1.-abs(dot(normal,rd)),3.);
   vec3 body=mix(vec3(.025,.07,.12),vec3(.19,.36,.31),light);
   vec3 ribs=mix(vec3(.12,.23,.48),vec3(.62,.42,.19),.5+.5*sin(v.z+inner-time*.14));
   vec3 radiance=body*(.28+light)+ribs*rib*(.35+lace*.65)+vec3(.12,.23,.3)*edge*.28;
   col+=transmission*density*radiance*exp(-distance*.012);
   transmission*=exp(-density*1.8);
  }
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const field=new T.Mesh(new T.BoxGeometry(180,180,180),m);field.frustumCulled=false;root.add(field);materials.push(m);
}
let interactionCount=0;
function being(kind,x,y,z,size,create=GeometricBeings.create){
 const evidence=keys[{elf:'elves',jester:'jester',mother:'mother',mantis:'mantis'}[kind]];
 const actor=create(kind,x,y,z,size,root,materials,motions,evidence,actors.length*.9);
 actors.push(actor);entities.push(kind);return actor;
}
function offering(x,y,z,size,parent=root){
 return GeometricBeings.offering(x,y,z,size,parent,materials,motions,[keys.elves,keys.language,'geometry|Hyper-dimensional objects','geometry|Dimensional Layering & Space-Folding']);
}
function visibleLanguage(){
 const g=F.language(root,materials,motions);
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=[keys.language,'phase|The Download / Lesson'];});
}
function animateBeings(t){for(const a of actors){const near=camera.position.distanceTo(a.g.position)<8;
 if(entered&&near&&!a.engaged){a.engaged=true;interactionCount++;}
 const attentive=a.engaged?1:0,w=Math.sin(t*.65+a.seed);
 a.body.position.y=w*(a.kind==='mother'?.035:.055);a.body.rotation.y=Math.max(-.35,Math.min(.35,Math.atan2(camera.position.x-a.g.position.x,camera.position.z-a.g.position.z)))*attentive;
 a.body.rotation.x=a.kind==='mantis'?.06+attentive*.08+Math.sin(t*.4)*.025:0;
 for(const j of a.joints){j.o.rotation.x=Math.sin(t*.8+a.seed+j.side)*.12-attentive*.13;j.o.rotation.z=j.side*(j.mother?-.12+w*.05:j.mantis?.04+w*.06:.08+w*.1);}
 }}
function updateUI(){
 const branch=!!branches[stage.id];$('step').textContent=branch?'AN OPTIONAL PATH':`${String(routeIndex+1).padStart(2,'0')} / ${route.length} · ${stage.id==='afterglow'?'RETURNED':'THE PASSAGE'}`;
 $('sceneName').textContent=stage.name;$('sceneHint').textContent=stage.hint;
 $('pace').textContent=`Paced journey: ${paced?'on':'off'}`;$('pace').setAttribute('aria-pressed',String(paced));
 $('pause').textContent=paused?'Continue':'Pause';$('pause').setAttribute('aria-pressed',String(paused));
 $('motion').textContent=`Reduced motion: ${reduced?'on':'off'}`;$('motion').setAttribute('aria-pressed',String(reduced));
 $('next').textContent=branch?'Back to the dome →':stage.id==='afterglow'?'Travel again ↺':stage.id==='contact'?'Receive the forms →':'Move onward →';$('next').disabled=paused;
 $('branchPaths').hidden=stage.id!=='cathedral';$('restart').hidden=!entered;
 $('stateText').textContent=paused?'Journey paused':branch?'Return whenever you wish':stage.id==='afterglow'?'Journey complete':paced?(reduced?'Still views · timed passage':'Carried gently forward'):'Explore at your own pace';
 document.body.classList.toggle('paused',paused);
}
function changeStage(s){stage=s;const idx=route.indexOf(s);if(idx>=0)routeIndex=idx;build(s);if(!visited.includes(s.id))visited.push(s.id);$('paths').hidden=true;$('pathsToggle').setAttribute('aria-expanded','false');updateUI();}
function go(s){if(transition||!entered||paused||$('evidence').open)return;input.clear();lastMovement=performance.now();transition={to:s,time:0,switched:false};}
function onward(){if(stage.id==='afterglow'){restart();return;}go(branches[stage.id]?route[6]:route[Math.min(routeIndex+1,route.length-1)]);}
function begin(){lastMovement=performance.now();entered=true;paced=$('autoStart').checked;$('welcome').hidden=true;$('hud').hidden=false;elapsed=0;visited=['onset'];updateUI();$('world').focus({preventScroll:true});}
function restart(){lastMovement=performance.now();transition=null;manualUntil=0;drag=null;$('veil').style.opacity='0';input.clear();entered=false;paused=false;visited=[];interactionCount=0;routeIndex=0;changeStage(route[0]);$('welcome').hidden=false;$('hud').hidden=true;updateUI();$('begin').focus();}
function togglePause(){if(!entered)return;syncMovement();paused=!paused;input.clear();updateUI();}
function manual(){manualUntil=performance.now()+2000;if(paced){paced=false;updateUI();}}
// Navigation measures actual held wall time, independent of capped animation
// deltas and GPU-delayed RAF timestamps. Flush the OLD input state at events,
// so neither a late release loses time nor a fresh press inherits an idle gap.
// RAF can be withheld for seconds by a slow compositor even while native
// input and timer tasks run. Pump held navigation independently, without GL
// calls, so controls/observers see incremental motion during a pending frame.
// All callers share one monotonic clock: no duplicate or discarded held time.
// Demand-driven: one timer at most, and no repeating work once input stops.
function scheduleMovement(){
 if(movementTimer!==null||!input.size||!entered||paused||transition||$('evidence').open||document.hidden)return;
 movementTimer=setTimeout(()=>{movementTimer=null;syncMovement();scheduleMovement();},16);
}
function syncMovement(){
 const now=performance.now(),dt=Math.max(0,(now-lastMovement)/1000);lastMovement=now;
 if(entered&&!paused&&!transition&&!$('evidence').open&&!document.hidden){
  move(dt);if(!camera.position.equals(drawnPosition))drawInvalidated=true;
 }
}
function move(dt){
 let f=Number(input.has('forward'))-Number(input.has('back')),r=Number(input.has('right'))-Number(input.has('left'));
 if(!f&&!r)return;manual();const norm=Math.hypot(f,r);f/=norm;r/=norm;const steps=Math.max(1,Math.ceil(dt/.05)),speed=(stage.id==='cathedral'?5:3.2)*dt/steps;
 // Keep collisions/portal crossings reliable even when a software-rendered frame is slow.
 for(let step=0;step<steps;step++){
  const ox=camera.position.x,oz=camera.position.z;
  camera.position.x+=(-Math.sin(yaw)*f+Math.cos(yaw)*r)*speed;camera.position.z+=(-Math.cos(yaw)*f-Math.sin(yaw)*r)*speed;
  for(const b of solids)if(Math.abs(camera.position.x-b.x)<b.w/2+.2&&Math.abs(camera.position.z-b.z)<b.d/2+.2){camera.position.x=ox;camera.position.z=oz;break;}
  checkPortals();camera.position.x=T.MathUtils.clamp(camera.position.x,-bounds.x,bounds.x);camera.position.z=T.MathUtils.clamp(camera.position.z,bounds.zMin,bounds.zMax);if(transition)break;
 }
}
function checkPortals(){
 if(stage.id==='afterglow')return;
 for(const p of portals){if(p.target!=='next'&&Math.abs(camera.position.x-p.x)<1.1&&Math.abs(camera.position.z-p.z)<p.width/2-.25){go(branches[p.target]);return;}}
 if(camera.position.z<exitZ&&Math.abs(camera.position.x)<(stage.id==='cathedral'?4:1.75))onward();
}
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function link(url,label,cls=''){try{const u=new URL(url,'https://www.reddit.com');if(!['https:','http:'].includes(u.protocol))return esc(label);return `<a class="${cls}" href="${esc(u.href)}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a>`;}catch{return esc(label);}}
function sourceHTML(ref){const s=sourceMap.get(ref.source_key);if(!s)return `<p>Unresolved citation: ${esc(ref.source_key)}</p>`;return `<details class="source"><summary>${esc(s.author)} · ${esc(s.year)}</summary><p>${esc(s.work)}</p><small>${esc(s.type)}</small><p>${esc(ref.detail)}</p>${s.note?`<p>${esc(s.note)}</p>`:''}${s.url?link(s.url,'Open source'):''}</details>`;}
function dossier(key,i){
 const n=nodeMap.get(key);if(!n)return `<p>Evidence entry unavailable: ${esc(key)}</p>`;
 const fields=['description','appearance','behavior','communication','emotional_tone','message_or_purpose','what_happens_there'];
 return `<details class="node" ${i===0?'open':''}><summary>${esc(n.name)} <small>${esc(n.kind)}</small></summary>${fields.filter(f=>n[f]).map(f=>`${f==='description'?'':`<h4>${esc(f.replaceAll('_',' '))}</h4>`}<p>${esc(n[f])}</p>`).join('')}<h4>Citations</h4>${(n.sources||[]).map(sourceHTML).join('')}<h4>Tagged report trail</h4><small>${n.report_count==null?'Outside the tagged vocabulary; not a count of zero.':`${Number(n.report_count).toLocaleString()} tagged reports in this archive; not population prevalence.`} Only dates, tags and mention order are stored locally. Open originals for context.</small>${(n.report_ids||[]).slice(0,8).map(id=>{const r=D.reports[id];return `${link(`https://www.reddit.com/r/${encodeURIComponent(r.sub)}/comments/${encodeURIComponent(id)}/`,`${id} · r/${r.sub}`,'report-link')}<small>${esc(r.seq.map(k=>k.split('|')[1]).join(' → '))}</small>`;}).join('')||'<p>No report tags indexed for this entry.</p>'}<h4>Credited depiction candidates</h4>${(n.depiction_ids||[]).slice(0,5).map(id=>{const a=D.depictions[id];return a?link(a.permalink,`${a.title} · u/${a.author||'[unknown]'} · ${a.kind}`,'art-link'):'';}).join('')||'<p>No depiction links indexed for this entry.</p>'}</details>`;
}
function openEvidence(){syncMovement();input.clear();$('evidenceTitle').textContent=stage.name;$('evidenceContent').innerHTML=`<p>Procedural surfaces, architecture, gestures and forms in this scene are interpreted from the entries below. Individual character designs are not witness likenesses. ${['onset','afterglow','return'].includes(stage.id)?'The familiar room and its furnishings are an editorial grounding device, not a universal reported setting.':''}</p>${window.fidelityHTML?window.fidelityHTML(stage.id):''}${pointedAt&&currentEvidence.includes(pointedAt)?'<p class="pointed">You pointed at:</p>'+dossier(pointedAt):''}${currentEvidence.filter(k=>k!==pointedAt).map(dossier).join('')}`;$('evidence').showModal();}
function closeEvidence(){lastMovement=performance.now();$('evidence').close();$('sources').focus();}
$('begin').onclick=begin;$('next').onclick=onward;$('restart').onclick=restart;$('pause').onclick=togglePause;
$('pace').onclick=()=>{paced=!paced;elapsed=0;entryZ=camera.position.z;updateUI();};
$('motion').onclick=()=>{reduced=!reduced;updateUI();};
$('sources').onclick=openEvidence;$('closeEvidence').onclick=closeEvidence;
$('pathsToggle').onclick=()=>{$('paths').hidden=!$('paths').hidden;$('pathsToggle').setAttribute('aria-expanded',String(!$('paths').hidden));};
document.querySelectorAll('[data-branch]').forEach(b=>b.onclick=()=>go(branches[b.dataset.branch]));
const keyMoves={w:'forward',ArrowUp:'forward',s:'back',ArrowDown:'back',a:'left',ArrowLeft:'left',d:'right',ArrowRight:'right'};
addEventListener('keydown',e=>{
 if($('evidence').open)return;if(e.target.matches('input,button,a,summary')&&['Enter',' '].includes(e.key))return;
 const key=e.key.length===1?e.key.toLowerCase():e.key;if(keyMoves[key]&&entered){e.preventDefault();syncMovement();if(!paused){input.add(keyMoves[key]);scheduleMovement();}}
 if(e.repeat)return;if(key==='e'){e.preventDefault();openEvidence();}else if(key===' '&&entered){e.preventDefault();togglePause();}else if(key==='Escape'&&entered&&!paused)togglePause();
});
addEventListener('keyup',e=>{syncMovement();input.delete(keyMoves[e.key.length===1?e.key.toLowerCase():e.key]);});
addEventListener('blur',()=>{syncMovement();input.clear();});
document.addEventListener('visibilitychange',()=>{input.clear();lastMovement=lastFrame=performance.now();if(document.hidden&&entered&&!paused){paused=true;updateUI();}});
let drag=null;
$('world').addEventListener('pointerdown',e=>{if(!entered||paused||transition)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY};$('world').setPointerCapture(e.pointerId);});
$('world').addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId||paused)return;syncMovement();yaw-=(e.clientX-drag.x)*.0035;pitch=T.MathUtils.clamp(pitch-(e.clientY-drag.y)*.003,-1.25,1.25);drag.x=e.clientX;drag.y=e.clientY;camera.rotation.set(pitch,yaw,0);if(!camera.quaternion.equals(drawnRotation))drawInvalidated=true;});
$('world').addEventListener('pointerup',e=>{if(drag&&Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)<7){const ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);const hit=ray.intersectObjects(actors.map(a=>a.g),true)[0];if(hit){let o=hit.object;while(o&&!o.userData.entityKey)o=o.parent;const a=actors.find(a=>a.g===o);if(a){a.engaged=true;interactionCount++;drawInvalidated=true;pointedAt=a.evidence||null;$('sceneHint').textContent=(a.kind==='mantis'?'The examiner inclines its head and extends its forelimbs.':a.kind==='mother'?'The presence turns toward you, her arms held open.':'The figure turns toward you and lifts its changing forms.')+(pointedAt?' Drawn from the atlas entry \u201c'+pointedAt.split('|').slice(1).join('|')+'\u201d \u2014 open Sources for the reports behind it.':'');}}}drag=null;});
$('world').addEventListener('pointercancel',()=>{drag=null;});
document.querySelectorAll('[data-move]').forEach(b=>{b.addEventListener('pointerdown',e=>{e.preventDefault();if(paused)return;syncMovement();b.setPointerCapture(e.pointerId);input.add(b.dataset.move);scheduleMovement();});for(const name of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(name,()=>{syncMovement();input.delete(b.dataset.move);});});
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);composite.resize();drawInvalidated=true;}
addEventListener('resize',resize);
function detailUI(){$('detail').textContent=`Detail: ${F.quality==='high'?'high':'lower'}`;$('detail').setAttribute('aria-pressed',String(F.quality==='high'));}
$('detail').addEventListener('click',()=>{F.setQuality(F.quality==='high'?'low':'high');prTarget=Math.min(devicePixelRatio,F.quality==='high'?1.5:.85);for(const k in prBad)delete prBad[k];for(const k in prMemo)delete prMemo[k];setPR(prTarget);frameEma=16;for(const m of materials)if(m.uniforms.detail)m.uniforms.detail.value=F.quality==='high'?6:4;resize();detailUI();});detailUI();
$('world').addEventListener('webglcontextlost',e=>{e.preventDefault();paused=true;$('failure').hidden=false;});
function frame(now){
 requestAnimationFrame(frame);const dt=Math.min((now-lastFrame)/1000,1);lastFrame=now;
 syncMovement();
 const active=entered&&!paused&&!$('evidence').open&&!document.hidden;
 if(active){
  if(transition){transition.time+=dt;const duration=reduced?.6:1.3,half=duration/2;$('veil').style.opacity=String(transition.time<half?transition.time/half:Math.max(0,1-(transition.time-half)/half));
   if(transition.time>=half&&!transition.switched){transition.switched=true;changeStage(transition.to);}if(transition.time>=duration){transition=null;$('veil').style.opacity='0';}
  }else{elapsed+=dt;if(paced&&stage.duration&&performance.now()>manualUntil){
    if(!reduced){const target=entryZ+(exitZ-entryZ)*Math.min(1,elapsed/stage.duration);camera.position.z=Math.min(camera.position.z,target);}
    if(elapsed>=stage.duration)onward();
   }
  }
 }
 if(!paused&&!$('evidence').open&&!document.hidden){if(!reduced){animTime+=dt;for(const m of materials)m.uniforms.time.value=animTime;for(const fn of motions)fn(animTime);}animateBeings(animTime);}
 const progress=branches[stage.id]?(routeIndex+.5)/route.length:(routeIndex+(stage.duration?Math.min(1,elapsed/stage.duration):1))/route.length;$('progress').firstElementChild.style.width=`${progress*100}%`;
 const age=animTime-stageAnimStart,signal=signalStages.includes(stage.id);
 const grain=signal?(stage.id==='onset'?.025+.12*Math.min(1,age/18):stage.id==='return'?.045+.12*Math.min(1,age/20):.035):0;
 const seam=signal&&!reduced&&transition?Math.sin(Math.PI*Math.min(1,transition.time/1.3))*.65:0;
 // Reduced views can be temporally still while walking, looking or engaging a
 // being. Compare against the submitted pose so changes survive an in-flight
 // frame. Scene builds and resize/detail changes invalidate explicitly.
 const frozen=paused||$('evidence').open||document.hidden||reduced;
 if(!frozen||!lastDrawFrozen||!camera.position.equals(drawnPosition)||!camera.quaternion.equals(drawnRotation)||interactionCount!==drawnInteractions)drawInvalidated=true;
 // Capture tools (Playwright, ?capture=1) keep at most one GPU frame in flight so a
 // screenshot is a settled frame. For a person watching, that fence serialises CPU
 // and GPU and drops a 60 Hz display to ~10 fps (measured Sep 6 on an RTX 4070:
 // 7-12 renders/s while the loop ran at 60), so it is off unless automation asks.
 let gpuReady=true;
 if(renderFence){
  gpuReady=renderGL.clientWaitSync(renderFence,0,0)!==renderGL.TIMEOUT_EXPIRED;
  if(gpuReady){renderGL.deleteSync(renderFence);renderFence=null;}
 }
 if(drawInvalidated&&gpuReady){
  composite.render(scene,camera,['onset','afterglow'].includes(stage.id)?.16:stage.id==='void'?.3:.8,animTime,grain+seam*.25,seam);renderReady=true;frames++;
  renderedAnimTime=animTime;
  drawnPosition.copy(camera.position);drawnRotation.copy(camera.quaternion);drawnInteractions=interactionCount;
  if(GPU_FENCE&&renderGL.fenceSync){renderFence=renderGL.fenceSync(renderGL.SYNC_GPU_COMMANDS_COMPLETE,0);renderGL.flush();}
  drawInvalidated=false;
  if(!GPU_FENCE&&!frozen){
   frameEma=frameEma*.9+dt*100;prCooldown-=dt;
   if(prCooldown<=0){
    // 60 Hz sits at 16.7 ms; step down once frames run long enough to drop below ~52 fps,
    // step back up only while the display rate is actually being held.
    if(frameEma>19.5&&prNow>.6){prBad[stage.id]=Math.min(prBad[stage.id]??9,prNow);setPR(Math.max(.6,prNow-(frameEma>40?.5:.25)));prMemo[stage.id]=prNow;prCooldown=.6;frameEma=16;}
    else if(frameEma<17.2&&prNow<prTarget){const next=Math.min(prTarget,prNow+.25);
     // a level that failed on this stage is never retried: no oscillation between two scales
     if(next>=(prBad[stage.id]??9)){prCooldown=4;}else{setPR(next);prMemo[stage.id]=prNow;prCooldown=2.5;frameEma=16;}}
   }
  }
 }
 lastDrawFrozen=frozen;
}
window.journeyDiagnostics=()=>({stage:stage.id,routeIndex,entered,paused,paced,reduced,elapsed,animTime,transition:!!transition,renderReady,renderPending:drawInvalidated||!!renderFence,renderedAnimTime,frames,position:camera.position.toArray(),yaw,pitch,visited:[...visited],entities:[...entities],interactions:interactionCount,evidence:[...currentEvidence],missingEvidence:currentEvidence.filter(k=>!nodeMap.has(k)),sourceCount:currentEvidence.reduce((n,k)=>n+(nodeMap.get(k)?.sources?.length||0),0),portals:portals.map(p=>({...p})),detail:F.quality,pixelRatio:prNow,frameEma:Math.round(frameEma*10)/10,prCooldown:Math.round(prCooldown*100)/100,prBad:{...prBad},prMemo:{...prMemo},drawCalls:composite.calls,triangles:composite.triangles,geometries:renderer.info.memory.geometries,actors:actors.map(a=>{const p=a.g.localToWorld(new T.Vector3(0,a.kind==='mantis'?3:2,0)).project(camera);return {kind:a.kind,engaged:a.engaged,joints:a.joints.length,arm:a.joints[0]?.o.rotation.x,evidence:a.evidence,screen:[(p.x+1)*innerWidth/2,(1-p.y)*innerHeight/2]};}),uncitedMeshes:(()=>{let n=0;root.traverse(o=>{if((o.isMesh||o.isPoints)&&!o.userData.evidence?.length)n++;});return n;})()});
changeStage(route[0]);updateUI();requestAnimationFrame(frame);
})();
