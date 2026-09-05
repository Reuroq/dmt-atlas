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
   // Exact closest distance to a circular arc, swept with an elliptical solid
   // section. Endpoints have the same rounded section as the body: no graph
   // projection, taper singularity, backing sheet or subtraction edge.
   float sweep(vec3 q,float radius,float start,float turn,vec2 section){
    q.xy=rot(start+turn*.5-1.57079633)*q.xy;
    q.x=abs(q.x);
    vec2 end=vec2(sin(turn*.5),cos(turn*.5));
    float planar=end.y*q.x>end.x*q.y?length(q.xy-radius*end):abs(length(q.xy)-radius);
    return (length(vec2(planar,q.z*section.x/section.y))-section.x)*min(1.,section.y/section.x);
   }
   // A bifurcating rachis and its curled interiors are connected solids, not
   // motifs laid on a panel. Each child starts on its parent's centreline;
   // rotations pivot at that common root, so animation cannot detach it.
   float frond(vec3 q,float breath){
    q.x=abs(q.x);
    q.yz=rot(.22+breath*.16)*q.yz;
    q.xz=rot(.28)*q.xz;
    vec3 centre=vec3(0.,-1.,0.);
    float solid=sweep(q-centre,3.3,-1.57079633,3.55+breath*.18,vec2(.29,.72));
    for(int b=0;b<3;b++){
     float branch=float(b),a=-.92+branch*.91,r=1.12-branch*.19;
     vec3 root=centre+vec3(cos(a),sin(a),0.)*3.3;
     vec3 child=q-root;
     child.yz=rot(-.42+branch*.24+breath*.22)*child.yz;
     vec3 childCentre=-vec3(cos(a),sin(a),0.)*r;
     float curl=4.65+breath*.28;
     solid=smoothUnion(solid,sweep(child-childCentre,r,a,curl,vec2(.18,.43)),.22);
     if(high>.5||b<2){
      float twigAngle=a+2.1,twigR=r*.38;
      vec3 twigRoot=childCentre+vec3(cos(twigAngle),sin(twigAngle),0.)*r;
      vec3 twig=child-twigRoot;
      twig.xz=rot(.6+breath*.2)*twig.xz;
      vec3 twigCentre=-vec3(cos(twigAngle),sin(twigAngle),0.)*twigR;
      solid=smoothUnion(solid,sweep(twig-twigCentre,twigR,twigAngle,4.8,vec2(.095,.21)),.1);
     }
    }
    return solid;
   }
   float field(vec3 p){
    p.y-=1.7;
    float radial=length(p.xy),angle=atan(p.y,p.x),nearest=100.;
    for(int j=0;j<9;j++){
     float layer=float(j),scale=1.-layer*.065;
     float breath=sin(time*.62-layer*.48);
     // An eight-unit local sphere contains every animated branch, including
     // smooth unions. Near spheres leave >=4.6 units of radial clearance;
     // closing spheres lie wholly beyond the physical exit at z=-22.
     float centreR=layer<5.?4.6+8.*scale:max(.45,5.3-(layer-5.)*1.65);
     float centreZ=layer<5.?-5.-layer*4.1:-29.-(layer-5.)*3.4;
     float bound=length(vec2(radial-centreR,p.z-centreZ))-8.*scale;
     if(bound>nearest)continue;
     // Outside a bound use its conservative distance, but evaluate geometry
     // before approaching the hit epsilon so the bound cannot become a shell.
     if(bound>1.){nearest=min(nearest,bound);continue;}
     float spin=time*.065+layer*.34;
     float sector=floor((angle-spin)/(.125*TAU)+.5)*(.125*TAU)+spin;
     vec2 axis=vec2(cos(sector),sin(sector));
     vec3 q=vec3(dot(p.xy,vec2(-axis.y,axis.x)),dot(p.xy,axis)-centreR,p.z-centreZ);
     q/=scale;
     float solid=frond(q,breath)*scale;
     nearest=min(nearest,solid);
    }
    return nearest*.9;
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
     if(abs(d)<.0015+distanceAlong*pixelScale*.4){hit=true;break;}
     distanceAlong+=max(abs(d)*.9,.006);
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
