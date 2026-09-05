"""Synthetic-only successor integration; no field module or browser imports."""
import ast
import copy
import json
import os
import sys
from pathlib import Path
import numpy as np
import canonical_runtime_v35r3 as r
import canonical_evidence_v35r3 as e
import root_reference_contract_v35r2 as contract
from build_canonical_v35r3 import derive


def rejected(callback):
    try:
        callback()
    except (AssertionError, ValueError, TypeError, KeyError, OSError):
        return
    raise AssertionError('Invalid evidence accepted')


def node(source, name):
    return next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)


def source_checks():
    for name, expected in derive().items():
        r.require((r.HERE/name).read_text() == expected, 'Derivation: '+name)
    old_global = (r.HERE/'global_additive_v35r2.py').read_text()
    new_global = (r.HERE/'global_canonical_v35r3.py').read_text()
    r.require(ast.dump(node(old_global, 'main')) == ast.dump(node(new_global, 'main')))
    old_e = (r.HERE/'additive_evidence_v35r2.py').read_text()
    new_e = (r.HERE/'canonical_evidence_v35r3.py').read_text()
    fixed = node(new_e, 'finish_global')
    expected_read = ast.parse("results=read(artifact('global','raw.json'))").body[0]
    r.require(ast.dump(fixed.body[1]) == ast.dump(expected_read))
    fixed.body.pop(1)
    r.require(ast.dump(fixed) == ast.dump(node(old_e, 'finish_global')))
    for fn in ('global_valid', 'numeric_assessment', 'validate_scan', 'validate_local'):
        r.require(ast.dump(node(old_e, fn)) == ast.dump(node(new_e, fn)))
    old_r = (r.HERE/'additive_runtime_v35r2.py').read_text()
    new_r = (r.HERE/'canonical_runtime_v35r3.py').read_text()
    for fn in ('atomic_json', 'read', 'expected_cases', 'expected_keys', 'bijection'):
        r.require(ast.dump(node(old_r, fn)) == ast.dump(node(new_r, fn)))
    r.require(r.STAGES == ('global', 'combination') and len(r.expected_keys()) == 720)
    return {'exact_derivations': 5, 'entire_global_main_ast_unchanged': True,
            'finish_global_only_change': 'read canonical raw after durable save',
            'strict_predicates_unchanged': True}


