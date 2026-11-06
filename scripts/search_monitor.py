#!/usr/bin/env python3
"""Scheduled public technical checks and private, read-only search observations."""
import argparse
from copy import deepcopy
import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo

import crawl_access
from check_metadata import Metadata, validate, LOCALES
from check_technical_preview import TechnicalHTML
from search_console import CONFIG, SITE, private_json
from search_engines import sitemap, save_new, destination, bing_get, bing_url
from search_growth import google_post, targets as core_targets
from answer_observation import paged, ai_source
from measurement_audit import PROPERTY, ga_session, ga_call, aligned_window, exact, together, flat

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
OUTPUT = Path.home() / '.local/share/blog-audits/search-monitor'


def weekly_slot(now):
    local = now.astimezone(ZoneInfo('Asia/Seoul'))
    slot = (local - timedelta(days=local.weekday())).replace(hour=8, minute=37, second=0, microsecond=0)
    return slot if local >= slot else slot - timedelta(days=7)


def due(now, state):
    slot = weekly_slot(now)
    if state.get('successfulSlot') == slot.isoformat(): return False
    attempted = state.get('attemptedAt')
    return not attempted or now - datetime.fromisoformat(attempted) >= timedelta(hours=6)


def public_target(url):
    parsed = urlsplit(url)
    parts = parsed.path.strip('/').split('/')
    if (parsed.scheme != 'https' or parsed.netloc != 'youdozi.github.io'
            or parsed.query or parsed.fragment or '..' in parts or parts[0] not in LOCALES):
        raise ValueError('Expected a clean public locale URL')
    kind = 'home' if len(parts) == 1 else 'archive' if parts[1:] == ['archive'] else 'article' if parts[1] in ('posts', 'digest') and len(parts) == 3 else 'page'
    return {'url': url, 'language': parts[0], 'key': '/'.join(parts[1:]),
            'group': '/'.join(parts[1:]), 'kind': kind, 'expectedCanonical': url}


def selected_targets(urls):
    if not urls or len(urls) > 5000 or len(set(urls)) != len(urls):
        raise ValueError('Expected a bounded, unique public sitemap')
    return [public_target(url) for url in urls]


def daily(get):
    transport = get
    deadline = time.monotonic() + 900
    def get(url, **kwargs):
        if time.monotonic() >= deadline: raise TimeoutError('Public audit time budget exceeded')
        return transport(url, **kwargs)
    public_map = sitemap(get)
    if 'urls' not in public_map:
        return {'mode': 'daily', 'state': 'failed', 'errors': ['sitemap-unavailable'], 'sitemap': public_map}
    selected = selected_targets(public_map['urls'])
    errors, images = {}, {}

    def read(url, **kwargs):
        response = get(url, **kwargs)
        if url in wanted and response.status_code == 200:
            page = Metadata(); page.feed(response.text)
            errors[url] = validate(url, page) if page.language in LOCALES else ['unknown-html-language']
            body = TechnicalHTML(); body.feed(response.text)
            images[url] = body.images
        return response

    wanted = {row['url'] for row in selected}
    report = crawl_access.collect(selected, read)
    assets = set()
    for row in report['urls']:
        row['issues'].extend(errors.get(row['url'], []))
        for image in images.get(row['url'], []):
            source = image.get('src', '')
            if not image.get('alt', '').strip(): row['issues'].append('missing-image-alt')
            if source.startswith('/assets/') and not source.startswith('//'):
                asset = urlsplit(SITE.rstrip('/') + source)
                if asset.query or asset.fragment or '..' in asset.path.split('/'):
                    row['issues'].append('unexpected-image-path')
                else: assets.add(asset.geturl())

    def image_status(url):
        try:
            response = get(url, timeout=20, allow_redirects=False)
            valid = response.status_code == 200 and response.headers.get('Content-Type', '').lower().startswith('image/')
            return {'url': url, 'state': 'checks-passed' if valid else 'issue', 'httpStatus': response.status_code}
        except Exception:
            return {'url': url, 'state': 'unknown'}

    with ThreadPoolExecutor(max_workers=2) as pool:
        report['images'] = list(pool.map(image_status, sorted(assets)))
    for row in report['urls']:
        row['state'] = 'issue' if row['issues'] else 'unknown' if row['unknown'] else 'checks-passed'
    report.update({'mode': 'daily', 'metadataAndImagesChecked': True,
                   'state': 'passed' if all(row['state'] == 'checks-passed' for row in report['urls'] + report['images']) else 'failed'})
    report['summary'] = {state: sum(r['state'] == state for r in report['urls']) for state in ('checks-passed', 'issue', 'unknown')}
    return report


