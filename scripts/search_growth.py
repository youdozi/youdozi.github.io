#!/usr/bin/env python3
"""Read-only Search Console and live URL baseline for the selected technical guides."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from types import SimpleNamespace
from urllib.parse import quote
from zoneinfo import ZoneInfo

from search_console import CONFIG, SITE, access_token

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'content/seo/core-articles.json'


def targets(registry):
    articles = registry['articles']
    if registry.get('version') != 1 or len(articles) != 10:
        raise ValueError('Expected ten selected topics')
    result = []
    for article in articles:
        key, legacy = article['key'], article['legacyPath']
        if (not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9.-]+', key)
                or not re.fullmatch(r'/[a-z0-9-]+/[a-z0-9.-]+/', legacy)
                or any(part in ('.', '..') for part in legacy.split('/'))):
            raise ValueError('Invalid article path')
        for language in ('en', 'ko'):
            url = SITE + f'{language}/posts/{key}/'
            result.append({'key': key, 'language': language, 'url': url,
                           'expectedCanonical': url, 'kind': 'article'})
        result.append({'key': key, 'language': 'ko', 'url': SITE.rstrip('/') + legacy,
                       'expectedCanonical': SITE + f'ko/posts/{key}/', 'kind': 'legacy'})
    if len({r['url'] for r in result}) != 30:
        raise ValueError('Expected thirty unique URLs')
    return result


def windows(now):
    # Exclude the most recent three PT calendar days and explicitly request final data.
    end = now.astimezone(ZoneInfo('America/Los_Angeles')).date() - timedelta(days=3)
    start = end - timedelta(days=27)
    return {'current': (str(start), str(end)),
            'previous': (str(start - timedelta(days=28)), str(start - timedelta(days=1)))}


class Signals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals, self.robots, self.refresh = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'meta':
            if a.get('name', '').lower() in ('robots', 'googlebot', 'bingbot'):
                self.robots.append(a.get('content', '').lower())
            if a.get('http-equiv', '').lower() == 'refresh':
                self.refresh.append(a.get('content', ''))


def live_signals(target, get):
    response = get(target['url'], timeout=30, allow_redirects=False,
                   headers={'Cache-Control': 'no-cache'})
    signals = Signals()
    signals.feed(response.text)
    noindex = any(re.search(r'\b(noindex|none)\b', value) for value in signals.robots)
    refresh = ['0;url=' + target['expectedCanonical'].removeprefix(SITE.rstrip('/'))]
    if target['kind'] == 'legacy':
        valid = (response.status_code == 200 and signals.canonicals == [target['expectedCanonical']]
                 and signals.refresh == refresh)
    else:
        valid = (response.status_code == 200 and signals.canonicals == [target['url']]
                 and not noindex and not signals.refresh)
    return {'httpStatus': response.status_code, 'canonical': signals.canonicals,
            'noindex': bool(noindex), 'metaRefresh': signals.refresh,
            'matchesExpectedStaticRoute': valid,
            'serverRedirect': response.status_code in (301, 302, 303, 307, 308),
            'location': response.headers.get('Location')}


def google_post(token, url, payload):
    import requests
    response = requests.post(url, headers={'Authorization': 'Bearer ' + token},
                             json=payload, timeout=40, allow_redirects=False)
    if response.status_code != 200:
        # Do not echo response bodies, auth headers or request objects.
        return {'httpStatus': response.status_code, 'error': 'Google API request failed'}
    return {'httpStatus': 200, 'data': response.json()}


def collect(token, selected, now, post=google_post, get=None):
    if get is None:
        import requests
        get = requests.get
    report = {'checkedAt': now.isoformat(), 'site': SITE,
              'inspectionBasis': 'Google indexed version; not a live indexing test or indexing request',
              'searchAnalyticsBasis': 'final web data; PT dates; top rows, not exhaustive; omitted rows are not zero',
              'windows': windows(now), 'performance': {}, 'urls': []}
    endpoint = 'https://www.googleapis.com/webmasters/v3/sites/' + quote(SITE, safe='') + '/searchAnalytics/query'
    wanted = {t['url'] for t in selected}
    for period, (start, end) in report['windows'].items():
        params = {'startDate': start, 'endDate': end, 'dataState': 'final', 'type': 'web', 'rowLimit': 25000}
        output = {}
        for name, dimensions in [('totals', []), ('pages', ['page']), ('queries', ['page', 'query'])]:
            if period == 'previous' and name == 'queries':
                continue
            response = post(token, endpoint, {**params, 'dimensions': dimensions})
            if name != 'totals' and response.get('httpStatus') == 200:
                data = response['data']
                output[name] = {'httpStatus': 200,
                                'returnedRowsBeforeSelection': len(data.get('rows', [])),
                                'rows': [r for r in data.get('rows', []) if r['keys'][0] in wanted]}
            else:
                output[name] = response
        report['performance'][period] = output

    def check(target):
        result = dict(target)
        try:
            result['live'] = live_signals(target, get)
        except Exception as error:
            result['live'] = {'error': type(error).__name__}
        try:
            response = post(token, 'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
                            {'inspectionUrl': target['url'], 'siteUrl': SITE, 'languageCode': 'en-US'})
            result['inspection'] = {'httpStatus': response['httpStatus'],
                                    'indexStatus': response.get('data', {}).get('inspectionResult', {}).get('indexStatusResult', {})}
        except Exception as error:
            result['inspection'] = {'error': type(error).__name__}
        return result

    # Bound parallel API requests; never submit a sitemap or request indexing.
    with ThreadPoolExecutor(max_workers=2) as pool:
        report['urls'] = list(pool.map(check, selected))
    report['summary'] = summarize(report)
    return report


def index_status(inspection):
    state = inspection.get('indexStatus', {})
    return state if inspection.get('httpStatus') == 200 and isinstance(state, dict) and state.get('verdict') in ('PASS', 'FAIL', 'NEUTRAL', 'PARTIAL') else None


def summarize(report):
    result = {}
    for kind in ('article', 'legacy'):
        rows = [r for r in report['urls'] if r['kind'] == kind]
        successful = [r for r in rows if r['inspection'].get('httpStatus') == 200]
        known = [state for r in rows if (state := index_status(r['inspection'])) is not None]
        result[kind] = {'checked': len(rows),
                        'liveMatches': sum(bool(r['live'].get('matchesExpectedStaticRoute')) for r in rows),
                        'inspectionResponses': len(successful),
                        'googleKnown': sum(index_status(r['inspection']) is not None for r in rows),
                        'googleUnknownOrError': sum(index_status(r['inspection']) is None for r in rows),
                        'googlePass': sum(state.get('verdict') == 'PASS' for state in known),
                        'coverageStates': dict(Counter(state.get('coverageState', 'unspecified') for state in known))}
    return result


def compare(previous, current):
    before = {r['url']: r for r in previous['urls']}
    after = {r['url']: r for r in current['urls']}
    if previous.get('site') != SITE or current.get('site') != SITE or before.keys() != after.keys() or len(before) != len(previous['urls']) or len(after) != len(current['urls']):
        raise ValueError('Compare snapshots for the same property and URL set')
    result = {'previousCheckedAt': previous['checkedAt'], 'currentCheckedAt': current['checkedAt'],
              'newPass': [], 'noLongerPass': [], 'canonicalChanges': [], 'uncomparableUrls': [], 'canonicalUncomparableUrls': [],
              'performanceWindows': {'previousSnapshot': previous['windows']['current'],
                                     'currentSnapshot': current['windows']['current']},
              'note': 'Rolling windows can overlap; changes are observations, not causal effects.'}
    for url, row in after.items():
        old, new = index_status(before[url]['inspection']), index_status(row['inspection'])
        if old is None or new is None:
            result['uncomparableUrls'].append(url)
            continue
        if old.get('verdict') != 'PASS' and new.get('verdict') == 'PASS':
            result['newPass'].append(url)
        if old.get('verdict') == 'PASS' and new.get('verdict') != 'PASS':
            result['noLongerPass'].append(url)
        if not old.get('googleCanonical') or not new.get('googleCanonical'):
            result['canonicalUncomparableUrls'].append(url)
        elif old['googleCanonical'] != new['googleCanonical']:
            result['canonicalChanges'].append({'url': url, 'before': old.get('googleCanonical'),
                                                'after': new.get('googleCanonical')})
    return result


def format_report(report):
    """Summarize an existing private snapshot without API calls or query disclosure."""
    if report.get('site') != SITE:
        raise ValueError('Expected this site’s private snapshot')
    summary = summarize(report)
    lines = [f"조회 시각: {report['checkedAt']}",
             'Google 저장 색인 상태와 당시 공개 응답입니다. 실시간 색인 검사가 아닙니다.']
    for kind, label in [('article', '핵심 글'), ('legacy', '과거 주소')]:
        s = summary[kind]
        lines.append(f"{label}: {s['checked']}개 중 Google PASS {s['googlePass']}개 / 판정 미제공·오류 {s['googleUnknownOrError']}개 / API 응답 {s['inspectionResponses']}개 / 공개 경로 일치 {s['liveMatches']}개")
    for row in report['urls']:
        inspection = row['inspection']
        state = index_status(inspection) or {}
        status = state.get('coverageState', '상태 미제공·비교 불가') if inspection.get('httpStatus') == 200 else '조회 실패·비교 불가'
        lines.extend([f"\n{row['url']}", f"  색인: {status}",
                      f"  Google canonical: {state.get('googleCanonical', '미제공')}",
                      f"  마지막 크롤링: {state.get('lastCrawlTime', '미제공')}"])
    for period, label in [('current', '현재 28일'), ('previous', '직전 28일')]:
        totals = report['performance'][period]['totals']
        start, end = report['windows'][period]
        rows = totals.get('data', {}).get('rows', [])
        if totals.get('httpStatus') == 200 and rows:
            lines.append(f"\n{label} ({start}~{end}, PT): 사이트 전체 클릭 {rows[0]['clicks']}, 노출 {rows[0]['impressions']}")
        else:
            lines.append(f"\n{label} ({start}~{end}, PT): 합계 미제공 또는 조회 실패")
    comparison = report.get('comparison')
    if comparison:
        missing = len(comparison['canonicalUncomparableUrls']) if 'canonicalUncomparableUrls' in comparison else '미기록'
        lines.append(f"\n이전 조회 대비: PASS 전환 {len(comparison['newPass'])}, PASS 해제 {len(comparison['noLongerPass'])}, canonical 변경 {len(comparison['canonicalChanges'])}, 비교 불가 {len(comparison['uncomparableUrls'])}, canonical 미제공 {missing}")
    lines.append('\n미반환 행은 노출 0이 아니며, 겹치는 28일 구간과 변경 전후 차이는 인과효과를 증명하지 않습니다.')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Read Google APIs and public URLs; no indexing submission')
    parser.add_argument('--output', type=Path, help='Private snapshot path outside the repository')
    parser.add_argument('--previous', type=Path, help='Compare URL index states with an earlier private snapshot')
    parser.add_argument('--report', type=Path, help='Read an existing private snapshot as text; no network or file writes')
    args = parser.parse_args()
    try:
        if args.report:
            if args.live or args.output or args.previous:
                raise ValueError('Report mode cannot be combined with live collection options')
            print(format_report(json.loads(args.report.expanduser().read_text())))
            return 0
        selected = targets(json.loads(REGISTRY.read_text()))
        if not args.live:
            print(json.dumps({'mode': 'preview', 'articles': 20, 'legacyUrls': 10, 'urls': selected}, indent=2))
            return 0
        now = datetime.now(timezone.utc)
        from search_engines import destination, save_new
        output = destination(args.output or CONFIG / f'search-growth-{now:%Y%m%dT%H%M%SZ}.json')
        previous = json.loads(args.previous.expanduser().read_text()) if args.previous else None
        if previous is not None:
            # Validate the selected property and URL set before spending API quota.
            compare(previous, {'site': SITE, 'checkedAt': now.isoformat(), 'windows': windows(now),
                               'urls': [{**t, 'inspection': {}} for t in selected]})
        token = access_token(SimpleNamespace(client=None, token_file=CONFIG / 'token.json'))
        report = collect(token, selected, now)
        if previous is not None:
            report['comparison'] = compare(previous, report)
        save_new(output, report)
        print(json.dumps({'snapshot': str(output), 'windows': report['windows'], 'summary': report['summary']}, ensure_ascii=False, indent=2))
        failed = any(index_status(r['inspection']) is None or not r['live'].get('matchesExpectedStaticRoute') for r in report['urls'])
        failed |= any(v.get('httpStatus') != 200 for p in report['performance'].values() for v in p.values())
        return 1 if failed else 0
    except Exception as error:
        print(f'Search growth check failed ({type(error).__name__}). Credentials and response bodies are omitted.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
