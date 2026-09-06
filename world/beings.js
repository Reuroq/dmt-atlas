/* Articulated, geometry-built interpretations. All parts inherit explicit atlas evidence. */
(() => {
'use strict';
const T=THREE,F=FractalWorld,TAU=Math.PI*2,up=new T.Vector3(0,1,0);
const motifs=['geometry|Embedded Faces & the Pareidolia Cascade','geometry|Fractal lattices & jeweled tilings','geometry|Hyper-dimensional objects'];
// Small facets get a cheap luminous cut-crystal shader.
function crystalMaterial(palette,materials){
 const colors=[['#00ffb3','#ffe39a'],['#ff0765','#2ee9ff'],['#12ef79','#d6ff4c'],['#b24aff','#35ddff'],['#ff3aaa','#ffdd83']][palette];
 const m=new T.ShaderMaterial({uniforms:{time:{value:0},a:{value:new T.Color(colors[0])},b:{value:new T.Color(colors[1])}},vertexShader:`
 varying vec3 vN,vP,vView;uniform float time;
 void main(){vec3 p=position*(1.+.028*sin(position.y*5.+time*.6));vP=p;vec3 n=normal;vec4 transformed=vec4(p,1.);
 #ifdef USE_INSTANCING
 transformed=instanceMatrix*transformed;mat3 basis=mat3(instanceMatrix);n=basis*(n/vec3(dot(basis[0],basis[0]),dot(basis[1],basis[1]),dot(basis[2],basis[2])));
 transformed.xyz+=sin(transformed.yzx*5.+time*.4)*.018;
 #endif
 vN=normalize(normalMatrix*n);vec4 mv=modelViewMatrix*transformed;vView=mv.xyz;gl_Position=projectionMatrix*mv;}`,fragmentShader:`
 precision highp float;varying vec3 vN,vP,vView;uniform float time;uniform vec3 a,b;
 void main(){vec3 n=normalize(vN);float incidence=max(dot(n,normalize(vec3(-.5,.8,1.))),0.);
 float edge=pow(1.-abs(dot(n,normalize(-vView))),2.);float colour=.5+.5*sin(vP.y*4.+vP.x*3.+time*.17);
 vec3 col=mix(a,b,smoothstep(.6,.95,colour))*(.16+incidence*.4)+b*edge*.24;
 col+=vec3(.6,.85,1.)*pow(incidence,18.)*.09;gl_FragColor=vec4(col,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});m.userData.entity=true;materials.push(m);return m;
}
// Continuous bilateral contour engraving follows the face, with no repeated medallion cells.
function faceMaterial(palette,materials){
 const m=crystalMaterial(palette,materials);m.side=T.DoubleSide;
 m.vertexShader=`varying vec2 vUv;varying vec3 vN,vView;uniform float time;
 void main(){vUv=uv;vec3 p=position;p.z+=.008*sin(uv.y*19.+time*.4)*sin(uv.x*3.14159);
 vN=normalize(normalMatrix*normal);vec4 mv=modelViewMatrix*vec4(p,1.);vView=mv.xyz;gl_Position=projectionMatrix*mv;}`;
 m.fragmentShader=`precision highp float;varying vec2 vUv;varying vec3 vN,vView;uniform float time;uniform vec3 a,b;
 float line(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d),.0015),abs(d));}
 void main(){vec2 p=vUv*2.-1.;p.x=abs(p.x);float t=time*.13;
 float brow=p.y-.2-.22*sin(p.x*4.2);float cheek=p.x-(.22+.36*pow(abs(p.y+.08),.65));
 float contour=cheek+.045*sin(p.y*11.+sin(p.x*9.)+t);float engraving=0.;
 for(int i=0;i<4;i++){float k=pow(2.6,float(i));
 float ridge=sin(contour*k*19.+sin(brow*k*3.)*.65+t);
 engraving+=line(ridge,.06)/(1.+float(i)*1.8);}
 float bridge=line(p.x-.035-.035*cos(p.y*4.),.009);
 float eye=exp(-pow((p.x-.47)*4.,2.)-pow((p.y-.13)*8.,2.));
 float arch=line(brow,.014)+line(brow-.065,.006);vec3 n=normalize(vN);
 float lit=.25+.55*abs(dot(n,normalize(vec3(-.5,.8,1.))));
 vec3 enamel=mix(a,b,.3+.25*sin(p.y*6.+p.x*4.+t));
 vec3 col=enamel*(.12+lit*.16)+b*(engraving*.24+bridge*.55+arch*.33);
 col*=1.-eye*.75;col+=b*pow(1.-abs(dot(n,normalize(-vView))),3.)*.18;
 gl_FragColor=vec4(col,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`;return m;
}
function create(kind,x,y,z,size,root,materials,motions,evidence,seed){
 const g=new T.Group(),body=new T.Group();g.position.set(x,y,z);g.scale.setScalar(size);root.add(g);g.add(body);g.userData.entityKey=evidence;
 const joints=[],mantis=kind==='mantis',mother=kind==='mother',jester=kind==='jester';
 const palette=mantis?2:mother?4:jester?1:0;
 const skin=crystalMaterial(palette,materials),gold=crystalMaterial(mother?4:1,materials),light=crystalMaterial(mother?4:2,materials);
 const maskMat=faceMaterial(palette,materials);
 const crystal=new T.OctahedronGeometry(1,0),gem=new T.IcosahedronGeometry(1,0),dummy=new T.Object3D();
 const dark=new T.MeshBasicMaterial({color:mantis?0x011915:0x090119});
 function batch(parent,parts,material=skin,geo=crystal){
  const mesh=new T.InstancedMesh(geo,material,parts.length);mesh.frustumCulled=false;parent.add(mesh);
  parts.forEach((p,i)=>{dummy.position.set(...p.p);dummy.scale.set(...p.s);dummy.rotation.set(...(p.r||[0,0,0]));if(p.q)dummy.quaternion.copy(p.q);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);});return mesh;
 }
 function segment(parts,a,b,r,phase=0){
  const av=new T.Vector3(...a),bv=new T.Vector3(...b),v=bv.clone().sub(av),q=new T.Quaternion().setFromUnitVectors(up,v.clone().normalize());
  const n=F.quality==='high'?9:6;
  for(let i=0;i<n;i++){
   const f=(i+.5)/n,p=av.clone().lerp(bv,f),rr=r*(.7+.3*Math.sin(Math.PI*f));
   parts.push({p:p.toArray(),s:[rr,v.length()/n*.85,rr*.8],q});
   // Every articulated segment branches into smaller interlocking facets.
   for(let s=0;s<2;s++){
    const a=s/2*TAU+phase+i*.39,offset=new T.Vector3(Math.cos(a)*rr,0,Math.sin(a)*rr).applyQuaternion(q);
    parts.push({p:p.clone().add(offset).toArray(),s:[rr*.33,rr*.8,rr*.3],r:[a,f*3,phase+i*.4]});
   }
  }
 }
 function branch(parts,a,b,r,depth,phase){
  segment(parts,a,b,r,phase);if(depth===0)return;
  const v=new T.Vector3(...b).sub(new T.Vector3(...a));
  for(const s of [-1,1]){
   const end=new T.Vector3(...b).add(v.clone().multiplyScalar(.56).applyAxisAngle(new T.Vector3(0,0,1),s*.64));
   end.z+=Math.sin(phase+depth)*v.length()*.17;
   branch(parts,b,end.toArray(),r*.57,depth-1,phase+s*.6);
  }
 }
 // An open, jewelled rib cage surrounds a branching spine, not a solid toy torso.
 const ribs=[],spine=[],torsoY=mantis?2.35:1.65,torsoH=mantis?1.35:.93,torsoW=mantis?.29:mother?.48:.36;
 segment(spine,[0,torsoY-torsoH*.6,0],[0,torsoY+torsoH*.65,0],.12);
 for(let j=0;j<19;j++){
  const v=j/18,yy=torsoY+(v-.5)*torsoH,rr=torsoW*Math.pow(Math.sin(Math.PI*(v*.8+.1)),.6);
  for(let k=0;k<24;k++){
   const a=k/24*TAU+j*.09;
   ribs.push({p:[Math.cos(a)*rr,yy+.028*Math.cos(a*6),Math.sin(a)*rr*.62],s:[.045,.026,.034],r:[a,j*.12,a]});
  }
 }
 batch(body,ribs,skin);batch(body,spine,light);
 const legs=[];
 if(!mother){
  for(const s of [-1,1]){
   const hip=[s*.21,torsoY-torsoH*.45,0],knee=[s*(mantis?.55:.31),mantis?.63:.5,mantis?-.28:.08],foot=[s*(mantis?.85:.43),.06,.2];
   segment(legs,hip,knee,mantis?.095:.12,s);segment(legs,knee,foot,.07,s);
   branch(legs,foot,[s*(mantis?1.05:.56),.02,.48],.035,1,s);
  }
  batch(body,legs,skin);
 }
 // Geometric mantle: recursively ribbed, perforated surfaces flowing around empty space.
 if(mother){
  const mantle=[];
  for(let strand=0;strand<40;strand++){
   const a=strand/40*TAU;
   for(let j=0;j<28;j++){
    const v=j/27,rr=.3+1.12*v*v;
    mantle.push({p:[Math.cos(a)*rr,1.8-v*1.73,Math.sin(a)*rr*.54],s:[.035+v*.025,.069,.027],r:[a+v,strand*.2,v*4]});
   }
  }
  const skirt=batch(body,mantle,skin);motions.push(t=>{skirt.rotation.y=Math.sin(t*.16+seed)*.13;});
 }
 for(const s of [-1,1]){
  const arm=new T.Group();arm.position.set(s*(mantis?.29:mother?.44:.38),torsoY+torsoH*.32,0);body.add(arm);joints.push({o:arm,side:s,mantis,mother});
  const armParts=[],elbow=[s*(mantis?.84:mother?.75:.49),mantis?-.38:mother?-.12:-.26,mantis?.27:.16],hand=[s*(mantis?.49:mother?1.14:.55),mantis?-.91:mother?-.01:-.31,mantis?1.06:.62];
  segment(armParts,[0,0,0],elbow,mantis?.073:.09,s);segment(armParts,elbow,hand,mantis?.053:.065,s);
  if(mantis){
   for(let j=0;j<9;j++){
    const v=j/9,a=new T.Vector3(...elbow).lerp(new T.Vector3(...hand),v);
    branch(armParts,a.toArray(),[a.x-s*.15,a.y+.1,a.z+.08],.023,1,v);
   }
  }
  for(let f=0;f<(mantis?3:5);f++){
   const spread=(f-(mantis?1:2))*.055;
   branch(armParts,[hand[0]+spread,hand[1],hand[2]],[hand[0]+spread*1.8,hand[1]-.15,hand[2]+.25],.024,1,f);
  }
  batch(arm,armParts,light);
  if(!mantis&&!mother)offering(hand[0],hand[1]+.19,hand[2]+.13,.26,arm,materials,motions,[evidence,...motifs]);
 }
 // Elongated carved mask. Eye apertures are negative space, surrounded by fractured facets.
 const face=new T.Group(),faceY=mantis?3.76:mother?2.62:jester?2.8:2.63;
 face.position.set(0,faceY,mantis?.02:.03);body.add(face);
 const w=mantis?.76:mother?.43:.41,h=mantis?.4:mother?.68:.7;
 function maskPoint(u,v){
  const yy=v*h,xx=u*w;
  const nose=.17*Math.exp(-u*u*85.-(v+.05)*(v+.05)*4.);
  const sockets=.14*Math.exp(-Math.pow((Math.abs(u)-.47)*6.,2)-Math.pow((v-.12)*8.,2));
  const contour=mantis?.18*(1-Math.abs(u)):.2*(1-u*u);
  return new T.Vector3(xx,yy,contour+nose-sockets+.025*Math.cos(u*22)*Math.cos(v*15));
 }
 const pos=[],uv=[],idx=[],rows=48,cols=40;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const u=i/cols*2-1,v=j/rows*2-1,p=maskPoint(u,v);pos.push(...p.toArray());uv.push(i/cols,j/rows);
  if(i<cols&&j<rows){
   const almond=Math.pow((Math.abs(u)-.47)/.33,2)+Math.pow((v-.13)/.065,2);
   const inside=mantis?Math.abs(u)<(v+1)*.52&&v<.8:u*u+v*v<.98&&almond>1.;
   if(inside){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
  }
 }
 const faceGeo=new T.BufferGeometry();faceGeo.setAttribute('position',new T.Float32BufferAttribute(pos,3));faceGeo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));faceGeo.setIndex(idx);faceGeo.computeVertexNormals();
 const mask=new T.Mesh(faceGeo,maskMat);face.add(mask);
 const facets=[],eyes=[];
 for(const side of [-1,1])for(let track=0;track<9;track++)for(let j=0;j<28;j++){
  const v=(j+.5)/28*1.86-.93;
  const u=side*(.07+track*.083+Math.sin(v*3.7+track*.26)*.075),almond=Math.pow((Math.abs(u)-.47)/.35,2)+Math.pow((v-.13)/.085,2);
  if(mantis?(Math.abs(u)>(v+1)*.52||v>.8):(u*u+v*v>.94||almond<1.15))continue;
  const p=maskPoint(u,v);p.z+=.025;
  const taper=.65+.35*Math.sin((v+1)*Math.PI*.5);
  facets.push({p:p.toArray(),s:[.008*taper,.029*taper,.012],r:[v*.15,-u*.4,-side*Math.cos(v*3.7+track*.26)*.27]});
 }
 batch(face,facets,gold);
 if(mantis){
  const compound=[];
  for(const s of [-1,1])for(let j=0;j<12;j++)for(let i=0;i<18;i++){
   const a=(i/17-.5)*Math.PI,b=(j/11-.5)*Math.PI;
   compound.push({p:[s*.53+Math.sin(a)*Math.cos(b)*.25,.16+Math.sin(b)*.2,.16+Math.cos(a)*Math.cos(b)*.2],s:[.034,.026,.031],r:[b,-a,s*.3]});
  }
  batch(face,compound,crystalMaterial(3,materials),gem);
 }else for(const s of [-1,1]){
  const eyeX=s*w*.47,eyeY=h*.13;
  const aperture=new T.Mesh(new T.CircleGeometry(1,40),dark);aperture.position.set(eyeX,eyeY,.105);aperture.scale.set(w*.35,h*.063,1);face.add(aperture);
  for(let layer=0;layer<(mantis?4:3);layer++)for(let i=0;i<32;i++){
   const a=i/32*TAU,rr=1-layer*.19;
   eyes.push({p:[eyeX+Math.cos(a)*w*.36*rr,eyeY+Math.sin(a)*h*.075*rr,.14+layer*.018],s:[.015,.008,.016],r:[a,layer*.7,a]});
  }
  // A slit of light rather than cartoon sclera or round googly pupils.
  for(let i=0;i<5;i++)eyes.push({p:[eyeX,eyeY+(i-2)*.008,.23],s:[.006,.006,.012],r:[0,0,i*.5]});
 }
 if(eyes.length)batch(face,eyes,light);
 motions.push(t=>{face.rotation.y=Math.sin(t*.29+seed)*.075;face.rotation.z=Math.sin(t*.17+seed)*.035;face.scale.x=1+Math.sin(t*.23+seed)*.045;});
 // Antennae, filigree crowns and branching halos are made from the same fractal limbs.
 const crown=[];
 if(mantis){
  for(const s of [-1,1])branch(crown,[s*.27,.28,0],[s*.58,1.03,-.1],.033,3,s);
 }else if(jester){
  for(let l=0;l<3;l++){
   const s=l-1,pts=[];
   for(let j=0;j<9;j++){const v=j/8;pts.push([s*(.18+v*.66),.43+Math.sin(v*1.9)*.85,.1*Math.sin(v*4+l)]);}
   for(let j=0;j<8;j++)segment(crown,pts[j],pts[j+1],.11*(1-j/10),j);
   branch(crown,pts[7],pts[8],.055,3,l);
  }
 }else{
  for(let i=0;i<(mother?17:9);i++){
   const a=(i/(mother?16:8)-.5)*Math.PI*1.32,rr=mother?1.15:.68;
   branch(crown,[Math.sin(a)*.34,Math.cos(a)*.43,-.08],[Math.sin(a)*rr,Math.cos(a)*rr,-.19],.045,F.quality==='high'?2:1,i);
  }
 }
 const halo=batch(face,crown,mantis?light:gold);motions.push(t=>{halo.rotation.z=Math.sin(t*.12+seed)*.05;});
 g.traverse(o=>{if(o.isMesh||o.isPoints||o.isLineSegments)o.userData.evidence=[evidence,...motifs];});
 return {kind,g,body,joints,engaged:false,evidence,seed};
}
// A 4D hypercube projection with recursive gem cells: continuously changes its apparent topology.
function offering(x,y,z,size,parent,materials,motions,evidence){
 const g=new T.Group();g.position.set(x,y,z);g.scale.setScalar(size);parent.add(g);
 const material=crystalMaterial(0,materials),gemMat=crystalMaterial(1,materials);
 const vertices=[];for(let i=0;i<16;i++)vertices.push([i&1?1:-1,i&2?1:-1,i&4?1:-1,i&8?1:-1]);
 const edges=[];for(let i=0;i<16;i++)for(let bit=0;bit<4;bit++){const j=i^(1<<bit);if(j>i)edges.push([i,j]);}
 const depth=size<.5?2:F.quality==='high'?4:3,divisions=size<.5?3:5,count=edges.length*depth*divisions;
 const filaments=new T.InstancedMesh(new T.OctahedronGeometry(1,0),material,count);g.add(filaments);filaments.frustumCulled=false;
 const nodes=new T.InstancedMesh(new T.IcosahedronGeometry(1,1),gemMat,16*depth);g.add(nodes);nodes.frustumCulled=false;const d=new T.Object3D();
 motions.push(t=>{
  const a=t*.27,b=t*.19,projected=vertices.map(([x,y,z,w])=>{
   const xx=x*Math.cos(a)-w*Math.sin(a),ww=x*Math.sin(a)+w*Math.cos(a),yy=y*Math.cos(b)-z*Math.sin(b),zz=y*Math.sin(b)+z*Math.cos(b);
   const perspective=1/(2.8-ww*.6);return new T.Vector3(xx,yy,zz).multiplyScalar(perspective);
  });let k=0,n=0;
  for(let layer=0;layer<depth;layer++){
   const s=Math.pow(.62,layer);
   for(const v of projected){d.position.copy(v).multiplyScalar(s);d.scale.setScalar(.092*s);d.rotation.set(t*.3+layer,t*.24,layer*.7);d.updateMatrix();nodes.setMatrixAt(n++,d.matrix);}
   for(const [i,j] of edges){
    const av=projected[i].clone().multiplyScalar(s),bv=projected[j].clone().multiplyScalar(s),v=bv.clone().sub(av),q=new T.Quaternion().setFromUnitVectors(up,v.clone().normalize());
    for(let p=0;p<divisions;p++){d.position.copy(av).lerp(bv,(p+.5)/divisions);d.quaternion.copy(q);d.scale.set(.022*s,v.length()/divisions*.72,.022*s);d.updateMatrix();filaments.setMatrixAt(k++,d.matrix);}
   }
  }
  filaments.instanceMatrix.needsUpdate=true;nodes.instanceMatrix.needsUpdate=true;g.rotation.set(Math.sin(t*.11)*.3,t*.13,Math.sin(t*.21)*.2);
 });
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=evidence;});return g;
}
// Waiting-only continuous usher. Shared entity appearances remain unchanged.
function createWaitingUsher(kind,x,y,z,size,root,materials,motions,evidence,seed){
 if(kind==='jester')return createContactBeing(kind,x,y,z,size*.74,root,materials,motions,evidence,seed);
 const g=new T.Group(),body=new T.Group(),joints=[];
 g.position.set(x,y,z);g.scale.setScalar(size);g.userData.entityKey=evidence;g.add(body);root.add(g);
 const skin=new T.ShaderMaterial({uniforms:{time:{value:0}},vertexShader:`
 varying vec3 p,n,v;uniform float time;
 void main(){p=position;vec3 q=position+normal*.012*sin(position.y*8.+position.x*6.+time*.7);
 n=normalize(normalMatrix*normal);vec4 mv=modelViewMatrix*vec4(q,1.);v=mv.xyz;gl_Position=projectionMatrix*mv;}`,
 fragmentShader:`precision highp float;uniform float time;varying vec3 p,n,v;
 void main(){vec3 N=normalize(n),V=normalize(-v),L=normalize(vec3(-.5,.8,1.));
 vec3 q=p*9.+.5*sin(p.yzx*5.+time*.24);
 float a=dot(sin(q),cos(q.zxy));float b=dot(sin(q*3.1),cos(q.yzx*3.1));
 float rim=pow(1.-abs(dot(N,V)),2.);float ridge=exp(-a*a*15.);
 vec3 col=mix(vec3(.015,.16,.14),vec3(.48,.22,.065),ridge*(.55+.45*exp(-b*b*4.)));
 col*=.5+.8*max(dot(N,L),0.);col+=vec3(.25,.17,.48)*rim;
 col+=vec3(.85,.75,.45)*pow(max(dot(N,normalize(L+V)),0.),52.)*.55;
 gl_FragColor=vec4(col,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(skin);
 const dark=new T.MeshBasicMaterial({color:0x090b19}),iris=new T.MeshBasicMaterial({color:0xc0e5c2});
 const sphere=new T.SphereGeometry(1,40,28);
 function ell(parent,at,scale,mat=skin){const o=new T.Mesh(sphere,mat);o.position.set(...at);o.scale.set(...scale);parent.add(o);return o;}
 function tube(parent,points,r,mat=skin){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));const o=new T.Mesh(new T.TubeGeometry(curve,40,r,12,false),mat);parent.add(o);return o;}
 // One closed flowing mantle, widening into the room's floor rather than dotted legs.
 const profile=[[0,0],[.92,.02],[.74,.16],[.56,.55],[.43,1.1],[.36,1.65],[.43,2.15],[.58,2.55],[.45,2.75],[.21,2.9],[.18,3.15],[0,3.2]].map(p=>new T.Vector2(...p));
 body.add(new T.Mesh(new T.LatheGeometry(profile,72),skin));
 const head=ell(body,[0,3.42,0],[.42,.65,.33]);
 // Brow, almond sockets, raised nose, parted lips and a pointed chin form an actual face.
 for(const s of [-1,1]){
  const eye=ell(body,[s*.17,3.54,.285],[.145,.082,.063],dark);eye.rotation.z=s*.17;
  ell(body,[s*.16,3.535,.341],[.044,.052,.018],iris);
  ell(body,[s*.16,3.535,.359],[.016,.039,.006],dark);
  tube(body,[[s*.04,3.61,.3],[s*.17,3.65,.32],[s*.3,3.6,.25]],.036);
  tube(body,[[s*.055,3.48,.3],[s*.17,3.45,.34],[s*.3,3.51,.25]],.025);
  tube(body,[[s*.31,3.38,.24],[s*.23,3.28,.31],[s*.13,3.13,.24]],.043);
  // Swept crown folds connect to the skull; no detached jewels or antenna dots.
  tube(body,[[s*.3,3.77,0],[s*.42,4.03,-.08],[s*.31,4.28,-.16],[s*.12,4.4,-.2]],.075);
 }
 ell(body,[0,3.4,.33],[.068,.18,.1]);ell(body,[0,3.29,.38],[.08,.06,.06]);
 ell(body,[0,3.17,.303],[.135,.039,.025],dark);
 tube(body,[[-.14,3.18,.29],[0,3.205,.33],[.14,3.18,.29]],.021);
 tube(body,[[-.12,3.15,.29],[0,3.125,.325],[.12,3.15,.29]],.022);
 for(const s of [-1,1]){
  const arm=new T.Group();arm.position.set(s*.43,2.61,0);body.add(arm);joints.push({o:arm,side:s,mantis:false,mother:false});
  // Right palm offers the passage; left palm is raised toward the arriving viewer.
  const py=s>0?-.1:.15,pz=s>0?.05:.42;
  tube(arm,[[0,0,0],[s*.32,-.16,.04],[s*.65,-.38,.15],[s*.9,py,pz]],.135);
  ell(arm,[s*.98,py,pz],[.16,.21,.09]);
  for(let f=0;f<4;f++){
   const fx=s*(.88+f*.066),len=.27+Math.sin((f+1)*.7)*.09;
   tube(arm,[[fx,py+.12,pz],[fx+s*(f-1.5)*.025,py+.25,pz+.03],[fx+s*(f-1.5)*.046,py+len+.15,pz+.09]],.028);
  }
  tube(arm,[[s*.87,py-.035,pz],[s*.73,py+.08,pz+.05],[s*.7,py+.2,pz+.08]],.043);
  for(let f=0;f<3;f++)tube(body,[[s*.4,.5,-.1-f*.12],[s*(.7+f*.2),.12,-.2-f*.24],[s*(1.25+f*.22),.035,-.45-f*.4]],.055-f*.009);
 }
 motions.push(t=>{head.scale.x=.42*(1.+.035*Math.sin(t*.7));head.scale.y=.65*(1.+.025*Math.cos(t*.6));});
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=[evidence];});
 return {kind,g,body,joints,engaged:false,evidence,seed};
}
// Continuous implicit body; the mother variant is used only by the garden.
function createContactBeing(kind,x,y,z,size,root,materials,motions,evidence,seed){
 const g=new T.Group(),body=new T.Group(),joints=[];
 g.position.set(x,y,z);g.scale.setScalar(size);g.userData.entityKey=evidence;g.add(body);root.add(g);
 const skin=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{
  time:{value:0},seed:{value:seed},jester:{value:kind==='jester'?1:0},gardenMother:{value:kind==='mother'?1:0},elf:{value:kind==='elf'?1:0},
  localFromWorld:{value:new T.Matrix4()},worldFromLocal:{value:new T.Matrix4()}
 },vertexShader:`varying vec3 localSurface;void main(){localSurface=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
 fragmentShader:`precision highp float;
 uniform float time,seed,jester,gardenMother,elf;uniform mat4 localFromWorld,worldFromLocal,projectionMatrix;
 varying vec3 localSurface;
 float join(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float ell(vec3 p,vec3 r){float k0=length(p/r),k1=length(p/(r*r));return k0*(k0-1.)/max(k1,.00001);}
 float limb(vec3 p,vec3 a,vec3 b,float r){vec3 ab=b-a;return length(p-a-ab*clamp(dot(p-a,ab)/dot(ab,ab),0.,1.))-r;}
 vec3 living(vec3 p){
  float rise=smoothstep(0.,3.,p.y);p.x-=rise*.09*sin(p.y*.85+time*.75+seed);
  p.xz/=1.+.055*sin(time*.9+seed)*exp(-pow(p.y-3.1,2.));
  if(jester>.5){
   float head=smoothstep(4.25,4.7,p.y),t=time*.85+seed;
   p.x/=1.+head*.13*sin(t*.83);
   p.y-=head*.055*sin(p.x*4.+t*.9);
   p.z-=head*.025*sin(p.x*5.+p.y*2.-t);
  }
  return p;
 }
 float elfBody(vec3 p,float t){
  // A continuous branching sheet fills the torso; smaller openings reveal its depth.
  vec3 q=p-vec3(0.,2.65,0.);
  q.xz/=1.+.19*sin(t*.72+q.y*.8);
  float twist=q.y*.38+.42*sin(t*.6);
  q.xz=mat2(cos(twist),-sin(twist),sin(twist),cos(twist))*q.xz;
  float envelope=ell(q,vec3(.72,1.23,.48));
  envelope=join(envelope,ell(q-vec3(0.,.98,0.),vec3(.61,.30,.34)),.18);
  vec3 cell=q*4.2+vec3(.30*sin(t*.5),t*.19,.35*cos(t*.6));
  float sheet=abs(dot(sin(cell),cos(cell.zxy)))/7.35-.115;
  float d=max(envelope,sheet);
  vec3 inner=cell.yzx*2.65+.22*sin(cell.zxy);
  float openings=(length(sin(inner))-.88)/11.13;
  d=max(d,-openings);
  d=join(d,ell(p-vec3(0.,2.7,-.08),vec3(.13,1.16,.15)),.085);
  d=join(d,limb(p,vec3(0.,3.4,0.),vec3(0.,4.12,0.),.12),.12);
  return d;
 }
 float motherHead(vec3 p,float t){
  p.x-=.04*sin(t*.65)*smoothstep(4.45,5.5,p.y);
  float d=ell(p-vec3(0.,5.12,0.),vec3(.425,.61,.32));
  d=join(d,ell(p-vec3(0.,4.77,.065),vec3(.27,.29,.265)),.14);
  for(int i=0;i<2;i++){
   float s=i==0?-1.:1.,expression=.028*sin(t*.85+s*.4);
   vec3 q=p;q.x*=s;
   d=join(d,ell(q-vec3(.255,5.0+expression,.255),vec3(.145,.18,.13)),.08);
   d=join(d,limb(q,vec3(.07,5.34+expression,.305),vec3(.34,5.32-expression,.245),.046),.04);
   vec3 eye=q-vec3(.20,5.19+expression*.35,.315);eye.y-=eye.x*.12;
   d=-join(-d,ell(eye,vec3(.132,.060,.10)),.022);
   d=join(d,ell(eye-vec3(0.,-.018,-.065),vec3(.107,.030,.035)),.016);
   d=max(d,-ell(q-vec3(.062,4.98,.371),vec3(.028,.023,.033)));
  }
  d=join(d,ell(p-vec3(0.,5.115,.306),vec3(.054,.20,.081)),.035);
  d=join(d,ell(p-vec3(0.,5.0,.367),vec3(.077,.066,.064)),.03);
  vec3 lips=p-vec3(0.,4.80,.303);lips.y-=(.9+.25*sin(t*.7))*lips.x*lips.x;
  d=join(d,ell(lips-vec3(0.,.022,0.),vec3(.15,.035,.045)),.025);
  d=join(d,ell(lips+vec3(0.,.029,0.),vec3(.14,.035,.044)),.024);
  d=max(d,-ell(lips,vec3(.137,.012+.006*(.5+.5*sin(t*.8)),.065)));
  return d;
 }
 float form(vec3 point){
  vec3 p=living(point);float t=time*.85+seed,face=.5+.5*sin(seed*2.3);
  // A fluted mantle grows directly out of a buried, spreading base.
  float angle=atan(p.z,p.x),flare=.29+1.38*exp(-max(p.y,0.)*1.85)+gardenMother*.32*exp(-pow((p.y-1.4)/1.35,2.));
  float folds=.045*cos(angle*9.+p.y*1.8+.35*sin(t))+.018*cos(angle*18.-p.y*3.);
  float d=max(length(p.xz/vec2(1.,.68))-flare-folds,max(-p.y-.48,p.y-2.9));
  d=join(d,ell(p-vec3(0.,3.12,0.),vec3(.37+gardenMother*.09,1.03,.26+gardenMother*.045)),.25);
  d=join(d,ell(p-vec3(0.,3.73,-.035),vec3(.54,.27,.25)),.16);
  if(gardenMother>.5){
   // A living calyx: rounded overlapping lobes enclose deep, smaller chambers.
   // The same volume grows from the waist into the buried roots.
   vec3 mantle=p;mantle.xz/=1.+.07*sin(t*.65+p.y*1.2);
   float a=atan(mantle.z/.68,mantle.x)+.22*sin(p.y*1.6-t*.42);
   float radius=length(mantle.xz/vec2(1.,.68));
   float spread=.31+1.38*exp(-max(p.y,0.)*1.85)+.43*exp(-pow((p.y-1.7)/1.35,2.));
   float petals=.105*cos(a*7.+p.y*2.-t*.36)+.025*cos(a*21.-p.y*3.+t*.5);
   d=max(radius-spread-petals,max(-p.y-.48,p.y-3.4));
   for(int layer=0;layer<3;layer++){
    float f=float(layer),yy=.95+f*.88+.10*sin(t*.7+f);
    float phase=a+f*.40+.12*sin(t*.5+f);
    float arc=atan(sin(phase*7.),cos(phase*7.))/7.;
    vec3 chamber=vec3(arc*max(spread,.35),p.y-yy,radius-spread+.045);
    float hollow=ell(chamber,vec3(.14-f*.018,.35-f*.025,.23));
    d=-join(-d,hollow,.065);
    // A smaller recessed bud sits inside each chamber, joined at its base.
    vec3 bud=chamber-vec3(0.,-.12,-.17);
    d=join(d,ell(bud,vec3(.062,.18,.095)),.06);
   }
   d=join(d,ell(p-vec3(0.,3.12,0.),vec3(.46,1.03,.305)),.25);
   d=join(d,ell(p-vec3(0.,3.73,-.035),vec3(.54,.27,.25)),.16);
  }
  if(elf>.5)d=elfBody(p,t);
  if(jester>.5){
   // Thick rounded folds enclose unequal nested windows, without cut ribbon edges.
   vec3 mantle=p;
   float twist=.30*(p.y-2.)+.24*sin(t*.55+p.y*.6);
   mantle.xz=mat2(cos(twist),-sin(twist),sin(twist),cos(twist))*mantle.xz;
   d=ell(mantle-vec3(0.,2.42,0.),vec3(.78,1.42,.46));
   d=join(d,ell(mantle-vec3(0.,1.04,0.),vec3(.38,.89,.30)),.20);
   for(int k=0;k<2;k++){
    float s=k==0?-1.:1.;vec3 q=mantle;q.x*=s;
    float breathe=.07*sin(t*.8+s);
    float window=ell(q-vec3(.40,2.45+breathe,.07),vec3(.21+breathe*.3,.64,.64));
    d=-join(-d,window,.075);
    window=ell(q-vec3(.43,3.32-breathe,.04),vec3(.15,.22,.53));
    d=-join(-d,window,.045);
    window=ell(q-vec3(.20,1.33+breathe,.10),vec3(.115,.30,.42));
    d=-join(-d,window,.035);
   }
   d=join(d,ell(p-vec3(0.,3.60,0.),vec3(.47,.26,.30)),.15);
   for(int k=0;k<3;k++){
    float f=float(k),yy=4.02+f*.13;
    vec3 r=p-vec3(0.,yy,0.);
    float a=atan(r.z,r.x),flute=.07*cos(a*10.+t*.5+f*.8);
    float collar=max(length(r.xz)-(.67-f*.12+flute),abs(r.y-.055*cos(a*10.+t*.5))-.055);
    d=join(d,collar,.045);
   }
  }
  d=join(d,limb(p,vec3(0.,3.7,0.),vec3(0.,4.75,0.),.125),.16);
  if(gardenMother>.5)d=join(d,motherHead(p,t),.13);
  else{
   d=join(d,ell(p-vec3(0.,5.14,0.),vec3(.31+face*.055+jester*.13,.76-jester*.08,.28+jester*.035)),.14);
   d=join(d,ell(p-vec3(0.,4.66,.08),vec3(.16+face*.025,.36,.21)),.1);
  }
  for(int i=0;i<2;i++){
   float s=i==0?-1.:1.;vec3 q=p;q.x*=s;
   if(elf>.5){
    vec3 hip=vec3(.32,1.65,0.),knee=vec3(.62+.16*sin(t*.7+s),.84,.19*cos(t*.7+s));
    vec3 ankle=vec3(.51+.13*sin(t*.7+s),.13,.12);
    d=join(d,limb(q,hip,knee,.14),.12);
    d=join(d,limb(q,knee,ankle,.085),.08);
    for(int toe=0;toe<3;toe++){
     float f=float(toe)-1.;
     vec3 fork=ankle+vec3(f*.28,-.14,.27);
     vec3 tip=ankle+vec3(f*.65+.15,-.32,.70-abs(f)*.15);
     d=join(d,limb(q,ankle,fork,.065),.085);
     d=join(d,limb(q,fork,tip,.03),.06);
     d=join(d,limb(q,mix(fork,tip,.55),tip+vec3(.18,-.035,-.14),.018),.025);
    }
   }else if(jester>.5){
    vec3 knee=vec3(.53,.20,.12);
    d=join(d,limb(q,vec3(.19,1.02,0.),knee,.16),.17);
    d=join(d,limb(q,knee,vec3(1.60,-.43,.31),.085),.13);
    d=join(d,limb(q,vec3(.36,.42,-.06),vec3(1.04,-.44,-.64),.085),.13);
   }else{
    d=join(d,limb(q,vec3(.25,1.1,.04),vec3(1.83,-.32,.3),.16),.3);
    d=join(d,limb(q,vec3(.2,.65,-.1),vec3(1.32,-.35,-.72),.18),.28);
   }
   vec3 shoulder=vec3(.46,3.73,0.),elbow=vec3(.91+gardenMother*.16,3.08+.18*sin(t+s),.17);
   vec3 palm=vec3(1.42+gardenMother*.16,3.57+.32*sin(t+s*1.2),.53+.17*cos(t+s));
   d=join(d,limb(q,shoulder,elbow,.103),.14);d=join(d,limb(q,elbow,palm,.075),.095);
   d=join(d,ell(q-palm,vec3(.155,.27,.08)),.065);
   for(int f=0;f<4;f++){
    float fi=float(f),spread=fi-1.5;
    vec3 a=palm+vec3(spread*.082,.19,0.);
    vec3 b=a+vec3(spread*.039,.25+.06*sin(fi),.035);
    vec3 c=b+vec3(spread*.022,.17+.05*sin(fi),.08+.065*sin(t+fi*.55));
    d=join(d,limb(q,a,b,.031),.03);d=join(d,limb(q,b,c,.024),.025);
   }
   vec3 thumb=palm+vec3(-.24,.015,.09);
   d=join(d,limb(q,palm+vec3(-.1,-.07,0.),thumb,.054),.055);
   d=join(d,limb(q,thumb,thumb+vec3(-.065,.15,.045),.04),.04);
   // Swept temple planes replace horns; each face has different orbital proportions.
   if(gardenMother<.5)d=join(d,ell(q-vec3(.24,5.35,-.08),vec3(.105,.65+jester*.12,.21)),.055);
   if(jester>.5){
    vec3 bend=vec3(.53+.09*sin(t*.65+s),5.93,-.07);
    vec3 tip=vec3(.76+.10*sin(t*.65+s),5.60+.13*cos(t*.8+s),-.02);
    d=join(d,limb(q,vec3(.25,5.55,-.08),bend,.13),.12);
    d=join(d,limb(q,bend,tip,.085),.08);
    d=join(d,ell(q-tip,vec3(.085,.15,.10)),.06);
    d=join(d,ell(q-vec3(.30,4.96,.20),vec3(.16,.25,.11)),.08);
    float expression=.045*sin(t*.8+s*.7);
    d=join(d,limb(q,vec3(.06,5.42+expression,.28),vec3(.34,5.47-expression,.22),.068),.055);
    d=join(d,ell(q-vec3(.32,5.04+expression,.27),vec3(.15,.15,.12)),.055);
    d=-join(-d,ell(q-vec3(.29,4.83+expression,.30),vec3(.065,.15,.095)),.025);
    d=max(d,-ell(q-vec3(.07,4.90,.356),vec3(.035,.035,.053)));
   }
   if(gardenMother>.5){
    // One tapered sweep carries nested longitudinal folds from crown into torso.
    float u=clamp((5.78-q.y)/2.78,0.,1.);
    float taper=sqrt(max(.002,1.-pow((q.y-4.39)/1.39,2.)));
    float sweep=.10+.53*sin(u*2.8)+.025*sin(u*8.-t*.45)*sin(u*3.14159);
    vec2 hair=vec2(q.x-sweep,q.z+.10+.15*u);
    vec2 radii=vec2(.09+.065*sin(u*3.14159),.20-.065*u)*taper;
    float theta=atan(hair.y/radii.y,hair.x/radii.x);
    float flow=theta+u*2.4+.15*sin(u*9.-t*.35);
    float folds=(.019*cos(flow*7.)+.007*cos(flow*19.+u*3.)
                +.0025*cos(flow*43.-u*6.))*taper;
    float lock=(length(hair/radii)-1.)*min(radii.x,radii.y)+folds;
    lock=max(lock,abs(q.y-4.39)-1.39);
    d=join(d,lock,.055+.045*smoothstep(.6,1.,u));
   }
   if(gardenMother<.5){
   vec3 eye=q-vec3(.15+face*.025+jester*.045,5.21+face*.055,.245);
   eye.xy=mat2(.94,-.34,.34,.94)*eye.xy;
   d=max(d,-ell(eye,vec3(.13,.10+face*.025,.12)));
   d=join(d,limb(q,vec3(.035,5.34,.26),vec3(.29,5.42,.17),.038),.025);
   d=join(d,ell(q-vec3(.2,4.99,.205),vec3(.095,.27,.085)),.035);
   d=max(d,-ell(q-vec3(.17,4.83,.255),vec3(.065,.16,.065)));
   }
  }
  if(gardenMother<.5){
  d=join(d,ell(p-vec3(0.,5.05,.267),vec3(.046,.31,.08+face*.035)),.025);
  d=join(d,ell(p-vec3(0.,4.88,.315),vec3(.065,.065,.07)),.022);
  vec3 mouth=p-vec3(0.,4.67,.236);mouth.y-=(.18+jester*(2.+.7*sin(t*.72)))*mouth.x*mouth.x;
  d=max(d,-ell(mouth,vec3(.113+face*.02+jester*.15,.033+jester*(.025+.012*sin(t)),.065)));
  if(jester>.5){
   vec3 grin=p-vec3(0.,4.73,.29);
   grin.y-=(1.8+.6*sin(t*.72))*grin.x*grin.x;
   float gape=.075+.025*sin(t*.9);
   d=-join(-d,ell(grin,vec3(.27,gape,.14)),.022);
   d=join(d,ell(grin+vec3(0.,gape+.02,-.018),vec3(.255,.033,.055)),.023);
   for(int tooth=0;tooth<5;tooth++){
    float x=(float(tooth)-2.)*.086;
    d=join(d,ell(grin-vec3(x,gape*.65,.012),vec3(.034,.045,.042)),.008);
   }
  }
  d=join(d,ell(p-vec3(0.,4.615,.223),vec3(.105,.024,.029)),.016);
  }
  if(jester>.5){
   float body=smoothstep(.6,1.1,p.y)*(1.-smoothstep(3.7,4.15,p.y));
   vec3 relief=p*8.+.35*sin(p.yzx*3.+t*.4);
   float carving=sin(relief.x)*sin(relief.y)*sin(relief.z);
   carving+=.38*sin(relief.x*2.3+carving)*sin(relief.y*2.3)*sin(relief.z*2.3);
   carving+=.12*sin(relief.x*5.1)*sin(relief.y*5.1+carving)*sin(relief.z*5.1);
   d+=body*.038*carving;
  }
  if(gardenMother>.5){
   float mantle=smoothstep(.05,.6,p.y)*(1.-smoothstep(3.5,3.9,p.y));
   vec3 vein=p*13.+.35*sin(p.yzx*5.+t*.4);
   d+=mantle*(.016*sin(vein.x)*sin(vein.y)*sin(vein.z)
      +.005*sin(vein.x*2.7)*sin(vein.y*2.7)*sin(vein.z*2.7));
  }
  return d*.72;
 }
 vec3 normalAt(vec3 p){vec2 e=vec2(.003,0.);return normalize(vec3(form(p+e.xyy)-form(p-e.xyy),form(p+e.yxy)-form(p-e.yxy),form(p+e.yyx)-form(p-e.yyx)));}
 void main(){
  vec3 ro=(localFromWorld*vec4(cameraPosition,1.)).xyz,rd=normalize(localSurface-ro);
  vec3 inv=1./rd,ta=(vec3(-2.2,-.6,-1.3)-ro)*inv,tb=(vec3(2.2,6.3,1.3)-ro)*inv;
  vec3 lo=min(ta,tb),hi=max(ta,tb);float travel=max(0.,max(lo.x,max(lo.y,lo.z))),end=min(hi.x,min(hi.y,hi.z));
  bool hit=false;vec3 p;
  for(int i=0;i<144;i++){p=ro+rd*travel;float d=form(p);if(d<.002){hit=true;break;}travel+=max(d,.0015);if(travel>end)break;}
  if(!hit)discard;
  vec3 n=normalAt(p),v=-rd,q=living(p),l=normalize(vec3(-.6,1.,1.4));
  vec3 domain=q*11.+.6*sin(q.yzx*4.+time*.3);
  float weave=dot(sin(domain),cos(domain.zxy));
  float finer=dot(sin(domain*2.8),cos(domain.yzx*2.8));
  float gold=exp(-weave*weave*9.)*(.5+.5*exp(-finer*finer*3.));
  vec3 col=mix(vec3(.018,.34,.26),vec3(.83,.42,.095),gold);
  if(gardenMother>.5){
   float face=smoothstep(4.3,4.85,q.y)*smoothstep(-.05,.19,q.z);
   float silk=.5+.5*sin(q.y*2.3+atan(q.z,q.x)*7.+time*.28);
   col=mix(vec3(.018,.20,.15),vec3(.24,.075,.18),silk*.7);
   col+=vec3(.53,.33,.10)*gold*.25*(1.-face);
   col=mix(col,vec3(.52,.30,.22),face*.87);
  }
  col=mix(col,vec3(.38,.045,.32),jester*(.3+.25*sin(q.y*3.+time*.4)));
  float diffuse=.32+.75*max(dot(n,l),0.);float rim=pow(1.-max(dot(n,v),0.),3.);
  vec3 film=.5+.5*cos(vec3(.1,2.1,4.3)+dot(n,v)*6.+q.y*.7+time*.25);
  col*=diffuse;col+=film*rim*.32;
  col+=mix(vec3(.85,1.,.9),film,.3)*pow(max(dot(n,normalize(l+v)),0.),48.)*.85;
  col+=vec3(.1,.85,.6)*gold*.11;
  if(gardenMother>.5){
   float mantle=1.-smoothstep(3.6,4.3,q.y);
   float petals=.5+.5*cos(atan(q.z/.68,q.x)*7.+q.y*2.-time*.306);
   vec3 jewel=mix(vec3(.025,.18,.12),vec3(.22,.035,.15),petals);
   float cavity=clamp(form(p+n*.09)/.0648,.15,1.);
   vec3 organic=jewel*(.32+.85*max(dot(n,l),0.))*cavity;
   organic+=film*rim*.29+vec3(.8,.63,.33)*pow(max(dot(n,normalize(l+v)),0.),32.)*.45;
   organic+=vec3(.16,.38,.22)*gold*.075;
   col=mix(col,organic,mantle);
   float face=smoothstep(4.50,4.85,q.y)*smoothstep(.10,.27,q.z);
   vec3 pearl=mix(vec3(.40,.17,.13),vec3(.64,.40,.23),max(dot(n,l),0.));
   pearl*=.48+.58*max(dot(n,l),0.);
   pearl+=film*rim*.24+vec3(.9,.75,.48)*pow(max(dot(n,normalize(l+v)),0.),28.)*.24;
   col=mix(col,pearl,face);
   vec3 head=q;head.x-=.04*sin((time*.85+seed)*.65)*smoothstep(4.45,5.5,head.y);
   for(int i=0;i<2;i++){
    float s=i==0?-1.:1.,expression=.028*sin((time*.85+seed)*.85+s*.4);
    vec2 eye=head.xy-vec2(s*.20,5.19+expression*.35);
    col+=vec3(.28,.65,.38)*exp(-dot(eye/vec2(.025,.026),eye/vec2(.025,.026)))*step(.20,q.z)*.7;
   }
  }
  for(int i=0;i<2;i++){
   float s=i==0?-1.:1.,face=.5+.5*sin(seed*2.3);vec3 eye=q-vec3(s*(.15+face*.025+jester*.045),5.21+face*.055,.19);
   float iris=exp(-dot(eye.xy/vec2(.021,.053),eye.xy/vec2(.021,.053))*1.4)*step(.13,q.z);
   col+=vec3(.9,1.,.55)*iris*1.1*(1.-gardenMother);
  }
  if(jester>.5){
   float mask=smoothstep(4.45,4.95,q.y)*smoothstep(.03,.22,q.z);
   float fold=.5+.5*sin(atan(q.z,q.x)*6.+q.y*2.1+time*.47+seed);
   float a=atan(q.z,q.x)+q.y*.65+.35*sin(q.y*1.4-(time*.85+seed)*.6);
   float rib=pow(.5+.5*cos(a*10.-q.y*3.+(time*.85+seed)*.7),5.);
   vec3 enamel=mix(vec3(.025,.12,.14),vec3(.20,.025,.16),fold);
   enamel=mix(enamel,vec3(.52,.30,.085),rib*.18);
   vec3 base=mix(enamel,vec3(.40,.29,.17),mask);
   col=base*(.28+.8*max(dot(n,l),0.));
   col+=film*rim*.38;
   col+=vec3(.75,.82,.9)*pow(max(dot(n,normalize(l+v)),0.),64.)*.8;
   col+=vec3(.06,.32,.31)*pow(1.-abs(n.z),3.)*(1.-mask)*.45;
   for(int i=0;i<2;i++){
    float s=i==0?-1.:1.,variation=.5+.5*sin(seed*2.3);
    vec3 eye=q-vec3(s*(.195+variation*.025),5.21+variation*.055,.19);
    col+=vec3(.48,.9,.75)*exp(-dot(eye.xy/vec2(.025,.044),eye.xy/vec2(.025,.044))*1.4)*step(.13,q.z);
   }
  }
  if(elf>.5){
   // Jewel interiors and metallic edges follow the branching volume, not painted bands.
   float face=smoothstep(4.3,4.8,q.y)*smoothstep(.04,.19,q.z);
   float depth=smoothstep(-.3,.4,q.z);
   float inlay=pow(1.-abs(n.z),2.)*.72;
   vec3 jewel=mix(vec3(.055,.018,.12),vec3(.025,.31,.25),depth);
   vec3 metal=vec3(.57,.35,.11);
   vec3 base=mix(jewel,metal,inlay);
   base=mix(base,vec3(.34,.27,.18),face*.96);
   vec3 reflected=reflect(-v,n);
   float cool=pow(max(dot(reflected,normalize(vec3(-.8,.5,1.))),0.),18.);
   float warm=pow(max(dot(reflected,normalize(vec3(.7,.25,1.))),0.),32.);
   col=base*(.3+.76*max(dot(n,l),0.));
   col+=vec3(.34,.67,.85)*cool*.75+vec3(.95,.66,.3)*warm*.65;
   col+=film*rim*.26+base*(1.-face)*(.08+.15*depth);
   for(int i=0;i<2;i++){
    float s=i==0?-1.:1.,variation=.5+.5*sin(seed*2.3);
    vec3 eye=q-vec3(s*(.15+variation*.025),5.21+variation*.055,.19);
    col+=vec3(.38,.85,.8)*exp(-dot(eye.xy/vec2(.022,.045),eye.xy/vec2(.022,.045))*1.4)*step(.13,q.z);
   }
  }
  vec4 world=worldFromLocal*vec4(p,1.);vec4 clip=projectionMatrix*viewMatrix*world;
  gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,1.);
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const volume=new T.Mesh(new T.BoxGeometry(4.4,6.9,2.6).translate(0,2.85,0),skin);
 volume.userData.evidence=[evidence];body.add(volume);materials.push(skin);
 volume.onBeforeRender=()=>{skin.uniforms.worldFromLocal.value.copy(volume.matrixWorld);skin.uniforms.localFromWorld.value.copy(volume.matrixWorld).invert();};
 return {kind,g,body,joints,engaged:false,evidence,seed};
}
// Solid insectoid examiner, scoped to the clinical branch only.
function createClinicalBeing(kind,x,y,z,size,root,materials,motions,evidence,seed){
 const g=new T.Group(),body=new T.Group(),joints=[];
 g.position.set(x,y,z);g.scale.setScalar(size);g.userData.entityKey=evidence;g.add(body);root.add(g);
 const skin=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{
  time:{value:0},localFromWorld:{value:new T.Matrix4()},worldFromLocal:{value:new T.Matrix4()}
 },vertexShader:'varying vec3 localSurface;void main(){localSurface=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
 fragmentShader:`precision highp float;
 uniform float time;uniform mat4 localFromWorld,worldFromLocal,projectionMatrix;varying vec3 localSurface;
 float join(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float ell(vec3 p,vec3 r){float a=length(p/r),b=length(p/(r*r));return a*(a-1.)/max(b,.00001);}
 float limb(vec3 p,vec3 a,vec3 b,float r){vec3 ab=b-a;return length(p-a-ab*clamp(dot(p-a,ab)/dot(ab,ab),0.,1.))-r;}
 // Long overlapping chitin plates: broad at the root, keeled and pointed distally.
 float plate(vec3 p,vec3 a,vec3 b,float width,float depth){
  vec3 axis=normalize(b-a),side=normalize(cross(axis,vec3(0.,0.,1.))),front=cross(side,axis);
  vec3 v=p-mix(a,b,.46);float len=length(b-a),u=dot(p-a,axis)/len;
  vec3 q=vec3(dot(v,side),dot(v,axis),dot(v,front));
  q.x/=clamp(1.25-.85*u,.35,1.25);
  float shell=ell(q,vec3(width,len*.58,depth));
  return max(shell,(abs(q.x)*.52+q.z-depth*.86)*.65);
 }
 // Rounded tapered exoskeletons carry nested longitudinal flutes around their full depth.
 float chitinLimb(vec3 p,vec3 a,vec3 b,float width,float depth){
  vec3 axis=normalize(b-a),side=normalize(cross(axis,vec3(0.,0.,1.))),front=cross(side,axis);
  vec3 v=p-mix(a,b,.46);float len=length(b-a),u=dot(p-a,axis)/len;
  vec3 q=vec3(dot(v,side),dot(v,axis),dot(v,front));
  float taper=clamp(1.22-.68*u,.5,1.22);q.xz/=taper;
  float angle=atan(q.z/depth,q.x/width);
  float flute=pow(.5+.5*cos(angle*7.+u*1.8),6.);
  float fine=pow(.5+.5*cos(angle*21.-u*3.6),8.);
  return ell(q,vec3(width,len*.56,depth))+(flute*.012+fine*.004)*sin(clamp(u,0.,1.)*3.14159);
 }
 // Swept tarsal fans grow out of the lower shin and disappear beneath the room floor.
 vec3 tarsalPath(float s,float fan,float u,float t){
  float sway=.045*sin(t*.55+fan*1.8+s)*sin(u*3.14159);
  return vec3(s*(.85+fan*.61*pow(u,.8))+sway,
   .34*(1.-u)*(1.-u)+.10*sin(u*3.14159)-.14*u,
   .18+(1.02+abs(fan)*.22)*u+.11*sin(u*3.14159+fan)*u);
 }
 vec3 living(vec3 p){p.x-=.055*sin(time*.65+p.y*.7)*smoothstep(.2,3.,p.y);p.z-=(.16+.08*sin(time*.8))*smoothstep(2.8,4.7,p.y);return p;}
 float compoundLens(vec3 eye){
  vec2 uv=vec2(atan(eye.x,eye.z),atan(eye.y,length(eye.xz)))*6.;
  vec2 period=vec2(1.73205,1.);
  vec2 a=mod(uv,period)-period*.5,b=mod(uv-period*.5,period)-period*.5;
  return 1.-smoothstep(.10,.24,min(dot(a,a),dot(b,b)));
 }
 vec2 form(vec3 point){
  vec3 p=living(point);float t=time*.82;
  // Oblique overlapping shell plates grow around a narrow living core.
  float d=ell(p-vec3(0.,1.99,-.10),vec3(.21,.72,.19));
  d=join(d,ell(p-vec3(0.,3.13,0.),vec3(.16,.78,.17)),.15);
  for(int j=0;j<6;j++){
   float f=float(j)/5.,yy=1.48+f*1.04;
   float width=.18+.065*sin(f*3.14159);
   vec3 shell=vec3(abs(p.x)-width*.64,p.y-yy,p.z+.015);
   shell.y-=shell.x*.65;
   shell.z+=.018*sin(f*5.+t*.65);
   float scale=ell(shell,vec3(width,.16,.245-.045*f));
   float ridge=sin(shell.x*48.+shell.y*12.+f*2.);
   scale+=.008*ridge+.003*sin(shell.x*113.+shell.y*31.);
   d=join(d,scale,.035);
  }
  vec3 chest=p;chest.x=abs(chest.x);
  d=join(d,limb(chest,vec3(.055,2.58,.16),vec3(.14,3.45,.12),.055),.045);
  d=join(d,limb(chest,vec3(.14,3.45,.12),vec3(.055,3.72,.07),.040),.035);
  // Nested lengthwise recesses interrupt the broad smooth thorax highlight.
  float thorax=exp(-pow((p.y-3.14)/.48,4.));
  d+=thorax*(.009*cos(atan(p.z,p.x)*12.+p.y*2.)
             +.003*cos(atan(p.z,p.x)*31.-p.y*5.));
  d=join(d,limb(p,vec3(0.,3.55,0.),vec3(0.,4.02,.05),.13),.14);
  vec3 face=p-vec3(0.,4.28,.05);
  face.x/=clamp(.65+face.y*1.12,.23,1.05);
  d=join(d,ell(face,vec3(.78,.46,.29)),.055);
  // Thin central facial keel and swept brow replace the rounded mask.
  d=join(d,plate(p,vec3(0.,4.53,.20),vec3(0.,4.02,.22),.085,.065),.028);
  for(int i=0;i<2;i++){
   float s=i==0?-1.:1.;
   vec3 hip=vec3(s*.24,1.95,-.08),knee=vec3(s*.81,1.03,-.31),ankle=vec3(s*.85,.13,.18);
   d=join(d,chitinLimb(p,hip,knee,.16,.14),.065);d=join(d,chitinLimb(p,knee,ankle,.085,.085),.045);
   d=join(d,ell(p-knee,vec3(.11,.115,.105)),.025);
   d=join(d,limb(p,mix(hip,knee,.83),mix(knee,ankle,.15),.062),.028);
   for(int f=0;f<3;f++){
    float fan=float(f)-1.;
    for(int j=0;j<6;j++){
     float u=float(j)/6.,v=float(j+1)/6.;
     vec3 a=tarsalPath(s,fan,u,t),b=tarsalPath(s,fan,v,t);
     float r=mix(.095,.026,v)+.027*sin(v*3.14159);
     d=join(d,limb(p,a,b,r),.055);
    }
    // Smaller lateral offshoots split from the sweep, ending below floor level.
    vec3 a=tarsalPath(s,fan,.48,t),b=tarsalPath(s,fan,.72,t);
    b.x+=s*(fan==0.?-.19:fan*.14);b.z+=.11;b.y-=.045;
    vec3 c=b+vec3(s*(fan==0.?-.12:fan*.08),-.20,.25);
    d=join(d,limb(p,a,b,.042),.035);
    d=join(d,limb(p,b,c,.023),.028);
   }
   vec3 shoulder=vec3(s*.24,3.46,0.);
   vec3 elbow=vec3(s*(1.05+.06*sin(t+s)),2.88+s*.17,.20);
   vec3 wrist=vec3(s*(.54+.14*sin(t*.7+s)),3.06+s*.25+.14*cos(t+s),1.22+.16*sin(t+s));
   d=join(d,chitinLimb(p,shoulder,elbow,.125,.12),.065);
   d=join(d,ell(p-elbow,vec3(.11,.10,.115)),.025);
   d=join(d,limb(p,mix(shoulder,elbow,.86),mix(elbow,wrist,.13),.061),.028);
   d=join(d,chitinLimb(p,elbow,wrist,.15,.135),.045);
   // Smaller overlapping distal plate leaves a narrow flexing joint membrane.
   d=join(d,chitinLimb(p,mix(elbow,wrist,.53)+vec3(0.,0.,.055),wrist+vec3(0.,.015,.04),.105,.10),.025);
   vec3 palm=wrist+vec3(s*.025,-.055,.12);
   d=join(d,plate(p,wrist,palm+vec3(0.,-.13,.12),.14,.068),.04);
   // Three long independently curling fingers and an opposing grasping digit.
   for(int f=0;f<3;f++){
    float k=float(f)-1.,curl=.08*sin(t*1.15+s+float(f)*.8);
    vec3 a=palm+vec3(k*.105,-.08,.08);
    vec3 b=a+vec3(k*.068,-.11+curl,.24);
    vec3 c=b+vec3(-k*.024,-.13-curl,.16);
    d=join(d,plate(p,a,b,.039,.027),.026);d=join(d,plate(p,b,c,.027,.021),.022);
   }
   vec3 thumb=palm+vec3(-s*.14,.025,.035),knuckle=thumb+vec3(-s*.14,-.095,.13);
   d=join(d,limb(p,thumb,knuckle,.050),.065);
   d=join(d,limb(p,knuckle,knuckle+vec3(s*.015,-.14,.11),.034),.055);
   for(int f=0;f<4;f++){
    float k=(float(f)+1.)/5.;vec3 a=mix(elbow,wrist,k);
    d=join(d,plate(p,a,a+vec3(-s*.14,.065,.13),.038,.024),.025);
   }
   // Recessed cheeks frame independently opening, forward-projecting mandibles.
   d=-join(-d,ell(p-vec3(s*.17,4.18,.30),vec3(.07,.12,.10)),.018);
   vec3 jaw=vec3(s*.16,4.16,.31),tip=vec3(s*(.045+.04*sin(t+s*.4)),3.99,.39);
   d=join(d,plate(p,jaw,tip,.073,.049),.026);
   d=join(d,limb(p,tip,tip+vec3(-s*.035,.07,.05),.027),.022);
   d=join(d,plate(p,vec3(s*.14,4.51,.19),vec3(s*.63,4.47,.12),.072,.052),.027);
   // Swept antennae remain continuous and taper along their curves.
   for(int j=0;j<5;j++){
    float v=float(j)/5.,v2=(float(j)+1.)/5.;
    vec3 a=vec3(s*(.29+.41*v),4.60+v*.95,.01-.24*v*v+.05*sin(t+v*2.));
    vec3 b=vec3(s*(.29+.41*v2),4.60+v2*.95,.01-.24*v2*v2+.05*sin(t+v2*2.));
    d=join(d,limb(p,a,b,.028-v*.017),.035);
   }
  }
  float id=0.;
  for(int i=0;i<2;i++){
   float s=i==0?-1.:1.;vec3 eye=p-vec3(s*.445,4.44,.25);
   eye.xy=mat2(.94,s*.342,-s*.342,.94)*eye.xy;
   float orbit=ell(eye,vec3(.29,.235,.19));
   orbit=max(orbit,-ell(eye-vec3(0.,0.,.045),vec3(.255,.195,.18)));
   d=join(d,orbit,.026);
   eye.z-=.045;
   float ed=ell(eye,vec3(.252,.186,.16))-.007*compoundLens(eye);
   if(ed<d){d=ed;id=1.;}
  }
  return vec2(d*.70,id);
 }
 vec3 normalAt(vec3 p){vec2 e=vec2(.0025,0.);return normalize(vec3(form(p+e.xyy).x-form(p-e.xyy).x,form(p+e.yxy).x-form(p-e.yxy).x,form(p+e.yyx).x-form(p-e.yyx).x));}
 void main(){
  vec3 ro=(localFromWorld*vec4(cameraPosition,1.)).xyz,rd=normalize(localSurface-ro);
  vec3 inv=1./rd,ta=(vec3(-1.7,-.2,-.8)-ro)*inv,tb=(vec3(1.7,5.8,2.5)-ro)*inv;
  vec3 lo=min(ta,tb),hi=max(ta,tb);float travel=max(0.,max(lo.x,max(lo.y,lo.z))),end=min(hi.x,min(hi.y,hi.z));
  vec3 p=ro;vec2 d;bool hit=false;
  for(int i=0;i<180;i++){p=ro+rd*travel;d=form(p);if(d.x<.0018){hit=true;break;}travel+=max(d.x,.0012);if(travel>end)break;}
  if(!hit)discard;
  vec3 q=living(p),n=normalAt(p),v=-rd,l=normalize(vec3(-.6,1.,1.5));
  vec3 film=.5+.5*cos(vec3(.2,2.3,4.2)+dot(n,v)*5.+q.y*.7-time*.28);
  float grain=dot(sin(q*38.+.25*sin(q.yzx*9.+time*.2)),cos(q.zxy*38.));
  float vein=exp(-pow(dot(sin(q*9.),cos(q.yzx*9.))*5.,2.));
  vec3 col=mix(vec3(.025,.12,.085),vec3(.10,.35,.23),.5+.5*sin(q.y*2.8+time*.25));
  col+=film*.07+vec3(.19,.22,.06)*vein*.12;
  col*=.98+.02*grain;
  if(d.y>.5){
   col=vec3(.008,.055,.044)+film*.035;
   float s=q.x<0.?-1.:1.;vec3 eye=q-vec3(s*.445,4.44,.25);
   eye.xy=mat2(.94,s*.342,-s*.342,.94)*eye.xy;eye.z-=.045;
   float cells=compoundLens(eye);
   col+=vec3(.045,.18,.12)*cells;
  }
  float diffuse=.30+.75*max(dot(n,l),0.);
  float ao=clamp(form(p+n*.09).x/.063,.3,1.);
  col*=diffuse*ao;
  col+=mix(vec3(.42,.73,.62),film,.35)*pow(max(dot(n,normalize(l+v)),0.),d.y>.5?80.:38.)*.7;
  col+=film*pow(1.-abs(dot(n,v)),3.)*.17;
  vec4 world=worldFromLocal*vec4(p,1.);vec4 clip=projectionMatrix*viewMatrix*world;
  gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,1.);gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const volume=new T.Mesh(new T.BoxGeometry(3.4,6.,3.3).translate(0,2.8,.85),skin);
 volume.userData.evidence=[evidence];body.add(volume);materials.push(skin);
 volume.onBeforeRender=()=>{skin.uniforms.worldFromLocal.value.copy(volume.matrixWorld);skin.uniforms.localFromWorld.value.copy(volume.matrixWorld).invert();};
 return {kind,g,body,joints,engaged:false,evidence,seed};
}
window.GeometricBeings={create,offering,createWaitingUsher,createContactBeing,createClinicalBeing};
})();
