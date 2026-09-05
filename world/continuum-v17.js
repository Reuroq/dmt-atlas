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
   float roundedIntersection(float a,float b,float radius){
    float h=max(radius-abs(a-b),0.)/radius;
    return max(a,b)+h*h*radius*.25;
   }
   float smoothUnion(float a,float b,float radius){
    float h=max(radius-abs(a-b),0.)/radius;
    return min(a,b)-h*h*radius*.25;
   }
   // A capsule vault in a rigid local frame: rounded solid wall, open mouth.
   // No heightfield backing, angular displacement or spatially sheared cups.
   float vault(vec3 q,float radius,float reach,float thickness){
    vec3 spine=vec3(q.x,max(abs(q.y)-reach,0.),q.z);
    float shell=abs(length(spine)-radius)-thickness;
    float cut=radius*.28;
    shell=roundedIntersection(shell,q.z-cut,thickness*.65);
    float mouth=sqrt(radius*radius-cut*cut);
    float outline=length(vec2(q.x,max(abs(q.y)-reach,0.)));
    float lip=length(vec2(outline-mouth,q.z-cut))-thickness*1.22;
    return smoothUnion(shell,lip,thickness*.5);
   }
   // Seven interleaved rings of hollow petals. Every orientation is orthonormal
   // and constant across its petal, so walking reveals walls with real thickness.
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x),nearest=100.;
    for(int j=0;j<7;j++){
     float layer=float(j),scale=1.-layer*.085;
     float breath=sin(time*.62-layer*.48);
     float centreR=12.8-layer*1.63+breath*.45;
     float centreZ=-8.-layer*5.8;
     // Bounding sphere encloses parent, lips and both subordinate vaults.
     float bound=length(vec2(radial-centreR,p.z-centreZ))-8.7*scale;
     if(bound>nearest)continue;
     float spin=time*.065+layer*.293;
     float sector=floor((angle-spin)/(.125*TAU)+.5)*(.125*TAU)+spin;
     vec2 axis=vec2(cos(sector),sin(sector));
     vec3 q=vec3(dot(p.xy,vec2(-axis.y,axis.x)),dot(p.xy,axis)-centreR,p.z-centreZ);
     q.yz=rot(-.42+breath*.22+layer*.06)*q.yz;
     q/=scale;
     float solid=vault(q,3.25,3.8,.29);
     // Paired child chambers grow from the curved back, angled into the mouth.
     // Their smaller interior walls remain geometry at close range in both modes.
     vec3 child=vec3(abs(q.x)-1.13,q.y+.7,q.z+2.05);
     child.xz=rot(-.5-.12*breath)*child.xz;
     child.yz=rot(.32)*child.yz;
     solid=smoothUnion(solid,vault(child,1.16,1.28,.18),.2);
     if(high>.5){
      vec3 seed=child-vec3(.18,-.62,-.8);
      seed.yz=rot(-.48)*seed.yz;
      solid=smoothUnion(solid,vault(seed,.46,.42,.095),.09);
     }
     solid*=scale;
     // Keep the physical corridor empty. Deeper petals can close beyond its exit.
     float inner=j<3?4.45+layer*.12:0.;
     solid=max(solid,inner-radial);
     // Broad aligned gaps expose genuinely empty distance, not surface pigment.
     float gapPhase=angle*3.+sin(radial*.31)*.8-time*.07;
     float gapCross=radial*.48+sin(angle*5.)*.7-time*.09;
     float openingField=(cos(gapPhase)*cos(gapCross)-.58)*.8;
     solid=max(solid,min(openingField,(radial-5.2)*.4));
     nearest=min(nearest,solid);
    }
    return nearest*.72;
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
    for(int i=0;i<160;i++){
     if(i>=112&&high<.5)break;
     p=ro+rd*distanceAlong;d=field(p);
     if(abs(d)<.0015+distanceAlong*pixelScale*.4){hit=true;break;}
     distanceAlong+=max(abs(d)*.78,.008);
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     // Resolve the rounded wall gradient without crossing its full thickness.
     float e=clamp(.002+distanceAlong*pixelScale*.18,.004,.028);
     vec2 k=vec2(1.,-1.);
     vec3 normal=normalize(k.xyy*field(p+k.xyy*e)+k.yyx*field(p+k.yyx*e)+k.yxy*field(p+k.yxy*e)+k.xxx*field(p+k.xxx*e));
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.02+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     vec3 reflected=radiance(reflect(rd,normal));
     float fresnel=pow(1.-facing,3.);
     float recess=clamp(field(p+normal*.8)/.14,.3,1.);
     float light=max(0.,dot(normal,normalize(vec3(.6,.9,.7))));
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.24+.62*light+.14*facing)*mix(.55,1.,recess);
     color+=reflected*(.025+.12*fresnel);
     color+=mix(pigment,vec3(1.),.35)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),48.)*.9;
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
