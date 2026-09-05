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
    float pole=r*r/(r*r+4.);
    vec3 gp=vec3(8.*p.xy,0.)/pow(r*r+4.,2.);
    vec3 ga=vec3(-p.y,p.x,0.)/max(r*r,.0000001);
    float shear=1.45+.18*sin(time*.61);
    // Smooth axial meridian warp creates rounded nested folds at the cap.
    // It and its first derivative vanish at the tube/cap join, beyond exit.
    float capWeight=cap*cap/(cap*cap+4.),dome=exp(-.10*r*r);
    vec3 gdome=5.*dome*vec3(-.20*p.xy*capWeight,8.*cap/pow(cap*cap+4.,2.));
    float v=p.z*.84+shear*u-time*.65+5.*capWeight*dome;
    vec3 gv=vec3(0.,0.,.84)+shear*gu+gdome;
    float petal=10.*a+.28*sin(v*.5+time*.37);
    vec3 gt=10.*ga+.14*cos(v*.5+time*.37)*gv;
    float phase=v+.72*pole*cos(petal);
    vec3 gphase=gv+.72*(gp*cos(petal)-pole*sin(petal)*gt);
    float f=u-1.35*sin(phase);
    vec3 g=gu-1.35*cos(phase)*gphase;
    phase=petal+.7*sin(v);gphase=gt+.7*cos(v)*gv;
    f-=.45*pole*cos(phase);
    g-=.45*(gp*cos(phase)-pole*sin(phase)*gphase);
    phase=2.*v-petal+.6*sin(petal+v);
    gphase=2.*gv-gt+.6*cos(petal+v)*(gt+gv);
    f-=.32*pole*sin(phase);
    g-=.32*(gp*sin(phase)+pole*cos(phase)*gphase);
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.14:(octave==1?.06:.022);
     float fv=octave==0?2.8:(octave==1?6.5:14.);
     float fa=octave==0?1.:(octave==1?2.:-4.);
     // Fixed global frequency estimates make the filter differentiable even
     // at the pole; include its derivative in the root solver and normals.
     float frequency=octave==0?14.:(octave==1?32.:64.);
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
    // Displacement <=2.342, reserve .008: clearance >=4.65 before cap.
    // All new axial folding starts at -27.5, beyond the physical exit -22.
    return abs(rho-7.)-2.35;
   }
   float raySlope(vec3 p,vec3 rd){
    // Bound the directional derivative over the NEXT .4 world units, not
    // just at this point. This remains valid near tangencies and at the cap.
    float transverse=length(rd.xy);
    float lower=max(0.,length(p.xy-vec2(0.,1.7))-.4*transverse);
    float poleSlope=transverse*(lower>1.15471?8.*lower/pow(4.+lower*lower,2.):.325);
    float angular=transverse*(lower>2.?lower/(4.+lower*lower):.25);
    float radial=p.z-.4*abs(rd.z)>-27.5?transverse:1.;
    float meridian=.84*abs(rd.z)+(1.45+.18*sin(time*.61))*radial;
    if(p.z-.4*abs(rd.z)<-27.5){
     float domeRadial=lower>2.23607?.2*lower*exp(-.1*lower*lower):.27126;
     meridian+=5.*(domeRadial*transverse+.325*exp(-.1*lower*lower)*abs(rd.z));
    }
    float petalSlope=10.*angular+.14*meridian;
    float result=radial+1.35*(meridian+.72*(poleSlope+petalSlope));
    result+=.45*(poleSlope+petalSlope+.7*meridian);
    result+=.32*(poleSlope+2.*meridian+petalSlope+.6*(petalSlope+meridian));
    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;
    result+=.14*exp(-.5*pow(footprint*14.,2.))*(poleSlope+2.8*meridian+petalSlope);
    result+=.06*exp(-.5*pow(footprint*32.,2.))*(poleSlope+6.5*meridian+2.*petalSlope);
    if(high>.5)result+=.022*exp(-.5*pow(footprint*64.,2.))*(poleSlope+14.*meridian+4.*petalSlope);
    return result+4.*pixelScale;
   }
   vec3 spectrum(float x){return .5+.5*cos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d,float roughness){
    // Broad spherical area-light lobes: no periodic angular bands/seams.
    float power=mix(5.,1.4,roughness),energy=1./(1.+2.*roughness);
    vec3 jewel=vec3(.008,.012,.024);
    jewel+=vec3(1.4,.46,.07)*pow(max(0.,dot(d,normalize(vec3(-.7,.5,.4)))),power);
    jewel+=vec3(.08,.75,1.3)*pow(max(0.,dot(d,normalize(vec3(.6,-.3,.7)))),power);
    jewel+=vec3(.7,.09,.45)*pow(max(0.,dot(d,normalize(vec3(.1,.8,-.6)))),power);
    return jewel*energy;
   }
   void main(){
    float column=floor(screenUV.x*3.),row=floor(screenUV.y*2.);
    float panel=(1.-row)*3.+column;
    vec2 uv=fract(screenUV*vec2(3.,2.))*2.-1.;
    uv.x*=2./3.;
    vec4 eye=inverseProjection*vec4(uv,1.,1.);
    vec3 rd=normalize((cameraWorld*vec4(normalize(eye.xyz/eye.w),0.)).xyz);
    vec3 ro=cameraWorld[3].xyz,p=ro;
    float distanceAlong=0.,previousAlong=0.,previousValue=0.;bool hit=false,havePrevious=false;
    vec4 sampleValue=vec4(0.);
    for(int i=0;i<2048;i++){
     if(i>=1536&&high<.5)break;
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
     // No Newton root acceptance: every forward step retains the bound.
     // Residual tolerance and floating-point limits are still not a proof.
     previousAlong=distanceAlong;previousValue=value;havePrevious=true;
     distanceAlong+=stepSize;
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     p=ro+rd*distanceAlong;
     vec3 normal=normalize(sheetSample(p).xyz);
     if(dot(normal,rd)>0.)normal=-normal;
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.039+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     float roughness=.32+.18*(1.-facing);
     vec3 reflected=radiance(reflect(rd,normal),roughness);
     float fresnel=pow(1.-facing,3.);
     // Darken actual nearby re-entrant folds, never arbitrary angular masks.
     float side=sign(dot(sheetSample(p).xyz,normal)),recess=1.;
     for(int j=0;j<4;j++){
      float reach=.18*pow(2.,float(j));
      float clearance=side*sheetSample(p+normal*reach).w;
      recess-=.22*(1.-smoothstep(-.08,.08,clearance));
     }
     // Shadowing samples real material between the fold and the key light.
     // Finite sampling approximates visibility; never a painted gap mask.
     vec3 key=normalize(vec3(.6,.9,.7));
     float visibility=1.;
     for(int j=0;j<8;j++){
      float reach=.18*pow(1.65,float(j));
      float clearance=side*sheetSample(p+normal*.045+key*reach).w;
      visibility=min(visibility,smoothstep(-.10,.08,clearance));
     }
     if(panel>.5&&panel<1.5 || panel>2.5&&panel<3.5)visibility=1.;
     if(panel>1.5&&panel<3.5)recess=1.;
     float light=max(0.,dot(normal,key));
     float openness=recess*recess;
     color=pigment*(.018+.78*light*visibility+.12*facing*openness)*openness;
     color+=reflected*(.09+.28*fresnel)*openness*(.15+.85*visibility);
     color+=mix(pigment,vec3(1.),.25)*pow(max(0.,dot(reflect(rd,normal),key)),5.)*.24*visibility*openness;
     float haze=1.-exp(-distanceAlong*.005);
     color=mix(color,vec3(.018,.002,.009),haze);
     // Diagnostic channels bypass haze/material, but keep shared postprocessing.
     if(panel>3.5&&panel<4.5)color=normal*.5+.5;
     if(panel>4.5)color=vec3(clamp(distanceAlong/60.,0.,1.));
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // Miss fallback is not evidence of an opening in the closed corolla.
     color=vec3(.001,.0005,.003)+vec3(.14,.025,.002)*exp(-45.*length(rd.xy));
     if(panel>3.5)color=vec3(1.,0.,1.); // Explicit missed-ray marker.
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
