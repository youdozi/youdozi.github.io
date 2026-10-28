#!/usr/bin/env python3
"""Read-only Google/Bing observations for public multilingual editions and core guides."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import search_growth as growth
from search_console import CONFIG, SITE, access_token

ROOT = Path(__file__).resolve().parents[1]
BING_ENDPOINT = 'https://ssl.bing.com/webmaster/api.svc/json/'
BING_READS = frozenset(('GetUserSites', 'GetFeeds', 'GetRankAndTrafficStats', 'GetUrlInfo'))


def targets(base=ROOT):
    registry = json.loads((base / 'content/seo/core-articles.json').read_text())
    result = growth.targets(registry)
    for row in result:
        row['group'] = 'core'
    locales = json.loads((base / 'src/lib/locales.json').read_text())
    languages = locales['locales']
    editions = set()
    for path in sorted((base / 'src/content/translations').glob('*.json')):
        record = json.loads(path.read_text())
        language, source_id = record['language'], record['renewalId']
        if language not in languages or not re.fullmatch('[a-f0-9]{16}', source_id):
            raise ValueError('Invalid public translation identity')
        source = json.loads((base / f'src/content/renewals/{source_id}.json').read_text())
        slug = source['slug']
        if not re.fullmatch('[a-z0-9.-]+', slug) or slug in ('.', '..'):
            raise ValueError('Invalid public source slug')
        for lang in ('en', 'ko', language):
            editions.add((lang, slug))
    for language, slug in sorted(editions):
        url = SITE + f'{language}/digest/{slug}/'
        result.append({'language': language, 'key': slug, 'url': url,
                       'expectedCanonical': url, 'kind': 'article', 'group': 'published-digest'})
    for language in languages:
        url = SITE + language + '/'
        result.append({'language': language, 'key': language, 'url': url,
                       'expectedCanonical': url, 'kind': 'home', 'group': 'home'})
    if len({r['url'] for r in result}) != len(result):
        raise ValueError('Duplicate observation URL')
    return result


def bing_get(key, method, params, get=None):
    if method not in BING_READS:
        raise ValueError('Only fixed read operations are allowed')
    if get is None:
        import requests
        get = requests.get
    try:
        response = get(BING_ENDPOINT + method, params={**params, 'apikey': key},
                       timeout=40, allow_redirects=False)
        if response.status_code != 200:
            failure = {'httpStatus': response.status_code, 'error': 'Bing API request failed'}
            try:
                code = response.json().get('ErrorCode')
                if type(code) is int and 0 <= code <= 16: failure['apiErrorCode'] = code
            except Exception:
                pass
            return failure
        data = response.json()
        if not isinstance(data, dict) or 'd' not in data:
            return {'httpStatus': 200, 'error': 'Unexpected Bing response'}
        return {'httpStatus': 200, 'data': data['d']}
    except Exception as error:
        # Request URLs can contain API keys. Never serialize an exception or request.
        return {'error': type(error).__name__}


def bing_date(value):
    match = re.fullmatch(r'/Date\((-?\d+)(?:[+-]\d{4})?\)/', value or '')
    if not match or int(match[1]) <= 0:
        return None
    try:
        return datetime.fromtimestamp(int(match[1]) / 1000, timezone.utc).isoformat()
    except (ValueError, OSError, OverflowError):
        return None


def bing_url(response):
    output = {k: v for k, v in response.items() if k in ('httpStatus', 'error', 'apiErrorCode')}
    data = response.get('data')
    if response.get('httpStatus') != 200 or response.get('error'):
        return output
    if not isinstance(data, dict) or not isinstance(data.get('Url'), str):
        output['error'] = 'Missing Bing URL observation'
        return output
    output.update({k: data.get(k) for k in ('Url', 'HttpStatus', 'DocumentSize', 'IsPage')})
    output['lastCrawledAt'] = bing_date(data.get('LastCrawledDate'))
    output['discoveredAt'] = bing_date(data.get('DiscoveryDate'))
    output['observation'] = 'crawl-record-present' if output['lastCrawledAt'] else 'no-recorded-crawl'
    output['indexingConfirmed'] = None  # GetUrlInfo has no index-membership field.
    return output


def sitemap(get):
    try:
        response = get(SITE + 'sitemap.xml', timeout=30, allow_redirects=False)
        if response.status_code != 200:
            return {'httpStatus': response.status_code, 'error': 'Public sitemap read failed'}
        urls = [n.text for n in ET.fromstring(response.text).findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        if not urls or any(not isinstance(u, str) or not u.startswith(SITE) for u in urls):
            return {'httpStatus': 200, 'error': 'Unexpected sitemap contents'}
        return {'httpStatus': 200, 'urls': urls, 'urlCount': len(urls)}
    except Exception as error:
        return {'error': type(error).__name__}


def collect(token, key, selected, now, post=growth.google_post, get=None, bing=bing_get):
    if get is None:
        import requests
        get = requests.get
    report = growth.collect(token, selected, now, post, get)
    report.update({'schemaVersion': 1, 'selection': 'Public translation files, their en/ko counterparts, core guides/legacy URLs, locale homes; no private drafts',
                   'bingBasis': 'GetUrlInfo is a crawl observation, not proof of index membership; empty performance rows are not zero exposure',
                   'publicSitemap': sitemap(get), 'bingSite': {}})
    for method in ('GetUserSites', 'GetFeeds', 'GetRankAndTrafficStats'):
        response = bing(key, method, {} if method == 'GetUserSites' else {'siteUrl': SITE})
        rows = response.get('data')
        clean = {k: v for k, v in response.items() if k in ('httpStatus', 'error', 'apiErrorCode')}
        if isinstance(rows, list):
            fields = {'GetUserSites': ('Url', 'IsVerified'), 'GetFeeds': ('Url', 'Status', 'UrlCount', 'LastCrawled', 'Submitted'),
                      'GetRankAndTrafficStats': ('Date', 'Clicks', 'Impressions')}[method]
            clean['rows'] = [{k: row[k] for k in fields if k in row} for row in rows if isinstance(row, dict)]
        elif not clean.get('error'):
            clean['error'] = 'Unexpected Bing site observation'
        report['bingSite'][method] = clean
    def observe(row):
        row['bing'] = bing_url(bing(key, 'GetUrlInfo', {'siteUrl': SITE, 'url': row['url']}))
        if row['bing'].get('Url') not in (None, row['url']):
            row['bing']['error'] = 'Bing URL identity differs'
        row['inPublicSitemap'] = (row['url'] in report['publicSitemap']['urls']) if 'urls' in report['publicSitemap'] else None
        return row
    # Stop the batch on a host/user throttle; don't keep spending its quota.
    throttle = next((r['apiErrorCode'] for r in report['bingSite'].values() if r.get('apiErrorCode') in (4, 5)), None)
    for row in report['urls']:
        if throttle is None:
            observe(row)
            if row['bing'].get('apiErrorCode') in (4, 5): throttle = row['bing']['apiErrorCode']
        else:
            row['bing'] = {'error': 'Deferred after Bing throttling', 'apiErrorCode': throttle, 'notRequested': True}
            row['inPublicSitemap'] = (row['url'] in report['publicSitemap']['urls']) if 'urls' in report['publicSitemap'] else None
    report['summary'] = summarize(report)
    return report


def retry_bing(previous, key, now, bing=bing_get, pause=time.sleep):
    if previous.get('site') != SITE or previous.get('schemaVersion') != 1:
        raise ValueError('Expected this site’s search-engine snapshot')
    report = deepcopy(previous)
    if 'comparison' in report:
        report['comparisonBeforeBingRetry'] = report.pop('comparison')
    failed = [r for r in report['urls'] if r['bing'].get('error') or r['bing'].get('httpStatus') != 200]
    if not failed:
        raise ValueError('No failed Bing URL observations to retry')
    allowed = {t['url'] for t in targets()}
    if any(r['url'] not in allowed for r in failed):
        raise ValueError('Retry URL is not in the current public selection')
    attempted = 0
    for index, row in enumerate(failed):
        row['bingPrevious'] = deepcopy(row['bing'])
        row['bing'] = bing_url(bing(key, 'GetUrlInfo', {'siteUrl': SITE, 'url': row['url']}))
        if row['bing'].get('Url') not in (None, row['url']):
            row['bing']['error'] = 'Bing URL identity differs'
        row['bing']['observedAt'] = now.isoformat()
        attempted += 1
        if row['bing'].get('apiErrorCode') in (4, 5): break
        if index + 1 < len(failed): pause(0.5)
    report['bingRecheckedAt'] = now.isoformat()
    report['bingRetriedURLCount'] = attempted
    report['bingRetryDeferredURLCount'] = len(failed) - attempted
    report['summary'] = summarize(report)
    return report


def google_state(row):
    inspection = row['inspection']
    state = inspection.get('indexStatus', {})
    return state if inspection.get('httpStatus') == 200 and state.get('verdict') in ('PASS', 'FAIL', 'NEUTRAL', 'PARTIAL') else None


def summarize(report):
    result = {}
    for language in sorted({r['language'] for r in report['urls']}):
        rows = [r for r in report['urls'] if r['language'] == language]
        known = [r for r in rows if google_state(r) is not None]
        bing_known = [r for r in rows if r['bing'].get('httpStatus') == 200 and not r['bing'].get('error')]
        result[language] = {'checked': len(rows), 'byGroup': dict(Counter(r['group'] for r in rows)),
                            'liveMatches': sum(bool(r['live'].get('matchesExpectedStaticRoute')) for r in rows),
                            'googleKnown': len(known), 'googlePass': sum(google_state(r)['verdict'] == 'PASS' for r in known),
                            'googleUnknownOrError': len(rows) - len(known),
                            'bingResponses': len(bing_known), 'bingErrors': len(rows) - len(bing_known), 'bingDeferred': sum(bool(r['bing'].get('notRequested')) for r in rows), 'bingCrawlRecords': sum(r['bing'].get('lastCrawledAt') is not None for r in bing_known),
                            'googleCanonicalDifferences': sum(bool(google_state(r).get('googleCanonical')) and google_state(r)['googleCanonical'] != r['expectedCanonical'] for r in known)}
    return result


def compare(previous, current):
    before = {r['url']: r for r in previous['urls']}
    after = {r['url']: r for r in current['urls']}
    if previous.get('site') != SITE or current.get('site') != SITE or before.keys() != after.keys():
        raise ValueError('Compare the same property and URL selection')
    result = {'previousCheckedAt': previous['checkedAt'], 'newGooglePass': [], 'noLongerGooglePass': [], 'googleUncomparable': [], 'newBingCrawlRecords': [],
              'note': 'Stored observations can lag; rolling performance windows overlap and do not prove causal effects.'}
    for url, row in after.items():
        old, new = google_state(before[url]), google_state(row)
        if old is None or new is None:
            result['googleUncomparable'].append(url)
        elif old['verdict'] != new['verdict']:
            if new['verdict'] == 'PASS': result['newGooglePass'].append(url)
            if old['verdict'] == 'PASS': result['noLongerGooglePass'].append(url)
        a, b = before[url]['bing'], row['bing']
        if a.get('observation') == 'no-recorded-crawl' and b.get('observation') == 'crawl-record-present' and not a.get('error') and not b.get('error'):
            result['newBingCrawlRecords'].append(url)
    return result


def format_report(report):
    if report.get('site') != SITE or report.get('schemaVersion') != 1:
        raise ValueError('Expected this site’s search-engine snapshot')
    lines = [f"조회 시각: {report['checkedAt']}", 'Google 저장 색인 상태 / Bing 크롤링 관측. API 오류와 미제공 값은 미색인·노출 0으로 처리하지 않습니다.']
    if report.get('bingRecheckedAt'): lines.append(f"Bing 실패 URL만 재조회한 시각: {report['bingRecheckedAt']} (Google·실적·공개 응답은 원래 조회 시점 유지)")
    for lang, item in summarize(report).items():
        lines.append(f"{lang}: URL {item['checked']} · 공개 응답 일치 {item['liveMatches']} · Google PASS {item['googlePass']}/{item['googleKnown']} · Google 비교 불가 {item['googleUnknownOrError']} · Bing 크롤링 기록 {item['bingCrawlRecords']}/{item['bingResponses']} · Bing 조회 실패 {item['bingErrors']} · Google canonical 차이 {item['googleCanonicalDifferences']}")
    for row in report['urls']:
        state = google_state(row)
        bing_status = '조회 실패' if row['bing'].get('error') or row['bing'].get('httpStatus') != 200 else row['bing'].get('lastCrawledAt') or '크롤링 기록 미제공'
        lines.append(f"{row['url']}\n  Google: {state.get('coverageState', state['verdict']) if state else '조회 실패·상태 미제공'}; canonical: {state.get('googleCanonical', '미제공') if state else '미제공'}\n  Bing 크롤링: {bing_status}; 색인 확정: 불가")
    public_map = report['publicSitemap']
    lines.append(f"공개 사이트맵 URL 수: {public_map.get('urlCount', '조회 실패')}")
    for feed in report['bingSite']['GetFeeds'].get('rows', []):
        if feed.get('Url') == SITE + 'sitemap.xml':
            lines.append(f"Bing 사이트맵 기록: 상태 {feed.get('Status', '미제공')} · URL 수 {feed.get('UrlCount', '미제공')} · 마지막 수집 {bing_date(feed.get('LastCrawled')) or '미제공'}")
    totals = report.get('performance', {}).get('current', {}).get('totals', {})
    rows = totals.get('data', {}).get('rows', [])
    lines.append(f"Google 현재 구간(PT): {report['windows']['current']}")
    if totals.get('httpStatus') == 200 and rows:
        lines.append(f"사이트 전체 클릭 {rows[0].get('clicks', '미제공')} · 노출 {rows[0].get('impressions', '미제공')}")
    else: lines.append('Google 사이트 전체 실적 미제공 또는 조회 실패')
    traffic = report['bingSite']['GetRankAndTrafficStats']
    lines.append(f"Bing 실적 반환 행: {len(traffic['rows'])}" if 'rows' in traffic else 'Bing 실적 조회 실패')
    lines.append('Bing 빈 실적은 노출 0의 증거가 아닙니다. Google PASS도 개별 검색어 순위나 현재 검색 결과 노출을 보장하지 않습니다.')
    if 'comparison' in report:
        c = report['comparison']
        lines.append(f"이전 대비 Google PASS 전환 {len(c['newGooglePass'])} · PASS 해제 {len(c['noLongerGooglePass'])} · 비교 불가 {len(c['googleUncomparable'])} · Bing 새 크롤링 기록 {len(c['newBingCrawlRecords'])}")
    return '\n'.join(lines)


def destination(path):
    path = path.expanduser().resolve()
    import subprocess
    worktrees = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], cwd=ROOT, text=True)
    roots = [Path(line.removeprefix('worktree ')).resolve() for line in worktrees.splitlines() if line.startswith('worktree ')]
    if any(path.is_relative_to(root) for root in roots) or path.exists():
        raise ValueError('Use a new private snapshot outside repository checkouts')
    return path


def save_new(path, report):
    path = destination(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
    except Exception:
        path.unlink()
        raise
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--retry-bing', type=Path, help='Retry only failed Bing URL reads from an existing snapshot')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.report:
            if args.live or args.previous or args.output or args.retry_bing: raise ValueError('Report is offline only')
            print(format_report(json.loads(args.report.expanduser().read_text())))
            return 0
        if args.retry_bing:
            if args.live or args.previous: raise ValueError('Bing retry cannot collect Google again')
            now = datetime.now(timezone.utc)
            output = destination(args.output or CONFIG / f'search-engines-bing-retry-{now:%Y%m%dT%H%M%SZ}.json')
            previous = json.loads(args.retry_bing.expanduser().read_text())
            key = (CONFIG / 'bing-api-key.txt').read_text().strip()
            if not key: raise ValueError('Bing key is empty')
            report = retry_bing(previous, key, now)
            path = save_new(output, report)
            print(json.dumps({'snapshot': str(path), 'retried': report['bingRetriedURLCount'], 'summary': report['summary']}, ensure_ascii=False, indent=2))
            return int(any(r['bing'].get('error') or r['bing'].get('httpStatus') != 200 for r in report['urls']))
        selected = targets()
        if not args.live:
            if args.previous or args.output: raise ValueError('Collection options require --live')
            print(json.dumps({'mode': 'preview', 'urls': selected}, ensure_ascii=False, indent=2))
            return 0
        now = datetime.now(timezone.utc)
        output = args.output or CONFIG / f'search-engines-{now:%Y%m%dT%H%M%SZ}.json'
        # Validate destinations before spending API quota; save_new still uses exclusive creation.
        output = destination(output)
        previous = json.loads(args.previous.expanduser().read_text()) if args.previous else None
        if previous is not None:
            if {r['url'] for r in previous['urls']} != {r['url'] for r in selected} or previous.get('site') != SITE:
                raise ValueError('Previous selection differs')
        key = (CONFIG / 'bing-api-key.txt').read_text().strip()
        if not key: raise ValueError('Bing key is empty')
        token = access_token(SimpleNamespace(client=None, token_file=CONFIG / 'token.json'))
        report = collect(token, key, selected, now)
        if previous is not None: report['comparison'] = compare(previous, report)
        path = save_new(output, report)
        print(json.dumps({'snapshot': str(path), 'summary': report['summary']}, ensure_ascii=False, indent=2))
        failed = any(google_state(r) is None or r['bing'].get('error') or not r['live'].get('matchesExpectedStaticRoute') for r in report['urls'])
        failed |= bool(report['publicSitemap'].get('error')) or any(v.get('error') for v in report['bingSite'].values())
        failed |= any(v.get('httpStatus') != 200 for p in report['performance'].values() for v in p.values())
        return int(failed)
    except Exception as error:
        print(f'Search-engine audit failed ({type(error).__name__}); credentials and response bodies omitted.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
