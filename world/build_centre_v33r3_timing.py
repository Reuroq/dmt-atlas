"""One-shot, insertion-only observation copies; never modify the live renderer."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'diagnostic-centre-v33r3-timing'
OUT = HERE / (PREFIX + '-build.json')
assert not OUT.exists(), 'Do not replay this builder'

def digest(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()

gate = json.loads((HERE / 'centre-v33r3-capture-integrity.json').read_text())
for group in ['files', 'protected', 'display']:
    for name, expected in gate[group].items():
        assert digest(name) == expected, name

insertions = []
def mark(code):
    n = len(insertions)
    insertions.append(n)
    return f'/*TIMING_INSERT_{n}_BEGIN*/' + code + f'/*TIMING_INSERT_{n}_END*/'

def after(source, anchor, code):
    assert source.count(anchor) == 1, anchor
    return source.replace(anchor, anchor + mark(code))

trip_original = (HERE / 'trip.js').read_bytes()
trip = trip_original.decode()
anchor = 'let elapsed=0, animTime=0, stageAnimStart=0, yaw=0, pitch=0, transition=null, renderReady=false, frames=0;'
trip = after(trip, anchor, r'''
// Perturbative observation only: no extra GL queries, readbacks or scheduling.
const timingCapacity=4096,timingRing=new Array(timingCapacity),timingCounts={},timingLast={};
let timingTotal=0,timingCursor=0,timingSubmit=0,timingOwner=null,timingWaitResult=null;
let timingWasInvalidated=drawInvalidated,timingSamplePoll=false,timingOpen={};
function timingState(){return {stage:stage.id,animTime,renderedAnimTime,frames,paused,
 transition:!!transition,invalidated:drawInvalidated,fence:!!renderFence,detail:F.quality,
 submission:timingSubmit,fenceOwner:timingOwner?{...timingOwner}:null};}
function timingRecord(event,data={},sampled=false){
 const ms=performance.now();timingCounts[event]=(timingCounts[event]||0)+1;
 if(sampled&&ms-(timingLast[event]??-Infinity)<1000)return;
 timingLast[event]=ms;
 const entry={sequence:++timingTotal,ms,event,...timingState(),...data};
 timingRing[timingCursor]=entry;timingCursor=(timingCursor+1)%timingCapacity;
 console.debug('DMT_TIMING '+JSON.stringify(entry));
}
function timingInvalidation(reason){
 const rising=!timingWasInvalidated;timingWasInvalidated=drawInvalidated;
 timingRecord('invalidate:'+reason,{rising},!rising);
}
function timingBegin(name,data={}){
 timingOpen[name]={ms:performance.now(),...timingState(),...data};
 timingRecord(name+':begin',data);
}
function timingEnd(name,data={}){
 const begin=timingOpen[name];
 timingRecord(name+':end',{durationMs:begin?performance.now()-begin.ms:null,...data});
 delete timingOpen[name];
}
function timingSnapshot(){
 const count=Math.min(timingTotal,timingCapacity),start=timingTotal>timingCapacity?timingCursor:0;
 return {schema:1,timeOrigin:performance.timeOrigin,exportMs:performance.now(),capacity:timingCapacity,
 totalRecorded:timingTotal,dropped:Math.max(0,timingTotal-timingCapacity),counts:{...timingCounts},
 state:timingState(),open:JSON.parse(JSON.stringify(timingOpen)),
 records:Array.from({length:count},(_,i)=>({...timingRing[(start+i)%timingCapacity]}))};
}
// Scoped bridge for observing the existing four compositor calls only.
const timingCompositeObserver=(name,begin)=>begin?timingBegin(name):timingEnd(name);
''')

# Comma additions stay inside original conditional assignment statements.
reasons = ['scene-build', 'movement', 'look', 'engagement', 'resize', 'frame-policy']
matches = list(re.finditer(r'drawInvalidated=true;', trip))
assert len(matches) == len(reasons)
for match, reason in reversed(list(zip(matches, reasons))):
    at = match.end() - 1
    trip = trip[:at] + mark(f",timingInvalidation('{reason}')") + trip[at:]

trip = after(trip, 'function frame(now){', "\n timingRecord('raf:start',{},true);")
trip = after(trip, ' let gpuReady=true;', "\n timingRecord('render-decision',{frozen,lastDrawFrozen},true);")
trip = after(trip, ' if(renderFence){', "\n  timingSamplePoll=performance.now()-(timingLast['fence-poll:begin']??-Infinity)>=1000; if(timingSamplePoll)timingBegin('fence-poll');")
needle = 'renderGL.clientWaitSync(renderFence,0,0)'
assert trip.count(needle) == 1
trip = trip.replace(needle, mark('(timingWaitResult=') + needle + mark(')'))
trip = after(trip, '!==renderGL.TIMEOUT_EXPIRED;', "\n  timingCounts['fence-result:'+timingWaitResult]=(timingCounts['fence-result:'+timingWaitResult]||0)+1; if(timingSamplePoll)timingEnd('fence-poll',{result:timingWaitResult,gpuReady});")
trip = after(trip, 'if(gpuReady){renderGL.deleteSync(renderFence);renderFence=null;', "timingRecord('fence-retired',{result:timingWaitResult,ageMs:timingOwner?performance.now()-timingOwner.createdMs:null});timingOwner=null;")
trip = after(trip, ' if(drawInvalidated&&gpuReady){', "\n  timingSubmit++;timingBegin('submission');")
trip = after(trip, 'grain+seam*.25,seam);', "timingEnd('submission');")
# Optional observer argument is confined to the isolated compositor copy.
needle = 'grain+seam*.25,seam'
assert trip.count(needle) == 1
trip = trip.replace(needle, needle + mark(',timingCompositeObserver'))
trip = after(trip, 'if(renderGL.fenceSync){', "timingBegin('fence-create');")
trip = after(trip, 'renderGL.fenceSync(renderGL.SYNC_GPU_COMMANDS_COMPLETE,0);', "timingOwner={submission:timingSubmit,stage:stage.id,animTime,createdMs:performance.now(),valid:!!renderFence};timingEnd('fence-create');timingBegin('flush');")
trip = after(trip, 'renderGL.flush();', "timingEnd('flush');")
trip = after(trip, '  drawInvalidated=false;', "timingWasInvalidated=false;timingRecord('invalidation-cleared');")
trip = after(trip, ' lastDrawFrozen=frozen;', "\n timingRecord('raf:end',{},true);")
trip = after(trip, 'window.journeyDiagnostics=(', 'timingExport=false')
needle = ')=>({stage:stage.id,routeIndex'
assert trip.count(needle) == 1
trip = trip.replace(needle, ')=>({' + mark('...(timingExport?{timing:timingSnapshot()}:{}),') + 'stage:stage.id,routeIndex')

fractal_original = (HERE / 'fractal.js').read_bytes()
fractal = fractal_original.decode()
needle = 'function render(scene,camera,intensity,time=0,grain=0,seam=0'
fractal = after(fractal, needle, ',timingObserver=null')
passes = ['scene', 'blur-horizontal', 'blur-vertical', 'finish']
lines = fractal.splitlines(keepends=True)
indices = [i for i, line in enumerate(lines) if 'renderer.render(' in line]
assert len(indices) == 4
for i, name in zip(indices, passes):
    line = lines[i]
    lines[i] = mark(f"if(timingObserver)timingObserver('composite:{name}',true);") + line.rstrip('\n') + mark(f"if(timingObserver)timingObserver('composite:{name}',false);") + '\n'
fractal = ''.join(lines)

copies = {'trip-v33r3-timing.js': (trip, trip_original),
          'fractal-v33r3-timing.js': (fractal, fractal_original)}
reversal = {}
for name, (source, original) in copies.items():
    path = HERE / name
    assert not path.exists()
    restored = re.sub(r'/\*TIMING_INSERT_(\d+)_BEGIN\*/.*?/\*TIMING_INSERT_\1_END\*/', '', source, flags=re.S).encode()
    assert restored == original, name
    path.write_bytes(source.encode())
    subprocess.run(['node', '--check', str(path)], check=True)
    reversal[name] = {'restored_sha256': hashlib.sha256(restored).hexdigest(), 'byte_exact': True}

html = (HERE / 'index.html').read_text()
for parent, candidate in [('trip.js', 'trip-v33r3-timing.js'), ('fractal.js', 'fractal-v33r3-timing.js'),
                          ('continuum.js', 'continuum-v33r3-candidate.js')]:
    assert html.count(f'src="{parent}"') == 1
    html = html.replace(f'src="{parent}"', f'src="{candidate}"')
html = html.replace('A reported-pattern interpretation', 'ISOLATED v33r3 timing · synthesised diagnostic')
html_name = PREFIX + '.html'
assert not (HERE / html_name).exists()
(HERE / html_name).write_text(html)
ast.parse(Path(__file__).read_text())
files = [*copies, html_name, 'continuum-v33r3-candidate.js', Path(__file__).name]
OUT.write_text(json.dumps({'diagnostic_only': True, 'insertion_only': True, 'reversal': reversal,
    'protected': gate['protected'], 'parent_gate': digest('centre-v33r3-capture-integrity.json'),
    'files': {n: digest(n) for n in files}, 'capacity': 4096,
    'limits': 'Timestamp/console observation is perturbative. No extra GPU queries, readbacks, waits, flushes, fences or frame scheduling. Original fence WAIT_FAILED semantics retained and raw result recorded.'}, indent=2) + '\n')
print('Timing build PASS: two reversible JS copies; candidate shader unchanged.')
