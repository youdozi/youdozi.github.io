#!/usr/bin/env python3
"""Check emitted canonical, hreflang and sitemap relationships without network access."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

SITE = 'https://youdozi.github.io'
LANGUAGES = set(json.loads((Path(__file__).resolve().parents[1] / 'src/lib/locales.json').read_text())['locales'])
SM = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
XHTML = '{http://www.w3.org/1999/xhtml}'


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.language = None
        self.canonicals = []
        self.alternates = []
        self.noindex = False
        self.refresh = False
        self.in_head = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.language = a.get('lang')
        if tag == 'head':
            self.in_head = True
        if not self.in_head:
            return
        if tag == 'link':
            rel = a.get('rel', '').lower().split()
            if 'canonical' in rel:
                self.canonicals.append(a.get('href', ''))
            if 'alternate' in rel and 'hreflang' in a:
                self.alternates.append((a['hreflang'], a.get('href', '')))
        if tag == 'meta':
            if a.get('name', '').lower() in ('robots', 'googlebot', 'bingbot'):
                self.noindex |= bool(re.search(r'\b(noindex|none)\b', a.get('content', '').lower()))
            self.refresh |= a.get('http-equiv', '').lower() == 'refresh'

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False


def audit(root):
    root = Path(root)
    pages = {}
    for file in root.rglob('*.html'):
        head = Head()
        head.feed(file.read_text(encoding='utf-8'))
        # Ownership verification files contain text only, not public HTML pages.
        if head.language is None:
            continue
        path = '/' + file.relative_to(root).as_posix()
        if path.endswith('/index.html'):
            path = path[:-10]
        pages[SITE + path] = head
    errors = []
    eligible = {url: p for url, p in pages.items()
                if p.canonicals == [url] and not p.noindex and not p.refresh}

    def links(source, pairs):
        labels = [language for language, _ in pairs]
        if len(labels) != len(set(labels)):
            errors.append(f'{source}: duplicate hreflang')
        for language, href in pairs:
            if language not in LANGUAGES | {'x-default'}:
                errors.append(f'{source}: unsupported hreflang {language}')
            parsed = urlsplit(href)
            if parsed.scheme != 'https' or parsed.netloc != 'youdozi.github.io' or parsed.query or parsed.fragment:
                errors.append(f'{source}: alternate must be an absolute clean site URL: {href}')
            target = eligible.get(href)
            if target is None:
                errors.append(f'{source}: alternate is missing, redirected, noindex or not self-canonical: {href}')
            elif language != 'x-default' and target.language != language:
                errors.append(f'{source}: alternate language disagrees with target: {language} {href}')
        return dict(pairs)

    edges = 0
    clusters = set()
    for url, page in eligible.items():
        if not page.alternates:
            continue
        mapping = links(url, page.alternates)
        edges += len(page.alternates)
        clusters.add(tuple(sorted((lang, href) for lang, href in mapping.items() if lang != 'x-default')))
        if mapping.get(page.language) != url:
            errors.append(f'{url}: hreflang must include itself')
        if 'en' in mapping and mapping.get('x-default') != mapping['en']:
            errors.append(f'{url}: site policy requires the English alternate as x-default')
        if 'en' not in mapping and 'x-default' in mapping:
            errors.append(f'{url}: x-default requires an English counterpart under site policy')
        for language, href in mapping.items():
            if language == 'x-default' or href not in eligible:
                continue
            if dict(eligible[href].alternates).get(page.language) != url:
                errors.append(f'{url}: alternate does not link back: {href}')

    tree = ET.parse(root / 'sitemap.xml')
    if tree.getroot().tag != SM + 'urlset':
        raise ValueError('Expected a namespaced sitemap urlset')
    sitemap_urls = []
    for node in tree.getroot().findall(SM + 'url'):
        url = node.findtext(SM + 'loc', default='')
        sitemap_urls.append(url)
        if url not in eligible:
            errors.append(f'{url}: sitemap target is missing, redirected, noindex or not self-canonical')
        pairs = [(link.get('hreflang', ''), link.get('href', ''))
                 for link in node.findall(XHTML + 'link') if link.get('rel') == 'alternate']
        if pairs:
            mapping = links('sitemap ' + url, pairs)
            if url in pages and mapping != dict(pages[url].alternates):
                errors.append(f'{url}: sitemap and HTML hreflang disagree')
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append('Duplicate sitemap loc')
    if not sitemap_urls:
        errors.append('Sitemap must contain public URLs')
    return sorted(set(errors)), {
        'htmlPages': len(pages), 'selfCanonicalIndexablePages': len(eligible),
        'sitemapURLs': len(sitemap_urls), 'htmlAlternateEdges': edges,
        'alternateGroups': len(clusters),
        'sitemapByLanguage': dict(sorted(Counter(pages[url].language for url in sitemap_urls if url in pages).items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    try:
        errors, summary = audit(args.dist)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f'[error] SEO validation failed: {error}')
        return 1
    for error in errors:
        print('[error]', error)
    if not errors:
        print('[ok] Static SEO relationships:', json.dumps(summary, sort_keys=True))
        print('[ok] This validates generated metadata, not search-engine indexing or ranking.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
