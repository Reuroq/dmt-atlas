/* Continuous distance-field interpretation, not a witness image.
   Evidence: The Chrysanthemum, mandalas, breathing surfaces and ultra-detail.
   Camera rays use the actual walking camera; animation uses the shared pause clock. */
(() => {
 'use strict';
 const T=THREE;
 function chrysanthemum(root,materials,camera){
  const material=new T.ShaderMaterial({depthTest:true,depthWrite:true,extensions:{fragDepth:true},uniforms:{
   time:{value:0},high:{value:1},pixelScale:{value:.0016},inverseProjection:{value:new T.Matrix4()},cameraWorld:{value:new T.Matrix4()},viewProjection:{value:new T.Matrix4()}
  },vertexShader:`varying vec2 screenUV;void main(){screenUV=uv;gl_Position=vec4(position.xy,0.,1.);}`,
  fragmentShader:`
   precision highp float;
   varying vec2 screenUV;
   uniform float time,high,pixelScale;
   uniform mat4 inverseProjection,cameraWorld,viewProjection;
   const float TAU=6.28318530718;
   mat2 rot(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}
   // Nested folded sheets: an editorial unfolding-flower interpretation.
   // Near sheets stay outside the walking corridor; inner folds lie beyond exit.
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x);
    float nearest=100.;
    for(int j=0;j<7;j++){
     float layer=float(j);
     float phase=angle*8.+layer*2.13+radial*.19-time*.23;
     float opening=.5+.5*sin(time*.32-layer*.57);
     float petal=.5+.5*cos(phase);
     float inner=j<3?4.45+layer*.12:max(0.,3.8-(layer-3.)*1.3);
     float rim=inner+(j<6?1.7:0.)*petal*petal;
     // Broad cupped folds have subordinate folds in the actual surface, not bump noise.
     float wave=sin(phase)+.22*sin(phase*3.+radial*.38+opening);
     if(high>.5)wave+=.055*sin(phase*9.-radial*.64-opening*2.);
     float rise=radial*.84+(.6+radial*.16)*wave;
     float curl=2.3*sin(radial*.41-layer*.8-opening*1.7)*petal;
     float sheetZ=-12.-layer*8.+rise+curl+opening*1.5;
     float sheet=abs(p.z-sheetZ)/3.4-.10;
     nearest=min(nearest,max(sheet,(rim-radial)*.5));
    }
    return nearest*.8;
   }
   // Nonperiodic nested domain folds, evaluated at the ray hit, retain spatial parallax.
   vec3 ornament(vec3 p){
    p=p*.48+vec3(0.,0.,time*.035);
    float v=0.,ridge=0.,amp=.5;
    for(int j=0;j<7;j++){
     if(j>4&&high<.5)break;
     p.xy=rot(.71+float(j)*.17)*p.xy;
     p.yz=rot(.57)*p.yz;
     p=abs(p+vec3(.31,-.27,.19));
     float f=sin(p.x)*cos(p.y)+sin(p.y)*cos(p.z)+sin(p.z)*cos(p.x);
     v+=amp*f;
     ridge+=amp*exp(-abs(f)*12.);
     p=p*2.13+vec3(.71,1.17,-.43);amp*=.48;
    }
    return vec3(v,ridge,sin(v*14.+p.z*.002));
   }
   vec3 spectrum(float x){return .5+.5*cos(TAU*(x+vec3(0.,.14,.32)));}
   vec3 radiance(vec3 d){
    float a=atan(d.y,d.x),b=asin(clamp(d.z,-1.,1.));
    float silk=.5+.5*sin(a*5.+sin(b*7.+time*.12)*2.);
    vec3 jewel=mix(vec3(.025,.025,.13),vec3(.9,.22,.012),silk);
    jewel+=vec3(.1,.55,.8)*pow(.5+.5*sin(a*11.-b*13.+time*.18),18.);
    return jewel;
   }
   void main(){
    vec2 uv=screenUV*2.-1.;
    vec4 eye=inverseProjection*vec4(uv,1.,1.);
    vec3 rd=normalize((cameraWorld*vec4(normalize(eye.xyz/eye.w),0.)).xyz);
    vec3 ro=cameraWorld[3].xyz,p=ro;
    float distanceAlong=0.,d=0.;bool hit=false;
    for(int i=0;i<144;i++){
     if(i>=96&&high<.5)break;
     p=ro+rd*distanceAlong;d=field(p);
     if(abs(d)<.0015+distanceAlong*pixelScale*.4){hit=true;break;}
     distanceAlong+=max(abs(d)*.78,.008);
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     float e=.003+distanceAlong*pixelScale*.75;
     vec2 k=vec2(1.,-1.);
     vec3 normal=normalize(k.xyy*field(p+k.xyy*e)+k.yyx*field(p+k.yyx*e)+k.yxy*field(p+k.yxy*e)+k.xxx*field(p+k.xxx*e));
     vec3 o=ornament(p);
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=a*.12+p.z*.022+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.05+vec3(.018,.005,.025);
     vec3 reflected=radiance(reflect(rd,normal));
     float fresnel=pow(1.-facing,3.);
     float recess=clamp(1.-(.6-field(p+normal*.6)/.43)*.75-(1.5-field(p+normal*1.5)/.43)*.25,.18,1.);
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.35+.48*facing)*mix(.65,1.,recess);
     color+=reflected*(.12+.42*fresnel);
     color+=vec3(1.,.72,.32)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),64.)*.85;
     float haze=1.-exp(-distanceAlong*.009);
     color=mix(color,vec3(.085,.008,.033),haze);
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // The unresolved axial distance stays luminous rather than a hard black disc.
     color=vec3(.065,.004,.018)+vec3(.38,.09,.008)*exp(-24.*length(rd.xy));
     gl_FragDepthEXT=.999999;
    }
    gl_FragColor=vec4(color,1.);
   }`});
  const volume=new T.Mesh(new T.PlaneGeometry(2,2),material);
  volume.frustumCulled=false;volume.renderOrder=-100;
  volume.userData.evidence=['geometry|The Chrysanthemum','geometry|Mandalas & symmetry fields','geometry|Breathing & Liquid Surfaces','geometry|Ultra-Detail & Infinite Resolution'];
  const drawingSize=new T.Vector2();
  volume.onBeforeRender=renderer=>{
   material.uniforms.high.value=FractalWorld.quality==='high'?1:0;
   material.uniforms.pixelScale.value=2*camera.projectionMatrixInverse.elements[5]/renderer.getDrawingBufferSize(drawingSize).y;
   material.uniforms.inverseProjection.value.copy(camera.projectionMatrixInverse);
   material.uniforms.cameraWorld.value.copy(camera.matrixWorld);
   material.uniforms.viewProjection.value.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
  };
  root.add(volume);materials.push(material);
  return volume;
 }
 window.ContinuousWorld={chrysanthemum};
})();
