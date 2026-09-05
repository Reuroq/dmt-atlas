/* Procedural geometry, not witness imagery. Evidence is attached by the journey builder. */
(() => {
'use strict';
const T=THREE, TAU=Math.PI*2;
const palettes=[['#040921','#00eabf','#ffc24b'],['#240009','#ff174b','#ffd13b'],['#020f21','#08f5db','#b5ff57'],['#100027','#952bff','#ffb62d'],['#19051d','#ff297d','#ffe3a1']];
const vertex=`
varying vec2 vUv; varying vec3 vP,vN,vView; uniform float time,strength,relief;
void main(){
 vUv=uv;vP=position;vN=normal;
 float wave=sin(position.x*1.3+time*.31+sin(position.z*.7-time*.19));
 wave+=.5*sin(position.y*2.1-time*.28+cos(position.x*1.8));
 vec3 p=position+normal*wave*relief*strength;
 vec4 transformed=vec4(p,1.);
 #ifdef USE_INSTANCING
 transformed=instanceMatrix*transformed;
 #endif
 vec4 mv=modelViewMatrix*transformed;vView=mv.xyz;
 gl_Position=projectionMatrix*mv;
}`;
const fragment=`
precision highp float;
varying vec2 vUv;varying vec3 vP,vN,vView;
uniform float time,scale,strength,detail,alpha,radiance;uniform vec3 a,b,c;
mat2 rotate(float t){return mat2(cos(t),-sin(t),sin(t),cos(t));}
float line(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d)*.9,.001),abs(d));}
void main(){
 vec3 n=abs(normalize(vN));
 vec2 p=n.z>max(n.x,n.y)?vP.xy:(n.y>n.x?vP.xz:vP.zy);
 // Local position preserves the scale of ornament on wide and tall surfaces.
 p*=.22*sqrt(scale);float t=time*.19*strength;
 vec2 domain=p;
 p+=.18*strength*sin(p.yx*1.7+vec2(t,-t*.83));
 p+=.07*strength*sin(p.yx*3.7+sin(p*2.)+t*.7);
 vec2 q=p;float height=0.,vein=0.,inlay=0.,jewel=0.,weight=1.;
 for(int i=0;i<6;i++){
  if(float(i)>=detail)break;
  // Nested radial/diamond folds with coherent large cuts and finer engraved cuts.
  vec2 cell=fract(q+.5)-.5;
  float r=length(cell),ang=atan(cell.y,cell.x);
  float petal=r-(.29+.065*cos(ang*8.+t*.43+float(i)));
  float web=abs(cell.x)+abs(cell.y)-.46;
  float engraving=min(abs(petal),abs(web)*.7);
  float lod=1.-smoothstep(.12,.6,length(fwidth(q)));
  height+=weight*lod*(exp(-engraving*23.)*.52+exp(-r*r*38.)*.8);
  vein+=weight*lod*(line(petal,.011)+line(web,.008)*.5);
  inlay+=weight*lod*(line(petal+.065,.01)+exp(-r*r*55.)*.55);
  jewel+=weight*lod*exp(-r*r*110.);
  q=rotate(.7854+t*.015)*q*3.05+vec2(.21,-.08);
  weight*=.46;
 }
 // Small circuit-like incisions sit inside the folds, not on a flat checkerboard.
 vec2 glyph=abs(fract(q*1.7)-.5);
 float circuit=line(min(abs(glyph.x-.18),max(abs(glyph.y-.25),glyph.x-.27)),.017);
 float facet=pow(.5+.5*cos(height*9.+domain.x*.4-t),3.);
 float iridescence=.5+.5*sin(height*5.+length(domain)*.6-t*.5);
 vec3 enamel=mix(b,c,smoothstep(.62,.83,iridescence));
 vec3 col=a*.4+enamel*(.012+height*.045+facet*.04);
 col+=c*min(vein,1.6)*1.05+b*inlay*1.1;
 col+=mix(c,vec3(.01,1.,.8),smoothstep(.35,.65,iridescence))*jewel*.85;
 col+=enamel*circuit*.018;
 // Screen-space relief lighting puts a bright cut and a dark edge on every fold.
 vec2 slope=vec2(dFdx(height),dFdy(height))/max(length(vec2(dFdx(vView.x),dFdy(vView.y))),.015);
 float light=dot(normalize(vec3(-slope*.75,1.)),normalize(vec3(-.7,.9,1.3)));
 col*=.65+max(light,0.)*.55;
 col+=vec3(1.,.85,.59)*pow(max(light,0.),22.)*min(vein,.8)*.35;
 col=mix(a+col*.22,col,strength);
 gl_FragColor=vec4(col*radiance,alpha);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
}`;
function surface(palette,scale,strength,materials){
 const colors=palettes[palette%palettes.length];
 const m=new T.ShaderMaterial({side:T.DoubleSide,extensions:{derivatives:true},uniforms:{
  time:{value:0},scale:{value:scale},strength:{value:strength},detail:{value:quality==='high'?6:4},
  relief:{value:.075},alpha:{value:1},radiance:{value:.7},a:{value:new T.Color(colors[0])},b:{value:new T.Color(colors[1])},c:{value:new T.Color(colors[2])}
 },vertexShader:vertex,fragmentShader:fragment});
 materials.push(m);return m;
}
// Woven negative-curvature surfaces. The centre stays open for the actual walking route.
function vault(root,materials,motions,{radius=7,length=40,z=-10,palette=0,rush=false}={}){
 const rows=quality==='high'?96:60,cols=quality==='high'?128:80;
 const pos=[],uv=[],idx=[];
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const u=i/cols,v=j/rows,a=u*TAU;
  const scallop=.52*Math.cos(a*12+v*15)+.19*Math.cos(a*36-v*27);
  const r=radius+scallop+.5*Math.cos(v*TAU*5);
  pos.push(Math.cos(a)*r,Math.sin(a)*r+3,(v-.5)*length+z);uv.push(u,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const m=surface(palette,14,1,materials);m.uniforms.relief.value=.2;
 const shell=new T.Mesh(geo,m);root.add(shell);
 // Interlaced helical filaments give real parallax over the deeply folded enclosure.
 const points=[],colors=[];const color=new T.Color();
 for(let h=0;h<24;h++)for(let k=0;k<150;k++){
  for(const v of [k/150,(k+1)/150]){
   const a=h/24*TAU+Math.sin(v*13)*.17+v*TAU*(h%2?1:-1);
   const r=radius-.28+.22*Math.sin(v*40+h);
   points.push(Math.cos(a)*r,3+Math.sin(a)*r,z+(v-.5)*length);
   color.setHSL((h/24+v*.3)%1,.87,.51);colors.push(color.r,color.g,color.b);
  }
 }
 const wires=new T.BufferGeometry();wires.setAttribute('position',new T.Float32BufferAttribute(points,3));wires.setAttribute('color',new T.Float32BufferAttribute(colors,3));
 const weave=new T.LineSegments(wires,new T.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.52}));root.add(weave);
 motions.push(t=>{shell.rotation.z=Math.sin(t*.09)*.035;weave.rotation.z=t*(rush?.085:.016);});
 return shell;
}
// A sculpted chrysanthemum, built from recursively lobed folded petals, not rings.
function mandala(root,materials,motions,{z=-12,radius=6,palette=1}={}){
 const group=new T.Group();group.position.set(0,3,z);root.add(group);
 const pos=[],uv=[],idx=[],rows=20,cols=10;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const v=j/rows,u=i/cols*2-1;
  const width=Math.pow(Math.sin(Math.PI*v),.7)*(.8+.16*Math.cos(v*22));
  pos.push(u*width,v*3.3,.42*Math.sin(v*Math.PI)+.27*u*u*Math.sin(v*20));uv.push(i/cols,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const count=quality==='high'?320:192,m=surface(palette,24,1,materials);m.uniforms.relief.value=.13;
 const petals=new T.InstancedMesh(geo,m,count);petals.frustumCulled=false;group.add(petals);const dummy=new T.Object3D();
 motions.push(t=>{
  for(let i=0;i<count;i++){
   const per=32,layer=Math.floor(i/per),a=i%per/per*TAU+layer*.31+t*.012*(layer%2?1:-1);
   const s=1-layer*.063,r=radius*(1-layer*.067)+.15*Math.sin(t*.4+layer*.6);
   dummy.position.set(Math.sin(a)*r,Math.cos(a)*r,-layer*.5);
   dummy.rotation.set(.55+Math.sin(t*.27+layer*.6)*.38,Math.sin(a*3+t*.13)*.17,-a+Math.PI);
   dummy.scale.set(.5*s,1.2*s,.9*s);dummy.updateMatrix();petals.setMatrixAt(i,dummy.matrix);
  }
  petals.instanceMatrix.needsUpdate=true;group.rotation.z=Math.sin(t*.08)*.1;
 });return group;
}
// Open, recursively divided canopy: thin interwoven ribs leave the vault visible.
function lattice(root,materials,motions,{radius=14,z=-4,height=11,palette=3}={}){
 const s=structures(root,materials,{palette}),arms=quality==='high'?18:12,steps=12;
 const V=(x,y,z)=>new T.Vector3(x,y,z);
 function fork(a,dir,len,r,depth,phase){
  const b=a.clone().addScaledVector(dir,len);s.segment(a,b,r);
  if(!depth)return;
  for(const side of [-1,1]){
   const next=dir.clone().multiplyScalar(.7).add(V(Math.cos(phase)*side,.42,Math.sin(phase)*side)).normalize();
   fork(b,next,len*.52,r*.54,depth-1,phase+1.1);
  }
 }
 for(let arm=0;arm<arms;arm++)for(const side of [-1,1]){
  const phase=arm/arms*TAU;
  const point=u=>{const a=phase+side*u*TAU/arms*.82,r=radius*(.83-.14*Math.sin(u*Math.PI))+.16*Math.sin(u*TAU+phase);
   return V(Math.cos(a)*r,Math.sin(u*Math.PI)*2.7+u*.9+side*.13,Math.sin(a)*r);};
  for(let j=0;j<steps;j++){
   const u=j/steps,a=point(u),b=point((j+1)/steps);s.segment(a,b,.07*(1-u*.68));
   if(j%2===1){const radial=V(Math.cos(phase)*side*.65,.7,Math.sin(phase)*side*.65).normalize();
    fork(b,radial,.65+Math.sin(u*Math.PI)*.7,.029,quality==='high'?2:1,phase+u*2);
   }
  }
 }
 const canopy=s.finish();canopy.position.set(0,height-1.2,z);
 motions.push(t=>{canopy.rotation.y=Math.sin(t*.055)*.09;canopy.scale.y=1+Math.sin(t*.24)*.035;});return canopy;
}
// Spatial folds share an inexpensive vein shader; depth comes from the mesh, not tiled medallions.
function veinMaterial(palette,materials,{floral=false}={}){
 const colors=palettes[palette%palettes.length];
 const m=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{time:{value:0},radiance:{value:.7},surfaceMode:{value:0},floral:{value:floral?1:0},a:{value:new T.Color(colors[0])},b:{value:new T.Color(colors[1])},c:{value:new T.Color(colors[2])}},vertexShader:`
 varying vec3 vP,vN,vView;uniform float time;
 void main(){vP=position;vec3 n=normal;vec4 p=vec4(position,1.);
 #ifdef USE_INSTANCING
 mat3 basis=mat3(instanceMatrix);n=basis*(n/vec3(dot(basis[0],basis[0]),dot(basis[1],basis[1]),dot(basis[2],basis[2])));p=instanceMatrix*p;
 #endif
 p.x+=.065*sin(p.y*.8+time*.32)*smoothstep(0.,2.,p.y);p.z+=.055*sin(p.y*1.2-time*.24)*smoothstep(0.,2.,p.y);
 vN=normalize(normalMatrix*n);vec4 mv=modelViewMatrix*p;vView=mv.xyz;gl_Position=projectionMatrix*mv;
 }`,fragmentShader:`
 varying vec3 vP,vN,vView;uniform float time,radiance,surfaceMode,floral;uniform vec3 a,b,c;
 float cut(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d),.002),abs(d));}
 void main(){vec3 n=normalize(vN);float light=.2+.8*abs(dot(n,normalize(vec3(-.6,.8,1.))));
 float mid=cut(vP.x,.018)*(1.-surfaceMode);float vein=0.;vec2 p=vP.xy;
 p+=surfaceMode*vec2(sin(p.y*.73+sin(p.x*.4)),sin(p.x*.63-p.y*.3))*1.3;
 for(int i=0;i<4;i++){float k=pow(2.7,float(i));float d=sin((p.y-abs(p.x)*.66)*k*13.+sin(p.x*k*3.)+time*.15);vein+=cut(d,.045)/(1.+float(i)*1.9);p.x=abs(p.x)-.17/k;}
 float hue=.5+.5*sin(vP.y*2.+sin(vP.x*3.-vP.y*.7)*2.+time*.14);vec3 enamel=mix(b,c,pow(hue,5.)*.65);
 float rim=pow(1.-abs(dot(n,normalize(-vView))),3.);vec3 col=a*.5+enamel*(.045+light*.13)+c*mid*.7+enamel*vein*.5+enamel*rim*.3;
 col=mix(col,b*(.28+light*.22)+c*vein*.16,floral*.6);col*=mix(1.,.42,surfaceMode);
 gl_FragColor=vec4(col*radiance*1.65,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(m);return m;
}
function foldedLeaf(){
 const pos=[],uv=[],idx=[],rows=12,cols=6;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const v=j/rows,u=i/cols*2-1,w=Math.pow(Math.sin(v*Math.PI),.8)*(1+.18*Math.cos(v*Math.PI*12));
  pos.push(u*w*.38,v,.25*Math.sin(v*Math.PI)+Math.abs(u)*w*.23+Math.cos(u*Math.PI*3)*w*.06);uv.push(i/cols,v);
  if(j<rows&&i<cols){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();return geo;
}
function structures(root,materials,{palette=2}={}){
 const group=new T.Group();root.add(group);const stems=[],leaves=[],up=new T.Vector3(0,1,0);
 function segment(a,b,r){const d=b.clone().sub(a);stems.push({p:a.clone().add(b).multiplyScalar(.5),q:new T.Quaternion().setFromUnitVectors(up,d.clone().normalize()),s:new T.Vector3(r,d.length(),r)});}
 function leaf(a,b,width=1,roll=0){const d=b.clone().sub(a),q=new T.Quaternion().setFromUnitVectors(up,d.clone().normalize());q.multiply(new T.Quaternion().setFromAxisAngle(up,roll));leaves.push({p:a.clone(),q,s:new T.Vector3(d.length()*width,d.length(),d.length()*.65)});}
 function finish(){const mat=veinMaterial(palette,materials),dummy=new T.Object3D();
  for(const [parts,geo] of [[stems,new T.CylinderGeometry(.5,1,1,5,1)],[leaves,foldedLeaf()]]){
   if(!parts.length){geo.dispose();continue;}const batch=new T.InstancedMesh(geo,mat,parts.length);
   parts.forEach((p,i)=>{dummy.position.copy(p.p);dummy.quaternion.copy(p.q);dummy.scale.copy(p.s);dummy.updateMatrix();batch.setMatrixAt(i,dummy.matrix);});batch.computeBoundingSphere();group.add(batch);
  }return group;
 }return {group,segment,leaf,finish};
}
// Recursive fronds split at several scales; the centre path is kept free below head height.
function growth(root,materials,motions,{x=0,y=0,z=0,height=7,spread=3,palette=2,seed=0}={}){
 const s=structures(root,materials,{palette}),V=(x,y,z)=>new T.Vector3(x,y,z);
 const depth=quality==='high'?3:2;
 function branch(a,dir,len,r,level,phase){
  const b=a.clone().addScaledVector(dir,len);s.segment(a,b,r);
  if(level===0){s.leaf(a,b,1.1,phase);return;}
  for(let k=0;k<3;k++){
   const angle=phase+k*2.399,origin=a.clone().lerp(b,.4+k*.19);
   const outward=V(Math.cos(angle)*spread/height,.48,Math.sin(angle)*spread/height).normalize();
   branch(origin,outward,len*(level===depth?.57:.49),r*.52,level-1,angle+1.3);
   if(level<depth)s.leaf(origin,origin.clone().addScaledVector(outward,len*.63),.72,angle);
  }
 }
 branch(V(0,0,0),V(.08*Math.sin(seed),1,.05*Math.cos(seed)).normalize(),height,.15*height/7,depth,seed);
 const g=s.finish();g.position.set(x,y,z);motions.push(t=>{g.rotation.y=Math.sin(t*.12+seed)*.055;g.scale.y=1+Math.sin(t*.25+seed)*.025;});return g;
}
// Garden variants: creek/flowers (DMT/1kcu4uv), folding light (o4e5yd),
// clockwork garden terrace (jqvq0s). A synthesis, not one shared reported place.
function gardenDetails(root,materials,motions){
 const g=new T.Group();root.add(g);g.userData.evidence=['realm|The Garden'];
 const pos=[],uv=[],indices=[],bankPos=[],bankIndices=[],rows=160,cols=12;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const z=16-j/rows*36,u=i/cols*2-1,pond=Math.exp(-Math.pow((z-4)/3.4,2));
  const center=-4.15+.65*Math.sin(z*.27)-pond*.9,width=.88+pond*1.7;
  pos.push(center+u*width,.035,z);uv.push(i/cols,z);
  if(j<rows&&i<cols){const k=j*(cols+1)+i;indices.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
  if(i===0)for(const side of [-1,1]){
   for(let k=0;k<3;k++)bankPos.push(center+side*(width+k*.2),k===1?.085:k===0?.035:-.02,z);
   if(j<rows)for(let k=0;k<2;k++){const a=j*6+(side===1?3:0)+k;bankIndices.push(a,a+1,a+6,a+1,a+7,a+6);}
  }
 }
 const bankGeo=new T.BufferGeometry();bankGeo.setAttribute('position',new T.Float32BufferAttribute(bankPos,3));bankGeo.setIndex(bankIndices);bankGeo.computeVertexNormals();g.add(new T.Mesh(bankGeo,veinMaterial(2,materials)));
 const waterGeo=new T.BufferGeometry();waterGeo.setAttribute('position',new T.Float32BufferAttribute(pos,3));waterGeo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));waterGeo.setIndex(indices);waterGeo.computeVertexNormals();
 const water=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{time:{value:0},radiance:{value:.7}},vertexShader:`
 varying vec2 vUv;uniform float time;
 void main(){vUv=uv;vec3 p=position;p.y+=.024*sin(p.z*4.-time*1.7+sin(p.x*7.));gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}
 `,fragmentShader:`
 varying vec2 vUv;uniform float time,radiance;
 void main(){vec2 p=vec2(vUv.x*5.,vUv.y);float flow=p.y-time*.65;
 float ripple=sin(flow*7.+sin(p.x*5.+sin(flow*.7))*2.2);
 float fine=sin(flow*27.+sin(p.x*17.-flow*1.3)*2.);
 float glint=pow(.5+.5*ripple,24.)*.24+pow(.5+.5*fine,28.)*.1;
 float bank=pow(abs(vUv.x*2.-1.),12.);float reflection=.5+.5*sin(p.x*8.+sin(flow*.8)*2.);
 vec3 col=mix(vec3(.008,.055,.16),vec3(.015,.39,.37),reflection*.7);
 col+=vec3(.24,.85,1.)*glint+vec3(.12,.3,.22)*bank*(.25+.15*sin(flow*3.));
 gl_FragColor=vec4(col*(.7+radiance),1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(water);g.add(new T.Mesh(waterGeo,water));
 // Multi-tier corollas open at different phases; all plants stay outside x ±2.6.
 const flowers=quality==='high'?84:48,per=quality==='high'?30:21;
 const petals=new T.InstancedMesh(foldedLeaf(),veinMaterial(4,materials,{floral:true}),flowers*per);
 petals.frustumCulled=false;g.add(petals);const dummy=new T.Object3D(),blooms=[],facing=new T.Quaternion().setFromEuler(new T.Euler(.5,0,0));
 const stems=structures(g,materials,{palette:2}),V=(x,y,z)=>new T.Vector3(x,y,z);
 for(let n=0;n<flowers;n++){
  const side=n%2?1:-1,z=11-Math.floor(n/2)*.74,x=side*(3.5+(n%5)*1.42),y=.8+(n%4)*.33;
  blooms.push({x,y,z,phase:n*2.399,size:.46+(n%3)*.13});
  stems.segment(V(x,0,z),V(x,y,z),.033);stems.leaf(V(x,y*.25,z),V(x+side*.45,y*.72,z+.2),.8,n);
 }
 stems.finish();
 motions.push(t=>{
  blooms.forEach((b,n)=>{const opened=.5+.5*Math.sin(t*.48+b.phase),sway=.09*Math.sin(t*.32+b.phase);
   for(let k=0;k<per;k++){
    const layer=Math.floor(k/(per/3)),a=k/(per/3)*TAU+layer*.38,tilt=.24+opened*1.02+layer*.13;
    dummy.position.set(b.x+sway,b.y+layer*.065,b.z);dummy.rotation.set(0,a,tilt);
    dummy.quaternion.premultiply(facing);
    const s=b.size*(1-layer*.21);dummy.scale.set(s*.9,s,s);dummy.updateMatrix();petals.setMatrixAt(n*per+k,dummy.matrix);
   }
  });petals.instanceMatrix.needsUpdate=true;
 });
 // A small lateral brick terrace, with actual treads and articulated gearing.
 const terrace=new T.Group();terrace.position.set(8,0,-1);g.add(terrace);
 const brickMat=veinMaterial(1,materials),blocks=[];
 for(let row=0;row<9;row++)for(let col=0;col<6;col++)blocks.push([ -2.2+col*.86+(row%2)*.16,.25+row*.43,-2.7,.8,.39,.5]);
 blocks.push([0,.62,0,4.8,1.24,5.2]);
 for(let i=0;i<6;i++)blocks.push([0,(i+1)*.105,5.2-i*.44,2,(i+1)*.21,.46]);
 const masonry=new T.InstancedMesh(new T.BoxGeometry(1,1,1),brickMat,blocks.length);
 blocks.forEach((b,i)=>{dummy.position.set(...b.slice(0,3));dummy.rotation.set(0,0,0);dummy.scale.set(...b.slice(3));dummy.updateMatrix();masonry.setMatrixAt(i,dummy.matrix);});masonry.computeBoundingSphere();terrace.add(masonry);
 const iron=structures(terrace,materials,{palette:3});
 for(const x of [-2.25,2.25]){for(let z=-2.4;z<=2.5;z+=.6)iron.segment(V(x,1.24,z),V(x,2.2,z),.033);iron.segment(V(x,2.2,-2.4),V(x,2.2,2.5),.045);}
 iron.finish();
 const mechanism=new T.Group();mechanism.position.set(-2.4,2.1,2.5);terrace.add(mechanism);
 function gear(radius,teeth,x,y,speed){
  const shape=new T.Shape();
  for(let i=0;i<=teeth*4;i++){const a=i/(teeth*4)*TAU,r=radius*(i%4===1||i%4===2?1:.85);const px=Math.cos(a)*r,py=Math.sin(a)*r;if(i===0)shape.moveTo(px,py);else shape.lineTo(px,py);}
  const hole=new T.Path();hole.absarc(0,0,radius*.66,0,TAU,true);shape.holes.push(hole);
  const wheel=new T.Group();wheel.position.set(x,y,0);mechanism.add(wheel);
  const mat=veinMaterial(3,materials);wheel.add(new T.Mesh(new T.ExtrudeGeometry(shape,{depth:.14,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.024,bevelThickness:.025,curveSegments:32}),mat));
  const ribs=structures(wheel,materials,{palette:3});
  for(let k=0;k<6;k++){const a=k/6*TAU;ribs.segment(V(0,0,.08),V(Math.cos(a)*radius*.72,Math.sin(a)*radius*.72,.08),.045);}
  ribs.finish();motions.push(t=>{wheel.rotation.z=t*speed;});
 }
 gear(.92,24,0,0,.12);gear(.61,16,1.39,.03,-.18);gear(.46,12,.06,1.29,-.24);
 const lever=new T.Group();lever.position.set(1.39,.03,.24);mechanism.add(lever);
 const handle=structures(lever,materials,{palette:1});handle.segment(V(0,0,0),V(.15,1.35,0),.075);handle.segment(V(.15,1.35,0),V(.48,1.35,0),.1);handle.finish();
 motions.push(t=>{lever.rotation.z=Math.sin(t*.36)*.5;});return g;
}
// Workshop variants: 1nenuqr pistons/cogs; 3d1lik clockwork manufacturing;
// 18te7qt white box-carriers; z270gs white-on-black boxed-body grid.
// A synthesis of distinct reports, not a single universal factory layout.
function workshopDetails(root,materials,motions){
 const g=new T.Group();root.add(g);
 const white=new T.MeshBasicMaterial({color:0xe9edf0}),black=new T.MeshBasicMaterial({color:0x090b12});
 const steel=new T.MeshStandardMaterial({color:0x8dabb4,metalness:.8,roughness:.28});
 const gold=new T.MeshStandardMaterial({color:0xffb631,emissive:0x9b4104,emissiveIntensity:.35,metalness:.7,roughness:.3});
 const pattern=veinMaterial(1,materials),unit=new T.BoxGeometry(1,1,1);
 function box(parent,material,x,y,z,w,h,d){const m=new T.Mesh(unit,material);m.position.set(x,y,z);m.scale.set(w,h,d);parent.add(m);return m;}
 // The monochrome wing has a legible quiet backdrop, not just white highlights.
 box(g,white,12,-.03,-30,15,.14,88);box(g,white,19.8,8,-30,.25,16,88);
 box(g,black,12,8,-30,15,.18,88);
 const shape=new T.Shape(),teeth=20;
 for(let i=0;i<=teeth*4;i++){const a=i/(teeth*4)*TAU,r=i%4===1||i%4===2?1:.85;const x=Math.cos(a)*r,y=Math.sin(a)*r;if(i===0)shape.moveTo(x,y);else shape.lineTo(x,y);}
 const hole=new T.Path();hole.absarc(0,0,.62,0,TAU,true);shape.holes.push(hole);
 const gearGeo=new T.ExtrudeGeometry(shape,{depth:.18,bevelEnabled:true,bevelSize:.025,bevelThickness:.025,bevelSegments:1,curveSegments:24,steps:1});
 function gear(parent,x,y,z,r,material){
  const wheel=new T.Group();wheel.position.set(x,y,z);wheel.scale.setScalar(r);parent.add(wheel);wheel.add(new T.Mesh(gearGeo,material));
  for(let k=0;k<5;k++){const spoke=box(wheel,material,0,0,.09,1.4,.09,.16);spoke.rotation.z=k*Math.PI/5;}
  box(wheel,steel,0,0,.14,.27,.27,.26);return wheel;
 }
 const packets=[],presses=[],wheels=[],workers=[];
 for(const side of [-1,1])for(const [index,z] of [7,-1,-9,-19,-31,-45,-61].entries()){
  const station=new T.Group();station.position.set(side*7,0,z);g.add(station);
  const mono=side===1,frame=mono?white:gold,body=mono?black:steel;
  box(station,body,0,1.35,0,4.4,.35,5.6);
  for(const x of [-1.9,1.9]){box(station,frame,x,.65,0,.23,1.3,5.4);box(station,frame,x,3.05,-1.6,.24,3.5,.3);}
  box(station,frame,0,4.8,-1.6,4.1,.28,.5);
  box(station,body,0,4.05,-1.6,.65,1.25,.65);
  const piston=new T.Group();station.add(piston);box(piston,steel,0,3.3,-1.6,.24,1.45,.24);box(piston,frame,0,2.62,-1.6,1.65,.23,1.35);
  presses.push({piston,phase:index*.81+side});
  // Long parallel rails, transverse rollers and products make the transport direction readable.
  for(const x of [-1.3,1.3])box(station,frame,x,1.62,0,.12,.2,5.6);
  for(let k=0;k<12;k++)box(station,steel,0,1.57,-2.5+k*.45,2.4,.13,.12);
  for(let k=0;k<3;k++){
   const packet=new T.Group();station.add(packet);box(packet,mono?white:pattern,0,0,0,.85,.8,.85);
   for(const x of [-.3,0,.3])box(packet,mono?black:gold,x,.405,0,.035,.02,.8);
   packets.push({packet,phase:k/3+index*.117});
  }
  // Front-facing meshing wheels remain distinct from the patterned casing.
  const a=gear(station,-.8,2.4,2.95,.88,frame),b=gear(station,.65,2.4,2.95,.66,frame);
  wheels.push({wheel:a,speed:.41,phase:index},{wheel:b,speed:-.41*.88/.66,phase:index+.08});
  // Tiny boxed carriers beside larger products give an explicit local scale comparison.
  if(mono){const worker=new T.Group();worker.position.set(-1.78,1.55,.4);station.add(worker);
   box(worker,white,0,.46,0,.26,.3,.2);box(worker,white,0,.73,0,.24,.24,.24);
   for(const x of [-.09,.09])box(worker,white,x,.19,0,.07,.3,.08);
   for(const x of [-.2,.2])box(worker,white,x,.49,.13,.08,.08,.36);
   box(worker,white,0,.52,.4,.34,.3,.3);workers.push({worker,phase:index});
  }
  // Repeated structural frames recede far beyond the original exit portal.
  box(g,frame,side*4.3,5.8,z-3,.18,11.6,.22);box(g,frame,side*12,5.8,z-3,.18,11.6,.22);
  box(g,frame,side*8.15,11.5,z-3,8,.22,.22);
  if(index>2)box(g,body,side*7,1.3,z+4,4.4,.3,5.8);
 }
 motions.push(t=>{
  for(const {wheel,speed,phase} of wheels)wheel.rotation.z=t*speed+phase;
  for(const {piston,phase} of presses)piston.position.y=.46*Math.sin(t*1.17+phase);
  for(const {packet,phase} of packets)packet.position.set(0,2.03,((t*.073+phase)%1)*4.8-2.4);
  for(const {worker,phase} of workers)worker.position.z=.4+Math.sin(t*.63+phase)*.6;
 });
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=['realm|The Workshop / Factory / Market'];});return g;
}
// Rib cages grow into fan vaults, with recursive spurs and folded webs between the ribs.
function arcade(root,materials,motions,{x=0,z=0,width=16,height=10,ry=0,palette=3}={}){
 const s=structures(root,materials,{palette}),V=(x,y,z)=>new T.Vector3(x,y,z),r=width/2;
 for(const side of [-1,1])for(let rail=0;rail<3;rail++){
  let a=V(side*(r+(rail-1)*.13),0,(rail-1)*.38);
  for(let j=1;j<=9;j++){
   const t=j/9,inset=Math.pow(Math.max(0,(t-.48)/.52),1.6)*r;
   const b=V(side*(r-inset+(rail-1)*.13),height*t,(rail-1)*(.38+Math.sin(t*Math.PI)*.45));s.segment(a,b,.11+(1-t)*.06);
   if(j>2){const end=b.clone().add(V(-side*width*.07,height*.075,rail===1?.35:(rail-1)*.9));s.segment(b,end,.055);s.leaf(a,end,.65,side*.7);
    for(let k=0;k<3;k++){const c=b.clone().lerp(end,.3+k*.25),tip=c.clone().add(V(-side*width*.027,height*.027,(k-1)*.23));s.segment(c,tip,.023);s.leaf(c,tip,.8,k);}}
   a=b;
  }
 }
 const g=s.finish();g.position.set(x,0,z);g.rotation.y=ry;return g;
}
// A pleated, branching relief skin: substantial silhouette depth instead of a smooth plane.
function panel(root,materials,{w=10,h=10,x=0,y=0,z=0,rx=0,ry=0,palette=3,depth=.65,ground=false}={}){
 const cols=Math.ceil(w*3),rows=Math.ceil(h*3),pos=[],uv=[],idx=[];
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const u=i/cols,v=j/rows,px=(u-.5)*w,py=(v-.5)*h;
  const fold=Math.abs(Math.sin(px*1.3+Math.sin(py*.65)*1.7))+.38*Math.abs(Math.sin(px*3.7-py*1.8));
  // Passage edges curl into the enclosure; shallow central relief leaves walking clear.
  const bank=ground?Math.pow(Math.abs(px)/(w*.5),4)*(.65+.25*Math.sin(py*.47)):0;
  const swell=ground?0:.28*Math.sin(px*.37+py*.21)*Math.cos(py*.43);
  pos.push(px,py,depth*(fold-.6+swell)+bank);uv.push(u,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const m=new T.Mesh(geo,veinMaterial(palette,materials));m.material.uniforms.surfaceMode.value=1;m.position.set(x,y,z);m.rotation.set(rx,ry,0);root.add(m);return m;
}
// Connected, nonliteral script grows along curved carriers in several depth planes.
function language(root,materials,motions){
 const s=structures(root,materials,{palette:1}),V=(x,y,z)=>new T.Vector3(x,y,z),count=quality==='high'?42:28;
 for(let layer=0;layer<3;layer++)for(const side of [-1,1]){
  const point=u=>V(side*(2.1+u*3.5+layer*.42),3.15+Math.sin(u*5.4+layer*.7)*.65+layer*.7,-1-u*10-layer*.8);
  let last=point(0);
  for(let j=1;j<=count;j++){
   const u=j/count,p=point(u);s.segment(last,p,.022);last=p;
   const rise=.22+.3*(.5+.5*Math.sin(j*2.399+layer)),bend=side*(.14+.08*Math.cos(j));
   const a=p.clone().add(V(bend,rise*.55,.035)),b=p.clone().add(V(bend*.6,rise,.08));
   s.segment(p,a,.018);s.segment(a,b,.013);
   for(let k=0;k<3;k++){
    const q=a.clone().lerp(b,k/3),tip=q.clone().add(V(side*(.12-k*.025),.035,-.10));
    s.segment(q,tip,.009);s.segment(tip,tip.clone().add(V(-side*.04,.08,.035)),.006);
   }
   if(j%3===0){const q=point(Math.min(1,u+1/count)).add(V(0,-rise*.7,.10));s.segment(p,q,.012);s.segment(q,q.clone().add(V(side*.18,.04,.08)),.008);}
  }
 }
 const g=s.finish();g.traverse(o=>{if(o.material){o.material.userData.entity=true;o.material.uniforms.radiance.value=.8;}});
 motions.push(t=>{g.rotation.y=Math.sin(t*.1)*.06;g.position.y=Math.sin(t*.3)*.09;g.scale.z=1+Math.sin(t*.17)*.06;});return g;
}
function cabinet(root,materials,{x=0,z=-3,w=2,h=4,d=18}={}){
 const s=structures(root,materials,{palette:2}),V=(x,y,z)=>new T.Vector3(x,y,z);
 for(let k=0;k<=d*2;k++){
  const z0=-d/2+k*.5;
  for(const side of [-1,1]){let a=V(side*w/2,0,z0);
   for(let j=1;j<=6;j++){const b=V(side*(w/2-.16*Math.sin(j*Math.PI/3)),j*h/6,z0+(j%2)*.18);s.segment(a,b,.055);s.leaf(a,b,Math.min(1.15,3/h),side*Math.PI/2);a=b;}
   s.leaf(V(side*w/2,h,z0),V(0,h+.12,z0),.7,0);
  }
 }
 const g=s.finish();g.position.set(x,0,z);return g;
}
// Spatial samples of one contour at delayed phases, not retained image frames.
function timeLayers(root,materials,motions,{z=0,palette=2,loosening=false}={}){
 const group=new T.Group();root.add(group);
 for(let layer=0;layer<3;layer++){
  const s=structures(group,materials,{palette}),steps=quality==='high'?30:20;
  for(const side of [-1,1]){
   const point=u=>new T.Vector3(side*(3.7+.6*Math.sin(u*TAU*1.3)),.2+u*8,.4*Math.sin(u*TAU));
   for(let j=0;j<steps;j++){
    const u=j/steps,a=point(u),b=point((j+1)/steps);s.segment(a,b,.055);
    if(j%2===0){const tip=b.clone().add(new T.Vector3(side*(.5+.3*Math.sin(u*9)),.4,.24));s.segment(b,tip,.024);s.leaf(b,tip,.3,side*u*3);}
   }
  }
  const contour=s.finish();
  motions.push(t=>{const moment=t-layer*1.8,spread=loosening?1.15+.12*Math.sin(moment*.15):1;
   contour.position.set(Math.sin(moment*.32)*.22,Math.sin(moment*.27)*.16,z-layer*3.4);
   contour.rotation.set(Math.sin(moment*.19)*.065,Math.sin(moment*.23)*.12,Math.sin(moment*.31)*.055);
   contour.scale.set(spread*(1+.075*Math.sin(moment*.4)),1+.05*Math.sin(moment*.4+1),1);
  });
 }
 return group;
}
let quality=matchMedia('(pointer: coarse)').matches?'low':'high';
// Small separable bloom pass. No history buffer: pause/reduced-motion frames stay identical.
function compositor(renderer){
 const options={type:T.HalfFloatType,depthBuffer:true};
 const target=new T.WebGLRenderTarget(1,1,options),blurA=new T.WebGLRenderTarget(1,1,{...options,depthBuffer:false}),blurB=blurA.clone();
 const quadScene=new T.Scene(),cam=new T.OrthographicCamera(-1,1,1,-1,0,1),quad=new T.Mesh(new T.PlaneGeometry(2,2));quadScene.add(quad);
 const passVertex='varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}';
 const blur=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{tex:{value:null},stepSize:{value:new T.Vector2()},threshold:{value:0}},vertexShader:passVertex,fragmentShader:`
 varying vec2 vUv;uniform sampler2D tex;uniform vec2 stepSize;uniform float threshold;
 vec3 sampleLight(vec2 p){vec3 c=texture2D(tex,p).rgb;return max(c-vec3(threshold),vec3(0.));}
 void main(){vec3 c=sampleLight(vUv)*.227027;c+=(sampleLight(vUv+stepSize*1.384615)+sampleLight(vUv-stepSize*1.384615))*.316216;c+=(sampleLight(vUv+stepSize*3.230769)+sampleLight(vUv-stepSize*3.230769))*.070270;gl_FragColor=vec4(c,1.);}`});
 const finish=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{tex:{value:target.texture},bloom:{value:blurB.texture},amount:{value:.2},time:{value:0},grain:{value:0},seam:{value:0},resolution:{value:new T.Vector2(1,1)}},vertexShader:passVertex,fragmentShader:`
 varying vec2 vUv;uniform sampler2D tex,bloom;uniform float amount,time,grain,seam;uniform vec2 resolution;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 void main(){vec2 p=vUv-.5;vec2 shift=p*dot(p,p)*amount*.002;
 float tick=floor(time*12.);vec2 cell=floor(vUv*resolution/1.6);
 float noise=hash(cell+vec2(tick,tick*.73));
 float boundary=exp(-abs(p.x+.026*sin(p.y*19.+time*.8))*(85.+noise*55.))*seam;
 vec2 uv=clamp(vUv+vec2((noise-.5)*boundary*.009,0.),vec2(0.),vec2(1.));
 vec3 col=texture2D(tex,uv).rgb;
 col.r=texture2D(tex,clamp(uv+shift,vec2(0.),vec2(1.))).r;col.b=texture2D(tex,clamp(uv-shift,vec2(0.),vec2(1.))).b;
 col+=texture2D(bloom,vUv).rgb*amount*.47;
 col*=1.-dot(p,p)*.24;
 // Fine low-luminance grain and a narrow seam, without full-field flashing.
 col*=1.-grain*.18;
 col+=mix(vec3(.03,.22,.2),vec3(.6,.35,.16),noise)*pow(noise,9.)*grain;
 col+=vec3(.24,.48,.44)*boundary*(.15+.85*noise);
 gl_FragColor=vec4(col,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});
 let calls=0,triangles=0;
 function resize(){const size=renderer.getDrawingBufferSize(new T.Vector2());target.setSize(size.x,size.y);blurA.setSize(Math.max(1,size.x>>2),Math.max(1,size.y>>2));blurB.setSize(blurA.width,blurA.height);finish.uniforms.resolution.value.copy(size);}
 function render(scene,camera,intensity,time=0,grain=0,seam=0/*TIMING_INSERT_24_BEGIN*/,timingObserver=null/*TIMING_INSERT_24_END*/){
/*TIMING_INSERT_25_BEGIN*/if(timingObserver)timingObserver('composite:scene',true);/*TIMING_INSERT_25_END*/  renderer.setRenderTarget(target);renderer.render(scene,camera);calls=renderer.info.render.calls;triangles=renderer.info.render.triangles;/*TIMING_INSERT_26_BEGIN*/if(timingObserver)timingObserver('composite:scene',false);/*TIMING_INSERT_26_END*/
/*TIMING_INSERT_27_BEGIN*/if(timingObserver)timingObserver('composite:blur-horizontal',true);/*TIMING_INSERT_27_END*/  quad.material=blur;blur.uniforms.tex.value=target.texture;blur.uniforms.threshold.value=.48;blur.uniforms.stepSize.value.set(1/blurA.width,0);renderer.setRenderTarget(blurA);renderer.render(quadScene,cam);/*TIMING_INSERT_28_BEGIN*/if(timingObserver)timingObserver('composite:blur-horizontal',false);/*TIMING_INSERT_28_END*/
/*TIMING_INSERT_29_BEGIN*/if(timingObserver)timingObserver('composite:blur-vertical',true);/*TIMING_INSERT_29_END*/  blur.uniforms.tex.value=blurA.texture;blur.uniforms.threshold.value=0;blur.uniforms.stepSize.value.set(0,1/blurA.height);renderer.setRenderTarget(blurB);renderer.render(quadScene,cam);/*TIMING_INSERT_30_BEGIN*/if(timingObserver)timingObserver('composite:blur-vertical',false);/*TIMING_INSERT_30_END*/
/*TIMING_INSERT_31_BEGIN*/if(timingObserver)timingObserver('composite:finish',true);/*TIMING_INSERT_31_END*/  quad.material=finish;finish.uniforms.amount.value=intensity;finish.uniforms.time.value=time;finish.uniforms.grain.value=grain;finish.uniforms.seam.value=seam;renderer.setRenderTarget(null);renderer.render(quadScene,cam);/*TIMING_INSERT_32_BEGIN*/if(timingObserver)timingObserver('composite:finish',false);/*TIMING_INSERT_32_END*/
 }
 resize();return {resize,render,get calls(){return calls;},get triangles(){return triangles;}};
}
window.FractalWorld={surface,vault,mandala,lattice,growth,gardenDetails,workshopDetails,arcade,panel,cabinet,language,timeLayers,veinMaterial,compositor,get quality(){return quality;},setQuality(value){quality=value;}};
})();
