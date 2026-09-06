"""Local v0.4 enrichment; no network, file writes, or semantic rejection.

Provider records retain free-text descriptors. ``normalised`` maps them to the
existing vocabulary; quote objects carry locally derived evidence metadata.
"""
from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
import json
from pathlib import Path
import re


EXCLUDED = re.compile(
    r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ug|milligrams?|micrograms?)\b|'
    r'\b(?:dos(?:e|es|ed|ing|age)|smok(?:e|ed|ing)|'
    r'vap(?:e|ed|ing|ori[sz](?:e|ed|er|ing))|inject(?:ed|ing|ion)?|'
    r'snort(?:ed|ing)?|insufflat\w*|sublingual(?:ly)?|intravenous(?:ly)?|'
    r'oral(?:ly)?|procure(?:d|ment)?|vendors?|dealers?|naphtha)\b', re.I)

DESCRIPTORS = ('light', 'colour', 'motion', 'geometry', 'material', 'density',
               'scale', 'affect', 'transition_trigger')
BEING_DESCRIPTORS = ('form', 'behaviour', 'communication', 'affect')
SYNONYMS = {
    'colour': {'gray': 'grey', 'multicolored': 'multicoloured',
               'multicoloured': 'multicoloured', 'golden': 'gold'},
    'motion': {'spinning': 'rotating', 'motionless': 'still'},
    'affect': {'afraid': 'fear', 'fearful': 'fear', 'joyful': 'joy',
               'loving': 'love', 'peaceful': 'calm'},
    'communication': {'telepathy': 'telepathic'},
}


def decode_record(text):
    """Accept JSON, fenced JSON, or the first balanced object in surrounding text."""
    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant')
    try:
        return json.loads(text, parse_constant=invalid_constant)
    except json.JSONDecodeError:
        start = text.find('{')
        if start < 0:
            raise ValueError('No JSON object') from None
        # raw_decode respects escaped quotes and braces inside JSON strings.
        try:
            return json.JSONDecoder(parse_constant=invalid_constant).raw_decode(text[start:])[0]
        except json.JSONDecodeError:
            raise ValueError('First JSON object does not parse') from None


def structural_check(record):
    """Only a boolean classification and a quote for every scene are required.

    Missing/null scenes represent zero scenes and are flagged during enrichment.
    A non-list scene collection or a scene without quotes cannot satisfy the
    scene/quote structure. Descriptor values never determine acceptance.
    """
    if not isinstance(record, dict) or type(record.get('is_trip_report')) is not bool:
        raise ValueError('is_trip_report must be a boolean in a JSON object')
    scenes = record.get('scenes')
    if scenes is None:
        return
    if not isinstance(scenes, list):
        raise ValueError('scenes must be an array')
    for scene in scenes:
        if (not isinstance(scene, dict) or not isinstance(scene.get('quotes'), list)
                or not scene['quotes']):
            raise ValueError('Every scene must have at least one quote')


def folded(text):
    """Casefold and collapse whitespace, retaining Unicode code-point spans."""
    chars, spans = [], []
    for index, char in enumerate(text):
        if char.isspace():
            if chars and chars[-1] == ' ':
                spans[-1] = (spans[-1][0], index + 1)
            else:
                chars.append(' ')
                spans.append((index, index + 1))
        else:
            for lowered in char.casefold():
                chars.append(lowered)
                spans.append((index, index + 1))
    return ''.join(chars), spans


