#!/usr/bin/env python3
"""Read public crawl-access signals without authentication, JavaScript or indexing requests."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from check_seo import Head, LANGUAGES
from search_console import SITE
from search_engines import targets, sitemap, destination, save_new
from search_growth import live_signals, Signals

BOTS = ('googlebot', 'bingbot')


def directives(values):
    """Observe scoped index restrictions; unsupported conditional rules require review."""
    result = {bot: set() for bot in BOTS}
    unknown = False
    for value in values:
        scope = '*'
        for item in value.lower().split(','):
            item = item.strip()
            if ':' in item:
                prefix, rest = item.split(':', 1)
                prefix = prefix.strip()
                if prefix in ('max-snippet', 'max-image-preview', 'max-video-preview'):
                    continue
                if prefix == 'unavailable_after':
                    unknown = True
                    continue
                if re.fullmatch(r'[a-z][a-z0-9_-]*', prefix):
                    scope, item = prefix, rest.strip()
                else:
                    unknown = True
                    continue
            for token in item.split():
                if token in ('noindex', 'none'):
                    for bot in BOTS:
                        if scope in ('*', bot):
                            result[bot].add('noindex')
                elif token not in ('all', 'index', 'follow', 'nofollow', 'noarchive', 'nocache', 'nosnippet', 'noimageindex', 'notranslate'):
                    unknown = True
    return {'noindex': {bot: 'noindex' in result[bot] for bot in BOTS}, 'requiresReview': unknown}


def header_values(response):
    raw = getattr(getattr(response, 'raw', None), 'headers', None)
    if raw is not None and hasattr(raw, 'getlist'):
        return raw.getlist('X-Robots-Tag')
    value = response.headers.get('X-Robots-Tag')
    return [value] if value else []


def robots_policy(response):
    """Recognize this site's simple explicit allow-all policy, not arbitrary REP syntax."""
    if response is None or response.status_code != 200:
        return {'httpStatus': getattr(response, 'status_code', None), 'state': 'unavailable', 'explicitAllowAll': None}
    rules = []
    for line in response.text.lstrip('\ufeff').splitlines():
        line = line.split('#', 1)[0].strip()
        if line and ':' in line:
            key, value = line.split(':', 1)
            rules.append((key.strip().lower(), value.strip()))
        elif line:
            rules.append(('unrecognized', line))
    expected = [('user-agent', '*'), ('allow', '/'), ('sitemap', SITE + 'sitemap.xml')]
    matches = rules == expected and response.headers.get('Content-Type', '').split(';')[0].strip().lower() == 'text/plain'
    return {'httpStatus': 200, 'state': 'expected-explicit-allow-all' if matches else 'requires-review',
            'explicitAllowAll': True if matches else None}


def page_observation(target, response):
    signals = live_signals(target, lambda *a, **k: response)
    page = Head(); page.feed(response.text)
    meta = Signals(); meta.feed(response.text)
    headers = directives(header_values(response))
    # Existing HTML observation combines robots/googlebot/bingbot restrictions;
    # body meta directives are included because Google also respects them there.
    meta_conditional = any(directives([value])['requiresReview'] for value in meta.robots)
    content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
    issues, unknown = [], []
    if not signals['matchesExpectedStaticRoute']:
        issues.append('http-or-canonical-or-refresh-mismatch')
    if signals['noindex']:
        issues.append('html-noindex')
    if any(headers['noindex'].values()):
        issues.append('http-header-noindex')
    if headers['requiresReview'] or meta_conditional:
        unknown.append('conditional-or-unrecognized-index-directive')
    if not content_type:
        unknown.append('missing-content-type')
    elif content_type != 'text/html':
        issues.append('not-html-content-type')
    if page.language != target['language']:
        issues.append('html-language-mismatch')
    if target['kind'] != 'legacy':
        if len(dict(page.alternates)) != len(page.alternates):
            issues.append('duplicate-hreflang')
        mapping = dict(page.alternates)
        if mapping.get(target['language']) != target['url']:
            issues.append('missing-self-hreflang')
        if 'en' in mapping and mapping.get('x-default') != mapping['en']:
            issues.append('x-default-must-match-english')
    return {**target, 'httpStatus': response.status_code, 'contentType': content_type or None,
            'signals': signals, 'headerIndexDirectives': headers, 'language': page.language,
            'alternates': page.alternates, 'issues': issues, 'unknown': unknown}


