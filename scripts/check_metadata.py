#!/usr/bin/env python3
"""Compare generated article JSON-LD, social tags and visible dates offline."""
import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import re

from check_seo import Head, SITE, emitted_url

LOCALES = json.loads((Path(__file__).resolve().parents[1] / 'src/lib/locales.json').read_text())['locales']


class Metadata(Head):
    def __init__(self):
        super().__init__()
        self.meta = defaultdict(list)
        self.jsonld = []
        self.script = None
        self.in_h1 = False
        self.h1 = []
        self.date_role = None
        self.dates = defaultdict(list)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        a = dict(attrs)
        if self.in_head and tag == 'meta':
            key = a.get('property') or a.get('name')
            if key:
                self.meta[key].append(a.get('content', ''))
        if self.in_head and tag == 'script' and a.get('type') == 'application/ld+json':
            self.script = []
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'span' and a.get('class') in ('publication-date', 'modification-date'):
            self.date_role = a['class']
        if tag == 'time' and self.date_role:
            self.dates[self.date_role].append(a.get('datetime'))

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)
        if self.in_h1:
            self.h1.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.jsonld.append(''.join(self.script))
            self.script = None
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'span':
            self.date_role = None
        super().handle_endtag(tag)


def validate(url, page):
    errors = []

    def equal(key, value):
        if page.meta.get(key, []) != [value]:
            errors.append(f'{key} must match its source exactly once')

    equal('og:url', url)
    for key in ('og:title', 'description', 'og:site_name'):
        if len(page.meta.get(key, [])) != 1 or not page.meta[key][0].strip():
            errors.append(f'{key} must occur once with a value')
    equal('twitter:title', next(iter(page.meta.get('og:title', [])), ''))
    description = next(iter(page.meta.get('description', [])), '')
    equal('og:description', description)
    equal('twitter:description', description)
    equal('og:locale', LOCALES[page.language]['ogLocale'])
    expected_locales = {LOCALES[lang]['ogLocale'] for lang, _ in page.alternates
                        if lang in LOCALES and lang != page.language}
    actual_locales = page.meta.get('og:locale:alternate', [])
    if set(actual_locales) != expected_locales or len(actual_locales) != len(set(actual_locales)):
        errors.append('og:locale:alternate must match actual alternate editions without duplicates')
    if len(page.jsonld) != 1:
        errors.append('Expected exactly one JSON-LD block')
        return errors
    try:
        graph = json.loads(page.jsonld[0])
        if not isinstance(graph, list) or any(not isinstance(item, dict) for item in graph):
            raise ValueError('Expected the site JSON-LD array')
    except (ValueError, TypeError):
        errors.append('JSON-LD must parse as the site graph')
        return errors
    articles = [item for item in graph if item.get('@type') == 'BlogPosting']
    is_article = bool(re.fullmatch(r'https://youdozi\.github\.io/[^/]+/(posts|digest)/[^/]+/', url))
    if len(articles) != int(is_article):
        errors.append('Article route must have one BlogPosting; other routes must have none')
        return errors
    if not is_article:
        equal('og:type', 'website')
        if any(key.startswith('article:') for key in page.meta):
            errors.append('Non-article route must not emit article metadata')
        return errors
    article = articles[0]
    equal('og:type', 'article')
    if article.get('url') != url or article.get('mainEntityOfPage') != url or article.get('@id') != url + '#article':
        errors.append('BlogPosting URL identity must match canonical')
    if article.get('inLanguage') != page.language:
        errors.append('BlogPosting language must match HTML')
    equal('og:title', article.get('headline'))
    if article.get('headline') != ''.join(page.h1).strip():
        errors.append('BlogPosting headline must match the visible h1')
    if article.get('description') != description:
        errors.append('BlogPosting description must match description tags')
    published, modified = article.get('datePublished'), article.get('dateModified')
    equal('article:published_time', published)
    equal('article:modified_time', modified)
    if page.dates['publication-date'] != [published]:
        errors.append('Visible publication date must match JSON-LD')
    try:
        start, end = [datetime.fromisoformat(value.replace('Z', '+00:00')) for value in (published, modified)]
        if start.utcoffset() is None or end.utcoffset() is None or end < start:
            raise ValueError('Expected ordered timezone-aware timestamps')
        if page.dates['modification-date'] != ([modified] if end > start else []):
            errors.append('Visible modification date must match the recorded change')
    except (ValueError, TypeError, AttributeError):
        errors.append('Article dates must be ordered timezone-aware timestamps')
    author = article.get('author')
    author_url = SITE + ('/ko/about/' if page.language == 'ko' else '/en/about/')
    if not isinstance(author, dict) or author.get('url') != author_url or author.get('@id') != SITE + '/#author':
        errors.append('BlogPosting author must match the site profile identity')
    equal('article:author', author_url)
    return errors


def audit(root):
    errors, checked, articles = [], 0, 0
    for file in Path(root).rglob('*.html'):
        page = Metadata()
        page.feed(file.read_text(encoding='utf-8'))
        path = '/' + file.relative_to(root).as_posix()
        url = emitted_url(Path(root), file)
        if page.language not in LOCALES or page.noindex or page.refresh or page.canonicals != [url]:
            continue
        checked += 1
        articles += bool(re.fullmatch(r'https://youdozi\.github\.io/[^/]+/(posts|digest)/[^/]+/', url))
        errors.extend(f'{path}: {error}' for error in validate(url, page))
    if not checked:
        errors.append('No eligible pages found for metadata validation')
    return errors, {'pages': checked, 'articles': articles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    try:
        errors, counts = audit(args.dist)
    except OSError as error:
        print('[error]', error)
        return 1
    for error in errors:
        print('[error]', error)
    if not errors:
        print('[ok] JSON-LD/social/visible metadata agree:', json.dumps(counts, sort_keys=True))
        print('[ok] Static metadata checks do not measure search rankings or platform previews.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