def anchor_quote(quote, source, prepared=None):
    """Score before redaction; retain weak matches and earliest tied matches.

    Fuzzy search tests word-boundary windows near quote length and windows
    aligned to matching blocks. It is a heuristic, not an exhaustive substring
    optimiser or a semantic support test. No source text is truncated.
    """
    text, spans = prepared if prepared is not None else folded(source)
    needle = folded(quote)[0].strip()
    start, end, score = None, None, 0.0
    repeated = False
    if needle and text:
        exact = text.find(needle)
        if exact >= 0:
            start, end, score = exact, exact + len(needle), 1.0
            repeated = text.find(needle, exact + 1) >= 0
        else:
            size = len(needle)
            margin = max(2, size // 5)
            candidates = set()
            words = list(re.finditer(r'\S+', text))
            for i, word in enumerate(words):
                left = word.start()
                candidates.add((left, min(len(text), left + size)))
                for j in range(i, len(words)):
                    right = words[j].end()
                    if right - left > size + margin:
                        break
                    if right - left >= max(1, size - margin):
                        candidates.add((left, right))
            matcher = SequenceMatcher(None, needle, text, autojunk=False)
            for block in matcher.get_matching_blocks():
                if not block.size:
                    continue
                left = max(0, block.b - block.a)
                for delta in (-margin, 0, margin):
                    candidates.add((left, min(len(text), left + size + delta)))
            for left, right in sorted(candidates):
                if right <= left:
                    continue
                matcher = SequenceMatcher(None, needle, text[left:right], autojunk=False)
                if matcher.quick_ratio() <= score:
                    continue
                ratio = matcher.ratio()
                if ratio > score:
                    start, end, score = left, right, ratio
    redacted, count = EXCLUDED.subn('[redacted]', quote)
    return {
        'text': redacted,
        'start': spans[start][0] if start is not None else None,
        'end': spans[end - 1][1] if end is not None else None,
        'anchor_score': score, 'weak_anchor': score < 0.85,
        'redacted': bool(count), 'ambiguous_anchor': repeated,
    }


def key(text):
    return ' '.join(text.casefold().replace('-', ' ').replace('_', ' ').split())


def vocabulary_maps(vocab):
    maps = {field: {key(value): value for value in values}
            for field, values in vocab['values'].items()}
    for field, catalog in (('place', 'realm'), ('form', 'entity'), ('geometry', 'geometry')):
        mapping = maps.setdefault(field, {})
        aliases = {}
        for entry in vocab['catalog'][catalog]:
            slug = entry['slug']
            mapping[key(slug)] = slug
            for alias in [entry['name'], *entry.get('aliases', []), *entry.get('extra_keys', [])]:
                aliases.setdefault(key(alias), set()).add(slug)
        for alias, targets in aliases.items():
            # Ambiguous aliases stay other:<text>; never choose an arbitrary realm.
            if len(targets) == 1:
                mapping.setdefault(alias, next(iter(targets)))
    for field, aliases in SYNONYMS.items():
        for alias, target in aliases.items():
            if target in vocab['values'].get(field, []):
                maps[field][key(alias)] = target
    maps['transition_trigger'] = maps['trigger']
    return maps


def normalise_record(record, source, report_id=None, vocab=None):
    """Return a new enriched record; semantic or anchoring doubts only add flags."""
    structural_check(record)
    if vocab is None:
        vocab = json.loads(Path(__file__).with_name('vocab.json').read_text())
    maps = vocabulary_maps(vocab)
    result = deepcopy(record)
    flags = result.get('flags', [])
    flags = list(flags) if isinstance(flags, list) else ['malformed_flags']
    result['flags'] = flags
    result['schema_version'] = '0.4.0'
    if report_id is not None:
        if record.get('report_id') != report_id:
            flags.append('report_id_corrected')
        result['report_id'] = report_id
    if result.get('scenes') is None:
        result['scenes'] = []
        flags.append('missing_scenes')
    if result['is_trip_report'] and not result['scenes']:
        flags.append('trip_without_scenes')
    if not result['is_trip_report'] and result['scenes']:
        flags.append('non_trip_with_scenes')

    def mapped(value, field, path):
        if not isinstance(value, str):
            flags.append('non_string:' + path)
            value = json.dumps(value, ensure_ascii=False)
        if not value.strip():
            flags.append('empty_descriptor:' + path)
        if value.startswith('other:'):
            return value
        found = maps.get(field, {}).get(key(value))
        if found is None:
            flags.append('unmapped:' + path)
            return 'other:' + value
        return found

    def descriptors(obj, fields, path):
        normal = {}
        for field in fields:
            values = obj.get(field, [])
            if not isinstance(values, list):
                flags.append('non_array:' + path + '/' + field)
                values = [] if values is None else [values]
            normal[field] = [mapped(value, field, path + '/' + field) for value in values]
        obj['normalised'] = normal

    prepared = folded(source)
    for i, scene in enumerate(result['scenes']):
        path = '/scenes/' + str(i)
        descriptors(scene, DESCRIPTORS, path)
        scene['normalised']['place'] = mapped(scene.get('place', ''), 'place', path + '/place')
        for j, quote in enumerate(scene['quotes']):
            if not isinstance(quote, str):
                flags.append('non_string_quote:' + path + '/quotes/' + str(j))
                quote = json.dumps(quote, ensure_ascii=False)
            anchored = anchor_quote(quote, source, prepared)
            scene['quotes'][j] = anchored
            for flag in ('weak_anchor', 'redacted', 'ambiguous_anchor'):
                if anchored[flag]:
                    flags.append(flag + ':' + path + '/quotes/' + str(j))
        beings = scene.get('beings', [])
        if not isinstance(beings, list):
            flags.append('non_array:' + path + '/beings')
            beings = []
        for j, being in enumerate(beings):
            if isinstance(being, dict):
                descriptors(being, BEING_DESCRIPTORS, path + '/beings/' + str(j))
            else:
                flags.append('non_object:' + path + '/beings/' + str(j))

    def redact(value):
        if isinstance(value, str):
            cleaned, count = EXCLUDED.subn('[redacted]', value)
            if count:
                flags.append('excluded_text_redacted')
            return cleaned
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, dict):
            return {k: v if k in ('report_id', 'flags') else redact(v) for k, v in value.items()}
        return value

    result = redact(result)
    result['flags'] = list(dict.fromkeys(str(flag) for flag in flags))
    return result
