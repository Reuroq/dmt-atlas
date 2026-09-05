"""Isolated demand-driven navigation pump; preserve live and v17 evidence."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/'trip-v18-candidate.js'
assert not OUT.exists(), 'One shot'
s=(HERE/'trip-v17-candidate.js').read_text()
def change(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)
change('let lastMovement=performance.now();', 'let lastMovement=performance.now(),movementTimer=null;')
change('function syncMovement(){', '''// RAF can be withheld for seconds by a slow compositor even while native
// input and timer tasks run. Pump held navigation independently, without GL
// calls, so controls/observers see incremental motion during a pending frame.
// All callers share one monotonic clock: no duplicate or discarded held time.
// Demand-driven: one timer at most, and no repeating work once input stops.
function scheduleMovement(){
 if(movementTimer!==null||!input.size||!entered||paused||transition||$('evidence').open||document.hidden)return;
 movementTimer=setTimeout(()=>{movementTimer=null;syncMovement();scheduleMovement();},16);
}
function syncMovement(){''')
change('if(!paused)input.add(keyMoves[key]);', 'if(!paused){input.add(keyMoves[key]);scheduleMovement();}')
change('input.add(b.dataset.move);', 'input.add(b.dataset.move);scheduleMovement();')
OUT.write_text(s)
(HERE/'input-pump-v18-candidate.html').write_text((HERE/'index.html').read_text().replace('src="trip.js"','src="trip-v18-candidate.js"'))
v=(HERE/'verify_walk_clock_v17.py').read_text().replace('walk-clock-v17','input-pump-v18').replace('trip-v17-candidate.js','trip-v18-candidate.js')
v=v.replace("        assert -3.2 <= diag(page)['position'][0] <= 0", "        out['centre_return_x']=diag(page)['position'][0]\n        assert -3.2 <= out['centre_return_x'] <= 0")
v=v.replace('# Key release may arrive one capped movement frame after crossing centre.','# Preserve the original centre tolerance; navigation now has an independent pump.')
(HERE/'verify_input_pump_v18.py').write_text(v)
v=(HERE/'verify_idle_walk_v17.py').read_text().replace('walk-clock-v17-candidate.html','input-pump-v18-candidate.html').replace('idle-walk-v17','idle-pump-v18').replace('trip-v17-candidate.js','trip-v18-candidate.js')
(HERE/'verify_idle_pump_v18.py').write_text(v)
print('Built isolated v18 input pump and original focused gates; not promoted.')
