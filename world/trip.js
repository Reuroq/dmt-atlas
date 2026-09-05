/* Through: all imagery is procedural interpretation. Scene keys resolve into the local evidence bundle. */
(() => {
'use strict';
const $ = id => document.getElementById(id), D = window.WORLD_DATA;
if (!window.THREE || !D) { $('failure').hidden = false; return; }
const T = THREE, nodeMap = new Map(D.nodes.map(n => [n.key,n])), sourceMap = new Map(D.sources.map(s => [s.key,s]));
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
 {id:'chrysanthemum',name:'The chrysanthemum',hint:'An orange-gold opening, folding into itself. Move through its centre.',duration:22,evidence:['phase|The Chrysanthemum',keys.flower]},
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
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5)); renderer.setSize(innerWidth,innerHeight);
renderer.outputColorSpace=T.SRGBColorSpace; renderer.toneMapping=T.ACESFilmicToneMapping; renderer.toneMappingExposure=1.2;
const scene=new T.Scene(), camera=new T.PerspectiveCamera(68,innerWidth/innerHeight,.06,180);
camera.rotation.order='YXZ';
let root, stage=route[0], routeIndex=0, entered=false, paused=false, paced=true;
let reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let elapsed=0, animTime=0, yaw=0, pitch=0, transition=null, renderReady=false, frames=0;
let actors=[], motions=[], materials=[], portals=[], solids=[], visited=[], entities=[], currentEvidence=[];
let bounds={x:7,zMin:-11,zMax:8}, entryZ=7, exitZ=-10, lastFrame=performance.now(), manualUntil=0;
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
 const palettes=[['#130e2a','#228d9a','#dc8e39'],['#260b36','#d24d6b','#eabd67'],['#142b3b','#35bfa7','#f5d39a'],['#211042','#4b60c0','#e6bd76'],['#523024','#946d3b','#d4ac6b']];
 const c=palettes[palette];
 const m=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{time:{value:0},scale:{value:scale},strength:{value:strength},a:{value:new T.Color(c[0])},b:{value:new T.Color(c[1])},c:{value:new T.Color(c[2])}},
 vertexShader:`varying vec2 vUv; varying vec3 vP; void main(){vUv=uv;vP=position;vec4 transformed=vec4(position,1.);
 #ifdef USE_INSTANCING
 transformed=instanceMatrix*transformed;
 #endif
 gl_Position=projectionMatrix*modelViewMatrix*transformed;}`,
 fragmentShader:`precision highp float;varying vec2 vUv;varying vec3 vP;uniform float time,scale,strength;uniform vec3 a,b,c;
 float band(float d,float w){return 1.-smoothstep(w,w+.018,abs(d));}
 void main(){vec2 p=vUv*scale; p+=.022*strength*vec2(sin(p.y*3.+time*.36),cos(p.x*3.-time*.27));
 vec2 cell=fract(p)-.5;float checker=mod(floor(p.x)+floor(p.y),2.);vec2 q=mat2(.707,-.707,.707,.707)*cell;
 float diamond=abs(cell.x)+abs(cell.y);float r=length(cell);float angle=atan(cell.y,cell.x);
 float flower=.24+.055*cos(angle*8.+time*.12*strength);float petals=band(r-flower,.015);
 float frame=band(diamond-.46,.018)+band(diamond-.38,.007);float star=band(abs(q.x)+abs(q.y)-.27,.012);
 float inner=band(r-.087,.012);vec3 col=mix(a,b,.14+checker*.15);col=mix(col,b,.44*petals);col=mix(col,c,clamp(frame*.7+star*.66+inner*.8,0.,.9));
 vec2 fine=fract(p*5.)-.5;float bead=1.-smoothstep(.025,.09,length(fine));col+=c*bead*.22;col+=b*.13*(.5+.5*cos(diamond*36.));
 col*=.83+.17*cos(cell.x*6.)*cos(cell.y*6.);gl_FragColor=vec4(col,1.);}`});
 materials.push(m);return m;
}
function plane(w,h,material,x,y,z,rx=0,ry=0,parent=root){const o=mesh(new T.PlaneGeometry(w,h,1,1),material,x,y,z,1,1,1,parent);o.rotation.set(rx,ry,0);return o;}
function light(color,intensity,x,y,z,dist=80){const l=new T.PointLight(color,intensity,dist,1.3);l.position.set(x,y,z);root.add(l);return l;}
function arch(x,z,width,height,material=gold,ry=0){const g=new T.Group();g.position.set(x,0,z);g.rotation.y=ry;root.add(g);const r=width/2,shoulder=height-r;rod([-r,0,0],[-r,shoulder,0],.16,material,g);rod([r,0,0],[r,shoulder,0],.16,material,g);const pts=[];for(let i=0;i<=24;i++){const a=i/24*Math.PI;pts.push([Math.cos(a)*r,shoulder+Math.sin(a)*r,0]);}tube(pts,.16,material,g);return g;}
function opening(x,z,width,height,target,ry=0,color=0x85eadb){const a=arch(x,z,width,height,gold,ry);const glow=new T.MeshBasicMaterial({color,transparent:true,opacity:.075,side:T.DoubleSide,depthWrite:false});plane(width,height,glow,0,height/2,-.25,0,0,a);if(target)portals.push({x,z,width,target});return a;}
function dust(count=250,color=0xd9c49e,spread=24){const coords=[];for(let i=0;i<count;i++)coords.push(Math.sin(i*83.17)*spread,1+(Math.sin(i*13.3)*.5+.5)*spread,Math.cos(i*39.31)*spread);const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(coords,3));const p=new T.Points(g,new T.PointsMaterial({color,size:.035,transparent:true,opacity:.6,depthWrite:false}));root.add(p);motions.push(t=>{p.rotation.y=t*.007;});}
function disposeScene(){if(!root)return;const gs=new Set(),ms=new Set();root.traverse(o=>{if(o.geometry&&!Object.values(geometry).includes(o.geometry))gs.add(o.geometry);if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>ms.add(m));});gs.forEach(g=>g.dispose());ms.forEach(m=>m.dispose());scene.remove(root);}
function build(s){
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
 currentEvidence=[...new Set(s.evidence)];root.userData.evidence=currentEvidence;
 root.traverse(o=>{if(o.isMesh||o.isPoints)o.userData.evidence=o.userData.evidence||currentEvidence;});
 camera.position.set(0,1.7,entryZ);yaw=0;pitch=s.id==='cathedral'?.12:0;camera.rotation.set(pitch,yaw,0);elapsed=0;renderReady=false;
 for(const m of materials)m.uniforms.time.value=animTime;for(const fn of motions)fn(animTime);animateBeings(animTime);
}
function ordinary(after=false){
 bounds={x:6.6,zMin:-8.5,zMax:8};entryZ=6.5;exitZ=-7.7;scene.background=new T.Color(0x181c2b);scene.fog.density=.018;
 const wall=mat(after?0x686375:0x454554,0),wood=mat(0x493b36,.05),cloth=mat(0x646376,0),floor=mat(0x433f40,.1);
 plane(14,18,floor,0,0,0,-Math.PI/2);plane(18,7,wall,-7,3.5,0,0,Math.PI/2);plane(18,7,wall,7,3.5,0,0,-Math.PI/2);plane(14,7,wall,0,3.5,9,0,Math.PI);plane(14,18,wall,0,7,0,Math.PI/2);
 box(wall,-4.25,3.5,-9,5.5,7,.3);box(wall,4.25,3.5,-9,5.5,7,.3);box(wall,0,5.75,-9,3,2.5,.3);
 opening(0,-8.95,3,4.5,'next',0,0xfed394);plane(3,4.5,new T.MeshBasicMaterial({color:after?0xada7a3:0x9d7958}),0,2.25,-10);
 const rug=patterned(4,5,0);plane(7,8,rug,0,.012,1,-Math.PI/2);
 box(cloth,-5,.62,-.8,2.6,1.1,5);box(cloth,-6,1.5,-.8,.7,1.3,5);box(cloth,-5,1.2,-3.25,2.7,.9,.45);box(cloth,-5,1.2,1.65,2.7,.9,.45);
 for(let i=0;i<3;i++)box(mat(0x999183,0),-4.95,1.24,-2.2+i*1.4,1.8,.28,1.3);
 box(wood,-2.1,.7,-.5,2.5,.15,3);for(const x of [-3.1,-1.1])for(const z of [-1.6,.6])rod([x,0,z],[x,.7,z],.07,wood);solids.push({x:-2.1,z:-.5,w:3,d:3.5},{x:-5,z:-.8,w:3,d:5.7},{x:5,z:-4,w:2,d:.65},{x:4.5,z:0,w:.25,d:.25},{x:3.5,z:3,w:.8,d:.8});
 box(ivory,-2.1,.83,-.8,.6,.12,.85);ball(ivory,-1.5,.94,.1,.12,.17,.12);
 box(wood,5,.85,-4,2,1.7,.65);for(let i=0;i<9;i++)box(mat([0x816763,0x536f71,0xaa9061][i%3]),4.25+i*.17,1.99,-4,.12,.6+(i%3)*.06,.4);
 rod([4.5,0,0],[4.5,3,0],.045,gold);mesh(new T.CylinderGeometry(.58,.83,.8,32,1,true),mat(0xf5d4a0,0,0xffb553,.55),4.5,3,0);light(0xffc48b,23,4.5,2.7,0,15);
 box(wood,3.5,3.7,-8.76,3.1,3,.1);plane(2.8,2.7,new T.MeshBasicMaterial({color:after?0xb6bcd0:0x596879}),3.5,3.7,-8.68);box(wood,3.5,3.7,-8.58,.065,2.8,.06);box(wood,3.5,3.7,-8.58,2.8,.065,.06);
 for(let i=0;i<8;i++){const x=3.5+Math.cos(i*2.4)*.45,z=3+Math.sin(i*2.4)*.35;rod([3.5,.5,3],[x,1.4+i*.1,z],.025,teal);const leaf=ball(mat(0x355d51),x,1.4+i*.1,z,.16,.44,.06);leaf.rotation.z=i*.8;}mesh(geometry.cylinder,wood,3.5,.3,3,.38,.6,.38);
 if(!after){const overlay=patterned(1,8);overlay.uniforms.alpha={value:0};overlay.fragmentShader=overlay.fragmentShader.replace('uniform float time,scale,strength;','uniform float time,scale,strength,alpha;').replace('vec4(col,1.)','vec4(col,alpha)');overlay.transparent=true;overlay.depthWrite=false;plane(18,7,overlay,-6.97,3.5,0,0,Math.PI/2);plane(18,7,overlay,6.97,3.5,0,0,-Math.PI/2);plane(5.5,7,overlay,-4.25,3.5,-8.82);plane(5.5,7,overlay,4.25,3.5,-8.82);motions.push(()=>{overlay.uniforms.alpha.value=Math.min(.76,elapsed/22);});}
 dust(70,0xd9b689,7);
}
function passage(id){
 const rushing=id==='rush',returning=id==='return';bounds={x:4,zMin:rushing?-58:-25,zMax:10};entryZ=8;exitZ=rushing?-54:-22;
 scene.fog.density=.006;const p=patterned(id==='chrysanthemum'?1:0,rushing?32:18);
 const tunnel=mesh(new T.CylinderGeometry(6.5,6.5,rushing?84:52,64,12,true),p,0,3,rushing?-28:-12);tunnel.rotation.x=Math.PI/2;
 plane(10,rushing?84:52,patterned(3,22),0,-.15,rushing?-28:-12,-Math.PI/2);
 for(let i=0;i<(rushing?14:8);i++){
  const z=8-i*5.5;
  const g=torus(6.32,.07,gold,0,3,z);g.scale.x=1.01;
  for(let k=0;k<8;k++){const a=k*Math.PI/4;const f=mesh(geometry.ico,k%2?teal:rose,Math.cos(a)*6.1,3+Math.sin(a)*6.1,z,.24,.24,.45);f.rotation.z=a;}
 }
 if(['chrysanthemum','geometry','return'].includes(id)){
  const petalMat=patterned(id==='chrysanthemum'?1:2,2);
  const petals=new T.InstancedMesh(geometry.sphere,petalMat,192);root.add(petals);const dummy=new T.Object3D();
  function shape(t){for(let i=0;i<192;i++){const layer=Math.floor(i/32),a=i%32/32*Math.PI*2+layer*.19+t*.014;const r=4.3+(layer%3)*.65;dummy.position.set(Math.sin(a)*r,3+Math.cos(a)*r,-2-layer*3.1);dummy.rotation.set(.13*Math.sin(a),.17*Math.cos(a),-a+Math.sin(t*.16+layer)*.06);dummy.scale.set(.39,1.85,.37);dummy.updateMatrix();petals.setMatrixAt(i,dummy.matrix);}petals.instanceMatrix.needsUpdate=true;}
  shape(0);motions.push(shape);
 }
 if(id==='membrane'){
  const membrane=new T.ShaderMaterial({transparent:true,side:T.DoubleSide,depthWrite:false,uniforms:{time:{value:0}},vertexShader:'varying vec2 p;void main(){p=uv*2.-1.;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'precision highp float;varying vec2 p;uniform float time;void main(){float r=length(p);float a=atan(p.y,p.x);float wave=sin(r*48.-time*.7+sin(a*12.)*1.2);vec3 col=mix(vec3(.08,.33,.36),vec3(.94,.61,.28),wave*.5+.5);float hole=smoothstep(.13,.27,r);float edge=1.-smoothstep(.9,1.,r);gl_FragColor=vec4(col,.68*hole*edge);}'});materials.push(membrane);plane(12.5,12.5,membrane,0,3,-9);torus(6.1,.16,gold,0,3,-9);
 }
 opening(0,exitZ-1,3.5,6,'next');
 if(returning){const m=new T.MeshBasicMaterial({color:0xb6a196});plane(3,4.5,m,0,2.25,exitZ-2);motions.push(()=>{const f=1-Math.min(.75,elapsed/26);p.uniforms.strength.value=f;});}
 dust(260,0xf2c58b,rushing?30:18);
}
function roomShell(w,l,h,palette=1){
 plane(w,l,patterned(0,l/3),0,0,0,-Math.PI/2);plane(l,h,patterned(palette,l/2),-w/2,h/2,0,0,Math.PI/2);plane(l,h,patterned(palette,l/2),w/2,h/2,0,0,-Math.PI/2);plane(w,l,patterned(palette,l/3),0,h,0,Math.PI/2);plane(w,h,patterned(palette,w/2),0,h/2,l/2,0,Math.PI);
 const side=(w-4)/2;plane(side,h,patterned(palette,side/2),-(w+4)/4,h/2,-l/2);plane(side,h,patterned(palette,side/2),(w+4)/4,h/2,-l/2);plane(4,h-6,patterned(palette,2),0,6+(h-6)/2,-l/2);
 opening(0,-l/2,4,6,'next');bounds={x:w/2-.65,zMin:-l/2+.2,zMax:l/2-.7};entryZ=l/2-3;exitZ=-l/2+1;
 for(const x of [-w/2+.25,w/2-.25])for(let z=-l/2+2;z<l/2;z+=4){rod([x,.2,z],[x,h-.3,z],.13,gold);ball(teal,x,h-.8,z,.24);}
}
function waiting(){
 roomShell(18,28,10,1);
 for(const x of [-7,7]){box(rose,x,.65,-1,1.6,1.1,14);solids.push({x,z:-1,w:1.6,d:14});for(let z=-6;z<7;z+=2)box(gold,x,1.25,z,1.55,.08,1.7);}
 // A ribbed canopy makes the threshold enclosed, with a clear central opening.
 for(let z=-11;z<12;z+=4){const a=arch(0,z,16,10);a.children.forEach(o=>o.material=gold);}
 for(let i=0;i<5;i++){const r=torus(1.2+i*.65,.09,gold,0,9.1,-3,Math.PI/2);r.rotation.z=i*.12;}
 being('jester',-2.4,0,-7,1.3);dust(180,0xdba8eb,13);
}
function cathedral(id){
 bounds={x:22,zMin:-27,zMax:23};entryZ=id==='cathedral'?19:9;exitZ=id==='cathedral'?-23:-11;
 scene.fog.density=.006;const wall=patterned(3,15);plane(48,58,patterned(0,22),0,0,-3,-Math.PI/2);
 const dome=mesh(new T.SphereGeometry(30,80,40,0,Math.PI*2,0,Math.PI/2),patterned(1,24),0,0,-3);dome.scale.y=.94;
 for(let i=0;i<16;i++){const a=i/16*Math.PI*2;const pts=[];for(let j=0;j<=24;j++){const p=j/24*Math.PI/2;pts.push([Math.cos(a)*29.7*Math.cos(p),28.1*Math.sin(p),-3+Math.sin(a)*29.7*Math.cos(p)]);}tube(pts,.065,gold);}
 for(const x of [-13,13])for(const z of [-20,-10,0,10,20]){
  solids.push({x,z,w:1.9,d:1.9});
  mesh(geometry.cylinder,patterned(2,7),x,7,z,.65,14,.65);mesh(geometry.cylinder,gold,x,.25,z,.95,.5,.95);mesh(geometry.cylinder,gold,x,13.8,z,1,.65,1);torus(.78,.12,gold,x,3,z,Math.PI/2);torus(.78,.12,gold,x,10,z,Math.PI/2);
 }
 for(const z of [-20,-10,0,10,20])arch(0,z,26,26,gold);
 plane(19,13,wall,-14.5,6.5,-28);plane(19,13,wall,14.5,6.5,-28);plane(10,4,wall,0,15,-28);opening(0,-25,9,13,'next');
 // Four real side openings; crossing their planes enters an optional interpretation.
 const doors=[[-22,-6,'workshop',0x78e6c0],[-22,9,'garden',0xf1bccc],[22,-6,'clinical',0xa4ded8],[22,9,'void',0x737cd0]];
 for(const [x,z,target,color] of doors){opening(x,z,5,8,target,Math.PI/2,color);const sideMat=patterned(target==='clinical'?2:3,5);plane(10,12,sideMat,x,6,z-7.5,0,Math.PI/2);plane(5,4,sideMat,x,10,z,0,Math.PI/2);}
 for(let i=0;i<4;i++)torus(2.4+i*.5,.08,gold,0,23-i*.6,-3,Math.PI/2);
 const jewel=mesh(geometry.ico,teal,0,21,-3,.8,1.4,.8);motions.push(t=>{jewel.rotation.y=t*.15;});
 if(id==='cathedral'){being('elf',-3,0,-16,1);being('elf',3,0,-16,1);}
 else{being('elf',-2.9,0,-4,1.25);being('elf',2.9,0,-4,1.25);being('elf',0,0,-6,1);being('jester',-5,0,-6,1.4);offering(0,2.05,-2,1.1);}
 if(id==='download')visibleLanguage();dust(320,0xf1c5a1,26);
}
function workshop(){
 roomShell(22,28,12,2);const fabric=patterned(1,5);
 for(const x of [-7,7])for(let z=-9;z<=7;z+=8){const g=torus(2,.16,gold,x,4,z,0,Math.PI/2);const core=mesh(geometry.ico,fabric,x,4,z,.8);motions.push(t=>{g.rotation.x=t*.12;core.rotation.set(t*.2,t*.15,0);});}
 being('elf',-2.6,0,-3,1.25);being('elf',2.6,0,-3,1.25);being('elf',0,0,-6,1.1);being('elf',-5,0,3,.9);being('elf',5,0,3,.9);offering(0,2,-2,1.15);visibleLanguage();dust();
}
function garden(){
 bounds={x:13,zMin:-20,zMax:17};entryZ=13;exitZ=-17;scene.background=new T.Color(0x1d2438);scene.fog=new T.FogExp2(0x393048,.018);
 plane(36,48,patterned(2,16),0,-.04,-3,-Math.PI/2);const canopy=mesh(new T.SphereGeometry(26,48,24),patterned(3,15),0,2,-4);canopy.material.side=T.BackSide;
 for(let i=0;i<18;i++){
  const side=i%2?-1:1,z=14-Math.floor(i/2)*4,x=side*(7+Math.sin(i*6)*2);const h=5+(i%4);tube([[x,0,z],[x+side*.5,h*.5,z],[x-side,h,z-.3]],.16,gold);
  for(let k=0;k<4;k++){const a=k*1.7+i;const leaf=ball(k%2?teal:rose,x+Math.cos(a)*1.25,h-1+Math.sin(a),z+Math.sin(a)*.8,.6,1.8,.12);leaf.rotation.z=-a;}
 }
 for(let i=0;i<70;i++){const x=(i%2?1:-1)*(3.5+(i%7)*1.1),z=14-Math.floor(i/7)*3;const f=ball(i%3?rose:ivory,x,.25,z,.23,.4,.23);f.rotation.z=i;}
 being('mother',0,0,-6,1.9);opening(0,-19,5,8,'next');dust(300,0xf4c8e5,20);
}
function clinical(){
 roomShell(20,28,10,2);const porcelain=mat(0x98bfb7,.45,0x478386,.08);
 for(const x of [-8,8]){box(porcelain,x,2,-3,2,4,18);solids.push({x,z:-3,w:2,d:18});for(let z=-10;z<7;z+=3)box(teal,x>0?6.96:-6.96,2.5,z,.03,2,1.4);}
 for(const z of [-9,0,9]){torus(4,.16,ivory,0,8,z,Math.PI/2);light(0xa8eee3,30,0,7,z);}
 being('mantis',0,0,-5,1.35);dust(100,0xb2eddb,12);
}
function voidSpace(){bounds={x:18,zMin:-23,zMax:18};entryZ=8;exitZ=-19;scene.fog=new T.FogExp2(0x04060d,.04);dust(45,0x535d94,35);const m=new T.MeshBasicMaterial({color:0x374268,transparent:true,opacity:.15});torus(9,.012,m,0,2,-25);}
let interactionCount=0;
function being(kind,x,y,z,size){
 const g=new T.Group();g.position.set(x,y,z);g.scale.setScalar(size);root.add(g);
 const evidence=keys[{elf:'elves',jester:'jester',mother:'mother',mantis:'mantis'}[kind]];g.userData.entityKey=evidence;
 const body=new T.Group();g.add(body);const joints=[];
 const skin=kind==='mother'?mat(0xffecd0,.45,0xffcba1,.65):kind==='mantis'?mat(0x84b898,.7,0x3d755c,.18):kind==='jester'?ivory:teal;
 const eye=mat(0x071420,.72),shine=new T.MeshBasicMaterial({color:0xf5e9d7});
 if(kind==='mantis'){
  ball(skin,0,2.6,0,.34,1.25,.32,body);ball(gold,0,1.7,-.2,.46,.65,.35,body);
  const shape=new T.Shape();shape.moveTo(-.82,.32);shape.quadraticCurveTo(0,.58,.82,.32);shape.lineTo(.15,-.56);shape.quadraticCurveTo(0,-.68,-.15,-.56);shape.closePath();
  const head=mesh(new T.ExtrudeGeometry(shape,{depth:.25,bevelEnabled:true,bevelSize:.08,bevelThickness:.08,bevelSegments:2,steps:1}),skin,0,4,0,1,1,1,body);
  for(const s of [-1,1]){
   const e=ball(eye,s*.47,4.12,.27,.25,.34,.18,body);e.rotation.z=-s*.4;ball(shine,s*.49,4.23,.425,.04,.065,.025,body);
   tube([[s*.35,4.38,.05],[s*.58,4.98,-.1],[s*.94,5.35,.06]],.018,gold,body);
   rod([s*.24,1.9,0],[s*.85,.85,-.45],.12,skin,body);ball(gold,s*.85,.85,-.45,.16,.16,.16,body);rod([s*.85,.85,-.45],[s*1.08,.05,.6],.075,skin,body);
   const arm=new T.Group();arm.position.set(s*.3,3.35,0);body.add(arm);rod([0,0,0],[s*1.05,-.75,.3],.11,skin,arm);ball(gold,s*1.05,-.75,.3,.16,.16,.16,arm);rod([s*1.05,-.75,.3],[s*.5,-1.08,1.35],.075,skin,arm);
   for(let k=0;k<3;k++)tube([[s*.5,-1.08,1.35],[s*(.5+k*.09),-1.3,1.6],[s*(.32+k*.11),-1.42,1.8]],.027,skin,arm);
   joints.push({o:arm,side:s,mantis:true});
   rod([s*.3,2.4,-.12],[s*1.25,1.9,-.5],.065,skin,body);rod([s*1.25,1.9,-.5],[s*1.55,1,.2],.04,skin,body);
  }
 }else{
  const mother=kind==='mother',jester=kind==='jester',h=mother?1.7:1.2,headY=mother?2.75:2;
  if(mother){mesh(new T.ConeGeometry(.86,2.35,40),mat(0xeee3cd,.45,0xe9bb9a,.32),0,1.18,0,1,1,.64,body);ball(skin,0,2,0,.43,.65,.25,body);const halo=torus(.88,.035,gold,0,headY,-.17,0,0,body);halo.scale.y=1.18;
   for(let i=0;i<12;i++){const a=i/12*Math.PI*2;rod([Math.sin(a)*.95,headY+Math.cos(a)*1.1,-.19],[Math.sin(a)*1.11,headY+Math.cos(a)*1.28,-.19],.014,gold,body);}
  }else{
   ball(jester?rose:skin,0,h,0,.45,.58,.27,body);
   for(const s of [-1,1]){rod([s*.2,.85,0],[s*.26,.3,.04],.15,jester?(s<0?rose:teal):dark,body);ball(gold,s*.26,.13,.19,.18,.13,.35,body);}
   for(let i=0;i<12;i++){const a=i/12*Math.PI*2;mesh(geometry.cone,i%2?gold:ivory,Math.cos(a)*.32,1.67,Math.sin(a)*.23,.1,.28,.1,body).rotation.z=Math.cos(a)*.65;}
   for(let i=0;i<5;i++)mesh(geometry.ico,gold,0,.92+i*.14,.28,.075,.075,.03,body);
  }
  ball(skin,0,headY,0,mother?.28:.37,mother?.4:.4,.29,body);
  for(const s of [-1,1]){
   if(!mother&&!jester){const ear=mesh(geometry.cone,gold,s*.43,headY+.06,0,.14,.4,.08,body);ear.rotation.z=-s*.95;}
   const e=ball(eye,s*(mother?.105:.145),headY+.045,.263,mother?.045:.085,mother?.025:.107,.043,body);e.rotation.z=s*.13;ball(shine,s*.14,headY+.08,.301,.018,.02,.012,body);
   if(jester){mesh(geometry.cone,rose,s*.15,headY-.1,.291,.058,.18,.008,body).rotation.z=Math.PI;rod([s*.07,headY+.21,.255],[s*.23,headY+.23,.23],.023,dark,body);}
   const arm=new T.Group();arm.position.set(s*(mother?.35:.36),mother?2.2:1.5,0);body.add(arm);
   const elbow=[s*(mother?.6:.25),mother?-.34:-.4,.12],hand=[s*(mother?1.03:.25),mother?-.2:-.3,mother?.6:.64];
   rod([0,0,0],elbow,mother?.105:.11,jester?(s<0?teal:rose):skin,arm);ball(gold,...elbow,.12,.12,.12,arm);rod(elbow,hand,.075,skin,arm);ball(skin,...hand,.12,.12,.14,arm);
   for(let k=0;k<4;k++)rod([hand[0]+(k-1.5)*.05,hand[1],hand[2]],[hand[0]+(k-1.5)*.065,hand[1]+.04,hand[2]+.21],.021,skin,arm);
   joints.push({o:arm,side:s,mother});
  }
  ball(skin,0,headY-.035,.293,.055,.075,.065,body);
  tube([[-.12,headY-.15,.257],[0,headY-.19,.29],[.12,headY-.15,.257]],.014,jester?rose:gold,body);
  if(jester){for(let k=-1;k<=1;k++){tube([[k*.16,2.3,0],[k*.47,2.78,-.02],[k*.69,2.57,.08]],.125,k===0?teal:rose,body);ball(gold,k*.69,2.57,.08,.115,.115,.115,body);}ball(rose,0,headY-.02,.345,.075,.075,.075,body);}
  else if(!mother){for(let k=0;k<7;k++){const a=k/7*Math.PI;mesh(geometry.ico,gold,Math.cos(a)*.29,headY+.3+Math.sin(a)*.14,0,.1,.16,.1,body);}for(let k=0;k<8;k++){const a=k*.8;mesh(geometry.ico,rose,Math.cos(a)*.36,1.02+(k%3)*.18,.23,.07,.12,.05,body);}offering(0,1.45,.85,.28,g);}
 }
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=[evidence];});
 const actor={kind,g,body,joints,engaged:false,evidence,seed:actors.length*.9};actors.push(actor);entities.push(kind);
 return actor;
}
function offering(x,y,z,size,parent=root){
 const g=new T.Group();g.position.set(x,y,z);g.scale.setScalar(size);parent.add(g);
 const knot=mesh(new T.TorusKnotGeometry(.46,.095,72,8,2,3),gold,0,0,0,1,1,1,g);const shell=mesh(geometry.ico,teal,0,0,0,.31,.31,.31,g);
 for(let i=0;i<6;i++){const a=i*Math.PI/3;const ring=torus(.28,.045,i%2?rose:gold,Math.cos(a)*.6,Math.sin(a)*.6,0,0,i*Math.PI/6,g);ring.rotation.z=a;}
 motions.push(t=>{g.rotation.y=t*.24;g.rotation.z=Math.sin(t*.21)*.2;knot.rotation.x=t*.3;shell.scale.setScalar(.28+Math.sin(t*.8)*.045);});
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=[keys.elves,keys.language];});
}
function visibleLanguage(){
 const g=new T.Group();root.add(g);
 for(let i=0;i<32;i++){
  const a=i*.73,r=1.1+(i%5)*.58,x=Math.cos(a)*r,y=3.4+Math.sin(a)*r*.55,z=-2-Math.floor(i/8)*1.4;
  const letter=new T.Group();letter.position.set(x,y,z);g.add(letter);
  rod([-.12,-.2,0],[.12,.2,0],.026,gold,letter);rod([-.15,.15,0],[.16,.09,0],.026,teal,letter);if(i%2)torus(.13,.025,rose,.12,-.07,0,0,0,letter);else rod([.12,-.2,0],[.12,.2,0],.02,teal,letter);
  motions.push(t=>{letter.rotation.y=Math.sin(t*.22+i)*.55;letter.position.y=y+Math.sin(t*.4+i)*.13;});
 }
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
function go(s){if(transition||!entered||paused||$('evidence').open)return;input.clear();transition={to:s,time:0,switched:false};}
function onward(){if(stage.id==='afterglow'){restart();return;}go(branches[stage.id]?route[6]:route[Math.min(routeIndex+1,route.length-1)]);}
function begin(){entered=true;paced=$('autoStart').checked;$('welcome').hidden=true;$('hud').hidden=false;elapsed=0;visited=['onset'];updateUI();$('world').focus({preventScroll:true});}
function restart(){transition=null;manualUntil=0;drag=null;$('veil').style.opacity='0';input.clear();entered=false;paused=false;visited=[];interactionCount=0;routeIndex=0;changeStage(route[0]);$('welcome').hidden=false;$('hud').hidden=true;updateUI();$('begin').focus();}
function togglePause(){if(!entered)return;paused=!paused;input.clear();updateUI();}
function manual(){manualUntil=performance.now()+2000;if(paced){paced=false;updateUI();}}
function move(dt){
 let f=Number(input.has('forward'))-Number(input.has('back')),r=Number(input.has('right'))-Number(input.has('left'));
 if(!f&&!r)return;manual();const norm=Math.hypot(f,r);f/=norm;r/=norm;const speed=(stage.id==='cathedral'?5:3.2)*dt;
 const ox=camera.position.x,oz=camera.position.z;
 camera.position.x+=(-Math.sin(yaw)*f+Math.cos(yaw)*r)*speed;camera.position.z+=(-Math.cos(yaw)*f-Math.sin(yaw)*r)*speed;
 for(const b of solids)if(Math.abs(camera.position.x-b.x)<b.w/2+.2&&Math.abs(camera.position.z-b.z)<b.d/2+.2){camera.position.x=ox;camera.position.z=oz;break;}
 checkPortals();camera.position.x=T.MathUtils.clamp(camera.position.x,-bounds.x,bounds.x);camera.position.z=T.MathUtils.clamp(camera.position.z,bounds.zMin,bounds.zMax);
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
function openEvidence(){input.clear();$('evidenceTitle').textContent=stage.name;$('evidenceContent').innerHTML=`<p>Procedural surfaces, architecture, gestures and forms in this scene are interpreted from the entries below. Individual character designs are not witness likenesses. ${['onset','afterglow'].includes(stage.id)?'The familiar room and its furnishings are an editorial grounding device, not a universal reported setting.':''}</p>${currentEvidence.map(dossier).join('')}`;$('evidence').showModal();}
function closeEvidence(){$('evidence').close();$('sources').focus();}
$('begin').onclick=begin;$('next').onclick=onward;$('restart').onclick=restart;$('pause').onclick=togglePause;
$('pace').onclick=()=>{paced=!paced;elapsed=0;entryZ=camera.position.z;updateUI();};
$('motion').onclick=()=>{reduced=!reduced;updateUI();};
$('sources').onclick=openEvidence;$('closeEvidence').onclick=closeEvidence;
$('pathsToggle').onclick=()=>{$('paths').hidden=!$('paths').hidden;$('pathsToggle').setAttribute('aria-expanded',String(!$('paths').hidden));};
document.querySelectorAll('[data-branch]').forEach(b=>b.onclick=()=>go(branches[b.dataset.branch]));
const keyMoves={w:'forward',ArrowUp:'forward',s:'back',ArrowDown:'back',a:'left',ArrowLeft:'left',d:'right',ArrowRight:'right'};
addEventListener('keydown',e=>{
 if($('evidence').open)return;if(e.target.matches('input,button,a,summary')&&['Enter',' '].includes(e.key))return;
 const key=e.key.length===1?e.key.toLowerCase():e.key;if(keyMoves[key]&&entered){e.preventDefault();if(!paused)input.add(keyMoves[key]);}
 if(e.repeat)return;if(key==='e'){e.preventDefault();openEvidence();}else if(key===' '&&entered){e.preventDefault();togglePause();}else if(key==='Escape'&&entered&&!paused)togglePause();
});
addEventListener('keyup',e=>{input.delete(keyMoves[e.key.length===1?e.key.toLowerCase():e.key]);});
addEventListener('blur',()=>{input.clear();});
document.addEventListener('visibilitychange',()=>{input.clear();lastFrame=performance.now();if(document.hidden&&entered&&!paused){paused=true;updateUI();}});
let drag=null;
$('world').addEventListener('pointerdown',e=>{if(!entered||paused||transition)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY};$('world').setPointerCapture(e.pointerId);});
$('world').addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId||paused)return;yaw-=(e.clientX-drag.x)*.0035;pitch=T.MathUtils.clamp(pitch-(e.clientY-drag.y)*.003,-1.25,1.25);drag.x=e.clientX;drag.y=e.clientY;camera.rotation.set(pitch,yaw,0);});
$('world').addEventListener('pointerup',e=>{if(drag&&Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)<7){const ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);const hit=ray.intersectObjects(actors.map(a=>a.g),true)[0];if(hit){let o=hit.object;while(o&&!o.userData.entityKey)o=o.parent;const a=actors.find(a=>a.g===o);if(a){a.engaged=true;interactionCount++;$('sceneHint').textContent=a.kind==='mantis'?'The examiner inclines its head and extends its forelimbs.':a.kind==='mother'?'The presence turns toward you, her arms held open.':'The figure turns toward you and lifts its changing forms.';}}}drag=null;});
$('world').addEventListener('pointercancel',()=>{drag=null;});
document.querySelectorAll('[data-move]').forEach(b=>{b.addEventListener('pointerdown',e=>{e.preventDefault();if(paused)return;b.setPointerCapture(e.pointerId);input.add(b.dataset.move);});for(const name of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(name,()=>input.delete(b.dataset.move));});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
$('world').addEventListener('webglcontextlost',e=>{e.preventDefault();paused=true;$('failure').hidden=false;});
function frame(now){
 requestAnimationFrame(frame);const dt=Math.min((now-lastFrame)/1000,.05);lastFrame=now;
 const active=entered&&!paused&&!$('evidence').open&&!document.hidden;
 if(active){
  if(transition){transition.time+=dt;const duration=reduced?.6:1.3,half=duration/2;$('veil').style.opacity=String(transition.time<half?transition.time/half:Math.max(0,1-(transition.time-half)/half));
   if(transition.time>=half&&!transition.switched){transition.switched=true;changeStage(transition.to);}if(transition.time>=duration){transition=null;$('veil').style.opacity='0';}
  }else{elapsed+=dt;move(dt);if(paced&&stage.duration&&performance.now()>manualUntil){
    if(!reduced){const target=entryZ+(exitZ-entryZ)*Math.min(1,elapsed/stage.duration);camera.position.z=Math.min(camera.position.z,target);}
    if(elapsed>=stage.duration)onward();
   }
  }
 }
 if(!paused&&!$('evidence').open&&!document.hidden){if(!reduced){animTime+=dt;for(const m of materials)m.uniforms.time.value=animTime;for(const fn of motions)fn(animTime);}animateBeings(animTime);}
 const progress=branches[stage.id]?(routeIndex+.5)/route.length:(routeIndex+(stage.duration?Math.min(1,elapsed/stage.duration):1))/route.length;$('progress').firstElementChild.style.width=`${progress*100}%`;
 renderer.render(scene,camera);renderReady=true;frames++;
}
window.journeyDiagnostics=()=>({stage:stage.id,routeIndex,entered,paused,paced,reduced,elapsed,animTime,transition:!!transition,renderReady,frames,position:camera.position.toArray(),yaw,pitch,visited:[...visited],entities:[...entities],interactions:interactionCount,evidence:[...currentEvidence],missingEvidence:currentEvidence.filter(k=>!nodeMap.has(k)),sourceCount:currentEvidence.reduce((n,k)=>n+(nodeMap.get(k)?.sources?.length||0),0),portals:portals.map(p=>({...p})),drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,geometries:renderer.info.memory.geometries,actors:actors.map(a=>{const p=a.g.localToWorld(new T.Vector3(0,a.kind==='mantis'?3:2,0)).project(camera);return {kind:a.kind,engaged:a.engaged,joints:a.joints.length,arm:a.joints[0]?.o.rotation.x,evidence:a.evidence,screen:[(p.x+1)*innerWidth/2,(1-p.y)*innerHeight/2]};}),uncitedMeshes:(()=>{let n=0;root.traverse(o=>{if((o.isMesh||o.isPoints)&&!o.userData.evidence?.length)n++;});return n;})()});
changeStage(route[0]);updateUI();requestAnimationFrame(frame);
})();
