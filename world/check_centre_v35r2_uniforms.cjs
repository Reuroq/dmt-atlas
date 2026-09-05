// Execute real candidate constructors and fixture JS under offline Three stubs.
// This checks binding/transform wiring, not GLSL execution or GPU arithmetic.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const [candidate,fixture]=process.argv.slice(2);
function bits(x){return new Uint32Array(new Float32Array([x]).buffer)[0];}
function validate(material){
 const u=material.uniforms,s=material.fragmentShader;
 assert.strictEqual(u.childAxialOffset.value,Math.fround(.20));
 assert.strictEqual(u.childAngularOffset.value,Math.fround(.28));
 assert.strictEqual(bits(u.childAxialOffset.value),0x3e4ccccd);
 assert.strictEqual(bits(u.childAngularOffset.value),0x3e8f5c29);
 assert.strictEqual((s.match(/uniform float childAxialOffset,childAngularOffset;/g)||[]).length,1);
 assert.strictEqual((s.match(/\bchildAxialOffset\b/g)||[]).length,2);
 assert.strictEqual((s.match(/\bchildAngularOffset\b/g)||[]).length,2);
 assert(s.includes('axB=offset(axA,childAxialOffset);'));
 assert(s.includes('angB=offset(angA,childAngularOffset);'));
 assert(!s.includes('axB=offset(axA,.20);')&&!s.includes('angB=offset(angA,.28);'));
}
let draws=0,reads=0,ticks=0;
class Matrix4 {constructor(){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];}copy(){return this;}multiplyMatrices(){return this;}}
class Camera {constructor(){this.position={set(){}};for(const k of ['matrixWorld','matrixWorldInverse','projectionMatrix','projectionMatrixInverse'])this[k]=new Matrix4();}updateMatrixWorld(){}}
class Renderer {constructor(){this.debug={};}setSize(){}setRenderTarget(){}render(scene){validate(scene.children[0].material);draws++;}readRenderTargetPixels(){reads++;}getDrawingBufferSize(v){v.y=800;return v;}}
class Scene {constructor(){this.children=[];}add(mesh){this.children.push(mesh);}}
const THREE={Matrix4,PerspectiveCamera:Camera,Scene,WebGLRenderer:Renderer,
 ShaderMaterial:class{constructor(options){Object.assign(this,options);}},
 Mesh:class{constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};}},
 PlaneGeometry:class{},Vector2:class{},WebGLRenderTarget:class{setSize(){}},
 DataTexture:class{dispose(){}},FloatType:1015,RGBAFormat:1023,NearestFilter:1003};
const context={THREE,assert,validate,Math,Float32Array,Uint32Array,FractalWorld:{quality:'high'},performance:{now:()=>++ticks}};
context.window=context;vm.createContext(context);
vm.runInContext(fs.readFileSync(candidate,'utf8'),context);
if(fixture){
 const html=fs.readFileSync(fixture,'utf8'),inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
 assert.strictEqual(inline.length,1);vm.runInContext(inline[0][1],context);
 vm.runInContext(`
  let reachedRead=false,failed=false;
  try {renderer.debug.onShaderError({getProgramInfoLog:()=>"bad link",getShaderInfoLog:()=>"bad shader"},0,1,2);reachedRead=true;}
  catch(e){failed=e.message.startsWith('GLSL_COMPILE_OR_LINK_FAILED:');}
  assert(failed&&!reachedRead);
  for(const high of [1,0]){
   if(window.auditLeaves)window.auditLeaves({width:2,height:1,z:8,time:4.895,high,points:[0,1.7,8,0,1,1.7,8,0]});
   else window.runCase(8,4.895,high,2,1);
   validate(material);
  }
 `,context);
 assert.strictEqual(draws,fixture.endsWith('leaves.html')?44:8);
 assert.strictEqual(reads,draws);
}else{
 vm.runInContext(`
 const scene=new THREE.Scene(),materials=[],camera=new THREE.PerspectiveCamera();
 const mesh=ContinuousWorld.chrysanthemum(scene,materials,camera),material=materials[0];
 for(const quality of ['high','low']){
  FractalWorld.quality=quality;mesh.onBeforeRender(new THREE.WebGLRenderer());
  assert.strictEqual(material.uniforms.high.value,quality==='high'?1:0);validate(material);
 }
 `,context);
}
// Reject realistic wiring regressions against the actual resulting material.
vm.runInContext(`
 validate(material);
 const savedShader=material.fragmentShader;
 const savedAxial=material.uniforms.childAxialOffset.value;
 const savedAngular=material.uniforms.childAngularOffset.value;
 material.uniforms.childAxialOffset.value=.20;assert.throws(()=>validate(material));
 material.uniforms.childAxialOffset.value=savedAxial;
 material.uniforms.childAngularOffset.value=0;assert.throws(()=>validate(material));
 material.uniforms.childAngularOffset.value=savedAngular;
 delete material.uniforms.childAngularOffset;assert.throws(()=>validate(material));
 material.uniforms.childAngularOffset={value:savedAngular};
 for(const [before,after] of [
  ['uniform float childAxialOffset,childAngularOffset;',''],
  ['axB=offset(axA,childAxialOffset);','axB=offset(axA,.20);'],
  ['angB=offset(angA,childAngularOffset);','angB=offset(angA,.28);']]){
  material.fragmentShader=savedShader.replace(before,after);assert.throws(()=>validate(material));
 }
 material.fragmentShader=savedShader;validate(material);
 window.snapshot={fragmentShader:material.fragmentShader,vertexShader:material.vertexShader,
  uniforms:Object.keys(material.uniforms).sort(),offsetWords:[0x3e4ccccd,0x3e8f5c29],
  highLowChecked:true,negativeChecks:6,actualGLSL:false};
`,context);
process.stdout.write(JSON.stringify({...context.snapshot,draws,reads}));
