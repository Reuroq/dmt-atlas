"""One-shot submission-time PBO diagnostic. Never edits the live application."""
from pathlib import Path
import hashlib
import json
import ast

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-submission-v18'
HELPER = 'trace_submission_v18.py'
assert not list(HERE.glob(PREFIX + '*')) and not (HERE / HELPER).exists()
protected = ['trip.js', 'trip-v18.js', 'continuum.js', 'fractal.js',
             'visual-chrysanthemum.png', 'visual-chrysanthemum.json',
             'accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-before.png',
             'accessibility-input-pump-v18-restored-detail-reduced-pixel-stillness-after.png',
             'VISUAL_RESEARCH.json', 'fidelity-grades.json', 'realism-grades.json']
protected = [p for p in protected if (HERE / p).exists()]
hashes = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in protected}
s = (HERE / 'trip.js').read_text()
assert s == (HERE / 'trip-v18.js').read_text()

def change(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)

change('function frame(now){', '''// Isolated diagnostic: readPixels is queued before the application's fence.
const submissionRecords=[],submissionEvents=[];let pendingPixels=null;
function probeEvent(type,extra={}){if(submissionEvents.length<24000)submissionEvents.push({type,now:performance.now(),frames,animTime,renderedAnimTime,detail:F.quality,...extra});}
function queuePixels(){
 if(stage.id!=='chrysanthemum')return;
 const gl=renderGL,started=performance.now();
 if(!gl.getBufferSubData||pendingPixels)throw Error('PBO unsupported or already pending');
 const prior=gl.getParameter(gl.PIXEL_PACK_BUFFER_BINDING);
 const packing=[gl.PACK_ALIGNMENT,gl.PACK_ROW_LENGTH,gl.PACK_SKIP_PIXELS,gl.PACK_SKIP_ROWS].map(p=>gl.getParameter(p));
 if(packing[1]||packing[2]||packing[3]||gl.getParameter(gl.READ_FRAMEBUFFER_BINDING)!==null)throw Error('Unexpected readPixels state');
 const width=gl.drawingBufferWidth,height=gl.drawingBufferHeight,buffer=gl.createBuffer();
 const record={frame:frames,time:animTime,renderedTime:renderedAnimTime,stage:stage.id,detail:F.quality,width,height,position:camera.position.toArray(),yaw,pitch,queuedAt:started,packing,context:gl.getContextAttributes(),readBuffer:gl.getParameter(gl.READ_BUFFER)};
 try{gl.bindBuffer(gl.PIXEL_PACK_BUFFER,buffer);gl.bufferData(gl.PIXEL_PACK_BUFFER,width*height*4,gl.STREAM_READ);gl.readPixels(0,0,width,height,gl.RGBA,gl.UNSIGNED_BYTE,0);record.queueError=gl.getError();}
 finally{gl.bindBuffer(gl.PIXEL_PACK_BUFFER,prior);}
 record.queueBindingRestored=gl.getParameter(gl.PIXEL_PACK_BUFFER_BINDING)===prior;
 record.queueMs=performance.now()-started;
 pendingPixels={buffer,record};probeEvent('pixels-queued',{frame:record.frame});
}
function retirePixels(){
 if(!pendingPixels)return;
 const gl=renderGL,{buffer,record}=pendingPixels,started=performance.now(),prior=gl.getParameter(gl.PIXEL_PACK_BUFFER_BINDING);
 const bytes=new Uint8Array(record.width*record.height*4);
 try{gl.bindBuffer(gl.PIXEL_PACK_BUFFER,buffer);gl.getBufferSubData(gl.PIXEL_PACK_BUFFER,0,bytes);record.retrieveError=gl.getError();}
 finally{gl.bindBuffer(gl.PIXEL_PACK_BUFFER,prior);gl.deleteBuffer(buffer);}
 record.retrieveBindingRestored=gl.getParameter(gl.PIXEL_PACK_BUFFER_BINDING)===prior;
 record.retiredAt=performance.now();record.retrieveMs=record.retiredAt-started;
 let alphaMin=255,alphaMax=0,nonzeroRGB=0;
 for(let i=0;i<bytes.length;i+=4){alphaMin=Math.min(alphaMin,bytes[i+3]);alphaMax=Math.max(alphaMax,bytes[i+3]);if(bytes[i]||bytes[i+1]||bytes[i+2])nonzeroRGB++;}
 Object.assign(record,{alphaMin,alphaMax,nonzeroRGB});
 submissionRecords.push({record,bytes});pendingPixels=null;probeEvent('pixels-retired',{frame:record.frame});
}
window.submissionProbe={
 snapshot:()=>({now:performance.now(),diagnostics:window.journeyDiagnostics(),latest:submissionRecords.at(-1)?.record||null,pending:pendingPixels?.record.frame||null}),
 events:()=>submissionEvents,
 exportFrame:frame=>{const item=submissionRecords.find(v=>v.record.frame===frame);if(!item)throw Error('Missing submitted frame');let binary='';for(let i=0;i<item.bytes.length;i+=16384)binary+=String.fromCharCode(...item.bytes.subarray(i,i+16384));return {record:item.record,base64:btoa(binary)};}
};
function frame(now){
 probeEvent('raf',{raf:now});''')
