
'use strict';
// Translated shader queries deliberately absent; see staged-arithmetic-protocol.md.
let renderer, gl, target, texture, geometry, mesh, scene, camera, material, program, rendererExt;
const resources=[], callbacks=[], W=128;

const identities=new Map(), cleanupOrder=[];
function register(resource,kind) {
 if(identities.has(resource))throw Error('Duplicate resource identity');
 const entry={id:'resource-'+resources.length,kind,resource,attempted:false,succeeded:false,error:null};
 identities.set(resource,entry);resources.push(entry);return resource;
}
function resourceSnapshot() {
 return resources.map(({resource,...entry})=>({...entry}));
}
function cleanup() {
 for(const e of [...resources.filter(e=>e.kind!=='renderer'),...resources.filter(e=>e.kind==='renderer')]) {
  if(e.attempted)continue;
  e.attempted=true;cleanupOrder.push(e.id);
  try {e.resource.dispose();e.succeeded=true;}catch(error){e.error=String(error.stack||error);}
 }
 const registered=resourceSnapshot();
 return {registered,attempted:cleanupOrder.slice(),succeeded:registered.filter(e=>e.succeeded).map(e=>e.id),
  errors:registered.filter(e=>e.error!==null).map(e=>({id:e.id,error:e.error})),
  rendererDisposed:registered.some(e=>e.kind==='renderer'&&e.succeeded),
  complete:registered.every(e=>e.attempted&&e.succeeded&&e.error===null)};
}
function cleanupDrain() {
 try{return drainErrors();}catch(error){return {errors:[],drained:false,exception:String(error.stack||error)};}
}

const vertexShader='varying vec2 sampleUV; void main(){sampleUV=uv;gl_Position=vec4(position.xy,0.,1.);}';
window.shaderSource=(leaf,arm)=>{
 const c1=leaf===0?'-.62':'-.90', c2=leaf===0?'.20':'.28';
 const second=arm==='literal'?c2:'secondOffset';
 return `precision highp float;
uniform sampler2D inputTex; uniform float textureRow; uniform float secondOffset;
varying vec2 sampleUV;
vec4 offset(vec4 a,float b){return vec4(a.xyz,a.w+b);}
void main(){
 float x=texture2D(inputTex,vec2(sampleUV.x,(textureRow+.5)/2.)).r;
 vec4 predecessor=vec4(0.,0.,0.,x);
 vec4 parent=offset(predecessor,${c1});
 vec4 child=offset(parent,${second});
 float folded=x+(${c1}+${c2});
 gl_FragColor=vec4(x,parent.w,child.w,folded);
}`;
};
function drainErrors() {
 const errors=[];
 if(!gl)return {errors,drained:true};
 for(let i=0;i<32;i++) {const code=gl.getError();if(code===gl.NO_ERROR)return {errors,drained:true};errors.push(code);}
 return {errors,drained:false};
}
function pack(pixels) {
 return {values:Array.from(pixels,x=>Number.isFinite(x)?x:String(x)),
  bits:pixels instanceof Float32Array?Array.from(new Uint32Array(pixels.buffer)):Array.from(pixels)};
}

