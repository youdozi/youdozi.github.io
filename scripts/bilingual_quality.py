"""Conservative checks, shared with the browser, for new editorial candidates.

These detect omissions, not semantic equivalence. AI review and human review remain
necessary. Legacy digests without editorial metadata keep their original contract.
"""
import json
import re
from pathlib import Path

POLICY = json.loads((Path(__file__).resolve().parents[1] / 'src/lib/bilingual-quality-policy.json').read_text())


def numbers(text):
    words = POLICY['numberWords']
    text = re.sub(r'\b(' + '|'.join(words) + r')\b', lambda m: words[m[0].lower()], text, flags=re.I)
    return {value.replace(',', '') for value in re.findall(POLICY['numberPattern'], text)}


def terms(text):
    return {name for name, pattern in POLICY['terms'].items()
            if re.search(r'(?<![A-Za-z0-9])(?:' + pattern + r')(?![A-Za-z0-9])', text, re.I)}


def validate_editions(editions):
    errors = []
    en, ko = editions['en'], editions['ko']
    if len(en['claims']) != len(ko['claims']):
        return ['language editions must have the same ordered claim count']
    for index, (left, right) in enumerate(zip(en['claims'], ko['claims'])):
        for label, extract in [('numbers', numbers), ('protected terms', terms)]:
            a, b = extract(left['text']), extract(right['text'])
            if a != b:
                errors.append(f'claim {index + 1}: bilingual {label} differ (en-only: {", ".join(sorted(a-b)) or "none"}; ko-only: {", ".join(sorted(b-a)) or "none"})')
    for lang, edition in [('en', en), ('ko', ko)]:
        body = ' '.join(c['text'] for c in edition['claims'])
        for label, extract in [('numbers', numbers), ('protected terms', terms)]:
            if extract(edition['title']) - extract(body):
                errors.append(f'{lang} title {label} must also appear in verified claims')
    if en.get('review') != ko.get('review'):
        errors.append('language editions must classify the same ordered claims into review sections')
    return errors
