"""Foreground closure: publish full fixture receipt only after actual exit0."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from cost_lifecycle_v34 import atomic_json

HERE=Path(__file__).resolve().parent
log=HERE/'close-centre-v34-fixtures-once.log'
exit_path=HERE/'close-centre-v34-fixtures-once-exit.json'
destination=HERE/'centre-v34-fixture-integrity.json'
assert not any(p.exists() for p in [log,exit_path,destination])
with log.open('x') as stream:
    result=subprocess.run([sys.executable,'-u',str(HERE/'close_centre_v34_fixtures.py')],
                          stdout=stream,stderr=subprocess.STDOUT)
    stream.flush();os.fsync(stream.fileno())
atomic_json(exit_path,{'actual_exit':result.returncode,'log':log.name,
    'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
if result.returncode:
    print(json.dumps({'actual_exit':result.returncode,'log':log.name}));sys.exit(result.returncode)
draft=HERE/'centre-v34-fixture-closure-draft.json'
receipt=json.loads(draft.read_text())
for path in [draft,log,exit_path]:
    receipt['files'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
for group in ['files','protected','display']:
    for name,want in receipt[group].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==want,name
atomic_json(destination,receipt)
print(json.dumps({'actual_exit':0,'fixtures_complete':True,'numerical_run':False,
                  'bound_files':len(receipt['files'])}))
