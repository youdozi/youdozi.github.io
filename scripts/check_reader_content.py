#!/usr/bin/env python3
"""Reject known internal editorial material in public articles, feeds and search data."""
from technical_publications import technical_records
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
INTERNAL_KEYS = ('archive', 'notice', 'reviewed', 'renewed', 'followUp', 'noFollowUp',
                 'reviewFocus', 'editorial', 'evidence', 'context')
INTERNAL_FIELDS = frozenset(('reviewFocus', 'renewalFocus', 'review', 'editorial', 'reviewedAt', 'reviewScope'))
BLOCKS = frozenset(('p', 'div', 'span', 'li', 'dt', 'summary', 'strong', 'aside', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))
SKIP = frozenset(('pre', 'code', 'blockquote', 'script', 'style', 'template'))
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'))


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def policy(base=BASE):
    ui = json.loads((base / 'src/lib/archive-ui.json').read_text())
    labels = {normalize(edition[key]) for edition in ui.values() for key in INTERNAL_KEYS}
    labels.update(map(normalize, ('기존 아카이브 글', '검토/보강', '활용 가이드', '편집 제안',
                                 '후보 검토 카드', 'Candidate review card')))
    advice = {}
    for path in (base / 'src/content/renewals').glob('*.json'):
        source = json.loads(path.read_text())
        for language, text in source['reviewFocus'].items():
            advice[f"/{language}/digest/{source['slug']}/"] = text
    languages = {'en', 'ko'}
    for path in (base / 'src/content/translations').glob('*.json'):
        translation = json.loads(path.read_text())
        source = json.loads((base / f"src/content/renewals/{translation['renewalId']}.json").read_text())
        language = translation['language']; languages.add(language)
        advice[f"/{language}/digest/{source['slug']}/"] = translation['reviewFocus']
    languages.update(record['language'] for record in technical_records(base).values())
    return labels, advice, languages


def label_violation(text, labels):
    text = normalize(text)
    if text in labels or re.sub(r'\s+', '', text) in ('편집제안', '검토/보강', '기존아카이브글', '활용가이드'):
        return True
    return bool(re.match(r'^(?:검토\s*기록|검증 및 보강|검토\s*/\s*보강|검토\s*시점\s*후속\s*확인)(?:\s*[—–:：-].*)?$', text)
                or re.match(r'^(?:검토\s*초점(?:\s*[·:：—–-]|$)|리뉴얼\s*검토일\s*[:：]|확인할 점\(자동 분류\)\s*[:：])', text))


def advice_violation(text, advice):
    text, advice = normalize(text), normalize(advice)
    return bool(advice and (text == advice or len(advice) >= 24 and advice in text))


class ReaderHTML(HTMLParser):
    def __init__(self, labels, fragment=False):
        super().__init__()
        self.labels, self.fragment = labels, fragment
        self.stack, self.text, self.errors = [], [], set()
        self.article = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        article = tag == 'article' and 'article' in attrs.get('class', '').split()
        self.article |= article
        active = self.fragment or article or parent.get('active', False)
        skip = tag in SKIP or parent.get('skip', False)
        if not skip and ('data-candidate-review' in attrs or 'data-review-fields' in attrs
                         or 'candidate-review' in attrs.get('class', '').split()):
            self.errors.add('internal-review-markup')
        if tag not in VOID:
            self.stack.append({'tag': tag, 'active': active, 'skip': skip, 'parts': []})

    def handle_data(self, data):
        if self.fragment and not self.stack:
            self.text.append(data)
            if label_violation(data, self.labels): self.errors.add('internal-editorial-label')
        if self.stack and self.stack[-1]['active'] and not self.stack[-1]['skip']:
            self.text.append(data)
            for frame in self.stack:
                if frame['active'] and not frame['skip'] and frame['tag'] in BLOCKS:
                    frame['parts'].append(data)

    def handle_endtag(self, tag):
        index = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i]['tag'] == tag), None)
        if index is None: return
        for frame in self.stack[index:]:
            if frame['active'] and not frame['skip'] and frame['tag'] in BLOCKS:
                if label_violation(''.join(frame['parts']), self.labels):
                    self.errors.add('internal-editorial-label')
        del self.stack[index:]

    def close(self):
        super().close()
        for frame in self.stack:
            if frame['active'] and not frame['skip'] and frame['tag'] in BLOCKS:
                if label_violation(''.join(frame['parts']), self.labels):
                    self.errors.add('internal-editorial-label')
        self.stack.clear()