def integration_checks():
    root = r.HERE/(r.PREFIX+'-serialization-fixtures'); root.mkdir()
    home, old_home = r.HERE, r.old.HERE
    read_fn, save_fn = e.read, e.atomic_json
    identities = r.expected_keys()
    raw, legacy, results = [], [], []
    for identity in r.expected_cases():
        case = dict(zip(('width', 'height', 'z', 'time', 'high'), identity))
        refs, independent = [], []
        for fullkey in (k for k in identities if k[:5] == identity):
            ray = fullkey[-1]
            reference = {'ray': ray, 'missing_reference': True}
            lo, hi, gpu = np.float64(10), np.float64(10+5e-8), np.float64(10.001)
            refs.append(reference)
            independent.append({'ray': ray, 'gpu_depth': gpu, 'original_reference': reference,
                'first_bracket': [lo, hi, 1., -1.], 'difference': abs((lo+hi)/2-gpu),
                'subdivisions': 1, 'refined_intervals_excluded': 0, 'coarse_intervals': 3334,
                'potential_intervals': 1, 'unresolved': [], 'passed': True})
        raw.append(dict(case, hits=[10.001, 0., 0., 0.]*(identity[0]*identity[1])))
        legacy.append(dict(case, references=refs))
        results.append(dict(case, references=independent, passed=True))
    example = results[0]['references'][0]
    r.require(type(example['first_bracket'][0]) is np.float64)
    r.require(not contract.finite(example['first_bracket'][0]) and not e.global_valid(example, 10.001))
    native = json.loads(json.dumps(example, allow_nan=False))
    r.require(e.global_valid(native, 10.001) and native == example)
    mutations = {
        'passed_false': lambda x: x.update(passed=False),
        'unresolved': lambda x: x.update(unresolved=[{'lo': 0}]),
        'bool_difference': lambda x: x.update(difference=False),
        'wrong_difference': lambda x: x.update(difference=0.),
        'wide': lambda x: x['first_bracket'].__setitem__(1, 10.+1e-6),
        'wrong_sign': lambda x: x['first_bracket'].__setitem__(2, -1.),
        'zero_endpoint': lambda x: x['first_bracket'].__setitem__(3, 0.),
        'bool_endpoint': lambda x: x['first_bracket'].__setitem__(2, True),
        'negative_depth': lambda x: x['first_bracket'].__setitem__(0, -1.),
        'nonfinite': lambda x: x['first_bracket'].__setitem__(0, np.float64('nan')),
        'reference_mismatch': lambda x: x['original_reference'].update(missing_reference=False),
        'gpu_mismatch': lambda x: x.update(gpu_depth=9.),
    }
    scenarios = ('numpy_success', 'mutated_memory', *mutations,
                 'duplicate_key', 'missing_key', 'file_fsync_failure', 'dir_fsync_failure', 'read_failure')
    receipts = []
    try:
        for label in scenarios:
            here = root/label; here.mkdir(); r.HERE = r.old.HERE = here
            r.directory('numerical').mkdir(); r.directory('global').mkdir()
            r.atomic_json(r.artifact('numerical', 'raw.json'), raw)
            r.atomic_json(r.artifact('numerical', 'legacy-check.json'), {'cases': legacy})
            data = copy.deepcopy(results)
            if label in mutations:
                mutations[label](data[0]['references'][0])
            if label == 'duplicate_key': data[0]['references'].append(copy.deepcopy(data[0]['references'][0]))
            if label == 'missing_key': data[0]['references'].pop()
            journal = r.Journal(here/r.artifact('global', 'rays'))
            barriers, reads = [], []
            durable = [False]
            def save(name, value):
                if name != r.artifact('global', 'raw.json'):
                    return save_fn(name, value)
                fsync = os.fsync
                def sync(fd):
                    barriers.append('fsync')
                    if label == 'file_fsync_failure' and len(barriers) == 1:
                        raise OSError('synthetic file fsync failure')
                    if label == 'dir_fsync_failure' and len(barriers) == 2:
                        raise OSError('synthetic directory fsync failure')
                    fsync(fd)
                os.fsync = sync
                try:
                    save_fn(name, value)
                finally:
                    os.fsync = fsync
                r.require(len(barriers) == 2)
                durable[0] = True
                if label == 'mutated_memory': value[0]['references'][0]['passed'] = False
            def read(name):
                if name == r.artifact('global', 'raw.json'):
                    r.require(durable[0] and len(barriers) == 2, 'Assessment read before durability')
                    r.require(not (here/(name+'.pending')).exists())
                    reads.append(name)
                    if label == 'read_failure': raise OSError('synthetic canonical read failure')
                return read_fn(name)
            e.atomic_json, e.read = save, read
            good = label in ('numpy_success', 'mutated_memory')
            if good: e.finish_global(data, journal)
            else: rejected(lambda: e.finish_global(data, journal))
            result_path = here/r.artifact('global', 'result.json')
            result = r.read(result_path) if result_path.exists() else None
            r.require((result is not None and result['global_roots_passed'] is True) == good)
            if good:
                r.require(len(reads) == 1 and len(result['records']) == 720 and result['numeric_passed'] is False)
                for record in result['records']:
                    item = record['independent']
                    r.require(all(type(v) is float for v in item['first_bracket']))
                    r.require(e.global_valid(item, 10.001))
                r.require(result['raw_sha256'] == r.digest(r.artifact('global', 'raw.json')))
            receipts.append({'scenario': label, 'accepted': good, 'result_saved': result is not None,
                             'raw_reads': len(reads), 'durability_barriers': len(barriers)})
    finally:
        r.HERE, r.old.HERE = home, old_home
        e.read, e.atomic_json = read_fn, save_fn
    return {'numpy_version': np.__version__, 'complete_synthetic_keys': 720,
            'native_numpy_equal_pair_reproduced': True, 'scenarios': receipts,
            'synthetic_inputs_only': True, 'field_samples': 0}


