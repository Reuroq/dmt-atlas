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
   // Value and analytic world-space gradient. Pixel filtering removes only
   // unresolved wrinkles; it is not a texture or a cut in the corolla.
   vec4 sheetSample(vec3 p){
    vec3 toEye=p-cameraWorld[3].xyz;
    float footprint=length(toEye)*pixelScale;
    vec3 footprintGradient=normalize(toEye)*pixelScale;
    p.y-=1.7;
    float r=length(p.xy),cap=min(p.z+27.5,0.);
    float rho=length(vec2(r,cap)),u=rho-7.;
    vec3 gu=vec3(p.xy,cap)/max(rho,.00001);
    float a=atan(p.y,p.x)-time*.065;
    float pole=r*r/(r*r+1.);
    vec3 gp=vec3(2.*p.xy,0.)/pow(r*r+1.,2.);
    vec3 ga=vec3(-p.y,p.x,0.)/max(r*r,.0000001);
    float shear=1.45+.18*sin(time*.61);
    float v=p.z*.84+shear*u-time*.65;
    vec3 gv=vec3(0.,0.,.84)+shear*gu;
    float petal=10.*a+.28*sin(v*.5+time*.37);
    vec3 gt=10.*ga+.14*cos(v*.5+time*.37)*gv;
    float phase=v+.72*pole*cos(petal);
    vec3 gphase=gv+.72*(gp*cos(petal)-pole*sin(petal)*gt);
    float f=u-1.35*sin(phase);
    vec3 g=gu-1.35*cos(phase)*gphase;
    phase=petal+.7*sin(v);gphase=gt+.7*cos(v)*gv;
    f-=.45*pole*cos(phase);
    g-=.45*(gp*cos(phase)-pole*sin(phase)*gphase);
    phase=3.*v-2.*petal+.35*sin(petal+v);
    gphase=3.*gv-2.*gt+.35*cos(petal+v)*(gt+gv);
    f-=.22*pole*sin(phase);
    g-=.22*(gp*sin(phase)+pole*cos(phase)*gphase);
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.085:(octave==1?.028:.010);
     float fv=octave==0?8.:(octave==1?21.:55.);
     float fa=octave==0?4.:(octave==1?-8.:16.);
     // Fixed global frequency estimates make the filter differentiable even
     // at the pole; include its derivative in the root solver and normals.
     float frequency=octave==0?32.:(octave==1?72.:180.);
     float q=footprint*frequency;
     float weight=exp(-.5*q*q);
     vec3 gw=-weight*frequency*frequency*footprint*footprintGradient;
     phase=fv*v+fa*petal;gphase=fv*gv+fa*gt;
     f-=amplitude*pole*weight*sin(phase);
     g-=amplitude*((gp*weight+pole*gw)*sin(phase)+pole*weight*cos(phase)*gphase);
    }
    return vec4(g,f);
   }
   float envelope(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,min(p.z+27.5,0.)));
    // Total displacement <=2.143 plus .055 thickness: radial clearance
    // >=4.802 before the rounded cap begins, 5.5 units beyond the exit.
    return abs(rho-7.)-2.198;
   }
   float raySlope(vec3 p,vec3 rd){
    // Bound the directional derivative over the NEXT .4 world units, not
    // just at this point. This remains valid near tangencies and at the cap.
    float transverse=length(rd.xy);
    float lower=max(0.,length(p.xy-vec2(0.,1.7))-.4*transverse);
    float poleSlope=transverse*(lower>.57736?2.*lower/pow(1.+lower*lower,2.):.65);
    float angular=transverse*(lower>1.?lower/(1.+lower*lower):.5);
    float radial=p.z-.4*abs(rd.z)>-27.5?transverse:1.;
    float meridian=.84*abs(rd.z)+(1.45+.18*sin(time*.61))*radial;
    float petalSlope=10.*angular+.14*meridian;
    float result=radial+1.35*(meridian+.72*(poleSlope+petalSlope));
    result+=.45*(poleSlope+petalSlope+.7*meridian);
    result+=.22*(poleSlope+3.*meridian+2.*petalSlope+.35*(petalSlope+meridian));
    result+=.085*(poleSlope+8.*meridian+4.*petalSlope);
    result+=.028*(poleSlope+21.*meridian+8.*petalSlope);
    if(high>.5)result+=.010*(poleSlope+55.*meridian+16.*petalSlope);
    return result+4.*pixelScale;
   }
   vec3 spectrum(float x){return .5+.5*cos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d){
    float a=atan(d.y,d.x),b=asin(clamp(d.z,-1.,1.));
    float silk=.5+.5*sin(a*5.+sin(b*7.+time*.12)*2.);
    vec3 jewel=mix(vec3(.025,.025,.13),vec3(.9,.22,.012),silk);
    jewel+=vec3(.1,.55,.8)*pow(.5+.5*sin(a*11.-b*13.+time*.18),18.);
    return jewel;
   }
   float traceRay(vec3 ro,vec3 rd,bool useNewton,out bool found){
    vec3 p;
    float distanceAlong=0.,previousAlong=0.,previousValue=0.;bool hit=false,havePrevious=false;
    vec4 sampleValue=vec4(0.);
    for(int i=0;i<4096;i++){
     if(useNewton&&i>=1024)break;
     p=ro+rd*distanceAlong;
     float bound=envelope(p);
     if(bound>.08){distanceAlong+=bound*.95;havePrevious=false;continue;}
     sampleValue=sheetSample(p);
     float value=sampleValue.w;
     if(havePrevious&&value*previousValue<0.){
      // A real sign bracket: bisection cannot walk off to another fold.
      float lo=previousAlong,hi=distanceAlong,lv=previousValue;
      for(int refine=0;refine<14;refine++){
       float mid=(lo+hi)*.5,mv=sheetSample(ro+rd*mid).w;
       if(mv*lv>0.){lo=mid;lv=mv;}else hi=mid;
      }
      distanceAlong=(lo+hi)*.5;hit=true;break;
     }
     if(abs(value)<.00015){hit=true;break;}
     float stepSize=min(.4,abs(value)*.95/raySlope(p,rd));
     if(useNewton&&abs(value)<.065){
      // Near-root Newton proposal; reject nonconverging or distant proposals.
      // Conservative marching remains the fallback, not a painted failed ray.
      float trial=distanceAlong;
      for(int refine=0;refine<6;refine++){
       vec4 s=sheetSample(ro+rd*trial);float derivative=dot(s.xyz,rd);
       if(abs(derivative)<.0001)break;
       trial-=clamp(s.w/derivative,-.08,.08);
       trial=clamp(trial,distanceAlong,distanceAlong+.24);
      }
      if(abs(sheetSample(ro+rd*trial).w)<.00015){distanceAlong=trial;hit=true;break;}
     }
     previousAlong=distanceAlong;previousValue=value;havePrevious=true;
     distanceAlong+=max(stepSize,.000001);
     if(distanceAlong>105.)break;
    }
    found=hit;return distanceAlong;
   }
   void main(){
    float column=floor(screenUV.x*3.),row=floor(screenUV.y*2.);
    float panel=(1.-row)*3.+column;
    vec2 uv=fract(screenUV*vec2(3.,2.))*2.-1.;
    uv.x*=2./3.;
    vec4 eye=inverseProjection*vec4(uv,1.,1.);
    vec3 rd=normalize((cameraWorld*vec4(normalize(eye.xyz/eye.w),0.)).xyz);
    vec3 ro=cameraWorld[3].xyz,p=ro;
    bool hit=false;
    float distanceAlong=traceRay(ro,rd,panel<4.5,hit);
    vec3 color;
    if(hit){
     p=ro+rd*distanceAlong;
     vec3 normal=normalize(sheetSample(p).xyz);
     if(dot(normal,rd)>0.)normal=-normal;
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.039+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     vec3 reflected=radiance(reflect(rd,normal));
     float fresnel=pow(1.-facing,3.);
     // Darken actual nearby re-entrant folds, never arbitrary angular masks.
     float side=sign(dot(sheetSample(p).xyz,normal)),recess=1.;
     for(int j=0;j<4;j++){
      float reach=.18*pow(2.,float(j));
      float clearance=side*sheetSample(p+normal*reach).w;
      recess-=.22*(1.-smoothstep(-.08,.08,clearance));
     }
     float light=max(0.,dot(normal,normalize(vec3(.6,.9,.7))));
     // Self-lit pigment keeps depth without reducing every recess to brown rock.
     color=pigment*(.06+.72*light+.14*facing)*recess;
     color+=reflected*(.015+.10*fresnel)*recess;
     color+=mix(pigment,vec3(1.),.18)*pow(max(0.,dot(reflect(rd,normal),normalize(vec3(.3,.8,.6)))),10.)*.18*recess;
     float haze=1.-exp(-distanceAlong*.009);
     color=mix(color,vec3(.085,.008,.033),haze);
     if(panel>.5&&panel<1.5 || panel>4.5)
      color=vec3(.72)*(.08+.75*light+.08*facing);
     if(panel>1.5&&panel<2.5)color=normal*.5+.5;
     if(panel>2.5&&panel<3.5)color=vec3(distanceAlong/55.);
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // Miss fallback is not evidence of an opening in the closed corolla.
     color=vec3(.001,.0005,.003)+vec3(.14,.025,.002)*exp(-45.*length(rd.xy));
     gl_FragDepthEXT=.999999;
    }
    if(panel>3.5&&panel<4.5){
     bool strictHit=false;
     float strictDistance=traceRay(ro,rd,false,strictHit);
     color=vec3(0.,.42,0.);
     if(hit&&strictHit){
      float delta=distanceAlong-strictDistance;
      if(delta>.002)color=vec3(1.,.6,0.);
      if(delta<-.002)color=vec3(.25,.1,1.);
     }else if(hit)color=vec3(1.,0.,0.);
     else if(strictHit)color=vec3(0.,1.,1.);
     else color=vec3(1.,0.,1.);
    }else if(!hit)color=vec3(1.,0.,1.);
    gl_FragColor=vec4(color,1.);
   }`});
  const volume=new T.Mesh(new T.PlaneGeometry(2,2),material);
  volume.frustumCulled=false;volume.renderOrder=-100;
  volume.userData.evidence=['geometry|The Chrysanthemum','geometry|Mandalas & symmetry fields','geometry|Breathing & Liquid Surfaces','geometry|Ultra-Detail & Infinite Resolution'];
  const drawingSize=new T.Vector2();
  volume.onBeforeRender=renderer=>{
   material.uniforms.high.value=FractalWorld.quality==='high'?1:0;
   material.uniforms.pixelScale.value=4*camera.projectionMatrixInverse.elements[5]/renderer.getDrawingBufferSize(drawingSize).y;
   material.uniforms.inverseProjection.value.copy(camera.projectionMatrixInverse);
   material.uniforms.cameraWorld.value.copy(camera.matrixWorld);
   material.uniforms.viewProjection.value.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
  };
  root.add(volume);materials.push(material);
  return volume;
 }
 window.ContinuousWorld={chrysanthemum};
})();
