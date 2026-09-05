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
   // One connected, closed corolla: a radially ruffled tube with a rounded
   // axial end. No sector objects, backing planes, radial cuts or gap masks.
   // The meridian shear makes z(v) nonmonotone: the sheet folds back through
   // depth rather than merely displacing a single-valued projected surface.
   float sheet(vec3 p){
    p.y-=1.7;
    float r=length(p.xy),cap=min(p.z+27.5,0.);
    float u=length(vec2(r,cap))-7.;
    float a=atan(p.y,p.x)-time*.065;
    float pole=r*r/(r*r+1.);
    float v=p.z*.84+(1.45+.18*sin(time*.61))*u-time*.65;
    float petal=10.*a+.28*sin(v*.5+time*.37);
    float f=u-1.35*sin(v+.72*pole*cos(petal));
    f-=pole*(.45*cos(petal+.7*sin(v))
       +.22*sin(3.*v-2.*petal+.35*sin(petal+v))
       +.085*sin(8.*v+4.*petal)
       +.028*sin(21.*v-8.*petal));
    if(high>.5)f-=pole*.010*sin(55.*v+16.*petal);
    return f;
   }
   float field(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,min(p.z+27.5,0.)));
    // Total displacement <=2.143 plus .055 thickness: radial clearance
    // >=4.802 before the rounded cap begins, 5.5 units beyond the exit.
    float bound=abs(rho-7.)-2.198;
    if(bound>.3)return bound;
    // Conservative slope bound includes shear and all geometric frequencies.
    return (abs(sheet(p))-.055)/12.;
   }
   vec3 spectrum(float x){return .5+.5*cos(TAU*(x+vec3(0.,.333,.667)));}
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
    for(int i=0;i<256;i++){
     if(i>=176&&high<.5)break;
     p=ro+rd*distanceAlong;d=field(p);
     if(abs(d)<.00035+distanceAlong*pixelScale*.025){hit=true;break;}
     distanceAlong+=max(abs(d)*.9,.0005);
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     // Refine the hit before shading: coarse termination on thin volumes
     // otherwise prints march-step contours into the normal highlights.
     for(int refine=0;refine<3;refine++){
      distanceAlong+=field(ro+rd*distanceAlong)*.7;
     }
     p=ro+rd*distanceAlong;
     float e=clamp(distanceAlong*pixelScale*.18,.002,.012);
     vec2 k=vec2(1.,-1.);
     // Differentiate the smooth sheet, never the bound or absolute shell.
     // This avoids normal discontinuities at thin-sheet midplanes.
     vec3 normal=normalize(k.xyy*sheet(p+k.xyy*e)+k.yyx*sheet(p+k.yyx*e)+k.yxy*sheet(p+k.yxy*e)+k.xxx*sheet(p+k.xxx*e));
     if(dot(normal,rd)>0.)normal=-normal;
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.039+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     vec3 reflected=radiance(reflect(rd,normal));
     float fresnel=pow(1.-facing,3.);
     float recess=clamp(field(p+normal*.8)/.14,.3,1.);
     float light=max(0.,dot(normal,normalize(vec3(.6,.9,.7))));
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.24+.62*light+.14*facing)*mix(.55,1.,recess);
     color+=reflected*(.025+.12*fresnel);
     color+=mix(pigment,vec3(1.),.18)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),14.)*.24;
     float haze=1.-exp(-distanceAlong*.009);
     color=mix(color,vec3(.085,.008,.033),haze);
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // Real openings reveal dark distance; only the far axial centre glows.
     color=vec3(.001,.0005,.003)+vec3(.14,.025,.002)*exp(-45.*length(rd.xy));
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
