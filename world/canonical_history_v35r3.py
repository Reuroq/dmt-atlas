"""Read-only eligibility for a distinct successor; failed global is never credited."""
import additive_runtime_v35r2 as old

HISTORY = 'centre-v35r2-additive-runtime-integrity.json'
HISTORY_SHA = '86465f6ee8b4617b7638dc9d1852c9eb19c6d6ca28e64314b01c2c316a1e0f78'
UPSTREAM = ('bounds', 'numerical', 'local')


def verify_history(archives=None):
    old.require(old.digest(HISTORY) == HISTORY_SHA, 'Wrong terminal history')
    gate = old.read(HISTORY)
    for group in ('files', 'protected'):
        old.verify(gate[group])
    for name, sha in gate['display'].items():
        target = (archives or {}).get(name, name)
        old.require(old.digest(target) == sha, 'Historical display: '+name)
    stem = 'centre-v35r2-additive-runtime-close-once'
    receipt, launch = old.read(stem+'-exit.json'), old.read(stem+'-launch.json')
    old.require(type(receipt['actual_exit']) is int and receipt['actual_exit'] == 0
                and receipt['launcher_error'] is None)
    for key, name in (('manifest', HISTORY), ('log', stem+'.log'), ('launch', stem+'-launch.json')):
        old.require(receipt[key+'_sha256'] == old.digest(name))
    for key, name in (('script', 'close_additive_runtime_v35r2.py'),
                      ('launcher', 'run_close_additive_runtime_v35r2_once.py'),
                      ('history', old.MANIFEST)):
        old.require(launch[key+'_sha256'] == old.digest(name))
    old.require(gate['runtime_closed'] is True and gate['failed_stage'] == 'global'
                and gate['numeric_passed'] is False and gate['capture_permitted'] is False)
    accepted = {stage: old.stage_receipt(stage) for stage in UPSTREAM}
    failed = old.read(old.artifact('global', 'exit.json'))
    old.require(type(failed['actual_exit']) is int and failed['actual_exit'] == 1
                and failed['launcher_error'] is None)
    old.require(failed['files'] == old.inventory('global', ('exit.json',)))
    old.require(old.read(old.artifact('global', 'result.json'))['global_roots_passed'] is False)
    old.require((old.directory('global')/'failure.json').is_file()
                and not (old.directory('global')/'completed.json').exists())
    old.require(not old.directory('combination').exists(), 'Historical successor must remain unattempted')
    try:
        old.stage_receipt('global')
    except AssertionError:
        pass
    else:
        raise AssertionError('Failed historical global became eligible')
    return gate, accepted