def lifecycle_checks():
    import run_canonical_v35r3_once as launcher
    root = r.HERE/(r.PREFIX+'-lifecycle-fixtures'); root.mkdir()
    source_names = ('canonical_runtime_v35r3.py', 'canonical_history_v35r3.py',
                    'additive_runtime_v35r2.py', 'run_canonical_v35r3_once.py')
    sources = {n: (r.HERE/n).read_bytes() for n in source_names}
    home, eligibility, prerequisites, gate = r.HERE, r.eligibility, r.prerequisite_hashes, r.fixture_gate
    receipt_fn, argv = r.stage_receipt, sys.argv[:]
    callbacks = {
        'success': "r.atomic_json(r.artifact('global','result.json'),{'global_roots_passed':True})",
        'false-result': "r.atomic_json(r.artifact('global','result.json'),{'global_roots_passed':False})",
        'exception': "raise RuntimeError('synthetic failure')",
        'partial': "(r.directory('global')/'raw.json.pending').write_text('partial');raise RuntimeError('partial')",
        'signal': "import os,signal;os.kill(os.getpid(),signal.SIGTERM)",
        'late-exit': "r.atomic_json(r.artifact('global','result.json'),{'global_roots_passed':True})",
    }
    receipts = []
    try:
        for label, callback in callbacks.items():
            here = root/label; here.mkdir(); r.HERE = here
            for name, source in sources.items(): (here/name).write_bytes(source)
            (here/r.MANIFEST).write_text('{}')
            script = "import canonical_runtime_v35r3 as r\nr.eligibility=lambda stage:{}\nr.prerequisite_hashes=lambda stage:{}\ndef callback():\n    "+callback+"\nr.worker('global',callback)\n"
            if label == 'late-exit': script += 'raise SystemExit(7)\n'
            (here/r.SCRIPTS['global']).write_text(script)
            r.eligibility = lambda stage: {}; r.prerequisite_hashes = lambda stage: {}
            sys.argv = ['synthetic-launcher', 'global']
            code = launcher.main()
            r.require((code == 0) == (label == 'success'))
            if label == 'success': receipt_fn('global')
            else: rejected(lambda: receipt_fn('global'))
            rejected(launcher.main)
            # Exercise the actual two-stage dependency graph, not a reimplementation.
            r.fixture_gate = lambda: {}
            r.stage_receipt = lambda s: {'synthetic_upstream': True} if s in r.UPSTREAM else receipt_fn(s)
            r.eligibility = eligibility
            if label == 'success': r.require(set(r.eligibility('combination')) == set(r.UPSTREAM+('global',)))
            else: rejected(lambda: r.eligibility('combination'))
            receipts.append({'scenario': label, 'actual_exit': r.read(r.artifact('global', 'exit.json'))['actual_exit']})
        r.HERE = root/'success'; r.stage_receipt = receipt_fn
        for name, change in (('result.json', lambda x: x.update(global_roots_passed=False)),
                             ('exit.json', lambda x: x.update(actual_exit=False)),
                             ('launch.json', lambda x: x.update(prerequisites={'forged': 'hash'}))):
            path = r.directory('global')/name; original = path.read_bytes()
            value = json.loads(original); change(value); path.write_text(json.dumps(value))
            rejected(lambda: receipt_fn('global')); path.write_bytes(original)
            receipt_fn('global')
        # Every accepted upstream is mandatory; a passing global cannot replace one.
        for missing in r.UPSTREAM:
            def upstream(stage):
                r.require(stage != missing, 'synthetic ineligible upstream')
                return {} if stage in r.UPSTREAM else receipt_fn(stage)
            r.stage_receipt = upstream
            for stage in r.STAGES: rejected(lambda: eligibility(stage))
        rejected(lambda: eligibility('numerical'))
    finally:
        r.HERE, r.eligibility, r.prerequisite_hashes, r.fixture_gate = home, eligibility, prerequisites, gate
        r.stage_receipt, sys.argv = receipt_fn, argv
    # Actual read-only eligibility uses successful old receipts, never old global.
    from canonical_history_v35r3 import verify_history
    _, accepted = verify_history()
    r.require(set(accepted) == set(r.UPSTREAM))
    r.require(r.directory('global') != r.old.directory('global'))
    digest_fn = r.digest
    try:
        r.digest = lambda name: 'synthetic-hash-for:'+name
        r.require(r.artifact('global', 'exit.json') not in prerequisites('global'))
        r.require(r.old.artifact('global', 'exit.json') not in prerequisites('combination'))
        r.require(r.artifact('global', 'exit.json') in prerequisites('combination'))
    finally:
        r.digest = digest_fn
    rejected(lambda: r.old.stage_receipt('global'))
    rejected(lambda: r.eligibility('global'))  # No static close receipt yet.
    return {'actual_foreground_children': receipts, 'replay_rejections': 6,
            'failed_successor_rejections': 5, 'tamper_or_boolean_exit_rejections': 3,
            'upstream_rejections': 6, 'premature_runtime_rejected': True,
            'original_global_ineligible': True, 'synthetic_gate_overrides_labelled': True}


def check():
    result = {'source': source_checks(), 'serialization': integration_checks(),
              'lifecycle': lifecycle_checks()}
    r.require('field_centre_v35r2' not in sys.modules and 'csg_interval_v35r2' not in sys.modules)
    r.require(not any(n.startswith('playwright') for n in sys.modules))
    result.update(static_passed=True, runtime_fixtures_complete=True, numerical_run=False,
                  numeric_passed=False, field_samples=0, browser_runs=0, capture_permitted=False)
    return result
