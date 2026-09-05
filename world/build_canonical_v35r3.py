"""Deterministic source derivations only; never imports or runs field workers."""
import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'centre-v35r3-canonical'


def replace(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def function(text, name, replacement):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return replace(text, ast.get_source_segment(text, node), replacement.strip())


def derive():
    runtime = (HERE/'additive_runtime_v35r2.py').read_text()
    runtime = replace(runtime, "PREFIX = 'centre-v35r2-additive'", "PREFIX = '"+PREFIX+"'")
    runtime = replace(runtime, "HISTORY = 'centre-v35r2-root-contract-integrity.json'", "from canonical_history_v35r3 import HISTORY, UPSTREAM, verify_history\nimport additive_runtime_v35r2 as old")
    start = runtime.index('STAGES = '); end = runtime.index('\n\n\ndef require', start)
    runtime = runtime[:start]+'''STAGES = ('global', 'combination')
SCRIPTS = {'global': 'global_canonical_v35r3.py', 'combination': 'combine_canonical_v35r3.py'}
READY = {'global': 'global_roots_passed', 'combination': 'numeric_passed'}'''+runtime[end:]
    runtime = replace(runtime, "    require(stage in STAGES)\n    return HERE/(PREFIX+'-'+stage)", "    if stage in UPSTREAM:\n        return old.directory(stage)\n    require(stage in STAGES)\n    return HERE/(PREFIX+'-'+stage)")
    runtime = replace(runtime, "def stage_receipt(stage):\n", "def stage_receipt(stage):\n    if stage in UPSTREAM:\n        return old.stage_receipt(stage)\n")
    runtime = runtime.replace('prepare_additive_v35r2.py', 'prepare_canonical_v35r3.py').replace('run_additive_static_v35r2_once.py', 'run_canonical_static_v35r3_once.py').replace('run_additive_v35r2_once.py', 'run_canonical_v35r3_once.py')
    runtime = function(runtime, 'fixture_gate', '''
def fixture_gate():
    gate = read(MANIFEST)
    require(gate['static_passed'] is True and gate['runtime_fixtures_complete'] is True)
    require(gate['numerical_run'] is False and gate['capture_permitted'] is False)
    for group in ('files', 'protected', 'display'):
        verify(gate[group])
    verify_history(gate['historical_display'])
    require(gate['history_sha256'] == digest(HISTORY))
    for label in ('freeze', 'check', 'close'):
        static_receipt(label)
    return gate
''')
    runtime = function(runtime, 'eligibility', '''
def eligibility(stage):
    fixture_gate()
    require(stage in STAGES)
    return {prior: stage_receipt(prior) for prior in UPSTREAM+STAGES[:STAGES.index(stage)]}
''')
    runtime = function(runtime, 'prerequisite_hashes', '''
def prerequisite_hashes(stage):
    require(stage in STAGES)
    return {HISTORY: digest(HISTORY),
            'centre-v35r2-additive-runtime-close-once-exit.json': digest('centre-v35r2-additive-runtime-close-once-exit.json'),
            **{artifact(prior, 'exit.json'): digest(artifact(prior, 'exit.json'))
               for prior in UPSTREAM+STAGES[:STAGES.index(stage)]}}
''')
    evidence = (HERE/'additive_evidence_v35r2.py').read_text().replace('from additive_runtime_v35r2 import', 'from canonical_runtime_v35r3 import')
    evidence = replace(evidence, "    atomic_json(artifact('global','raw.json'),results)\n    cases=", "    atomic_json(artifact('global','raw.json'),results)\n    results=read(artifact('global','raw.json'))\n    cases=")
    global_source = (HERE/'global_additive_v35r2.py').read_text().replace('from additive_runtime_v35r2 import', 'from canonical_runtime_v35r3 import').replace('from additive_evidence_v35r2 import', 'from canonical_evidence_v35r3 import')
    combined = (HERE/'combine_additive_v35r2.py').read_text().replace('from additive_runtime_v35r2 import', 'from canonical_runtime_v35r3 import').replace('from additive_evidence_v35r2 import', 'from canonical_evidence_v35r3 import')
    launcher = (HERE/'run_additive_v35r2_once.py').read_text().replace('import additive_runtime_v35r2 as r', 'import canonical_runtime_v35r3 as r')
    return {'canonical_runtime_v35r3.py': runtime, 'canonical_evidence_v35r3.py': evidence,
            'global_canonical_v35r3.py': global_source, 'combine_canonical_v35r3.py': combined,
            'run_canonical_v35r3_once.py': launcher}


def build():
    from canonical_history_v35r3 import verify_history
    verify_history()
    for name, source in derive().items():
        ast.parse(source, filename=name)
        with (HERE/name).open('x') as stream:
            stream.write(source)


if __name__ == '__main__':
    build()