def weekly_windows(now):
    end = now.astimezone(ZoneInfo('America/Los_Angeles')).date() - timedelta(days=3)
    start = end - timedelta(days=6)
    return {'current': {'start': str(start), 'end': str(end)},
            'previous': {'start': str(start - timedelta(days=7)), 'end': str(start - timedelta(days=1))}}


def index_sample(urls):
    rows = selected_targets(urls)
    picked = {row['url']: row for row in rows if row['kind'] == 'home'}
    public = {row['url']: row for row in rows}
    core = core_targets(json.loads((ROOT / 'content/seo/core-articles.json').read_text()))
    for row in core:
        if row['kind'] == 'article' and row['url'] in public: picked[row['url']] = public[row['url']]
    for language in LOCALES:
        recent = sorted((r for r in rows if r['kind'] == 'article' and r['language'] == language), key=lambda r: r['key'].rsplit('/', 1)[-1], reverse=True)
        for row in recent[:3]: picked[row['url']] = row
    if len(picked) > 64: raise ValueError('Inspection sample exceeds request budget')
    return list(picked.values())


def observed_value(response, field):
    if response.get('httpStatus') != 200 or response.get('error'): return None
    rows = response.get('data', {}).get('rows', [])
    return rows[0].get(field) if len(rows) == 1 else None


def deltas(periods):
    output = {}
    for metric in ('clicks', 'impressions'):
        before = observed_value(periods['previous']['gscTotals'], metric)
        after = observed_value(periods['current']['gscTotals'], metric)
        output[metric] = {'previous': before, 'current': after, 'absoluteChange': after - before if before is not None and after is not None else None}
    for metric in ('totalUsers', 'sessions', 'engagedSessions', 'screenPageViews'):
        values = []
        for name in ('previous', 'current'):
            rows = flat(periods[name]['gaTotals'])
            values.append(float(rows[0][metric]) if rows and len(rows) == 1 and metric in rows[0] else None)
        before, after = values
        output['ga:' + metric] = {'previous': before, 'current': after, 'absoluteChange': after - before if before is not None and after is not None else None}
    return output


