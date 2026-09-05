"""One-shot isolated readback/presentation instrumentation; no runtime repair."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREFIX='diagnostic-presentation-v18r2'
assert not list(HERE.glob(PREFIX+'*')) and not (HERE/'trace_presentation_v18r2.py').exists()
s=(HERE/'trip.js').read_text()
assert s==(HERE/'trip-v18.js').read_text()
def change(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
change('function frame(now){', '''const presentationTrace=window.presentationTrace=[];
function tracePresentation(type,extra={}){if(presentationTrace.length<24000)presentationTrace.push({type,now:performance.now(),frames,animTime,renderedAnimTime,invalidated:drawInvalidated,fence:!!renderFence,detail:F.quality,...extra});}
function frame(now){
 tracePresentation('raf',{raf:now});''')
change('if(gpuReady){renderGL.deleteSync', "if(gpuReady){tracePresentation('fence-retired');renderGL.deleteSync")
change('  composite.render(scene,camera,', "  tracePresentation('submit-before');composite.render(scene,camera,")
change('renderReady=true;frames++;', "renderReady=true;frames++;tracePresentation('submit-after');")
(HERE/(PREFIX+'.js')).write_text(s)
(HERE/(PREFIX+'.html')).write_text((HERE/'index.html').read_text().replace('src="trip.js"',f'src="{PREFIX}.js"'))
s=(HERE/'render_visual.py').read_text()
change('import argparse', 'import argparse\nimport base64\nimport hashlib')
change("page.goto((HERE / 'index.html').as_uri())",f"page.goto((HERE / '{PREFIX}.html').as_uri())")
change("            settled = page.evaluate('journeyDiagnostics()')", '''            # Read-only copy of the browser canvas AFTER the first screenshot.
            # This is a Canvas2D copy, not a guaranteed raw framebuffer readback;
            # default preserveDrawingBuffer=false and colour conversion matter.
            def canvas_copy():
                started_copy=time.monotonic()
                data=page.evaluate('''+repr('''clip => {const src=document.querySelector('#world'),copy=document.createElement('canvas');copy.width=clip.width;copy.height=clip.height;const ctx=copy.getContext('2d');const sx=src.width/innerWidth,sy=src.height/innerHeight;ctx.drawImage(src,clip.x*sx,clip.y*sy,clip.width*sx,clip.height*sy,0,0,clip.width,clip.height);return {png:copy.toDataURL('image/png').split(',')[1],now:performance.now(),d:journeyDiagnostics(),buffer:[src.width,src.height]};}''')+''',clip)
                data['seconds']=time.monotonic()-started_copy
                pixels=Image.open(BytesIO(base64.b64decode(data.pop('png')))).convert('RGBA')
                data['rgba_sha256']=hashlib.sha256(pixels.tobytes()).hexdigest()
                data['alpha_extrema']=pixels.getchannel('A').getextrema()
                return pixels,data
            raw_a,readback_a=canvas_copy()
            settled = page.evaluate('journeyDiagnostics()')''')
change("            second_seconds = time.monotonic() - started\n            after = page.evaluate('journeyDiagnostics()')", "            second_seconds = time.monotonic() - started\n            raw_b,readback_b=canvas_copy()\n            after = page.evaluate('journeyDiagnostics()')")
change("                    'label': label, 'before': before, 'settled': settled, 'after': after,", "                    'label': label, 'before': before, 'settled': settled, 'after': after,\n                    'canvas_copies':[readback_a,readback_b],\n                    'canvas_changed_pixels':sum(any(p) for p in ImageChops.difference(raw_a,raw_b).getdata()),\n                    'canvas_difference_bbox':ImageChops.difference(raw_a,raw_b).getbbox(),\n                    'screenshot_max_channel_delta':max(max(p) for p in difference.getdata()),\n                    'presentation_trace':page.evaluate('presentationTrace'),\n                    'browser_errors':list(errors),")
change("                    b.save(HERE / (stem + '-after.png'))", "                    b.save(HERE / (stem + '-after.png'))\n                    raw_a.save(HERE / (stem + '-canvas-before.png'))\n                    raw_b.save(HERE / (stem + '-canvas-after.png'))")
change("        (HERE / 'latest.png').write_bytes(image_path.read_bytes())", "        # Isolated diagnostic: do not overwrite the default display.")
change("    if args.capture_name:\n        path.write_bytes((HERE / f'{prefix}.png').read_bytes())\n        path.with_suffix('.json').write_bytes((HERE / f'{prefix}.json').read_bytes())", "    # Isolated diagnostic: leave full-size default captures unchanged.")
(HERE/'trace_presentation_v18r2.py').write_text(s)
print('Built isolated RAF/fence trace and Canvas2D-copy diagnostic. No scene/time/input changes.')
