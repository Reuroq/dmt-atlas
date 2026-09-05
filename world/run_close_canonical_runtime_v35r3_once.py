"""Exclusive foreground saved-only terminal closer with actual exit receipt."""
import os
import subprocess
import sys
import canonical_runtime_v35r3 as r


def main():
    r.fixture_gate()
    stem='centre-v35r3-canonical-runtime-close-once'
    r.require(not any((r.HERE/(stem+s)).exists() for s in ('-launch.json','-exit.json','.log','-launch.json.pending')))
    script='close_canonical_runtime_v35r3.py';argv=[sys.executable,'-B','-u',str(r.HERE/script)]
    r.atomic_json(stem+'-launch.json',{'argv':argv,'script_sha256':r.digest(script),
        'launcher_sha256':r.digest(os.path.basename(__file__)),'history_sha256':r.digest(r.MANIFEST)})
    actual,error=None,None
    try:
        with (r.HERE/(stem+'.log')).open('x') as stream:
            try:actual=subprocess.run(argv,cwd=r.HERE.parent,stdout=stream,stderr=subprocess.STDOUT,timeout=60).returncode
            finally:stream.flush();os.fsync(stream.fileno())
    except BaseException as exc:error=repr(exc)
    manifest='centre-v35r3-canonical-runtime-integrity.json'
    r.atomic_json(stem+'-exit.json',{'actual_exit':actual,'launcher_error':error,
        'log_sha256':r.digest(stem+'.log'),'launch_sha256':r.digest(stem+'-launch.json'),
        'manifest_sha256':r.digest(manifest) if (r.HERE/manifest).exists() else None})
    print('Terminal close actual exit',actual,'launcher error',error,flush=True)
    return actual if actual is not None and actual>=0 else 1


if __name__=='__main__':
    sys.exit(main())