def html_errors(content, labels, advice='', fragment=False):
    page = ReaderHTML(labels, fragment)
    page.feed(content); page.close()
    errors = set(page.errors)
    if not fragment and not page.article: errors.add('missing-public-article')
    if advice_violation(' '.join(page.text), advice): errors.add('internal-review-advice')
    return errors


def text_errors(content, labels, advice=''):
    lines, fence = [], None
    for line in content.splitlines():
        opening = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*', line): fence = None
            continue
        if opening:
            fence = (opening[1][0], len(opening[1])); continue
        if line.lstrip().startswith('>'): continue
        lines.append(re.sub(r'^(?:#{1,6}\s+|[-*+]\s+)', '', line).replace('**', '').strip())
    errors = set()
    if any(label_violation(line, labels) for line in lines): errors.add('internal-editorial-label')
    if advice_violation(' '.join(lines), advice): errors.add('internal-review-advice')
    return errors


def article_file(root, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not url.startswith('/'):
        raise ValueError('Expected relative public article URL')
    path = root / unquote(parsed.path).lstrip('/') / 'index.html'
    if not path.resolve().is_relative_to(root.resolve()): raise ValueError('Article outside output')
    return path


def check(root, labels, advice, languages):
    errors, seen, feed_count = [], set(), 0
    def record(path, rules):
        errors.extend(f'{path.relative_to(root)}: {rule}' for rule in sorted(rules))
    for language in sorted(languages):
        index = root / language / 'search-index.json'
        try:
            rows = json.loads(index.read_text())
            if not isinstance(rows, list) or not rows: raise ValueError('Empty public index')
            for row in rows:
                url = row['url']
                if not url.startswith('/' + language + '/') or url in seen: raise ValueError('Invalid article identity')
                seen.add(url)
                focus = advice.get(url, '')
                if INTERNAL_FIELDS & row.keys():
                    record(index, {'internal-review-metadata'})
                record(index, set().union(*(text_errors(row[key], labels, focus) for key in ('title', 'description', 'content'))))
                path = article_file(root, url)
                record(path, html_errors(path.read_text(), labels, focus))
        except (OSError, ValueError, TypeError, KeyError):
            record(index, {'invalid-public-index-or-article'})
    for path in [root / 'feed.xml', *(root / lang / 'feed.xml' for lang in sorted(languages))]:
        try:
            items = ET.fromstring(path.read_text()).findall('./channel/item')
            if not items: raise ValueError('Empty public feed')
            for item in items:
                url = urlsplit(item.findtext('link', '')).path
                if url not in seen: raise ValueError('Feed article missing from public index')
                focus = advice.get(url, '')
                if any(element.tag.rsplit('}', 1)[-1] in INTERNAL_FIELDS for element in item.iter()):
                    record(path, {'internal-review-metadata'})
                for tag in ('title', 'description'):
                    value = item.findtext(tag, '')
                    record(path, text_errors(value, labels, focus) | html_errors(value, labels, focus, fragment=True))
                for content in item.findall('{http://purl.org/rss/1.0/modules/content/}encoded'):
                    record(path, html_errors(content.text or '', labels, focus, fragment=True))
            feed_count += 1
        except (OSError, ValueError, TypeError, ET.ParseError):
            record(path, {'invalid-public-feed'})
    return sorted(set(errors)), {'articles': len(seen), 'searchIndexes': len(languages), 'feeds': feed_count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    errors, counts = check(args.dist, *policy())
    for error in errors: print('[error]', error)  # Rule names only; never dump private review advice.
    if not errors: print('[ok] Public reader content excludes known editorial labels, cards and review advice:', json.dumps(counts))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
