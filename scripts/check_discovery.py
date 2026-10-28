#!/usr/bin/env python3
"""Check same-language HTML discovery paths and empty destinations offline."""
import argparse
from collections import deque
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit, quote
import xml.etree.ElementTree as ET

from check_seo import Head, SITE, LANGUAGES, emitted_url, SM


class DiscoveryPage(Head):
    def __init__(self):
        super().__init__()
        self.links = []
        self.empty = False

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        self.empty |= 'empty' in a.get('class', '').split()


def destination(source, href):
    target = urlsplit(urljoin(source, href))
    if target.scheme not in ('http', 'https') or target.netloc != 'youdozi.github.io':
        return None
    return target.scheme + '://' + target.netloc + quote(target.path, safe="/%:@!$&'()*+,;=-._~")


def inspect(root):
    root = Path(root)
    pages = {}
    for file in root.rglob('*.html'):
        page = DiscoveryPage()
        page.feed(file.read_text(encoding='utf-8'))
        if page.language in LANGUAGES:
            pages[emitted_url(root, file)] = page
    public = {url: p for url, p in pages.items() if not p.noindex and not p.refresh and p.canonicals == [url]}
    empty = {url for url, page in pages.items() if page.noindex and page.empty}
    graph = {url: {destination(url, href) for href in page.links} for url, page in public.items()}
    empty_links = sorted((url, target) for url, targets in graph.items() for target in targets if target in empty)
    sitemap = ET.parse(root / 'sitemap.xml').getroot()
    if sitemap.tag != SM + 'urlset':
        raise ValueError('Expected a sitemap urlset')
    urls = [node.findtext(SM + 'loc', default='') for node in sitemap.findall(SM + 'url')]
    errors = []
    if not urls or len(urls) != len(set(urls)):
        errors.append('Expected unique nonempty sitemap URLs')
    errors.extend(f'{url}: link leads to an empty noindex destination {target}' for url, target in empty_links)
    by_language = {}
    article_urls = {url for url in public if re.fullmatch(re.escape(SITE) + r'/[^/]+/(posts|digest)/[^/]+/', url)}
    for language in sorted({urlsplit(url).path.split('/')[1] for url in urls if url.startswith(SITE + '/')}):
        if language not in LANGUAGES:
            errors.append('Unsupported sitemap language: ' + language)
            continue
        home = SITE + '/' + language + '/'
        prefix = home
        distances = {home: 0} if home in public else {}
        queue = deque(distances)
        while queue:
            current = queue.popleft()
            for target in graph.get(current, set()):
                if target in public and target.startswith(prefix) and target not in distances:
                    distances[target] = distances[current] + 1
                    queue.append(target)
        expected = {url for url in urls if url.startswith(prefix)}
        missing = sorted(expected - distances.keys())
        errors.extend(url + ': sitemap URL not reachable from its own language home' for url in missing)
        articles = sorted(url for url in article_urls if url.startswith(prefix))
        too_deep = [url for url in articles if distances.get(url, float('inf')) > 2]
        errors.extend(url + ': article requires more than two HTML link steps from its language home' for url in too_deep)
        by_language[language] = {'sitemapURLs': len(expected), 'reachableSitemapURLs': len(expected) - len(missing),
                                 'articles': len(articles),
                                 'maxArticleLinkSteps': max((distances.get(url, -1) for url in articles), default=0)}
    return errors, {'publicPages': len(public), 'emptyDestinations': len(empty),
                    'emptyDestinationLinks': len(empty_links), 'sitemapURLs': len(urls),
                    'articles': len(article_urls), 'languages': by_language}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    args = parser.parse_args()
    try:
        errors, summary = inspect(args.dist)
    except (OSError, ValueError, ET.ParseError) as error:
        print('[error]', error)
        return 1
    for error in errors:
        print('[error]', error)
    if not errors:
        print('[ok] HTML discovery graph:', json.dumps(summary, sort_keys=True))
        print('[ok] Link steps measure static paths, not crawler visits, indexing or reading effort.')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