def weekly(now, urls, gsc, ga, bing, zone='Asia/Seoul', pause=time.sleep, budget_seconds=600):
    deadline = time.monotonic() + budget_seconds
    def budgeted(call):
        def read(*args):
            if time.monotonic() >= deadline:
                return {'error': 'request-budget-exceeded', 'notRequested': True}
            try: return call(*args)
            except Exception: return {'error': 'API-transport-failure'}
        return read
    gsc, ga, bing = (budgeted(call) for call in (gsc, ga, bing))
    report = {'mode': 'weekly', 'site': SITE, 'observedAt': now.isoformat(), 'windows': weekly_windows(now),
              'gaTimezone': zone, 'periods': {}, 'apiErrors': [], 'indexSample': [],
              'dedicatedAIReports': {'google': 'not-collected', 'bing': 'not-collected'},
              'limitations': ['GSC final web data excludes the newest three PT dates; query/page rows are not exhaustive.',
                 'GA is filtered to corresponding property-timezone hours. GA sessions are not search clicks.',
                 'AI source-label matches are not proof of an AI citation, a human visitor or incremental impact.',
                 'Country is traffic geolocation, not nationality; engagement does not establish a human reader.',
                 'GA country/hour session rows can overlap. Do not sum them to reconstruct unique session totals.',
                 'Dedicated Google/Bing AI citation reports are not collected.',
                 'Index inspection is a current saved-state sample, not a live crawl or indexing request.',
                 'Bing GetUrlInfo observes crawl records and does not confirm index membership.',
                 'Missing/error responses are unknown, not zero. Differences do not establish causality.']}
    for name, span in report['windows'].items():
        aligned = aligned_window(span['start'], span['end'], zone)
        base = {'startDate': span['start'], 'endDate': span['end'], 'dataState': 'final', 'type': 'web', 'rowLimit': 25000}
        ga_base = {'dateRanges': [aligned['gaDates']], 'dimensionFilter': together(exact('hostName', 'youdozi.github.io'),
                   {'filter': {'fieldName': 'dateHour', 'inListFilter': {'values': aligned['gaHours']}}})}
        period = {'alignment': aligned, 'gscTotals': gsc('performance', {**base, 'dimensions': []}),
                  'gscPages': paged(lambda body: gsc('performance', body), {**base, 'dimensions': ['page']}, 'startRow', 'rows'),
                  'gaTotals': ga({**ga_base, 'metrics': [{'name': x} for x in ('totalUsers', 'sessions', 'engagedSessions', 'screenPageViews')]}),
                  'gaSources': paged(ga, {**ga_base, 'dimensions': [{'name': x} for x in ('landingPage', 'sessionSource', 'sessionMedium')],
                          'metrics': [{'name': x} for x in ('sessions', 'engagedSessions')], 'limit': 25000}, 'offset', 'rows')}
        period['gscCountries'] = paged(lambda body: gsc('performance', body),
                                      {**base, 'dimensions': ['country']}, 'startRow', 'rows')
        for field, dimensions in [('gaCountries', ('country',)), ('gaCountryHours', ('country', 'hour')),
                                  ('gaCountrySources', ('country', 'sessionSource', 'sessionMedium'))]:
            period[field] = paged(ga, {**ga_base, 'dimensions': [{'name': x} for x in dimensions],
                'metrics': [{'name': x} for x in ('sessions', 'engagedSessions', 'screenPageViews', 'userEngagementDuration')],
                'limit': 25000}, 'offset', 'rows')
        sources = period['gaSources']
        rows = flat({'httpStatus': 200, 'data': sources}) if sources.get('dimensionHeaders') and sources.get('metricHeaders') else None
        period['aiDomainMatchedRows'] = [row for row in (rows or []) if ai_source(row.get('sessionSource'))]
        period['aiAttributionState'] = sources['state']
        for field in ('gscTotals', 'gaTotals'):
            if period[field].get('httpStatus') != 200 or period[field].get('error'): report['apiErrors'].append(name + ':' + field)
        for field in ('gscPages', 'gaSources', 'gscCountries', 'gaCountries', 'gaCountryHours', 'gaCountrySources'):
            if not period[field]['completePagination']: report['apiErrors'].append(name + ':' + field)
        report['periods'][name] = period
    report['changes'] = deltas(report['periods'])
    sites = bing('GetUserSites', {})
    matches = {r['Url'] for r in sites.get('data', []) if isinstance(r, dict) and isinstance(r.get('Url'), str) and r['Url'].rstrip('/') == SITE.rstrip('/')} if isinstance(sites.get('data'), list) else set()
    bing_site = next(iter(matches)) if len(matches) == 1 else None
    report['bingStats'] = bing('GetRankAndTrafficStats', {'siteUrl': bing_site}) if bing_site else {'error': 'Registered-site-unconfirmed'}
    report['bingSiteUrl'] = bing_site
    if report['bingStats'].get('httpStatus') != 200 or report['bingStats'].get('error'): report['apiErrors'].append('bing:stats')
    throttled = report['bingStats'].get('apiErrorCode') in (4, 5) or report['bingStats'].get('httpStatus') == 429
    def inspect(target):
        if time.monotonic() >= deadline:
            return {'error': 'request-budget-exceeded', 'notRequested': True}
        try: return gsc('inspect', {'inspectionUrl': target['url'], 'siteUrl': SITE, 'languageCode': 'en-US'})
        except Exception: return {'error': 'Google-inspection-transport-failure'}
    selected = index_sample(urls)
    with ThreadPoolExecutor(max_workers=2) as pool:
        inspections = pool.map(inspect, selected)
        for target, inspection in zip(selected, inspections):
            if inspection.get('httpStatus') != 200 or inspection.get('error'): report['apiErrors'].append('google:inspection')
            if bing_site and not throttled and time.monotonic() < deadline:
                observed = bing_url(bing('GetUrlInfo', {'siteUrl': bing_site, 'url': target['url']}))
                throttled = observed.get('apiErrorCode') in (4, 5) or observed.get('httpStatus') == 429
                pause(0.6)
            else: observed = {'error': 'deferred-throttle-site-or-budget', 'notRequested': True}
            if observed.get('httpStatus') != 200 or observed.get('error'): report['apiErrors'].append('bing:url-observation')
            report['indexSample'].append({'url': target['url'], 'language': target['language'], 'google': inspection, 'bing': observed})
    report['apiErrors'] = sorted(set(report['apiErrors']))
    report['state'] = 'passed' if not report['apiErrors'] else 'partial-failure'
    return report


