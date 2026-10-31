#!/usr/bin/env python3
"""Notify IndexNow about deployed canonical pages. Preview is the default."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SITE = 'https://youdozi.github.io'
ENDPOINT = 'https://api.indexnow.org/indexnow'
KEY_PATH = 'indexnow-key.txt'
LANGUAGES = ('en', 'ko', 'zh-CN', 'ja', 'de', 'fr', 'ru', 'es')


def public_url(value):
    if not isinstance(value, str) or not value:
        raise ValueError('Expected a nonempty canonical URL')
    parsed = urlsplit(value)
    path = unquote(parsed.path)
    if (parsed.scheme != 'https' or parsed.netloc != 'youdozi.github.io'
            or parsed.query or parsed.fragment or '\\' in path
            or any(ord(c) < 32 for c in path)
            or any(p in ('.', '..') for p in path.split('/'))):
        raise ValueError('Expected a canonical URL on the production site')
    pattern = r'/(' + '|'.join(LANGUAGES) + r')/(?:|(?:posts|digest|categories|tags|archive|guides)/|(?:posts|digest|categories)/[^/]+/)'
    if not re.fullmatch(pattern + r'|/(?:en|ko)/about/', path):
        raise ValueError('URL is outside published language routes')
    return value


class PageSignals(HTMLParser):
    """Hash article content and search metadata, excluding site chrome."""
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False
        self.refresh = False
        self.description = ''
        self.title = []
        self.main = []
        self.in_title = False
        self.main_depth = 0
        self.main_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta':
            if attrs.get('name', '').lower() in ('robots', 'googlebot', 'bingbot'):
                self.noindex |= bool(re.search(r'\b(noindex|none)\b', attrs.get('content', ''), re.I))
            if attrs.get('name', '').lower() == 'description':
                self.description = attrs.get('content', '')
            self.refresh |= attrs.get('http-equiv', '').lower() == 'refresh'
        if tag == 'title':
            self.in_title = True
        if tag == 'main':
            self.main_depth += 1
            self.main_count += 1
        if self.main_depth:
            self.main.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.main_depth:
            self.main.append(f'</{tag}>')
        if tag == 'main':
            self.main_depth -= 1
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.main_depth:
            self.main.append(data)


def build_manifest(dist):
    dist = Path(dist).resolve()
    tree = ET.fromstring((dist / 'sitemap.xml').read_bytes())
    if tree.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
        raise ValueError('Expected a sitemap urlset')
    urls = [e.text for e in tree.findall('{*}url/{*}loc')]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError('Sitemap must contain unique nonempty URLs')
    pages = {}
    for url in urls:
        public_url(url)
        page = (dist / unquote(urlsplit(url).path).lstrip('/') / 'index.html').resolve()
        if not page.is_relative_to(dist):
            raise ValueError('Page escapes build directory')
        signals = PageSignals()
        signals.feed(page.read_text(encoding='utf-8'))
        if signals.canonicals != [url] or signals.noindex or signals.refresh or signals.main_count != 1:
            raise ValueError('Sitemap contains a noncanonical, excluded, redirect or invalid page')
        content = json.dumps([''.join(signals.title), signals.description, ''.join(signals.main)], ensure_ascii=False)
        pages[url] = hashlib.sha256(content.encode()).hexdigest()
    return {'schemaVersion': 1, 'site': SITE, 'pages': dict(sorted(pages.items()))}


def validate_manifest(data):
    if (not isinstance(data, dict) or data.get('schemaVersion') != 1
            or data.get('site') != SITE or not isinstance(data.get('pages'), dict)):
        raise ValueError('Invalid IndexNow state')
    for url, digest in data['pages'].items():
        public_url(url)
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('Invalid page fingerprint')
    return data


def changed_urls(previous, current):
    validate_manifest(current)
    previous = validate_manifest(previous) if previous is not None else {'pages': {}}
    return sorted(url for url in set(previous['pages']) | set(current['pages'])
                  if previous['pages'].get(url) != current['pages'].get(url))


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.indexnow-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def http(request):
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.read(), response.geturl()
    except HTTPError as error:
        return error.code, b'', request.full_url
    except URLError:
        raise RuntimeError('IndexNow network or TLS request failed') from None


def submit_changes(urls, key, fetch=http):
    if not re.fullmatch('[a-f0-9]{32}', key):
        raise ValueError('Expected the generated public verification key')
    if len(urls) > 10000 or len(urls) != len(set(urls)):
        raise ValueError('Expected at most 10000 unique URLs')
    for url in urls:
        public_url(url)
    if not urls:
        return None
    # A completed Pages deployment can precede propagation of the new key file.
    key_url = SITE + '/' + KEY_PATH
    for attempt in range(6):
        status, body, location = fetch(Request(key_url, headers={'Cache-Control': 'no-cache'}))
        if status == 200 and location == key_url and body.decode('utf-8').strip() == key:
            break
        if attempt == 5:
            raise RuntimeError('Deployed IndexNow verification key is unavailable or mismatched')
        time.sleep(5)
    payload = {'host': 'youdozi.github.io', 'key': key, 'keyLocation': key_url, 'urlList': urls}
    status, _, location = fetch(Request(ENDPOINT, data=json.dumps(payload).encode(),
                                        headers={'Content-Type': 'application/json'}, method='POST'))
    if status not in (200, 202) or location != ENDPOINT:
        raise RuntimeError(f'IndexNow rejected notification: HTTP {status}')
    return status


def run(dist, state, submit=False, fetch=http):
    current = build_manifest(dist)
    path = Path(state)
    previous = json.loads(path.read_text()) if path.is_file() else None
    urls = changed_urls(previous, current)
    result = {'mode': 'submit' if submit else 'preview', 'publishedPages': len(current['pages']),
              'changedUrls': len(urls), 'firstSubmission': previous is None}
    if submit:
        key = (Path(dist) / KEY_PATH).read_text().strip()
        result['httpStatus'] = submit_changes(urls, key, fetch)
        # Advance only after acknowledgement; failed notifications remain pending.
        atomic_json(path, current)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    parser.add_argument('--state', type=Path, default=Path('.pipeline/indexnow-state.json'))
    parser.add_argument('--submit', action='store_true', help='Send notifications and update saved state')
    args = parser.parse_args()
    try:
        result = run(args.dist, args.state, args.submit)
    except (OSError, ValueError, RuntimeError, ET.ParseError) as error:
        print(f'[error] {error}')
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.submit:
        print('Notification acceptance does not guarantee crawling, indexing or ranking.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
