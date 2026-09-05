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
   // Power-fractal corolla: each iteration grows geometry inside geometry.
   // Thirteen radial sectors, with no copied axial rings or ellipsoid petals.
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x);
    float sector=mod(angle+time*.055+p.z*.016+TAU/26.,TAU/13.)-TAU/26.;
    vec3 c=vec3((radial*cos(sector)-9.)/3.1,radial*sin(sector)/3.1,(p.z+12.)/17.5);
    c.z*=.87+.035*sin(time*.32);
    vec3 z=c;float dr=1.,r=0.;
    for(int j=0;j<9;j++){
     if(j>=6&&high<.5)break;
     r=length(z);
     if(r>3.)break;
     r=max(r,.00001);
     float theta=acos(clamp(z.z/r,-1.,1.));
     float phi=atan(z.y,z.x);
     float r7=pow(r,7.);
     dr=8.*r7*dr+1.;
     theta=theta*8.+.08*sin(time*.28);
     phi=phi*8.;
     z=r7*r*vec3(sin(theta)*cos(phi),sin(theta)*sin(phi),cos(theta))+c;
    }
    float fractal=.5*log(max(r,.00001))*r/max(dr,.00001)*3.1;
    // A safety clearance only: the recursive corolla itself sits outside it.
    float aperture=4.4+.1*sin(angle*8.+p.z*.2-time*.2);
    return max(fractal,aperture-radial)*.72;
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
     // Fine relief affects the reflection, not a grid of decorative lines.
     vec3 bump=vec3(ornament(p+vec3(e,0,0)).x-o.x,ornament(p+vec3(0,e,0)).x-o.x,ornament(p+vec3(0,0,e)).x-o.x)/e;
     normal=normalize(normal+.018*(bump-normal*dot(bump,normal)));
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.045+.16*sin(a*13.+p.z*.23-time*.17)+o.x*.045;
     float gold=.5+.5*sin(a*13.+p.z*.43-time*.28+o.x*.5);
     vec3 pigment=mix(vec3(.62,.006,.022),vec3(1.35,.48,.009),gold);
     vec3 reflected=radiance(reflect(rd,normal));
     float fresnel=pow(1.-facing,3.);
     float recess=clamp(1.-(.6-field(p+normal*.6)/.43)*.75-(1.5-field(p+normal*1.5)/.43)*.25,.18,1.);
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.26+.38*facing)*mix(.75,1.,recess);
     color+=reflected*(.17+.48*fresnel);
     color+=pigment*o.y*.18;
     color+=vec3(.9,.56,.16)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),48.)*.65;
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
