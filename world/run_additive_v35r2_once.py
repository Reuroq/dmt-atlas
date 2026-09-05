"""Launch one new stage synchronously; a partial attempt permanently claims its name."""
import os
import signal
import subprocess
import sys
import additive_runtime_v35r2 as r


def main():
    stage=sys.argv[1]
    r.eligibility(stage)
    root=r.directory(stage)
    root.mkdir()  # Atomic claim: includes pre-launch and SIGKILL failures.
    script=r.SCRIPTS[stage]
    argv=[sys.executable,'-B','-u',str(r.HERE/script)]
    r.atomic_json(root/'launch.json', {'stage':stage,'argv':argv,
        'script_sha256':r.digest(script),'launcher_sha256':r.digest(os.path.basename(__file__)),
        'manifest_sha256':r.digest(r.MANIFEST),'prerequisites':r.prerequisite_hashes(stage)})
    actual,error=None,None
    child=None
    pending_signals=[]
    def forward(signum, frame):
        if child is None:
            pending_signals.append(signum)
        elif child.poll() is None:
            child.send_signal(signum)
    old={s:signal.signal(s,forward) for s in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP)}
    try:
        env=dict(os.environ,PLAYWRIGHT_BROWSERS_PATH='/opt/ms-playwright',
                 PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='/home/clawd/pixelvision-venv/lib/python3.12/site-packages')
        with (root/'foreground.log').open('x') as stream:
            try:
                # No detached/session/background execution: synchronously waited child.
                child=subprocess.Popen(argv,cwd=r.HERE.parent,env=env,stdout=stream,stderr=subprocess.STDOUT)
                for sig in pending_signals:
                    if child.poll() is None:child.send_signal(sig)
                actual=child.wait()
            finally:
                stream.flush();os.fsync(stream.fileno())
    except BaseException as exc:
        error=repr(exc)
        if child is not None and child.poll() is None:
            child.terminate();actual=child.wait()
    finally:
        r.atomic_json(root/'exit.json', {'actual_exit':actual,'launcher_error':error,'files':r.inventory(stage)})
        for sig,handler in old.items():
            signal.signal(sig,handler)
    print(stage,'actual exit',actual,'launcher error',error,flush=True)
    return actual if actual is not None and actual>=0 else 1


if __name__=='__main__':
    sys.exit(main())
