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
    float warp=2.6*cos(x)*cos(y)+.75*sin(xx)*cos(yy);
    vec3 gw=vec3(-2.21*sin(x)*cos(y)+1.275*cos(xx)*cos(yy),
                 -2.21*cos(x)*sin(y)-1.275*sin(xx)*sin(yy),0.);
    float shear=1.8+.22*sin(time*.61);
    // Stagger the depth of petal families so the corolla is not stacked rings.
    float v=p.z*1.18+shear*u-time*.57+cw*warp;
    vec3 gv=vec3(0.,0.,1.18)+shear*gu+gcw*warp+cw*gw;
    float stagger=5.*a+.45*p.z+time*.37;
    vec3 gs=5.*ga+vec3(0.,0.,.45);
    v+=1.4*pole*sin(stagger);
    gv+=1.4*(gp*sin(stagger)+pole*cos(stagger)*gs);
    float petal=18.*a+.32*sin(v*.5+time*.31);
    vec3 gt=18.*ga+.16*cos(v*.5+time*.31)*gv;
    float phase=v+1.25*pole*cos(petal);
    vec3 gphase=gv+1.25*(gp*cos(petal)-pole*sin(petal)*gt);
    float f=u-1.55*sin(phase);
    vec3 g=gu-1.55*cos(phase)*gphase;
    phase=petal+1.2*sin(v);gphase=gt+1.2*cos(v)*gv;
    f-=.4*pole*cos(phase);
    g-=.4*(gp*cos(phase)-pole*sin(phase)*gphase);
    // Each lip divides into smaller curled lobes that cross its parent fold.
    float branch=petal+.8*v-time*.43;
    vec3 gb=gt+.8*gv;
    phase=2.*petal-1.7*v+1.4*sin(branch);
    gphase=2.*gt-1.7*gv+1.4*cos(branch)*gb;
    f-=.52*pole*sin(phase);
    g-=.52*(gp*sin(phase)+pole*cos(phase)*gphase);
    phase=3.*petal+2.3*v+.8*sin(branch);
    gphase=3.*gt+2.3*gv+.8*cos(branch)*gb;
    f-=.24*pole*cos(phase);
    g-=.24*(gp*cos(phase)-pole*sin(phase)*gphase);
    // Nested crossed lobes, continuous and nonzero at the cap axis.
    float cx=1.7*p.x+.4*sin(v),cy=1.7*p.y-.4*cos(v);
    vec3 gx=vec3(1.7,0.,0.)+.4*cos(v)*gv;
    vec3 gy=vec3(0.,1.7,0.)+.4*sin(v)*gv;
    f-=.28*cw*cos(cx)*cos(cy);
    g-=.28*(gcw*cos(cx)*cos(cy)-cw*(sin(cx)*cos(cy)*gx+cos(cx)*sin(cy)*gy));
    float plane=sin(.8*p.x)+cos(.8*p.y);
    vec3 gplane=vec3(.8*cos(.8*p.x),-.8*sin(.8*p.y),0.);
    float chart=pole*sin(petal)+cw*plane;
    vec3 gchart=gp*sin(petal)+pole*cos(petal)*gt+gcw*plane+cw*gplane;
    for(int octave=0;octave<3;octave++){
     if(octave==2&&high<.5)break;
     float amplitude=octave==0?.18:(octave==1?.08:.035);
     float fv=octave==0?2.7:(octave==1?5.7:12.1);
     float fc=octave==0?2.:(octave==1?-4.:7.);
     float frequency=octave==0?30.:(octave==1?64.:130.);
     float q=footprint*frequency,weight=exp(-.5*q*q);
     vec3 gweight=-weight*frequency*frequency*footprint*footprintGradient;
     phase=fv*v+fc*chart;gphase=fv*gv+fc*gchart;
     f-=amplitude*weight*sin(phase);
     g-=amplitude*(gweight*sin(phase)+weight*cos(phase)*gphase);
    }
    return vec4(g,f);
   }
   float envelope(vec3 p){
    float r=length(p.xy-vec2(0.,1.7));
    float rho=length(vec2(r,.45*min(p.z+27.5,0.)));
    // |displacement| <=3.285. Clearance >=3.71 for z>=-27.5.
    // Scaled z is a contraction, so this remains a safe world-space bound.
    return abs(rho-7.)-3.29;
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
    float meridian=1.18*abs(rd.z)+(1.8+.22*sin(time*.61))*radial;
    if(cap)meridian+=3.35*capSlope+3.485*crosswise;
    meridian+=1.4*(poleSlope+5.*angular+.45*abs(rd.z));
    float petalSlope=18.*angular+.16*meridian;
    float result=radial+1.55*(meridian+1.25*(poleSlope+petalSlope));
    result+=.4*(poleSlope+petalSlope+1.2*meridian);
    result+=.52*(poleSlope+3.4*petalSlope+2.82*meridian);
    result+=.24*(poleSlope+3.8*petalSlope+2.94*meridian);
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
   vec3 spectrum(float x){return .5+.5*cos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d,float roughness){
    // Coloured jewel reflections stay narrow instead of washing petals white.
    float power=mix(38.,5.,roughness),energy=1./(1.+roughness);
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
     vec3 geometricNormal=normal,relief=vec3(0.);
     float engraving=0.,reliefWeight=0.;
     // Nested, flowing intaglio: surface relief, not extra silhouette geometry.
     vec3 axisX=vec3(.8,.6,0.),axisY=vec3(-.36,.48,.8),axisZ=vec3(.48,-.64,.6);
     for(int layer=0;layer<4;layer++){
      if(layer==3&&high<.5)break;
      float scale=2.2*pow(2.17,float(layer));
      float detailFilter=exp(-.5*pow(distanceAlong*pixelScale*scale,2.));
      float weight=detailFilter*pow(.72,float(layer));
      vec3 q=vec3(dot(p,axisX),dot(p,axisY),dot(p,axisZ))*scale;
      q+=vec3(.17,-.23,.13)*time*(mod(float(layer),2.)<.5?1.:-1.);
      float warp=q.z*.7+time*.11;
      q.x+=.7*sin(warp);
      vec3 s=sin(q),c=cos(q);
      float cell=s.x*s.y+.45*c.z;
      vec3 slope=vec3(c.x*s.y,s.x*c.y,.49*cos(warp)*c.x*s.y-.45*s.z);
      relief+=weight*(axisX*slope.x+axisY*slope.y+axisZ*slope.z);
      engraving+=weight*exp(-14.*abs(cell));
      reliefWeight+=weight;
     }
     engraving/=max(reliefWeight,.001);
     normal=normalize(normal-.65*(relief-normal*dot(relief,normal)));
     if(dot(normal,rd)>0.)normal=-normal;
     float a=atan(p.y-1.7,p.x),facing=max(0.,dot(normal,-rd));
     float hue=.14*sin(a*3.+time*.12)+p.z*.039+time*.025;
     vec3 pigment=pow(spectrum(hue),vec3(2.2))*1.25+vec3(.012,.004,.018);
     float roughness=.08+.16*engraving;
     vec3 reflected=radiance(reflect(rd,normal),roughness);
     float fresnel=pow(1.-facing,3.);
     // Fold recesses suppress both ambient reflection and etched emission.
     float side=sign(dot(sheetSample(p).xyz,geometricNormal)),occlusion=0.;
     for(int j=0;j<3;j++){
      float reach=.12*pow(2.4,float(j));
      vec4 nearby=sheetSample(p+geometricNormal*reach);
      float clearance=side*nearby.w/max(1.,length(nearby.xyz));
      occlusion+=pow(.5,float(j))*clamp(1.-clearance/reach,0.,1.);
     }
     float openness=1.-.82*occlusion/1.75;
     vec3 key=normalize(vec3(.6,.9,.7));
     float visibility=1.;
     for(int j=0;j<4;j++){
      float reach=.24*pow(1.9,float(j));
      vec4 blocker=sheetSample(p+geometricNormal*.07+key*reach);
      float clearance=side*blocker.w/max(1.,length(blocker.xyz));
      visibility=min(visibility,mix(.18,1.,smoothstep(-reach*.25,reach*.2,clearance)));
     }
     // Broad lighting follows the actual sheet, not the tiny engraved normals.
     float light=max(0.,dot(geometricNormal,key));
     float foldRadius=length(vec2(length(p.xy-vec2(0.,1.7)),.45*min(p.z+27.5,0.)));
     float raisedLip=smoothstep(-.6,1.7,7.-foldRadius);
     float ridgeExposure=(.12+.88*raisedLip)*openness*(.35+.65*light);
     color=pigment*(.035+.12*openness+.62*light*visibility);
     color+=reflected*mix(vec3(.32),pigment,.7)*(1.1+1.8*fresnel)*openness;
     color+=pigment*pow(max(0.,dot(reflect(rd,normal),key)),56.)*1.3*visibility;
     vec3 ridge=spectrum(hue+.16+.12*fresnel);
     color+=ridge*engraving*(1.1+.7*fresnel)*ridgeExposure;
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
