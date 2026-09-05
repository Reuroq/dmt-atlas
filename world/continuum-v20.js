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
   float smoothUnion(float a,float b,float radius){
    float h=max(radius-abs(a-b),0.)/radius;
    return min(a,b)-h*h*radius*.25;
   }
   // Ellipsoidal distance estimate: round in every direction, including tips.
   // No backing, angular cut mask, projected heightfield or circular inventory.
   float lobe(vec3 q){
    q.y-=1.25;
    vec3 r=vec3(.82,1.4,.38);
    float k0=length(q/r),k1=length(q/(r*r));
    return k0*(k0-1.)/max(k1,.0001);
   }
   // A binary corolla tree folded in its own moving joint frames. Each child
   // starts INSIDE its parent's volume; changing the joint angle folds the
   // smaller lobes over one another without detaching them. Five true spatial
   // scales in HIGH, four in LOW, all contributing to the visible silhouette.
   float frond(vec3 q,float breath){
    q.y=-q.y;
    q.yz=rot(.2+breath*.25)*q.yz;
    float solid=lobe(q),size=1.;
    for(int b=0;b<4;b++){
     if(b==3&&high<.5)break;
     float level=float(b);
     q.x=abs(q.x);
     q.y-=1.15;
     q.xy=rot(-.65-breath*.16-level*.08)*q.xy;
     q.yz=rot(.25+sin(time*.85+level*.95+breath)*.68)*q.yz;
     q/=.68;size*=.68;
     solid=smoothUnion(solid,lobe(q)*size,.19*size);
    }
    return solid;
   }
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x),nearest=100.;
    for(int j=0;j<11;j++){
     float layer=float(j),scale=1.-layer*.05;
     float breath=sin(time*.72-layer*.59);
     // Joint-frame rotations preserve the <4-unit tree bound (including
     // smooth unions). Near volumes stay outside radial4.6. Closing bounds
     // start beyond z=-25.2, safely past the physical exit at z=-22.
     float centreR=layer<6.?4.6+4.*scale:max(.2,6.5-(layer-6.)*1.5);
     float centreZ=layer<6.?5.-layer*4.5:-28.-(layer-6.)*3.1;
     float bound=length(vec2(radial-centreR,p.z-centreZ))-4.*scale;
     if(bound>nearest)continue;
     // Outside a bound use its conservative distance, but evaluate geometry
     // before approaching the hit epsilon so the bound cannot become a shell.
     if(bound>1.){nearest=min(nearest,bound);continue;}
     float spin=time*.075+layer*.29;
     float sector=floor((angle-spin)/(.1*TAU)+.5)*(.1*TAU)+spin;
     vec2 axis=vec2(cos(sector),sin(sector));
     vec3 q=vec3(dot(p.xy,vec2(-axis.y,axis.x)),dot(p.xy,axis)-centreR,p.z-centreZ);
     q/=scale;
     float solid=frond(q,breath)*scale;
     nearest=min(nearest,solid);
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
    for(int i=0;i<144;i++){
     if(i>=104&&high<.5)break;
     p=ro+rd*distanceAlong;d=field(p);
     if(abs(d)<.0007+distanceAlong*pixelScale*.12){hit=true;break;}
     distanceAlong+=max(abs(d)*.85,.001);
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
     float e=clamp(distanceAlong*pixelScale*.45,.006,.035);
     vec2 k=vec2(1.,-1.);
     vec3 normal=normalize(k.xyy*field(p+k.xyy*e)+k.yyx*field(p+k.yyx*e)+k.yxy*field(p+k.yxy*e)+k.xxx*field(p+k.xxx*e));
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.025+time*.025;
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
