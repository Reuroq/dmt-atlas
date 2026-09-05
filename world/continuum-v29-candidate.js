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

   // Jets carry analytic Cartesian gradients in xyz, scalar value in w.
   // No angular chart or radial colour fan at the cap's axis.
   vec4 jc(vec4 q){return vec4(-preciseSin(q.w)*q.xyz,preciseCos(q.w));}
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
   void fieldParts(vec3 p,out vec4 f,out vec4 holeA,out vec4 holeB){
    vec3 q=p-vec3(0.,1.7,0.);
    float angle=time*.065,c=preciseCos(angle),s=preciseSin(angle);
    vec4 x=vec4(c,-s,0.,c*q.x-s*q.y),y=vec4(s,c,0.,s*q.x+c*q.y);
    vec4 z=vec4(0.,0.,1.,q.z);
    float cap=min(q.z+27.5,0.),rho=length(vec3(q.xy,.45*cap));
    vec4 radial=vec4(vec3(q.xy,.2025*cap)/max(rho,.00001),rho-7.);
    // Each finer rosette is phase-modulated by its parent, and displaces
    // actual geometry. This is not pigment/noise counted as hierarchy.
    vec4 r0=jm(rose(x,y,.62),jc(offset(.24*z,-time*.30)));
    vec4 r1=jm(rose(x,y,1.65),jc(offset(.58*z+1.2*r0,-time*.36)));
    vec4 r2=jm(rose(x,y,4.4),jc(offset(1.1*z+1.1*r1,-time*.41)));
    vec4 w1=filtered(r1,4.,p),w2=filtered(r2,11.,p);
    f=radial-.86*jc(offset(.68*z+1.1*r0,-time*.48))-.55*r0-.32*w1-.14*w2;
    if(high>.5){
     vec4 r3=jm(rose(x,y,11.7),jc(offset(2.3*z+.9*r2,-time*.47)));
     f-=.06*filtered(r3,27.,p);
    }
    // Positive hole fields remove material, exposing another membrane
    // 2.6 units farther out and a real dark backing 6 units farther out.
    holeA=offset(w1,-.05);
    holeB=offset(w2+.35*r0,-.14);
   }
   vec4 membrane(vec4 f,float centre,float thickness,vec4 hole){
    vec4 a=offset(f,-centre);
    vec4 shell=vec4(sign(a.w)*a.xyz,abs(a.w)-thickness);
    return shell.w>hole.w?shell:hole;
   }
   vec4 compose(vec4 f,vec4 a,vec4 b,out float layer){
    vec4 first=membrane(f,0.,.14,a),second=membrane(f,2.6,.18,b);
    vec4 backing=offset(-f,6.);
    vec4 result=first;layer=0.;
    if(second.w<result.w){result=second;layer=1.;}
    if(backing.w<result.w){result=backing;layer=2.;}
    return result;
   }
   vec4 sheetSample(vec3 p){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);return compose(f,a,b,layer);
   }
   float envelope(vec3 p){
    float rho=length(vec3(p.xy-vec2(0.,1.7),.45*min(p.z+27.5,0.)));
    // Displacement <=1.93, inner half-thickness .14: rho>=4.93.
    // Clearance holds before the cap, beyond the physical exit at -22.
    return max(0.,4.925-rho);
   }
   float raySlope(vec3 p,vec3 rd){return 12.+12.*pixelScale;}
   float positiveReach(vec4 leaf,vec3 rd){
    if(leaf.w<=0.)return 0.;
    // New v29 leaf bound; NEVER apply a smooth Hessian bound to CSG max/min.
    // For shells this is valid until |f-centre| reaches thickness, before
    // the abs cusp. See centre-v29-bounds.md for CSG first-entry reasoning.
    float curvature=100.+160.*pixelScale+400.*pixelScale*pixelScale;
    float slope=abs(dot(leaf.xyz,rd)),remaining=.95*leaf.w;
    return min(.4,2.*remaining/(slope+sqrt(slope*slope+2.*curvature*remaining)));
   }
   float membraneReach(vec4 f,float centre,float thickness,vec4 hole,vec3 rd){
    vec4 a=offset(f,-centre);
    vec4 shell=vec4(sign(a.w)*a.xyz,abs(a.w)-thickness);
    // Both constraints must be nonpositive to enter this intersection.
    return max(positiveReach(shell,rd),positiveReach(hole,rd));
   }
   vec4 traceSample(vec3 p,vec3 rd,out float safeStep){
    vec4 f,a,b;float layer;fieldParts(p,f,a,b);
    safeStep=min(membraneReach(f,0.,.14,a,rd),membraneReach(f,2.6,.18,b,rd));
    // To enter a union, any component can be the first encountered.
    safeStep=min(safeStep,positiveReach(offset(-f,6.),rd));
    return compose(f,a,b,layer);
   }
   vec3 spectrum(float x){return .5+.5*preciseCos(TAU*(x+vec3(0.,.333,.667)));}
   vec3 radiance(vec3 d,float roughness){
    // Small HDR reflection sources over a genuinely dark environment.
    // Distinct sharp glints and dim fill replace broad wax-like gradients.
    float power=mix(180.,35.,roughness);
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
     float safeStep;sampleValue=traceSample(p,rd,safeStep);
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
     float hue=.10*p.z+.16*preciseCos(.42*p.x)*preciseCos(.42*(p.y-1.7))+time*.018;
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
     color+=pigment*(.026+.11*diffuse*openness);
     // The third surface is a recessed, low-radiance backing, not a miss
     // painted black or evidence that numerical failure makes an opening.
     if(layer>1.5)color=color*.045+vec3(.0005,.0007,.001);
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
