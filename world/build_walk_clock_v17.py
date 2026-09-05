"""One-shot isolated movement-clock repair. Keep live and old evidence unchanged."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/'trip-v17-candidate.js'
assert not OUT.exists()
s=(HERE/'trip-v16.js').read_text()
assert s==(HERE/'trip.js').read_text()
def change(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)

change('const input=new Set()', 'let lastMovement=performance.now();\nconst input=new Set()')
change('function move(dt){', '''// Navigation measures actual held wall time, independent of capped animation
// deltas and GPU-delayed RAF timestamps. Flush the OLD input state at events,
// so neither a late release loses time nor a fresh press inherits an idle gap.
function syncMovement(){
 const now=performance.now(),dt=Math.max(0,(now-lastMovement)/1000);lastMovement=now;
 if(entered&&!paused&&!transition&&!$('evidence').open&&!document.hidden){
  move(dt);if(!camera.position.equals(drawnPosition))drawInvalidated=true;
 }
}
function move(dt){''')
change("function go(s){if(transition||!entered||paused||$('evidence').open)return;input.clear();", "function go(s){if(transition||!entered||paused||$('evidence').open)return;input.clear();lastMovement=performance.now();")
change('function begin(){entered=true;', 'function begin(){lastMovement=performance.now();entered=true;')
change('function restart(){transition=null;', 'function restart(){lastMovement=performance.now();transition=null;')
change('function togglePause(){if(!entered)return;paused=!paused;', 'function togglePause(){if(!entered)return;syncMovement();paused=!paused;')
change('function openEvidence(){input.clear();', 'function openEvidence(){syncMovement();input.clear();')
change("function closeEvidence(){$('evidence').close();", "function closeEvidence(){lastMovement=performance.now();$('evidence').close();")
change('e.preventDefault();if(!paused)input.add(keyMoves[key]);', 'e.preventDefault();syncMovement();if(!paused)input.add(keyMoves[key]);')
change("addEventListener('keyup',e=>{input.delete", "addEventListener('keyup',e=>{syncMovement();input.delete")
change("addEventListener('blur',()=>{input.clear();});", "addEventListener('blur',()=>{syncMovement();input.clear();});")
change('input.clear();lastFrame=performance.now();', 'input.clear();lastMovement=lastFrame=performance.now();')
change('||paused)return;yaw-=', '||paused)return;syncMovement();yaw-=')
change('if(paused)return;b.setPointerCapture', 'if(paused)return;syncMovement();b.setPointerCapture')
change('b.addEventListener(name,()=>input.delete(b.dataset.move));', 'b.addEventListener(name,()=>{syncMovement();input.delete(b.dataset.move);});')
change('lastFrame=now;\n const active=', 'lastFrame=now;\n syncMovement();\n const active=')
change('}else{elapsed+=dt;move(dt);if(paced', '}else{elapsed+=dt;if(paced')
OUT.write_text(s)
html=(HERE/'index.html').read_text().replace('src="trip.js"','src="trip-v17-candidate.js"')
(HERE/'walk-clock-v17-candidate.html').write_text(html)

# Original focused gate: same viewport, controls, assertions and 45000ms exit.
v=(HERE/'verify_continuum_v25.py').read_text()
v=v.replace('from verify import ARGS, open_page,', 'from verify import ARGS,')
at="HERE = Path(__file__).resolve().parent"
v=v.replace(at, at+'''
assert not (HERE/'verification-walk-clock-v17.json').exists(), 'Preserve evidence'
def open_page(browser, **options):
    page=browser.new_page(**options)
    page.set_default_timeout(20000)
    page.on('pageerror', lambda e: results['errors'].append(str(e)))
    page.on('console', lambda m: results['errors'].append(m.text) if m.type=='error' else None)
    page.route('https://**/*', lambda r:r.abort())
    page.route('http://**/*', lambda r:r.abort())
    page.goto((HERE/'walk-clock-v17-candidate.html').as_uri(),wait_until='load')
    page.wait_for_function('window.journeyDiagnostics && journeyDiagnostics().renderReady')
    return page
''')
v=v.replace('verification-continuum-v25.json','verification-walk-clock-v17.json')
v=v.replace('assert args.walk_timeout_ms > 0', 'assert args.walk_timeout_ms == 45000')
v=v.replace("'exit_walk_timeout_ms': args.walk_timeout_ms}", "'exit_walk_timeout_ms': args.walk_timeout_ms, 'candidate_sha256': __import__('hashlib').sha256((HERE/'trip-v17-candidate.js').read_bytes()).hexdigest()}")
v=v.replace("        hold_until(page, 'w', 'journeyDiagnostics().transition', timeout=args.walk_timeout_ms)", "        walk_start=__import__('time').monotonic()\n        hold_until(page, 'w', 'journeyDiagnostics().transition', timeout=args.walk_timeout_ms)\n        out['exit_wall_seconds']=__import__('time').monotonic()-walk_start")
(HERE/'verify_walk_clock_v17.py').write_text(v)
print('Built isolated movement-clock v17 and unchanged original focused gate; not live.')
