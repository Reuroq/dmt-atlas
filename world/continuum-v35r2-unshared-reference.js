/* Continuous distance-field interpretation, not a witness image.
   Evidence: The Chrysanthemum, mandalas, breathing surfaces and ultra-detail.
   Camera rays use the actual walking camera; animation uses the shared pause clock. */
(() => {
 'use strict';
 const T=THREE;
 function chrysanthemum(root,materials,camera){
  const material=new T.ShaderMaterial({depthTest:true,depthWrite:true,extensions:{fragDepth:true},uniforms:{
   childAxialOffset:{value:Math.fround(.20)},childAngularOffset:{value:Math.fround(.28)},time:{value:0},high:{value:1},pixelScale:{value:.0016},inverseProjection:{value:new T.Matrix4()},cameraWorld:{value:new T.Matrix4()},viewProjection:{value:new T.Matrix4()}
  },vertexShader:`varying vec2 screenUV;void main(){screenUV=uv;gl_Position=vec4(position.xy,0.,1.);}`,
  fragmentShader:`
   precision highp float;
   varying vec2 screenUV;
   uniform float time,high,pixelScale;
   uniform float childAxialOffset,childAngularOffset;
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
// Shared range reduction for the analytic jet; original polynomials unchanged.
vec2 preciseSinCos(float x){
 x-=TAU*floor((x+3.14159265359)/TAU);float s=1.;
 if(x>1.57079632679){x=3.14159265359-x;s=-1.;}
 else if(x< -1.57079632679){x=-3.14159265359-x;s=-1.;}
 float q=x*x;
 float sine=x*(1.+q*(-.166666666667+q*(.00833333333333+q*(-.000198412698413+q*(.0000027557319224+q*(-.0000000250521083854+q*.000000000160590438368))))));
 float cosine=s*(1.+q*(-.5+q*(.0416666666667+q*(-.00138888888889+q*(.0000248015873016+q*(-.00000027557319224+q*.00000000208767569879))))));
 return vec2(sine,cosine);
}
vec3 preciseCos(vec3 x){return vec3(preciseCos(x.x),preciseCos(x.y),preciseCos(x.z));}
   mat2 rot(float a){float c=preciseCos(a),s=preciseSin(a);return mat2(c,-s,s,c);}

   // Jets carry analytic Cartesian gradients in xyz, scalar value in w.
   // No angular chart or radial colour fan at the cap's axis.
   vec4 jc(vec4 q){vec2 sc=preciseSinCos(q.w);return vec4(-sc.x*q.xyz,sc.y);}
   vec4 jm(vec4 a,vec4 b){return vec4(a.xyz*b.w+b.xyz*a.w,a.w*b.w);}
   vec4 offset(vec4 a,float b){return vec4(a.xyz,a.w+b);}
   vec4 rose(vec4 x,vec4 y,float k){
    return (jc(k*x)+jc(k*(.5*x+.866025403784*y))+jc(k*(-.5*x+.866025403784*y)))/3.;
   }
   vec4 filtered(vec4 a,float frequency,vec3 p){
    vec3 delta=p-cameraWorld[3].xyz;
    float q=frequency*pixelScale,w=exp(-.5*q*q*dot(delta,delta));
    return jm(a,vec4(-q*q*w*delta,w));
   }

   // v35r2: clipped curled laminae with volumetrically attached child folds.
   // Every reach below belongs to a SMOOTH leaf, never to a max/abs crease.
   vec4 jis(vec4 v){float s=inversesqrt(v.w);return vec4(-.5*s*s*s*v.xyz,s);}
   void cubePair(vec4 x,vec4 y,out vec4 a,out vec4 b){
    vec4 xx=jm(x,x),yy=jm(y,y);
    a=jm(x,xx-3.*yy);b=jm(y,3.*xx-yy);
   }
   void jcs(vec4 q,out vec4 cosine,out vec4 sine){
    vec2 sc=preciseSinCos(q.w);
    cosine=vec4(-sc.x*q.xyz,sc.y);sine=vec4(sc.y*q.xyz,sc.x);
   }
   vec4 turnPair(vec4 a,vec4 b,vec4 phase){
    vec4 cosine,sine;jcs(phase,cosine,sine);
    return jm(a,cosine)-jm(b,sine);
   }
   vec4 jmax(vec4 a,vec4 b){return a.w>b.w?a:b;}
   struct CommonJets {
    vec4 radius;vec4 r6;vec4 i6;vec4 radial;vec4 local;
    vec4 cosLocal;vec4 sinLocal;
   };
   CommonJets commonParts(vec3 p){
    vec3 q=p-vec3(0.,1.7,0.);
    float angle=time*.075,c=preciseCos(angle),s=preciseSin(angle);
    vec4 x=vec4(c,-s,0.,c*q.x-s*q.y),y=vec4(s,c,0.,s*q.x+c*q.y);
    vec4 z=vec4(0.,0.,1.,q.z);
    float cap=min(q.z+27.5,0.),rho=length(vec3(q.xy,.85*cap));
    vec4 radius=vec4(vec3(q.xy,.7225*cap)/max(rho,.00001),rho);
    vec4 inv=jis(offset(jm(x,x)+jm(y,y),2.25));
    vec4 u=jm(x,inv),v=jm(y,inv),r3,i3;
    cubePair(u,v,r3,i3);
    vec4 r6=jm(r3,r3)-jm(i3,i3),i6=2.*jm(r3,i3);
    vec4 radial=offset(1.05*radius+.16*z+.10*r6,-time*.12);
    vec4 local=offset(.62*z-.28*radius+.12*i6,-time*.19);
    vec4 cosLocal,sinLocal;jcs(local,cosLocal,sinLocal);
    return CommonJets(radius,r6,i6,radial,local,cosLocal,sinLocal);
   }
   void cheapPartsShared(vec3 p,CommonJets sharedJetsState,out vec4 f,out vec4 axA,out vec4 axB){
    f=offset(-sharedJetsState.radius,6.2)+.4*sharedJetsState.r6;
    axA=offset(-sharedJetsState.cosLocal,-.62);axB=offset(axA,childAxialOffset);
   }
   void cheapParts(vec3 p,out vec4 f,out vec4 axA,out vec4 axB){
    cheapPartsShared(p,commonParts(p),f,axA,axB);
   }
   void fieldPartsReachShared(vec3 p,CommonJets sharedJetsState,out vec4 f,out vec4 a,out vec4 b,out vec4 axA,out vec4 axB,out vec4 angA,out vec4 angB,out vec4 shellA,out vec4 shellB){
    cheapPartsShared(p,sharedJetsState,f,axA,axB);
    vec4 r6=sharedJetsState.r6,i6=sharedJetsState.i6;
    vec4 radial=sharedJetsState.radial,local=sharedJetsState.local;
    vec4 cosLocal=sharedJetsState.cosLocal,sinLocal=sharedJetsState.sinLocal;
    vec4 r12=jm(r6,r6)-jm(i6,i6),i12=2.*jm(r6,i6);
    vec4 curl=radial+.92*sinLocal;
    vec4 phase=offset(.42*sinLocal+.16*jc(radial),time*.20);
    angA=offset(jm(r6,r6)+jm(i6,i6)-turnPair(r12,i12,phase),-.90);
    angB=offset(angA,childAngularOffset);
    // Shell thickness and petal silhouette are separate intersections.
    // The long fold is not squeezed into an oval by summed square costs.
    shellA=jc(curl)-.72*cosLocal;
    vec4 branchScale=offset(.24*filtered(jc(2.3*radial+.25*r6),4.,p),1.);
    if(high>.5){
     shellA+=.045*filtered(jc(4.3*radial+.35*r6),6.,p);
     branchScale+=.07*filtered(jc(6.1*local+.20*i6),9.,p);
    }
    // At cos(local)=1 the child shares the parent centreline exactly.
    // Nonzero shell thickness makes a finite overlap band around each root.
    vec4 shift=.30*jm(offset(-cosLocal,1.),branchScale);
    shellB=shellA-shift;
    a=jmax(jmax(offset(shellA,-.095),offset(-shellA,-.095)),jmax(axA,angA));
    b=jmax(jmax(offset(shellB,-.062),offset(-shellB,-.062)),jmax(axB,angB));
   }
   void fieldPartsReach(vec3 p,out vec4 f,out vec4 a,out vec4 b,out vec4 axA,out vec4 axB,out vec4 angA,out vec4 angB,out vec4 shellA,out vec4 shellB){
    fieldPartsReachShared(p,commonParts(p),f,a,b,axA,axB,angA,angB,shellA,shellB);
   }
   void fieldParts(vec3 p,out vec4 f,out vec4 a,out vec4 b){
    vec4 axA,axB,angA,angB,shellA,shellB;
    fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);
   }
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    vec4 parent=jmax(f,a),child=jmax(offset(f,.3),b),backing=offset(f,10.);
    vec4 result=parent;layer=0.;
    if(child.w<result.w){result=child;layer=1.;}
    if(backing.w<result.w){result=backing;layer=2.;}
    return result;
   }
   vec4 sheetSample(vec3 p){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);return compose(f,a,b,layer);
   }
   float envelope(vec3 p){
    float rho=length(vec3(p.xy-vec2(0.,1.7),.85*min(p.z+27.5,0.)));
    return max(0.,5.445-rho);
   }
   // Coefficientwise padded bounds generated from the independent calculus.
   // Valid along each <=.4 reach: rho>=5.365-.4=4.965.
   float raySlope(vec3 p,vec3 rd){return 9.0+2.0*pixelScale;}
   vec3 leafCurvature(){float s=pixelScale;return vec3(5.0,15.0,22.0)+vec3(1.0,4.0,11.0)*s+vec3(1.0,3.0,9.0)*s*s;}
   vec2 gateCurvature(){float s=pixelScale;return vec2(4.0,47.0)+vec2(1.0,1.0)*s+vec2(1.0,1.0)*s*s;}
   float positiveReach(vec4 leaf,vec3 rd,float curvature){
    if(leaf.w<=0.)return 0.;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   float cheapReach(vec3 p,vec3 rd,CommonJets sharedJetsState){
    vec4 f,axA,axB;cheapPartsShared(p,sharedJetsState,f,axA,axB);
    float m=leafCurvature().x,ax=gateCurvature().x;
    float parent=max(positiveReach(f,rd,m),positiveReach(axA,rd,ax));
    float child=max(positiveReach(offset(f,.3),rd,m),positiveReach(axB,rd,ax));
    return min(min(parent,child),positiveReach(offset(f,10.),rd,m));
   }
   vec4 traceSample(vec3 p,vec3 rd,CommonJets sharedJetsState,out float safeStep){
    vec4 f,a,b,axA,axB,angA,angB,shellA,shellB;float layer;
    fieldPartsReach(p,f,a,b,axA,axB,angA,angB,shellA,shellB);
    vec3 m=leafCurvature();vec2 gate=gateCurvature();
    float parent=max(positiveReach(f,rd,m.x),positiveReach(axA,rd,gate.x));
    parent=max(parent,positiveReach(angA,rd,gate.y));
    parent=max(parent,positiveReach(offset(shellA,-.095),rd,m.y));
    parent=max(parent,positiveReach(offset(-shellA,-.095),rd,m.y));
    float child=max(positiveReach(offset(f,.3),rd,m.x),positiveReach(axB,rd,gate.x));
    child=max(child,positiveReach(angB,rd,gate.y));
    child=max(child,positiveReach(offset(shellB,-.062),rd,m.z));
    child=max(child,positiveReach(offset(-shellB,-.062),rd,m.z));
    safeStep=min(min(parent,child),positiveReach(offset(f,10.),rd,m.x));
    return compose(f,a,b,layer);
   }

   vec3 spectrum(float x){return .5+.5*preciseCos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d,float roughness){
    // Small HDR reflection sources over a genuinely dark environment.
    // Distinct sharp glints and dim fill replace broad wax-like gradients.
    float power=mix(420.,120.,roughness);
    vec3 warm=normalize(vec3(-.7,.5,.4)),cool=normalize(vec3(.6,-.3,.7));
    vec3 rim=normalize(vec3(.1,.8,-.6));
    vec3 light=vec3(.0015,.002,.004);
    light+=vec3(8.,4.2,.8)*pow(max(0.,dot(d,warm)),power);
    light+=vec3(.7,4.8,9.)*pow(max(0.,dot(d,cool)),power*.7);
    light+=vec3(4.,.2,1.4)*pow(max(0.,dot(d,rim)),power*.5);
    light+=vec3(.07,.025,.008)*pow(max(0.,dot(d,warm)),3.);
    light+=vec3(.008,.035,.09)*pow(max(0.,dot(d,cool)),3.);
    return light;
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
     // This threshold selects a useful certificate; it never floors a step.
     CommonJets sharedJetsState=commonParts(p);
     float fastStep=cheapReach(p,rd,sharedJetsState);
     if(fastStep>.08){
      distanceAlong+=fastStep;havePrevious=false;
      if(distanceAlong>105.)break;
      continue;
     }
     float safeStep;sampleValue=traceSample(p,rd,sharedJetsState,safeStep);
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
     // Use ray-direction depth below, not normal-distance acceptance.
     float tolerance=min(.0015,max(.00015,distanceAlong*pixelScale*.08));
     // Require BOTH the existing residual and a ray-direction depth
     // estimate. Normal-distance alone can accept a near-tangent non-root.
     // This is still local sampled acceptance, not a tangency proof.
     if(abs(value)<.00015 && abs(value)/max(.00001,abs(dot(sampleValue.xyz,rd)))<tolerance){hit=true;break;}
     // Conservative first-entry CSG leaf reach; no forced minimum step.
     float stepSize=safeStep;
     previousAlong=distanceAlong;previousValue=value;havePrevious=true;
     distanceAlong+=stepSize;
     if(distanceAlong>105.)break;
    }
    vec3 color;
    if(hit){
     p=ro+rd*distanceAlong;
     vec3 normal=normalize(sheetSample(p).xyz);
     if(dot(normal,rd)>0.)normal=-normal;
     vec4 base,openingA,openingB;float layer;
     fieldParts(p,base,openingA,openingB);compose(base,openingA,openingB,layer);
     float facing=max(0.,dot(normal,-rd));
     float hue=.032*p.z+.14*length(p.xy-vec2(0.,1.7))+.24*openingB.w+time*.012;
     vec3 pigment=pow(spectrum(hue),vec3(1.8));
     // Metallic F0 retains saturated colour, with angle-dependent thin-film
     // tint. Layer selection follows actual intersections, never a hole mask.
     vec3 metal=mix(vec3(.55),pigment,.72);
     float fresnel=pow(1.-facing,5.);
     vec3 film=mix(metal,spectrum(hue+.22*(1.-facing)),.25);
     vec3 reflected=radiance(reflect(rd,normal),.10+.10*(1.-facing));
     float openness=1.;
     for(int j=0;j<3;j++){
      float reach=.08*pow(3.,float(j));
      vec4 nearby=sheetSample(p+normal*reach);
      float clearance=nearby.w/max(1.,length(nearby.xyz));
      openness-=.18*pow(.55,float(j))*clamp(1.-clearance/reach,0.,1.);
     }
     vec3 key=normalize(vec3(.6,.9,.7));
     float diffuse=max(0.,dot(normal,key));
     color=reflected*mix(film,vec3(1.),fresnel)*openness;
     color+=pigment*(.18+.28*diffuse*openness);
     // The outer backing is reached through real gaps in the petal volume, not a miss
     // painted black or evidence that numerical failure makes an opening.
     if(layer>1.5)color=color*.009+vec3(.0005,.0007,.001);
     float haze=1.-exp(-distanceAlong*.002);
     color=mix(color,vec3(.001,.0007,.002),haze);
     vec4 clip=viewProjection*vec4(p,1.);
     gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,.999999);
    }else{
     // A miss remains a numerical failure, not evidence of an aperture.
     color=vec3(.001,.0005,.003);
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
