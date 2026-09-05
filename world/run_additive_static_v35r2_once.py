"""Exclusive static stages, synchronously waited actual child exit receipts."""
import os
import subprocess
import sys
import prepare_additive_v35r2 as p
import additive_runtime_v35r2 as r


def main():
    label=sys.argv[1];r.require(label in ('build','freeze','check','close'))
    stem=r.PREFIX+'-'+label+'-once'
    r.require(not any((r.HERE/(stem+s)).exists() for s in ('-launch.json','-exit.json','.log','-launch.json.pending')),'Never replay')
    p.prior()
    if label!='build':p.receipt('build')
    if label in ('check','close'):p.gate();p.receipt('freeze')
    if label=='close':p.receipt('check')
    script='prepare_additive_v35r2.py';argv=[sys.executable,'-B','-u',str(r.HERE/script),label]
    r.atomic_json(stem+'-launch.json',{'argv':argv,'script_sha256':r.digest(script),
        'launcher_sha256':r.digest(os.path.basename(__file__)),'history_sha256':r.digest(r.HISTORY),
        'builder_sha256':r.digest('build_additive_v35r2.py'),
        'freeze_sha256':r.digest(r.PREFIX+'-freeze.json') if label in ('check','close') else None})
    actual,error=None,None
    try:
        with (r.HERE/(stem+'.log')).open('x') as stream:
            try:
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='/home/clawd/pixelvision-venv/lib/python3.12/site-packages')
                actual=subprocess.run(argv,cwd=r.HERE.parent,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=60).returncode
            finally:stream.flush();os.fsync(stream.fileno())
    except BaseException as exc:error=repr(exc)
    r.atomic_json(stem+'-exit.json',{'actual_exit':actual,'launcher_error':error,
        'log_sha256':r.digest(stem+'.log'),'launch_sha256':r.digest(stem+'-launch.json'),
        'manifest_sha256':r.digest(r.MANIFEST) if label=='close' and (r.HERE/r.MANIFEST).exists() else None})
    print(label,'actual exit',actual,'launcher error',error,flush=True)
    return actual if actual is not None and actual>=0 else 1


if __name__=='__main__':
    sys.exit(main())
