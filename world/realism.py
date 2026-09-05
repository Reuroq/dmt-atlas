"""REDIRECT4's manual realism gate. No inferred grades or automatic recognition claims."""
import json
from pathlib import Path

QUESTION = 'Would someone who has had this experience recognise this, or does it read as a game?'
GRADES = ('RECOGNISE', 'CLOSE', 'GAME')


def evaluate(here, targets, being_stages, signature, digest):
    path = here / 'realism-grades.json'
    ledger = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {'targets': {}}
    rows = []
    for target in targets:
        review = ledger.get('targets', {}).get(target, {})
        grade = review.get('grade')
        blockers, frames = [], []
        if grade not in GRADES:
            blockers.append('No inspected realism grade')
        elif grade != 'RECOGNISE':
            blockers.append('Rebuild required: ' + grade)
        if not review.get('reason') or not review.get('temporal_observation'):
            blockers.append('Specific visual and temporal reasons required')
        captures = review.get('captures', [])
        for capture in captures:
            try:
                image = (here / capture['file']).resolve()
                receipt_path = image.with_suffix('.json')
                assert image.is_relative_to(here) and image.suffix == '.png'
                assert digest(image) == capture['sha256']
                assert digest(receipt_path) == capture['receipt_sha256']
                receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
                assert receipt['file'] == image.name and receipt['capture_sha256'] == capture['sha256']
                assert receipt['render_signature'] == signature
                assert capture.get('inspection') and not receipt['errors']
                d = receipt['capture_diagnostics']
                assert d['detail'] == 'high' and d['paused'] and not d['transition']
                assert not d['missingEvidence'] and d['uncitedMeshes'] == 0
                assert receipt.get('veil_opacity', 0) == 0
                assert d['stage'] in being_stages.get(target, [target])
                if target in being_stages:
                    assert review.get('close_up') and any(a['kind'] == target for a in d['actors'])
                    assert capture.get('close_up_observation')
                frames.append((capture['sha256'], d))
            except (AssertionError, KeyError, OSError, ValueError, TypeError):
                blockers.append('Missing, stale, invalid or uninspected HIGH receipt: ' + str(capture.get('file')))
        # A real temporal pair, not two copies or an animation timestamp typed into the ledger.
        pair = any(a[0] != b[0] and a[1]['stage'] == b[1]['stage']
                   and a[1]['position'] == b[1]['position']
                   and a[1]['yaw'] == b[1]['yaw'] and a[1]['pitch'] == b[1]['pitch']
                   and abs(a[1]['animTime'] - b[1]['animTime']) >= 2
                   for a in frames for b in frames)
        if not pair:
            blockers.append('Two inspected fresh HIGH frames, same camera, >=2 animation seconds apart required')
        rows.append({'id': target, 'grade': grade if grade in GRADES else 'PENDING',
                     'reason': review.get('reason', 'Not yet inspected under REDIRECT4.'),
                     'temporal_observation': review.get('temporal_observation', ''),
                     'passed': not blockers, 'blockers': list(dict.fromkeys(blockers)),
                     'captures': [c.get('file') for c in captures]})
    result = {'question': QUESTION, 'passed': all(r['passed'] for r in rows),
              'render_signature': signature, 'targets': rows,
              'limits': 'Adversarial visual judgment of a procedural interpretation, not witness validation or a claim to reproduce a subjective experience.'}
    (here / 'realism-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    lines = ['# Visual realism — REDIRECT4', '', QUESTION, '',
             '**' + ('PASS' if result['passed'] else 'NOT PASSED') + '**. Coverage and navigation acceptance remain separate required gates.', '',
             'RECOGNISE: convincing continuous, embodied and moving visual space. CLOSE: some qualities convincing, identifiable realism gaps. GAME: visibly built from game-like primitives, flat surfaces, repeated tiles or disconnected dot/lattice actors. PENDING is not a grade; no fresh inspection exists.', '',
             result['limits'], '', '| Target | Grade | Specific visual reasons |', '| --- | --- | --- |']
    lines += [f"| {r['id']} | {r['grade']} | {r['reason'].replace('|', '/')} |" for r in rows]
    for r in rows:
        lines += ['', '## ' + r['id'], '', r['temporal_observation'] or 'Temporal inspection pending.', '',
                  'Frames: ' + (', '.join(r['captures']) or 'none'), '',
                  'Gate: ' + ('PASS' if r['passed'] else '; '.join(r['blockers']))]
    (here / 'REALISM.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return result
