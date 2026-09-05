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
   // Distance to a bounded swept leaf, thickened on every edge. The ends taper
   // naturally; no subtraction planes, radial clipping or perforation masks.
   float leaf(vec3 q,float width,float reach,float curl,float thickness){
    float y=clamp(q.y,-reach,reach),t=y/reach;
    float w=width*sqrt(max(0.,1.-t*t))*(.86+.14*cos(t*6.));
    float x=clamp(q.x,-w,w);
    float z=-1.7+curl*t*t+.24*x*x+.27*sin(t*3.);
    // Graph distance divided by a bound on its gradient, including taper ends.
    float dz=(q.z-z)/sqrt(1.+pow(2.*curl/reach+.81/reach,2.)+pow(.48*width,2.));
    return length(vec3(q.x-x,q.y-y,dz))-thickness;
   }
   // Overlapping swept corollas share thick roots and split into smaller fronds.
   // Their mouths, branch intervals and tapered ends form the dark openings.
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x),nearest=100.;
    for(int j=0;j<9;j++){
     float layer=float(j),scale=1.-layer*.065;
     float breath=sin(time*.62-layer*.48);
     // First five full animated extents stay outside radius 4.45. The closing
     // corollas start beyond z=-22 (the physical exit), including their front tips.
     float centreR=layer<5.?max(10.4,12.8-layer*1.4):10.4-(layer-4.)*2.2;
     float centreZ=layer<5.?-6.-layer*3.6:-28.-(layer-5.)*3.8;
     float bound=length(vec2(radial-centreR,p.z-centreZ))-9.8*scale;
     if(bound>nearest)continue;
     float spin=time*.065+layer*.34;
     float sector=floor((angle-spin)/(.125*TAU)+.5)*(.125*TAU)+spin;
     vec2 axis=vec2(cos(sector),sin(sector));
     vec3 q=vec3(dot(p.xy,vec2(-axis.y,axis.x)),dot(p.xy,axis)-centreR,p.z-centreZ);
     q/=scale;
     float solid=leaf(q,4.8,5.4,2.5+breath*.65,.14);
     // Three paired branches emerge along the parent bowl. Each has an open
     // concavity and two attached finer folds; the roots meet the parent volume.
     for(int b=0;b<3;b++){
      float branch=float(b),s=.62-branch*.12;
      vec3 child=q-vec3(0.,(branch-1.)*2.65,0.);
      child.x=abs(child.x)-(1.5-branch*.28);
      child.z-=.24*pow(1.5-branch*.28,2.)+.16*pow((branch-1.)*2.65,2.);
      child.xy=rot(.42+branch*.13)*child.xy;
      child/=s;
      float twig=leaf(child,1.85,2.4,2.8+breath*.5,.14)*s;
      solid=smoothUnion(solid,twig,.24);
      if(high>.5||b<2){
       vec3 bud=child-vec3(0.,.25,-.55);
       bud.x=abs(bud.x)-.75;
       bud.xy=rot(-.48)*bud.xy;
       solid=smoothUnion(solid,leaf(bud/.38,1.05,1.9,2.1,.16)*s*.38,.11);
      }
     }
     solid*=scale;
     nearest=min(nearest,solid);
    }
    return nearest*.64;
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
     color+=mix(pigment,vec3(1.),.22)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),28.)*.48;
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