function makePlan() {
 const p=['renderer','metadata','renderer-extension','unmasked-renderer','float-extension','shared'].map(op=>({op}));
 const cases=[{name:'float-control'},...['childAxial','childAngular'].flatMap((name,leaf)=>['literal','uniform'].map(arm=>({name,leaf,arm})))];
 for(const identity of cases) {
  for(const op of ['material','bind','framebuffer-status','framebuffer-binding','attachment-type',
   'implementation-format','implementation-type','compile','program-reference','program-link','program-log',
   'render','framebuffer-status','framebuffer-binding','read-three','read-raw'])p.push({...identity,op});
  for(const shader of ['vertexShader','fragmentShader'])
   for(const op of ['shader-is','shader-compiled','shader-log','shader-source'])p.push({...identity,op,shader});
 }
 return p;
}
function perform(s) {
 const shader=()=>program[s.shader];
 switch(s.op) {
 case 'renderer':
  renderer=register(new THREE.WebGLRenderer({antialias:false}),'renderer');gl=renderer.getContext();renderer.setSize(W,1);
  renderer.debug.checkShaderErrors=true;
  renderer.debug.onShaderError=()=>callbacks.push({event:'shader-error-callback',queryPerformed:false});
  return {three:THREE.REVISION,webgl2:renderer.capabilities.isWebGL2,precision:renderer.capabilities.precision};
 case 'metadata': {const h=gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER,gl.HIGH_FLOAT);
  return {version:gl.getParameter(gl.VERSION),shadingLanguage:gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
   vendor:gl.getParameter(gl.VENDOR),renderer:gl.getParameter(gl.RENDERER),highFloat:{precision:h.precision,rangeMin:h.rangeMin,rangeMax:h.rangeMax}};}
 case 'renderer-extension': rendererExt=gl.getExtension('WEBGL_debug_renderer_info');return {supported:!!rendererExt};
 case 'unmasked-renderer': return rendererExt?{renderer:gl.getParameter(rendererExt.UNMASKED_RENDERER_WEBGL)}:{skipped:true};
 case 'float-extension': return {supported:!!gl.getExtension('EXT_color_buffer_float')};
 case 'shared': {
  if(!Array.isArray(s.dataBits)||s.dataBits.length!==1024||!s.dataBits.every(b=>Number.isInteger(b)&&b>=0&&b<=0xffffffff))throw Error('Invalid uint32 input');
  const words=new Uint32Array(s.dataBits),data=new Float32Array(words.buffer);
  if(data.length!==1024)throw Error('Wrong frozen input texture length');
  target=register(new THREE.WebGLRenderTarget(W,1,{type:THREE.FloatType,minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,depthBuffer:false}),'target');
  texture=register(new THREE.DataTexture(data,W,2,THREE.RGBAFormat,THREE.FloatType),'texture');
  texture.minFilter=texture.magFilter=THREE.NearestFilter;texture.needsUpdate=true;
  geometry=register(new THREE.PlaneGeometry(2,2),'geometry');scene=new THREE.Scene();camera=new THREE.Camera();
  mesh=new THREE.Mesh(geometry,null);mesh.frustumCulled=false;scene.add(mesh);
  return {width:W,height:1,textureHeight:2,input:pack(data),targetType:target.texture.type};}
 case 'material': {
  const control=s.name==='float-control', second=s.leaf===0?Math.fround(.20):Math.fround(.28);
  const fragmentShader=control?'precision highp float; void main(){gl_FragColor=vec4(.125,-.5,2.,1.);}':window.shaderSource(s.leaf,s.arm);
  const uniforms={inputTex:{value:texture},textureRow:{value:control?0:s.leaf},secondOffset:{value:second}};
  material=register(new THREE.ShaderMaterial({vertexShader,fragmentShader,uniforms,depthTest:false,depthWrite:false,blending:THREE.NoBlending}),'material');
  mesh.material=material;
  return {vertexShader,fragmentShader,uniforms:{inputTex:'shared frozen 128x2 RGBA32F',textureRow:uniforms.textureRow.value,
   secondOffset:second,secondOffsetBits:pack(new Float32Array([second])).bits[0]},control};}
 case 'bind': renderer.setRenderTarget(target);return {width:target.width,height:target.height,type:target.texture.type};
 case 'framebuffer-status': return {status:gl.checkFramebufferStatus(gl.FRAMEBUFFER),completeEnum:gl.FRAMEBUFFER_COMPLETE};
 case 'framebuffer-binding': return {bound:gl.getParameter(gl.FRAMEBUFFER_BINDING)!==null};
 case 'attachment-type': return {type:gl.getFramebufferAttachmentParameter(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE)};
 case 'implementation-format': return {format:gl.getParameter(gl.IMPLEMENTATION_COLOR_READ_FORMAT)};
 case 'implementation-type': return {type:gl.getParameter(gl.IMPLEMENTATION_COLOR_READ_TYPE)};
 case 'compile': renderer.compile(scene,camera);return {callbacks:callbacks.slice()};
 case 'render': renderer.render(scene,camera);return {callbacks:callbacks.slice()};
 case 'read-three': case 'read-raw': {
  const pixels=new Float32Array(W*4);pixels.fill(-123.75);
  if(s.op==='read-three')renderer.readRenderTargetPixels(target,0,0,W,1,pixels);
  else gl.readPixels(0,0,W,1,gl.RGBA,gl.FLOAT,pixels);
  return {...pack(pixels),sentinel:-123.75,method:s.op};}
 case 'program-reference': program=renderer.properties.get(material).currentProgram;
  return {present:!!program,vertexPresent:!!program?.vertexShader,fragmentPresent:!!program?.fragmentShader};
 case 'program-link': return {linked:gl.getProgramParameter(program.program,gl.LINK_STATUS)};
 case 'program-log': return {log:gl.getProgramInfoLog(program.program)};
 case 'shader-is': return {isShader:gl.isShader(shader())};
 case 'shader-compiled': return {compiled:gl.getShaderParameter(shader(),gl.COMPILE_STATUS)};
 case 'shader-log': return {log:gl.getShaderInfoLog(shader())};
 case 'shader-source': return {source:gl.getShaderSource(shader())};
 case 'dispose': return cleanup();
 default: throw Error('Unknown operation '+s.op);
 }
}
window.arithmeticPlan=makePlan;
window.arithmeticStep=s=>{
 const disposing=s.op==='dispose',before=disposing?cleanupDrain():drainErrors();
 const r={step:s,before,after:null,value:null,exception:null,skipped:false};
 if(!disposing&&(!before.drained||before.errors.length)){r.skipped=true;r.reason='dirty pre-operation error queue';r.resources=resourceSnapshot();return r;}
 try {r.value=perform(s);}catch(e){r.exception=String(e.stack||e);}
 finally {
  r.resources=resourceSnapshot();r.after=disposing?cleanupDrain():drainErrors();
  try{r.contextLost=gl?gl.isContextLost():false;}catch(error){r.contextLost=true;r.contextException=String(error.stack||error);}
 }
 return r;
};

