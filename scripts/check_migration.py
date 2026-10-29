#!/usr/bin/env python3
"""Check built migration routes and their final destinations without network access."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

from check_seo import Head, SITE, emitted_url

REGISTRY = Path(__file__).resolve().parents[1] / 'content/seo/core-articles.json'


class MigrationPage(Head):
    def __init__(self):
        super().__init__()
        self.refreshes, self.anchors = [], []

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        if tag == 'meta' and self.in_head and values.get('http-equiv', '').lower() == 'refresh':
            self.refreshes.append(values.get('content', ''))
        if tag == 'meta' and self.in_head and values.get('name', '').lower() in ('robots', 'googlebot', 'bingbot'):
            self.noindex |= bool(re.search(r'\b(noindex|none)\b', values.get('content', '').lower()))
        if tag == 'a' and values.get('href'):
            self.anchors.append(values['href'])


def audit(root, registry=None):
    root = Path(root)
    registry = registry if registry is not None else json.loads(REGISTRY.read_text())
    pages = {}
    for file in root.rglob('*.html'):
        page = MigrationPage()
        page.feed(file.read_text(encoding='utf-8'))
        if page.language:
            pages[emitted_url(root, file)] = page
    sitemap = {n.text for n in ET.parse(root / 'sitemap.xml').getroot().iter() if n.tag.endswith('}loc')}
    redirects = {url: page for url, page in pages.items() if page.refresh}
    errors, counts = [], Counter()
    for url, page in redirects.items():
        counts['redirects'] += 1
        match = re.fullmatch(r'0;url=(/[^?#]*)', page.refreshes[0]) if len(page.refreshes) == 1 else None
        if not match or match[1].startswith('//'):
            errors.append(url + ': expected one immediate local meta refresh')
            continue
        target_url = SITE + match[1]
        target = pages.get(target_url)
        if target is None or target.refresh or target.canonicals != [target_url] or target_url == url:
            errors.append(url + ': destination must exist and be final/self-canonical, without a redirect chain')
            continue
        if page.canonicals != [target_url] or target_url not in [urljoin(url, href) for href in page.anchors]:
            errors.append(url + ': canonical and visible continuation link must match the destination')
        if url in sitemap:
            errors.append(url + ': redirect must not appear in sitemap')
        if page.language != target.language:
            errors.append(url + ': redirect language must match its destination')
        article_move = bool(re.fullmatch(r'/(en|ko)/posts/[^/]+/', urlsplit(target_url).path)) and not target.noindex
        if article_move:
            counts['articleMoves'] += 1
            if page.noindex or target_url not in sitemap:
                errors.append(url + ': article move must avoid noindex and lead to a sitemap article')
        else:
            counts['navigationOrExcludedMoves'] += 1
            if not page.noindex:
                errors.append(url + ': navigation/example redirects must remain noindex')
    for url, page in pages.items():
        if page.refresh or page.noindex or page.canonicals != [url]:
            continue
        for href in page.anchors:
            parsed = urlsplit(urljoin(url, href))
            target = parsed._replace(query='', fragment='').geturl()
            if target in redirects:
                errors.append(url + ': public internal link still points to a redirect: ' + target)
    for article in registry['articles']:
        key = article['key']
        old_url = SITE + article['legacyPath']
        expected = SITE + '/ko/posts/' + key + '/'
        old = redirects.get(old_url)
        if old is None or old.canonicals != [expected] or old.refreshes != ['0;url=/ko/posts/' + key + '/']:
            errors.append(old_url + ': core legacy route must move to its registered Korean edition')
        for language in ('en', 'ko'):
            url = SITE + '/' + language + '/posts/' + key + '/'
            page = pages.get(url)
            if page is None or page.noindex or page.refresh or page.canonicals != [url] or url not in sitemap:
                errors.append(url + ': core edition must be a self-canonical sitemap article')
            counts['coreEditions'] += 1
    if not redirects:
        errors.append('No migration routes found')
    return sorted(set(errors)), dict(sorted(counts.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    errors, counts = audit(args.dist)
    for error in errors:
        print('[error] ' + error)
    if not errors:
        print('[ok] Migration signals and final destinations: ' + json.dumps(counts))
        print('[ok] Static migration checks do not confirm Google crawling, indexing or ranking changes.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
