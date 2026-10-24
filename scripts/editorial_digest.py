"""Candidate relevance rules and human-owned editorial metadata."""
import json
from pathlib import Path
import re

POLICY = json.loads((Path(__file__).resolve().parents[1] / 'src/lib/editorial-policy.json').read_text())
SECTIONS = tuple(POLICY['sections'])


def selection_profile(item):
    if re.search(POLICY['promotionalPattern'], item.title, re.I):
        return None
    content = item.title + ' ' + item.summary
    reasons = [key for key, value in POLICY['reasons'].items() if re.search(value['pattern'], content, re.I)]
    if not reasons:
        return None
    return {'audience': POLICY['audience']['id'], 'method': POLICY['method'],
            'relevance': 'direct' if 'jvm-spring' in reasons else 'adjacent',
            'priority': 'review-soon' if re.search(POLICY['priorityPattern'], content, re.I) else 'normal',
            'reasons': reasons}


def empty_editorial():
    return {'opinion': {'en': '', 'ko': ''}, 'experiment': {
        'status': 'not_tested', 'reportUrl': None,
        'environment': {'en': '', 'ko': ''}, 'result': {'en': '', 'ko': ''}}}


def validate_review_map(review, claims):
    if not isinstance(review, dict) or set(review) != set(SECTIONS):
        return False
    for key in SECTIONS:
        indices = review[key]
        if (not isinstance(indices, list) or (key == 'keyChange' and not indices)
                or any(type(index) is not int or not 0 <= index < len(claims) for index in indices)
                or len(set(indices)) != len(indices)):
            return False
    return True


def validate_article_editorial(article):
    errors = []
    selection = article.get('selection')
    if selection is not None:
        if (not isinstance(selection, dict) or selection.get('audience') != POLICY['audience']['id']
                or selection.get('method') != POLICY['method']
                or selection.get('relevance') not in ('direct', 'adjacent')
                or selection.get('priority') not in POLICY['priorities']
                or not isinstance(selection.get('reasons'), list) or not selection['reasons']
                or any(not isinstance(reason,str) or reason not in POLICY['reasons'] for reason in selection['reasons'])):
            errors.append('invalid candidate selection metadata')
        elif (selection['relevance']=='direct') != ('jvm-spring' in selection['reasons']):
            errors.append('selection relevance does not match its reasons')
    for edition in article['editions'].values():
        if 'review' in edition and not validate_review_map(edition['review'], edition['claims']):
            errors.append('review sections must reference verified claim indices')
    editorial = article.get('editorial')
    if editorial is not None:
        try:
            for field in [editorial['opinion'], editorial['experiment']['environment'], editorial['experiment']['result']]:
                if any(not isinstance(field[lang], str) or len(field[lang]) > 2000 for lang in ('en', 'ko')):
                    errors.append('invalid human editorial text')
            experiment = editorial['experiment']
            if experiment['status'] not in ('not_tested', 'tested'):
                errors.append('invalid experiment status')
            if experiment['status'] == 'tested':
                from urllib.parse import urlparse
                url = urlparse(experiment['reportUrl'])
                if url.scheme != 'https' or not url.hostname or url.port not in (None,443) or url.username or url.password or re.search(r'[\s<>\\]', experiment['reportUrl']):
                    errors.append('tested experiment requires an HTTPS report URL')
                if any(not experiment[field][lang].strip() for field in ('environment', 'result') for lang in ('en', 'ko')):
                    errors.append('tested experiment requires environment and result in both languages')
            elif experiment['reportUrl'] is not None:
                errors.append('untested experiment cannot claim a report URL')
        except (KeyError, TypeError, ValueError, AttributeError):
            errors.append('invalid human editorial metadata')
    return errors