def retry_bing(report, urls, bing, now, pause=time.sleep):
    if report.get('site') != SITE or report.get('mode') != 'weekly' or report.get('schemaVersion') != 1:
        raise ValueError('Expected a private weekly snapshot for this site')
    result = deepcopy(report)
    deadline = time.monotonic() + 600
    transport = bing
    def bing(method, params):
        if time.monotonic() >= deadline:
            return {'error': 'request-budget-exceeded', 'notRequested': True}
        try: return transport(method, params)
        except Exception: return {'error': 'Bing-transport-failure'}
    allowed = {r['url'] for r in selected_targets(urls)}
    if any(row.get('url') not in allowed for row in result['indexSample']):
        raise ValueError('Retry snapshot no longer matches public URLs')
    site = result.get('bingSiteUrl')
    if not site or site.rstrip('/') != SITE.rstrip('/'):
        sites = bing('GetUserSites', {})
        matches = {r['Url'] for r in sites.get('data', []) if isinstance(r, dict) and isinstance(r.get('Url'), str) and r['Url'].rstrip('/') == SITE.rstrip('/')} if isinstance(sites.get('data'), list) else set()
        site = next(iter(matches)) if len(matches) == 1 else None
    result['bingSiteUrl'] = site
    if result['bingStats'].get('httpStatus') != 200 or result['bingStats'].get('error'):
        result['bingStats'] = bing('GetRankAndTrafficStats', {'siteUrl': site}) if site else {'error': 'Registered-site-unconfirmed'}
    throttled = result['bingStats'].get('apiErrorCode') in (4, 5) or result['bingStats'].get('httpStatus') == 429
    for row in result['indexSample']:
        if row['bing'].get('httpStatus') == 200 and not row['bing'].get('error'): continue
        if not site or throttled or time.monotonic() >= deadline: break
        row['bing'] = bing_url(bing('GetUrlInfo', {'siteUrl': site, 'url': row['url']}))
        row['bing']['observedAt'] = now.isoformat()
        throttled = row['bing'].get('apiErrorCode') in (4, 5) or row['bing'].get('httpStatus') == 429
        pause(0.6)
    errors = [error for error in result['apiErrors'] if not error.startswith('bing:')]
    if result['bingStats'].get('httpStatus') != 200 or result['bingStats'].get('error'): errors.append('bing:stats')
    if any(r['bing'].get('httpStatus') != 200 or r['bing'].get('error') for r in result['indexSample']): errors.append('bing:url-observation')
    result.update({'apiErrors': errors, 'state': 'partial-failure' if errors else 'passed',
                   'bingRecheckedAt': now.isoformat(), 'dataOrigin': 'Bing retry; Google and performance retain original observedAt'})
    result.setdefault('originalCollectionSource', {'commit': report.get('sourceCommit'), 'fileSha256': report.get('sourceFileSha256')})
    return result


def headless_gsc_token():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    credentials = Credentials.from_authorized_user_file(str(CONFIG / 'token.json'))
    if not credentials.valid:
        credentials.refresh(Request())
        private_json(CONFIG / 'token.json', json.loads(credentials.to_json()))
    return credentials.token


def live_weekly(now, urls):
    session = None
    try:
        token = headless_gsc_token()
    except Exception: token = None
    try:
        session = ga_session()
        response = session.get('https://analyticsadmin.googleapis.com/v1beta/' + PROPERTY, timeout=30)
        zone = response.json().get('timeZone') if response.status_code == 200 else None
        if not zone: raise ValueError('Property timezone unavailable')
    except Exception:
        if session: session.close()
        session, zone = None, 'Asia/Seoul'
    try:
        key = (CONFIG / 'bing-api-key.txt').read_text().strip()
    except OSError: key = None
    def gsc(kind, body):
        if not token: return {'error': 'Google-reauthorization-required'}
        endpoint = ('https://searchconsole.googleapis.com/v1/urlInspection/index:inspect' if kind == 'inspect' else
                    'https://www.googleapis.com/webmasters/v3/sites/' + quote(SITE, safe='') + '/searchAnalytics/query')
        try: return google_post(token, endpoint, body)
        except Exception: return {'error': 'Google-transport-failure'}
    try:
        report = weekly(now, urls, gsc,
                      lambda body: ga_call(session, 'POST', PROPERTY + ':runReport', body) if session else {'error': 'GA-authentication-or-timezone-unavailable'},
                      lambda method, params: bing_get(key, method, params) if key else {'error': 'Bing-key-unavailable'}, zone)
        report['gaTimezoneVerified'] = session is not None
        return report
    finally:
        if session: session.close()


