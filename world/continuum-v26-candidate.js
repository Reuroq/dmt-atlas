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

float preciseSin(float x){
 x-=TAU*floor((x+3.14159265359)/TAU);
 if(x>1.57079632679)x=3.14159265359-x;
 else if(x< -1.57079632679)x=-3.14159265359-x;
 float q=x*x;
 return x*(1.+q*(-.166666666667+q*(.00833333333333+q*(-.000198412698413+q*(.0000027557319224+q*(-.0000000250521083854+q*.000000000160590438368))))));
}
float preciseCos(float x){
 x-=TAU*floor((x+3.14159265359)/TAU);float s=1.;
 if(x>1.57079632679){x=3.14159265359-x;s=-1.;}
 else if(x< -1.57079632679){x=-3.14159265359-x;s=-1.;}
 float q=x*x;
 return s*(1.+q*(-.5+q*(.0416666666667+q*(-.00138888888889+q*(.0000248015873016+q*(-.00000027557319224+q*.00000000208767569879))))));
}
vec3 preciseCos(vec3 x){return vec3(preciseCos(x.x),preciseCos(x.y),preciseCos(x.z));}
   mat2 rot(float a){float c=preciseCos(a),s=preciseSin(a);return mat2(c,-s,s,c);}
   // A connected corolla with a deep ellipsoidal end beyond the walk exit.
   // Cartesian cap folds survive at the axis: no angular pole fan is used
   // as the centre's only geometry. All octaves displace the actual sheet.
   vec4 sheetSample(vec3 p){
    vec3 toEye=p-cameraWorld[3].xyz;
    float footprint=length(toEye)*pixelScale;
    vec3 footprintGradient=normalize(toEye)*pixelScale;
    p.y-=1.7;
    float r=length(p.xy),cap=min(p.z+27.5,0.);
    float rho=length(vec2(r,.45*cap)),u=rho-7.;
    vec3 gu=vec3(p.xy,.2025*cap)/max(rho,.00001);
    float a=atan(p.y,p.x)-time*.065;
    vec3 ga=vec3(-p.y,p.x,0.)/max(r*r,.0000001);
    float pole=r*r/(r*r+4.);
    vec3 gp=vec3(8.*p.xy,0.)/pow(r*r+4.,2.);
    float cw=cap*cap/(cap*cap+4.);
    vec3 gcw=vec3(0.,0.,8.*cap/pow(cap*cap+4.,2.));
    float x=.85*p.x,y=.85*p.y;
    float xx=1.7*p.x+time*.19,yy=1.7*p.y-time*.17;
    float warp=2.6*preciseCos(x)*preciseCos(y)+.75*preciseSin(xx)*preciseCos(yy);
    vec3 gw=vec3(-2.21*preciseSin(x)*preciseCos(y)+1.275*preciseCos(xx)*preciseCos(yy),
                 -2.21*preciseCos(x)*preciseSin(y)-1.275*preciseSin(xx)*preciseSin(yy),0.);
    float shear=1.8+.22*preciseSin(time*.61);
    float v=p.z*.72+shear*u-time*.57+cw*warp;
    vec3 gv=vec3(0.,0.,.72)+shear*gu+gcw*warp+cw*gw;
    float petal=8.*a+.32*preciseSin(v*.5+time*.31);
    vec3 gt=8.*ga+.16*preciseCos(v*.5+time*.31)*gv;
    float phase=v+.65*pole*preciseCos(petal);
    vec3 gphase=gv+.65*(gp*preciseCos(petal)-pole*preciseSin(petal)*gt);
    float f=u-1.18*preciseSin(phase);
    vec3 g=gu-1.18*preciseCos(phase)*gphase;
    phase=petal+.6*preciseSin(v);gphase=gt+.6*preciseCos(v)*gv;
    f-=.4*pole*preciseCos(phase);
    g-=.4*(gp*preciseCos(phase)-pole*preciseSin(phase)*gphase);
    // Nested crossed lobes, continuous and nonzero at the cap axis.
    float cx=1.7*p.x+.4*preciseSin(v),cy=1.7*p.y-.4*preciseCos(v);
    vec3 gx=vec3(1.7,0.,0.)+.4*preciseCos(v)*gv;
    vec3 gy=vec3(0.,1.7,0.)+.4*preciseSin(v)*gv;
    f-=.28*cw*preciseCos(cx)*preciseCos(cy);
    g-=.28*(gcw*preciseCos(cx)*preciseCos(cy)-cw*(preciseSin(cx)*preciseCos(cy)*gx+preciseCos(cx)*preciseSin(cy)*gy));
    float plane=preciseSin(.8*p.x)+preciseCos(.8*p.y);
    vec3 gplane=vec3(.8*preciseCos(.8*p.x),-.8*preciseSin(.8*p.y),0.);
    float chart=pole*preciseSin(petal)+cw*plane;
    vec3 gchart=gp*preciseSin(petal)+pole*preciseCos(petal)*gt+gcw*plane+cw*gplane;
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.18:(octave==1?.08:.035);
     float fv=octave==0?2.7:(octave==1?5.7:12.1);
     float fc=octave==0?2.:(octave==1?-4.:7.);
     float frequency=octave==0?30.:(octave==1?64.:130.);
     float q=footprint*frequency,weight=exp(-.5*q*q);
     vec3 gweight=-weight*frequency*frequency*footprint*footprintGradient;
     phase=fv*v+fc*chart;gphase=fv*gv+fc*gchart;
     f-=amplitude*weight*preciseSin(phase);
     g-=amplitude*(gweight*preciseSin(phase)+weight*preciseCos(phase)*gphase);
    }
    return vec4(g,f);
   }
   float envelope(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,.45*min(p.z+27.5,0.)));
    // |displacement| <=2.155. Clearance >=4.84 for z>=-27.5.
    // Scaled z is a contraction, so this remains a safe world-space bound.
    return abs(rho-7.)-2.16;
   }
   float raySlope(vec3 p,vec3 rd){
    // Directional derivative bound throughout the next .4 world units.
    float transverse=length(rd.xy),crosswise=abs(rd.x)+abs(rd.y);
    float lower=max(0.,length(p.xy-vec2(0.,1.7))-.4*transverse);
    float poleSlope=transverse*(lower>1.15471?8.*lower/pow(4.+lower*lower,2.):.325);
    float angular=transverse*(lower>2.?lower/(4.+lower*lower):.25);
    bool cap=p.z-.4*abs(rd.z)<-27.5;
    float radial=cap?length(vec3(rd.xy,.45*rd.z)):transverse;
    float capSlope=cap?.325*abs(rd.z):0.;
    float meridian=.72*abs(rd.z)+(1.8+.22*preciseSin(time*.61))*radial;
    if(cap)meridian+=3.35*capSlope+3.485*crosswise;
    float petalSlope=8.*angular+.16*meridian;
    float result=radial+1.18*(meridian+.65*(poleSlope+petalSlope));
    result+=.4*(poleSlope+petalSlope+.6*meridian);
    if(cap)result+=.28*(capSlope+1.7*crosswise+.8*meridian);
    float chartSlope=poleSlope+petalSlope;
    if(cap)chartSlope+=2.*capSlope+.8*crosswise;
    float footprint=max(0.,length(p-cameraWorld[3].xyz)-.4)*pixelScale;
    result+=.18*exp(-.5*pow(footprint*30.,2.))*(2.7*meridian+2.*chartSlope);
    result+=.08*exp(-.5*pow(footprint*64.,2.))*(5.7*meridian+4.*chartSlope);
    if(high>.5)result+=.035*exp(-.5*pow(footprint*130.,2.))*(12.1*meridian+7.*chartSlope);
    // Max filter derivative: sum(amplitude*frequency)*exp(-.5)<9.2.
    return result+9.2*pixelScale;
   }
   vec3 spectrum(float x){return .5+.5*preciseCos(TAU*(x+vec3(0.,.333,.667)));}
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
    vec2 uv=screenUV*2.-1.;
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
     // Resolve within .08 pixel, capped at .0015 world units. This
     // avoids chasing subpixel grazing rims to floating-point exhaustion.
     // It is a local surface-distance estimate, not an exact-root proof.
     float tolerance=min(.0015,max(.00015,distanceAlong*pixelScale*.08));
     if(abs(value)<.00015 || abs(value)/max(1.,length(sampleValue.xyz))<tolerance){hit=true;break;}
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
     float hue=.14*preciseSin(a*3.+time*.12)+p.z*.039+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     float roughness=.32+.18*(1.-facing);
     vec3 reflected=radiance(reflect(rd,normal),roughness);
     float fresnel=pow(1.-facing,3.);
     // Normalized local field clearance estimates smooth near-field AO.
     // Bounded ambient attenuation only; never square it across material.
     float side=sign(dot(sheetSample(p).xyz,normal)),occlusion=0.;
     for(int j=0;j<3;j++){
      float reach=.12*pow(2.4,float(j));
      vec4 nearby=sheetSample(p+normal*reach);
      float clearance=side*nearby.w/max(1.,length(nearby.xyz));
      occlusion+=pow(.5,float(j))*clamp(1.-clearance/reach,0.,1.);
     }
     float openness=1.-.24*occlusion/1.75;
     vec3 key=normalize(vec3(.6,.9,.7));
     float visibility=1.;
     for(int j=0;j<4;j++){
      float reach=.24*pow(1.9,float(j));
      vec4 blocker=sheetSample(p+normal*.07+key*reach);
      float clearance=side*blocker.w/max(1.,length(blocker.xyz));
      visibility=min(visibility,mix(.18,1.,smoothstep(-reach*.25,reach*.2,clearance)));
     }
     float light=max(0.,dot(normal,key));
     // Emission and broad environment reflection are independent of key
     // visibility. Only diffuse/specular light from that key is shadowed.
     color=pigment*(.19+(.16+.12*facing)*openness+.68*light*visibility);
     color+=reflected*(.25+.55*fresnel)*mix(.85,1.,openness);
     color+=mix(pigment,vec3(1.),.4)*pow(max(0.,dot(reflect(rd,normal),key)),9.)*.42*visibility;
     float haze=1.-exp(-distanceAlong*.005);
     color=mix(color,vec3(.018,.002,.009),haze);
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // Miss fallback is not evidence of an opening in the closed corolla.
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
