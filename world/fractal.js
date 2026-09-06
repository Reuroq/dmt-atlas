/* Procedural geometry, not witness imagery. Evidence is attached by the journey builder. */
(() => {
'use strict';
const T=THREE, TAU=Math.PI*2;
const palettes=[['#040921','#00eabf','#ffc24b'],['#240009','#ff174b','#ffd13b'],['#020f21','#08f5db','#b5ff57'],['#100027','#952bff','#ffb62d'],['#19051d','#ff297d','#ffe3a1']];
const vertex=`
varying vec2 vUv; varying vec3 vP,vN,vView; uniform float time,strength,relief;
void main(){
 vUv=uv;vP=position;vN=normal;
 float wave=sin(position.x*1.3+time*.31+sin(position.z*.7-time*.19));
 wave+=.5*sin(position.y*2.1-time*.28+cos(position.x*1.8));
 vec3 p=position+normal*wave*relief*strength;
 vec4 transformed=vec4(p,1.);
 #ifdef USE_INSTANCING
 transformed=instanceMatrix*transformed;
 #endif
 vec4 mv=modelViewMatrix*transformed;vView=mv.xyz;
 gl_Position=projectionMatrix*mv;
}`;
const fragment=`
precision highp float;
varying vec2 vUv;varying vec3 vP,vN,vView;
uniform float time,scale,strength,detail,alpha,radiance;uniform vec3 a,b,c;
mat2 rotate(float t){return mat2(cos(t),-sin(t),sin(t),cos(t));}
float line(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d)*.9,.001),abs(d));}
void main(){
 vec3 n=abs(normalize(vN));
 vec2 p=n.z>max(n.x,n.y)?vP.xy:(n.y>n.x?vP.xz:vP.zy);
 // Local position preserves the scale of ornament on wide and tall surfaces.
 p*=.22*sqrt(scale);float t=time*.19*strength;
 vec2 domain=p;
 p+=.18*strength*sin(p.yx*1.7+vec2(t,-t*.83));
 p+=.07*strength*sin(p.yx*3.7+sin(p*2.)+t*.7);
 vec2 q=p;float height=0.,vein=0.,inlay=0.,jewel=0.,weight=1.;
 for(int i=0;i<6;i++){
  if(float(i)>=detail)break;
  // Nested radial/diamond folds with coherent large cuts and finer engraved cuts.
  vec2 cell=fract(q+.5)-.5;
  float r=length(cell),ang=atan(cell.y,cell.x);
  float petal=r-(.29+.065*cos(ang*8.+t*.43+float(i)));
  float web=abs(cell.x)+abs(cell.y)-.46;
  float engraving=min(abs(petal),abs(web)*.7);
  float lod=1.-smoothstep(.12,.6,length(fwidth(q)));
  height+=weight*lod*(exp(-engraving*23.)*.52+exp(-r*r*38.)*.8);
  vein+=weight*lod*(line(petal,.011)+line(web,.008)*.5);
  inlay+=weight*lod*(line(petal+.065,.01)+exp(-r*r*55.)*.55);
  jewel+=weight*lod*exp(-r*r*110.);
  q=rotate(.7854+t*.015)*q*3.05+vec2(.21,-.08);
  weight*=.46;
 }
 // Small circuit-like incisions sit inside the folds, not on a flat checkerboard.
 vec2 glyph=abs(fract(q*1.7)-.5);
 float circuit=line(min(abs(glyph.x-.18),max(abs(glyph.y-.25),glyph.x-.27)),.017);
 float facet=pow(.5+.5*cos(height*9.+domain.x*.4-t),3.);
 float iridescence=.5+.5*sin(height*5.+length(domain)*.6-t*.5);
 vec3 enamel=mix(b,c,smoothstep(.62,.83,iridescence));
 vec3 col=a*.4+enamel*(.012+height*.045+facet*.04);
 col+=c*min(vein,1.6)*1.05+b*inlay*1.1;
 col+=mix(c,vec3(.01,1.,.8),smoothstep(.35,.65,iridescence))*jewel*.85;
 col+=enamel*circuit*.018;
 // Screen-space relief lighting puts a bright cut and a dark edge on every fold.
 vec2 slope=vec2(dFdx(height),dFdy(height))/max(length(vec2(dFdx(vView.x),dFdy(vView.y))),.015);
 float light=dot(normalize(vec3(-slope*.75,1.)),normalize(vec3(-.7,.9,1.3)));
 col*=.65+max(light,0.)*.55;
 col+=vec3(1.,.85,.59)*pow(max(light,0.),22.)*min(vein,.8)*.35;
 col=mix(a+col*.22,col,strength);
 gl_FragColor=vec4(col*radiance,alpha);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
}`;
function surface(palette,scale,strength,materials){
 const colors=palettes[palette%palettes.length];
 const m=new T.ShaderMaterial({side:T.DoubleSide,extensions:{derivatives:true},uniforms:{
  time:{value:0},scale:{value:scale},strength:{value:strength},detail:{value:quality==='high'?6:4},
  relief:{value:.075},alpha:{value:1},radiance:{value:.7},a:{value:new T.Color(colors[0])},b:{value:new T.Color(colors[1])},c:{value:new T.Color(colors[2])}
 },vertexShader:vertex,fragmentShader:fragment});
 materials.push(m);return m;
}
// Return: the same continuous surface relaxes from flowing relief into a sunlit room.
function returnField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{derivatives:true},uniforms:{time:{value:0},detail:{value:quality==='high'?6:4}},
  vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
  fragmentShader:`
   precision highp float;
   uniform float time,detail;varying vec3 fieldWorld;
   float loosen(vec3 p){
    // Islands of depth peel back into the same room, rather than ending at a portal.
    float wave=sin(p.z*.34+p.y*.72+time*.23)+.4*sin(p.x*.65-p.z*.17-time*.19);
    float islands=smoothstep(-.6,.65,wave);
    float floorCalm=mix(.16,1.,smoothstep(.2,2.5,p.y));
    float windowCalm=smoothstep(1.4,3.8,length((p.yz-vec2(3.65,-3.))*vec2(1.,.65)));
    return smoothstep(-24.,2.,p.z)*mix(.07,1.,islands)*floorCalm*mix(1.,windowCalm,smoothstep(2.,4.5,p.x));
   }
   float relief(vec3 p){
    vec3 q=p*.92;
    q+=.52*sin(q.zxy*.63+vec3(time*.34,-time*.27,time*.21));
    float h=0.,w=.48;
    for(int j=0;j<4;j++){
     float fold=dot(sin(q),cos(q.yzx));
     h+=w*exp(-abs(fold)*3.8);
     q=q.zxy*2.7+.32*sin(q.yzx)+vec3(1.2,2.3,.7);w*=.37;
    }
    return h;
   }
   float box(vec3 p,vec3 b,float r){vec3 q=abs(p)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
   vec2 field(vec3 p){
    float f=loosen(p);
    vec3 q=p;
    q.x+=f*.35*sin(p.z*.39-time*.37);
    q.y+=f*.15*sin(p.x*.8+p.z*.48-time*.42);
    // Rounded wall/floor junctions and changing relief share one implicit boundary.
    float shell=-box(q-vec3(0.,3.3,-8.),vec3(4.6,2.75,22.),.65);
    shell-=f*relief(q)*1.25;
    // Quiet upholstered bench at the far end grounds the returning room.
    float seat=box(p-vec3(-3.7,.52,-5.5),vec3(.66,.29,1.55),.16);
    seat=min(seat,box(p-vec3(-4.2,1.02,-5.5),vec3(.17,.64,1.55),.16));
    seat=min(seat,box(p-vec3(-3.7,.83,-7.),vec3(.66,.29,.14),.16));
    seat=min(seat,box(p-vec3(-3.7,.83,-4.),vec3(.66,.29,.14),.16));
    return seat<shell?vec2(seat,1.):vec2(shell,0.);
   }
   vec3 normalAt(vec3 p,float e){vec2 k=vec2(e,0.);return normalize(vec3(field(p+k.xyy).x-field(p-k.xyy).x,field(p+k.yxy).x-field(p-k.yxy).x,field(p+k.yyx).x-field(p-k.yyx).x));}
   void main(){
    vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);float travel=0.;vec2 d=vec2(0.);bool hit=false;
    for(int i=0;i<150;i++){
     d=field(ro+rd*travel);
     if(d.x<.002+travel*.00013){hit=true;break;}
     travel+=max(d.x*.48,.003);if(travel>65.||float(i)>mix(105.,148.,step(5.,detail)))break;
    }
    vec3 col=vec3(.055,.065,.08);
    if(hit){
     vec3 p=ro+rd*travel,n=normalAt(p,.009),v=-rd;
     float f=loosen(p),h=relief(p),floorMask=1.-smoothstep(.15,.6,p.y);
     vec3 lightPos=vec3(5.,4.5,-3.),l=normalize(lightPos-p);
     float diffuse=.22+.7*max(dot(n,l),0.)+.24*max(dot(n,normalize(vec3(-2.,4.,9.)-p)),0.);
     float ao=clamp(field(p+n*.36).x/.36,.2,1.);
     vec3 plain=mix(vec3(.56,.47,.35),vec3(.28,.17,.09),floorMask);
     float boards=pow(.5+.5*cos(p.x*7.),32.);plain*=1.-floorMask*.14*boards;
     vec3 film=.5+.5*cos(vec3(.1,2.2,4.3)+h*11.+p.z*.16-time*.29+dot(n,v)*3.);
     vec3 jewel=mix(vec3(.015,.10,.11),vec3(.43,.12,.07),.5+.5*sin(p.z*.28+p.y*.65+time*.22));
     jewel+=film*pow(clamp(h*1.7,0.,1.),3.)*.55;
     vec3 base=mix(plain,jewel,f);
     if(d.y>.5){
      float seam=exp(-pow(sin((p.z+5.5)*2.05)*35.,2.));
      base=vec3(.12,.21,.19)*(1.-seam*.15);
     }
     col=base*diffuse*ao;
     float spec=pow(max(dot(n,normalize(l+v)),0.),mix(12.,58.,f));
     col+=mix(vec3(.2),film,f)*spec*(.14+f*.55);
     col+=film*pow(1.-max(dot(n,v),0.),3.)*f*.22;
     // Smooth inner colour lives in the carved folds; no contour-line overlay.
     col+=film*pow(.5+.5*sin(h*28.+p.y*.7-time*.23),4.)*f*.10;
     // A window belongs to the distant wall, not an opaque portal in the passage.
     vec2 w=abs(p.xy-vec2(1.4,3.65));
     float window=(1.-smoothstep(1.3,1.34,w.x))*(1.-smoothstep(1.6,1.64,w.y))*step(p.z,-30.45);
     float mullion=smoothstep(.035,.065,abs(p.x-1.4))*smoothstep(.035,.065,abs(p.y-3.65));
     col=mix(col,mix(vec3(.25,.21,.16),vec3(1.1,.92,.65)+vec3(.18,.26,.3)*(p.y-2.)*.15,mullion),window);
     vec2 side=abs(p.zy-vec2(-3.,3.65));
     float sideWindow=(1.-smoothstep(2.1,2.15,side.x))*(1.-smoothstep(1.45,1.5,side.y))*smoothstep(5.1,5.2,p.x);
     float frame=smoothstep(.045,.085,side.x)*smoothstep(.035,.075,side.y);
     vec3 daylight=mix(vec3(.65,.75,.59),vec3(.76,.94,1.1),smoothstep(2.5,4.6,p.y));
     col=mix(col,mix(vec3(.31,.25,.17),daylight,frame),sideWindow);
     col=mix(col,vec3(.14,.16,.16),1.-exp(-travel*.007));
    }
    gl_FragColor=vec4(col,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`});
 const field=new T.Mesh(new T.BoxGeometry(150,150,150),m);field.position.set(0,3,-10);field.frustumCulled=false;
 root.add(field);materials.push(m);return field;
}
// One continuous enclosure for the room-falling-away stage: relief is spatial, not wallpaper.
function geometryField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,uniforms:{time:{value:0},detail:{value:quality==='high'?6:4}},
  vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
  fragmentShader:`
   precision highp float;
   uniform float time,detail;varying vec3 fieldWorld;
   const float PI=3.14159265359;
   vec3 coordinates(vec3 p){
    p.y-=3.;
    float a=atan(p.y,p.x)+.11*sin(p.z*.24-time*.23);
    return vec3(a,length(p.xy),p.z);
   }
   float weave(vec3 q){
    return dot(sin(q),cos(q.zxy));
   }
   float porousShell(vec3 c,float radius,float throat){
    // Intersecting folded channels form rounded branches instead of broad sheets.
    float radial=c.y/throat-radius;
    vec3 q=vec3(c.x*16.,c.z*1.65+time*.32,radial*1.65);
    q.y+=.7*sin(c.x*4.-time*.2);
    q.z+=.4*sin(c.x*8.+c.z*.3-time*.33);
    vec2 network=vec2(weave(q),weave(q+vec3(1.4,2.1,.7)));
    q=q.yzx*2.+vec3(.8,1.3,.4);
    network+=.3*vec2(weave(q),weave(q+vec3(.7,1.8,2.4)));
    q=q.zxy*2.+vec3(1.6,.3,.9);
    network+=.12*vec2(weave(q),weave(q+vec3(2.2,.9,1.5)));
    // Fade branch thickness toward the clear core; no planar cylinder cut faces.
    float inner=2.8*(1.-smoothstep(-2.3,-.1,radial));
    float lace=(length(network)-.68+inner)*.42*throat;
    float backing=(1.6-radial+.16*weave(q*.25))*throat;
    float blend=.32*throat,h=clamp(.5+.5*(backing-lace)/blend,0.,1.);
    return mix(backing,lace,h)-blend*h*(1.-h);
   }
   float enclosure(vec3 p){
    vec3 c=coordinates(p);
    float breath=sin(c.x*8.+c.z*.23-time*.48);
    float radius=6.65+.7*breath+.44*sin(c.z*.73+sin(c.x*4.)-time*.3);
    // The enclosure narrows in depth instead of terminating on a radial end panel.
    float throat=1.-.965*smoothstep(9.,77.,-p.z);
    float side=porousShell(c,radius,throat);
    return side*.32;
   }
   vec3 normalAt(vec3 p,float e){
    vec2 k=vec2(e,0.);
    return normalize(vec3(enclosure(p+k.xyy)-enclosure(p-k.xyy),
     enclosure(p+k.yxy)-enclosure(p-k.yxy),enclosure(p+k.yyx)-enclosure(p-k.yyx)));
   }
   void main(){
    vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);
    float travel=0.,d=0.;bool hit=false;
    for(int i=0;i<160;i++){
     d=enclosure(ro+rd*travel);
     if(d<.0015+travel*.00016){hit=true;break;}
     travel+=max(d,.003);
     if(travel>85.||float(i)>mix(105.,158.,step(5.,detail)))break;
    }
    vec3 col=vec3(.008,.012,.035);
    if(hit){
     vec3 p=ro+rd*travel,c=coordinates(p),n=normalAt(p,.007+travel*.0002),v=-rd;
     float hue=.5+.5*sin(c.x*4.+c.z*.21+time*.17);
     vec3 jewel=mix(vec3(.065,.012,.24),vec3(.012,.34,.29),hue);
     jewel=mix(jewel,vec3(.38,.055,.16),pow(.5+.5*cos(c.z*.42-c.x*8.-time*.24),5.)*.65);
     vec3 l1=normalize(vec3(2.5,5.,ro.z-2.)-p),l2=normalize(vec3(-3.,3.,-19.)-p);
     float diffuse=.32+.62*max(dot(n,l1),0.)+.48*max(dot(n,l2),0.);
     float occ=clamp(enclosure(p+n*.55)/(.55*.32),.12,1.);
     float gloss=pow(max(dot(n,normalize(l1+v)),0.),48.)
      +.65*pow(max(dot(n,normalize(l2+v)),0.),72.);
     float rim=pow(1.-max(dot(n,v),0.),3.);
     vec3 film=.5+.5*cos(vec3(.2,2.3,4.4)+dot(n,v)*7.+c.z*.12+time*.16);
     col=jewel*diffuse*occ+mix(vec3(.7,.95,1.),film,.4)*gloss*1.2;
     col+=film*rim*.17;
     col+=jewel*.18;
     float haze=1.-exp(-travel*.017);
     col=mix(col,vec3(.025,.055,.09),haze);
    }
    gl_FragColor=vec4(col,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`});
 const field=new T.Mesh(new T.BoxGeometry(180,180,180),m);field.position.set(0,3,-20);field.frustumCulled=false;
 root.add(field);materials.push(m);return field;
}
// Rush-only continuous folded channel; travelling relief replaces floor, vault and wires.
function rushField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{derivatives:true},uniforms:{time:{value:0},detail:{value:quality==='high'?6:4}},
  vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
  fragmentShader:`
   precision highp float;
   uniform float time,detail;varying vec3 fieldWorld;
   vec3 channel(vec3 p){
    p.y-=2.5;
    float z=p.z-time*8.;
    float a=atan(p.y,p.x)+.22*sin(z*.12)+.09*sin(z*.31-time*.4);
    return vec3(a,length(p.xy),z);
   }
   float rushRelief(vec3 c){
    // Seamless cylindrical domain: branching ridges carry smaller branching ridges.
    vec3 q=vec3(cos(c.x)*7.,sin(c.x)*7.,c.z*1.1);
    q+=.4*sin(q.zxy*.7);
    float height=0.,weight=1.15;
    for(int j=0;j<4;j++){
     float network=dot(sin(q),cos(q.yzx));
     height+=weight*exp(-network*network*3.2);
     q=q.yzx*2.65+.32*sin(q.zxy)+vec3(1.4,2.1,.5);
     weight*=.38;
    }
    return height;
   }
   float wall(vec3 p){
    vec3 c=channel(p);
    float throat=1.-.96*smoothstep(65.,112.,-p.z);
    float r=c.y/throat;
    // Volumetric branching struts leave real apertures in front of a deeper wall.
    vec3 q=vec3(cos(c.x)*r,sin(c.x)*r,c.z*.72)*1.3;
    q+=.45*sin(q.zxy*.6);
    float g1=dot(sin(q),cos(q.yzx));
    float g2=dot(sin(q+vec3(1.8,.7,2.3)),cos(q.yzx+vec3(.4,2.1,1.2)));
    vec3 fine=q.yzx*2.6+vec3(1.4,2.1,.5);
    g1+=.18*dot(sin(fine),cos(fine.yzx));
    g2+=.13*dot(sin(fine+1.2),cos(fine.zxy));
    float core=3.*(1.-smoothstep(4.9,6.5,r));
    float branches=(length(vec2(g1,g2*.8))-.62+core)*.48;
    float backing=9.6+.45*sin(c.x*6.+c.z*.21)-r-.25*rushRelief(c);
    float blend=.35,h=clamp(.5+.5*(backing-branches)/blend,0.,1.);
    return (mix(backing,branches,h)-blend*h*(1.-h))*throat*.25;
   }
   vec3 normalAt(vec3 p,float e){
    vec2 k=vec2(e,0.);
    return normalize(vec3(wall(p+k.xyy)-wall(p-k.xyy),wall(p+k.yxy)-wall(p-k.yxy),wall(p+k.yyx)-wall(p-k.yyx)));
   }
   void main(){
    vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);
    float travel=0.;bool hit=false;
    for(int i=0;i<180;i++){
     float d=wall(ro+rd*travel);
     if(d<.002+travel*.00025){hit=true;break;}
     travel+=max(d,.003);
     if(travel>125.||float(i)>mix(119.,178.,step(5.,detail)))break;
    }
    vec3 col=vec3(.025,.12,.16);
    if(hit){
     vec3 p=ro+rd*travel,c=channel(p),n=normalAt(p,.008+travel*.00015),v=-rd;
     float fold=c.x*8.+c.z*.38+.7*sin(c.z*.17);
     float flowing=.5+.5*sin(c.x*3.+.35*sin(c.z*.21)+c.y*.6);
     vec3 jewel=mix(vec3(.012,.28,.32),vec3(.4,.018,.12),smoothstep(.2,.85,flowing));
     float relief=rushRelief(c);
     float crest=smoothstep(.85,1.6,relief);
     jewel=mix(jewel,vec3(.85,.34,.025),crest*.4);
     vec3 l=normalize(vec3(1.,4.,ro.z+3.)-p);
     float diffuse=.3+.7*max(dot(n,l),0.);
     float occ=clamp(wall(p+n*.6)/(.6*.25),.08,1.);
     float gloss=pow(max(dot(n,normalize(l+v)),0.),38.);
     float rim=pow(1.-max(dot(n,v),0.),3.);
     vec3 film=.5+.5*cos(vec3(.1,2.2,4.3)+dot(n,v)*8.+c.z*.08);
     float engraving=relief*65.+sin(c.z*8.+sin(c.x*32.));
     float fine=pow(.5+.5*cos(engraving),18.)*(1.-smoothstep(.5,2.,fwidth(engraving)));
     col=jewel*(diffuse*occ+.08)+film*(gloss*.85+rim*.16)*occ;
     col+=mix(vec3(.05,.8,.9),vec3(1.,.55,.08),crest)*fine*.28;
     col+=vec3(.04,.5,.52)*crest*.08;
     col=mix(col,vec3(.012,.065,.095),1.-exp(-travel*.007));
    }
    gl_FragColor=vec4(col,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`});
 const field=new T.Mesh(new T.BoxGeometry(240,240,240),m);field.position.set(0,2.5,-25);field.frustumCulled=false;
 root.add(field);materials.push(m);return field;
}
// Yielding iris sheets: the aperture reveals other folded surfaces, not an end panel.
function membraneField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`
 precision highp float;
 uniform float time;varying vec3 fieldWorld;
 vec2 sheet(vec3 p,float k){
  vec2 q=p.xy-vec2(.3*sin(k*1.7+time*.23),1.7+.25*cos(k*2.+time*.3));
  float r=length(q),a=atan(q.y,q.x),t=time*.65;
  float aperture=3.7+k*.45+.75*sin(t-k*.47);
  aperture+=.15*sin(a*3.+t+k)+.08*sin(a*5.-t);
  float lip=exp(-pow((r-aperture)*.9,2.));
  float folds=sin(a*9.+r*.7-t+k)+.38*sin(a*19.-r*1.8+t);
  float nested=sin(r*5.+sin(a*9.-t)*1.7)*sin(a*27.+r*2.+t);
  float z=-1.-k*6.+.24*r+(.6+.48*lip)*folds+lip*.8;
  z+=.2*nested+.065*sin(r*17.+sin(a*27.+t)*2.);
  // A circular lip cross-section turns back into the surface without extruded sidewalls.
  float edge=max(aperture+.55-r,0.);
  float thickness=.5+.23*lip+.1*lip*sin(a*17.+r*3.-t);
  float d=length(vec2(edge,p.z-z))-thickness;
  return vec2(d*.26,k);
 }
 vec2 field(vec3 p){
  vec2 d=sheet(p,0.);
  for(int i=1;i<5;i++){vec2 s=sheet(p,float(i));if(s.x<d.x)d=s;}
  // The nested openings lead into a concave chamber, not a central solid rosette.
  vec3 q=p-vec3(0.,1.7,-37.);
  float a=atan(q.y,q.x),r=length(q.xy),t=time*.45;
  float relief=.7*sin(a*9.+r*.8-t)*sin(r*1.3+t);
  relief+=.2*sin(r*6.+sin(a*19.+t)*2.);
  vec2 chamber=vec2(max(16.-length(q)-relief,p.z+28.)*.3,5.);
  if(chamber.x<d.x)d=chamber;
  return d;
 }
 vec3 normalAt(vec3 p){
  vec2 e=vec2(.012,0.);
  return normalize(vec3(field(p+e.xyy).x-field(p-e.xyy).x,field(p+e.yxy).x-field(p-e.yxy).x,field(p+e.yyx).x-field(p-e.yyx).x));
 }
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);float travel=0.;vec2 hit;
  for(int i=0;i<240;i++){
   hit=field(ro+rd*travel);
   if(hit.x<.008||travel>85.)break;
   travel+=max(.008,hit.x);
  }
  vec3 col;
  if(travel<85.&&hit.x<.018){
   vec3 p=ro+rd*travel,n=normalAt(p);if(dot(n,rd)>0.)n=-n;
   vec2 q=p.xy-vec2(.3*sin(hit.y*1.7+time*.23),1.7+.25*cos(hit.y*2.+time*.3));
   float r=length(q),a=atan(q.y,q.x),t=time*.65;
   vec2 uv=vec2(a*5.5+r*.24-t*.09,r*1.8+.5*sin(a*7.+t));
   float tracery=0.,weight=.5;
   for(int j=0;j<4;j++){
    uv=mat2(.8,-.6,.6,.8)*uv*2.13+sin(uv.yx*1.3+t*.15)*.43;
    float lace=abs(sin(uv.x+sin(uv.y))*sin(uv.y+sin(uv.x)));
    tracery+=weight*exp(-lace*18.);weight*=.52;
   }
   float facing=max(0.,dot(n,-rd)),rim=pow(1.-facing,2.);
   vec3 jewel=.45+.4*cos(vec3(.2,2.3,4.2)+r*.31+sin(a*5.+r*.4)*.8+hit.y*.7+t*.18);
   float light=.28+.72*max(0.,dot(n,normalize(vec3(-.4,.6,1.))));
   col=jewel*(light*.7+tracery*.65);
   col+=vec3(.24,.8,.72)*rim*.65+vec3(1.,.65,.27)*pow(tracery,2.)*.6;
   vec3 h=normalize(normalize(vec3(-.4,.6,1.))-rd);
   col+=vec3(.9,.85,1.)*pow(max(0.,dot(n,h)),38.)*.7;
   col=mix(col,vec3(.09,.17,.22),1.-exp(-travel*.009));
  }else{
   col=vec3(.09,.17,.22);
  }
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const fieldMesh=new T.Mesh(new T.BoxGeometry(240,240,240),m);fieldMesh.position.set(0,1.7,-20);fieldMesh.frustumCulled=false;
 root.add(fieldMesh);materials.push(m);return fieldMesh;
}
// Waiting-room architecture is one carved, breathing volume, not a stack of ribs.
function waitingField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`
 precision highp float;
 uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float roundedBox(vec3 p,vec3 b,float r){vec3 q=abs(p)-b+r;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
 float blend(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float weave(vec3 p){return dot(sin(p),cos(p.yzx));}
 vec3 carving(vec3 p){
  vec3 q=p*.62;
  q+=.48*sin(q.yzx*.61+vec3(time*.21,-time*.17,time*.13));
  float g=weave(q);
  float primary=exp(-g*g*3.2);
  q=q.zxy*2.31+.42*sin(q.yzx)+vec3(.7,1.3,2.1);
  g=weave(q);
  float secondary=exp(-g*g*4.5);
  q=q.yzx*2.73+.28*sin(q.zxy);
  g=weave(q);
  return vec3(primary,secondary,exp(-g*g*5.));
 }
 float chamber(vec3 p){
  float t=time*.48;
  vec3 q=p;
  float high=smoothstep(.3,3.,p.y);
  q.x+=high*(.3*sin(p.z*.38+t)+.13*sin(p.y*.8-p.z*.22-t));
  q.y+=high*.25*sin(p.x*.48+p.z*.3-t);
  float inside=-roundedBox(q-vec3(0.,5.,0.),vec3(9.,5.2,14.),1.4);
  float hall=-roundedBox(p-vec3(0.,2.8,-22.),vec3(2.25,3.,10.),.9);
  inside=-blend(-inside,-hall,1.1);
  // Upholstered ledges grow out of both walls; the centre remains walkable.
  float ledge=roundedBox(vec3(abs(q.x)-7.7,q.y-.35,q.z+1.),vec3(1.25,.85,7.6),.7);
  inside=blend(inside,ledge,.7);
  vec3 cut=carving(q);
  // Deep interlocking mouldings carry finer carvings on their shoulders.
  float relief=.78*cut.x+.19*cut.y*(.35+.65*cut.x)+.045*cut.z;
  return inside-relief*mix(.1,1.,smoothstep(.25,1.6,p.y));
 }
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);float travel=.06;bool hit=false;
  for(int i=0;i<320;i++){
   float d=chamber(ro+rd*travel);
   if(d<.004+travel*.00018){hit=true;break;}
   travel+=max(.002,d*.34);if(travel>75.)break;
  }
  vec3 p=ro+rd*travel,col=vec3(.035,.025,.09);
  if(hit){
   float e=.012;
   vec3 n=normalize(vec3(chamber(p+vec3(e,0,0))-chamber(p-vec3(e,0,0)),chamber(p+vec3(0,e,0))-chamber(p-vec3(0,e,0)),chamber(p+vec3(0,0,e))-chamber(p-vec3(0,0,e))));
   vec3 cut=carving(p);
   float filigree=cut.z*cut.y;
   float hue=.5+.5*sin(p.y*.31+p.z*.13+weave(p*.19)+time*.2);
   vec3 enamel=mix(vec3(.055,.009,.2),vec3(.009,.24,.19),smoothstep(.15,.85,hue));
   float gild=smoothstep(.55,.95,cut.x)*(.35+.65*cut.y);
   enamel=mix(enamel,vec3(.65,.24,.035),gild*.85);
   float ao=clamp(chamber(p+n*.35)/.35,.12,1.);
   ao*=clamp(chamber(p+n*.8)/.8,.35,1.);
   vec3 l=normalize(vec3(-3.,7.,4.)-p),h=normalize(l-rd);
   float diffuse=max(0.,dot(n,l)),fres=pow(1.-max(0.,dot(n,-rd)),3.);
   col=enamel*(.3+diffuse*.95)*ao;
   col+=mix(vec3(.08,.5,.39),vec3(.7,.32,.06),hue)*filigree*(.06+.22*fres)*ao;
   col+=vec3(1.,.82,.58)*pow(max(0.,dot(n,h)),76.)*.48*ao;
   col+=vec3(.15,.12,.4)*fres*.2;
   float doorway=exp(-length((p-vec3(0.,3.,-19.))*vec3(.32,.28,.13)));
   col+=vec3(.19,.42,.72)*doorway*.28;
   col=mix(col,vec3(.055,.04,.14),1.-exp(-travel*.012));
  }
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);
  gl_FragDepthEXT=hit?clamp(clip.z/clip.w*.5+.5,0.,1.):1.;
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const field=new T.Mesh(new T.BoxGeometry(160,160,160),m);field.frustumCulled=false;field.renderOrder=-1;
 root.add(field);materials.push(m);return field;
}
// Cathedral-only solid architecture: the piers, vault, floor and recesses share one field.
function cathedralField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`
 precision highp float;uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float join(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float box(vec3 p,vec3 b,float r){vec3 q=abs(p)-b+r;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
 vec3 coffer(vec2 uv){
  uv*=.24;
  uv+=.11*sin(uv.yx*1.3+time*.36)+.035*sin(uv.yx*2.7-time*.23);
  float depth=0.,lip=0.,inlay=0.,weight=1.;
  for(int i=0;i<3;i++){
   vec2 cell=abs(fract(uv)-.5);
   float r=length(max(cell-vec2(.19),0.))+min(max(cell.x,cell.y),.19);
   float outer=1.-smoothstep(.24,.47,r);
   float inner=1.-smoothstep(.045,.25,r);
   depth+=weight*(.42*outer+.19*inner);
   lip+=weight*exp(-pow((r-.405)*36.,2.));
   inlay+=weight*exp(-pow((r-.24)*48.,2.));
   uv=mat2(.96,-.28,.28,.96)*uv*3.07+.055*sin(uv.yx*2.+time*.3);
   weight*=.17;
  }
  return vec3(depth,clamp(lip,0.,1.),clamp(inlay,0.,1.));
 }
 vec3 cathedralWarp(vec3 p){
  vec3 q=p;float lift=smoothstep(.4,5.,p.y);
  q.x+=lift*.23*sin(p.z*.23+time*.45);
  q.y+=lift*.28*sin(p.z*.31-time*.38)*cos(p.x*.17);
  return q;
 }
 vec3 ornament(vec3 p){
  // Blend relief from separate surface-facing projections, never blended UVs.
  vec2 radial=vec2(p.x,max(p.y-13.,0.));float radius=max(length(radial),.001);
  float arc=radius-13.,z=mod(p.z+5.,10.)-5.;
  float rib=max(length(vec2(arc,z))-.95,abs(p.z)-23.);
  float shell=(1.-length(vec3(p.x/24.,max(p.y-9.,0.)/20.,(p.z+3.)/33.)))*18.;
  vec3 wallN=normalize(vec3(p.x/576.,max(p.y-9.,.01)/400.,(p.z+3.)/1089.));
  vec3 ribN=normalize(vec3(arc*radial/radius,z)+vec3(.0001));
  vec3 wallW=pow(abs(wallN),vec3(4.)),ribW=pow(abs(ribN),vec3(4.));
  wallW/=dot(wallW,vec3(1.));ribW/=dot(ribW,vec3(1.));
  vec3 w=mix(wallW,ribW,smoothstep(-1.,1.,shell-rib));
  w=mix(w,vec3(0.,1.,0.),smoothstep(-.5,.5,min(shell,rib)-(p.y+.12)));
  return coffer(p.yz)*w.x+coffer(p.xz)*w.y+coffer(p.xy)*w.z;
 }
 float hall(vec3 p){
  vec3 q=cathedralWarp(p);
  // Elevated ellipsoidal dome, with an uninterrupted floor and deep axial passage.
  float inside=(1.-length(vec3(q.x/24.,max(q.y-9.,0.)/20.,(q.z+3.)/33.)))*18.;
  float passage=-box(q-vec3(0.,6.,-38.),vec3(4.5,6.5,18.),1.6);
  inside=-join(-inside,-passage,2.);
  // Actual side bays align with the four existing optional-path crossing planes.
  for(int i=0;i<2;i++){
   float z=i==0?-6.:9.;
   float bay=-box(vec3(abs(q.x)-28.,q.y-4.,q.z-z),vec3(10.,4.5,2.5),1.1);
   inside=-join(-inside,-bay,1.2);
  }
  inside=min(inside,q.y+.12);
  // Five thick arches grow directly out of the piers and bend across the nave.
  float bayZ=mod(q.z+5.,10.)-5.;
  float arc=length(vec2(q.x,max(q.y-13.,0.)))-13.;
  float theta=atan(max(q.y-13.,0.),q.x);
  float ribs=length(vec2(arc,bayZ))-(.88+.07*cos(theta*32.+time*.35));
  // Flanking mouldings produce nested profiles, rather than detached wire arches.
  float mould=length(vec2(arc-.85,abs(bayZ)-.65))-.32;
  ribs=join(ribs,mould,.3);
  ribs=max(ribs,abs(q.z)-23.);
  inside=join(inside,ribs,.9);
  vec3 o=ornament(q);
  // Carve into the solid, retaining thick load-bearing ribs and a walkable floor.
  float ribLimit=mix(.38,1.,smoothstep(1.,2.6,abs(arc)));
  float carving=(o.x-.055*o.y)*ribLimit*mix(.035,1.,smoothstep(.3,2.,q.y));
  return inside+carving;
 }
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro);float travel=.04;bool hit=false;
  for(int i=0;i<280;i++){float d=hall(ro+rd*travel);if(d<.004+travel*.00016){hit=true;break;}travel+=max(.002,d*.48);if(travel>105.)break;}
  vec3 p=ro+rd*travel,col=vec3(.025,.045,.09);
  if(hit){
   float e=.014;vec3 n=normalize(vec3(hall(p+vec3(e,0,0))-hall(p-vec3(e,0,0)),hall(p+vec3(0,e,0))-hall(p-vec3(0,e,0)),hall(p+vec3(0,0,e))-hall(p-vec3(0,0,e))));
   vec3 o=ornament(cathedralWarp(p));float band=.5+.5*cos(p.y*.28+sin(p.z*.14)+time*.17);
   vec3 enamel=mix(vec3(.025,.08,.19),vec3(.025,.28,.22),band);
   enamel=mix(enamel,vec3(.7,.39,.095),o.y*.85);
   enamel*=1.-.32*o.x;
   float ao=clamp(hall(p+n*.4)/.4,.15,1.)*clamp(hall(p+n*1.1)/1.1,.3,1.);
   vec3 l=normalize(vec3(-5.,19.,3.)-p),h=normalize(l-rd);
   float diff=max(dot(n,l),0.),fres=pow(1.-max(dot(n,-rd),0.),3.);
   col=enamel*(.32+diff*.95)*ao;
   col+=vec3(.9,.8,.6)*pow(max(dot(n,h),0.),64.)*.55*ao;
   col+=vec3(.18,.13,.42)*fres*.42+vec3(.045,.48,.37)*o.z*.22*ao;
   float axial=exp(-length((p-vec3(0.,7.,-35.))*vec3(.1,.09,.06)));
   col+=vec3(.15,.28,.38)*axial*.28;
   col=mix(col,vec3(.055,.075,.16),1.-exp(-travel*.009));
  }
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);gl_FragDepthEXT=hit?clamp(clip.z/clip.w*.5+.5,0.,1.):1.;
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const field=new T.Mesh(new T.BoxGeometry(240,240,240),m);field.frustumCulled=false;field.renderOrder=-1;root.add(field);materials.push(m);return field;
}
// Woven negative-curvature surfaces. The centre stays open for the actual walking route.
function vault(root,materials,motions,{radius=7,length=40,z=-10,palette=0,rush=false}={}){
 const rows=quality==='high'?96:60,cols=quality==='high'?128:80;
 const pos=[],uv=[],idx=[];
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const u=i/cols,v=j/rows,a=u*TAU;
  const scallop=.52*Math.cos(a*12+v*15)+.19*Math.cos(a*36-v*27);
  const r=radius+scallop+.5*Math.cos(v*TAU*5);
  pos.push(Math.cos(a)*r,Math.sin(a)*r+3,(v-.5)*length+z);uv.push(u,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const m=surface(palette,14,1,materials);m.uniforms.relief.value=.2;
 const shell=new T.Mesh(geo,m);root.add(shell);
 // Interlaced helical filaments give real parallax over the deeply folded enclosure.
 const points=[],colors=[];const color=new T.Color();
 for(let h=0;h<24;h++)for(let k=0;k<150;k++){
  for(const v of [k/150,(k+1)/150]){
   const a=h/24*TAU+Math.sin(v*13)*.17+v*TAU*(h%2?1:-1);
   const r=radius-.28+.22*Math.sin(v*40+h);
   points.push(Math.cos(a)*r,3+Math.sin(a)*r,z+(v-.5)*length);
   color.setHSL((h/24+v*.3)%1,.87,.51);colors.push(color.r,color.g,color.b);
  }
 }
 const wires=new T.BufferGeometry();wires.setAttribute('position',new T.Float32BufferAttribute(points,3));wires.setAttribute('color',new T.Float32BufferAttribute(colors,3));
 const weave=new T.LineSegments(wires,new T.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.52}));root.add(weave);
 motions.push(t=>{shell.rotation.z=Math.sin(t*.09)*.035;weave.rotation.z=t*(rush?.085:.016);});
 return shell;
}
// A sculpted chrysanthemum, built from recursively lobed folded petals, not rings.
function mandala(root,materials,motions,{z=-12,radius=6,palette=1}={}){
 const group=new T.Group();group.position.set(0,3,z);root.add(group);
 const pos=[],uv=[],idx=[],rows=20,cols=10;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const v=j/rows,u=i/cols*2-1;
  const width=Math.pow(Math.sin(Math.PI*v),.7)*(.8+.16*Math.cos(v*22));
  pos.push(u*width,v*3.3,.42*Math.sin(v*Math.PI)+.27*u*u*Math.sin(v*20));uv.push(i/cols,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const count=quality==='high'?320:192,m=surface(palette,24,1,materials);m.uniforms.relief.value=.13;
 const petals=new T.InstancedMesh(geo,m,count);petals.frustumCulled=false;group.add(petals);const dummy=new T.Object3D();
 motions.push(t=>{
  for(let i=0;i<count;i++){
   const per=32,layer=Math.floor(i/per),a=i%per/per*TAU+layer*.31+t*.012*(layer%2?1:-1);
   const s=1-layer*.063,r=radius*(1-layer*.067)+.15*Math.sin(t*.4+layer*.6);
   dummy.position.set(Math.sin(a)*r,Math.cos(a)*r,-layer*.5);
   dummy.rotation.set(.55+Math.sin(t*.27+layer*.6)*.38,Math.sin(a*3+t*.13)*.17,-a+Math.PI);
   dummy.scale.set(.5*s,1.2*s,.9*s);dummy.updateMatrix();petals.setMatrixAt(i,dummy.matrix);
  }
  petals.instanceMatrix.needsUpdate=true;group.rotation.z=Math.sin(t*.08)*.1;
 });return group;
}
// Open, recursively divided canopy: thin interwoven ribs leave the vault visible.
function lattice(root,materials,motions,{radius=14,z=-4,height=11,palette=3}={}){
 const s=structures(root,materials,{palette}),arms=quality==='high'?18:12,steps=12;
 const V=(x,y,z)=>new T.Vector3(x,y,z);
 function fork(a,dir,len,r,depth,phase){
  const b=a.clone().addScaledVector(dir,len);s.segment(a,b,r);
  if(!depth)return;
  for(const side of [-1,1]){
   const next=dir.clone().multiplyScalar(.7).add(V(Math.cos(phase)*side,.42,Math.sin(phase)*side)).normalize();
   fork(b,next,len*.52,r*.54,depth-1,phase+1.1);
  }
 }
 for(let arm=0;arm<arms;arm++)for(const side of [-1,1]){
  const phase=arm/arms*TAU;
  const point=u=>{const a=phase+side*u*TAU/arms*.82,r=radius*(.83-.14*Math.sin(u*Math.PI))+.16*Math.sin(u*TAU+phase);
   return V(Math.cos(a)*r,Math.sin(u*Math.PI)*2.7+u*.9+side*.13,Math.sin(a)*r);};
  for(let j=0;j<steps;j++){
   const u=j/steps,a=point(u),b=point((j+1)/steps);s.segment(a,b,.07*(1-u*.68));
   if(j%2===1){const radial=V(Math.cos(phase)*side*.65,.7,Math.sin(phase)*side*.65).normalize();
    fork(b,radial,.65+Math.sin(u*Math.PI)*.7,.029,quality==='high'?2:1,phase+u*2);
   }
  }
 }
 const canopy=s.finish();canopy.position.set(0,height-1.2,z);
 motions.push(t=>{canopy.rotation.y=Math.sin(t*.055)*.09;canopy.scale.y=1+Math.sin(t*.24)*.035;});return canopy;
}
// Spatial folds share an inexpensive vein shader; depth comes from the mesh, not tiled medallions.
function veinMaterial(palette,materials,{floral=false}={}){
 const colors=palettes[palette%palettes.length];
 const m=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{time:{value:0},radiance:{value:.7},surfaceMode:{value:0},floral:{value:floral?1:0},a:{value:new T.Color(colors[0])},b:{value:new T.Color(colors[1])},c:{value:new T.Color(colors[2])}},vertexShader:`
 varying vec3 vP,vN,vView;uniform float time;
 void main(){vP=position;vec3 n=normal;vec4 p=vec4(position,1.);
 #ifdef USE_INSTANCING
 mat3 basis=mat3(instanceMatrix);n=basis*(n/vec3(dot(basis[0],basis[0]),dot(basis[1],basis[1]),dot(basis[2],basis[2])));p=instanceMatrix*p;
 #endif
 p.x+=.065*sin(p.y*.8+time*.32)*smoothstep(0.,2.,p.y);p.z+=.055*sin(p.y*1.2-time*.24)*smoothstep(0.,2.,p.y);
 vN=normalize(normalMatrix*n);vec4 mv=modelViewMatrix*p;vView=mv.xyz;gl_Position=projectionMatrix*mv;
 }`,fragmentShader:`
 varying vec3 vP,vN,vView;uniform float time,radiance,surfaceMode,floral;uniform vec3 a,b,c;
 float cut(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d),.002),abs(d));}
 void main(){vec3 n=normalize(vN);float light=.2+.8*abs(dot(n,normalize(vec3(-.6,.8,1.))));
 float mid=cut(vP.x,.018)*(1.-surfaceMode);float vein=0.;vec2 p=vP.xy;
 p+=surfaceMode*vec2(sin(p.y*.73+sin(p.x*.4)),sin(p.x*.63-p.y*.3))*1.3;
 for(int i=0;i<4;i++){float k=pow(2.7,float(i));float d=sin((p.y-abs(p.x)*.66)*k*13.+sin(p.x*k*3.)+time*.15);vein+=cut(d,.045)/(1.+float(i)*1.9);p.x=abs(p.x)-.17/k;}
 float hue=.5+.5*sin(vP.y*2.+sin(vP.x*3.-vP.y*.7)*2.+time*.14);vec3 enamel=mix(b,c,pow(hue,5.)*.65);
 float rim=pow(1.-abs(dot(n,normalize(-vView))),3.);vec3 col=a*.5+enamel*(.045+light*.13)+c*mid*.7+enamel*vein*.5+enamel*rim*.3;
 col=mix(col,b*(.28+light*.22)+c*vein*.16,floral*.6);col*=mix(1.,.42,surfaceMode);
 gl_FragColor=vec4(col*radiance*1.65,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(m);return m;
}
function foldedLeaf(){
 const pos=[],uv=[],idx=[],rows=12,cols=6;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const v=j/rows,u=i/cols*2-1,w=Math.pow(Math.sin(v*Math.PI),.8)*(1+.18*Math.cos(v*Math.PI*12));
  pos.push(u*w*.38,v,.25*Math.sin(v*Math.PI)+Math.abs(u)*w*.23+Math.cos(u*Math.PI*3)*w*.06);uv.push(i/cols,v);
  if(j<rows&&i<cols){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();return geo;
}
// Garden-only broad, curled blades: a smooth living surface, not serrated foil.
function gardenLeaf(){
 const pos=[],uv=[],idx=[],rows=40,cols=20;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const v=j/rows,u=i/cols*2-1,w=Math.pow(Math.sin(v*Math.PI),.72);
  pos.push(u*w*.37,v,.16*Math.sin(v*Math.PI)-.12*v*v+u*u*w*.10);
  uv.push(i/cols,v);
  if(j<rows&&i<cols){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();return geo;
}
function gardenFoliage(palette,materials){
 const m=new T.ShaderMaterial({side:T.DoubleSide,extensions:{derivatives:true},uniforms:{time:{value:0},radiance:{value:.7},floral:{value:palette===4?1:0}},vertexShader:`
 varying vec3 localP,worldP,foliageN;uniform float time;
 void main(){localP=position;vec4 p=vec4(position,1.);vec3 n=normal;
 #ifdef USE_INSTANCING
 mat3 im=mat3(instanceMatrix);
 n/=vec3(dot(im[0],im[0]),dot(im[1],im[1]),dot(im[2],im[2]));n=im*n;
 p=instanceMatrix*p;
 #endif
 foliageN=mat3(modelMatrix)*n;
 p=modelMatrix*p;
 float rise=smoothstep(0.,4.,p.y);
 p.x+=rise*.17*sin(p.z*.31+p.y*.61+time*.47);p.z+=rise*.12*sin(p.x*.43+p.y*.7-time*.39);
 worldP=p.xyz;gl_Position=projectionMatrix*viewMatrix*p;
 }`,fragmentShader:`
 varying vec3 localP,worldP,foliageN;uniform float time,radiance,floral;
 float line(float d,float w){return 1.-smoothstep(w,w+max(fwidth(d),.002),abs(d));}
 void main(){
 vec3 n=normalize(foliageN),v=normalize(cameraPosition-worldP);if(dot(n,v)<0.)n=-n;
 vec3 l=normalize(vec3(-.6,1.,.7)),h=normalize(l+v);
 float rib=line(localP.x,.008),branch=sin((localP.y-abs(localP.x)*.8)*53.+sin(localP.x*12.)*.35);
 float veins=line(branch,.035)*smoothstep(.012,.045,abs(localP.x));
 float hue=.5+.5*sin(worldP.y*.63+worldP.z*.18+localP.y*3.-time*.19);
 vec3 base=mix(vec3(.008,.12,.075),vec3(.04,.43,.22),hue);
 base=mix(base,mix(vec3(.22,.008,.08),vec3(.85,.10,.24),hue),floral);
 float diffuse=.27+.73*max(dot(n,l),0.);
 vec3 film=.5+.5*cos(vec3(.2,2.3,4.4)+dot(n,v)*5.+localP.y*3.+time*.23);
 vec3 col=base*diffuse+base*.16*max(dot(-n,l),0.);
 col+=mix(vec3(.15,.48,.13),vec3(1.,.56,.16),floral)*(rib*.5+veins*.10);
 col+=film*pow(1.-max(dot(n,v),0.),3.)*.26;
 col+=mix(vec3(.65,1.,.8),film,.45)*pow(max(dot(n,h),0.),42.)*.9;
 col=mix(col,vec3(.035,.055,.10),1.-exp(-length(cameraPosition-worldP)*.009));
 gl_FragColor=vec4(col*(.65+radiance),1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(m);return m;
}
function structures(root,materials,{palette=2,organic=false}={}){
 const group=new T.Group();root.add(group);const stems=[],leaves=[],up=new T.Vector3(0,1,0);
 function segment(a,b,r){const d=b.clone().sub(a);stems.push({p:a.clone().add(b).multiplyScalar(.5),q:new T.Quaternion().setFromUnitVectors(up,d.clone().normalize()),s:new T.Vector3(r,d.length(),r)});}
 function leaf(a,b,width=1,roll=0){const d=b.clone().sub(a),q=new T.Quaternion().setFromUnitVectors(up,d.clone().normalize());q.multiply(new T.Quaternion().setFromAxisAngle(up,roll));leaves.push({p:a.clone(),q,s:new T.Vector3(d.length()*width,d.length(),d.length()*.65)});}
 function finish(){const mat=organic?gardenFoliage(palette,materials):veinMaterial(palette,materials),dummy=new T.Object3D();
  const stemGeo=new T.CylinderGeometry(.5,1,1,organic?18:5,organic?16:1);
  if(organic){const p=stemGeo.attributes.position;
   for(let i=0;i<p.count;i++){const t=p.getY(i)+.5;p.setX(i,p.getX(i)+Math.sin(t*Math.PI)*1.8);p.setZ(i,p.getZ(i)+Math.sin(t*Math.PI*2.)*.4);}
   stemGeo.computeVertexNormals();
  }
  for(const [parts,geo] of [[stems,stemGeo],[leaves,organic?gardenLeaf():foldedLeaf()]]){
   if(!parts.length){geo.dispose();continue;}const batch=new T.InstancedMesh(geo,mat,parts.length);
   parts.forEach((p,i)=>{dummy.position.copy(p.p);dummy.quaternion.copy(p.q);dummy.scale.copy(p.s);dummy.updateMatrix();batch.setMatrixAt(i,dummy.matrix);});batch.computeBoundingSphere();group.add(batch);
  }return group;
 }return {group,segment,leaf,finish};
}
// Recursive fronds split at several scales; the centre path is kept free below head height.
function growth(root,materials,motions,{x=0,y=0,z=0,height=7,spread=3,palette=2,seed=0,organic=false}={}){
 const s=structures(root,materials,{palette,organic}),V=(x,y,z)=>new T.Vector3(x,y,z);
 const depth=quality==='high'?3:2;
 function branch(a,dir,len,r,level,phase){
  const b=a.clone().addScaledVector(dir,len);s.segment(a,b,r*(organic?1.75:1));
  if(organic&&level<depth)for(let j=0;j<4;j++){
   const f=.22+j*.19,side=j%2?-1:1,base=a.clone().lerp(b,f);
   const fan=V(Math.cos(phase)*side,.24-.13*j,Math.sin(phase)*side).normalize();
   s.leaf(base,base.clone().addScaledVector(fan,len*(.65-.07*j)),.9,phase*.2+side*.4);
  }
  if(level===0){s.leaf(a,b,1.1,phase);return;}
  for(let k=0;k<3;k++){
   const angle=phase+k*2.399,origin=a.clone().lerp(b,.4+k*.19);
   const outward=V(Math.cos(angle)*spread/height,.48,Math.sin(angle)*spread/height).normalize();
   branch(origin,outward,len*(level===depth?.57:.49),r*.52,level-1,angle+1.3);
   if(level<depth)s.leaf(origin,origin.clone().addScaledVector(outward,len*.63),.72,angle);
  }
 }
 branch(V(0,0,0),V(.08*Math.sin(seed),1,.05*Math.cos(seed)).normalize(),height,.15*height/7,depth,seed);
 const g=s.finish();g.position.set(x,y,z);motions.push(t=>{g.rotation.y=Math.sin(t*.12+seed)*.055;g.scale.y=1+Math.sin(t*.25+seed)*.025;});return g;
}
// Garden variants: creek/flowers (DMT/1kcu4uv), folding light (o4e5yd),
// clockwork garden terrace (jqvq0s). A synthesis, not one shared reported place.
function gardenGround(root,materials){
 const shape=`
 float weave(vec2 p){return sin(p.x+sin(p.y*.73))*sin(p.y+cos(p.x*.61));}
 float relief(vec2 p){
  vec2 q=p*.82+vec2(sin(p.y*.29+time*.22),cos(p.x*.31-time*.19))*.65;
  float h=.5+.5*weave(q);h+=.19*weave(q*2.73+1.7)+.065*weave(q*7.1-2.3);
  float path=smoothstep(1.5,3.5,abs(p.x-.32*sin(p.y*.24)));
  float pond=exp(-pow((p.y-4.)/3.4,2.));
  float creek=-4.15+.65*sin(p.y*.27)-pond*.9;
  float bank=smoothstep(.88+pond*1.7,1.65+pond*1.7,abs(p.x-creek));
  return -.10+bank*(.06+(.07+path*.48)*h);
 }`;
 const m=new T.ShaderMaterial({side:T.DoubleSide,extensions:{derivatives:true},uniforms:{time:{value:0}},
  vertexShader:`uniform float time;varying vec3 gardenP;${shape}
   void main(){vec3 p=position;p.y=relief(p.xz);gardenP=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,
  fragmentShader:`uniform float time;varying vec3 gardenP;${shape}
   void main(){
    vec2 p=gardenP.xz;float h=relief(p),e=.015;
    vec3 n=normalize(vec3(relief(p-vec2(e,0.))-relief(p+vec2(e,0.)),2.*e,relief(p-vec2(0.,e))-relief(p+vec2(0.,e))));
    vec2 q=p*3.1+vec2(sin(p.y*.7-time*.16),cos(p.x*.9+time*.13));
    float lobes=.5+.5*weave(q);float fine=.5+.5*weave(q*3.37+weave(q.yx)*.7);
    float micro=.5+.5*weave(q*11.3+fine);
    float detail=1.-smoothstep(.12,.7,length(fwidth(q)));
    float path=1.-smoothstep(1.5,3.5,abs(p.x-.32*sin(p.y*.24)));
    vec3 green=mix(vec3(.012,.095,.055),vec3(.055,.31,.18),lobes);
    vec3 film=.5+.5*cos(vec3(.3,2.1,4.4)+h*8.+lobes*2.8+time*.14);
    vec3 base=mix(green,vec3(.10,.14,.13),path*.72);
    base*=.7+.3*fine;base+=film*pow(fine,9.)*detail*.075;
    vec3 v=normalize(cameraPosition-gardenP),l=normalize(vec3(-.4,1.,.35));
    float diffuse=.36+.64*max(dot(n,l),0.);
    float spec=pow(max(dot(n,normalize(l+v)),0.),38.);
    vec3 col=base*diffuse+mix(vec3(.15,.3,.23),film,.5)*spec*(.25+.35*fine);
    col+=film*pow(micro,18.)*pow(lobes,4.)*detail*.14;
    col+=green*pow(1.-max(dot(n,v),0.),3.)*.22;
    col=mix(col,vec3(.045,.052,.09),1.-exp(-length(cameraPosition-gardenP)*.015));
    gl_FragColor=vec4(col,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
   }`});
 const geo=new T.PlaneGeometry(36,48,180,240);geo.rotateX(-Math.PI/2);geo.translate(0,0,-3);
 const ground=new T.Mesh(geo,m);ground.userData.evidence=['realm|The Garden'];
 root.add(ground);materials.push(m);return ground;
}
function gardenDetails(root,materials,motions){
 const g=new T.Group();root.add(g);g.userData.evidence=['realm|The Garden'];
 // Rooted leafy boughs take the place of the detached wire roof.
 const canopy=new T.Group();g.add(canopy);
 const canopyMat=gardenFoliage(2,materials),boughLeaves=structures(canopy,materials,{palette:2,organic:true});
 for(const z of [12,4,-4,-12,-20])for(const side of [-1,1]){
  const curve=new T.CatmullRomCurve3([
   new T.Vector3(side*8,-.08,z),new T.Vector3(side*7.4,4.2,z+.4),
   new T.Vector3(side*5.1,7.7,z-.6),new T.Vector3(side*1.9,9.1,z+.6),
   new T.Vector3(-side*1.8,9.8,z-1.2)]);
  const geo=new T.TubeGeometry(curve,64,.19,12,false);
  canopy.add(new T.Mesh(geo,canopyMat));
  for(let j=0;j<24;j++){
   const t=.22+j*.031,a=curve.getPoint(t),tangent=curve.getTangent(t);
   const across=new T.Vector3(-tangent.y,tangent.x,0).multiplyScalar((j%2?1:-1)*(.8+Math.sin(j*1.7)*.2));
   across.z=(j%2?1:-1)*.6;const b=a.clone().add(across);
   boughLeaves.segment(a,b,.035);boughLeaves.leaf(a,b.clone().addScaledVector(across,.65),.72,j*.7);
   boughLeaves.leaf(a.clone().lerp(b,.45),b.clone().add(new T.Vector3(0,.25,.45)),.6,-j*.5);
  }
 }
 boughLeaves.finish();
 const pos=[],uv=[],indices=[],bankPos=[],bankIndices=[],rows=160,cols=12;
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const z=16-j/rows*36,u=i/cols*2-1,pond=Math.exp(-Math.pow((z-4)/3.4,2));
  const center=-4.15+.65*Math.sin(z*.27)-pond*.9,width=.88+pond*1.7;
  pos.push(center+u*width,.035,z);uv.push(i/cols,z);
  if(j<rows&&i<cols){const k=j*(cols+1)+i;indices.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
  if(i===0)for(const side of [-1,1]){
   for(let k=0;k<3;k++)bankPos.push(center+side*(width+k*.2),k===1?.085:k===0?.035:-.02,z);
   if(j<rows)for(let k=0;k<2;k++){const a=j*6+(side===1?3:0)+k;bankIndices.push(a,a+1,a+6,a+1,a+7,a+6);}
  }
 }
 const bankGeo=new T.BufferGeometry();bankGeo.setAttribute('position',new T.Float32BufferAttribute(bankPos,3));bankGeo.setIndex(bankIndices);bankGeo.computeVertexNormals();g.add(new T.Mesh(bankGeo,veinMaterial(2,materials)));
 const waterGeo=new T.BufferGeometry();waterGeo.setAttribute('position',new T.Float32BufferAttribute(pos,3));waterGeo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));waterGeo.setIndex(indices);waterGeo.computeVertexNormals();
 const water=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{time:{value:0},radiance:{value:.7}},vertexShader:`
 varying vec2 vUv;uniform float time;
 void main(){vUv=uv;vec3 p=position;p.y+=.024*sin(p.z*4.-time*1.7+sin(p.x*7.));gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}
 `,fragmentShader:`
 varying vec2 vUv;uniform float time,radiance;
 void main(){vec2 p=vec2(vUv.x*5.,vUv.y);float flow=p.y-time*.65;
 float ripple=sin(flow*7.+sin(p.x*5.+sin(flow*.7))*2.2);
 float fine=sin(flow*27.+sin(p.x*17.-flow*1.3)*2.);
 float glint=pow(.5+.5*ripple,24.)*.24+pow(.5+.5*fine,28.)*.1;
 float bank=pow(abs(vUv.x*2.-1.),12.);float reflection=.5+.5*sin(p.x*8.+sin(flow*.8)*2.);
 vec3 col=mix(vec3(.008,.055,.16),vec3(.015,.39,.37),reflection*.7);
 col+=vec3(.24,.85,1.)*glint+vec3(.12,.3,.22)*bank*(.25+.15*sin(flow*3.));
 gl_FragColor=vec4(col*(.7+radiance),1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});materials.push(water);g.add(new T.Mesh(waterGeo,water));
 // Multi-tier corollas open at different phases; all plants stay outside x ±2.6.
 const flowers=quality==='high'?84:48,per=quality==='high'?30:21;
 const petals=new T.InstancedMesh(gardenLeaf(),gardenFoliage(4,materials),flowers*per);
 petals.frustumCulled=false;g.add(petals);const dummy=new T.Object3D(),blooms=[],facing=new T.Quaternion().setFromEuler(new T.Euler(.5,0,0));
 const stems=structures(g,materials,{palette:2,organic:true}),V=(x,y,z)=>new T.Vector3(x,y,z);
 for(let n=0;n<flowers;n++){
  const side=n%2?1:-1,z=11-Math.floor(n/2)*.74,x=side*(3.5+(n%5)*1.42),y=.8+(n%4)*.33;
  blooms.push({x,y,z,phase:n*2.399,size:.46+(n%3)*.13});
  stems.segment(V(x,0,z),V(x,y,z),.033);stems.leaf(V(x,y*.25,z),V(x+side*.45,y*.72,z+.2),.8,n);
 }
 stems.finish();
 motions.push(t=>{
  blooms.forEach((b,n)=>{const opened=.5+.5*Math.sin(t*.48+b.phase),sway=.09*Math.sin(t*.32+b.phase);
   for(let k=0;k<per;k++){
    const layer=Math.floor(k/(per/3)),a=k/(per/3)*TAU+layer*.38,tilt=.24+opened*1.02+layer*.13;
    dummy.position.set(b.x+sway,b.y+layer*.065,b.z);dummy.rotation.set(0,a,tilt);
    dummy.quaternion.premultiply(facing);
    const s=b.size*(1-layer*.21);dummy.scale.set(s*.9,s,s);dummy.updateMatrix();petals.setMatrixAt(n*per+k,dummy.matrix);
   }
  });petals.instanceMatrix.needsUpdate=true;
 });
 // A small lateral brick terrace, with actual treads and articulated gearing.
 const terrace=new T.Group();terrace.position.set(8,0,-1);g.add(terrace);
 const brickMat=veinMaterial(1,materials),blocks=[];
 for(let row=0;row<9;row++)for(let col=0;col<6;col++)blocks.push([ -2.2+col*.86+(row%2)*.16,.25+row*.43,-2.7,.8,.39,.5]);
 blocks.push([0,.62,0,4.8,1.24,5.2]);
 for(let i=0;i<6;i++)blocks.push([0,(i+1)*.105,5.2-i*.44,2,(i+1)*.21,.46]);
 const masonry=new T.InstancedMesh(new T.BoxGeometry(1,1,1),brickMat,blocks.length);
 blocks.forEach((b,i)=>{dummy.position.set(...b.slice(0,3));dummy.rotation.set(0,0,0);dummy.scale.set(...b.slice(3));dummy.updateMatrix();masonry.setMatrixAt(i,dummy.matrix);});masonry.computeBoundingSphere();terrace.add(masonry);
 const iron=structures(terrace,materials,{palette:3});
 for(const x of [-2.25,2.25]){for(let z=-2.4;z<=2.5;z+=.6)iron.segment(V(x,1.24,z),V(x,2.2,z),.033);iron.segment(V(x,2.2,-2.4),V(x,2.2,2.5),.045);}
 iron.finish();
 const mechanism=new T.Group();mechanism.position.set(-2.4,2.1,2.5);terrace.add(mechanism);
 function gear(radius,teeth,x,y,speed){
  const shape=new T.Shape();
  for(let i=0;i<=teeth*4;i++){const a=i/(teeth*4)*TAU,r=radius*(i%4===1||i%4===2?1:.85);const px=Math.cos(a)*r,py=Math.sin(a)*r;if(i===0)shape.moveTo(px,py);else shape.lineTo(px,py);}
  const hole=new T.Path();hole.absarc(0,0,radius*.66,0,TAU,true);shape.holes.push(hole);
  const wheel=new T.Group();wheel.position.set(x,y,0);mechanism.add(wheel);
  const mat=veinMaterial(3,materials);wheel.add(new T.Mesh(new T.ExtrudeGeometry(shape,{depth:.14,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.024,bevelThickness:.025,curveSegments:32}),mat));
  const ribs=structures(wheel,materials,{palette:3});
  for(let k=0;k<6;k++){const a=k/6*TAU;ribs.segment(V(0,0,.08),V(Math.cos(a)*radius*.72,Math.sin(a)*radius*.72,.08),.045);}
  ribs.finish();motions.push(t=>{wheel.rotation.z=t*speed;});
 }
 gear(.92,24,0,0,.12);gear(.61,16,1.39,.03,-.18);gear(.46,12,.06,1.29,-.24);
 const lever=new T.Group();lever.position.set(1.39,.03,.24);mechanism.add(lever);
 const handle=structures(lever,materials,{palette:1});handle.segment(V(0,0,0),V(.15,1.35,0),.075);handle.segment(V(.15,1.35,0),V(.48,1.35,0),.1);handle.finish();
 motions.push(t=>{lever.rotation.z=Math.sin(t*.36)*.5;});return g;
}
// Workshop variants: 1nenuqr pistons/cogs; 3d1lik clockwork manufacturing;
// 18te7qt white box-carriers; z270gs white-on-black boxed-body grid.
// A synthesis of distinct reports, not a single universal factory layout.
// Workshop-only continuous enclosure: receding manufactured ribs, flowing enamel,
// and a pearl/graphite wing share actual depth rather than line-covered panels.
function workshopShell(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`
 precision highp float;
 uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float fusion(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float scroll(vec3 p){return dot(sin(p),cos(p.yzx));}
 float relief(vec3 p){
  vec3 q=p*.57+.24*sin(p.zxy*.31+time*.19);
  float a=scroll(q+vec3(0.,time*.22,-time*.17));
  float b=scroll(q*2.13+.35*sin(q.yzx)+vec3(time*.13));
  return .18*sin(a*1.9)+.075*sin(b*2.3)+.045*sin(scroll(q*5.7)*2.);
 }
 // Irregular, advecting gem settings: no repeating texture or separate wire overlay.
 vec4 jewels(vec2 uv){
  uv+=.28*sin(uv.yx*.73+vec2(time*.19,-time*.16));
  uv+=.13*sin(uv.yx*1.71+vec2(.7,-.4)*time*.22);
  vec2 cell=floor(uv),f=fract(uv),nearest=vec2(0.);float best=10.,identity=0.;
  for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){
   vec2 offset=vec2(float(x),float(y)),id=cell+offset;
   vec2 seed=fract(sin(vec2(dot(id,vec2(127.1,311.7)),dot(id,vec2(269.5,183.3))))*43758.5453);
   vec2 q=f-offset-(.5+.3*sin(seed*6.283+time*.14));
   vec2 a=abs(q);float d=max(max(a.x,a.y),dot(a,vec2(.7071)));
   if(d<best){best=d;nearest=q;identity=seed.x;}
  }
  return vec4(nearest,best,identity);
 }
 float field(vec3 p){
  float r=relief(p);
  float floorD=p.y+.12-r*.56;
  float wall=20.-abs(p.x)-r;
  float roof=15.-p.y-.009*p.x*p.x-r;
  float shell=min(floorD,min(wall,min(roof,min(p.z+74.,14.-p.z))));
  float repeatZ=mod(p.z+3.5,9.)-4.5;
  float vault=length(vec2(p.x*.72,p.y-1.))-12.9;
  float rib=length(vec2(vault,repeatZ))-(.36+.09*sin(p.y*.8+time*.35));
  // Paired inset mouldings nest inside each rib; smooth junctions stay solid.
  float inner=length(vec2(vault+.68,abs(repeatZ)-.64))-.13;
  return fusion(shell,min(rib,inner),.5);
 }
 vec3 normalAt(vec3 p){vec2 e=vec2(.012,0.);return normalize(vec3(field(p+e.xyy)-field(p-e.xyy),field(p+e.yxy)-field(p-e.yxy),field(p+e.yyx)-field(p-e.yyx)));}
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro),p=ro;float travel=.03;bool hit=false;
  for(int i=0;i<112;i++){
   p=ro+rd*travel;float d=field(p);
   if(d<.009+travel*.00017){hit=true;break;}
   travel+=max(d*.62,.012);if(travel>120.)break;
  }
  vec3 col=vec3(.012,.022,.045);
  if(hit){
   vec3 n=normalAt(p),surfaceN=n,v=-rd;
   bool flooring=p.y<.55;
   vec2 uv=flooring?p.xz:vec2(atan(p.y-1.,p.x*.72)*18.,p.z);
   uv*=2.3;
   vec4 gem=jewels(uv);
   float radius=.32+.09*gem.w;
   float inset=1.-smoothstep(radius-.035,radius+.014,gem.z);
   float bezel=exp(-pow((gem.z-radius)*63.,2.));
   float cut=smoothstep(radius*.48,radius*.88,gem.z)*(1.-smoothstep(radius-.015,radius+.03,gem.z));
   float angle=floor(atan(gem.y,gem.x)/.785398+.5)*.785398;
   vec2 facet=vec2(cos(angle),sin(angle));
   vec3 tangent=flooring?vec3(1.,0.,0.):normalize(vec3(-p.y+1.,p.x*.72,0.));
   tangent=normalize(tangent-surfaceN*dot(tangent,surfaceN));
   vec3 bitangent=normalize(cross(surfaceN,tangent));
   float micro=sin(gem.z*155.+sin(angle*8.+time*.3)*1.5);
   n=normalize(surfaceN+tangent*(facet.x*cut*.62+gem.x*.13+micro*.055)+bitangent*(facet.y*cut*.62+gem.y*.13));
   float filigree=pow(.5+.5*sin(gem.z*105.+sin(atan(gem.y,gem.x)*12.)*1.7-time*.6),14.);
   float nested=pow(.5+.5*sin(uv.x*19.+sin(uv.y*13.+time*.24)*2.)*sin(uv.y*21.-time*.27),8.);
   vec3 spectral=pow(.5+.5*cos(vec3(.1,2.2,4.3)+gem.w*6.283+p.z*.04-time*.15),vec3(2.4));
   vec3 enamel=mix(vec3(.012,.022,.038),spectral*.62+.015,inset);
   enamel=mix(enamel,vec3(.62,.28,.038),bezel*.85);
   float mono=smoothstep(3.5,6.5,p.x);
   float pearl=mix(.025,.13+gem.w*.42,inset)+bezel*.2;
   enamel=mix(enamel,vec3(pearl)*vec3(.93,.97,1.03),mono);
   vec3 l=normalize(vec3(-.4,.8,.45)),h=normalize(l+v);
   float diffuse=.2+.72*max(dot(n,l),0.);
   float fres=pow(1.-max(dot(n,v),0.),3.);
   float ao=clamp(field(p+surfaceN*.38)/.38,.22,1.);
   float gloss=pow(max(dot(n,h),0.),72.);
   vec3 ray=reflect(-v,n);
   float strip=pow(.5+.5*sin(ray.y*11.+ray.x*4.),22.);
   vec3 reflected=.12+.1*cos(vec3(.3,2.5,4.8)+ray.y*4.+ray.z*2.);
   reflected=mix(reflected,vec3(dot(reflected,vec3(.3,.59,.11))),mono);
   col=enamel*diffuse*ao+reflected*(.1+.35*fres)+vec3(1.,.86,.63)*gloss*.85;
   col+=mix(vec3(.8,.59,.24),vec3(.7),mono)*strip*(.12+.36*inset);
   col+=mix(spectral,vec3(.5),mono)*(filigree*.16+nested*.09)*ao;
   col+=enamel*inset*.18;
   col=mix(col,vec3(.026,.045,.08),1.-exp(-travel*.011));
  }
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);
  gl_FragDepthEXT=hit?clamp(clip.z/clip.w*.5+.5,0.,1.):1.;
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const field=new T.Mesh(new T.BoxGeometry(200,200,200),m);field.frustumCulled=false;field.renderOrder=-1;
 field.userData.evidence=['realm|The Workshop / Factory / Market'];root.add(field);materials.push(m);return field;
}
function workshopDetails(root,materials,motions){
 const g=new T.Group();root.add(g);
 // Rounded enamel machinery, with flowing engraved relief and broad reflected light.
 const machineTime={value:0};motions.push(t=>{machineTime.value=t;});
 function enamel(color,mono=false,dark=false){
  const m=new T.MeshPhysicalMaterial({color,metalness:dark?.64:.48,roughness:.24,clearcoat:1,clearcoatRoughness:.16});
  m.onBeforeCompile=s=>{
   s.uniforms.machineTime=machineTime;
   s.vertexShader='varying vec3 machineP;\n'+s.vertexShader;
   s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nmachineP=position;');
   s.fragmentShader='varying vec3 machineP; uniform float machineTime;\n'+s.fragmentShader;
   s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    vec3 mp=machineP;float flow=sin(mp.y*8.+mp.z*5.-machineTime*.6);
    float engraving=pow(.5+.5*sin(mp.x*85.+flow*3.+sin(mp.y*31.)*1.4),12.);
    diffuseColor.rgb*=.78+.22*engraving;
   `);
   s.fragmentShader=s.fragmentShader.replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
    vec3 reflected=reflect(-normalize(vViewPosition),normal);
    float softbox=pow(.5+.5*sin(reflected.y*8.+reflected.x*3.),18.);
    float edge=pow(1.-abs(dot(normalize(vViewPosition),normal)),3.);
    vec3 spectral=${mono?'vec3(.7,.76,.8)':'(.5+.5*cos(reflected.y*5.+reflected.x*3.+vec3(0.,2.,4.)))'};
    totalEmissiveRadiance+=spectral*(softbox*.5+edge*.22)+vec3(.12)*engraving*softbox;
   `);
  };
  return m;
 }
 const white=enamel(0x929998,true),black=enamel(0x10151b,true,true);
 const steel=enamel(0x21556a,false,true),gold=enamel(0xa96522);
 const pattern=veinMaterial(1,materials);
 const outline=new T.Shape();outline.moveTo(-.36,-.5);outline.lineTo(.36,-.5);outline.quadraticCurveTo(.5,-.5,.5,-.36);outline.lineTo(.5,.36);outline.quadraticCurveTo(.5,.5,.36,.5);outline.lineTo(-.36,.5);outline.quadraticCurveTo(-.5,.5,-.5,.36);outline.lineTo(-.5,-.36);outline.quadraticCurveTo(-.5,-.5,-.36,-.5);
 const unit=new T.ExtrudeGeometry(outline,{depth:.72,bevelEnabled:true,bevelSize:.1,bevelThickness:.14,bevelSegments:4,curveSegments:8,steps:1});unit.translate(0,0,-.36);
 const orb=new T.SphereGeometry(1,48,32);
 function box(parent,material,x,y,z,w,h,d){const m=new T.Mesh(unit,material);m.position.set(x,y,z);m.scale.set(w,h,d);parent.add(m);return m;}
 function bulb(parent,material,x,y,z,w,h,d){const m=new T.Mesh(orb,material);m.position.set(x,y,z);m.scale.set(w,h,d);parent.add(m);return m;}
 function pipe(parent,material,points,r){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));const m=new T.Mesh(new T.TubeGeometry(curve,64,r,12,false),material);parent.add(m);return m;}
 function ring(parent,material,x,y,z,r,t){const m=new T.Mesh(new T.TorusGeometry(r,t,16,96),material);m.position.set(x,y,z);parent.add(m);return m;}
 // The continuous shell carries the monochrome wing; stations retain its contrast.
 const gearGeo=new T.TorusGeometry(.81,.15,16,240);
 const gearP=gearGeo.attributes.position;
 for(let i=0;i<gearP.count;i++){const x=gearP.getX(i),y=gearP.getY(i),a=Math.atan2(y,x),r=Math.hypot(x,y),lobe=.075*Math.cos(a*20.);gearP.setXYZ(i,x*(r+lobe)/r,y*(r+lobe)/r,gearP.getZ(i));}gearGeo.computeVertexNormals();
 function gear(parent,x,y,z,r,material){
  const wheel=new T.Group();wheel.position.set(x,y,z);wheel.scale.setScalar(r);parent.add(wheel);wheel.add(new T.Mesh(gearGeo,material));
  ring(wheel,steel,0,0,0,.57,.05);
  for(let k=0;k<6;k++){const a=k*TAU/6;pipe(wheel,material,[[.2*Math.cos(a),.2*Math.sin(a),.02],[.45*Math.cos(a+.35),.45*Math.sin(a+.35),.08],[.75*Math.cos(a+.15),.75*Math.sin(a+.15),0]],.065);}
  bulb(wheel,material,0,0,.06,.24,.24,.19);ring(wheel,steel,0,0,.23,.12,.045);return wheel;
 }
 const packets=[],presses=[],wheels=[],workers=[];
 for(const side of [-1,1])for(const [index,z] of [7,-1,-9,-19,-31,-45,-61].entries()){
  const station=new T.Group();station.position.set(side*7,0,z);g.add(station);
  const mono=side===1,frame=mono?white:gold,body=mono?black:steel;
  box(station,body,0,.95,0,4.1,1.05,5.3);
  for(const x of [-1.65,1.65]){
   bulb(station,frame,x,.8,0,.52,.8,2.65);
   pipe(station,frame,[[x,1.25,1.8],[x*1.1,2.7,.3],[x,4.1,-1.6],[x*.6,4.75,-1.8],[0,4.95,-1.8]],.29);
   pipe(station,body,[[x,1.4,2.3],[x*1.2,3.1,.1],[x,4.55,-1.9],[0,5.25,-1.9]],.12);
  }
  bulb(station,frame,0,4.25,-1.6,.7,.72,.65);
  for(let k=0;k<6;k++){const collar=ring(station,body,0,3.8+k*.15,-1.6,.4,.055);collar.rotation.x=Math.PI/2;}
  const piston=new T.Group();station.add(piston);bulb(piston,mono?white:steel,0,3.3,-1.6,.19,.84,.19);box(piston,frame,0,2.62,-1.6,1.65,.32,1.35);
  presses.push({piston,phase:index*.81+side});
  // Long parallel rails, transverse rollers and products make the transport direction readable.
  for(const x of [-1.3,1.3])box(station,frame,x,1.62,0,.12,.2,5.6);
  for(let k=0;k<12;k++)bulb(station,mono?white:steel,0,1.57,-2.5+k*.45,1.2,.14,.14);
  for(let k=0;k<3;k++){
   const packet=new T.Group();station.add(packet);bulb(packet,mono?white:pattern,0,0,0,.48,.42,.48);
   for(const y of [-.23,0,.23]){const band=ring(packet,mono?black:gold,0,y,0,Math.sqrt(.25-y*y),.028);band.rotation.x=Math.PI/2;}
   packets.push({packet,phase:k/3+index*.117});
  }
  // Rounded drive housings enclose moving, interlocking lobed wheels.
  for(const x of [-.8,.65]){bulb(station,body,x,2.4,2.55,1.08,1.08,.42);ring(station,frame,x,2.4,2.86,1.01,.13);}
  const a=gear(station,-.8,2.4,2.95,.88,frame),b=gear(station,.65,2.4,2.95,.66,frame);
  wheels.push({wheel:a,speed:.41,phase:index},{wheel:b,speed:-.41*.88/.66,phase:index+.08});
  // Tiny boxed carriers beside larger products give an explicit local scale comparison.
  if(mono){const worker=new T.Group();worker.position.set(-1.78,1.55,.4);station.add(worker);
   box(worker,white,0,.46,0,.26,.3,.2);box(worker,white,0,.73,0,.24,.24,.24);
   for(const x of [-.09,.09])box(worker,white,x,.19,0,.07,.3,.08);
   for(const x of [-.2,.2])box(worker,white,x,.49,.13,.08,.08,.36);
   box(worker,white,0,.52,.4,.34,.3,.3);workers.push({worker,phase:index});
  }
  // Linked work lines replace the old freestanding rectangular gantries.
  pipe(g,frame,[[side*9,1.1,z+3],[side*9.2,2.5,z+1],[side*9.2,2.5,z-3],[side*9,1.1,z-5]],.24);
  if(index>2)box(g,body,side*7,1.3,z+4,4.4,.3,5.8);
 }
 motions.push(t=>{
  for(const {wheel,speed,phase} of wheels)wheel.rotation.z=t*speed+phase;
  for(const {piston,phase} of presses)piston.position.y=.46*Math.sin(t*1.17+phase);
  for(const {packet,phase} of packets)packet.position.set(0,2.03,((t*.073+phase)%1)*4.8-2.4);
  for(const {worker,phase} of workers)worker.position.z=.4+Math.sin(t*.63+phase)*.6;
 });
 g.traverse(o=>{if(o.isMesh)o.userData.evidence=['realm|The Workshop / Factory / Market'];});return g;
}
// Rib cages grow into fan vaults, with recursive spurs and folded webs between the ribs.
function arcade(root,materials,motions,{x=0,z=0,width=16,height=10,ry=0,palette=3}={}){
 const s=structures(root,materials,{palette}),V=(x,y,z)=>new T.Vector3(x,y,z),r=width/2;
 for(const side of [-1,1])for(let rail=0;rail<3;rail++){
  let a=V(side*(r+(rail-1)*.13),0,(rail-1)*.38);
  for(let j=1;j<=9;j++){
   const t=j/9,inset=Math.pow(Math.max(0,(t-.48)/.52),1.6)*r;
   const b=V(side*(r-inset+(rail-1)*.13),height*t,(rail-1)*(.38+Math.sin(t*Math.PI)*.45));s.segment(a,b,.11+(1-t)*.06);
   if(j>2){const end=b.clone().add(V(-side*width*.07,height*.075,rail===1?.35:(rail-1)*.9));s.segment(b,end,.055);s.leaf(a,end,.65,side*.7);
    for(let k=0;k<3;k++){const c=b.clone().lerp(end,.3+k*.25),tip=c.clone().add(V(-side*width*.027,height*.027,(k-1)*.23));s.segment(c,tip,.023);s.leaf(c,tip,.8,k);}}
   a=b;
  }
 }
 const g=s.finish();g.position.set(x,0,z);g.rotation.y=ry;return g;
}
// A pleated, branching relief skin: substantial silhouette depth instead of a smooth plane.
function panel(root,materials,{w=10,h=10,x=0,y=0,z=0,rx=0,ry=0,palette=3,depth=.65,ground=false}={}){
 const cols=Math.ceil(w*3),rows=Math.ceil(h*3),pos=[],uv=[],idx=[];
 for(let j=0;j<=rows;j++)for(let i=0;i<=cols;i++){
  const u=i/cols,v=j/rows,px=(u-.5)*w,py=(v-.5)*h;
  const fold=Math.abs(Math.sin(px*1.3+Math.sin(py*.65)*1.7))+.38*Math.abs(Math.sin(px*3.7-py*1.8));
  // Passage edges curl into the enclosure; shallow central relief leaves walking clear.
  const bank=ground?Math.pow(Math.abs(px)/(w*.5),4)*(.65+.25*Math.sin(py*.47)):0;
  const swell=ground?0:.28*Math.sin(px*.37+py*.21)*Math.cos(py*.43);
  pos.push(px,py,depth*(fold-.6+swell)+bank);uv.push(u,v);
  if(i<cols&&j<rows){const k=j*(cols+1)+i;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
 }
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
 const m=new T.Mesh(geo,veinMaterial(palette,materials));m.material.uniforms.surfaceMode.value=1;m.position.set(x,y,z);m.rotation.set(rx,ry,0);root.add(m);return m;
}
// Connected, nonliteral script grows along curved carriers in several depth planes.
function language(root,materials,motions){
 // Download only: spoken forms condense into continuous, turning calligraphic solids.
 const g=new T.Group();root.add(g);
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`precision highp float;
 uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float join(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float stroke(vec3 p,vec3 a,vec3 b,float r){vec3 ab=b-a;return length(p-a-ab*clamp(dot(p-a,ab)/dot(ab,ab),0.,1.))-r;}
 mat2 turn(float a){return mat2(cos(a),-sin(a),sin(a),cos(a));}
 float field(vec3 p){
  float d=100.;
  for(int layer=0;layer<2;layer++)for(int side=0;side<2;side++){
   float h=float(layer),s=side==0?-1.:1.;
   float index=clamp(floor((1.-p.z)/2.65+.5),0.,4.);
   float z=1.-index*2.65,phase=index*1.91+h*2.4+s*.6+time*.65;
   vec3 centre=vec3(s*(1.65+index*.57+h*.32),2.9+h*1.85+.28*sin(phase*.7),z-h*.35);
   vec3 q=p-centre;q.xz=turn(.34*sin(phase))*q.xz;q.xy=turn(s*.25+phase*.23)*q.xy;
   q.yz=turn(.28*cos(phase*.8))*q.yz;
   float angle=atan(q.y,q.x),radius=.63+.13*sin(angle*3.+phase)+.045*cos(angle*7.-phase*.7);
   float width=.105+.035*sin(angle*2.+phase);
   float glyph=length(vec2((length(q.xy)-radius)*.8,q.z*1.35))-width;
   // Each orbital stroke carries an inner loop and branching, curling ascenders.
   vec3 b=q-vec3(.16*sin(phase),.07,.015);b.xy=turn(-phase*.6)*b.xy;
   glyph=join(glyph,length(vec2(length(b.xy/vec2(1.,.72))-.265,b.z*1.25))-.067,.09);
   for(int j=0;j<3;j++){
    float a=float(j)*2.094+phase*.3;
    vec3 v=vec3(cos(a),sin(a),0.),w=vec3(-v.y,v.x,0.);
    vec3 start=v*.4,end=v*(.91+.13*sin(phase+float(j)))+w*.18;
    glyph=join(glyph,stroke(q,start,end,.079),.1);
    glyph=join(glyph,stroke(q,end,end+w*(.28+.1*sin(phase*1.3))+vec3(0.,0.,.11),.061),.07);
   }
   float depth=clamp((1.-p.z)/2.65,0.,4.);
   vec2 track=vec2(s*(1.65+depth*.57+h*.32),2.9+h*1.85+.28*sin((depth*1.91+h*2.4+s*.6+time*.65)*.7));
   float stem=max(length((p.xy-track)/vec2(1.,.8))-.095,max(p.z-1.,-9.6-p.z));
   glyph=join(glyph,stem,.13);
   d=join(d,glyph,.075);
  }
  // Fine intaglio is cut into the solid, not drawn as wire geometry.
  float cut=sin(p.x*35.+sin(p.y*13.+time))*sin(p.y*31.+p.z*9.)*sin(p.z*29.-time*.6);
  return (d+cut*.009)*.48;
 }
 vec3 normalAt(vec3 p){vec2 e=vec2(.003,0.);return normalize(vec3(field(p+e.xyy)-field(p-e.xyy),field(p+e.yxy)-field(p-e.yxy),field(p+e.yyx)-field(p-e.yyx)));}
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro),inv=1./rd;
  vec3 a=(vec3(-6.,.8,-11.8)-ro)*inv,b=(vec3(6.,6.5,2.5)-ro)*inv;
  vec3 lo=min(a,b),hi=max(a,b);float travel=max(0.,max(lo.x,max(lo.y,lo.z))),end=min(hi.x,min(hi.y,hi.z));
  bool hit=false;vec3 p;
  for(int i=0;i<176;i++){p=ro+rd*travel;float d=field(p);if(d<.002){hit=true;break;}travel+=max(.0015,d);if(travel>end)break;}
  if(!hit)discard;
  vec3 n=normalAt(p),v=-rd,l=normalize(vec3(-.4,.9,1.));
  vec3 q=p*7.+.5*sin(p.yzx*3.+time*.45);float etch=dot(sin(q),cos(q.zxy));
  float inlay=exp(-etch*etch*18.);
  vec3 film=.5+.5*cos(vec3(.2,2.1,4.3)+dot(n,v)*5.+p.z*.42+time*.33);
  vec3 col=mix(vec3(.045,.36,.29),vec3(1.1,.55,.085),.5+.5*sin(p.z*.65+p.y+time*.35));
  col*=.42+.72*max(dot(n,l),0.);col=mix(col,vec3(.022,.065,.12),inlay*.7);
  col+=film*pow(1.-max(dot(n,v),0.),2.)*.65;
  col+=vec3(1.,.86,.49)*pow(max(dot(n,normalize(l+v)),0.),38.)*1.1;
  col+=film*.1;
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);gl_FragDepthEXT=clamp(clip.z/clip.w*.5+.5,0.,1.);
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 m.userData.entity=true;materials.push(m);
 const volume=new T.Mesh(new T.BoxGeometry(12,5.7,14.3).translate(0,3.65,-4.65),m);g.add(volume);
 return g;
}
// Clinical enclosure: one carved boundary, including the equipment banks and canopy.
function clinicalField(root,materials){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`
 precision highp float;uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float box(vec3 p,vec3 b,float r){vec3 q=abs(p)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
 float join(float a,float b,float k){float h=clamp(.5+.5*(b-a)/k,0.,1.);return mix(b,a,h)-k*h*(1.-h);}
 float ell(vec3 p,vec3 r){float a=length(p/r),b=length(p/(r*r));return a*(a-1.)/max(b,.00001);}
 float tissue(vec3 p){
  vec3 q=p*.95+.24*sin(p.zxy*.7+vec3(time*.27,-time*.22,time*.19));
  float f=0.,w=.55;
  for(int i=0;i<4;i++){
   float v=dot(sin(q),cos(q.yzx));f+=w*exp(-abs(v)*3.3);
   q=q.zxy*2.63+vec3(.7,1.4,2.1)+.22*sin(q.yzx);w*=.34;
  }return f;
 }
 vec2 field(vec3 p){
  vec3 q=p;q.x+=.10*sin(p.z*.41-time*.29)*smoothstep(2.,7.,abs(p.x));
  q.y+=.12*sin(p.z*.34+p.x*.28-time*.32)*smoothstep(1.,7.,p.y);
  float room=box(q-vec3(0.,5.,0.),vec3(8.5,3.5,12.5),1.5);
  float passage=box(q-vec3(0.,3.,-21.),vec3(1.6,2.3,9.),.7);
  float shell=-join(room,passage,1.);
  // A thick, porous vascular layer stands in front of a darker continuous backing.
  // Two intersecting fields make rounded branching fibres, not embossed contours.
  vec3 w=q*1.13+.48*sin(q.zxy*.43+vec3(time*.16,-time*.19,time*.13));
  w+=.16*sin(w.yzx*2.31+time*.12);
  float g1=dot(sin(w),cos(w.yzx));
  vec3 w2=w.zxy*1.19+vec3(1.7,.4,2.1);
  float g2=dot(sin(w2),cos(w2.yzx));
  float wallDepth=min(10.-abs(q.x),min(10.-q.y,14.+q.z));
  float reach=1.-smoothstep(.35,1.85,wallDepth);
  float fibres=(length(vec2(g1,g2))-.85*reach)*.24;
  fibres=max(fibres,wallDepth-1.85);
  fibres=max(fibres,abs(shell-.72)-1.02);
  fibres=max(fibres,1.05-q.y);
  shell-=tissue(q)*.035*smoothstep(.5,2.,q.y);
  float d=join(shell,fibres,.12),id=fibres<shell?4.:0.;
  // Unequal oval instrument cradles grow from a low continuous side bank.
  vec3 bank=vec3(abs(q.x)-8.45,q.y-1.15,q.z+3.);
  float cabinet=ell(bank,vec3(1.12,1.04,9.6)),sensors=100.;
  for(int j=0;j<3;j++){
   float k=float(j),zc=-9.2+k*6.7+.30*sin(k*2.4);
   float yc=2.25+.28*sin(k*2.1+sign(q.x)),wide=1.28+.18*cos(k*1.9);
   vec3 instrument=vec3(abs(q.x)-8.34,q.y-yc,q.z-zc);
   float cradle=ell(instrument,vec3(1.05,1.24,wide+.46));
   cabinet=join(cabinet,cradle,.42);
   float hollow=ell(instrument+vec3(.92,0.,0.),vec3(.94,.88,wide));
   cabinet=max(cabinet,-hollow);
   float sensor=ell(instrument+vec3(.24,0.,0.),vec3(.24,.58,wide*.62));
   sensors=min(sensors,sensor);
  }
  if(cabinet<d){d=join(d,cabinet,.36);id=1.;}
  if(sensors<d){d=sensors;id=3.;}
  // A lobed optical organ is embedded in the ceiling, without a freestanding ring.
  vec3 lens=q-vec3(0.,9.65,-4.5);float r=length(lens.xz*vec2(1.,1.22));
  float canopy=ell(lens,vec3(2.7,.64,2.15));
  canopy+=.065*sin(atan(lens.z,lens.x)*11.+r*7.-time*.35)*smoothstep(.4,2.,r);
  if(canopy<d){d=join(d,canopy,.35);id=2.;}
  return vec2(d,id);
 }
 vec3 normalAt(vec3 p){vec2 e=vec2(.009,0.);return normalize(vec3(field(p+e.xyy).x-field(p-e.xyy).x,field(p+e.yxy).x-field(p-e.yxy).x,field(p+e.yyx).x-field(p-e.yyx).x));}
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro),p=ro;float travel=0.;vec2 d=vec2(0.);bool hit=false;
  for(int i=0;i<180;i++){p=ro+rd*travel;d=field(p);if(d.x<.002+travel*.00014){hit=true;break;}travel+=max(d.x*.48,.003);if(travel>65.)break;}
  vec3 col=vec3(.025,.09,.105);
  if(hit){
   vec3 n=normalAt(p),v=-rd,l=normalize(vec3(-3.,8.,3.)-p),l2=normalize(vec3(3.,6.,-10.)-p);
   float h=tissue(p),ao=clamp(field(p+n*.30).x/.30,.25,1.);
   float floorMask=1.-smoothstep(.2,.8,p.y);
   vec3 film=.5+.5*cos(vec3(.2,2.3,4.4)+h*8.+dot(n,v)*3.+p.z*.13-time*.28);
   vec3 base=vec3(.018,.068,.085)+film*.028;
   base=mix(base,vec3(.023,.075,.087),floorMask);
   if(d.y>.5&&d.y<1.5)base=vec3(.045,.18,.17)+film*.07;
   if(d.y>3.5)base=mix(vec3(.015,.17,.19),vec3(.11,.46,.31),smoothstep(.10,.48,h))+film*.11;
   if(d.y>1.5&&d.y<3.5)base=vec3(.006,.035,.052)+film*.045;
   float diffuse=.19+.64*max(dot(n,l),0.)+.33*max(dot(n,l2),0.);
   col=base*diffuse*ao;
   float spec=pow(max(dot(n,normalize(l+v)),0.),48.);
   float spec2=pow(max(dot(n,normalize(l2+v)),0.),75.);
   col+=(vec3(.28,.76,.78)+film*.38)*(spec*.85+spec2*.55);
   col+=film*pow(1.-abs(dot(n,v)),3.)*mix(.035,.21,1.-floorMask);
   if(d.y>3.5){
    float flow=pow(.5+.5*sin(p.y*2.1+p.z*.85+h*18.-time*.65),7.);
    col+=mix(vec3(.012,.15,.22),vec3(.16,.85,.47),flow)*(.24+.5*ao);
   }
   if(d.y>1.5&&d.y<3.5){
    float optical=d.y<2.5?length((p.xz-vec2(0.,-4.5))*vec2(1.,1.22)):p.y*2.2+p.z*.23;
    float iris=pow(.5+.5*cos(optical*17.-time*.5),12.);
    col+=vec3(.045,.55,.66)*iris*.5+vec3(.01,.11,.14);
   }
   col=mix(col,vec3(.025,.085,.10),1.-exp(-travel*.009));
  }
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);gl_FragDepthEXT=hit?clamp(clip.z/clip.w*.5+.5,0.,1.):1.;
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const volume=new T.Mesh(new T.BoxGeometry(160,160,160),m);volume.position.set(0,5,-4);volume.frustumCulled=false;
 root.add(volume);materials.push(m);return volume;
}
function cabinet(root,materials,{x=0,z=-3,w=2,h=4,d=18}={}){
 const s=structures(root,materials,{palette:2}),V=(x,y,z)=>new T.Vector3(x,y,z);
 for(let k=0;k<=d*2;k++){
  const z0=-d/2+k*.5;
  for(const side of [-1,1]){let a=V(side*w/2,0,z0);
   for(let j=1;j<=6;j++){const b=V(side*(w/2-.16*Math.sin(j*Math.PI/3)),j*h/6,z0+(j%2)*.18);s.segment(a,b,.055);s.leaf(a,b,Math.min(1.15,3/h),side*Math.PI/2);a=b;}
   s.leaf(V(side*w/2,h,z0),V(0,h+.12,z0),.7,0);
  }
 }
 const g=s.finish();g.position.set(x,0,z);return g;
}
// Spatial samples of one contour at delayed phases, not retained image frames.
function timeLayers(root,materials,motions,{z=0,palette=2,loosening=false}={}){
 const group=new T.Group();root.add(group);
 for(let layer=0;layer<3;layer++){
  const s=structures(group,materials,{palette}),steps=quality==='high'?30:20;
  for(const side of [-1,1]){
   const point=u=>new T.Vector3(side*(3.7+.6*Math.sin(u*TAU*1.3)),.2+u*8,.4*Math.sin(u*TAU));
   for(let j=0;j<steps;j++){
    const u=j/steps,a=point(u),b=point((j+1)/steps);s.segment(a,b,.055);
    if(j%2===0){const tip=b.clone().add(new T.Vector3(side*(.5+.3*Math.sin(u*9)),.4,.24));s.segment(b,tip,.024);s.leaf(b,tip,.3,side*u*3);}
   }
  }
  const contour=s.finish();
  motions.push(t=>{const moment=t-layer*1.8,spread=loosening?1.15+.12*Math.sin(moment*.15):1;
   contour.position.set(Math.sin(moment*.32)*.22,Math.sin(moment*.27)*.16,z-layer*3.4);
   contour.rotation.set(Math.sin(moment*.19)*.065,Math.sin(moment*.23)*.12,Math.sin(moment*.31)*.055);
   contour.scale.set(spread*(1+.075*Math.sin(moment*.4)),1+.05*Math.sin(moment*.4+1),1);
  });
 }
 return group;
}
let quality=matchMedia('(pointer: coarse)').matches?'low':'high';
// Small separable bloom pass. No history buffer: pause/reduced-motion frames stay identical.
function compositor(renderer){
 const options={type:T.HalfFloatType,depthBuffer:true};
 const target=new T.WebGLRenderTarget(1,1,options),blurA=new T.WebGLRenderTarget(1,1,{...options,depthBuffer:false}),blurB=blurA.clone();
 const quadScene=new T.Scene(),cam=new T.OrthographicCamera(-1,1,1,-1,0,1),quad=new T.Mesh(new T.PlaneGeometry(2,2));quadScene.add(quad);
 const passVertex='varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}';
 const blur=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{tex:{value:null},stepSize:{value:new T.Vector2()},threshold:{value:0}},vertexShader:passVertex,fragmentShader:`
 varying vec2 vUv;uniform sampler2D tex;uniform vec2 stepSize;uniform float threshold;
 vec3 sampleLight(vec2 p){vec3 c=texture2D(tex,p).rgb;return max(c-vec3(threshold),vec3(0.));}
 void main(){vec3 c=sampleLight(vUv)*.227027;c+=(sampleLight(vUv+stepSize*1.384615)+sampleLight(vUv-stepSize*1.384615))*.316216;c+=(sampleLight(vUv+stepSize*3.230769)+sampleLight(vUv-stepSize*3.230769))*.070270;gl_FragColor=vec4(c,1.);}`});
 const finish=new T.ShaderMaterial({depthTest:false,depthWrite:false,uniforms:{tex:{value:target.texture},bloom:{value:blurB.texture},amount:{value:.2},time:{value:0},grain:{value:0},seam:{value:0},resolution:{value:new T.Vector2(1,1)}},vertexShader:passVertex,fragmentShader:`
 varying vec2 vUv;uniform sampler2D tex,bloom;uniform float amount,time,grain,seam;uniform vec2 resolution;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 void main(){vec2 p=vUv-.5;vec2 shift=p*dot(p,p)*amount*.002;
 float tick=floor(time*12.);vec2 cell=floor(vUv*resolution/1.6);
 float noise=hash(cell+vec2(tick,tick*.73));
 float boundary=exp(-abs(p.x+.026*sin(p.y*19.+time*.8))*(85.+noise*55.))*seam;
 vec2 uv=clamp(vUv+vec2((noise-.5)*boundary*.009,0.),vec2(0.),vec2(1.));
 vec3 col=texture2D(tex,uv).rgb;
 col.r=texture2D(tex,clamp(uv+shift,vec2(0.),vec2(1.))).r;col.b=texture2D(tex,clamp(uv-shift,vec2(0.),vec2(1.))).b;
 col+=texture2D(bloom,vUv).rgb*amount*.47;
 col*=1.-dot(p,p)*.24;
 // Fine low-luminance grain and a narrow seam, without full-field flashing.
 col*=1.-grain*.18;
 col+=mix(vec3(.03,.22,.2),vec3(.6,.35,.16),noise)*pow(noise,9.)*grain;
 col+=vec3(.24,.48,.44)*boundary*(.15+.85*noise);
 gl_FragColor=vec4(col,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
 }`});
 let calls=0,triangles=0;
 function resize(){const size=renderer.getDrawingBufferSize(new T.Vector2());target.setSize(size.x,size.y);blurA.setSize(Math.max(1,size.x>>2),Math.max(1,size.y>>2));blurB.setSize(blurA.width,blurA.height);finish.uniforms.resolution.value.copy(size);}
 function render(scene,camera,intensity,time=0,grain=0,seam=0){
  renderer.setRenderTarget(target);renderer.render(scene,camera);calls=renderer.info.render.calls;triangles=renderer.info.render.triangles;
  quad.material=blur;blur.uniforms.tex.value=target.texture;blur.uniforms.threshold.value=.48;blur.uniforms.stepSize.value.set(1/blurA.width,0);renderer.setRenderTarget(blurA);renderer.render(quadScene,cam);
  blur.uniforms.tex.value=blurA.texture;blur.uniforms.threshold.value=0;blur.uniforms.stepSize.value.set(0,1/blurA.height);renderer.setRenderTarget(blurB);renderer.render(quadScene,cam);
  quad.material=finish;finish.uniforms.amount.value=intensity;finish.uniforms.time.value=time;finish.uniforms.grain.value=grain;finish.uniforms.seam.value=seam;renderer.setRenderTarget(null);renderer.render(quadScene,cam);
 }
 resize();return {resize,render,get calls(){return calls;},get triangles(){return triangles;}};
}
// Contact's room is one carved volume: folds flow from the floor into living piers and vault.
function contactField(root,materials,download=false){
 const m=new T.ShaderMaterial({side:T.BackSide,extensions:{fragDepth:true},uniforms:{time:{value:0}},
 vertexShader:'varying vec3 fieldWorld;void main(){fieldWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(fieldWorld,1.);}',
 fragmentShader:`precision highp float;
 uniform float time;uniform mat4 projectionMatrix;varying vec3 fieldWorld;
 float join(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
 float ell(vec3 p,vec3 r){float k0=length(p/r),k1=length(p/(r*r));return k0*(k0-1.)/max(k1,.0001);}
 float box(vec3 p,vec3 b){vec3 q=abs(p)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.);}
 vec3 fold(vec3 p){
  vec3 q=p*.68;q.x=abs(q.x);q+=.45*sin(q.yzx*.67+vec3(time*.22,-time*.19,time*.16));
  float height=0.,inlay=0.,weight=.6;
  for(int i=0;i<4;i++){
   float net=dot(sin(q),cos(q.zxy));float ridge=exp(-net*net*3.8);
   height+=weight*ridge;inlay+=weight*exp(-net*net*24.);
   q=q.yzx*2.65+.34*sin(q.zxy)+vec3(.8,1.7,.4);weight*=.35;
  }
  return vec3(height,inlay,.5+.5*sin(q.x*.1+q.y*.13));
 }
 float room(vec3 p){
  vec3 q=p-vec3(0.,9.,-3.);float a=atan(q.y,q.x);
  float petal=.75*cos(a*12.+.24*sin(p.z*.29-time*.31))+.32*cos(a*24.-p.z*.3-time*.25);
  float shell=-ell(q,vec3(25.,20.,36.))-petal;
  float floor=p.y+.12;
  float d=join(shell,floor,1.6);
  // Thick fluted piers flare into the common vault and floor; no wire arcade remains.
  vec3 c=p;float lean=.9*sin(p.y*.16)+.25*sin(p.z*.19+time*.23);
  c.x=abs(c.x)-13.-lean;
  c.z=mod(c.z+25.,10.)-5.;
  float angle=atan(c.z,c.x);
  float flare=1.1+2.7*exp(-max(p.y,0.)*.9)+2.1*smoothstep(13.,24.,p.y);
  float pier=length(c.xz)-flare-.17*cos(angle*9.+p.y*.4-time*.22);
  d=join(d,pier,1.15);
  vec3 f=fold(p);
  // Carving remains shallow on the walkable floor, deep on the surrounding volume.
  float depth=mix(.17,1.15,smoothstep(.1,2.8,p.y));
  d-=depth*f.x;
  // Real open throats retain the existing onward and four side route planes.
  ${download?`// A round-topped passage recedes through the solid shell, with a carved inner lining.
  float throat=length(vec2(p.x,max(p.y-4.,0.)*.64))-4.5;
  throat+=.18*sin(p.z*1.15+time*.2)*(1.-smoothstep(-40.,-24.,p.z));
  float forward=max(max(throat,-p.y),abs(p.z+53.)-29.);`:
  `float forward=box(p-vec3(0.,5.,-34.),vec3(4.5,5.,10.));`}
  float side=min(box(vec3(abs(p.x)-25.,p.y-4.,p.z+6.),vec3(7.,4.,2.5)),box(vec3(abs(p.x)-25.,p.y-4.,p.z-9.),vec3(7.,4.,2.5)));
  d=max(d,-join(forward,side,.7));
  return d*.33;
 }
 vec3 normalAt(vec3 p,float e){vec2 k=vec2(e,0.);return normalize(vec3(room(p+k.xyy)-room(p-k.xyy),room(p+k.yxy)-room(p-k.yxy),room(p+k.yyx)-room(p-k.yyx)));}
 void main(){
  vec3 ro=cameraPosition,rd=normalize(fieldWorld-ro),p=ro;float travel=0.;bool hit=false;
  for(int i=0;i<256;i++){p=ro+rd*travel;float d=room(p);if(d<.003+travel*.0003){hit=true;break;}travel+=max(d,.002);if(travel>95.)break;}
  // The shallow floor has a solid backing beneath its carving, including at grazing angles.
  if(!hit&&rd.y<-.001){float ground=(-.12-ro.y)/rd.y;if(ground>0.&&ground<95.){travel=ground;p=ro+rd*travel;hit=true;}}
  vec3 col=vec3(.018,.038,.066);
  if(hit){
   vec3 n=normalAt(p,.006+travel*.00013),v=-rd,f=fold(p);
   float hue=.5+.5*sin(p.y*.26+p.z*.14+f.x*3.+time*.27);
   vec3 enamel=mix(vec3(.018,.3,.25),vec3(.3,.018,.15),hue);
   enamel=mix(enamel,vec3(.45,.19,.035),smoothstep(.2,.55,f.y)*.8);
   vec3 l1=normalize(vec3(-5.,12.,8.)-p),l2=normalize(vec3(7.,6.,-15.)-p);
   float shade=.32+.85*max(dot(n,l1),0.)+.65*max(dot(n,l2),0.);
   float occ=clamp(room(p+n*.38)/(.38*.33),.24,1.);
   vec3 film=.5+.5*cos(vec3(.3,2.3,4.3)+dot(n,v)*6.+p.y*.16+time*.24);
   float shine=pow(max(dot(n,normalize(l1+v)),0.),44.)+.55*pow(max(dot(n,normalize(l2+v)),0.),65.);
   float rim=pow(1.-max(dot(n,v),0.),3.);
   col=enamel*shade*occ+mix(vec3(.95,.75,.42),film,.4)*shine*.85;
   col+=film*rim*.18+vec3(.12,.48,.36)*pow(f.y,2.)*.28;
   col=mix(col,vec3(.032,.07,.09),1.-exp(-travel*.012));
  }
  vec4 clip=projectionMatrix*viewMatrix*vec4(p,1.);gl_FragDepthEXT=hit?clamp(clip.z/clip.w*.5+.5,0.,1.):1.;
  gl_FragColor=vec4(col,1.);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`});
 const volume=new T.Mesh(new T.BoxGeometry(190,190,190),m);volume.position.set(0,8,-3);volume.frustumCulled=false;
 root.add(volume);materials.push(m);return volume;
}
window.FractalWorld={surface,returnField,geometryField,rushField,membraneField,waitingField,cathedralField,contactField,clinicalField,vault,mandala,lattice,growth,gardenGround,gardenDetails,workshopShell,workshopDetails,arcade,panel,cabinet,language,timeLayers,veinMaterial,compositor,get quality(){return quality;},setQuality(value){quality=value;}};
})();
