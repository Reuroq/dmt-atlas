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
   // Nested folded sheets: an editorial unfolding-flower interpretation.
   // Near sheets stay outside the walking corridor; inner folds lie beyond exit.
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x);
    float nearest=100.;
    for(int j=0;j<7;j++){
     float layer=float(j);
     // A conservative slab bound avoids evaluating distant folded sheets.
     // Includes every wave, curl, opening and cup displacement below.
     float baseZ=-12.-layer*8.+radial*.42;
     float extent=(1.2+radial*.24)*1.18+8.4;
     float slab=(abs(p.z-baseZ)-extent)/5.5-.12;
     if(slab>nearest)continue;
     float phase=angle*8.+layer*2.13+radial*.32-time*.23;
     float opening=.5+.5*sin(time*.32-layer*.57);
     float petal=.5+.5*cos(phase);
     float inner=j<3?4.45+layer*.12:max(0.,3.8-(layer-3.)*1.3);
     float rim=inner+(j<6?2.7:0.)*petal*petal;
     // Three scales of cupped folds displace the surface itself. Their curved
     // rims share the parent's opening phase, rather than decorating a flat sheet.
     float wave=sin(phase)+.18*sin(phase*2.+radial*.58+opening);
     float rise=radial*.42+(1.2+radial*.24)*wave;
     float curl=3.4*sin(radial*.55-layer*.8-opening*1.7)*petal;
     float cupPhase=phase*2.+sin(radial*.6-opening)*1.2;
     float cupRadius=radial*.95+sin(phase)*.8-opening*1.6;
     float bowl=(.5+.5*cos(cupPhase))*(.5+.5*cos(cupRadius));
     float cups=2.5*bowl*(2.-bowl);
     float small=(.5+.5*cos(cupPhase*2.7))*(.5+.5*cos(cupRadius*2.7));
     cups+=.65*small*(2.-small);
     if(high>.5)cups+=.27*(.5+.5*cos(cupPhase*3.7))*(.5+.5*cos(cupRadius*3.7));
     float sheetZ=-12.-layer*8.+rise+curl+opening*1.5-cups;
     float sheet=abs(p.z-sheetZ)/5.5-.12;
     float outer=25.-layer*1.6+1.5*sin(phase);
     float boundary=max((rim-radial)*.5,(radial-outer)*.4);
     // Rounded, branching openings are missing material, not dark surface ink.
     // Shared spatial phases let some gaps continue through the deeper folds;
     // their slow motion remains part of the same paused/reduced-motion clock.
     float gapPhase=angle*3.+sin(radial*.31)*.8-time*.07;
     float gapCross=radial*.48+sin(angle*5.)*.7-time*.09;
     float openingField=(cos(gapPhase)*cos(gapCross)-.58)*.8;
     boundary=max(boundary,min(openingField,(radial-5.2)*.4));
     nearest=min(nearest,roundedIntersection(sheet,boundary,.11));
    }
    return nearest*.8;
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
    for(int i=0;i<208;i++){
     if(i>=144&&high<.5)break;
     p=ro+rd*distanceAlong;d=field(p);
     if(abs(d)<.0015+distanceAlong*pixelScale*.4){hit=true;break;}
     distanceAlong+=max(abs(d)*.78,.008);
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     // Keep the normal stencil narrower than the sheet: crossing both sides
     // cancels the gradient and produces dark edge streaks.
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
