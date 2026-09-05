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
window.GeometricBeings={create,offering};
})();