def collect(selected, get):
    def cluster(row):
        if row['kind'] in ('home', 'archive'):
            return (row['kind'],)
        return (row.get('group'), row.get('key') or urlsplit(row['url']).path.rstrip('/').rsplit('/', 1)[-1])
    expected_alternates = {}
    for row in selected:
        for key in ('url', 'expectedCanonical'):
            url = urlsplit(row[key])
            if url.scheme != 'https' or url.netloc != 'youdozi.github.io' or url.query or url.fragment:
                raise ValueError('Only clean production site URLs may be requested')
        if row['kind'] != 'legacy':
            group = expected_alternates.setdefault(cluster(row), {})
            if row['language'] in group:
                raise ValueError('Duplicate language in a public edition group')
            group[row['language']] = row['url']
    if len({row['url'] for row in selected}) != len(selected):
        raise ValueError('Duplicate selected URLs')
    def read(url):
        return get(url, timeout=30, allow_redirects=False, headers={'Cache-Control': 'no-cache', 'User-Agent': 'youdozi-blog-crawl-audit/1.0'})
    try:
        robots = robots_policy(read(SITE + 'robots.txt'))
    except Exception:
        robots = robots_policy(None)
    public_map = sitemap(lambda url, **kwargs: read(url))
    def observe(target):
        try:
            row = page_observation(target, read(target['url']))
        except Exception as error:
            row = {**target, 'httpStatus': None, 'alternates': [], 'issues': [], 'unknown': ['response-unavailable:' + type(error).__name__]}
        if robots['explicitAllowAll'] is not True:
            row['unknown'].append('robots-policy-unconfirmed')
        if 'urls' not in public_map:
            row['unknown'].append('sitemap-unavailable')
        elif (target['url'] in public_map['urls']) != (target['kind'] != 'legacy'):
            row['issues'].append('sitemap-membership-mismatch')
        return row
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(observe, selected))
    pages = {row['url']: row for row in rows}
    base_states = {row['url']: 'issue' if row['issues'] else 'unknown' if row['unknown'] else 'checks-passed' for row in rows}
    for row in rows:
        if row['kind'] == 'legacy':
            continue
        mapping = dict(row['alternates'])
        if any(mapping.get(language) != url for language, url in expected_alternates[cluster(row)].items()):
            row['issues'].append('published-edition-hreflang-missing-or-wrong')
        for language, url in row['alternates']:
            if language not in LANGUAGES | {'x-default'}:
                row['issues'].append('unsupported-hreflang')
            target = pages.get(url)
            if target is None or target['httpStatus'] is None:
                row['unknown'].append('alternate-not-observed:' + url)
            elif base_states[url] == 'issue' or target['kind'] == 'legacy' or target['httpStatus'] != 200 or target.get('signals', {}).get('canonical') != [url]:
                row['issues'].append('alternate-not-final-self-canonical:' + url)
            elif base_states[url] == 'unknown':
                row['unknown'].append('alternate-access-unconfirmed:' + url)
            elif language != 'x-default' and (target['language'] != language or dict(target['alternates']).get(row['language']) != row['url']):
                row['issues'].append('alternate-language-or-reciprocity-mismatch:' + url)
        row['issues'] = sorted(set(row['issues'])); row['unknown'] = sorted(set(row['unknown']))
    for row in rows:
        row['state'] = 'issue' if row['issues'] else 'unknown' if row['unknown'] else 'checks-passed'
    return {'schemaVersion': 1, 'site': SITE, 'checkedAt': datetime.now(timezone.utc).isoformat(),
            'robots': robots, 'sitemap': public_map, 'urls': rows, 'summary': dict(Counter(row['state'] for row in rows)),
            'limits': ['Ordinary HTTP requests, not authenticated Googlebot/Bingbot requests or proof of indexing/rankings.',
                       'No JavaScript, Google/Bing API, settings, publishing or submission requests.',
                       'robots.txt only recognizes the existing explicit allow-all policy; other rules/statuses require review.',
                       'Conditional/unsupported index directives and unobserved alternates remain unknown. No additional alternate URLs are fetched.']}


def format_report(report):
    if report.get('schemaVersion') != 1 or report.get('site') != SITE:
        raise ValueError('Expected this site crawl-access snapshot')
    lines = ['공개 URL 크롤링 접근성 관측: ' + report['checkedAt'],
             'robots.txt: ' + report['robots']['state'], '검사 결과: ' + json.dumps(report['summary'], ensure_ascii=False),
             '일반 HTTP 관측이며 실제 검색봇 방문·색인·순위의 증거가 아닙니다.']
    for row in report['urls']:
        if row['state'] != 'checks-passed':
            lines.append(row['url'] + ' · ' + row['state'] + ' · ' + ', '.join(row['issues'] + row['unknown']))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true'); parser.add_argument('--report', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.report:
            if args.live or args.output:
                raise ValueError('Report cannot query or write')
            print(format_report(json.loads(args.report.expanduser().read_text())))
            return 0
        selected = targets()
        if not args.live:
            if args.output:
                raise ValueError('Preview cannot write')
            print(json.dumps({'mode': 'preview', 'urls': len(selected), 'httpRequests': len(selected) + 2, 'authentication': False}))
            return 0
        if not args.output:
            raise ValueError('Live collection requires a new private output path')
        output = destination(args.output)
        import requests
        report = collect(selected, requests.get)
        save_new(output, report)
        print(format_report(report)); print('비공개 결과: ' + str(output))
        return 0 if report['summary'].get('checks-passed', 0) == len(selected) else 2
    except Exception as error:
        print('Crawl access audit failed (' + type(error).__name__ + '); response bodies omitted.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
