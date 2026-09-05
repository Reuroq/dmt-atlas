"""Create distinct revision sources once; never execute old preparation gates."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
OLD = 'centre_v34_staged_arithmetic'
NEW = OLD + '_r2'
OP = 'centre-v34-staged-arithmetic'
NP = OP + '-r2'


def put(name, content):
    with (HERE / name).open('x') as f:
        f.write(content)


def renamed(text):
    return text.replace(OLD, NEW).replace(OP, NP)


def main():
    import probe_centre_v34_staged_arithmetic as old
    history = old.read(OP + '-preparation-failure-integrity.json')
    for k in ('files', 'protected', 'display'):
        old.verify(history[k])
    html = (HERE / ('gpu_' + OLD + '.html')).read_text()
    assert 'window.arithmeticStep=' not in html
    local = (HERE / 'gpu_centre_v34_gl_localization.html').read_text()
    wrapper = local[local.index('window.localizationStep='):local.index('</script>', local.index('window.localizationStep='))]
    wrapper = wrapper.replace('window.localizationStep=', 'window.arithmeticStep=')
    put('gpu_' + NEW + '.html', html.replace('window.arithmeticPlan=makePlan;', 'window.arithmeticPlan=makePlan;\n' + wrapper))
    probe = renamed((HERE / ('probe_' + OLD + '.py')).read_text())
    probe = probe.replace("HISTORY = 'centre-v34-gl-localization-runtime-integrity.json'", "HISTORY = 'centre-v34-staged-arithmetic-preparation-failure-integrity.json'")
    probe = probe.replace("assert history['saved_evidence_verified'] and history['actual_exit'] == 1", "assert not history['static_passed'] and history['static_actual_exit'] == 1\n    prior = read('centre-v34-staged-arithmetic-static-once-exit.json')\n    assert prior['actual_exit'] == 1 and prior['launcher_error'] is None\n    assert prior['log_sha256'] == digest('centre-v34-staged-arithmetic-static-once.log')\n    assert prior['launch_sha256'] == digest('centre-v34-staged-arithmetic-static-once-launch.json')")
    put('probe_' + NEW + '.py', probe)
    put('run_' + NEW + '_once.py', renamed((HERE / ('run_' + OLD + '_once.py')).read_text()))
    check = renamed((HERE / ('check_' + OLD + '.py')).read_text())
    check = check.replace('import tempfile', 'import tempfile\nfrom static_centre_v34_staged_arithmetic_r2 import durable_node, staged_checks')
    check = check.replace("subprocess.run(['node', '--check'], input=js, text=True, check=True, capture_output=True)", "durable_node('syntax', js, syntax=True)")
    check = check.replace("checked = subprocess.run(['node', '-e', node], text=True, check=True, capture_output=True)\n    result = json.loads(checked.stdout); plan = result['plan']", "result = staged_checks(js, node); plan = result['plan']")
    # Freeze requires insertion-only HTML and unchanged protocol arithmetic functions.
    needle = "assert 'forceContextLoss' not in js"
    extra = """
    baseline = (p.HERE / 'gpu_centre_v34_staged_arithmetic.html').read_text()
    start = html.index('window.arithmeticStep=')
    end = html.index('</script>', start)
    assert html[:start] + html[end:] == baseline
    prior_tree = ast.parse((p.HERE / 'probe_centre_v34_staged_arithmetic.py').read_text())
    current_tree = ast.parse((p.HERE / 'probe_centre_v34_staged_arithmetic_r2.py').read_text())
    for name in ('f32','bit','inputs','expected','compare','assess','supported','run_steps','main'):
        pick = lambda tree: next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(pick(prior_tree)) == ast.dump(pick(current_tree)), name
"""
    check = check.replace(needle, needle + extra)
    put('check_' + NEW + '.py', check)
    protocol = renamed((HERE / (OP + '-protocol.md')).read_text())
    protocol += '''\n## Revision 2 static observability and repair\n\nThe frozen first attempt is immutable. Its HTML lacks arithmeticStep. This\nrevision inserts only the existing GL-localization operation wrapper, renamed;\nshader, plan, input and support/assessment/runtime-loop functions are unchanged.\nThe checker proves HTML insertion-only and Python function AST identity.\nBefore interpreting every Node status, exclusive source, argv/hash, stdout,\nstderr and actual-exit receipts are fsynced. A separate original-source mock\nreproduction must fail specifically at the missing API; it does not recover\nthe lost historical stderr. Independent stages name API, GL errors, exception,\nbounded drain, context loss, packing, shaders, materials and readbacks. The\noriginal combined mock and all original Python static requirements still run.\nFreeze/static only in this phase. No GPU or browser until separate runtime.\n'''
    put(NP + '-protocol.md', protocol)
    print('Distinct r2 sources created; not frozen or executed')


if __name__ == '__main__':
    main()
