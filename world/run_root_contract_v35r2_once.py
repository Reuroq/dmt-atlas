"""Exclusive foreground contract stages with durable actual exit receipts."""
import os
import subprocess
import sys
import prepare_root_contract_v35r2 as p


def main():
    label=sys.argv[1];assert label in ('freeze','check','close')
    stem=p.PREFIX+'-'+label+'-once'
    for suffix in ('-launch.json','-exit.json','.log'):
        assert not (p.HERE/(stem+suffix)).exists(),'Never replay'
    if label=='freeze':p.prior()
    else:
        p.gate();p.receipt('freeze')
        if label=='close':p.receipt('check')
    script='prepare_root_contract_v35r2.py';argv=[sys.executable,'-B','-u',str(p.HERE/script),label]
    p.save(stem+'-launch.json',{'argv':argv,'script_sha256':p.digest(script),
        'launcher_sha256':p.digest(os.path.basename(__file__)),'history_sha256':p.digest(p.HISTORY),
        'freeze_sha256':p.digest(p.PREFIX+'-freeze.json') if label!='freeze' else None})
    actual,error=None,None
    try:
        with (p.HERE/(stem+'.log')).open('x') as stream:
            try:actual=subprocess.run(argv,cwd=p.HERE.parent,stdout=stream,stderr=subprocess.STDOUT,timeout=60).returncode
            finally:stream.flush();os.fsync(stream.fileno())
    except Exception as exc:error=repr(exc)
    manifest=p.PREFIX+'-integrity.json'
    p.save(stem+'-exit.json',{'actual_exit':actual,'launcher_error':error,
        'log_sha256':p.digest(stem+'.log'),'launch_sha256':p.digest(stem+'-launch.json'),
        'manifest_sha256':p.digest(manifest) if label=='close' and (p.HERE/manifest).exists() else None})
    print(label,'actual exit',actual,'launcher error',error)
    return actual if actual is not None and actual>=0 else 1


if __name__=='__main__':
    sys.exit(main())