def format_weekly(report):
    lines = ['주간 SEO·AEO 관측: ' + report['checkedAt'], '상태: ' + report['state']]
    if 'changes' not in report: return '\n'.join(lines + ['수집 실패: ' + ', '.join(report.get('errors', []))])
    lines.append('검색·GA·Google 색인 원래 수집: ' + report['observedAt'])
    if report.get('bingRecheckedAt'): lines.append('Bing 실패분 재확인: ' + report['bingRecheckedAt'])
    for name, span in report['windows'].items():
        lines.append(f"{name}: {span['start']} ~ {span['end']} PT (GA는 속성 시간대의 대응 시간으로 필터)")
    for metric, change in report['changes'].items():
        lines.append(f"{metric}: 이전 {change['previous']} → 현재 {change['current']}, 차이 {change['absoluteChange']}")
    for name, period in report['periods'].items():
        lines.append(f"{name} AI 출처명 일치 행: {len(period['aiDomainMatchedRows'])}; 조회 상태: {period['aiAttributionState']}")
        for field in ('gscCountries', 'gaCountries', 'gaCountryHours', 'gaCountrySources'):
            audience = period.get(field)
            if audience is not None:
                lines.append(f"{name} {field}: {audience['state']}, 반환 행 {len(audience['rows'])}, 페이지 수집 완료 {audience['completePagination']}")
    if any('gaCountries' in period for period in report['periods'].values()):
        lines.append('국가·시간별 원본은 JSON 보고서에 저장합니다. GA 시간대: ' + report['gaTimezone'] + '. 참여 세션은 사람 판정이 아니며 시간별 세션을 단순 합산하지 않습니다.')
    known = [r['google'].get('data', {}).get('inspectionResult', {}).get('indexStatusResult', {}) for r in report['indexSample']]
    passed = sum(s.get('verdict') == 'PASS' for s in known)
    unknown = sum(s.get('verdict') not in ('PASS', 'FAIL', 'NEUTRAL', 'PARTIAL') for s in known)
    lines.append(f"Google 저장 색인 표본: {len(known)} URL, PASS {passed}, 조회 실패·판정 미제공 {unknown}")
    lines.append('API 오류: ' + (', '.join(report['apiErrors']) or '없음'))
    lines.append('Google/Bing 전용 AI 인용 보고서는 수집하지 않았습니다. AI 출처명 일치는 실제 인용·사람 방문의 증명이 아닙니다.')
    lines.append('HTTP 정상·Google 색인·Bing 크롤링 기록은 서로 다른 관측입니다. 누락 값은 0으로 간주하지 않으며, 전후 차이는 인과효과가 아닙니다.')
    return '\n'.join(lines) + '\n'


