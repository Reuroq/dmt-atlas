"""Close fixtures without replaying checks; wrapper binds closure log/exit."""
import ast
import hashlib
import json
from pathlib import Path
from cost_lifecycle_v34 import atomic_json

HERE=Path(__file__).resolve().parent
DRAFT=HERE/'centre-v34-fixture-closure-draft.json'
START=HERE/'centre-v34-fixture-closure-started.json'


def digest(name):
    return hashlib.sha256((HERE/name).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE/name).read_text())


def verify(group):
    for name,want in group.items():
        assert digest(name)==want,name


def main():
    assert not any(p.exists() for p in [DRAFT,START,HERE/'centre-v34-fixture-integrity.json'])
    prior=read('centre-v34-offline-fixtures.json')
    for group in ['files','protected','display']:verify(prior[group])
    check=read('centre-v34-fixture-check.json')
    assert check['static_passed'] and check['browser_runs']==check['actual_glsl_runs']==check['v34_field_samples']==0
    amendment=read('centre-v34-launcher-exit-check.json')
    assert amendment['passed'];verify(amendment['source_hashes'])
    build=read('centre-v34-fixture-build.json');verify(build['files'])
    exits={'prepare-centre-v34-fixtures-once-exit.json':0,
           'check-centre-v34-fixtures-once-exit.json':1,
           'check-centre-v34-fixtures-r2-once-exit.json':0,
           'check-centre-v34-exit-gate-once-exit.json':0}
    logs=[]
    for name,want in exits.items():
        receipt=read(name);assert receipt['actual_exit']==want,name
        assert (HERE/receipt['log']).exists();logs.append(receipt['log'])
    for name in ['centre-v34-bounds-started.json','centre-v34-bounds-check.json','centre-v34-bounds-failure.json',
                 'centre-v34-gpu-started.json','centre-v34-gpu-failure.json','numeric-candidate-v34-raw.json',
                 'centre-v34-first-root-started.json','centre-v34-first-root-check.json',
                 'centre-v34-cost-raw.json','centre-v34-cost-review.json','centre-v34-integrity.json']:
        assert not (HERE/name).exists(),name
    assert not list(HERE.glob('diagnostic-centre-v34*'))
    assert not list(HERE.glob('run-centre-v34-*-once-launch.json'))
    assert (HERE/'status.txt').read_text().startswith('Isolated v34 offline fixtures prepared:')
    for name in [Path(__file__).name,'close_centre_v34_fixtures_once.py']:
        ast.parse((HERE/name).read_text(),filename=name)
    original=(HERE/'NOTES.md').read_bytes();assert original.startswith(b'\xef\xbb\xbf')
    archive=HERE/'NOTES-before-centre-v34-fixtures.md';assert not archive.exists()
    notes=original.decode('utf-8-sig')
    notes=notes.replace(notes.splitlines()[0], '# Active: REDIRECT4 — v34 fixtures COMPLETE; numerical gates next; no runtime',1)
    position=notes.index('## Exact next bounded work')
    notes=notes[:position]+'''## v34 full fixture phase CLOSED — static PASS; zero numerical field runs
- Prepared new five-base/11expanded smooth-jet GPU audit,48cases/75996rays/720fixed+720interval first roots using csg_interval_v34.enclosure. Exact nested tie/sign/aperture/composite/normal replay; selected one-sided gradients recorded at creases,not unique normals. Original miss/error/unresolved/depth gates retained;non-envelope Taylor domain checked.
- NEW v34 unshared reference changes only full-trace fieldPartsReachShared→fieldPartsReach recomputation;exact single-edit construction and identical instrumentation verified.12balanced pairs retain hit/count,lower-prefix-work,total/median<=1 gates,both clocks,no warmup;add exact points/gradients and24complete-arm/clean-lifecycle requirements. Not v34-v33r6 speedup. Existing lifecycle evidence inherited via exact version-only equivalence,not rerun.
- prepare_centre_v34_fixtures.py ONCE exit0. Initial offline verifier ONCE exit1:global call-count assertion also counted unchanged wrapper,not a fixture/runtime failure. Preserved original checker/log/exit. Revised verifier ONCE exit0:AST/JS/string-transform/fake-link checks and1012synthetic CSG cases PASS;zero v34 samples/browser/GLSL. Generated fixtures unchanged after builder.
- New one-shot runtime/foreground launcher failure/replay contracts PASS. Launcher-only amendment requires prior actual exit0/log+launch hashes;four new synthetic amendment checks PASS,unchanged full checker not replayed. Unique foreground launch/log/actual-exit receipts;durable GPU cases and cost arms. Hardkill/storage loss can still leave cause-unknown partial attempts;never replay.
- centre-v34-fixture-integrity.json binds full fixtures/static checks/build/check logs+actual exits and prior180 evidence/16protected/4display snapshots. Authorizes numerical gates ONLY,not capture. Bounds/GPU/roots/cost NOT RUN;candidate/oracle/original renderer unchanged. README/status current;latest still inspected REJECTED GAME v33r6 entry. NOTES once,BOM preserved,prior notes archived verbatim.

## Exact next bounded work
Use foreground python3 world/run_centre_v34_gate_once.py bounds,then ONLY exit0/PASS gpu,then roots,then cost;each ONCE. Launcher supplies dependencies and saves unique run-centre-v34-{bounds,gpu,roots,cost}-once.log/-once-exit.json/-once-launch.json. Wait for completion,keep updates,no background/replay/prewarm/relaxed limits. Check full fixture manifest before execution. Bounds72000+12000 plus cap/filter/attachment;GPU48/75996/720fixed;interval720;cost12balanced same-v34 shared/unshared. Preserve failed/partial evidence and stop dependent gates. Only allPASS with verified actual exits permits NEW centre-v34-integrity.json,then unchanged render_centre_v34.py1200x800HIGH/90s ONCE. No numerical closure script prepared yet. No promotion/frame-pump change.

All19 realism,remaining16source gates,coverage,route/full acceptance remain unfinished.
'''
    readme_path=HERE/'README.md';readme=readme_path.read_text()
    old='Next: prepare GPU/first-root and matched-cost fixtures before one-shot numerical gates.'
    assert readme.count(old)==1
    readme=readme.replace(old,
        'Full GPU/720fixed+720interval/12balanced matched-cost fixtures are complete; '
        'offline JS/AST/CSG and failure-receipt contracts PASS, zero v34 field/browser runs. '
        'Initial verifier call-count failure and corrected check both preserved. '
        'See [complete fixture scope and commands](centre-v34-fixtures-review.md). '
        'Next: bounds → GPU → independent roots → same-v34 shared/unshared cost, each once '
        'after prior PASS/actual exit0. Not v34-v33r6 speedup evidence; capture remains blocked.')
    atomic_json(START,{'started':True,'prior_manifest':digest('centre-v34-offline-fixtures.json')})
    with archive.open('xb') as stream:stream.write(original)
    readme_path.write_text(readme)
    (HERE/'status.txt').write_text(
        'Isolated v34 fixtures COMPLETE/static PASS:5base/11signed smooth jets,48cases/75996rays,'
        '720fixed+720interval roots,12balanced identical-v34 shared/unshared cost. Offline checker '
        'call-count failure preserved;revised checks and durable-exit contracts PASS. '
        'Zero v34 field samples/browser/GLSL/numerical/cost/capture. Next bounds→GPU→roots→cost '
        'ONCE via foreground launcher,only after prior PASS/actual exit0. Capture still blocked. '
        'latest.png remains inspected REJECTED GAME v33r6 entry,not v34. Live/defaults/ledgers '
        'unchanged;all19/source/coverage/route/full unfinished;no promotion/replay/prewarm/relaxed limits.\n')
    (HERE/'NOTES.md').write_bytes(b'\xef\xbb\xbf'+notes.encode())
    for group in ['files','protected']:verify(prior[group])
    assert digest('latest.png')==prior['display']['latest.png']
    names=list(build['files'])+[
        'centre-v34-fixture-build.json','centre-v34-offline-fixtures.json',
        'close-centre-v34-offline-fixtures-once.log','close-centre-v34-offline-fixtures-once-exit.json',
        'gpu_csg_v34.py','runtime_centre_v34.py','run_centre_v34_gate_once.py',
        'prepare_centre_v34_fixtures.py','check_centre_v34_fixtures.py','check_centre_v34_fixtures_r2.py',
        'check_centre_v34_exit_gate.py','centre-v34-fixture-check.json','centre-v34-launcher-exit-check.json',
        'centre-v34-fixtures-review.md',Path(__file__).name,'close_centre_v34_fixtures_once.py',
        START.name,archive.name]+list(exits)+logs
    files={**prior['files'],**{n:digest(n) for n in names}}
    atomic_json(DRAFT,{'integrity_passed':True,'static_passed':True,'fixtures_complete':True,
        'numerical_run':False,'capture_permitted':False,'files':files,'protected':prior['protected'],
        'display':{n:digest(n) for n in prior['display']},'new_images':0,
        'check_receipt':'centre-v34-fixture-check.json','launcher_amendment':'centre-v34-launcher-exit-check.json',
        'limits':'Complete fixtures only. No GLSL, v34 field samples, cost, capture or realism. Initial offline checker failure preserved; corrected static evidence is not numerical PASS.'})
    print(json.dumps({'draft_ready':True,'files':len(files),'fixtures_complete':True,'numerical_run':False}))


if __name__=='__main__':main()
