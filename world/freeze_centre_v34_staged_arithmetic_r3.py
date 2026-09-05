"""One-shot static source freeze; no checker or browser execution."""
import ast
import probe_centre_v34_staged_arithmetic_r3 as p


def main():
    p.prior(True)
    sources=[
        'prepare_centre_v34_staged_arithmetic_r3.py','freeze_centre_v34_staged_arithmetic_r3.py',
        'probe_centre_v34_staged_arithmetic_r3.py','check_centre_v34_staged_arithmetic_r3.py',
        'checks_centre_v34_staged_arithmetic_r3.py','static_centre_v34_staged_arithmetic_r3.py',
        'run_centre_v34_staged_arithmetic_r3_once.py','close_centre_v34_staged_arithmetic_r3_preparation.py',
        p.HTML,p.PREFIX+'-source-delta.json',p.PREFIX+'-protocol.md',
        p.SEEDS,p.TEXTURE,'gpu_centre_v34_offsets.html','vendor/three.min.js',
        'centre-v34-transport-runtime-close-once-launch.json','centre-v34-transport-runtime-close-once-exit.json',
        'centre-v34-transport-runtime-close-once.log','run_centre_v34_transport_runtime_close_once.py',
    ]
    for name in sources:
        if name.endswith('.py'):ast.parse((p.HERE/name).read_text(),filename=name)
    assert not any(p.HERE.glob(p.PREFIX+'-node-*'))
    assert not any(p.HERE.glob(p.PREFIX+'-event-*'))
    assert not (p.HERE/(p.PREFIX+'-static-once-launch.json')).exists()
    p.save(p.PREFIX+'-freeze.json',{'sources':{n:p.digest(n) for n in sources},
        'history_sha256':p.digest(p.HISTORY),'runtime_run':False})
    print('Frozen',len(sources),'sources; static/browser NOT RUN')


if __name__=='__main__':main()