def authorize(client):
    from google_auth_oauthlib.flow import InstalledAppFlow
    config = json.loads(client.expanduser().read_text())
    installed = config.get('installed', {})
    if (installed.get('auth_uri') != 'https://accounts.google.com/o/oauth2/auth'
            or installed.get('token_uri') != 'https://oauth2.googleapis.com/token'):
        raise ValueError('Use the existing Google desktop OAuth client')
    scopes = ['https://www.googleapis.com/auth/webmasters', 'https://www.googleapis.com/auth/analytics.readonly']
    flow = InstalledAppFlow.from_client_config(config, scopes=scopes, autogenerate_code_verifier=True)
    credentials = flow.run_local_server(host='127.0.0.1', port=0, open_browser=True, timeout_seconds=300,
        authorization_prompt_message='Google 로그인 창에서 승인을 기다립니다.',
        success_message='Google 인증을 마쳤습니다. 이 창을 닫아도 됩니다.', access_type='offline', prompt='consent')
    if not credentials.refresh_token or not set(scopes) <= set(credentials.granted_scopes or credentials.scopes):
        raise ValueError('Both existing API scopes and offline access are required')
    payload = json.loads(credentials.to_json())
    private_json(CONFIG / 'token.json', payload); private_json(CONFIG / 'analytics-token.json', payload)
    print('Google API 인증을 로컬에 저장했습니다. 인증정보는 출력하거나 Actions로 전송하지 않았습니다.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['daily', 'weekly', 'authorize'])
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=OUTPUT)
    parser.add_argument('--scheduled', action='store_true', help='Weekly due check with six-hour failure retry spacing')
    parser.add_argument('--client', type=Path, default=CONFIG / 'oauth-client.json')
    args = parser.parse_args()
    if args.scheduled and args.mode != 'weekly': parser.error('--scheduled is weekly-only')
    if not args.live:
        print(json.dumps({'mode': args.mode, 'planOnly': True, 'credentialsRead': False, 'settingsModified': False,
                          'scope': {'daily': 'All sitemap pages and local images',
                                    'weekly': 'Two seven-day GSC/GA periods; <=64 current Google/Bing URL observations',
                                    'authorize': 'User Google consent in browser; OAuth files stay local'}[args.mode]}, indent=2))
        return 0
    if args.mode == 'authorize':
        authorize(args.client); return 0
    directory = args.output_dir.expanduser().resolve()
    # Validate before API/credential access; reports never enter Git or public artifacts.
    now = datetime.now(timezone.utc)
    output = destination(directory / f'{args.mode}-{now:%Y%m%dT%H%M%S%fZ}.json')
    source_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    state_path = directory / 'weekly-state.json'
    state = json.loads(state_path.read_text()) if args.mode == 'weekly' and state_path.is_file() else {}
    if args.scheduled and not due(now, state):
        print('Weekly search monitor is not due. No credentials or APIs used.'); return 0
    if args.mode == 'weekly':
        state.update({'attemptedAt': now.isoformat(), 'lastOutcome': 'running'})
        private_json(state_path, state)
    try:
        import requests
        get = requests.get
        if args.mode == 'daily': report = daily(get)
        else:
            public_map = sitemap(get)
            if 'urls' not in public_map: report = {'mode': 'weekly', 'state': 'failed', 'errors': ['sitemap-unavailable']}
            else:
                pending = state.get('pendingReport', '')
                candidate = directory / pending
                previous = None
                if (args.scheduled and state.get('pendingSlot') == weekly_slot(now).isoformat()
                        and re.fullmatch(r'weekly-\d{8}T\d{12}Z\.json', pending)
                        and candidate.is_file() and not candidate.is_symlink()):
                    saved = json.loads(candidate.read_text())
                    if saved.get('apiErrors') and all(error.startswith('bing:') for error in saved['apiErrors']): previous = saved
                if previous:
                    key = (CONFIG / 'bing-api-key.txt').read_text().strip()
                    report = retry_bing(previous, public_map['urls'], lambda method, params: bing_get(key, method, params), now)
                else: report = live_weekly(now, public_map['urls'])
    except Exception as error:
        report = {'mode': args.mode, 'state': 'failed', 'errors': [type(error).__name__]}
    report.update({'schemaVersion': 1, 'checkedAt': now.isoformat(),
                   'sourceCommit': source_commit,
                   'sourceFileSha256': SOURCE_SHA256})
    save_new(output, report)
    if args.mode == 'weekly':
        summary = destination(output.with_suffix('.txt'))
        with summary.open('x', encoding='utf-8') as stream:
            summary.chmod(0o600); stream.write(format_weekly(report))
        state['attemptedAt'] = now.isoformat()
        state['lastOutcome'] = report['state']
        if (report.get('periods') and report.get('indexSample') and report.get('apiErrors')
                and all(error.startswith('bing:') for error in report['apiErrors'])):
            state.update({'pendingReport': output.name, 'pendingSlot': weekly_slot(now).isoformat()})
        if report['state'] == 'passed':
            state['successfulSlot'] = weekly_slot(now).isoformat()
            state.pop('pendingReport', None); state.pop('pendingSlot', None)
        private_json(state_path, state)
    print(json.dumps({'mode': args.mode, 'state': report['state'], 'report': str(output)}, ensure_ascii=False))
    return 0 if report['state'] == 'passed' else 2


if __name__ == '__main__':
    try: raise SystemExit(main())
    except Exception as error:
        print('Search monitor failed: ' + type(error).__name__)
        raise SystemExit(1)