change('if(gpuReady){renderGL.deleteSync', "if(gpuReady){probeEvent('fence-retired');retirePixels();renderGL.deleteSync")
change('  composite.render(scene,camera,', "  probeEvent('submit-before');composite.render(scene,camera,")
change('  if(renderGL.fenceSync){renderFence=', "  queuePixels();\n  if(renderGL.fenceSync){renderFence=")
js = s
html = (HERE / 'index.html').read_text()
assert html.count('src="trip.js"') == 1
html = html.replace('src="trip.js"', f'src="{PREFIX}.js"')
s = (HERE / 'render_visual.py').read_text()
change('import argparse', 'import argparse\nimport base64\nimport hashlib\nimport sys')
change('errors = []', '''errors = []
exported_frames = {}
probe_hashes = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['diagnostic-submission-v18.js','diagnostic-submission-v18.html','trace_submission_v18.py']}
def on_failure(kind, value, tb):
    (HERE/'submission-v18-failure.json').write_text(json.dumps({'exception':str(value),'browser_errors':errors,'probe_hashes':probe_hashes},indent=2)+'\\n')
    sys.__excepthook__(kind,value,tb)
sys.excepthook=on_failure''')
change("page.goto((HERE / 'index.html').as_uri())", f"page.goto((HERE / '{PREFIX}.html').as_uri())")
change("            before = page.evaluate('journeyDiagnostics()')", "            before = page.evaluate('journeyDiagnostics()')\n            probe_before = page.evaluate('submissionProbe.snapshot()')")
change("            settled = page.evaluate('journeyDiagnostics()')", "            settled = page.evaluate('journeyDiagnostics()')\n            probe_settled = page.evaluate('submissionProbe.snapshot()')")
change("            second_seconds = time.monotonic() - started\n            after = page.evaluate('journeyDiagnostics()')", '''            second_seconds = time.monotonic() - started
            after = page.evaluate('journeyDiagnostics()')
            probe_after = page.evaluate('submissionProbe.snapshot()')
            snapshots = [probe_before,probe_settled,probe_after]
            # Export immutable submitted bytes only AFTER both screenshots.
            for snapshot in snapshots:
                r=snapshot['latest']
                assert r and not snapshot['pending'] and r['frame']==snapshot['diagnostics']['frames'], 'PBO frame association'
                frame=r['frame']
                if frame not in exported_frames:
                    started_export=time.monotonic()
                    data=page.evaluate('(f)=>submissionProbe.exportFrame(f)',frame)
                    raw=base64.b64decode(data['base64'])
                    assert len(raw)==r['width']*r['height']*4
                    filename=f'diagnostic-submission-v18-frame-{frame}.rgba'
                    (HERE/filename).write_bytes(raw)
                    exported_frames[frame]={'record':data['record'],'sha256':hashlib.sha256(raw).hexdigest(),'file':filename,'export_seconds':time.monotonic()-started_export}
                snapshot['submitted_bytes']=exported_frames[frame]
            raw= (HERE/exported_frames[probe_before['latest']['frame']]['file']).read_bytes()
            r=probe_before['latest']
            raw_image=Image.frombytes('RGBA',(r['width'],r['height']),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            assert (r['width'],r['height'])==(args.width,args.height), 'HIGH 1:1 crop required'
            raw_crop=raw_image.crop((clip['x'],clip['y'],clip['x']+clip['width'],clip['y']+clip['height'])).convert('RGB')
            raw_comparisons=[]
            for shot in [a,b]:
                diff=ImageChops.difference(raw_crop,shot)
                raw_comparisons.append({'changed_pixels':sum(any(p) for p in diff.getdata()),'bbox':diff.getbbox(),'max_channel_delta':max(max(p) for p in diff.getdata())})''')
change("                    'label': label, 'before': before, 'settled': settled, 'after': after,", "                    'label': label, 'before': before, 'settled': settled, 'after': after,\n                    'submission_snapshots':snapshots,'raw_to_screenshots':raw_comparisons,\n                    'probe_hashes':probe_hashes,'browser_errors':list(errors),\n                    'screenshot_max_channel_delta':max(max(p) for p in difference.getdata()),\n                    'submission_events':page.evaluate('submissionProbe.events()'),")
change("            for d in [before, settled, after]:", "            for snapshot in snapshots:\n                r=snapshot['latest']\n                assert r['alphaMin']==255 and r['alphaMax']==255 and r['nonzeroRGB']>0, 'Invalid/transparent PBO readback'\n                assert r['queueError']==0 and r['retrieveError']==0 and r['queueBindingRestored'] and r['retrieveBindingRestored'], 'PBO state/error'\n                assert r['time']==snapshot['diagnostics']['renderedAnimTime'], 'PBO time association'\n            print(label+': '+str(raw_comparisons),flush=True)\n            for d in [before, settled, after]:")
change("        (HERE / 'latest.png').write_bytes(image_path.read_bytes())", "        # Isolated diagnostic; display updated only after review.")
change("                   'capture_sha256': digest(image_path), 'file': image_path.name,", "                   'probe_hashes':probe_hashes, 'submission_snapshot':page.evaluate('submissionProbe.snapshot()'),\n                   'capture_sha256': digest(image_path), 'file': image_path.name,")
change("    if args.capture_name:\n        path.write_bytes((HERE / f'{prefix}.png').read_bytes())\n        path.with_suffix('.json').write_bytes((HERE / f'{prefix}.json').read_bytes())", "    # Preserve default captures.")
ast.parse(s)
(HERE / (PREFIX + '.js')).write_text(js)
(HERE / (PREFIX + '.html')).write_text(html)
(HERE / HELPER).write_text(s)
(HERE / 'submission-v18-baseline.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Built isolated submission PBO probe; live files unchanged.')
