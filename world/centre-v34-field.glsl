   // v34: clipped curled laminae with volumetrically attached child folds.
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
    axA=offset(-sharedJetsState.cosLocal,-.62);axB=offset(axA,.20);
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
    angB=offset(angA,.28);
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
   // @V34_BOUND_FUNCTIONS@
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
    fieldPartsReachShared(p,sharedJetsState,f,a,b,axA,axB,angA,angB,shellA,shellB);
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

